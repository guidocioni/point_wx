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
        dbc.ButtonGroup([
            dbc.Button("Search",
                       id="search-button",
                       color="secondary",
                       className="col-10"),
            dbc.Button(id='geolocate',
                       className="fa-solid fa-location-dot col-2",
                       color="secondary", outline=True)
        ], className="col-12 mb-2"),
        dbc.Spinner(
            dbc.InputGroup(
                dbc.Select(
                    id="locations",
                    persistence=True
                ),
                className="mb-2"
            ),
        ),
        dbc.Accordion(id='map-accordion',
                      children=[
                          dbc.AccordionItem(
                              children=html.Div(id='map-div'),
                              title='Map (click to show)')
                      ],
                      start_collapsed=True)
    ],
    body=True,
    className="mb-2",
)
