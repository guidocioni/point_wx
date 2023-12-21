import dash_bootstrap_components as dbc
from utils.settings import ENSEMBLE_MODELS

opts_selector = dbc.Card(
    [
        dbc.Row(
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
        ),
        dbc.Row(
            [
                dbc.Button("Submit",
                           id="submit-button-meteogram",
                           className="d-grid gap-2 col-10",
                           size='lg',
                           disabled=True)
            ], justify='center'
        ),
    ],
    body=True, className="mb-2"
)
