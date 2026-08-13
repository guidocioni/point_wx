from dash import callback, Output, Input, State, no_update, clientside_callback
from dash.exceptions import PreventUpdate
from utils.openmeteo_api import compute_daily_ensemble_meteogram, compute_climatology, compute_predictability_index, get_model_meta
from utils.figures_utils import get_weather_icons
from utils.settings import ASSETS_DIR, validate_model_selection
from utils.custom_logger import logging
from .figures import make_subplot_figure
import pandas as pd
from io import StringIO
from .options_selector import METEOGRAM_MODELS
from utils.url_sync import Param, register


@callback(
    [
        Output(dict(type="figure", id="meteogram"), "figure"),
        Output("figures-store", "data", allow_duplicate=True),
        Output("error-message", "children", allow_duplicate=True),
        Output("error-modal", "is_open", allow_duplicate=True),
        Output("figure-ready-signal", "data", allow_duplicate=True),
    ],
    Input({"type": "submit-button", "index": "meteogram"}, "n_clicks"),
    [
        State("locations-list", "data"),
        State("location-selected", "data"),
        State("models-selection-meteogram", "value"),
        State("meteogram-viewport-width", "data"),
        State("figures-store", "data"),
    ],
    prevent_initial_call=True,
)
def generate_figure(n_clicks, locations, location, model, viewport_width, figures_store):
    if n_clicks is None:
        raise PreventUpdate

    # Validate model selection (meteogram uses a filtered subset of ENSEMBLE_MODELS)
    is_valid, error_msg = validate_model_selection(model, METEOGRAM_MODELS, "model")
    if not is_valid:
        return no_update, no_update, error_msg, True, no_update

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
        # Add predictability index
        # Preserve attrs before merge
        data_attrs = data.attrs.copy()
        predictability = compute_predictability_index(data)
        # Merge on index (both have same integer index after reset_index)
        data = data.join(predictability)
        data.attrs = data_attrs

        # Add daily climatology (quite fast)
        clima = compute_climatology(
            latitude=loc["latitude"].item(),
            longitude=loc["longitude"].item(),
            daily=True,
            model="era5_seamless",
            variables="temperature_2m_max,temperature_2m_min,sunshine_duration",
        )
        clima = clima.rename(
            columns={
                "temperature_2m_max": "t_max_clima",
                "temperature_2m_min": "t_min_clima",
                "sunshine_duration": "sunshine_clima",
            }
        )

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
            f"<sup>Ens = <b>{model.upper()}</b>{run_info}</sup>"
        )

        figure = make_subplot_figure(data, title=loc_label, clima=clima, viewport_width=viewport_width)
        figures_data = figures_store.copy() if figures_store else {}
        figures_data["meteogram"] = figure
        return figure, figures_data, None, False, n_clicks

    except Exception as e:
        logging.error(
            f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}. Parameters used model={model}"
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
        if (!figures_store || !("meteogram" in figures_store)) {
            return [window.dash_clientside.no_update, window.dash_clientside.no_update];
        }
        return [figures_store["meteogram"], true];
    }
    """,
    Output(dict(type="figure", id="meteogram"), "figure", allow_duplicate=True),
    Output({'type': 'fade', 'index': 'meteogram'}, "is_open", allow_duplicate=True),
    Input("models-selection-meteogram", "id"),
    State("figures-store", "data"),
    prevent_initial_call='initial_duplicate',
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


clientside_callback(
    """
    function(id) {
        return window.innerWidth;
    }
    """,
    Output('meteogram-viewport-width', 'data'),
    Input('meteogram-page-div', 'id'),
)


# Keep the page's selectors and the URL query string in sync
register("meteogram", [
    Param("models-selection-meteogram", "value", "model", valid=METEOGRAM_MODELS),
])
