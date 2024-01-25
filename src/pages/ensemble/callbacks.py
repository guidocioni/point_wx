from dash import callback, Output, Input, State, no_update
from utils.openmeteo_api import get_locations, get_ensemble_data, compute_climatology
from utils.suntimes import find_suntimes
from dash.exceptions import PreventUpdate
from .figures import make_subplot_figure, make_barpolar_figure
import pandas as pd


@callback(
    [Output("locations", "options"),
     Output("locations", "value"),
     Output("locations-list", "data"),
     Output("locations-selected", "data"),
     Output("error-message", "children"),
     Output("error-modal", "is_open")],
    Input("search-button", "n_clicks"),
    [State("from_address", "value"),
     State("locations-list", "data"),
     State("locations-selected", "data")]
)
def get_closest_address(n_clicks, from_address, locations, locations_sel):
    if n_clicks is None:
        # In this case it means that the button has not been clicked
        # so we first check if there are already some locations
        # saved in the cache
        # If there is no data in the cache, locations will be an empty dict
        if len(locations) > 0:
            locations = pd.read_json(
                locations, orient='split', dtype={"id": str})
        else:
            # In this case it means the button has not been clicked AND
            # there is no data in the Store component
            raise PreventUpdate
    else:
        # In this case the button has been clicked so we load the data
        locations = get_locations(from_address)
        # If no location has been found raise an error
        if len(locations) < 1:
            return (
                no_update, no_update, no_update, no_update,
                "No location found, change the input!",  # Error message
                True
            )

    options = []
    for _, row in locations.iterrows():
        options.append(
            {
                "label": (
                    f"{row['name']} ({row['country']} | {row['longitude']:.1f}E, "
                    f"{row['latitude']:.1f}N, {row['elevation']:.0f}m)"
                ),
                "value": str(row['id'])
            }
        )
    if len(locations_sel) > 0 and n_clicks is None:
        # there was something already selected
        return (
            options,
            # Set the dropdown on the value saved in the Store cache
            locations_sel['value'],
            # locations saved in Store cache
            locations.to_json(orient='split'),
            no_update,  # DO not update the value saved in Store cache
            None, False  # Deactivate error popup
        )
    else:
        # there was nothing in the cache so we revert to the first value, and save it
        return (
            options, options[0]['value'],
            locations.to_json(orient='split'),  # locations saved in Store
            {'value': options[0]['value']},  # selected location saved in Store
            None, False  # Deactivate error popup
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


@callback(
    [Output("locations", "options", allow_duplicate=True),
     Output("locations", "value", allow_duplicate=True),
     Output("locations-list", "data", allow_duplicate=True),
     Output("locations-selected", "data", allow_duplicate=True),
     Output("from_address", "value")],
    [Input("geolocation", "local_date"),
     Input("geolocation", "position")],
    State("geolocate", "n_clicks"),
    prevent_initial_call=True
)
def display_output(date, pos, n_clicks):
    if pos and n_clicks:
        locations = pd.DataFrame({"id": 9999999999, "name": "Custom location", "latitude": pd.to_numeric(pos['lat']),
                                  "longitude": pd.to_numeric(pos['lon']), "elevation": float(pos['alt']) if pos['alt'] else 0,
                                  "feature_code": "", "country_code": "", "admin1_id": "",
                                  "admin3_id": "", "admin4_id": "", "timezone": "", "population": 0,
                                  "postcodes": [""], "country_id": "", "country": "",
                                  "admin1": "", "admin3": "", "admin4": ""})
        options = []
        for _, row in locations.iterrows():
            options.append(
                {
                    "label": (
                        f"{row['name']} ({row['country']} | {row['longitude']:.1f}E, "
                        f"{row['latitude']:.1f}N, {row['elevation']:.0f}m)"
                    ),
                    "value": str(row['id'])
                }
            )
        return (
            options, options[0]['value'],
            locations.to_json(orient='split'),  # locations saved in Store
            {'value': options[0]['value']},  # selected location saved in Store
            ""
        )
    else:
        raise PreventUpdate


@callback(
    Output("locations-selected", "data", allow_duplicate=True),
    Input("locations", "value"),
    prevent_initial_call=True
)
def update_locations_value_selected(value):
    return {'value': value}


@callback(
    Output("submit-button", "disabled"),
    [Input("locations", "value"),
     Input("search-button", "n_clicks")],
)
def activate_submit_button(location, _nouse):
    if location is not None and len(location) >= 2:
        return False
    else:
        return True


@callback(
    Output("fade-ensemble", "is_open"),
    [Input("submit-button", "n_clicks")],
)
def toggle_fade(n):
    if not n:
        # Button has never been clicked
        return False
    return True


@callback(
    [Output("ensemble-plot", "figure"),
     #  Output("polar-plot", "figure"),
     Output("error-message", "children", allow_duplicate=True),
     Output("error-modal", "is_open", allow_duplicate=True)],
    Input("submit-button", "n_clicks"),
    [State("locations-list", "data"),
     State("locations", "value"),
     State("models-selection", "value"),
     State("clima-switch", "value")],
    prevent_initial_call=True
)
def generate_figure(n_clicks, locations, location, model, clima_):
    if n_clicks is None:
        return no_update, no_update, no_update

    # unpack locations data
    locations = pd.read_json(locations, orient='split', dtype={"id": str})
    loc = locations[locations['id'] == location]

    try:
        data = get_ensemble_data(latitude=loc['latitude'].item(),
                                 longitude=loc['longitude'].item(),
                                 model=model,
                                 decimate=True)

        if clima_:
            clima = compute_climatology(latitude=loc['latitude'].item(),
                                        longitude=loc['longitude'].item(),
                                        variables='temperature_2m')
        else:
            clima = None

        sun = find_suntimes(df=data,
                            latitude=loc['latitude'].item(),
                            longitude=loc['longitude'].item(),
                            elevation=loc['elevation'].item())

        loc_label = (
            f"{loc['name'].item()}, {loc['country'].item()} | 🌐 {float(data.attrs['longitude']):.1f}E"
            f", {float(data.attrs['latitude']):.1f}N, {float(data.attrs['elevation']):.0f}m | "
            f"Ens: {model.upper()}"
        )

        return (
            make_subplot_figure(data, clima, loc_label, sun),
            # make_barpolar_figure(data),
            None, False  # deactivate error popup
        )

    except Exception as e:
        return (
            no_update,
            repr(e), True  # Error message
        )
