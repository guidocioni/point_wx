import dash
from dash import html
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from components.location_selector import loc_selector
from .options_selector import opts_selector
from .figures import fig_subplots
from .callbacks import *

dash.register_page(
    __name__,
    path='/meteogram',
    title='Meteogram'
)

layout = html.Div(
    [
        dbc.Row(
            dmc.Accordion(
                children=[
                    dmc.AccordionItem(
                        value='help',
                        children=[
                            dmc.AccordionControl("click to show",
                                                 icon=DashIconify(icon="ion:information",width=30),),
                            dmc.AccordionPanel(
                                dmc.Text(
                                    [
                                        "A simple meteogram showing daily maximum/minimum temperatures, and weather (icons).",
                                        html.Br(),
                                        "The first plot shows the average minimum and maximum temperatures (lines), and the extrema (shading). ",
                                        "The bottom plot shows the sunshine hours (yellow bar), precipitation amount (blue bar), probability (text inside blue bar) and range (vertical line).",
                                        html.Br(),
                                        "The diamond symbols represent the 1991-2020 climatology for the same location."
                                    ]
                                ),
                            ),
                        ],
                    )
                ],
                className="mb-2",
            )
        ),
        dbc.Row(
            [
                dbc.Col(loc_selector, sm=12, md=12, lg=6),
                dbc.Col(opts_selector, sm=12, md=12, lg=6)
            ]
        ),
        dbc.Row(
            dbc.Collapse(
                dbc.Col(
                    [
                        dbc.Spinner(fig_subplots),
                    ]
                ),
                id={'type':'fade', 'index':'meteogram'},
                is_open=False)
        ),
    ]
)
