# URL query-parameter sync for point_wx

> **This document is the working spec** for the URL query-parameter sync feature, kept in the repo
> so it stays versioned alongside the code.
>
> **Branch**: `experimental/url-query-params`, branched from `main`. Nothing merges to `main` until
> the full manual verification checklist at the bottom passes.

## Context

Today a point_wx session is unshareable. All UI state lives in browser-local `dcc.Store`s
(`locations-list`, `location-selected`, `locations-favorites`) plus Dash `persistence="true"` on a
dozen selectors. Sending someone "the ICON ensemble for Milano" means telling them which four
controls to set by hand. `dcc.Location(id="url", refresh=False)` already exists in
[app.py:160](src/app.py#L160) but **only `pathname` is ever read** — `search` is completely unused,
so this is greenfield.

Goal: make the URL a two-way mirror of the UI.

- Opening `/pointwx/ensemble?lat=45.4642&lon=9.1900&model=icon_seamless&clima=1` **pre-fills** the
  controls and the location, but does **not** compute the figure — submit stays manual, so a link
  opened 100 times costs 100 cheap cached geocodes, not 100 open-meteo fetches.
- Changing any control rewrites the query string in place (`history.replaceState`, no history spam).

Non-goals: auto-submitting from a URL; changing the store schemas; changing figure code.

Decisions taken (confirmed with the user): readable named params; location carried as `lat`/`lon`
only and rehydrated through the existing reverse-geocode path; `replaceState` for writes; all pages
wired in one go.

## URL shape

```
/pointwx/forecasts?lat=45.4642&lon=9.1900&models=icon_seamless,gfs_seamless&days=7&fromnow=1
/pointwx/ensemble?lat=45.4642&lon=9.1900&model=icon_seamless&clima=1&clouds=0
/pointwx/calendar?lat=45.4642&lon=9.1900&model=era5_seamless&graph=frost_days&year=1981
```

`lat`/`lon` rounded to 4 decimals (matches `create_unique_id`'s `:.4f` normalisation, so the
generated id is stable and cache keys collide usefully across shares). Booleans as `1`/`0`, lists
comma-joined, everything else `str()`.

## Architecture

Three pieces. The bulk is one new shared module; each page then costs ~10 lines.

### 1. New file: `src/utils/url_sync.py`

```python
Param = namedtuple("Param", "cid prop key kind valid")   # kind: str|int|bool|list|daterange
```

- `encode(params, values) -> "?a=1&b=x"` — skips `None`/empty, uses `urlencode`.
- `decode(search, params, current) -> [values]` — for each param: missing or invalid key →
  **`no_update`** (see "Persistence" below — this is what keeps the reader from ever clobbering a
  persisted or user-typed value), never raise. Whitelist `str`/`list` values against
  `get_valid_values(param.valid)` (already in [settings.py:103](src/utils/settings.py#L103)); clamp
  `int` to the component's `min`/`max`. A param may carry an optional `default` (callable or
  constant) applied only when the URL key is absent **and** the component's current value is `None`
  — needed for `year-selection-climate`, which ships with no `value=`.
- `register(page, params)` — builds the two callbacks below by closure, so pages just declare a
  spec list.

**Reader** (URL → UI), one per page:

```python
@callback(
    [Output(p.cid, p.prop, allow_duplicate=True) for p in params]
      + [Output("url-sync-applied", "data", allow_duplicate=True)],
    Input("url-sync-trigger", "data"),
    [State("url", "search")] + [State(p.cid, p.prop) for p in params],
    prevent_initial_call=True,
)
```

Every reader output uses `allow_duplicate`, which is what makes the ids duplicated across pages
(`from-now-switch`, `forecast-days`, `minutely-15-switch`, `heatmap-line-plot-switch`) legal —
without it Dash raises `DuplicateCallbackOutput` at import, since the callback graph is validated
globally rather than per mounted page. `allow_duplicate` forces `prevent_initial_call`, which is
why the mount signal has to arrive through a store (see app.py below) instead of being read
directly off the page's own components.

> **The trap this design exists to avoid.** Dash builds the suffix it appends to an
> `allow_duplicate` output from `sha256` of the callback's **inputs only** (`create_callback_id` in
> `dash/_callback.py`). Pages sharing one global trigger store therefore all produce the *same*
> suffix, and every shared selector ends up claimed by several callbacks under an identical
> `id.prop@hash`. Python does not catch this — it only compares whole callback ids, which still
> differ by component name — so the app imports, serves `_dash-dependencies`, and passes every
> server-side test. dash-renderer indexes individual outputs, so it only fails **in the browser**,
> as `Output N (...@<hash>) is already in use`. Keeping the trigger and handshake stores per page
> makes each reader's input list unique, and with it the suffix.
>
> `scripts/check_dup_outputs.py` replicates the renderer's check against a running server; run it
> after touching any `allow_duplicate` output, since nothing else will catch this headlessly.

The reader writes **only the props the URL explicitly names** (`no_update` for the rest — this is
the persistence-safety property) and always emits a token on `url-sync-applied`, even when it
applied nothing.

**Writer** (UI → URL), one per page:

```python
@callback(
    Output("url-query", "data", allow_duplicate=True),
    [Input("url-sync-applied", "data")] + [Input(p.cid, p.prop) for p in params]
      + [Input("location-selected", "data")],
    [State("locations-list", "data"), State("url", "search")],
    prevent_initial_call=True,
)
```

Serialises lat/lon (looked up from `locations-list` by `location-selected[0]["value"]`, the same
lookup [location_selector_callbacks.py](src/components/location_selector_callbacks.py) does in
`add_point_on_map`) plus every param, and pushes the full query string to a single global store.
Because the writer replaces the whole string, stale params from a previously visited page are
cleared on mount.

Two details that matter, both found while testing:

- The writer is driven by `url-sync-applied`, **not** by the mount trigger directly. Sharing the
  trigger would let the writer run in the same batch as the reader and briefly rewrite the address
  bar with the page's default values before the incoming link had been applied.
- When no location is selected yet it falls back to `coords_from_search(url.search)`. On a fresh
  page load the location stores are populated by `load_cache` one step *after* the writer first
  runs, and without the fallback the address bar would drop `lat`/`lon` for that window — long
  enough for a reload or a copied URL to lose the location.

Each page's reader/writer only fire while that page's components are mounted, and are keyed on that
page's own stores.

### 2. `src/app.py` — three additions

- `dcc.Store(id="url-query")` (the query string on its way to the address bar) next to the existing
  stores in `serve_layout`, plus `*sync_stores()` — a per-page `url-sync-trigger` (this page just
  mounted) and `url-sync-applied` (reader → writer handshake), generated from the list of pages that
  called `register()`.
- One global callback announcing the mounted page. Every page carries exactly one `fade` Collapse
  with the same index as its stores, so `MATCH` pairs them and only the mounted page fires — which
  means **no page layout has to change at all**:

```python
@callback(
    Output({"type": "url-sync-trigger", "index": MATCH}, "data"),
    Input({"type": "fade", "index": MATCH}, "id"),
)
def fire_url_sync(_):
    return str(uuid.uuid4())   # fresh token, so re-mounting a page always re-syncs
```

- One global clientside callback (mirroring the style of the existing scroll/back-to-top ones):

```python
clientside_callback(
    """function(qs) {
        if (qs === undefined || qs === null) { return window.dash_clientside.no_update; }
        window.history.replaceState(null, '', window.location.pathname + qs);
        return null;
    }""",
    Output("dummy-data", "data", allow_duplicate=True),
    Input("url-query", "data"),
    prevent_initial_call=True,
)
```

`replaceState` deliberately bypasses `dcc.Location`, so toggling a switch adds no history entry. The
side effect is that the `url.search` **prop** goes stale after edits; harmless, because the reader
only consumes it at page mount and the writer immediately re-normalises it.

### 3. Location: surgical changes in `src/components/location_selector_callbacks.py`

Extract the ~30-line DataFrame block that is **already duplicated verbatim** in `map_click`
([:266-292](src/components/location_selector_callbacks.py#L266-L292)) and
`update_location_with_geolocate` ([:333-361](src/components/location_selector_callbacks.py#L333-L361))
into one helper:

```python
def location_from_coords(lat, lon, elevation=None):
    """Build a one-row locations DataFrame from bare coordinates."""
    place = get_place_address_reverse(lon, lat)          # @cache.memoize(3600)
    ...  # id=create_unique_id(lat, lon, place["name"]), elevation=elevation or get_elevation(...)
```

Rewrite both existing callbacks to call it (net code *reduction*), then reuse it for the URL path.

Then extend the existing `load_cache` ([:72-98](src/components/location_selector_callbacks.py#L72-L98))
rather than adding a competing callback — it already owns `location_search_new.options`/`value`
non-duplicately and already fires on `Input("url","pathname")`:

- add `State("url", "search")` and `Output("locations-list", "data")`;
- if `lat`/`lon` are present in the search: `location_from_coords(...)`, concat with favorites,
  `create_options(...)`, and return that location's id as the value — **URL wins over the cached
  selection**;
- short-circuit: if the currently selected location's lat/lon already round-trip to the URL's
  4-decimal pair, keep the cached path and skip the geocode entirely (avoids re-geocoding on every
  intra-app navigation);
- otherwise behaviour is byte-for-byte what it is today.

Writing `locations-list` from `load_cache` is what makes the downstream page callbacks work — they
all do `locations[locations["id"] == location[0]["value"]]` and would otherwise `.item()` on an
empty frame. This requires flipping ownership of that output: add `allow_duplicate=True` to
`suggest_locs_dropdown`'s `Output("locations-list","data")`
([:104](src/components/location_selector_callbacks.py#L104)) — it already has
`prevent_initial_call=True`, so it is a one-word change.

Setting `location_search_new.value` then triggers the untouched `save_selected_into_cache`, which
does its normal favourites bookkeeping and populates `location-selected`; `activate_submit_button`
([app.py:271](src/app.py#L271)) then enables Submit on its own. No new code needed for either.

## Existing-callback conflicts to resolve (only one)

Because every reader output uses `allow_duplicate`, existing owners of those props keep their plain
outputs and need no change — `constrain_days_minutely_15`
([forecasts/callbacks.py](src/pages/forecasts/callbacks.py)) still clamps `forecast-days.value`
exactly as before. One case still has to yield, because it is a genuine clobber rather than an
ownership question:

**[model_climate_daily/callbacks.py](src/pages/model_climate_daily/callbacks.py)** `update_max_date`
wrote both `year-selection-climate.value` and `.max` on initial call, unconditionally resetting the
year to today's. **The `value` output is dropped**, keeping only `max`. The reader supplies `value`,
falling back to `date.today().year` when `?year=` is absent (the page's `NumberInput` has no
`value=`, so the reader's default is now the single source of the initial year).

Everything else (`disable_models`, `update_max_date` in `model_climate`, all the blur clientside
callbacks) is untouched.

## Three risks, resolved

### `URL_BASE_PATHNAME` (default `/pointwx/`, env-overridable)

Safe, and deliberately so:

- **Reading** only ever parses `url.search`. The query string is independent of the path, and the
  reader is triggered by the page's `{"type":"fade","index":...}` mount, not by matching a pathname —
  so it never has to know the base path.
- **Writing** uses `window.location.pathname` in the clientside shim, which is whatever the browser
  currently shows (`/pointwx/forecasts`, or `/whatever/forecasts` if the env var is changed). This is
  strictly more robust than reconstructing the path from `dcc.Location.pathname` or from
  `page["relative_path"]`, and it also survives being served behind a proxy prefix.
- Nothing in the design compares or constructs a pathname, so `update_navbar_links`
  ([app.py:241](src/app.py#L241)), which does exact `pathname == relative_path` matching, is
  untouched — a query string is not part of `pathname`.

Verification step 8 below covers this by running with a non-default `URL_BASE_PATHNAME`.

### 4-decimal lat/lon precision

Yes, comfortably. 1e-4° ≈ **11 m** of latitude and ≈ 8 m of longitude at 45°N. More to the point,
[`create_unique_id`](src/utils/mapbox_api.py#L68) already normalises to `f"{lat:.4f}{lon:.4f}{name}"`
before hashing, so 4 decimals is *exactly* the precision the app's own location identity is built on
— carrying more digits in the URL would produce stored coordinates that no longer match the id they
generated. And the open-meteo model grids being sampled are 1–11 km, so 11 m is three orders of
magnitude finer than anything that could change a forecast. Rounding also makes shared links collide
on the `@cache.memoize` key for `get_place_address_reverse`/`get_elevation`, which is the point.

### Persistence vs. URL params on a slow load

Two distinct orderings, only one of which was ever a real risk:

1. **Persistence vs. the reader** — not a race. Dash applies persisted values synchronously in the
   renderer when the component mounts; the reader is triggered *by* that mount and its response
   necessarily arrives afterwards. The order is deterministic no matter how slow the connection,
   and a callback-set value on a persisted prop is recorded as the new persisted value, so the two
   stay consistent.
2. **The reader vs. the user typing during the load window** — this was the genuine hazard, and it
   is why the reader returns `no_update` for every key the URL does *not* name. A late-arriving
   reader response can therefore only overwrite a control that the shared link explicitly set, and
   only if the user changed that exact control within the few hundred ms before the response landed.
   For every other control, persistence and user input are simply left alone. This is also why the
   writer is driven by the `url-sync-ready` handshake rather than by prop changes: it still
   normalises the URL even when the reader wrote nothing at all.

With that change, `persistence="true"` needs no modification anywhere.

## Per-page specs

Each page's `options_selector.py` gains an import and a `register(...)` call at the bottom. No
layout file changes.

| page | fade index | keys |
|---|---|---|
| forecasts | `deterministic` | `models`(list) `fromnow` `min15` `days` |
| forecasts_heatmap | `deterministic-heatmap` | `models`(list) `var` `fromnow` `min15` `heatmap` `days` |
| ensemble | `ensemble` | `model` `clima` `fromnow` `clouds` |
| ensemble_heatmap | `heatmap` | `model` `var` `decimate` `fromnow` `heatmap` |
| meteogram | `meteogram` | `model` |
| vertical | `vertical` | `model` `fromnow` `heatmap` `days` |
| model_climate | `monthly` | `model` `start` `end` (from `date-range-climate`, a 2-element list) |
| model_climate_daily | `daily` | `model` `year` `accvar` `instvar` |
| climate_calendar | `calendar` | `model` `graph` `year` |

`chatbot` and `home` are skipped (no location selector, nothing meaningful to sync).

Validation lists reuse what already exists in [settings.py](src/utils/settings.py):
`DETERMINISTIC_MODELS`, `DETERMINISTIC_VARS`, `ENSEMBLE_MODELS`, `ENSEMBLE_VARS`,
`REANALYSIS_MODELS`, plus the two inline lists in `model_climate_daily/options_selector.py`. The
inline graph list in `climate_calendar/options_selector.py` was lifted to a module-level
`graph_options` so it can be reused for validation instead of being duplicated.

## Files touched

- **New**: `docs/plans/url-query-params.md` (this document).
- **New**: `src/utils/url_sync.py` — the whole mechanism.
- `src/app.py` — three `dcc.Store`s, the page-mount announcer, the replaceState clientside callback.
- `src/components/location_selector_callbacks.py` — extract `location_from_coords` (removing a block
  that was duplicated verbatim between `map_click` and `update_location_with_geolocate`), extend
  `load_cache` with the `?lat`/`?lon` path, one `allow_duplicate` on `suggest_locs_dropdown`.
- 9 × `options_selector.py` (import + `register` call). No layout files.
- `src/pages/model_climate_daily/callbacks.py` — the `update_max_date` fix above.

## Verification

There are no tests or linter in this repo. The server-side half was verified by driving the real
callbacks over `_dash-update-component` (see the notes at the end); what is listed below still needs
a browser, because the address-bar rewrite and the history behaviour are clientside.

Run `python src/app.py` (serves `http://localhost:8083/pointwx/`) and check, in order:

1. **No regression first.** With an empty query string, every page behaves exactly as before: typing
   ≥4 chars searches, selecting fills the dropdown and enables Submit, favourites still cap at 5, the
   map marker still appears, page navigation still restores the last location, Submit still plots.
2. **Write.** Open `/pointwx/forecasts`, pick a location, toggle *From now on*, set days to 3, add a
   model. The address bar updates live to
   `?lat=..&lon=..&models=..&days=3&fromnow=0`. Press Back once → you leave the page (no history
   spam from the toggles).
3. **Read.** Copy that URL into a **private window** (empty `localStorage`, the real share scenario).
   Controls and the location dropdown come up pre-filled, Submit is enabled, **no figure is
   rendered** until clicked. Verify the plotted location matches, i.e. `locations-list` was populated
   — this is the failure mode to watch for.
4. **Round-trip every page** using the table above, including `model_climate` (date range) and
   `model_climate_daily` (`?year=1998` must survive `update_max_date`, previously the clobber case).
5. **Garbage tolerance.** `?model=not_a_model&days=999&lat=abc` must fall back to defaults silently,
   never a traceback or an error modal.
6. **Cross-page.** Land on a URL with `?days=7`, navigate to `/ensemble`: the query string is
   rewritten to ensemble's own keys, location preserved.
7. **Cost.** Reload a shared URL several times with `DISABLE_CACHE` unset and confirm from the logs
   that no open-meteo forecast request fires until Submit, and that the Mapbox reverse-geocode is
   served from the memoize cache after the first hit.
8. **Base path.** Restart with `URL_BASE_PATHNAME=/wxtest/ python src/app.py`, repeat steps 2–3 at
   `http://localhost:8083/wxtest/`, and confirm the rewritten URL keeps the `/wxtest/` prefix and the
   navbar active-link highlighting still works.
9. **Persistence.** With a persisted model selection already in `localStorage`, open a shared link
   that specifies a *different* model → the URL wins for that key. Open one that specifies no model →
   the persisted value survives and is then reflected into the URL by the writer. Throttle the
   network in devtools and confirm typing during the load window is not clobbered for keys the URL
   does not name.

Per CLAUDE.md, any throwaway verification script must start with `from app import app` to initialise
the cache.

### Already verified server-side

Checked by POSTing to `_dash-update-component` against a running dev server, i.e. exercising the
registered callbacks rather than the helpers in isolation:

- decode/encode of every kind (`str`, `int`, `bool`, `list`, `daterange`), including clamping,
  whitelisting against the settings option lists, and every garbage input falling back to
  "leave the selector alone";
- the reader applying a full query string on `forecasts`, and leaving unnamed keys untouched;
- readers for `calendar`, `monthly` and `daily`, including `?year=1998` surviving `update_max_date`
  and the current-year default when the URL is silent;
- the writer producing `?lat=45.4642&lon=9.1900&models=…&fromnow=0&min15=1&days=3`, keeping the
  incoming link's coordinates while the location stores catch up, and preferring the store once
  populated;
- reader → writer → reader being idempotent;
- both halves no-op'ing for a page other than the one mounted;
- `load_cache`: URL coordinates winning over the cached selection, the short-circuit when the
  selection already sits on those coordinates, and garbage coordinates falling through to the
  cached path;
- `_options_from_coords` round-tripping through the real Mapbox reverse geocode
  (45.4642, 9.19 → "Duomo (🇮🇹| 9.2E, 45.5N, 147m)") with a stable 6-digit id;
- the app importing with no `DuplicateCallbackOutput`, serving under both `/pointwx/` and a
  non-default `URL_BASE_PATHNAME=/wxtest/`, and issuing **zero** open-meteo forecast requests
  throughout;
- `scripts/check_dup_outputs.py` reporting 166 distinct outputs across 73 callbacks with no
  duplicate claims (it reports 5 collisions against the first, broken version — see the trap above).
