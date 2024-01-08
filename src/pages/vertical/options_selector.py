import dash_bootstrap_components as dbc
from utils.settings import DETERMINISTIC_MODELS, ENSEMBLE_VARS

opts_selector = dbc.Card(
    [
        dbc.InputGroup(
            [
                dbc.InputGroupText("Model"),
                dbc.Select(
                    id="models-selection-vertical",
                    options=DETERMINISTIC_MODELS,
                    value='best_match',
                    persistence=True
                ),
            ],
            className="mb-2",
        ),
        dbc.Button("Submit",
                   id="submit-button-vertical",
                   className="mb-2 col-12",
                   size='lg',
                   disabled=True)
    ],
    body=True, className="mb-2"
)
