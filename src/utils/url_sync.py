"""
Two-way synchronisation between the browser URL query string and the page selectors.

A page declares which of its components should live in the URL, and this module builds
the two callbacks that keep them in sync:

- the *reader* applies the query string to the components once, when the page mounts,
- the *writer* re-serialises the components into the query string whenever they change.

The figure is deliberately NOT computed from the URL: submit stays manual, so a shared
link that is opened many times does not translate into many open-meteo requests.

Usage, from a page's ``options_selector.py``::

    from utils.url_sync import Param, register

    register("ensemble", [
        Param("models-selection", "value", "model", valid=ENSEMBLE_MODELS),
        Param("clima-switch", "checked", "clima", kind="bool"),
    ])

where "ensemble" is the index the page already uses for its {"type": "fade", "index": ...}
Collapse. No change to the page layout is needed: app.py announces the mounted page through
the shared "url-sync-trigger" store.
"""

import logging
from dataclasses import dataclass, field
from io import StringIO
from typing import Any, Optional, Sequence, Union
from urllib.parse import parse_qs, quote, urlencode

import pandas as pd
from dash import Input, Output, State, callback, no_update
from dash.exceptions import PreventUpdate

from .settings import get_valid_values

# Coordinates are rounded to the same precision create_unique_id() normalises to,
# so the id generated from a shared link matches the one the app would build itself.
COORD_PRECISION = 4


@dataclass(frozen=True)
class Param:
    """One component property mirrored into the query string.

    kind is one of "str", "int", "bool", "list", "daterange". For "daterange" the
    component value is a two-element list and ``key`` must be a two-element tuple.
    ``valid`` is any option list accepted by settings.get_valid_values(); when given,
    values outside it are ignored. ``default`` is applied only when the URL does not
    carry the key AND the component currently holds no value.
    """

    cid: str
    prop: str
    key: Union[str, tuple]
    kind: str = "str"
    valid: Optional[Sequence] = None
    lo: Optional[int] = None
    hi: Optional[int] = None
    default: Any = None
    _valid_values: list = field(default_factory=list, compare=False, repr=False)

    def __post_init__(self):
        if self.valid is not None:
            object.__setattr__(self, "_valid_values", get_valid_values(self.valid))


def _encode_one(param, value):
    """Serialise a single component value into a list of (key, string) pairs."""
    if value is None or value == [] or value == "":
        return []
    if param.kind == "bool":
        return [(param.key, "1" if value else "0")]
    if param.kind == "list":
        return [(param.key, ",".join(str(v) for v in value))]
    if param.kind == "daterange":
        if not isinstance(value, (list, tuple)) or len(value) != 2 or not all(value):
            return []
        return [(param.key[0], str(value[0])), (param.key[1], str(value[1]))]
    return [(param.key, str(value))]


def _decode_one(param, query, current):
    """Read a single component value out of the parsed query string.

    Returns no_update when the key is absent or the value does not survive
    validation, so that persisted values and anything the user has already typed
    are never clobbered by a link that did not mention them.
    """
    if param.kind == "daterange":
        start, end = query.get(param.key[0]), query.get(param.key[1])
        if not start or not end:
            return _fallback(param, current)
        try:
            pd.to_datetime(start[0])
            pd.to_datetime(end[0])
        except (ValueError, TypeError):
            return _fallback(param, current)
        return [start[0], end[0]]

    raw = query.get(param.key)
    if not raw:
        return _fallback(param, current)
    raw = raw[0]

    if param.kind == "bool":
        if raw.lower() in ("1", "true", "yes", "on"):
            return True
        if raw.lower() in ("0", "false", "no", "off"):
            return False
        return _fallback(param, current)

    if param.kind == "int":
        try:
            out = int(float(raw))
        except (ValueError, TypeError):
            return _fallback(param, current)
        if param.lo is not None:
            out = max(param.lo, out)
        if param.hi is not None:
            out = min(param.hi, out)
        return out

    if param.kind == "list":
        out = [v for v in raw.split(",") if v]
        if param._valid_values:
            out = [v for v in out if v in param._valid_values]
        return out if out else _fallback(param, current)

    if param._valid_values and raw not in param._valid_values:
        return _fallback(param, current)
    return raw


def _fallback(param, current):
    """Value to use when the URL says nothing usable about this parameter."""
    if current in (None, [], "") and param.default is not None:
        return param.default() if callable(param.default) else param.default
    return no_update


def coords_of_selected(locations_list, location_selected):
    """Latitude/longitude of the currently selected location, or (None, None).

    Mirrors the lookup done in location_selector_callbacks.add_point_on_map().
    """
    if not locations_list or not location_selected or len(location_selected) < 1:
        return None, None
    try:
        locations = pd.read_json(
            StringIO(locations_list), orient="split", dtype={"id": str}
        )
        loc = locations[locations["id"] == location_selected[0]["value"]]
        if len(loc) != 1:
            return None, None
        return (
            round(float(loc["latitude"].item()), COORD_PRECISION),
            round(float(loc["longitude"].item()), COORD_PRECISION),
        )
    except (ValueError, KeyError, TypeError):
        return None, None


def register(page, params):
    """Wire up the URL <-> selectors sync for one page.

    ``page`` is the index already used by that page's {"type": "fade", "index": ...}
    Collapse and submit button.
    """

    @callback(
        [Output(p.cid, p.prop, allow_duplicate=True) for p in params]
        + [Output("url-sync-applied", "data", allow_duplicate=True)],
        Input("url-sync-trigger", "data"),
        [State("url", "search")] + [State(p.cid, p.prop) for p in params],
        prevent_initial_call=True,
    )
    def _read_url(trigger, search, *current):
        """Apply the query string to this page's selectors, once, on mount."""
        if not trigger or trigger.get("page") != page:
            raise PreventUpdate
        query = parse_qs((search or "").lstrip("?"))
        try:
            values = [_decode_one(p, query, cur) for p, cur in zip(params, current)]
        except Exception as e:
            # A malformed link must never break the page: leave every selector alone.
            logging.warning(f"Could not apply URL parameters for page {page}: {e}")
            values = [no_update] * len(params)
        # Always hand over to the writer, even when nothing was applied, so that the
        # address bar still gets normalised to this page's parameters
        return values + [{"page": page, "token": trigger.get("token")}]

    @callback(
        Output("url-query", "data", allow_duplicate=True),
        [Input("url-sync-applied", "data")]
        + [Input(p.cid, p.prop) for p in params]
        + [Input("location-selected", "data")],
        [State("locations-list", "data"), State("url", "search")],
        prevent_initial_call=True,
    )
    def _write_url(applied, *args):
        """Re-serialise this page's selectors (and the location) into the query string.

        Driven by url-sync-applied rather than by the mount trigger directly, so that it
        can never run before the reader has had a chance to apply an incoming link and
        briefly rewrite the address bar with this page's default values.
        """
        if not applied or applied.get("page") != page:
            raise PreventUpdate
        values = args[:-3]
        location_selected, locations_list, search = args[-3], args[-2], args[-1]
        pairs = []
        lat, lon = coords_of_selected(locations_list, location_selected)
        if lat is None:
            # The location stores are populated by load_cache one step later than this
            # runs on a fresh page load; keep the coordinates of the incoming link
            # rather than dropping them from the address bar in the meantime.
            lat, lon = coords_from_search(search)
        if lat is not None:
            pairs += [("lat", f"{lat:.{COORD_PRECISION}f}"),
                      ("lon", f"{lon:.{COORD_PRECISION}f}")]
        for p, value in zip(params, values):
            pairs += _encode_one(p, value)
        if not pairs:
            return ""
        # Keep commas and colons literal so the URL stays readable/hand-editable
        return "?" + urlencode(pairs, safe=",:", quote_via=quote)

    # Returned only to keep a reference; Dash has already registered both callbacks.
    return _read_url, _write_url


def coords_from_search(search):
    """Parse ?lat=..&lon=.. out of a query string. Returns (None, None) if absent/invalid."""
    query = parse_qs((search or "").lstrip("?"))
    try:
        lat = float(query["lat"][0])
        lon = float(query["lon"][0])
    except (KeyError, IndexError, ValueError, TypeError):
        return None, None
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        return None, None
    return round(lat, COORD_PRECISION), round(lon, COORD_PRECISION)
