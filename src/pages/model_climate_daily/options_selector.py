import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from utils.settings import REANALYSIS_MODELS

acc_vars_options = [
    {"label": "Precipitation [mm]", "value": "precipitation_sum"},
    {"label": "Rain [mm]", "value": "rain_sum"},
    {"label": "Snow [cm]", "value": "snowfall_sum"},
    {"label": "Precipitation hours", "value": "precipitation_hours"},
    # {"label": "Sunshine hours", "value": "sunshine_duration"},
    {"label": "Shortwave radiation [MJ/m²]", "value": "shortwave_radiation_sum"},
    {"label": "Wind speed maximum [km/h]", "value": "wind_speed_10m_max"},
]
daily_vars_options = [
    {"label": "Mean temperature [°C]", "value": "temperature_2m_mean"},
    {"label": "Maximum temperature [°C]", "value": "temperature_2m_max"},
    {"label": "Minimum temperature [°C]", "value": "temperature_2m_min"},
    {"label": "Mean MSLP [hPa]", "value": "pressure_msl_mean"},
]

opts_selector = dbc.Card(
    [
        dmc.Select(
            label="Model",
            id="models-selection-climate-daily",
            data=REANALYSIS_MODELS,
            value="era5_seamless",
            className="mb-2",
            allowDeselect=False,
        ),
        dmc.NumberInput(
            id="year-selection-climate",
            label="Year",
            min=1981,
            step=1,
            className="mb-2",
        ),
        dmc.Accordion(
            children=[
                dmc.AccordionItem(
                    style={"padding": "0px"},
                    value="options",
                    children=[
                        dmc.AccordionControl("Additional options"),
                        dmc.AccordionPanel(
                            style={"padding": "0px"},
                            children=[
                                dmc.Select(
                                    label="Accumulated variable",
                                    id="acc-variable-selection-daily",
                                    data=acc_vars_options,
                                    value="precipitation_sum",
                                    clearable=False,
                                ),
                                dmc.Select(
                                    label="Daily variable",
                                    id="inst-variable-selection-daily",
                                    data=daily_vars_options,
                                    value="temperature_2m_mean",
                                    clearable=False,
                                ),
                            ]
                        ),
                    ],
                )
            ],
            variant="contained",
            className="mb-2",
            style={"padding": "0px"}
        ),
        dbc.Button(
            "Submit",
            id={"type": "submit-button", "index": "daily"},
            className="col-12",
            size="md",
            disabled=True,
        ),
    ],
    body=True,
    className="mb-2",
)
