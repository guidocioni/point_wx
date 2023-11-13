import dash_bootstrap_components as dbc
import pandas as pd
from utils.settings import REANALYSIS_MODELS

opts_selector = dbc.Card(
    [
        dbc.InputGroup(
            [
                dbc.InputGroupText("Model"),
                dbc.Select(
                    id="models-selection-climate-daily",
                    options=REANALYSIS_MODELS,
                    value=REANALYSIS_MODELS[1]["value"],
                    persistence=True
                ),
            ],
            className="mb-2",
        ),
        dbc.InputGroup(
            [
                dbc.InputGroupText("Year"),
                dbc.Input(
                    id="year-selection-climate",
                    value=pd.to_datetime('now', utc=True).year,
                    autocomplete=True,
                    type='number',
                    persistence=True
                ),
            ],
            className="mb-2",
        ),
        dbc.Row(
            [
                dbc.Button("Submit",
                           id="submit-button-climate-daily",
                           className=["mb-2"],
                           disabled=True)
            ], justify='center'
        ),
    ],
    body=True, className="mb-2"
)
