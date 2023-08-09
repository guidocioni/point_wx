import pandas as pd
import requests as r
from .settings import cache, ENSEMBLE_VARS


@cache.memoize(3600)
def get_locations(name, count=10, language='en'):
    """
    Get a list of locations based on a name
    """
    payload = {
        "name": name,
        "count": count,
        "language": language,
        "format": 'json'
    }

    resp = r.get("https://geocoding-api.open-meteo.com/v1/search",
                 params=payload)

    data = pd.DataFrame.from_dict(resp.json()['results'])

    return data


@cache.memoize(3600)
def get_ensemble_data(latitude=53.55,
                      longitude=9.99,
                      variables=",".join(ENSEMBLE_VARS),
                      timezone='auto',
                      model='icon_seamless',
                      from_now=True):
    """
    Get the ensemble data
    """
    if model == 'icon_seamless':
        forecast_days = 7
    else:
        forecast_days = 14
    payload = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": variables,
        "timezone": timezone,
        "models": model,
        "forecast_days": forecast_days
    }

    resp = r.get("https://ensemble-api.open-meteo.com/v1/ensemble",
                 params=payload)
    data = pd.DataFrame.from_dict(resp.json()['hourly'])
    data['time'] = pd.to_datetime(
        data['time']).dt.tz_localize(resp.json()['timezone'])

    data = data.dropna()
    # Optionally subset data to start only from previous hour
    if from_now:
        data = data[data.time >= pd.to_datetime(
            'now', utc=True).tz_convert(resp.json()['timezone']).floor('H')]

    return data

# As historical data is in the past, it never changes
# so we can safely set these functions to infinite timeout
# They will only be re-computed if the parameter change


@cache.memoize(0)
def get_historical_data(latitude=53.55,
                        longitude=9.99,
                        variables='temperature_2m',
                        timezone='auto',
                        model='best_match',
                        start_date='1991-01-01',
                        end_date='2020-12-31'):
    """
    Get historical data for a point
    """
    payload = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": variables,
        "timezone": timezone,
        "models": model,
        "start_date": start_date,
        "end_date": end_date
    }

    resp = r.get("https://archive-api.open-meteo.com/v1/archive",
                 params=payload)
    data = pd.DataFrame.from_dict(resp.json()['hourly'])
    data['time'] = pd.to_datetime(
        data['time'], format='%Y-%m-%dT%H:%M')

    data = data.dropna()

    return data


@cache.memoize(0)
def compute_climatology(latitude=53.55,
                        longitude=9.99,
                        variables='temperature_2m',
                        timezone='auto',
                        model='best_match',
                        start_date='1991-01-01',
                        end_date='2020-12-31'):
    """
    Compute climatology.
    This is a very expensive operation (5-6 seconds for the full 30 years)
    so it should be cached!
    """
    data = get_historical_data(latitude, longitude, variables,
                               timezone, model, start_date, end_date)

    # Only take 3-hourly data
    data = data.resample('3H', on='time').first().reset_index()
    # Add doy not as integer but as string to allow for leap years
    data['doy'] = data.time.dt.strftime("%m%d")
    # Compute mean over day of the year AND hour
    mean = data.groupby([data.doy, data.time.dt.hour]).mean(
        numeric_only=True).round(1).rename_axis(['doy', 'hour']).reset_index()

    return mean
