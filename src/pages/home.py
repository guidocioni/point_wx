import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/", redirect_from=["/home"], title="Home")

layout = html.Div(
    [
        html.H3("Introduction"),
        html.P(
            [
                "This application lets you explore the weather (wx) for every city (point) in the World!",
                "You can decide whether to explore forecasts for the next days or "
                "dive into the history",
            ],
            className="mb-2",
        ),
        html.Hr(),
        html.H3("How to Use"),
        html.Div(
            [
                html.P("There are many different pages to explore different aspects. "
                       "Every page has tooltips and an info box at the top that should guide you in the right direction."),
                html.P(
                        "To select a location either use the search box, geolocation or just click on the map. "
                        "Then, after selecting the other parameters, press on submit. "
                        "Remember to press again on submit to update the results if you change something!"
                ),
            ],
            className="mb-2",
        ),
        html.Hr(),
        html.H4("Good to know"),
        html.Div(
            [
                dbc.Alert(
                    (
                        "This app will work also on mobile devices, "
                        "however plots may not be optimized for small displays."
                    ),
                    color="info",
                ),
            ]
        ),
    ]
)
