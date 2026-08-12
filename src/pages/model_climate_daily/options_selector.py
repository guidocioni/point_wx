import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from utils.settings import REANALYSIS_MODELS
from datetime import date
from utils.url_sync import Param, register

acc_vars_options = [
    {"label": "Precipitation [mm]", "value": "precipitation_sum"},
    {"label": "Rain [mm]", "value": "rain_sum"},
    {"label": "Snow [cm]", "value": "snowfall_sum"},
    {"label": "Precipitation hours", "value": "precipitation_hours"},
    {"label": "Sunshine hours", "value": "sunshine_duration"},
    {"label": "Shortwave radiation [MJ/m²]", "value": "shortwave_radiation_sum"},
    {"label": "Reference Evapotranspiration (ET0) [mm]", "value": "et0_fao_evapotranspiration"},
    {"label": "Warm Days (Max > 30°C)", "value": "days_tmax_gt_30"},
    {"label": "Hot Days (Max > 35°C)", "value": "days_tmax_gt_35"},
    {"label": "Tropical Nights (Min >= 20°C)", "value": "days_tmin_gt_20"},
    {"label": "Frost Days (Min <= 0°C)", "value": "days_tmin_lt_0"},
    {"label": "Extreme Warm Days (Max > local 99th pct)", "value": "days_tmax_gt_p99"},
    {"label": "Extreme Cold Days (Min < local 1th pct)", "value": "days_tmin_lt_p01"},
]
daily_vars_options = [
    {"label": "Mean temperature [°C]", "value": "temperature_2m_mean"},
    {"label": "Maximum temperature [°C]", "value": "temperature_2m_max"},
    {"label": "Minimum temperature [°C]", "value": "temperature_2m_min"},
    {"label": "Mean Apparent temperature [°C]", "value": "apparent_temperature_mean"},
    {"label": "Maximum Apparent temperature [°C]", "value": "apparent_temperature_max"},
    {"label": "Minimum Apparent temperature [°C]", "value": "apparent_temperature_min"},
    {"label": "Mean MSLP [hPa]", "value": "pressure_msl_mean"},
    {"label": "Mean Cloud Cover [%]", "value": "cloud_cover_mean"},
    {"label": "Mean Dewpoint [°C]", "value": "dew_point_2m_mean"},
    {"label": "Mean Relative Humidity [%]", "value": "relative_humidity_2m_mean"},
    {"label": "Mean Soil Moisture 0-7 cm [m³/m³]", "value": "soil_moisture_0_to_7cm_mean"},
    {"label": "Mean Soil Moisture 7-28 cm [m³/m³]", "value": "soil_moisture_7_to_28cm_mean"},
    {"label": "Mean Soil Moisture 28-100 cm [m³/m³]", "value": "soil_moisture_28_to_100cm_mean"},
    {"label": "Mean Soil Temperature 0-7 cm [°C]", "value": "soil_temperature_0_to_7cm_mean"},
    {"label": "Mean Soil Temperature 7-28 cm [°C]", "value": "soil_temperature_7_to_28cm_mean"},
    {"label": "Mean Soil Temperature 28-100 cm [°C]", "value": "soil_temperature_28_to_100cm_mean"},
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
            min=1951,
            step=1,
            className="mb-2",
        ),
        dmc.Select(
            label="Accumulated variable",
            id="acc-variable-selection-daily",
            data=acc_vars_options,
            value="precipitation_sum",
            clearable=False,
            allowDeselect=False,
            className="mb-2",
        ),
        dmc.Select(
            label="Daily variable",
            id="inst-variable-selection-daily",
            data=daily_vars_options,
            value="temperature_2m_mean",
            clearable=False,
            allowDeselect=False,
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
    className="mb-2 selector-card",
)


register("daily", [
    Param("models-selection-climate-daily", "value", "model", valid=REANALYSIS_MODELS),
    # No value= on the NumberInput itself: the current year is the fallback, applied
    # only when the URL does not carry a ?year= (see callbacks.update_max_date)
    Param("year-selection-climate", "value", "year", kind="int", lo=1951,
          default=lambda: date.today().year),
    Param("acc-variable-selection-daily", "value", "accvar", valid=acc_vars_options),
    Param("inst-variable-selection-daily", "value", "instvar", valid=daily_vars_options),
])
