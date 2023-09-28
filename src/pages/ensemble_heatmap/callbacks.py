from dash import callback, Output, Input, State, no_update
from utils.openmeteo_api import get_ensemble_data
from .figures import make_empty_figure, make_heatmap
import pandas as pd

@callback(
    Output("submit-button-heatmap", "disabled"),
    Input("locations", "value"),
)
def activate_submit_button(location):
    if len(location) >= 2:
        return False
    else:
        return True


@callback(
    [Output("ensemble-plot-heatmap", "figure"),
     Output("error-message", "children", allow_duplicate=True),
     Output("error-modal", "is_open", allow_duplicate=True)],
    Input("submit-button-heatmap", "n_clicks"),
    [State("locations-list", "data"),
     State("locations", "value"),
     State("models-selection-heatmap", "value"),
     State("variable-selection-heatmap", "value")],
    prevent_initial_call=True
)
def generate_figure(n_clicks, locations, location, model, variable):
    if n_clicks is None:
        return make_empty_figure(), no_update, no_update

    # unpack locations data
    locations = pd.read_json(locations, orient='split')
    loc = locations[locations['id'] == location['value']]

    try:
        data = get_ensemble_data(latitude=loc['latitude'].item(),
                                 longitude=loc['longitude'].item(),
                                 model=model)

        return make_heatmap(data, var=variable), None, False

    except Exception as e:
        return make_empty_figure(), repr(e), True
