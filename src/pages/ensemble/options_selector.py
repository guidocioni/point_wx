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
                    value=ENSEMBLE_MODELS[0]["value"],
                    persistence=True,
                ),
            ],
            className="mb-1",
        ),
        dbc.InputGroup(
            [
                dbc.InputGroupText(
                    dbc.Checkbox(
                        id="clima-switch",
                        value=False,
                    )
                ),
                dbc.Input(placeholder="Compute climatology", disabled=True),
            ],
            className="mb-2",
        ),
        dbc.Button(
            "Submit",
            id={"type": "submit-button", "index": "ensemble"},
            className="col-12",
            size="lg",
            disabled=True,
        ),
    ],
    body=True,
    className="mb-2",
)
