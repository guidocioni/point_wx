from dash import callback, Output, Input, State
from utils.openmeteo_api import compute_yearly_accumulation, compute_yearly_comparison
from .figures import (make_empty_figure, make_prec_figure, make_temp_figure)
import pandas as pd


@callback(
    Output("submit-button-climate-daily", "disabled"),
    Input("locations", "value"),
)
def activate_submit_button(location):
    if len(location) >= 2:
        return False
    else:
        return True


@callback(
    [Output("prec-climate-daily-figure", "figure"),
     Output("temp-climate-daily-figure", "figure")],
    Input("submit-button-climate-daily", "n_clicks"),
    [State("locations-list", "data"),
     State("locations", "value"),
     State("models-selection-climate-daily", "value"),
     State("year-selection-climate", "value")]
)
def generate_figure(n_clicks, locations, location, model, year):
    if n_clicks is None:
        return [make_empty_figure(), make_empty_figure()]

    # unpack locations data
    locations = pd.read_json(locations, orient='split')
    loc = locations[locations['id'] == location['value']]

    data = compute_yearly_accumulation(
        latitude=loc['latitude'].item(),
        longitude=loc['longitude'].item(),
        model=model,
        var='precipitation_sum',
        year=year,
    )

    data_2 = compute_yearly_comparison(
        latitude=loc['latitude'].item(),
        longitude=loc['longitude'].item(),
        model=model,
        var='temperature_2m_mean',
        year=year,
    )

    fig_prec = make_prec_figure(data, year=year, var='precipitation_sum')
    fig_temp = make_temp_figure(data_2, year=year, var='temperature_2m_mean')

    return [fig_prec, fig_temp]
