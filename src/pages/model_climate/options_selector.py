import dash_bootstrap_components as dbc
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
                dbc.InputGroupText("Start date"),
                dbc.Input(
                    id="date-start-climate",
                    value='1991-01-01',
                    type='text',
                    persistence=True
                ),
            ],
            className="mb-2",
        ),
        dbc.InputGroup(
            [
                dbc.InputGroupText("End date"),
                dbc.Input(
                    id="date-end-climate",
                    value='2020-12-31',
                    type='text',
                    persistence=True
                ),
            ],
            className="mb-2",
        ),
        dbc.Row(
            [
                dbc.Button("Submit",
                           id="submit-button-climate",
                           className=["mb-2"],
                           disabled=True)
            ], justify='center'
        ),
    ],
    body=True, className="mb-2"
)
