import dash_bootstrap_components as dbc
from datetime import date
from utils.settings import REANALYSIS_MODELS

opts_selector = dbc.Card(
    [
        dbc.InputGroup(
            [
                dbc.InputGroupText("Model"),
                dbc.Select(
                    id="models-selection-climate-daily",
                    options=REANALYSIS_MODELS,
                    value="era5_seamless",
                ),
            ],
            className="mb-2",
        ),
        dbc.InputGroup(
            [
                dbc.InputGroupText("Year"),
                dbc.Input(
                    id="year-selection-climate",
                    value=date.today().year,
                    autocomplete="true",
                    type='number',
                    max=date.today().year,
                    min=1981
                ),
            ],
            className="mb-2",
        ),
        dbc.Button("Submit",
                   id="submit-button-climate-daily",
                   className="mb-2 col-12",
                   size='lg',
                   disabled=True)
    ],
    body=True, className="mb-2"
)
