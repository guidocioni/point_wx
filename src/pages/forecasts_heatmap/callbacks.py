from dash import callback, Output, Input, State, no_update, clientside_callback
from utils.openmeteo_api import get_forecast_data
from utils.custom_logger import logging
from .figures import make_heatmap
import pandas as pd
from io import StringIO

@callback(
    [
        Output(dict(type="figure", id="deterministic-heatmap"), "figure"),
        Output("error-message", "children", allow_duplicate=True),
        Output("error-modal", "is_open", allow_duplicate=True),
    ],
    Input({"type": "submit-button", "index": "deterministic-heatmap"}, "n_clicks"),
    [
        State("locations-list", "data"),
        State("location-selected", "data"),
        State("models-selection-deterministic-heatmap", "value"),
        State("variable-selection-deterministic-heatmap", "value"),
    ],
    prevent_initial_call=True,
)
def generate_figure(n_clicks, locations, location, model, variable):
    if n_clicks is None:
        return no_update, no_update, no_update

    # unpack locations data
    locations = pd.read_json(StringIO(locations), orient="split", dtype={"id": str})
    loc = locations[locations["id"] == location[0]["value"]]

    try:
        data = get_forecast_data(
            latitude=loc["latitude"].item(),
            longitude=loc["longitude"].item(),
            model=model,
            variables=variable,
            from_now=True,
        )

        loc_label = location[0]["label"].split("|")[0] + (
            f"|📍 {float(data.attrs['longitude']):.1f}E"
            f", {float(data.attrs['latitude']):.1f}N, {float(data.attrs['elevation']):.0f}m)<br>"
            f"<sup>Variable = <b>{variable}</b> | "
            f"Models = <b>{", ".join(model)}</b></sup>"
        )
        return make_heatmap(data, var=variable, title=loc_label, models=model), None, False

    except Exception as e:
        logging.error(
            f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}"
        )
        return (
            no_update,
            "An error occurred when processing the data",
            True,  # Error message
        )


# Remove focus from dropdown once an element has been selected
clientside_callback(
    """
    function(value) {
        // Remove focus from the dropdown element
        document.activeElement.blur();
    }
    """,
    Input('variable-selection-deterministic-heatmap', 'value'),
    prevent_initial_call=True
)
