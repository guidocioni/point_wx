"""
Unicode emoji mapping for weather codes.
Provides a fast, lightweight alternative to PNG/SVG icon files.
"""

# Complete mapping of WMO weather codes to unicode emoji
WEATHER_EMOJI = {
    0: "☀️",     # Sunny / Clear
    1: "🌤",     # Mainly Sunny / Mainly Clear
    2: "⛅",     # Partly Cloudy
    3: "☁️",     # Cloudy
    45: "🌫️",    # Foggy
    48: "🌫",    # Rime Fog
    51: "🌦",    # Light Drizzle
    53: "🌦",    # Drizzle
    55: "🌧",    # Heavy Drizzle
    56: "🌧",    # Light Freezing Drizzle
    57: "🌧",    # Freezing Drizzle
    61: "🌦",    # Light Rain
    63: "🌧",    # Rain
    65: "🌧",    # Heavy Rain
    66: "🌧",    # Light Freezing Rain
    67: "🌧",    # Freezing Rain
    71: "🌨",    # Light Snow
    73: "❄️",    # Snow
    75: "🌨️",    # Heavy Snow
    77: "❄️",    # Snow Grains
    80: "🌦",    # Light Showers
    81: "🌧",    # Showers
    82: "🌧",    # Heavy Showers
    85: "🌨️",    # Light Snow Showers
    86: "🌨️",    # Snow Showers
    95: "⛈️",     # Thunderstorm
    96: "⛈️",     # Light Thunderstorms With Hail
    99: "⛈️",     # Thunderstorm With Hail
}


def get_weather_emoji(weather_code):
    """
    Get unicode emoji for a weather code.

    Parameters
    ----------
    weather_code : int or float
        WMO weather code

    Returns
    -------
    str
        Unicode emoji character, or empty string if code is invalid/missing
    """
    if pd.isna(weather_code):
        return ""

    try:
        code = int(weather_code)
        return WEATHER_EMOJI.get(code, "")
    except (ValueError, TypeError):
        return ""


def get_weather_emoji_series(weather_codes):
    """
    Convert a pandas Series of weather codes to emoji.

    Parameters
    ----------
    weather_codes : pd.Series
        Series of weather codes

    Returns
    -------
    pd.Series
        Series of emoji strings
    """
    import pandas as pd
    return weather_codes.apply(get_weather_emoji)


# Import pandas for isna check in get_weather_emoji
import pandas as pd
