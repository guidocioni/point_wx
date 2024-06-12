from dash import callback, Output, Input, State, no_update, clientside_callback
from utils.openmeteo_api import compute_monthly_clima, get_historical_daily_data
from utils.custom_logger import logging
from .figures import (make_clouds_climate_figure,
                      make_precipitation_climate_figure,
                      make_temp_prec_climate_figure,
                      make_temperature_climate_figure,
                      make_winds_climate_figure,
                      make_wind_rose_figure)
import pandas as pd
from datetime import date

@callback(
    Output("submit-button-climate", "disabled"),
    Input("location_search_new", "value"),
)
def activate_submit_button(location):
    if location is None:
        return True
    return False



@callback(
    Output("fade-climate", "is_open"),
    [Input("submit-button-climate", "n_clicks")],
)
def toggle_fade(n):
    if not n:
        # Button has never been clicked
        return False
    return True

@callback(
    [Output("temp-prec-climate-figure", "figure"),
     Output("clouds-climate-figure", "figure"),
     Output("temperature-climate-figure", "figure"),
     Output("precipitation-climate-figure", "figure"),
     Output("winds-climate-figure", "figure"),
     Output("winds-rose-climate-figure", "figure"),
     Output("error-message", "children", allow_duplicate=True),
     Output("error-modal", "is_open", allow_duplicate=True)],
    Input("submit-button-climate", "n_clicks"),
    [State("locations-list", "data"),
     State("location_search_new", "value"),
     State("models-selection-climate", "value"),
     State("date-start-climate", "date"),
     State("date-end-climate", "date")],
    prevent_initial_call=True
)
def generate_figure(n_clicks, locations, location, model, ds, de):
    if n_clicks is None:
        return [no_update, no_update,
                no_update, no_update, no_update,
                no_update, no_update, no_update]

    # unpack locations data
    locations = pd.read_json(locations, orient='split', dtype={"id": str})
    loc = locations[locations['id'] == location]

    try:
        data = compute_monthly_clima(
            latitude=loc['latitude'].item(),
            longitude=loc['longitude'].item(),
            model=model,
            start_date=date.fromisoformat(ds).strftime("%Y-%m-%d"),
            end_date=date.fromisoformat(de).strftime("%Y-%m-%d"))

        wind_rose_data = get_historical_daily_data(
            variables='wind_direction_10m_dominant',
            latitude=loc['latitude'].item(),
            longitude=loc['longitude'].item(),
            model=model,
            start_date=date.fromisoformat(ds).strftime("%Y-%m-%d"),
            end_date=date.fromisoformat(de).strftime("%Y-%m-%d"))

        fig_temp_prec = make_temp_prec_climate_figure(data)
        fig_temperature = make_temperature_climate_figure(data)
        fig_precipitation = make_precipitation_climate_figure(data)
        fig_clouds = make_clouds_climate_figure(data)
        fig_winds = make_winds_climate_figure(data)
        # fig_winds_rose = make_wind_rose_figure(wind_rose_data)

        return [fig_temp_prec, fig_clouds, fig_temperature,
                fig_precipitation, fig_winds, None, None, False]

    except Exception as e:
        logging.error(
            f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")
        return (
            no_update, no_update,
            no_update, no_update,
            no_update, no_update,
            "An error occurred when processing the data",
            True  # Error message
        )


clientside_callback(
    """
    function(n_clicks, element_id) {
            var targetElement = document.getElementById(element_id);
            if (targetElement) {
                setTimeout(function() {
                    targetElement.scrollIntoView({ behavior: 'smooth' });
                }, 500); // in milliseconds
            }
        return null;
    }
    """,
    Output('garbage', 'data', allow_duplicate=True),
    Input('submit-button-climate', 'n_clicks'),
    [State('temp-prec-climate-figure', 'id')],
    prevent_initial_call=True
)
