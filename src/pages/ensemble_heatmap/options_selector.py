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
                    value=ENSEMBLE_MODELS[0]["value"],
                    persistence=True,
                ),
            ],
            className="mb-2",
        ),
        dbc.InputGroup(
            [
                dbc.InputGroupText("Variable"),
                dbc.Select(
                    id="variable-selection-heatmap",
                    options=ENSEMBLE_VARS
                    + ["accumulated_precip", "accumulated_liquid", "accumulated_snow"],
                    value=ENSEMBLE_VARS[0],
                    persistence=True,
                ),
            ],
            className="mb-2",
        ),
        dbc.Button(
            "Submit",
            id={"type": "submit-button", "index": "heatmap"},
            className="mb-2 col-12",
            size="lg",
            disabled=True,
        ),
    ],
    body=True,
    className="mb-2",
)
