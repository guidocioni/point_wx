from dash import html, callback, Output, Input, State, dcc
from utils.openmeteo_api import get_locations, get_ensemble_data, compute_climatology
from .figures import make_empty_figure, make_heatmap
import pandas as pd

@callback(
    [Output("locations-heatmap", "options"),
     Output("locations-heatmap", "value"),
     Output("locations-list-heatmap", "data")],
    Input("search-button-heatmap", "n_clicks"),
    State("from_address_heatmap", "value"),
    prevent_initial_call=True
)
def get_closest_address(n_clicks, from_address):
    if n_clicks is None:
        return []

    locations = get_locations(from_address)

    options = []
    for _, row in locations.iterrows():
        options.append(
            {
                "label": f"{row['name']} ({row['country']} | {row['longitude']:.1f}N, {row['latitude']:.1f}E, {row['elevation']:.0f}m)",
                "value": row['id']
            }
        )

    return options, options[0], locations.to_json(orient='split')


@callback(
    Output("submit-button-heatmap", "disabled"),
    Input("locations-heatmap", "value"),
    prevent_initial_call=True
)
def activate_submit_button(location):
    if location:
        return False


@callback(
    Output("ensemble-plot-heatmap", "figure"),
    Input("submit-button-heatmap", "n_clicks"),
    [State("locations-list-heatmap", "data"),
     State("locations-heatmap", "value"),
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
