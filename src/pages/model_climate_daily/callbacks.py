from dash import callback, Output, Input, State, no_update, clientside_callback
from utils.openmeteo_api import compute_yearly_accumulation, compute_yearly_comparison
from utils.custom_logger import logging
from .figures import make_prec_figure, make_temp_figure
import pandas as pd


@callback(
    Output("submit-button-climate-daily", "disabled"),
    Input("location_search_new", "value"),
)
def activate_submit_button(location):
    if location is None:
        return True
    return False


@callback(
    Output("fade-climate-daily", "is_open"),
    [Input("submit-button-climate-daily", "n_clicks")],
)
def toggle_fade(n):
    if not n:
        # Button has never been clicked
        return False
    return True


@callback(
    [Output("prec-climate-daily-figure", "figure"),
     Output("temp-climate-daily-figure", "figure"),
     Output("error-message", "children", allow_duplicate=True),
     Output("error-modal", "is_open", allow_duplicate=True)],
    Input("submit-button-climate-daily", "n_clicks"),
    [State("locations-list", "data"),
     State("location-selected", "data"),
     State("models-selection-climate-daily", "value"),
     State("year-selection-climate", "value")],
    prevent_initial_call=True
)
def generate_figure(n_clicks, locations, location, model, year):
    if n_clicks is None:
        return [no_update, no_update,
                no_update, no_update]

    # unpack locations data
    locations = pd.read_json(locations, orient='split', dtype={"id": str})
    loc = locations[locations['id'] == location[0]['value']]
    loc_label = location[0]['label'].split("|")[0] + (
        f"| {float(loc['longitude'].item()):.1f}E"
        f", {float(loc['latitude'].item()):.1f}N, {float(loc['elevation'].item()):.0f}m)  -  "
        f"{model.upper()}"
    )

    try:
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

        fig_prec = make_prec_figure(
            data, year=year, var='precipitation_sum', title=loc_label)
        fig_temp = make_temp_figure(
            data_2, year=year, var='temperature_2m_mean', title=loc_label)

        return [fig_prec, fig_temp, None, False]

    except Exception as e:
        logging.error(
            f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")
        return (
            no_update,
            no_update,
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
                }, 800); // in milliseconds
            }
        return null;
    }
    """,
    Output('garbage', 'data', allow_duplicate=True),
    Input('submit-button-climate-daily', 'n_clicks'),
    [State('prec-climate-daily-figure', 'id')],
    prevent_initial_call=True
)
