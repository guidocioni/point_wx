# notes
'''
This file is for creating a simple footer element.
This component will sit at the bottom of each page of the application.
'''

# package imports
from dash import html
import dash_bootstrap_components as dbc

footer = html.Footer(
    dbc.Container(
        [
            html.Hr(),
            html.A('Guido Cioni', title ='email_me', href='mailto:guidocioni@gmail.com', target='_blank'),
            " | ",
            html.A("Open Meteo", href='https://open-meteo.com/')
        ]
    )
)
