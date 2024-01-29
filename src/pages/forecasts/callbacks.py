from dash import callback, Output, Input, State, no_update, clientside_callback
from utils.openmeteo_api import get_forecast_data, get_forecast_daily_data
from utils.suntimes import find_suntimes
from .figures import make_subplot_figure
import pandas as pd


@callback(
    Output("submit-button-deterministic", "disabled"),
    [Input("locations", "value"),
     Input("search-button", "n_clicks")],
)
def activate_submit_button(location, _nouse):
    if location is not None and len(location) >= 2:
        return False
    else:
        return True


@callback(
    Output("fade-deterministic", "is_open"),
    [Input("submit-button-deterministic", "n_clicks")],
)
def toggle_fade(n):
    if not n:
        # Button has never been clicked
        return False
    return True


@callback(
    [Output("forecast-plot", "figure"),
     Output("error-message", "children", allow_duplicate=True),
     Output("error-modal", "is_open", allow_duplicate=True)],
    Input("submit-button-deterministic", "n_clicks"),
    [State("locations-list", "data"),
     State("locations", "value"),
     State("models-selection-deterministic", "value")],
    prevent_initial_call=True
)
def generate_figure(n_clicks, locations, location, models):
    if n_clicks is None:
        return no_update, no_update, no_update

    # unpack locations data
    locations = pd.read_json(locations, orient='split', dtype={"id": str})
    loc = locations[locations['id'] == location]
    loc_label = (
        f"{loc['name'].item()} ({loc['country'].item()} | {float(loc['longitude'].item()):.1f}E"
        f", {float(loc['latitude'].item()):.1f}N, {float(loc['elevation'].item()):.0f}m)  -  "
        f'Models: {",".join(models)}'
    )

    try:
        data = get_forecast_data(latitude=loc['latitude'].item(),
                                 longitude=loc['longitude'].item(),
                                 model=",".join(models),
                                 forecast_days=14)

        sun = find_suntimes(df=data,
                            latitude=loc['latitude'].item(),
                            longitude=loc['longitude'].item(),
                            elevation=loc['elevation'].item())

        loc_label = (
            f"{loc['name'].item()}, {loc['country'].item()} | 🌐 {float(data.attrs['longitude']):.1f}E"
            f", {float(data.attrs['latitude']):.1f}N, {float(data.attrs['elevation']):.0f}m | "
            f'{",".join(models)}'
        )

        return make_subplot_figure(data=data, title=loc_label, sun=sun, models=models), None, False
    except Exception as e:
        return no_update, repr(e), True


clientside_callback(
    """
    function(n_clicks, element_id) {
            var targetElement = document.getElementById(element_id);
            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth' });
            }
        return null;
    }
    """,
    Output('garbage', 'data', allow_duplicate=True),
    Input('forecast-plot', 'figure'),
    [State('forecast-plot', 'id')],
    prevent_initial_call=True
)
