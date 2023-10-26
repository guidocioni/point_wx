import dash
from dash import html
import dash_bootstrap_components as dbc
from components.location_selector import loc_selector
from .options_selector import opts_selector
from .figures import fig_prec_climate_daily, fig_temp_climate_daily
from .callbacks import *

dash.register_page(
    __name__,
    path='/dailyclimate',
    title='Climate (daily)'
)

layout = html.Div(
    [
        dbc.Accordion([
            dbc.AccordionItem(
                html.Div(
                    [
                        "Here you can compare the daily typical climate to a certain year evolution. ",
                        html.Br(),
                        "The historical data starts from 1981.",
                    ]
                ),
                title='Description (click to show)')],
            start_collapsed=True, className="mb-2"),
        dbc.Row(
            [
                dbc.Col(loc_selector),
                dbc.Col(opts_selector),
            ]
        ),
        dbc.Fade(
            [
                dbc.Row(
                    [
                        dbc.Col(dbc.Spinner(fig_prec_climate_daily))
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(dbc.Spinner(fig_temp_climate_daily))
                    ]
                ),
            ], id="fade-climate-daily",
            is_in=False,
            appear=False
        )

    ]
)
