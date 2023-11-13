import dash_bootstrap_components as dbc
from utils.settings import ENSEMBLE_MODELS, ENSEMBLE_VARS

opts_selector = dbc.Card(
    [
        dbc.InputGroup(
            [
                dbc.InputGroupText("Model"),
                dbc.Select(
                    id="models-selection-heatmap",
                    options=ENSEMBLE_MODELS,
                    value=ENSEMBLE_MODELS[0]['value'],
                    persistence=True
                ),
            ],
            className="mb-2",
        ),
        dbc.InputGroup(
            [
                dbc.InputGroupText("Variable"),
                dbc.Select(
                    id="variable-selection-heatmap",
                    options=ENSEMBLE_VARS,
                    value=ENSEMBLE_VARS[0],
                    persistence=True
                ),
            ],
            className="mb-2",
        ),
        dbc.Row(
            [
                dbc.Button("Submit",
                           id="submit-button-heatmap",
                           className=["mb-2"],
                           disabled=True)
            ], justify='center'
        ),
    ],
    body=True, className="mb-2"
)
