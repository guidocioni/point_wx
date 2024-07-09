import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from utils.settings import DETERMINISTIC_MODELS

opts_selector = dbc.Card(
    [
        dmc.MultiSelect(
            label='Models',
            id="models-selection-deterministic",
            data=DETERMINISTIC_MODELS,
            value=["best_match"],
            persistence="true",
            className="mb-2",
            searchable=True,
            clearable=True,
            hidePickedOptions=True
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
