from dash import callback, Output, Input, State
from utils.openmeteo_api import get_locations, compute_monthly_clima
from .figures import (make_empty_figure, make_clouds_climate_figure,
                      make_precipitation_climate_figure,
                      make_temp_prec_climate_figure,
                      make_temperature_climate_figure,
                      make_winds_climate_figure)
import pandas as pd


@callback(
    Output("submit-button-climate", "disabled"),
    Input("locations", "value"),
)
def activate_submit_button(location):
    if len(location) >= 2:
        return False
    else:
        return True


@callback(
    [Output("temp-prec-climate-figure", "figure"),
     Output("clouds-climate-figure", "figure"),
     Output("temperature-climate-figure", "figure"),
     Output("precipitation-climate-figure", "figure"),
     Output("winds-climate-figure", "figure")],
    Input("submit-button-climate", "n_clicks"),
    [State("locations-list", "data"),
     State("locations", "value"),
     State("models-selection-climate", "value")]
)
def generate_figure(n_clicks, locations, location, model):
    if n_clicks is None:
        return [make_empty_figure(), make_empty_figure(),
                make_empty_figure(), make_empty_figure(),
                make_empty_figure()]

    # unpack locations data
    locations = pd.read_json(locations, orient='split')
    loc = locations[locations['id'] == location['value']]

    data = compute_monthly_clima(
        latitude=loc['latitude'].item(),
        longitude=loc['longitude'].item(),
        model=model)

    fig_temp_prec = make_temp_prec_climate_figure(data)
    fig_temperature = make_temperature_climate_figure(data)
    fig_precipitation = make_precipitation_climate_figure(data)
    fig_clouds = make_clouds_climate_figure(data)
    fig_winds = make_winds_climate_figure(data)

    return fig_temp_prec, fig_clouds, fig_temperature, fig_precipitation, fig_winds