from dash import callback, Output, Input, State, no_update, clientside_callback
from utils.openmeteo_api import get_ensemble_data
from utils.custom_logger import logging
from .figures import make_heatmap
import pandas as pd


@callback(
    Output("submit-button-heatmap", "disabled"),
    Input("location_search_new", "value"),
)
def activate_submit_button(location):
    if location is None:
        return True
    return False


@callback(
    Output("fade-heatmap", "is_open"),
    [Input("submit-button-heatmap", "n_clicks")],
)
def toggle_fade(n):
    if not n:
        # Button has never been clicked
        return False
    return True


@callback(
    [Output("ensemble-plot-heatmap", "figure"),
     Output("error-message", "children", allow_duplicate=True),
     Output("error-modal", "is_open", allow_duplicate=True)],
    Input("submit-button-heatmap", "n_clicks"),
    [State("locations-list", "data"),
     State("location-selected", "data"),
     State("models-selection-heatmap", "value"),
     State("variable-selection-heatmap", "value")],
    prevent_initial_call=True
)
def generate_figure(n_clicks, locations, location, model, variable):
    if n_clicks is None:
        return no_update, no_update, no_update

    # unpack locations data
    locations = pd.read_json(locations, orient='split', dtype={"id": str})
    loc = locations[locations['id'] == location[0]['value']]

    try:
        data = get_ensemble_data(latitude=loc['latitude'].item(),
                                 longitude=loc['longitude'].item(),
                                 model=model,
                                 decimate=True,
                                 from_now=True)

        loc_label = location[0]['label'].split("|")[0] + (
            f"|📍 {float(data.attrs['longitude']):.1f}E"
            f", {float(data.attrs['latitude']):.1f}N, {float(data.attrs['elevation']):.0f}m | "
            f"{variable} | "
            f"Ens: {model.upper()}"
        )

        return make_heatmap(data, var=variable, title=loc_label), None, False

    except Exception as e:
        logging.error(
            f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")
        return (
            no_update,
            "An error occurred when processing the data",
            True  # Error message
        )


clientside_callback(
    """
    function(n_clicks, element_id) {
            var targetElement = document.getElementById(element_id);
            if (targetElement) {
                setTimeout(function() {
                    targetElement.scrollIntoView({ behavior: 'smooth' });
                }, 800); // in milliseconds
            }
        return null;
    }
    """,
    Output('garbage', 'data', allow_duplicate=True),
    Input('submit-button-heatmap', 'n_clicks'),
    [State('ensemble-plot-heatmap', 'id')],
    prevent_initial_call=True
)
