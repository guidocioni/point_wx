'''
This file contains a wrapper for all functions that are exposed to the models automatically
throuh tools.
We can't use the functions directly because we may need to change something before passing the results
or settings some parameters.
'''
from utils.ai_utils import create_weather_data
from datetime import datetime
import pytz

tools = [
    {
        "type": "function",
        "function": {
            "name": "create_weather_data",
            "description": "Get the weather data for a specific location and date as JSON. Use it to get the input data for your analysis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The location used to get the weather data",
                    },
                    "date": {
                        "type": "string",
                        "description": "The date for which the weather data is requested",
                    },
                },
                "required": ["location", "date"],
                "additionalProperties": False,
            },
        },
        # "strict": True,
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
        # "strict": True,
    },
]

def get_current_datetime(timezone=None):
    if timezone:
        timezone = pytz.timezone(timezone)
    return datetime.now(timezone).strftime("Today is %d %b %Y and the time is %H:%M:%S")

