"""
This file contains a wrapper for all functions that are exposed to the models automatically
throuh tools.
TODO
- Remove useless spaces? 
"""

from utils.openmeteo_api import make_request, compute_climatology, r
from utils.settings import cache, OPENWEATHERMAP_KEY
from datetime import datetime
import pytz
import pandas as pd

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
            "description": "Get deterministic weather forecasts for a specific location and date range as JSON. Use it to get the input data for your analysis. These function returns an object with variables defined every hour ('hourly') or every day ('daily'). The returned data may contain the following variables: "
            "-precipitation is the total preciptiation (in all forms), which is a sum of rain, snowfall, showers. Precipitation probability is based on ensemble members. "
            "-cloud cover total is the total amount at the surface, which is consisted by low, mid and high cloud cover"
            "-wind_speed_10m,wind_direction_10m,wind_gusts_10m are the speed, direction and gusts, respectively at 10m. Gust is the wind speed maximum over the period. "
            "-snow_depth differs from snowfall being the istantaneous snow height at the surface "
            "-cape is the convective available potential energy"
            ,
            "parameters": {
                "type": "object",
                "properties": {
                    "location": location_object,
                    "start_date": {
                        "type": "string",
                        "description": "The start date of the forecast. Needs to be in the format YYYY-mm-dd. The maximum is 10 days from today.",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "The end date of the forecast. Needs to be in the format YYYY-mm-dd. The maximum is 10 days from today; end_date needs to be larger or equal than start_date.",
                    },
                    "daily": {
                        "type": "boolean",
                        "description": "If set to True request daily extremes/accumulations, otherwise set to False to retrieve hourly data.",
                    },
                },
                "required": ["location", "start_date", "end_date", "daily"],
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
                "Get the ensemble weather data for a specific location and date range as JSON. This data contains multiple members for the same variable and is thus useful to estimate uncertainty in the forecast. The member number is affixed to the variable name, e.g. temperature_2m_member_23. This data contains less variables with respect to the deterministic forecast. Also, ensemble models are usually characterized by lower resolution."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "location": location_object,
                    "var": {
                        "type": "string",
                        "description": "The variable to request the ensemble data from. Can be one of ['temperature_2m','precipitation','rain','snowfall']. You can only request one variable per function call.",
                    },
                    "start_date": {
                        "type": "string",
                        "description": "The start date of the forecast. Needs to be in the format YYYY-mm-dd. The maximum is 15 days from today.",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "The end date of the forecast. Needs to be in the format YYYY-mm-dd. The maximum is 15 days from today; end_date needs to be larger or equal than start_date.",
                    },
                },
                "required": ["location", "var", "start_date", "end_date"],
                "additionalProperties": False,
            },
        },
        "strict": True,
    },
    {
        "type": "function",
        "function": {
            "name": "get_marine_forecast",
            "description": (
                "Get marine forecasts concerning variables like wave height, period and direction. These date are based on marine models that only simulate ocean circulation based on atmospheric forcing."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "location": location_object,
                    "start_date": {
                        "type": "string",
                        "description": "The start date of the forecast. Needs to be in the format YYYY-mm-dd. The maximum is 10 days from today.",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "The end date of the forecast. Needs to be in the format YYYY-mm-dd. The maximum is 10 days from today; end_date needs to be larger or equal than start_date.",
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
            "name": "get_historical_daily_data",
            "description": (
                "Get the daily historical data for a location. "
                "This is the best estimate that we have according to reanalysis of the weather evolution everywhere on Earth. Still, it is based on models so it's not the same as a direct observation."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "location": location_object,
                    "var": {
                        "type": "string",
                        "description": "The variable to request the historical data from. Can be one of ['temperature_2m_max','temperature_2m_min','sunshine_duration','precipitation_sum','rain_sum','snowfall_sum']. You can only request one variable per function call.",
                    },
                    "start_date": {
                        "type": "string",
                        "description": "The start date to retrieve historical data. Needs to be in the format YYYY-mm-dd. The minimum value for this parameter is 1940-01-01, the maximum value is 6 days before today.",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "The end date to retrieve historical data. Needs to be in the format YYYY-mm-dd. The minimum value for this parameter is 1940-01-01, the maximum value is 6 days before today",
                    },
                    "agg_function": {       
                        "type": "string",
                        "description": "The aggregation function name to apply to the climatology before returning the results. Can be any of the functions accepted by the pandas agg() operation, e.g. 'min', 'max', 'mean',... If you need the original data without aggregation omit this parameter.",
                    },
                },
                "required": ["location", "var", "start_date", "end_date"],
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
                "Get the daily climatological data, that is data averaged over a 30 years period, which in this case is 1991-2020. The output of this function contains a time array without year information because this is a multi-year average. This time array is in the format %m-%d. Besides this, the formatting is the same as in 'get_historical_daily_data'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "location": location_object,
                    "var": {
                        "type": "string",
                        "description": "The variable to request the climatological data from. Can be one of ['temperature_2m_max','temperature_2m_min','sunshine_duration','precipitation_sum','rain_sum','snowfall_sum']. You can only request one variable per function call.",
                    },
                    "start_date": {
                        "type": "string",
                        "description": "The start date to retrieve climatological data. Needs to be in the format 2020-mm-dd. Note that the year is arbitrarily set to 2020 no matter the period you're comparing to.",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "The end date to retrieve climatological data. Needs to be in the format 2020-mm-dd. Note that the year is arbitrarily set to 2020 no matter the period you're comparing to.",
                    },
                    "agg_function": {       
                        "type": "string",
                        "description": "The aggregation function name to apply to the climatology before returning the results. Can be any of the functions accepted by the pandas agg() operation, e.g. 'min', 'max', 'mean',... If you need the original data without aggregation omit this parameter.",
                    },
                },
                "required": ["location", "var", "start_date", "end_date"],
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
                "Radar-based nowcasting of precipitation up to 2 hours from now for locations that are in Germany. "
                "The Response is a JSON containing array of objects with time and estimated precipitation (mm/h) every 15 minutes."
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
    {
        "type": "function",
        "function": {
            "name": "get_current_conditions",
            "description": (
                "Get current conditions in a specific location based on observations."
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
            "name": "get_daily_summary",
            "description": (
                "Get daily summary data in a specific location based on observations (not models)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "location": location_object,
                    "date": {
                        "type": "string",
                        "description": "The date to request the daily summary for, needs to be in the format YYYY-mm-dd.",
                    },
                },
                "required": ["location" ,"date"],
                "additionalProperties": False,
            },
        },
        "strict": True,
    },
]

def round_if_close(value):
    if isinstance(value, (int, float)) and value.is_integer():
        return int(value)  # Return as int if it's already an integer (like 1000.0 -> 1000)
    return value  # Otherwise, leave it unchanged

def get_current_datetime(timezone=None):
    if timezone:
        timezone = pytz.timezone(timezone)
    else:
        # default to UTC if nothing is specified
        timezone = pytz.timezone('UTC')
    return datetime.now(timezone).strftime("The current date is %Y-%m-%d (format is %%Y-%%m-%%d), time %H:%M:%S%z (format is %%H:%%M:%%S%%z)")

@cache.memoize(3600)
def get_deterministic_forecast(location, start_date, end_date, daily=False):
    payload = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "timezone": "auto",
        "models": "best_match",
        "start_date": start_date,
        "end_date": end_date,
    }
    if not daily:
        payload['hourly'] = "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,showers,snowfall,pressure_msl,cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,wind_speed_10m,wind_direction_10m,wind_gusts_10m,cape,sunshine_duration,snow_depth,temperature_850hPa,precipitation_probability"
    else:
        payload['daily'] = "temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,sunshine_duration,precipitation_sum,rain_sum,showers_sum,snowfall_sum,precipitation_hours,precipitation_probability_max,wind_speed_10m_max,wind_gusts_10m_max,wind_direction_10m_dominant"

    resp = make_request(url="https://api.open-meteo.com/v1/forecast", payload=payload)
    weather_data = resp.json()
    # Remove useless info
    for el in ['generationtime_ms', 'utc_offset_seconds', 'timezone_abbreviation']:
        weather_data.pop(el, None)
    # Correct precision
    vars_freq = "hourly" if not daily else "daily"
    for key in weather_data[vars_freq]:
        weather_data[vars_freq][key] = [round_if_close(val) for val in weather_data[vars_freq][key]]

    return weather_data

@cache.memoize(3600)
def get_ensemble_forecast(location, var, start_date, end_date):
    payload = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "hourly": var,
        "timezone": "auto",
        "models": "icon_seamless",
        "start_date": start_date,
        "end_date": end_date,
    }
    resp = make_request(
        url="https://ensemble-api.open-meteo.com/v1/ensemble", payload=payload
    )
    ensemble_data = resp.json()
    # Remove useless info
    for el in ['generationtime_ms', 'utc_offset_seconds', 'timezone_abbreviation', 'hourly_units']:
        ensemble_data.pop(el, None)
    # Correct precision
    for key in ensemble_data['hourly']:
        ensemble_data['hourly'][key] = [round_if_close(val) for val in ensemble_data['hourly'][key]]

    return ensemble_data

# @cache.memoize(31536000)
def get_climatology(location, var, start_date, end_date, agg_function=None):
    clima = compute_climatology(
        latitude=location["latitude"],
        longitude=location["longitude"],
        daily=True,
        model="era5_seamless",
        variables=var,
    )
    if 'sunshine_duration' in clima.columns:
        clima["sunshine_duration"] = (clima["sunshine_duration"] * 3600.0).astype(int)
    # Select the right dates
    time = pd.date_range(start_date, end_date, freq='1D')
    clima = clima[clima.doy.isin(time.strftime("%m%d"))]
    clima['time'] = time.strftime("%m-%d")
    weather_data = clima.attrs
    weather_data['daily'] = {}
    if agg_function is not None:
        weather_data['daily']['time'] = clima['time'].iloc[0] + " to " + clima['time'].iloc[-1]
        weather_data['daily'][var] = clima[var].agg(agg_function).round(2)
    else:
        weather_data['daily']['time'] = clima['time'].to_list()
        weather_data['daily'][var] = clima[var].to_list()
        # Correct precision
        for key in weather_data['daily']:
            weather_data['daily'][key] = [round_if_close(val) for val in weather_data['daily'][key]]

    # Remove useless info
    for el in ['generationtime_ms', 'utc_offset_seconds', 'timezone_abbreviation']:
        weather_data.pop(el, None)
    weather_data['daily_units'].pop('time', None)

    return weather_data

@cache.memoize(86400)
def get_historical_daily_data(location, var, start_date, end_date, agg_function=None):
    payload = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "daily": var,
        "timezone": "auto",
        "models": "era5_seamless",
        "start_date": start_date,
        "end_date": end_date,
    }

    resp = make_request("https://archive-api.open-meteo.com/v1/archive", payload).json()
    daily = pd.DataFrame.from_dict(resp['daily'])
    weather_data = {x: resp[x] for x in resp if x not in ["hourly", "daily"]}
    weather_data['daily'] = {}
    if agg_function is not None:
        weather_data['daily']['time'] = daily['time'].iloc[0] + " to " + daily['time'].iloc[-1]
        weather_data['daily'][var] = daily[var].agg(agg_function).round(2)
    else:
        weather_data['daily']['time'] = daily['time'].to_list()
        weather_data['daily'][var] = daily[var].to_list()
        # Correct precision
        for key in weather_data['daily']:
            weather_data['daily'][key] = [round_if_close(val) for val in weather_data['daily'][key]]

    # Remove useless info
    for el in ['generationtime_ms', 'utc_offset_seconds', 'timezone_abbreviation']:
        weather_data.pop(el, None)

    return weather_data


@cache.memoize(3600)
def get_marine_forecast(location, start_date, end_date):
    payload = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "hourly": "wave_height,wave_direction,wave_period",
        "timezone": "auto",
        "models": "best_match",
        "start_date": start_date,
        "end_date": end_date,
    }
    resp = make_request(
        url="https://marine-api.open-meteo.com/v1/marine", payload=payload
    )
    marine_data = resp.json()
    # Remove useless info
    for el in ['generationtime_ms', 'utc_offset_seconds', 'timezone_abbreviation']:
        marine_data.pop(el, None)
    # Correct precision
    for key in marine_data['hourly']:
        marine_data['hourly'][key] = [round_if_close(val) for val in marine_data['hourly'][key]]
    
    return marine_data


def get_radar_data(address):
    payload = {"address": address}
    resp = r.get(url="https://hh.guidocioni.it/nmwr/pointquery", params=payload)
    resp.raise_for_status()

    return resp.json()


@cache.memoize(60)
def get_current_conditions(location):
    payload = {
        "lat": location["latitude"],
        "lon": location["longitude"],
        "appid": OPENWEATHERMAP_KEY,
        "units": "metric"
    }
    resp = r.get(url="https://api.openweathermap.org/data/2.5/weather", params=payload)
    resp.raise_for_status()

    return resp.json()


@cache.memoize(60)
def get_daily_summary(location, date):
    payload = {
        "lat": location["latitude"],
        "lon": location["longitude"],
        "appid": OPENWEATHERMAP_KEY,
        "units": "metric",
        "date": date
    }
    resp = r.get(url="https://api.openweathermap.org/data/3.0/onecall/day_summary", params=payload)
    resp.raise_for_status()

    return resp.json()
