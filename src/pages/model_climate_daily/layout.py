import dash
from dash import html
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from components.location_selector import loc_selector
from dash_iconify import DashIconify
from .options_selector import opts_selector
from .callbacks import *

dash.register_page(__name__, path="/dailyclimate", title="Climate (daily)")

layout = html.Div(
    [
        dmc.Accordion(
            children=[
                dmc.AccordionItem(
                    value="help",
                    children=[
                        dmc.AccordionControl(
                            "click to show",
                            icon=DashIconify(icon="ion:information", width=30),
                        ),
                        dmc.AccordionPanel(
                            dmc.Text(
                                [
                                    "Here you can compare some variables behaviour of a certain year to historical data. ",
                                    "The first plot shows an accumulation starting from the beginning of the year, while the second plot shows a day to day comparison of the absolute value.",
                                    html.Br(),
                                    "Note that: ",
                                    html.Ul(
                                        children=[
                                            html.Li(
                                                "The minimum year is limited to 1981"
                                            ),
                                            html.Li(
                                                "The percentiles of the accumulated variable are computed on the period 1981-2020"
                                            ),
                                            html.Li(
                                                "The percentiles/statistics of the daily variable are computed on the period 1991-2020"
                                            ),
                                            html.Li(
                                                "ERA5-Seamless is the best option as it combines both ERA5 and ERA5-Land. IFS only covers from 2017 onwards and the option 'Best Match' combines ERA5-Seamless in the past with IFS from 2017, but statistics computed on this may not be consistent. CERRA only covers Europe up to 2021."
                                            ),
                                        ]
                                    ),
                                    "If selecting the current year, 10 days of forecasts from ECMWF-IFS are also shown.",
                                ]
                            ),
                        ),
                    ],
                )
            ],
            className="mb-2",
        ),
        dbc.Row(
            [
                dbc.Col(loc_selector, sm=12, md=12, lg=6),
                dbc.Col(opts_selector, sm=12, md=12, lg=6),
            ]
        ),
        dbc.Collapse(
            dbc.Spinner(
                html.Div([
                    html.Div(id="prec-climate-daily-container"),
                    html.Div(id="temp-climate-daily-container")
                ])
            
            ),
            id={"type": "fade", "index": "daily"},
            is_open=False,
        ),
    ]
)
