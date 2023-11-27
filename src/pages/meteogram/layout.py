import dash
from dash import html
import dash_bootstrap_components as dbc
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
            dbc.Accordion([
                dbc.AccordionItem(
                    html.Div(
                        [
                            "Simple meteogram",
                            html.Br(),
                            "",
                            html.Br(),
                        ]
                    ),
                    title='Description (click to show)')
            ], start_collapsed=True, className="mb-2")
        ),
        dbc.Row(
            [
                dbc.Col(loc_selector, sm=12, md=12, lg=6),
                dbc.Col(opts_selector, sm=12, md=12, lg=6)
            ]
        ),
        dbc.Row(
            dbc.Fade(
                dbc.Col(
                    [
                        dbc.Spinner(fig_subplots),
                    ]
                ),
                id="fade-meteogram",
                is_in=False,
                appear=False)
        ),
    ]
)
