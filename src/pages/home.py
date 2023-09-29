import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(
    __name__,
    path='/',
    redirect_from=['/home'],
    title='Home'
)

layout = html.Div(
    [
        dbc.Card(
            [html.H3("Introduction"),
             html.Div(["This application lets you explore the weather (WX) for every city in the World!",
                      html.Br(),
                      "You can decide whether to explore forecasts for the next days or "
                       "dive into the history"])],
            body=True,
            className="mb-2"),
        dbc.Card(
            [html.H3("How to Use"),
             html.Div([
                 "There are many different pages to explore different aspects. ",
                 html.Br(),
                 "First of all type in the location you want to explore, then press on Search. ",
                 "You will get a list of results: choose the one that you want. ",
                 html.Br(),
                 "Afterwards you just have to choose the different parameters on the other box and press on Submit. ",
                 "Computation can take a while, although many results are cached. ",
                 html.Br(),
                 "Remember to always press on submit if you change something!"
             ])],
            body=True,
            className="mb-2")
    ]
)
