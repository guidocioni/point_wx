import dash_bootstrap_components as dbc
from dash import dcc
from datetime import date, timedelta
from utils.settings import REANALYSIS_MODELS

opts_selector = dbc.Card(
    [
        dbc.InputGroup(
            [
                dbc.InputGroupText("Model"),
                dbc.Select(
                    id="models-selection-climate",
                    options=REANALYSIS_MODELS,
                    value=REANALYSIS_MODELS[1]["value"],
                    persistence=True
                ),
            ],
            className="mb-2",
        ),
        dbc.InputGroup(
            [
                dbc.InputGroupText("Start Date"),
                dcc.DatePickerSingle(
                    id="date-start-climate",
                    date=date(1991, 1, 1),
                    min_date_allowed=date(1950, 1, 1),
                    max_date_allowed=date.today() - timedelta(days=6),
                    className="dash-bootstrap",
                    display_format="DD/MM/YYYY",
                    first_day_of_week=1,
                    with_portal=True,
                    day_size=37,
                ),
            ],
            className="mb-2",
        ),
        dbc.InputGroup(
            [
                dbc.InputGroupText("End Date"),
                dcc.DatePickerSingle(
                    id="date-end-climate",
                    date=date(2020, 12, 31),
                    min_date_allowed=date(1950, 1, 1),
                    max_date_allowed=date.today() - timedelta(days=6),
                    className="dash-bootstrap",
                    display_format="DD/MM/YYYY",
                    first_day_of_week=1,
                    with_portal=True,
                    day_size=37
                ),
            ],
            className="mb-2",
        ),
        dbc.Button("Submit",
                   id="submit-button-climate",
                   className="mb-2 col-12",
                   size='lg',
                   disabled=True)
    ],
    body=True, className="mb-2"
)
