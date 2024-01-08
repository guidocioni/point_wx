from dash import callback, Output, Input, State, no_update
from utils.openmeteo_api import get_vertical_data
from .figures import make_figure_vertical
import pandas as pd


@callback(
    Output("submit-button-vertical", "disabled"),
    [Input("locations", "value"),
     Input("search-button", "n_clicks")],
)
def activate_submit_button(location, _nouse):
    if location is not None and len(location) >= 2:
        return False
    else:
        return True


@callback(
    Output("fade-vertical", "is_open"),
    [Input("submit-button-vertical", "n_clicks")],
)
def toggle_fade(n):
    if not n:
        # Button has never been clicked
        return False
    return True


@callback(
    [Output("plot-vertical", "figure"),
     Output("error-message", "children", allow_duplicate=True),
     Output("error-modal", "is_open", allow_duplicate=True)],
    Input("submit-button-vertical", "n_clicks"),
    [State("locations-list", "data"),
     State("locations", "value"),
     State("models-selection-vertical", "value")],
    prevent_initial_call=True
)
def generate_figure(n_clicks, locations, location, model):
    if n_clicks is None:
        return no_update, no_update, no_update

    # unpack locations data
    locations = pd.read_json(locations, orient='split', dtype={"id": str})
    loc = locations[locations['id'] == location]

    try:
        df, _, time_axis, vertical_levels, arrs = get_vertical_data(
            latitude=loc['latitude'].item(),
            longitude=loc['longitude'].item(),
            model=model)

        loc_label = (
            f"{loc['name'].item()}, {loc['country'].item()} | 🌐 {float(df.attrs['longitude']):.1f}E"
            f", {float(df.attrs['latitude']):.1f}N, {float(df.attrs['elevation']):.0f}m | "
            f"{model.upper()}"
        )

        return make_figure_vertical(time_axis, vertical_levels, arrs, title=loc_label), None, False

    except Exception as e:
        return no_update, repr(e), True
