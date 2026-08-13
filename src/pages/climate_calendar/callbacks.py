from dash import callback, Output, Input, State, no_update, clientside_callback
from dash.exceptions import PreventUpdate
from utils.openmeteo_api import get_historical_daily_data, compute_climatology
from utils.custom_logger import logging
from utils.settings import REANALYSIS_MODELS, validate_model_selection
from datetime import date, timedelta
from .figures import make_calendar_figure
import pandas as pd
from io import StringIO
from .options_selector import graph_options
from utils.url_sync import Param, register


@callback(
    [
        Output(dict(type="figure", id="calendar"), "figure"),
        Output("figures-store", "data", allow_duplicate=True),
        Output("error-message", "children", allow_duplicate=True),
        Output("error-modal", "is_open", allow_duplicate=True),
        Output("figure-ready-signal", "data", allow_duplicate=True),
    ],
    Input({"type": "submit-button", "index": "calendar"}, "n_clicks"),
    [
        State("locations-list", "data"),
        State("location-selected", "data"),
        State("models-selection-climate-calendar", "value"),
        State("graph-selection-climate-calendar", "value"),
        State("graph-selection-climate-calendar", "data"),
        State("year-selection-calendar", "value"),
        State("figures-store", "data"),
    ],
    prevent_initial_call=True,
)
def generate_figure(n_clicks, locations, location, model, graph_type, graph_types, year_start, figures_store):
    if n_clicks is None:
        raise PreventUpdate

    # Validate model selection
    is_valid, error_msg = validate_model_selection(model, REANALYSIS_MODELS, "model")
    if not is_valid:
        return no_update, no_update, error_msg, True, no_update

    # unpack locations data
    locations = pd.read_json(StringIO(locations), orient="split", dtype={"id": str})
    loc = locations[locations["id"] == location[0]["value"]]

    try:
        if graph_type in ['accumulated_precipitation', 'precipitation_days', 'dry_days', 'precipitation_anomaly']:
            var = 'precipitation_sum'
        elif graph_type in ['snow_days', 'snowfall', 'snow_anomaly']:
            var = 'snowfall_sum'
        elif graph_type in ['frost_days', 'tropical_nights', 'temperature_min']:
            var = 'temperature_2m_min'
        elif graph_type in ['hot_days', 'temperature_max']:
            var = 'temperature_2m_max'
        elif graph_type in ['overcast_days', 'partly_cloudy_days', 'sunny_days']:
            var = 'cloudcover_mean'
        elif graph_type in ['temperature_anomaly', 'temperature_anomaly_rank', 'temperature_mean']:
            var = 'temperature_2m_mean'
        elif graph_type == 'dominant_wind_direction':
            var = 'wind_direction_10m_dominant'
        else:
            raise ValueError()

        data = get_historical_daily_data(
            variables=var,
            latitude=loc["latitude"].item(),
            longitude=loc["longitude"].item(),
            model=model,
            start_date=f'{year_start}-01-01',
            end_date=date.today().strftime("%Y-%m-%d")
        )
        if graph_type in ['precipitation_anomaly', 'temperature_anomaly', 'temperature_anomaly_rank', 'snow_anomaly']:
            # TODO, Report in the frontend that it's better to use ERA5 when comparing to the clima
            data['doy'] = data.time.dt.strftime("%m%d")
            clima = compute_climatology(
                        latitude=loc["latitude"].item(),
                        longitude=loc["longitude"].item(),
                        model='era5_seamless',
                        variables=var,
                        daily=True
            )
            clima.attrs = data.attrs.copy()
            data = data.merge(
                clima.rename(columns={var:var+"_clima"}),
                left_on='doy',
                right_on='doy'
            ).sort_values(by='time')
            data.attrs = clima.attrs.copy()

        graph_title = [o["label"] for o in graph_types if o["value"] == graph_type]
        if len(graph_title) == 1:
            graph_title = graph_title[0]
        else:
            graph_title = graph_type
        last_date = data['time'].max().strftime('%Y-%m-%d')
        loc_label = location[0]["label"].split("|")[0] + (
            f"|📍 {float(data.attrs['longitude']):.1f}E"
            f", {float(data.attrs['latitude']):.1f}N, {float(data.attrs['elevation']):.0f}m)<br>"
            f"<sup>Metric = <b>{graph_title}</b> | "
            f"Model = <b>{model.upper()}</b> | "
            f"Until <b>{last_date}</b></sup>"
        )

        figure = make_calendar_figure(data, graph_type=graph_type, title=loc_label)
        figures_data = figures_store.copy() if figures_store else {}
        figures_data["calendar"] = figure
        return figure, figures_data, None, False, n_clicks

    except Exception as e:
        logging.error(
            f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e} Parameters used model={model}"
        )
        return (
            no_update,
            no_update,
            "An error occurred when processing the data",
            True,
            no_update,
        )


@callback(
    [
        Output(dict(type="figure", id="calendar"), "figure", allow_duplicate=True),
        Output({'type': 'fade', 'index': 'calendar'}, "is_open", allow_duplicate=True),
    ],
    Input("year-selection-calendar", "id"),
    State("figures-store", "data"),
    prevent_initial_call='initial_duplicate',
)
def restore_figure(_, figures_store):
    """Restore figure and open collapse when returning to this page"""
    if not figures_store or "calendar" not in figures_store:
        raise PreventUpdate

    return figures_store["calendar"], True


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


# Keep the page's selectors and the URL query string in sync
register("calendar", [
    Param("models-selection-climate-calendar", "value", "model", valid=REANALYSIS_MODELS),
    Param("graph-selection-climate-calendar", "value", "graph", valid=graph_options),
    Param("year-selection-calendar", "value", "year", kind="int", lo=1940,
          hi=lambda: date.today().year),
])
