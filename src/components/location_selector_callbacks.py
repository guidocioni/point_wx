from dash import callback, Output, Input, State, no_update, html, dcc
from utils.openmeteo_api import get_locations, get_elevation
from utils.mapbox_api import get_place_address_reverse
from dash.exceptions import PreventUpdate
from utils.figures_utils import make_map
from utils.flags import byCode, byName
import pandas as pd
import dash_leaflet as dl


@callback(
    [
        Output("locations", "options"),
        Output("locations", "value"),
        Output("locations-list", "data"),
        Output("locations-selected", "data"),
        Output("error-message", "children"),
        Output("error-modal", "is_open"),
    ],
    Input("search-button", "n_clicks"),
    [
        State("location_search", "value"),
        State("locations-list", "data"),
        State("locations-selected", "data"),
    ],
)
def get_closest_address(n_clicks, location_search, locations, locations_sel):
    if n_clicks is None:
        # In this case it means that the button has not been clicked
        # so we first check if there are already some locations
        # saved in the cache
        # If there is no data in the cache, locations will be an empty dict
        if len(locations) > 0:
            locations = pd.read_json(locations, orient="split", dtype={"id": str})
        else:
            # In this case it means the button has not been clicked AND
            # there is no data in the Store component
            raise PreventUpdate
    else:
        # In this case the button has been clicked so we load the data
        locations = get_locations(location_search)
        # If no location has been found raise an error
        if len(locations) < 1:
            return (
                no_update,
                no_update,
                no_update,
                no_update,
                "No location found, change the input!",  # Error message
                True,
            )

    options = []
    for _, row in locations.iterrows():
        options.append(
            {
                "label": (
                    f"{row['name']} ({byName(row['country'])} | {row['longitude']:.1f}E, "
                    f"{row['latitude']:.1f}N, {row['elevation']:.0f}m)"
                ),
                "value": str(row["id"]),
            }
        )
    if len(locations_sel) > 0 and n_clicks is None:
        # there was something already selected
        return (
            options,
            # Set the dropdown on the value saved in the Store cache
            locations_sel["value"],
            # locations saved in Store cache
            locations.to_json(orient="split"),
            no_update,  # DO not update the value saved in Store cache
            None,
            False,  # Deactivate error popup
        )
    else:
        # there was nothing in the cache so we revert to the first value, and save it
        return (
            options,
            options[0]["value"],
            locations.to_json(orient="split"),  # locations saved in Store
            {"value": options[0]["value"]},  # selected location saved in Store
            None,
            False,  # Deactivate error popup
        )


@callback(
    Output("geo", "children"), Input("geolocate", "n_clicks"), prevent_initial_call=True
)
def start_geolocation_section(n):
    return html.Div(
        [
            dcc.Geolocation(id="geolocation"),
        ]
    )


@callback(
    Output("geolocation", "update_now"),
    Input("geolocate", "n_clicks"),
)
def update_now(click):
    if not click:
        raise PreventUpdate
    else:
        return True


# Draw the empty map
# Points will be added in a different callbacks
@callback(
    Output("map-div", "children"),
    Input("map-accordion", "active_item"),
)
def create_map(item):
    if item is not None and item == "item-0":
        return make_map()
    else:
        raise PreventUpdate


# Add point on the map when a location is chosen
@callback(
    [Output("map-scatter-layer", "children"), Output("map", "center")],
    [Input("locations-list", "data"), Input("locations", "value")],
)
def add_point_on_map(locations, location):
    locations = pd.read_json(locations, orient="split", dtype={"id": str})
    loc = locations[locations["id"] == location]

    return (
        dl.Marker(position=[loc["latitude"].item(), loc["longitude"].item()]),
        [loc["latitude"].item(), loc["longitude"].item()],
    )


# When clicking on the map
# 1 - show a marker on the map
# 2 - update the selected location with the coordinates
#     of the point clicked
@callback(
    [
        Output("map-scatter-layer", "children", allow_duplicate=True),
        Output("locations", "options", allow_duplicate=True),
        Output("locations", "value", allow_duplicate=True),
        Output("locations-list", "data", allow_duplicate=True),
        Output("locations-selected", "data", allow_duplicate=True),
        Output("location_search", "value", allow_duplicate=True),
    ],
    [Input("map", "click_lat_lng"), Input("map", "clickData")],
    prevent_initial_call=True,
)
def map_click(click_lat_lng, clickData):
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
                "id": 9999999999,
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
        for _, row in locations.iterrows():
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
            dl.Marker(position=[lat, lon]),
            options,
            options[0]["value"],
            locations.to_json(orient="split"),  # locations saved in Store
            {"value": options[0]["value"]},  # selected location saved in Store
            "",
        )
    else:
        raise PreventUpdate


@callback(
    [
        Output("locations", "options", allow_duplicate=True),
        Output("locations", "value", allow_duplicate=True),
        Output("locations-list", "data", allow_duplicate=True),
        Output("locations-selected", "data", allow_duplicate=True),
        Output("location_search", "value", allow_duplicate=True),
    ],
    [
        Input("geolocation", "local_date"),  # need it just to force an update!
        Input("geolocation", "position"),
    ],
    State("geolocate", "n_clicks"),
    prevent_initial_call=True,
)
def update_location_with_geolocate(_, pos, n_clicks):
    if pos and n_clicks:
        lat = pd.to_numeric(pos["lat"])
        lon = pd.to_numeric(pos["lon"])
        place_details = get_place_address_reverse(lon, lat)
        locations = pd.DataFrame(
            {
                "id": 9999999999,
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
        for _, row in locations.iterrows():
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
            {"value": options[0]["value"]},  # selected location saved in Store
            "",
        )
    else:
        raise PreventUpdate


@callback(
    Output("locations-selected", "data", allow_duplicate=True),
    Input("locations", "value"),
    prevent_initial_call=True,
)
def update_locations_value_selected(value):
    return {"value": value}
