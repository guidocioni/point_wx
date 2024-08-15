import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from utils.settings import DETERMINISTIC_MODELS, DETERMINISTIC_VARS

opts_selector = dbc.Card(
    [
        dmc.MultiSelect(
            label='Models',
            id="models-selection-deterministic-heatmap",
            data=DETERMINISTIC_MODELS,
            value=["icon_seamless", "gfs_seamless", "ecmwf_ifs025"],
            persistence="true",
            className="mb-2",
            searchable=True,
            clearable=True,
            hidePickedOptions=True
        ),
        dmc.Select(
            label='Variable',
            id="variable-selection-deterministic-heatmap",
            data=DETERMINISTIC_VARS,
            value="temperature_2m",
            persistence="true",
            className="mb-2",
            clearable=False,
            ),
        dbc.Button(
            "Submit",
            id={"type": "submit-button", "index": "deterministic-heatmap"},
            className="mb-2 col-12",
            size="md",
            disabled=True,
        ),
    ],
    body=True,
    className="mb-2",
)
