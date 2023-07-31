import dash
from dash import html, callback, Output, Input, State
from .location_selector import loc_selector
from utils.openmeteo_api import get_locations

dash.register_page(
    __name__,
    path='/ensemble',
    title='Ensemble'
)

layout = html.Div(
    [
        loc_selector
    ]
)

@callback(Output('content', 'children'), Input('radios', 'value'))
def home_radios(value):
    return f'You have selected {value}'


@callback(
    [Output("locations", "options"),
     Output("locations", "value")],
    [Input("search-button", "n_clicks")],
    [State("from_address", "value")],
    prevent_initial_call=True
)
def get_closest_address(n_clicks, from_address):
    if n_clicks is None:
        return []
    else:
        locations = get_locations(from_address)

        options = []
        for _, row in locations.iterrows():
            options.append(
                {
                    "label": "%s (%2.1f,%2.1f,%3.0f m)" % (row['name'], row['longitude'], row['latitude'], row['elevation']),
                    "value": row.id
                }
            )

        return [options, options[0]]