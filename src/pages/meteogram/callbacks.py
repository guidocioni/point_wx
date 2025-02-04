from dash import callback, Output, Input, State, no_update, clientside_callback
from utils.openmeteo_api import compute_daily_ensemble_meteogram, compute_climatology
from utils.figures_utils import get_weather_icons
from utils.settings import ASSETS_DIR
from utils.custom_logger import logging
from .figures import make_subplot_figure
import pandas as pd
from io import StringIO


@callback(
    [
        Output(dict(type="figure", id="meteogram"), "figure"),
        Output("error-message", "children", allow_duplicate=True),
        Output("error-modal", "is_open", allow_duplicate=True),
    ],
    Input({"type": "submit-button", "index": "meteogram"}, "n_clicks"),
    [
        State("locations-list", "data"),
        State("location-selected", "data"),
        State("models-selection-meteogram", "value"),
    ],
    prevent_initial_call=True,
)
def generate_figure(n_clicks, locations, location, model):
    if n_clicks is None:
        return no_update, no_update, no_update

    # unpack locations data
    locations = pd.read_json(StringIO(locations), orient="split", dtype={"id": str})
    loc = locations[locations["id"] == location[0]["value"]]

    try:
        data = compute_daily_ensemble_meteogram(
            latitude=loc["latitude"].item(),
            longitude=loc["longitude"].item(),
            model=model,
        ).reset_index()
        data = get_weather_icons(
            data,
        )
        # Add daily climatology (quite fast)
        clima = compute_climatology(
            latitude=loc["latitude"].item(),
            longitude=loc["longitude"].item(),
            daily=True,
            model="era5",
            variables="temperature_2m_max,temperature_2m_min,precipitation_sum,sunshine_duration",
        )
        clima = clima.rename(
            columns={
                "temperature_2m_max": "t_max_clima",
                "temperature_2m_min": "t_min_clima",
                "precipitation_sum": "daily_prec_clima",
                "sunshine_duration": "sunshine_clima",
            }
        )

        loc_label = location[0]["label"].split("|")[0] + (
            f"|📍 {float(data.attrs['longitude']):.1f}E"
            f", {float(data.attrs['latitude']):.1f}N, {float(data.attrs['elevation']):.0f}m)<br>"
            f"<sup>Ens = <b>{model.upper()}</b></sup>"
        )

        return make_subplot_figure(data, title=loc_label, clima=clima), None, False

    except Exception as e:
        logging.error(
            f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}. Parameters used model={model}"
        )
        return (
            no_update,
            "An error occurred when processing the data",
            True,  # Error message
        )


clientside_callback(
    """
    function(value) {
        // Remove focus from the dropdown element
        document.activeElement.blur();
    }
    """,
    Input('models-selection-meteogram', 'value'),
    prevent_initial_call=True
)
