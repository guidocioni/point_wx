from dash import callback, Output, Input, State, no_update
from utils.openmeteo_api import get_forecast_data, get_forecast_daily_data
from utils.figures_utils import make_empty_figure
from utils.suntimes import find_suntimes
from .figures import make_subplot_figure
import pandas as pd


@callback(
    Output("submit-button-deterministic", "disabled"),
    [Input("locations", "value"),
     Input("search-button", "n_clicks")],
)
def activate_submit_button(location, _nouse):
    if len(location) >= 2:
        return False
    else:
        return True


@callback(
    Output("fade-deterministic", "is_in"),
    [Input("submit-button-deterministic", "n_clicks")],
)
def toggle_fade(n):
    if not n:
        # Button has never been clicked
        return False
    return True


@callback(
    [Output("forecast-plot", "figure"),
     Output("error-message", "children", allow_duplicate=True),
     Output("error-modal", "is_open", allow_duplicate=True)],
    Input("submit-button-deterministic", "n_clicks"),
    [State("locations-list", "data"),
     State("locations", "value"),
     State("models-selection-deterministic", "value")],
    prevent_initial_call=True
)
def generate_figure(n_clicks, locations, location, models):
    if n_clicks is None:
        return make_empty_figure(), no_update, no_update

    # unpack locations data
    locations = pd.read_json(locations, orient='split', dtype={"id": str})
    loc = locations[locations['id'] == location]
    loc_label = (
        f"{loc['name'].item()} ({loc['country'].item()} | {float(loc['longitude'].item()):.1f}E"
        f", {float(loc['latitude'].item()):.1f}N, {float(loc['elevation'].item()):.0f}m)  -  "
        f'{",".join(models)}'
    )

    try:
        data = get_forecast_data(latitude=loc['latitude'].item(),
                                 longitude=loc['longitude'].item(),
                                 model=",".join(models),
                                 forecast_days=14)

        sun = find_suntimes(df=data,
                            latitude=loc['latitude'].item(),
                            longitude=loc['longitude'].item(),
                            elevation=loc['elevation'].item())

        return make_subplot_figure(data=data, title=loc_label, sun=sun, models=models), None, False
    except Exception as e:
        return make_empty_figure(), repr(e), True
