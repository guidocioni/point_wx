import dash_bootstrap_components as dbc
from dash import html

loc_selector = dbc.Card(
    [
        dbc.Row(
            dbc.InputGroup(
                [
                    dbc.Input(placeholder="City/Town",
                              id='from_address',
                              type='text',
                              autocomplete="true",
                              persistence=True),
                ],
                className="mb-2",
            ),),
        dbc.Row(
            [
                dbc.Button("Search",
                           id="search-button",
                           color="secondary",
                           className="d-grid gap-2 col-10 mb-2")
            ], justify='center'
        ),
        dbc.Row(
            html.Div('Closest Locations',
                     id='closest_locations_description',
                     className="mb-2"),
        ),
        dbc.Row(
            dbc.InputGroup(
                [
                    dbc.Select(
                        id="locations",
                        persistence=True
                    ),
                ],
                className="mb-2",
            ),
        )
    ],
    body=True, className="mb-2"
)
