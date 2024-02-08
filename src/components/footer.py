# notes
'''
This file is for creating a simple footer element.
This component will sit at the bottom of each page of the application.
'''

# package imports
from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

footer = html.Footer(
    dbc.Container(
        [
            dcc.Link(
                dmc.Affix(dbc.Button(class_name='fa-solid fa-circle-chevron-up fa-3x',
                                     outline=True,
                                     id='back-to-top-button',
                                     style={'display':'none'}),
                          position={"bottom": 10, "right": 10},
                          ),
                href="#content"
            ),
            html.Hr(),
            html.A('Guido Cioni', title='email_me',
                   href='mailto:guidocioni@gmail.com', target='_blank'),
            " | ",
            html.A("Open Meteo", href='https://open-meteo.com/')
        ]
    )
)
