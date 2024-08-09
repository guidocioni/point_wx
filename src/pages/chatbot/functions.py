'''
This file contains a wrapper for all functions that are exposed to the models automatically
throuh tools.
We can't use the functions directly because we may need to change something before passing the results
or settings some parameters.
'''
from utils.openmeteo_api import make_request
from datetime import datetime
import pytz

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_deterministic_forecast",
            "description": "Get the weather data for a specific location and date range as JSON. Use it to get the input data for your analysis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "object",
                        "description": "The location used to get the weather data, including name, latitude, and longitude.",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "The name of the location. This can be a city a town or a specific location."
                            },
                            "country": {
                                "type": "string",
                                "description": "The name of the country where the location is."
                            },
                            "latitude": {
                                "type": "number",
                                "description": "The latitude of the location in decimal degrees."
                            },
                            "longitude": {
                                "type": "number",
                                "description": "The longitude of the location in decimal degrees."
                            }
                        },
                        "required": ["name", "latitude", "longitude"]
                    },
                    "start_date": {
                        "type": "string",
                        "description": "The start date of the forecast. Needs to be in the format YYYY-mm-dd.",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "The end date of the forecast. Needs to be in the format YYYY-mm-dd.",
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
            "description": "Get the ensemble weather data for a specific location and date range as JSON. This data contains multiple members for the same variable and is thus useful to estimate uncertainty in the forecast.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "object",
                        "description": "The location used to get the weather data, including name, latitude, and longitude.",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "The name of the location. This can be a city a town or a specific location."
                            },
                            "country": {
                                "type": "string",
                                "description": "The name of the country where the location is."
                            },
                            "latitude": {
                                "type": "number",
                                "description": "The latitude of the location in decimal degrees."
                            },
                            "longitude": {
                                "type": "number",
                                "description": "The longitude of the location in decimal degrees."
                            }
                        },
                        "required": ["name", "latitude", "longitude"]
                    },
                    "start_date": {
                        "type": "string",
                        "description": "The start date of the forecast. Needs to be in the format YYYY-mm-dd.",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "The end date of the forecast. Needs to be in the format YYYY-mm-dd.",
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
]

def get_current_datetime(timezone=None):
    if timezone:
        timezone = pytz.timezone(timezone)
    return datetime.now(timezone).strftime("Today is %d %b %Y and the time is %H:%M:%S")


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
    if 'country' in location:
        weather_data['country'] = location['country']
    
    return weather_data


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
    resp = make_request(url="https://ensemble-api.open-meteo.com/v1/ensemble", payload=payload)
    ensemble_data = resp.json()
    ensemble_data["location"] = location["name"]
    if 'country' in location:
        ensemble_data['country'] = location['country']
    
    return ensemble_data
