from dash import callback, Output, Input, State, no_update, clientside_callback
from utils.openmeteo_api import compute_daily_ensemble_meteogram
from utils.figures_utils import get_weather_icons
from utils.settings import ASSETS_DIR
from .figures import make_subplot_figure
import pandas as pd


@callback(
    Output("submit-button-meteogram", "disabled"),
    [Input("locations", "value"),
     Input("search-button", "n_clicks")],
)
def activate_submit_button(location, _nouse):
    if location is not None and len(location) >= 2:
        return False
    else:
        return True


@callback(
    Output("fade-meteogram", "is_open"),
    [Input("submit-button-meteogram", "n_clicks")],
)
def toggle_fade(n):
    if not n:
        # Button has never been clicked
        return False
    return True


@callback(
    [Output("meteogram-plot", "figure"),
     Output("error-message", "children", allow_duplicate=True),
     Output("error-modal", "is_open", allow_duplicate=True)],
    Input("submit-button-meteogram", "n_clicks"),
    [State("locations-list", "data"),
     State("locations", "value"),
     State("models-selection-meteogram", "value")],
    prevent_initial_call=True
)
def generate_figure(n_clicks, locations, location, model):
    if n_clicks is None:
        return no_update, no_update, no_update

    # unpack locations data
    locations = pd.read_json(locations, orient='split', dtype={"id": str})
    loc = locations[locations['id'] == location]

    try:
        data = compute_daily_ensemble_meteogram(
            latitude=loc['latitude'].item(),
            longitude=loc['longitude'].item(),
            model=model).reset_index()
        data = get_weather_icons(data,
                                 icons_path=f"{ASSETS_DIR}/yrno_png/",
                                 mapping_path=f"{ASSETS_DIR}/weather_codes.json")

        loc_label = (
            f"{loc['name'].item()}, {loc['country'].item()} | 🌐 {float(data.attrs['longitude']):.1f}E"
            f", {float(data.attrs['latitude']):.1f}N, {float(data.attrs['elevation']):.0f}m | "
            f"{model.upper()}"
        )

        return make_subplot_figure(data, title=loc_label), None, False

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
    Input('meteogram-plot', 'figure'),
    [State('meteogram-plot', 'id')],
    prevent_initial_call=True
)
