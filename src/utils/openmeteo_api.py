import pandas as pd
import requests as r


def get_ensemble_data(latitude=53.55,
                      longitude=9.99,
                      variables='temperature_2m,cloudcover,rain,snowfall,precipitation',
                      timezone='auto',
                      model='icon_seamless'):
    payload = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": variables,
        "timezone": timezone,
        "models": model
    }

    resp = r.get("https://ensemble-api.open-meteo.com/v1/ensemble",
                 params=payload)
    data = pd.DataFrame.from_dict(resp.json()['hourly'])
    data['time'] = pd.to_datetime(
        data['time']).dt.tz_localize(resp.json()['timezone'])

    data = data.dropna()

    return data


def get_locations(name, count=10, language='en'):
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
