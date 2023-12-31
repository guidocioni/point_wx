import dash_bootstrap_components as dbc
from utils.settings import ENSEMBLE_MODELS

opts_selector = dbc.Card(
    [
        dbc.InputGroup(
            [
                dbc.InputGroupText("Model"),
                dbc.Select(
                    id="models-selection-meteogram",
                    options=ENSEMBLE_MODELS,
                    value="gfs_seamless",
                    persistence=True
                ),
            ],
            className="mb-2",
        ),
        dbc.Button("Submit",
                   id="submit-button-meteogram",
                   className="mb-2 col-12",
                   size='lg',
                   disabled=True)
    ],
    body=True, className="mb-2"
)
