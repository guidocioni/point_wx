import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash import html, dcc

loc_selector = dbc.Card(
    [
        html.Div(id="geo"),
        dmc.Text("Location", size="sm"),
        dcc.Dropdown(
            multi=False,
            id="location_search_new",
            className="col-12 mt-1 mb-1",
            style={'fontSize': '15px'},
        ),
        dmc.Button(
            "Geolocate",
            id="geolocate",
            leftSection=DashIconify(icon="ion:location-outline", width=20),
            className="col-12 mb-2 mt-1",
            # variant="light",
            size='xs',
            color='gray',
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
