import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
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
                    value="era5_seamless",
                ),
            ],
            className="mb-2",
        ),
        dmc.DateRangePicker(
            label='Date Range',
            id="date-range-climate",
            value=['1991-01-01', '2020-12-31'],
            minDate='1950-01-01',
            maxDate=(date.today() - timedelta(days=6)).strftime('%Y-%m-%d'),
            inputFormat="DD/MM/YYYY",
            firstDayOfWeek=1,
            allowSingleDateInRange=False,
            clearable=True,
            className="mb-2",
            amountOfMonths=2,
        ),
        dbc.Button("Submit",
                   id={"type": "submit-button",
                       "index": "monthly"},
                   className="mb-2 col-12",
                   size='lg',
                   disabled=True)
    ],
    body=True, className="mb-2"
)
