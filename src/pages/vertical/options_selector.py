import dash_bootstrap_components as dbc
from utils.settings import DETERMINISTIC_MODELS, ENSEMBLE_VARS

opts_selector = dbc.Card(
    [
        dbc.InputGroup(
            [
                dbc.InputGroupText("Model"),
                dbc.Select(
                    id="models-selection-vertical",
                    # Manually remove models that do not have vertical level coverage
                    options=[
                        d
                        for d in DETERMINISTIC_MODELS
                        if d["value"]
                        not in [
                            "metno_nordic",
                            "meteofrance_arome_france_hd",
                            "bom_access_global",
                        ]
                    ],
                    value="best_match",
                    persistence=True,
                ),
            ],
            className="mb-2",
        ),
        dbc.Button(
            "Submit",
            id={"type": "submit-button", "index": "vertical"},
            className="mb-2 col-12",
            size="lg",
            disabled=True,
        ),
    ],
    body=True,
    className="mb-2",
)
