import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from utils.settings import REANALYSIS_MODELS

opts_selector = dbc.Card(
    [
        dmc.Select(
            label='Model',
            id="models-selection-climate-calendar",
            data=REANALYSIS_MODELS,
            value="era5_seamless",
            className="mb-2",
            allowDeselect=False
        ),
        dmc.Select(
            label='Graph',
            id="graph-selection-climate-calendar",
            data=[
                    {"label": "Accumulated precipitation (mm)", "value": "accumulated_precipitation"},
                    {"label": "Wet days (Precipitation >= 1 mm)", "value": "precipitation_days"},
                    {"label": "Precipitation anomaly (%)", "value": "precipitation_anomaly"},
                    {"label": "Snow days (snowfall >= 1 cm)", "value": "snow_days"},
                    {"label": "Total snowfall (cm)", "value": "snowfall"},
                    {"label": "Dry days (Precipitation < 1 mm)", "value": "dry_days"},
                    {"label": "Frost days (Tmin <= 0°C)", "value": "frost_days"},
                    {"label": "Overcast days (Cloud cover >= 80%)", "value": "overcast_days"},
                    {"label": "Partly cloudy days (20% <= Cloud cover < 80%)", "value": "partly_cloudy_days"},
                    {"label": "Sunny days (Cloud cover <= 20%)", "value": "sunny_days"},
                    {"label": "Hot days (Tmax >= 30°C)", "value": "hot_days"},
                    {"label": "Tropical nights (Tmin >= 20°C)", "value": "tropical_nights"},
                    {"label": "Dominant wind direction (degree)", "value": "dominant_wind_direction"},
                    {"label": "Temperature anomaly (°C)", "value": "temperature_anomaly"},
                    {"label": "Average temperature (°C)", "value": "temperature_mean"},
                    {"label": "Minimum temperature (°C)", "value": "temperature_min"},
                    {"label": "Maximum temperature (°C)", "value": "temperature_max"},
                ],
            value="accumulated_precipitation",
            className="mb-2",
            allowDeselect=False,
            searchable=True,
            persistence='true'
        ),
        dmc.NumberInput(
            id="year-selection-calendar",
            label="Start year",
            value=1981,
            min=1940,
            step=1,
            className="mb-2",
        ),
        dbc.Button(
            "Submit",
            id={"type": "submit-button", "index": "calendar"},
            className="col-12",
            size="md",
            disabled=True,
        ),
    ],
    body=True,
    className="mb-2",
)
