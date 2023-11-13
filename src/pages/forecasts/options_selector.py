import dash_bootstrap_components as dbc
from dash import dcc
from utils.settings import DETERMINISTIC_MODELS

opts_selector = dbc.Card(
    [
        dbc.Row(
            [
                dcc.Dropdown(
                    options=DETERMINISTIC_MODELS,
                    multi=True,
                    value=["best_match"],
                    id="models-selection-deterministic",
                    persistence=True
                ),
            ],
            className="mb-2",
        ),
        dbc.Row(
            [
                dbc.Button("Submit",
                           id="submit-button-deterministic",
                           className=["mb-2"],
                           disabled=True)
            ], justify='center'
        ),
    ],
    body=True, className="mb-2"
)
