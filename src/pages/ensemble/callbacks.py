from dash import callback, Output, Input, State, no_update, clientside_callback
from utils.openmeteo_api import get_ensemble_data, compute_climatology
from utils.suntimes import find_suntimes
from .figures import make_subplot_figure, make_barpolar_figure
import pandas as pd
from components import location_selector_callbacks


@callback(
    Output("submit-button", "disabled"),
    [Input("locations", "value"),
     Input("search-button", "n_clicks")],
)
def activate_submit_button(location, _nouse):
    if location is not None and len(location) >= 2:
        return False
    else:
        return True


# Hide the plots until the button hasn't been clicked
@callback(
    Output("fade-ensemble", "is_open"),
    [Input("submit-button", "n_clicks")],
)
def toggle_fade(n):
    if not n:
        # Button has never been clicked
        return False
    return True


@callback(
    [Output("ensemble-plot", "figure"),
     #  Output("polar-plot", "figure"),
     Output("error-message", "children", allow_duplicate=True),
     Output("error-modal", "is_open", allow_duplicate=True)],
    Input("submit-button", "n_clicks"),
    [State("locations-list", "data"),
     State("locations", "value"),
     State("models-selection", "value"),
     State("clima-switch", "value")],
    prevent_initial_call=True
)
def generate_figure(n_clicks, locations, location, model, clima_):
    if n_clicks is None:
        return no_update, no_update, no_update

    # unpack locations data
    locations = pd.read_json(locations, orient='split', dtype={"id": str})
    loc = locations[locations['id'] == location]

    try:
        data = get_ensemble_data(latitude=loc['latitude'].item(),
                                 longitude=loc['longitude'].item(),
                                 model=model,
                                 decimate=True,
                                 from_now=True)

        if clima_:
            clima = compute_climatology(latitude=loc['latitude'].item(),
                                        longitude=loc['longitude'].item(),
                                        variables='temperature_2m')
        else:
            clima = None

        sun = find_suntimes(df=data,
                            latitude=loc['latitude'].item(),
                            longitude=loc['longitude'].item(),
                            elevation=loc['elevation'].item())

        loc_label = (
            f"{loc['name'].item()}, {loc['country'].item()} | 🌐 {float(data.attrs['longitude']):.1f}E"
            f", {float(data.attrs['latitude']):.1f}N, {float(data.attrs['elevation']):.0f}m | "
            f"Ens: {model.upper()}"
        )

        return (
            make_subplot_figure(data, clima, loc_label, sun),
            # make_barpolar_figure(data),
            None, False  # deactivate error popup
        )

    except Exception as e:
        return (
            no_update,
            repr(e), True  # Error message
        )


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
    Output('garbage', 'data'),
    Input('ensemble-plot', 'figure'),
    [State('ensemble-plot', 'id')],
    prevent_initial_call=True
)
