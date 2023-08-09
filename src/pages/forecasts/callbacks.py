from dash import callback, Output, Input, State
from utils.openmeteo_api import get_forecast_data
from .figures import make_empty_figure, make_subplot_figure
import pandas as pd


@callback(
    Output("submit-button-deterministic", "disabled"),
    Input("locations", "value"),
)
def activate_submit_button(location):
    if len(location) >= 2:
        return False
    else:
        return True


@callback(
    Output("forecast-plot", "figure"),
    Input("submit-button-deterministic", "n_clicks"),
    [State("locations-list", "data"),
     State("locations", "value"),
     State("models-selection-deterministic", "value")]
)
def generate_figure(n_clicks, locations, location, models):
    if n_clicks is None:
        return make_empty_figure()

    # unpack locations data
    locations = pd.read_json(locations, orient='split')
    loc = locations[locations['id'] == location['value']]

    data = get_forecast_data(latitude=loc['latitude'].item(),
                             longitude=loc['longitude'].item(),
                             model=",".join(models))

    fig = make_subplot_figure(data)

    return fig
