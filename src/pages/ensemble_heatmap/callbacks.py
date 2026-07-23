from dash import callback, Output, Input, State, no_update, clientside_callback
from utils.openmeteo_api import get_ensemble_data, weather_code_to_precip_type
from utils.custom_logger import logging
from utils.settings import ENSEMBLE_MODELS, ENSEMBLE_VARS, validate_model_selection
from .figures import make_heatmap, make_lineplot
import pandas as pd
from io import StringIO


@callback(
    [
        Output(dict(type="figure", id="ensemble-heatmap"), "figure"),
        Output("error-message", "children", allow_duplicate=True),
        Output("error-modal", "is_open", allow_duplicate=True),
    ],
    Input({"type": "submit-button", "index": "heatmap"}, "n_clicks"),
    [
        State("locations-list", "data"),
        State("location-selected", "data"),
        State("models-selection-heatmap", "value"),
        State("variable-selection-heatmap", "value"),
        State("from-now-switch", "checked"),
        State("decimate-switch", "checked"),
        State("heatmap-line-plot-switch", "checked"),
    ],
    prevent_initial_call=True,
)
def generate_figure(n_clicks, locations, location, model, variable, from_now_, decimate_, _is_heatmap):
    if n_clicks is None:
        return no_update, no_update, no_update

    # Validate model and variable selections
    is_valid, error_msg = validate_model_selection(model, ENSEMBLE_MODELS, "model")
    if not is_valid:
        return no_update, error_msg, True

    is_valid, error_msg = validate_model_selection(variable, ENSEMBLE_VARS, "variable")
    if not is_valid:
        return no_update, error_msg, True

    # unpack locations data
    locations = pd.read_json(StringIO(locations), orient="split", dtype={"id": str})
    loc = locations[locations["id"] == location[0]["value"]]

    try:
        # Handle special case: precipitation_type requires fetching weather_code
        actual_variable = variable
        if variable == "precipitation_type":
            actual_variable = "weather_code"

        data = get_ensemble_data(
            latitude=loc["latitude"].item(),
            longitude=loc["longitude"].item(),
            model=model,
            variables=actual_variable,
            decimate=decimate_,
            from_now=from_now_,
        )

        # Convert weather_code to precipitation_type if needed
        if variable == "precipitation_type":
            # Find all weather_code columns (including ensemble members)
            weather_cols = [col for col in data.columns if col.startswith("weather_code")]

            # Convert each weather_code column to precipitation_type
            for col in weather_cols:
                new_col = col.replace("weather_code", "precipitation_type")
                data[new_col] = data[col].apply(weather_code_to_precip_type)

            # Drop the weather_code columns to avoid confusion
            data = data.drop(columns=weather_cols)

        loc_label = location[0]["label"].split("|")[0] + (
            f"|📍 {float(data.attrs['longitude']):.1f}E"
            f", {float(data.attrs['latitude']):.1f}N, {float(data.attrs['elevation']):.0f}m)<br>"
            f"<sup>Variable = <b>{variable}</b> | "
            f"Ens = <b>{model.upper()}</b></sup>"
        )
        if _is_heatmap:
            return make_heatmap(data, var=variable, title=loc_label), None, False
        else:
            return make_lineplot(data, var=variable, title=loc_label), None, False

    except Exception as e:
        logging.error(
            f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e} Parameters used model={model}, variable={variable}, from_now={from_now_}, decimate={decimate_}"
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
    Input('models-selection-heatmap', 'value'),
    prevent_initial_call=True
)
clientside_callback(
    """
    function(value) {
        // Remove focus from the dropdown element
        document.activeElement.blur();
    }
    """,
    Input('variable-selection-heatmap', 'value'),
    prevent_initial_call=True
)