import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from utils.settings import REANALYSIS_MODELS

opts_selector = dbc.Card(
    [
        dmc.Select(
            label='Model',
            id="models-selection-climate",
            data=REANALYSIS_MODELS,
            value="era5_seamless",
            className="mb-2",
            allowDeselect=False
        ),
        dmc.DatePickerInput(
            label="Date Range",
            id="date-range-climate",
            value=["1991-01-01", "2020-12-31"],
            minDate="1950-01-01",
            valueFormat="DD/MM/YYYY",
            firstDayOfWeek=1,
            allowSingleDateInRange=False,
            className="mb-2",
            type='range'
        ),
        dbc.Tooltip(
            "Data in this date range will be used for the plots."
            " If you want to show typical conditions choose a 30 years period"
            " otherwise you can select any period you want."
            " Note that at least one month of data is needed.",
            placement='top',
            target="date-range-climate",
        ),
        dbc.Button(
            "Submit",
            id={"type": "submit-button", "index": "monthly"},
            className="col-12",
            size="md",
            disabled=True,
        ),
    ],
    body=True,
    className="mb-2",
)
