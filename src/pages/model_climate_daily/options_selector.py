import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from utils.settings import REANALYSIS_MODELS

acc_vars_options = [
    {"label": "Precipitation [mm]", "value": "precipitation_sum"},
    {"label": "Rain [mm]", "value": "rain_sum"},
    {"label": "Snow [cm]", "value": "snowfall_sum"},
    {"label": "Precipitation hours", "value": "precipitation_hours"},
    # {"label": "Sunshine hours", "value": "sunshine_duration"}, # When it will be supported by the Ensemble daily aggregation
    {"label": "Shortwave radiation [MJ/m²]", "value": "shortwave_radiation_sum"},
    {"label": "Wind speed maximum [km/h]", "value": "wind_speed_10m_max"},
    {"label": "Wind speed [km/h]", "value": "wind_speed_10m_mean"},
    {"label": "Mean Cloud Cover [%]", "value": "cloud_cover_mean"},
]
daily_vars_options = [
    {"label": "Mean temperature [°C]", "value": "temperature_2m_mean"},
    {"label": "Maximum temperature [°C]", "value": "temperature_2m_max"},
    {"label": "Minimum temperature [°C]", "value": "temperature_2m_min"},
    {"label": "Mean MSLP [hPa]", "value": "pressure_msl_mean"},
    {"label": "Mean Cloud Cover [%]", "value": "cloud_cover_mean"},
    {"label": "Mean Dewpoint [°C]", "value": "dew_point_2m_mean"},
    {"label": "Mean Relative Humidity [%]", "value": "relative_humidity_2m_mean"},
    {"label": "Mean Soil Moisture 0-7 cm [m³/m³]", "value": "soil_moisture_0_to_7cm_mean"},
    {"label": "Mean Soil Moisture 7-28 cm [m³/m³]", "value": "soil_moisture_7_to_28cm_mean"},
    {"label": "Mean Soil Moisture 28-100 cm [m³/m³]", "value": "soil_moisture_28_to_100cm_mean"},
    {"label": "Mean Soil Temperature 0-7 cm [m³/m³]", "value": "soil_temperature_0_to_7cm_mean"},
    {"label": "Mean Soil Temperature 7-28 cm [m³/m³]", "value": "soil_temperature_7_to_28cm_mean"},
    {"label": "Mean Soil Temperature 28-100 cm [m³/m³]", "value": "soil_temperature_28_to_100cm_mean"},
]

opts_selector = dbc.Card(
    [
        dmc.Select(
            label="Model",
            id="models-selection-climate-daily",
            data=REANALYSIS_MODELS,
            value="era5",
            className="mb-2",
            allowDeselect=False,
            style={'display':'none'} # The other models cause too many issues, so we disable it for now
        ),
        dmc.NumberInput(
            id="year-selection-climate",
            label="Year",
            min=1981,
            step=1,
            className="mb-2",
        ),
        dmc.Select(
            label="Accumulated variable",
            id="acc-variable-selection-daily",
            data=acc_vars_options,
            value="precipitation_sum",
            clearable=False,
            className="mb-2",
        ),
        dmc.Select(
            label="Daily variable",
            id="inst-variable-selection-daily",
            data=daily_vars_options,
            value="temperature_2m_mean",
            clearable=False,
            className="mb-2",
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
