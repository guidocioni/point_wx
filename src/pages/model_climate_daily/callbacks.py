from dash import callback, Output, Input, State
from utils.openmeteo_api import compute_yearly_accumulation
from .figures import (make_empty_figure, make_prec_figure)
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
    [Output("prec-climate-daily-figure", "figure")],
    Input("submit-button-climate-daily", "n_clicks"),
    [State("locations-list", "data"),
     State("locations", "value"),
     State("models-selection-climate-daily", "value")]
)
def generate_figure(n_clicks, locations, location, model):
    if n_clicks is None:
        return [make_empty_figure()]

    # unpack locations data
    locations = pd.read_json(locations, orient='split')
    loc = locations[locations['id'] == location['value']]

    year = pd.to_datetime('now', utc=True).year
    var = 'precipitation_sum'

    data = compute_yearly_accumulation(
        latitude=loc['latitude'].item(),
        longitude=loc['longitude'].item(),
        model=model,
        var=var,
        year=year,
    )

    fig_prec = make_prec_figure(data, year=year, var=var)

    return [fig_prec]
