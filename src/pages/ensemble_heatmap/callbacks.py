from dash import callback, Output, Input, State, no_update, clientside_callback
from dash.exceptions import PreventUpdate
from utils.openmeteo_api import (
    get_ensemble_data,
    get_model_meta,
    weather_code_to_precip_type,
    compute_climatology,
    compute_climatology_zarr,
)
from utils.custom_logger import logging
from utils.constants import ENSEMBLE_MODELS, ENSEMBLE_VARS, CLIMATOLOGY_VARS
from utils.settings import validate_model_selection
from utils.location_model_filter import create_location_model_filter_callback
from .figures import make_heatmap, make_lineplot
import pandas as pd
from io import StringIO
from utils.url_sync import Param, register


@callback(
    [
        Output(dict(type="figure", id="ensemble-heatmap"), "figure"),
        Output("figures-store", "data", allow_duplicate=True),
        Output("error-message", "children", allow_duplicate=True),
        Output("error-modal", "is_open", allow_duplicate=True),
        Output("figure-ready-signal", "data", allow_duplicate=True),
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
        State("figures-store", "data"),
    ],
    prevent_initial_call=True,
)
def generate_figure(n_clicks, locations, location, model, variable, from_now_, decimate_, _is_heatmap, figures_store):
    if n_clicks is None:
        raise PreventUpdate

    # Validate model and variable selections
    is_valid, error_msg = validate_model_selection(model, ENSEMBLE_MODELS, "model")
    if not is_valid:
        return no_update, no_update, error_msg, True, no_update

    is_valid, error_msg = validate_model_selection(variable, ENSEMBLE_VARS, "variable")
    if not is_valid:
        return no_update, no_update, error_msg, True, no_update

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

        clima = None
        if not _is_heatmap:
            if variable in CLIMATOLOGY_VARS:
                try:
                    clima = compute_climatology(
                        latitude=loc["latitude"].item(),
                        longitude=loc["longitude"].item(),
                        variables=variable,
                        model="era5_seamless",
                    )
                except Exception as e:
                    logging.error(f"Could not fetch climatology for variable={variable}: {e}")
                    clima = None
            elif variable == "temperature_850hPa":
                # BETA, load the climatology of 850hPa T from a zarr, same as the ensemble page
                try:
                    clima = compute_climatology_zarr(
                        latitude=loc["latitude"].item(),
                        longitude=loc["longitude"].item(),
                    )
                    clima["time"] = (
                        clima["time"]
                        .dt.tz_localize("UTC")
                        .dt.tz_convert(data.attrs["timezone"])
                    )
                    clima["doy"] = clima["time"].dt.strftime("%m%d")
                    clima["hour"] = clima["time"].dt.hour
                    clima = clima.drop(columns=["time"])
                except Exception as e:
                    logging.error(f"Could not fetch t850hPa climatology: {e}")
                    clima = None

        run_info = ""
        try:
            meta = get_model_meta(type="ensemble", model=model)
            if meta and meta.get("last_run_initialisation_time") is not None:
                run_info = f" | Run: {meta['last_run_initialisation_time'].strftime('%Y-%m-%d %HZ')}"
        except Exception as e:
            logging.error(f"Could not fetch model run metadata for model={model}: {e}")

        loc_label = location[0]["label"].split("|")[0] + (
            f"|📍 {float(data.attrs['longitude']):.1f}E"
            f", {float(data.attrs['latitude']):.1f}N, {float(data.attrs['elevation']):.0f}m)<br>"
            f"<sup>Variable = <b>{variable}</b> | "
            f"Ens = <b>{model.upper()}</b>{run_info}</sup>"
        )
        if _is_heatmap:
            figure = make_heatmap(data, var=variable, title=loc_label)
        else:
            figure = make_lineplot(data, var=variable, title=loc_label, clima=clima)

        figures_data = figures_store.copy() if figures_store else {}
        figures_data["ensemble-heatmap"] = figure
        return figure, figures_data, None, False, n_clicks

    except Exception as e:
        logging.error(
            f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e} Parameters used model={model}, variable={variable}, from_now={from_now_}, decimate={decimate_}"
        )
        return (
            no_update,
            no_update,
            "An error occurred when processing the data",
            True,
            no_update,
        )


clientside_callback(
    """
    function(_, figures_store) {
        if (!figures_store || !("ensemble-heatmap" in figures_store)) {
            return [window.dash_clientside.no_update, window.dash_clientside.no_update];
        }
        return [figures_store["ensemble-heatmap"], true];
    }
    """,
    Output(dict(type="figure", id="ensemble-heatmap"), "figure", allow_duplicate=True),
    Output({'type': 'fade', 'index': 'heatmap'}, "is_open", allow_duplicate=True),
    Input("variable-selection-heatmap", "id"),
    State("figures-store", "data"),
    prevent_initial_call='initial_duplicate',
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


# Register location-based model filtering callback
create_location_model_filter_callback(
    model_dropdown_id="models-selection-heatmap",
    model_options=ENSEMBLE_MODELS,
    model_type="ensemble"
)


# Keep the page's selectors and the URL query string in sync
register("heatmap", [
    Param("models-selection-heatmap", "value", "model", valid=ENSEMBLE_MODELS),
    Param("variable-selection-heatmap", "value", "var", valid=ENSEMBLE_VARS),
    Param("decimate-switch", "checked", "decimate", kind="bool"),
    Param("from-now-switch", "checked", "fromnow", kind="bool"),
    Param("heatmap-line-plot-switch", "checked", "heatmap", kind="bool"),
])
