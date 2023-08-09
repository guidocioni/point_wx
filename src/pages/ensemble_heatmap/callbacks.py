from dash import callback, Output, Input, State
from utils.openmeteo_api import get_ensemble_data
from .figures import make_empty_figure, make_heatmap
import pandas as pd


@callback(
    Output("submit-button-heatmap", "disabled"),
    Input("locations", "value"),
    prevent_initial_call=True
)
def activate_submit_button(location):
    if location:
        return False


@callback(
    Output("ensemble-plot-heatmap", "figure"),
    Input("submit-button-heatmap", "n_clicks"),
    [State("locations-list", "data"),
     State("locations", "value"),
     State("models-selection-heatmap", "value"),
     State("variable-selection-heatmap", "value")]
)
def generate_figure(n_clicks, locations, location, model, variable):
    if n_clicks is None:
        return make_empty_figure()

    # unpack locations data
    locations = pd.read_json(locations, orient='split')
    loc = locations[locations['id'] == location['value']]

    data = get_ensemble_data(latitude=loc['latitude'].item(),
                             longitude=loc['longitude'].item(),
                             model=model)

    fig = make_heatmap(data, var=variable)

    return fig
