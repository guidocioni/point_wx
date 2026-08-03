from dash import callback, Output, Input, State, no_update, clientside_callback
from dash.exceptions import PreventUpdate
from utils.openmeteo_api import get_forecast_data
from utils.custom_logger import logging
from utils.settings import DETERMINISTIC_MODELS, DETERMINISTIC_VARS, get_valid_values
from .figures import make_heatmap, make_lineplot
import pandas as pd
from io import StringIO

@callback(
    [
        Output(dict(type="figure", id="deterministic-heatmap"), "figure"),
        Output("figures-store", "data", allow_duplicate=True),
        Output("error-message", "children", allow_duplicate=True),
        Output("error-modal", "is_open", allow_duplicate=True),
    ],
    Input({"type": "submit-button", "index": "deterministic-heatmap"}, "n_clicks"),
    [
        State("locations-list", "data"),
        State("location-selected", "data"),
        State("models-selection-deterministic-heatmap", "value"),
        State("variable-selection-deterministic-heatmap", "value"),
        State("from-now-switch", "checked"),
        State("forecast-days", "value"),
        State("heatmap-line-plot-switch", "checked"),
        State("minutely-15-switch", "checked"),
        State("figures-store", "data"),
    ],
    prevent_initial_call=True,
)
def generate_figure(n_clicks, locations, location, model, variable, from_now_, days_, _is_heatmap, minutes_15_, figures_store):
    if n_clicks is None:
        raise PreventUpdate

    if len(model) == 0:
        return (
            no_update,
            no_update,
            "You need to select a least one model!",
            True,
        )

    # Validate model selections
    valid_models = get_valid_values(DETERMINISTIC_MODELS)
    invalid_models = [m for m in model if m not in valid_models]
    if invalid_models:
        return (
            no_update,
            no_update,
            f"The following selected model(s) are no longer available: {', '.join(invalid_models)}. Please update your selection.",
            True,
        )

    # Validate variable selection
    valid_vars = get_valid_values(DETERMINISTIC_VARS)
    if variable not in valid_vars:
        return (
            no_update,
            no_update,
            "The selected variable is no longer available. Please select a different one.",
            True,
        )

    # unpack locations data
    locations = pd.read_json(StringIO(locations), orient="split", dtype={"id": str})
    loc = locations[locations["id"] == location[0]["value"]]

    try:
        data = get_forecast_data(
            latitude=loc["latitude"].item(),
            longitude=loc["longitude"].item(),
            model=model,
            variables=variable,
            from_now=from_now_,
            forecast_days=days_,
            minutes_15=minutes_15_
        )

        loc_label = location[0]["label"].split("|")[0] + (
            f"|📍 {float(data.attrs['longitude']):.1f}E"
            f", {float(data.attrs['latitude']):.1f}N, {float(data.attrs['elevation']):.0f}m)"
        )

        if _is_heatmap:
            figure = make_heatmap(data, var=variable, title=loc_label, models=model)
        else:
            figure = make_lineplot(data, var=variable, models=model, title=loc_label)

        figures_data = figures_store.copy() if figures_store else {}
        figures_data["deterministic-heatmap"] = figure
        return figure, figures_data, None, False

    except Exception as e:
        logging.error(
            f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}. Parameters used model={', '.join(model)}, variable={variable}, from_now={from_now_}, days={days_}, minutes_15={minutes_15_}"
        )
        return (
            no_update,
            no_update,
            "An error occurred when processing the data",
            True,
        )


@callback(
    [
        Output(dict(type="figure", id="deterministic-heatmap"), "figure", allow_duplicate=True),
        Output({'type': 'fade', 'index': 'deterministic-heatmap'}, "is_open", allow_duplicate=True),
    ],
    Input("variable-selection-deterministic-heatmap", "id"),
    State("figures-store", "data"),
    prevent_initial_call='initial_duplicate',
)
def restore_figure(_, figures_store):
    """Restore figure and open collapse when returning to this page"""
    if not figures_store or "deterministic-heatmap" not in figures_store:
        raise PreventUpdate

    return figures_store["deterministic-heatmap"], True


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
