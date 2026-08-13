from dash import callback, Output, Input, State, no_update, html, dcc, clientside_callback
from utils.mapbox_api import get_locations_mapbox, get_place_address_reverse, create_unique_id
from utils.openmeteo_api import get_elevation
from dash.exceptions import PreventUpdate
from utils.figures_utils import make_map
from utils.flags import flags_df
from utils.url_sync import coords_from_search, coords_of_selected
from utils.custom_logger import logging
import pandas as pd
import dash_leaflet as dl
from io import StringIO
from unidecode import unidecode


def location_from_coords(lat, lon, elevation=None):
    """Build a one-row locations DataFrame out of bare coordinates.

    Used by every path that produces a location without going through the search box:
    a click on the map, the geolocation button, and ?lat=..&lon=.. in the URL.
    The reverse geocoding and the elevation lookup are both cached (see mapbox_api and
    openmeteo_api), so repeatedly opening the same shared link is cheap.
    """
    place_details = get_place_address_reverse(lon, lat)
    return pd.DataFrame(
        {
            "id": create_unique_id(
                lat, lon, place_details["name"]
            ),  # Fake id just to have one
            "name": place_details["name"],
            "latitude": lat,
            "longitude": lon,
            "elevation": elevation if elevation is not None else get_elevation(lat, lon),
            "feature_code": "",
            "country_code": place_details["country_code"]
            if "country_code" in place_details
            else "",
            "admin1_id": "",
            "admin3_id": "",
            "admin4_id": "",
            "timezone": "",
            "population": 0,
            "postcodes": [""],
            "country_id": "",
            "country": place_details["country_name"]
            if "country_name" in place_details
            else "",
            "admin1": "",
            "admin3": "",
            "admin4": "",
        }
    )


def create_options(locations):
    """Helper function to create an options element
    for a dropdown component starting from a dataframe of locations.
    locations should always be a pd.Dataframe.
    Also take care of duplicates by smartly completing with region
    informations"""
    locations = locations.copy()
    locations["duplicated_name"] = locations.duplicated(
        subset=["country", "name"], keep=False
    )
    locations["duplicated_name_and_region"] = locations.duplicated(
        subset=["country", "name", "admin1"], keep=False
    )
    locations = locations.merge(
        flags_df[["code", "emoji", "unicode"]], left_on="country_code", right_on="code"
    )

    def formatter(x):
        # Add English transliteration if different from native name
        matching = x.get('matching_name', '')
        name_display = x['name']
        if matching and not pd.isna(matching) and matching != x['name']:
            name_display = f"{x['name']} ({matching})"

        return (
            f"{name_display}"
            f"{', '+ x['admin1'] if x['duplicated_name'] and not x['duplicated_name_and_region'] and 'admin1' in x and not pd.isna(x['admin1']) else ''}"
            f"{', '+ x['admin2'] if x['duplicated_name_and_region'] and 'admin2' in x and not pd.isna(x['admin2']) and x['name'] != x['admin2'] else ''}"
            f"{', '+ x['admin3'] if x['duplicated_name_and_region'] and 'admin2' in x and 'admin3' in x and pd.isna(x['admin2']) and not pd.isna(x['admin3']) else ''}"
            f" ({x['emoji']}| {x['longitude']:.1f}E, "
            f"{x['latitude']:.1f}N, {x['elevation']:.0f}m)"
        )

    locations["label"] = locations.apply(formatter, axis=1)
    locations["id"] = locations["id"].astype(str)

    # Create options with search field for better dropdown filtering
    # The 'search' property is used by Dash dropdown for matching user input
    options = []
    for _, row in locations.iterrows():
        # Use matching_name if available (Latin transliteration for CJK/Cyrillic)
        # Otherwise strip accents from the name
        matching = row.get("matching_name", "")
        # Handle NaN/None/empty cases - pandas can convert empty strings to NaN
        if pd.isna(matching) or not matching:
            search_text = str(row["name"])
        else:
            search_text = str(matching)

        option = {
            "value": row["id"],
            "label": row["label"],
            "search": unidecode(search_text)  # Strip accents for search
        }
        options.append(option)

    return options


@callback(
    [Output("locations-list", "data"), Output("url-location", "data")],
    Input("url", "pathname"),
    [
        State("url", "search"),
        State("location-selected", "data"),
        State("locations-list", "data"),
        State("locations-favorites", "data"),
    ],
)
def resolve_url_location(_, search, location_selected, locations_list, locations_favorites):
    """
    When the URL carries ?lat=..&lon=.. (a shared link), rebuild that location from the
    coordinates exactly like a click on the map would do, and put it in locations-list so
    that load_cache below and the page callbacks can find it.

    Both outputs are app-level stores on purpose. Dash only skips a callback when every
    one of its outputs is missing from the layout, so mixing these with the (page-level)
    dropdown would make this fire before the dropdown exists and be reported as writing
    to a nonexistent object.
    """
    lat, lon = coords_from_search(search)
    if lat is None:
        return no_update, None
    # Nothing to do if the cached selection already sits on those coordinates:
    # avoids a pointless geocode on every navigation within the app
    if (lat, lon) == coords_of_selected(locations_list, location_selected):
        return no_update, None
    try:
        locations = location_from_coords(lat, lon)
        target_id = str(locations["id"].iloc[0])
        if locations_favorites:
            favorites = pd.read_json(
                StringIO(locations_favorites), orient="split", dtype={"id": str}
            )
            locations = pd.concat([locations, favorites[favorites["id"] != target_id]])
        # create_options() inner-joins on the flags table, so a location the reverse
        # geocoding could not attach a country code to would silently vanish
        if not any(o["value"] == target_id for o in create_options(locations)):
            return no_update, None
        return locations.to_json(orient="split"), target_id
    except Exception as e:
        logging.warning(f"Could not build a location from URL coordinates {lat},{lon}: {e}")
        return no_update, None


@callback(
    [Output("location_search_new", "options"), Output("location_search_new", "value")],
    [Input("url", "pathname"), Input("url-location", "data")],
    [State("location-selected", "data"), State("locations-list", "data")],
)
def load_cache(_, url_location, location_selected, locations_list):
    """
    Every time the URL of the app changes (which happens when we load or change page)
    then load the selected value (and options) into the app.
    Unfortunately the dropdown component does not persist all the values even
    on page change.

    A location coming from the URL (resolved just above) wins over the cached selection.
    """
    cache_location_selected = no_update
    cache_locations_list = no_update

    if locations_list is not None and len(locations_list) >= 1:
        locations_list = pd.read_json(
            StringIO(locations_list), orient="split", dtype={"id": str}
        )
        cache_locations_list = create_options(locations_list)
        # Remove duplicates
        cache_locations_list = list({d['value']: d for d in cache_locations_list}.values())

    if url_location:
        cache_location_selected = url_location
    elif location_selected is not None and len(location_selected) >=1:
        cache_location_selected = location_selected[0]["value"]

    return cache_locations_list, cache_location_selected


@callback(
    [
        Output("location_search_new", "options", allow_duplicate=True),
        Output("locations-list", "data", allow_duplicate=True),
    ],
    Input("location_search_new", "search_value"),
    State("locations-favorites", "data"),
    prevent_initial_call=True,
)
def suggest_locs_dropdown(value, locations_favorites):
    """
    When the user types, update the dropdown with locations
    found with the API
    """
    if value is None or len(value) < 4:
        raise PreventUpdate
    locations = get_locations_mapbox(value, count=5)
    if locations_favorites:
        locations_favorites = pd.read_json(StringIO(locations_favorites), orient="split", dtype={"id": str})
        locations = pd.concat([locations, locations_favorites])
    if len(locations) == 0:
        raise PreventUpdate
    options = create_options(locations)

    return options, locations.to_json(orient="split")
    
    
@callback(
    [
        Output("location-selected", "data", allow_duplicate=True),
        Output("locations-favorites", "data"),
        Output("location_search_new", "options", allow_duplicate=True),
        Output("locations-list", "data", allow_duplicate=True)
    ],
    Input("location_search_new", "value"),
    [State("location_search_new", "options"),
     State("locations-favorites", "data"),
     State("locations-list", "data")],
    prevent_initial_call=True,
)
def save_selected_into_cache(selected_location, locations_options, locations_favorites, locations_list):
    """
    When the user selects an option in the dropdown
    - Add the selected location to the favorites list
    - Update the dropdown options so that they only contain the favorites (including the latest selected option)
    - Update the location-list store variable so that other functions can find the details
    """
    if locations_options is None or len(locations_options) == 0 or selected_location is None:
        raise PreventUpdate
    locations_list = pd.read_json(StringIO(locations_list), orient="split", dtype={"id": str})
    selected = [o for o in locations_options if o["value"] == selected_location]
    locations_list = locations_list[locations_list["id"] == selected[0]["value"]]

    if locations_favorites:
        locations_favorites = pd.read_json(StringIO(locations_favorites), orient="split", dtype={"id": str})
        if len(locations_list) > 0 and selected[0]["value"] not in locations_favorites['id'].unique():
            locations_favorites = pd.concat([locations_favorites, locations_list])
            # Ensure the favorite/recent list does not exceed a length of 5
            if len(locations_favorites) > 5:
                locations_favorites = locations_favorites[-5:]
    else:
        locations_favorites = locations_list
    
    options = create_options(locations_favorites)

    return [
        o for o in locations_options if o["value"] == selected_location
    ], locations_favorites.to_json(orient="split"), options, locations_favorites.to_json(orient="split")



@callback(
    Output("geo", "children"), Input("geolocate", "n_clicks"), prevent_initial_call=True
)
def start_geolocation_section(n):
    """
    Activate the Div containing the geolocation component, so that the permission is
    not requested at the beginning. If we want instead to always get the geolocation
    at load time we should remove this and add the Geolocation component directly
    into the app layout.
    """
    return html.Div(
        [
            dcc.Geolocation(id="geolocation", high_accuracy=True, show_alert=True),
        ]
    )


@callback(
    [Output("geolocation", "update_now"),
     Output("geolocate", "loading")],
    Input("geo", "children"),
    prevent_initial_call=True
)
def update_now(_children):
    """Trigger update of geolocation"""
    return True, True


@callback(
    Output("map-div", "children"),
    Input("map-accordion", "active_item"),
)
def create_map(item):
    """
    Draw the empty map
    Points will be added in a different callbacks
    """
    if item is not None and item == "item-0":
        return make_map()
    raise PreventUpdate


@callback(
    [Output("map-scatter-layer", "children"), Output("map", "viewport")],
    Input("location_search_new", "value"),
    State("locations-list", "data"),
)
def add_point_on_map(location, locations):
    """
    Add point marker on the map when a location is chosen.
    This could happen either from
    - user input (selecting option in dropdown)
    - geolocation
    - user clicks on the map
    """
    if location is None:
        raise PreventUpdate

    locations = pd.read_json(StringIO(locations), orient="split", dtype={"id": str})
    loc = locations[locations["id"] == location]

    return (
        dl.Marker(position=[loc["latitude"].item(), loc["longitude"].item()]),
        dict(center=[loc["latitude"].item(), loc["longitude"].item()], zoom=9)
    )


@callback(
    [
        Output("location_search_new", "options", allow_duplicate=True),
        Output("location_search_new", "value", allow_duplicate=True),
        Output("locations-list", "data", allow_duplicate=True),
    ],
    [
        Input("map", "click_lat_lng"),  # We cover also an outdated Dash leaflet method
        Input("map", "clickData"),
    ],
    State("locations-favorites", "data"),
    prevent_initial_call=True,
)
def map_click(click_lat_lng, clickData, locations_favorites):
    """
    When clicking on the map update the selected location with
    the coordinates of the point clicked
    """
    lat, lon = None, None
    if click_lat_lng is not None:
        lat = click_lat_lng[0]
        lon = click_lat_lng[1]
    elif clickData is not None:
        lat = clickData["latlng"]["lat"]
        lon = clickData["latlng"]["lng"]
    if lat is not None and lon is not None:
        locations = location_from_coords(lat, lon)
        if locations_favorites:
            locations_favorites = pd.read_json(StringIO(locations_favorites), orient="split", dtype={"id": str})
            locations = pd.concat([locations, locations_favorites])

        options = create_options(locations)

        return (
            options,
            options[0]["value"],
            locations.to_json(orient="split"),  # locations saved in Store
        )
    else:
        raise PreventUpdate


@callback(
    [
        Output("location_search_new", "options", allow_duplicate=True),
        Output("location_search_new", "value", allow_duplicate=True),
        Output("locations-list", "data", allow_duplicate=True),
        Output("geolocate", "loading", allow_duplicate=True),
    ],
    [
        Input("geolocation", "local_date"),  # need it just to force an update!
        Input("geolocation", "position"),
    ],
    [State("geolocate", "n_clicks"),
     State("locations-favorites", "data")],
    prevent_initial_call=True,
)
def update_location_with_geolocate(_, pos, n_clicks, locations_favorites):
    """
    When a new position with geolocation is obtained
    update the location selection
    """
    if pos and n_clicks:
        lat = pd.to_numeric(pos["lat"])
        lon = pd.to_numeric(pos["lon"])
        locations = location_from_coords(
            lat, lon, elevation=float(pos["alt"]) if pos["alt"] else None
        )
        if locations_favorites:
            locations_favorites = pd.read_json(StringIO(locations_favorites), orient="split", dtype={"id": str})
            locations = pd.concat([locations, locations_favorites])
        options = create_options(locations)

        return (
            options,
            options[0]["value"],
            locations.to_json(orient="split"),  # locations saved in Store
            False
        )
    else:
        raise PreventUpdate


# Remove focus from dropdown once an element has been selected
clientside_callback(
    """
    function(value) {
        // Remove focus from the dropdown element
        document.activeElement.blur();
    }
    """,
    Input('location_search_new', 'value'),
    prevent_initial_call=True
)
