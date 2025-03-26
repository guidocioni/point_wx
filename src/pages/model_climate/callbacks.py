from dash import (
    callback,
    Output,
    Input,
    State,
    no_update,
    dcc,
    clientside_callback,
)
from utils.openmeteo_api import compute_monthly_clima, get_historical_daily_data
from utils.custom_logger import logging
from .figures import (
    make_clouds_climate_figure,
    make_precipitation_climate_figure,
    make_temp_prec_climate_figure,
    make_temperature_climate_figure,
    make_winds_climate_figure,
    make_wind_rose_figure,
)
import pandas as pd
from io import StringIO
from datetime import date, timedelta
from utils.settings import images_config


@callback(
    [
        Output("temp-prec-climate-container", "children"),
        Output("clouds-climate-container", "children"),
        Output("precipitation-climate-container", "children"),
        Output("temperature-climate-container", "children"),
        Output("winds-climate-container", "children"),
        Output("winds-rose-climate-container", "children"),
        Output("error-message", "children", allow_duplicate=True),
        Output("error-modal", "is_open", allow_duplicate=True),
    ],
    Input({"type": "submit-button", "index": "monthly"}, "n_clicks"),
    [
        State("locations-list", "data"),
        State("location-selected", "data"),
        State("models-selection-climate", "value"),
        State("date-range-climate", "value"),
    ],
    prevent_initial_call=True,
)
def generate_figure(n_clicks, locations, location, model, dates):
    if n_clicks is None:
        return (
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
        )

    # unpack locations data
    locations = pd.read_json(StringIO(locations), orient="split", dtype={"id": str})
    loc = locations[locations["id"] == location[0]["value"]]
    loc_label = location[0]["label"].split("|")[0] + (
        f"| {float(loc['longitude'].item()):.1f}E"
        f", {float(loc['latitude'].item()):.1f}N, {float(loc['elevation'].item()):.0f}m)<br>"
        f"<sup>{dates[0]} to {dates[1]}</sup>"
    )

    try:
        data = compute_monthly_clima(
            latitude=loc["latitude"].item(),
            longitude=loc["longitude"].item(),
            model=model,
            start_date=dates[0],
            end_date=dates[1],
        )

        wind_rose_data = get_historical_daily_data(
            variables="wind_direction_10m_dominant",
            latitude=loc["latitude"].item(),
            longitude=loc["longitude"].item(),
            model=model,
            start_date=dates[0],
            end_date=dates[1],
        )

        fig_temp_prec = make_temp_prec_climate_figure(data, title=loc_label)
        fig_temperature = make_temperature_climate_figure(data, title=loc_label)
        fig_precipitation = make_precipitation_climate_figure(data, title=loc_label)
        fig_clouds = make_clouds_climate_figure(data, title=loc_label)
        fig_winds = make_winds_climate_figure(data, title=loc_label)
        fig_winds_rose = make_wind_rose_figure(wind_rose_data)

        temp_prec_container = dcc.Graph(
            figure=fig_temp_prec,
            id=dict(type="figure", id="temp-prec-climate"),
            config=images_config,
            style={"height": "45vh", "minHeight": "300px"},
        )

        clouds_container = dcc.Graph(
            figure=fig_clouds,
            config=images_config,
            style={"height": "45vh", "minHeight": "300px"},
        )

        precipitation_container = dcc.Graph(
            figure=fig_precipitation,
            config=images_config,
            style={"height": "45vh", "minHeight": "300px"},
        )

        temperature_container = dcc.Graph(
            figure=fig_temperature,
            config=images_config,
            style={"height": "45vh", "minHeight": "300px"},
        )

        winds_container = dcc.Graph(
            figure=fig_winds,
            config=images_config,
            style={"height": "45vh", "minHeight": "300px"},
        )

        winds_rose_container = dcc.Graph(figure=fig_winds_rose, config=images_config)

        return (
            temp_prec_container,
            clouds_container,
            precipitation_container,
            temperature_container,
            winds_container,
            winds_rose_container,
            None,
            False,
        )

    except Exception as e:
        logging.error(
            f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}. Parameters used model={model}, dates={dates[0]},{dates[1]}"
        )
        return (
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            "An error occurred when processing the data",
            True,
        )


@callback(Output("date-range-climate", "maxDate"), Input("date-range-climate", "id"))
def update_max_date(_):
    return (date.today() - timedelta(days=6)).strftime("%Y-%m-%d")


clientside_callback(
    """
    function(value) {
        // Remove focus from the dropdown element
        document.activeElement.blur();
    }
    """,
    Input("models-selection-climate", "value"),
    prevent_initial_call=True,
)
