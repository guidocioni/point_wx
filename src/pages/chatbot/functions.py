"""
This file contains a wrapper for all functions that are exposed to the models automatically
throuh tools.
We can't use the functions directly because we may need to change something before passing the results
or settings some parameters.
"""

from utils.openmeteo_api import make_request, compute_climatology, r
from utils.settings import cache
from datetime import datetime
import pytz

location_object = {
    "type": "object",
    "description": "The location used to get the weather data, including name, country, latitude, and longitude.",
    "properties": {
        "name": {
            "type": "string",
            "description": "The name of the location. This can be a city a town or a specific location.",
        },
        "country": {
            "type": "string",
            "description": "The name of the country where the location is.",
        },
        "latitude": {
            "type": "number",
            "description": "The latitude of the location in decimal degrees.",
        },
        "longitude": {
            "type": "number",
            "description": "The longitude of the location in decimal degrees.",
        },
    },
    "required": ["name", "latitude", "longitude"],
}

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_deterministic_forecast",
            "description": "Get deterministic weather forecasts for a specific location and date range as JSON. Use it to get the input data for your analysis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": location_object,
                    "start_date": {
                        "type": "string",
                        "description": "The start date of the forecast. Needs to be in the format YYYY-mm-dd. The minimum that this parameter can be is today, the maximum is 10 days from today.",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "The end date of the forecast. Needs to be in the format YYYY-mm-dd. The minimum that this parameter can be is today, the maximum is 10 days from today.",
                    },
                },
                "required": ["location", "start_date", "end_date"],
                "additionalProperties": False,
            },
        },
        "strict": True,
    },
    {
        "type": "function",
        "function": {
            "name": "get_ensemble_forecast",
            "description": (
                "Get the ensemble weather data for a specific location and date range as JSON. This data contains multiple members for the same variable and is thus useful to estimate uncertainty in the forecast. The member number is affixed to the variable name, e.g. temperature_2m_member_23."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "location": location_object,
                    "start_date": {
                        "type": "string",
                        "description": "The start date of the forecast. Needs to be in the format YYYY-mm-dd. The minimum that this parameter can be is today, the maximum is 15 days from today.",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "The end date of the forecast. Needs to be in the format YYYY-mm-dd. The minimum that this parameter can be is today, the maximum is 15 days from today.",
                    },
                },
                "required": ["location", "start_date", "end_date"],
                "additionalProperties": False,
            },
        },
        "strict": True,
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_datetime",
            "description": "Get the current date and time by providing the local timezone",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "The local timezone to get the date for. It needs to be in the pytz format, so e.g. Europe/Berlin",
                    },
                },
                "required": ["timezone"],
                "additionalProperties": False,
            },
        },
        "strict": True,
    },
    {
        "type": "function",
        "function": {
            "name": "get_climatology",
            "description": (
                "Get the daily climatological data (data averaged over a 30 years period) to compare observed values to the climatological average. "
                "The output of this function will be a JSON exported from a pandas dataframe using the orient='records' option. In order to identify the day of the year use the 'doy' attribute, which was obtained from the date by formatting as '%m%d'. Note that there is no year in this date, as these data are multi-year average."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "location": location_object,
                },
                "required": ["location"],
                "additionalProperties": False,
            },
        },
        "strict": True,
    },
    {
        "type": "function",
        "function": {
            "name": "get_historical_daily_data",
            "description": (
                "Get the daily historical data for a location. "
                "This is the best estimate that we have according to reanalysis of the weather evolution everywhere on Earth. Still, it is based on models so it's not the same as a direct observation."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "location": location_object,
                    "start_date": {
                        "type": "string",
                        "description": "The start date to retrieve historical data. Needs to be in the format YYYY-mm-dd. The minimum value for this parameter is 1940-01-01, the maximum value is 6 days before today.",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "The end date to retrieve historical data. Needs to be in the format YYYY-mm-dd. The minimum value for this parameter is 1940-01-01, the maximum value is 6 days before today",
                    },
                },
                "required": ["location", "start_date", "end_date"],
                "additionalProperties": False,
            },
        },
        "strict": True,
    },
    {
        "type": "function",
        "function": {
            "name": "get_radar_data",
            "description": (
                "Get radar-based estimation of precipitation for locations that are in Germany. "
                "The Response is a JSON containing array of objects with time and estimated precipitation for the next two hours"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "An address (could be a street, road, location or city) located in Germany",
                    },
                },
                "required": ["address"],
                "additionalProperties": False,
            },
        },
        "strict": True,
    },
]


def get_current_datetime(timezone=None):
    if timezone:
        timezone = pytz.timezone(timezone)
    return datetime.now(timezone).strftime("Today is %d %b %Y and the time is %H:%M:%S")

@cache.memoize(3600)
def get_deterministic_forecast(location, start_date, end_date):
    payload = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "hourly": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation_probability,precipitation,rain,snowfall,pressure_msl,cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,wind_speed_10m,wind_direction_10m,wind_gusts_10m,cape,sunshine_duration,snow_depth,is_day,uv_index,temperature_850hPa",
        "minutely_15": "temperature_2m,relative_humidity_2m,precipitation,rain,snowfall,wind_speed_10m,wind_direction_10m,wind_gusts_10m,cape,is_day",
        "timezone": "auto",
        "models": "best_match",
        "start_date": start_date,
        "end_date": end_date,
    }
    resp = make_request(url="https://api.open-meteo.com/v1/forecast", payload=payload)
    weather_data = resp.json()
    weather_data["location"] = location["name"]
    if "country" in location:
        weather_data["country"] = location["country"]

    return weather_data

@cache.memoize(3600)
def get_ensemble_forecast(location, start_date, end_date):
    payload = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "hourly": "temperature_2m,precipitation,rain,snowfall",
        "timezone": "auto",
        "models": "icon_seamless",
        "start_date": start_date,
        "end_date": end_date,
    }
    resp = make_request(
        url="https://ensemble-api.open-meteo.com/v1/ensemble", payload=payload
    )
    ensemble_data = resp.json()
    ensemble_data["location"] = location["name"]
    if "country" in location:
        ensemble_data["country"] = location["country"]

    return ensemble_data

@cache.memoize(86400)
def get_climatology(location):
    clima = compute_climatology(
        latitude=location["latitude"],
        longitude=location["longitude"],
        daily=True,
        model="era5_seamless",
        variables="temperature_2m_max,temperature_2m_min,sunshine_duration,precipitation_sum,rain_sum,snowfall_sum",
    )
    clima["sunshine_duration"] = clima["sunshine_duration"] * 3600.0
    weather_data = clima.to_dict(orient="records")

    return weather_data

@cache.memoize(86400)
def get_historical_daily_data(location, start_date, end_date):
    payload = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "daily": "temperature_2m_max,temperature_2m_min,sunshine_duration,precipitation_sum,rain_sum,snowfall_sum",
        "timezone": "auto",
        "models": "era5_seamless",
        "start_date": start_date,
        "end_date": end_date,
    }

    resp = make_request("https://archive-api.open-meteo.com/v1/archive", payload)
    weather_data = resp.json()
    weather_data["location"] = location["name"]
    if "country" in location:
        weather_data["country"] = location["country"]

    return weather_data


def get_radar_data(address):
    payload = {"address": address}
    resp = r.get(url="https://hh.guidocioni.it/nmwr/pointquery", params=payload)
    resp.raise_for_status()

    return resp.json()
