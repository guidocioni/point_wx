import dash_bootstrap_components as dbc
from dash import dcc
from utils.settings import DETERMINISTIC_MODELS

opts_selector = dbc.Card(
    [
        dcc.Dropdown(
            options=DETERMINISTIC_MODELS,
            multi=True,
            value=["best_match"],
            id="models-selection-deterministic",
            persistence=True,
            className="mb-2 mt-2",
        ),
        dbc.Button(
            "Submit",
            id={"type": "submit-button", "index": "deterministic"},
            className="mb-2 col-12",
            size="lg",
            disabled=True,
        ),
    ],
    body=True,
    className="mb-2",
)
