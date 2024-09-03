from dash import callback, Output, Input, State, no_update, clientside_callback
from utils.openmeteo_api import get_historical_daily_data
from utils.custom_logger import logging
from datetime import date, timedelta
from .figures import make_calendar_figure
import pandas as pd
from io import StringIO


@callback(
    [
        Output(dict(type="figure", id="calendar"), "figure"),
        Output("error-message", "children", allow_duplicate=True),
        Output("error-modal", "is_open", allow_duplicate=True),
    ],
    Input({"type": "submit-button", "index": "calendar"}, "n_clicks"),
    [
        State("locations-list", "data"),
        State("location-selected", "data"),
        State("models-selection-climate-calendar", "value"),
        State("graph-selection-climate-calendar", "value")
    ],
    prevent_initial_call=True,
)
def generate_figure(n_clicks, locations, location, model, graph_type):
    if n_clicks is None:
        return no_update, no_update, no_update

    # unpack locations data
    locations = pd.read_json(StringIO(locations), orient="split", dtype={"id": str})
    loc = locations[locations["id"] == location[0]["value"]]

    try:
        if graph_type == 'accumulated_precipitation':
            var = 'precipitation_sum'
        else:
            raise ValueError()

        data = get_historical_daily_data(
            variables=var,
            latitude=loc["latitude"].item(),
            longitude=loc["longitude"].item(),
            model=model,
            start_date='1991-01-01',
            end_date=(date.today() - timedelta(days=6)).strftime("%Y-%m-%d")
        )

        loc_label = location[0]["label"].split("|")[0] + (
            f"|📍 {float(data.attrs['longitude']):.1f}E"
            f", {float(data.attrs['latitude']):.1f}N, {float(data.attrs['elevation']):.0f}m)<br>"
            # f"<sup>Variable = <b>{variable}</b> | "
            f"Model = <b>{model.upper()}</b></sup>"
        )

        return make_calendar_figure(data, graph_type=graph_type, title=loc_label), None, False

    except Exception as e:
        logging.error(
            f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e} Parameters used model={model}"
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
    Input('models-selection-climate-calendar', 'value'),
    prevent_initial_call=True
)
clientside_callback(
    """
    function(value) {
        // Remove focus from the dropdown element
        document.activeElement.blur();
    }
    """,
    Input('graph-selection-climate-calendar', 'value'),
    prevent_initial_call=True
)