import dash_bootstrap_components as dbc
from dash import html

loc_selector = dbc.Card(
    [
        dbc.InputGroup(
            [
                dbc.Input(placeholder="Where are you?",
                          id='from_address',
                          type='text',
                          autoComplete=True),
            ],
            className="mb-2",
        ),
        dbc.Row(
            [
                dbc.Button("Search",
                           id="search-button",
                           className=["mb-2"],)
            ], justify='center'
        ),
        html.Div('Here are the closest locations',
                 id='closest_locations_description'),
        dbc.InputGroup(
            [
                dbc.Select(
                    id="locations",
                    options=[],
                    value=[],
                ),
            ],
            className="mb-2",
        )
    ],
    body=True, className="mb-2"
)
