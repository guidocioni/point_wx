from dash import callback, Output, Input, State, no_update
from utils.openmeteo_api import get_vertical_data
from utils.custom_logger import logging
from .figures import make_figure_vertical
import pandas as pd
from io import StringIO


@callback(
    [
        Output(dict(type="figure", id="vertical"), "figure"),
        Output("error-message", "children", allow_duplicate=True),
        Output("error-modal", "is_open", allow_duplicate=True),
    ],
    Input({"type": "submit-button", "index": "vertical"}, "n_clicks"),
    [
        State("locations-list", "data"),
        State("location-selected", "data"),
        State("models-selection-vertical", "value"),
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
        df, _, time_axis, vertical_levels, arrs = get_vertical_data(
            latitude=loc["latitude"].item(),
            longitude=loc["longitude"].item(),
            model=model,
        )

        loc_label = location[0]["label"].split("|")[0] + (
            f"|📍 {float(df.attrs['longitude']):.1f}E"
            f", {float(df.attrs['latitude']):.1f}N, {float(df.attrs['elevation']):.0f}m | "
            f"{model.upper()}"
        )

        return (
            make_figure_vertical(time_axis, vertical_levels, arrs, title=loc_label),
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
