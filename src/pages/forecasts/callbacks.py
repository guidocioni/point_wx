from dash import callback, Output, Input, State, no_update
from utils.openmeteo_api import get_forecast_data
from utils.suntimes import find_suntimes
from utils.custom_logger import logging
from .figures import make_subplot_figure
import pandas as pd
from io import StringIO


@callback(
    [
        Output(dict(type="figure", id="deterministic"), "figure"),
        Output("error-message", "children", allow_duplicate=True),
        Output("error-modal", "is_open", allow_duplicate=True),
    ],
    Input({"type": "submit-button", "index": "deterministic"}, "n_clicks"),
    [
        State("locations-list", "data"),
        State("location-selected", "data"),
        State("models-selection-deterministic", "value"),
    ],
    prevent_initial_call=True,
)
def generate_figure(n_clicks, locations, location, models):
    if n_clicks is None:
        return no_update, no_update, no_update

    # unpack locations data
    locations = pd.read_json(StringIO(locations), orient="split", dtype={"id": str})
    loc = locations[locations["id"] == location[0]["value"]]

    try:
        data = get_forecast_data(
            latitude=loc["latitude"].item(),
            longitude=loc["longitude"].item(),
            model=",".join(models),
            forecast_days=8,
        )

        sun = find_suntimes(
            df=data,
            latitude=loc["latitude"].item(),
            longitude=loc["longitude"].item(),
            elevation=loc["elevation"].item(),
        )

        loc_label = location[0]["label"].split("|")[0] + (
            f"|📍 {float(data.attrs['longitude']):.1f}E"
            f", {float(data.attrs['latitude']):.1f}N, {float(data.attrs['elevation']):.0f}m) | "
            f'{",".join(models)}'
        )

        return (
            make_subplot_figure(data=data, title=loc_label, sun=sun, models=models),
            None,
            False,
        )
    except Exception as e:
        logging.error(
            f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}"
        )
        return (
            no_update,
            "An error occurred when processing the data",
            True,  # Error message
        )
