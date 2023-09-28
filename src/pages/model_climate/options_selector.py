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
                    value=REANALYSIS_MODELS[1],
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
