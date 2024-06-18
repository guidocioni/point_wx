from dash import callback, Output, Input, State, no_update, clientside_callback
from utils.openmeteo_api import get_ensemble_data, compute_climatology
from utils.suntimes import find_suntimes
from utils.custom_logger import logging
from .figures import make_subplot_figure, make_barpolar_figure
from components import location_selector_callbacks
import pandas as pd
from io import StringIO


@callback(
    [Output('ensemble-plot', "figure"),
     #  Output("polar-plot", "figure"),
     Output("error-message", "children", allow_duplicate=True),
     Output("error-modal", "is_open", allow_duplicate=True)],
    Input({"type":"submit-button", "index": "ensemble"}, "n_clicks"),
    [State("locations-list", "data"),
     State("location-selected", "data"),
     State("models-selection", "value"),
     State("clima-switch", "value")],
    prevent_initial_call=True
)
def generate_figure(n_clicks, locations, location, model, clima_):
    if n_clicks is None:
        return no_update, no_update, no_update

    # unpack locations data
    locations = pd.read_json(StringIO(locations), orient='split', dtype={"id": str})
    loc = locations[locations['id'] == location[0]['value']]

    try:
        data = get_ensemble_data(latitude=loc['latitude'].item(),
                                 longitude=loc['longitude'].item(),
                                 model=model,
                                 decimate=True,
                                 from_now=True)

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

        loc_label = location[0]['label'].split("|")[0] + (
            f"|📍 {float(data.attrs['longitude']):.1f}E"
            f", {float(data.attrs['latitude']):.1f}N, {float(data.attrs['elevation']):.0f}m | "
            f"Ens: {model.upper()}"
        )

        return (
            make_subplot_figure(data, clima, loc_label, sun),
            # make_barpolar_figure(data),
            None, False  # deactivate error popup
        )

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
                }, 200); // in milliseconds
            }
        return null;
    }
    """,
    Output('garbage', 'data'),
    # Input({"type":"submit-button", "index": "ensemble"}, 'n_clicks'),
    Input('ensemble-plot', 'figure'),
    [State('ensemble-plot', 'id')],
    prevent_initial_call=True
)
