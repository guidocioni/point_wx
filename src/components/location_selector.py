import dash_bootstrap_components as dbc
from dash import html, dcc

loc_selector = dbc.Card(
    [
        html.Div(id="geo"),
        dcc.Dropdown(
            multi=False,
            id="location_search_new",
            className="mt-2 col-12",
        ),
        dbc.Button(
            id="geolocate",
            className="fa-solid fa-location-dot col-12 mb-2 mt-2",
            color="secondary",
            outline=False,
        ),
        dbc.Accordion(
            id="map-accordion",
            children=[
                dbc.AccordionItem(
                    children=html.Div(id="map-div"),
                    title="Map (click to show)",
                    class_name="map-accordion-body-padding",
                )
            ],
            start_collapsed=True,
        ),
    ],
    body=True,
    className="mb-2",
)
