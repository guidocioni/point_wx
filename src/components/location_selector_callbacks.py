from dash import callback, Output, Input, State, no_update, html, dcc
from utils.openmeteo_api import get_locations, get_elevation
from utils.mapbox_api import get_place_address_reverse, create_unique_id
from dash.exceptions import PreventUpdate
from utils.figures_utils import make_map
from utils.flags import byCode, byName
import pandas as pd
import dash_leaflet as dl
from io import StringIO


@callback(
    [Output("location_search_new", "options"), Output("location_search_new", "value")],
    Input("url", "pathname"),
    [State("location-selected", "data"), State("locations-list", "data")],
)
def load_cache(_, location_selected, locations_list):
    '''
    Every time the URL of the app changes (which happens when we load or change page)
    then load the selected value (and options) into the app.
    Unfortunately the dropdown component does not persist all the values even
    on page change.
    '''
    cache_location_selected = no_update
    cache_locations_list = no_update

    if location_selected is not None and len(location_selected) == 1:
        cache_location_selected = location_selected[0]["value"]

    if locations_list is not None and len(locations_list) >= 1:
        locations_list = pd.read_json(
            StringIO(locations_list), orient="split", dtype={"id": str}
        )
        options = []
        for _, row in locations_list.iterrows():
            options.append(
                {
                    "label": (
                        f"{row['name']} ({byCode(row['country_code'])} | {row['longitude']:.1f}E, "
                        f"{row['latitude']:.1f}N, {row['elevation']:.0f}m)"
                    ),
                    "value": str(row["id"]),
                }
            )
        cache_locations_list = options

    return cache_locations_list, cache_location_selected


@callback(
    [
        Output("location_search_new", "options", allow_duplicate=True),
        Output("locations-list", "data"),
    ],
    Input("location_search_new", "search_value"),
    prevent_initial_call=True,
)
def suggest_locs_dropdown(value):
    """
    When the user types, update the dropdown with locations
    found with the API
    """
    if value is None or len(value) < 4:
        raise PreventUpdate
    locations = get_locations(value, count=5)
    if len(locations) == 0:
        raise PreventUpdate
    options = []
    for _, row in locations.iterrows():
        options.append(
            dict(
                label=(
                    f"{row['name']} ({byName(row['country'])} | {row['longitude']:.1f}E, "
                    f"{row['latitude']:.1f}N, {row['elevation']:.0f}m)"
                ),
                value=str(row["id"]),
            )
        )

    return options, locations.to_json(orient="split")


@callback(
    Output("location-selected", "data", allow_duplicate=True),
    Input("location_search_new", "value"),
    State("location_search_new", "options"),
    prevent_initial_call=True,
)
def save_selected_into_cache(selected_location, locations_options):
    '''
    When the user selects a location (doesn't matter how) 
    then save the selected value
    into the cache, so that we can load if we leave or change
    page. 
    '''
    if locations_options is None or len(locations_options) == 0:
        raise PreventUpdate
    return [o for o in locations_options if o["value"] == selected_location]


@callback(
    Output("geo", "children"), Input("geolocate", "n_clicks"), prevent_initial_call=True
)
def start_geolocation_section(n):
    '''
    Activate the Div containing the geolocation component, so that the permission is
    not requested at the beginning. If we want instead to always get the geolocation
    at load time we should remove this and add the Geolocation component directly
    into the app layout.
    '''
    return html.Div(
        [
            dcc.Geolocation(id="geolocation", high_accuracy=True),
        ]
    )


@callback(
    Output("geolocation", "update_now"),
    Input("geolocate", "n_clicks"),
)
def update_now(click):
    '''Trigger update of geolocation'''
    if not click:
        raise PreventUpdate
    else:
        return True


@callback(
    Output("map-div", "children"),
    Input("map-accordion", "active_item"),
)
def create_map(item):
    '''
    Draw the empty map
    Points will be added in a different callbacks
    '''
    if item is not None and item == "item-0":
        return make_map()
    raise PreventUpdate


@callback(
    [Output("map-scatter-layer", "children"), Output("map", "center")],
    Input("location_search_new", "value"),
    State("locations-list", "data"),
)
def add_point_on_map(location, locations):
    '''
    Add point marker on the map when a location is chosen.
    This could happen either from
    - user input (selecting option in dropdown)
    - geolocation
    - user clicks on the map
    '''
    if location is None:
        raise PreventUpdate

    locations = pd.read_json(StringIO(locations),
                             orient="split",
                             dtype={"id": str})
    loc = locations[locations["id"] == location]

    return (
        dl.Marker(position=[loc["latitude"].item(), loc["longitude"].item()]),
        [loc["latitude"].item(), loc["longitude"].item()],
    )


@callback(
    [
        Output("location_search_new", "options", allow_duplicate=True),
        Output("location_search_new", "value", allow_duplicate=True),
        Output("locations-list", "data", allow_duplicate=True),
    ],
    [Input("map", "click_lat_lng"), # We cover also an outdated Dash leaflet method
     Input("map", "clickData")],
    prevent_initial_call=True,
)
def map_click(click_lat_lng, clickData):
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
        place_details = get_place_address_reverse(lon, lat)
        locations = pd.DataFrame(
            {
                "id": create_unique_id(lat, lon, place_details["name"]), # Fake id just to have one
                "name": place_details["name"],
                "latitude": lat,
                "longitude": lon,
                "elevation": get_elevation(lat, lon),
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
        row = locations.iloc[0]
        options = [
            {
                "label": (
                    f"{row['name']} ({byCode(row['country_code'])} | {row['longitude']:.1f}E, "
                    f"{row['latitude']:.1f}N, {row['elevation']:.0f}m)"
                ),
                "value": str(row["id"]),
            }
        ]
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
    ],
    [
        Input("geolocation", "local_date"),  # need it just to force an update!
        Input("geolocation", "position"),
    ],
    State("geolocate", "n_clicks"),
    prevent_initial_call=True,
)
def update_location_with_geolocate(_, pos, n_clicks):
    '''
    When a new position with geolocation is obtained
    update the location selection
    '''
    if pos and n_clicks:
        lat = pd.to_numeric(pos["lat"])
        lon = pd.to_numeric(pos["lon"])
        place_details = get_place_address_reverse(lon, lat)
        locations = pd.DataFrame(
            {
                "id": create_unique_id(lat, lon, place_details["name"]), # Fake id just to have one
                "name": place_details["name"],
                "latitude": lat,
                "longitude": lon,
                "elevation": float(pos["alt"])
                if pos["alt"]
                else get_elevation(pos["lat"], pos["lon"]),
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
        row = locations.iloc[0]
        options = [
            {
                "label": (
                    f"{row['name']} ({byCode(row['country_code'])} | {row['longitude']:.1f}E, "
                    f"{row['latitude']:.1f}N, {row['elevation']:.0f}m)"
                ),
                "value": str(row["id"]),
            }
        ]
        return (
            options,
            options[0]["value"],
            locations.to_json(orient="split"),  # locations saved in Store
        )
    else:
        raise PreventUpdate

