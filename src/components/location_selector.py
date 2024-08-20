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
                style={"fontSize": "15px"},
            ),
        dbc.Tooltip(
            "Start typing the name of a location (city, town, ...)"
            " and the dropdown will populate with some options."
            " Otherwise you can use the geolocation button "
            " or select a point on the map.",
            placement='top',
            target="location_search_new",
        ),
        dmc.Button(
            "Geolocate",
            id="geolocate",
            leftSection=DashIconify(icon="ion:location-outline", width=20),
            className="col-12 mb-2 mt-1",
            loaderProps={"type": "dots"},
            size="xs",
            color="gray",
            loading=False,
        ),
        dbc.Tooltip(
            "Use this button to get the current location",
            placement='top',
            target="geolocate",
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
        dbc.Tooltip(
            "You can use the map to visualise the location,"
            " or to select one by clicking on a point.",
            placement='top',
            target="map-accordion",
        ),
    ],
    body=True,
    className="mb-2",
)
