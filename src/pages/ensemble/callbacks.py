from dash import callback, Output, Input, State, no_update
from utils.openmeteo_api import get_locations, get_ensemble_data, compute_climatology, get_forecast_daily_data
from utils.figures_utils import make_empty_figure
from dash.exceptions import PreventUpdate
from .figures import make_subplot_figure, make_barpolar_figure
import pandas as pd


@callback(
    [Output("locations", "options"),
     Output("locations", "value"),
     Output("locations-list", "data"),
     Output("locations-selected", "data")],
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
        return options, locations_sel['value'], locations.to_json(orient='split'), no_update
    else:
        # there was nothing in the cache so we revert to the first value, and save it
        return options, options[0]['value'], locations.to_json(orient='split'), {'value': options[0]['value']}


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
    if len(location) >= 2:
        return False
    else:
        return True


@callback(
    Output("fade-ensemble", "is_in"),
    [Input("submit-button", "n_clicks")],
)
def toggle_fade(n):
    if not n:
        # Button has never been clicked
        return False
    return True


@callback(
    [Output("ensemble-plot", "figure"),
     Output("polar-plot", "figure"),
     Output("error-message", "children"),
     Output("error-modal", "is_open")],
    Input("submit-button", "n_clicks"),
    [State("locations-list", "data"),
     State("locations", "value"),
     State("models-selection", "value")]
)
def generate_figure(n_clicks, locations, location, model):
    if n_clicks is None:
        return make_empty_figure(), make_empty_figure(), no_update, no_update

    # unpack locations data
    locations = pd.read_json(locations, orient='split', dtype={"id": str})
    loc = locations[locations['id'] == location]
    loc_label = (
        f"{loc['name'].item()} ({loc['country'].item()} | {float(loc['longitude'].item()):.1f}E"
        f", {float(loc['latitude'].item()):.1f}N, {float(loc['elevation'].item()):.0f}m)  -  "
        f"{model.upper()}"
    )

    try:
        data = get_ensemble_data(latitude=loc['latitude'].item(),
                                 longitude=loc['longitude'].item(),
                                 model=model)

        clima = compute_climatology(latitude=loc['latitude'].item(),
                                    longitude=loc['longitude'].item(),
                                    variables='temperature_2m')

        sun = get_forecast_daily_data(latitude=loc['latitude'].item(),
                                      longitude=loc['longitude'].item(),
                                      variables='sunrise,sunset',
                                      forecast_days=None,
                                      start_date=data.time.min().strftime('%Y-%m-%d'),
                                      end_date=data.time.max().strftime('%Y-%m-%d'))

        return make_subplot_figure(data, clima, loc_label, sun), make_barpolar_figure(data), None, False

    except Exception as e:
        return make_empty_figure(), make_empty_figure(), repr(e), True
