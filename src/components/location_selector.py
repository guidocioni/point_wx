import dash_bootstrap_components as dbc
from dash import html

loc_selector = dbc.Card(
    [
        dbc.InputGroup(
            dbc.Input(placeholder="City/Town",
                      id='from_address',
                      type='text',
                      autocomplete="true",
                      persistence=True),
            className="mb-2"),
        dbc.Button("Search",
                   id="search-button",
                   color="secondary",
                   className="mb-2 col-12"),
        html.Div('Closest Locations',
                 id='closest_locations_description',
                 className="mb-2"),
        dbc.InputGroup(
            dbc.Spinner(
                dbc.Select(
                    id="locations",
                    persistence=True
                )
            ),
        )
    ],
    body=True,
    className="mb-2",
)
