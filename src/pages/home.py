import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/", redirect_from=["/home"], title="Home")

layout = html.Div(
    [
        html.H3("Introduction"),
        html.P(
            [
                "This application lets you explore the weather (WX) for every city in the World!",
                "You can decide whether to explore forecasts for the next days or "
                "dive into the history",
            ],
            className="mb-2",
        ),
        html.Hr(),
        html.H3("How to Use"),
        html.Div(
            [
                html.P("There are many different pages to explore different aspects. "),
                html.P(
                    [
                        "First of all type in the location you want to explore, then press on Search. ",
                        "You will get a list of results: choose the one that you want. ",
                    ]
                ),
                html.P(
                    [
                        "Afterwards you just have to choose the different parameters on the other box and press on Submit. ",
                        "Computation can take a while, although many results are cached. ",
                    ]
                ),
                html.P("Remember to always press on submit if you change something!"),
            ],
            className="mb-2",
        ),
        html.Hr(),
        html.H4("Good to know"),
        html.Div(
            [
                dbc.Alert(
                    (
                        "This app will also work on mobile devices, "
                        "however plots may not be optimized for small displays"
                    ),
                    color="info",
                ),
            ]
        ),
    ]
)
