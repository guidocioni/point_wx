import dash_bootstrap_components as dbc
from utils.settings import ENSEMBLE_MODELS

opts_selector = dbc.Card(
    [
        dbc.InputGroup(
            [
                dbc.InputGroupText("Model"),
                dbc.Select(
                    id="models-selection",
                    options=ENSEMBLE_MODELS,
                    value=ENSEMBLE_MODELS[0]['value'],
                    persistence=True
                ),
            ],
            className="mb-2",
        ),
        dbc.Row(
            [
                dbc.Button("Submit",
                           id="submit-button",
                           className=["mb-2"],
                           disabled=True)
            ], justify='center'
        ),
    ],
    body=True, className="mb-2"
)
