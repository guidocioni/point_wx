import pandas as pd
import requests as r
from .settings import cache, ENSEMBLE_VARS, ENSEMBLE_MODELS, DETERMINISTIC_VARS, DETERMINISTIC_MODELS


@cache.memoize(86400)
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
    resp.raise_for_status()
    if 'results' in resp.json():
        data = pd.DataFrame.from_dict(resp.json()['results'])
    else:
        data = pd.DataFrame()

    return data


@cache.memoize(1800)
def get_forecast_data(latitude=53.55,
                      longitude=9.99,
                      variables=",".join(DETERMINISTIC_VARS),
                      timezone='auto',
                      model=DETERMINISTIC_MODELS[0]['value'],
                      forecast_days=7,
                      from_now=True,
                      past_days=None,
                      start_date=None,
                      end_date=None):
    payload = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": variables,
        "timezone": timezone,
        "models": model,
    }

    if past_days:
        payload['past_days'] = past_days
    if forecast_days:
        payload['forecast_days'] = forecast_days
    if start_date:
        payload['start_date'] = start_date
    if end_date:
        payload['end_date'] = end_date

    resp = r.get("https://api.open-meteo.com/v1/forecast",
                 params=payload)
    resp.raise_for_status()
    data = pd.DataFrame.from_dict(resp.json()['hourly'])
    data['time'] = pd.to_datetime(
        data['time']).dt.tz_localize(resp.json()['timezone'], ambiguous='NaT')

    data = data.dropna(subset=data.columns[data.columns != 'time'],
                       how='all')
    # Optionally subset data to start only from previous hour
    if from_now:
        data = data[data.time >= pd.to_datetime(
            'now', utc=True).tz_convert(resp.json()['timezone']).floor('H')]

    # Units conversion
    for col in data.columns[data.columns.str.contains('snow_depth')]:
        data[col] = data[col] * 100.  # m to cm

    return data


@cache.memoize(1800)
def get_forecast_daily_data(latitude=53.55,
                            longitude=9.99,
                            variables="precipitation_sum",
                            timezone='auto',
                            model=DETERMINISTIC_MODELS[0]['value'],
                            forecast_days=7,
                            past_days=None,
                            start_date=None,
                            end_date=None):
    payload = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": variables,
        "timezone": timezone,
        "models": model,
    }

    if past_days:
        payload['past_days'] = past_days
    if forecast_days:
        payload['forecast_days'] = forecast_days
    if start_date:
        payload['start_date'] = start_date
    if end_date:
        payload['end_date'] = end_date

    resp = r.get("https://api.open-meteo.com/v1/forecast",
                 params=payload)
    resp.raise_for_status()
    data = pd.DataFrame.from_dict(resp.json()['daily'])
    data['time'] = pd.to_datetime(
        data['time']).dt.tz_localize(resp.json()['timezone'], ambiguous='NaT', nonexistent='NaT')

    return data


@cache.memoize(3600)
def get_ensemble_data(latitude=53.55,
                      longitude=9.99,
                      variables=",".join(ENSEMBLE_VARS),
                      timezone='auto',
                      model=ENSEMBLE_MODELS[0]['value'],
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
    resp.raise_for_status()
    data = pd.DataFrame.from_dict(resp.json()['hourly'])
    data['time'] = pd.to_datetime(
        data['time']).dt.tz_localize(resp.json()['timezone'], ambiguous='NaT', nonexistent='NaT')

    data = data.dropna(subset=data.columns[data.columns != 'time'],
                       how='all')
    # Optionally subset data to start only from previous hour
    if from_now:
        data = data[data.time >= pd.to_datetime(
            'now', utc=True).tz_convert(resp.json()['timezone']).floor('H')]

    # Units conversion
    for col in data.columns[data.columns.str.contains('snow_depth')]:
        data[col] = data[col] * 100.  # m to cm

    return data

# As historical data is in the past, it never changes
# so we can safely set these functions to infinite timeout
# They will only be re-computed if the parameters change


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
    resp.raise_for_status()
    data = pd.DataFrame.from_dict(resp.json()['hourly'])
    data['time'] = pd.to_datetime(
        data['time'], format='%Y-%m-%dT%H:%M')

    data = data.dropna()

    return data


@cache.memoize(86400)
def get_historical_daily_data(latitude=53.55,
                              longitude=9.99,
                              variables='precipitation_sum',
                              timezone='GMT',
                              model='best_match',
                              start_date='1991-01-01',
                              end_date='2020-12-31'):
    """
    Get historical data for a point
    """
    payload = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": variables,
        "timezone": timezone,
        "models": model,
        "start_date": start_date,
        "end_date": end_date
    }

    resp = r.get("https://archive-api.open-meteo.com/v1/archive",
                 params=payload)
    resp.raise_for_status()
    data = pd.DataFrame.from_dict(resp.json()['daily'])
    data['time'] = pd.to_datetime(data['time'])

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


@cache.memoize(0)
def compute_daily_stats(latitude=53.55, longitude=9.99, model='era5',
                        start_date='1991-01-01', end_date='2020-12-31'):
    """Starting from hourly data compute daily aggregations which are
    useful for other functions that compute climatologies"""

    df = get_historical_data(
        variables='temperature_2m,precipitation,snowfall,cloudcover,windspeed_10m',
        latitude=latitude,
        longitude=longitude,
        timezone='GMT',  # Use UTC to avoid issues with daily computations
        model=model,
        start_date=start_date,
        end_date=end_date)

    daily = df.resample('1D', on='time').agg(t2m_mean=('temperature_2m', 'mean'),
                                             t2m_min=('temperature_2m', 'min'),
                                             t2m_max=('temperature_2m', 'max'),
                                             wind_speed_max=(
                                                 'windspeed_10m', 'max'),  # in km/h
                                             daily_rain=(
                                                 'precipitation', 'sum'),  # in mm
                                             daily_snow=(
                                                 'snowfall', 'sum'),  # in cm
                                             cloudcover_mean=(
                                                 'cloudcover', 'mean')  # in %
                                             )

    return daily


@cache.memoize(0)
def compute_monthly_clima(latitude=53.55, longitude=9.99, model='era5',
                          start_date='1991-01-01', end_date='2020-12-31'):
    """Takes a 30 years hourly dataframe as input and compute
    some monthly statistics by aggregating many times"""

    daily = compute_daily_stats(latitude=latitude,
                                longitude=longitude,
                                model=model,
                                start_date=start_date,
                                end_date=end_date)

    daily['overcast'] = daily['cloudcover_mean'] >= 80
    daily['partly_cloudy'] = (daily['cloudcover_mean'] < 80) & (
        daily['cloudcover_mean'] > 20)
    daily['sunny'] = daily['cloudcover_mean'] <= 20
    daily['t_max_gt_30'] = daily['t2m_max'] > 30
    daily['t_max_gt_25'] = (daily['t2m_max'] > 25) & (daily['t2m_max'] <= 30)
    daily['t_max_gt_20'] = (daily['t2m_max'] > 20) & (daily['t2m_max'] <= 25)
    daily['t_max_gt_15'] = (daily['t2m_max'] > 15) & (daily['t2m_max'] <= 20)
    daily['t_max_gt_10'] = (daily['t2m_max'] > 10) & (daily['t2m_max'] <= 15)
    daily['t_max_gt_5'] = (daily['t2m_max'] > 5) & (daily['t2m_max'] <= 10)
    daily['t_max_gt_0'] = (daily['t2m_max'] >= 0) & (daily['t2m_max'] <= 5)
    daily['t_max_lt_0'] = (daily['t2m_max'] >= -5) & (daily['t2m_max'] < 0)
    daily['t_max_lt_m5'] = daily['t2m_max'] < -5
    daily['frost'] = daily['t2m_min'] <= 0
    daily['wet'] = daily['daily_rain'] >= 1.0  # mm
    daily['dry'] = daily['daily_rain'] < 1.0  # mm
    daily['snow'] = daily['daily_snow'] >= 1.0  # cm
    daily['p_50_100'] = (daily['daily_rain'] <= 100) & (
        daily['daily_rain'] > 50)
    daily['p_20_50'] = (daily['daily_rain'] <= 50) & (daily['daily_rain'] > 20)
    daily['p_10_20'] = (daily['daily_rain'] <= 20) & (daily['daily_rain'] > 10)
    daily['p_5_10'] = (daily['daily_rain'] <= 10) & (daily['daily_rain'] > 5)
    daily['p_2_5'] = (daily['daily_rain'] <= 5) & (daily['daily_rain'] > 2)
    daily['p_lt_2'] = (daily['daily_rain'] <= 2) & (daily['daily_rain'] > 1)
    daily['w_gt_61'] = (daily['wind_speed_max'] >= 61)
    daily['w_gt_50'] = (daily['wind_speed_max'] >= 50) & (
        daily['wind_speed_max'] < 61)
    daily['w_gt_38'] = (daily['wind_speed_max'] >= 38) & (
        daily['wind_speed_max'] < 50)
    daily['w_gt_28'] = (daily['wind_speed_max'] >= 28) & (
        daily['wind_speed_max'] < 38)
    daily['w_gt_19'] = (daily['wind_speed_max'] >= 19) & (
        daily['wind_speed_max'] < 28)
    daily['w_gt_12'] = (daily['wind_speed_max'] >= 12) & (
        daily['wind_speed_max'] < 19)
    daily['w_gt_5'] = (daily['wind_speed_max'] >= 5) & (
        daily['wind_speed_max'] < 12)
    daily['w_gt_1'] = (daily['wind_speed_max'] >= 1) & (
        daily['wind_speed_max'] < 5)
    daily['w_calm'] = daily['wind_speed_max'] <= 0.1
    #
    bool_cols = daily.dtypes[daily.dtypes == bool].index
    # Compute monthly stats
    monthly = daily[bool_cols].resample('1M').sum().add_suffix('_days')
    monthly['monthly_rain'] = daily['daily_rain'].resample('1M').sum()
    monthly['t2m_max_mean'] = daily['t2m_max'].resample('1M').mean()
    monthly['t2m_min_mean'] = daily['t2m_min'].resample('1M').mean()
    monthly['t2m_min_min'] = daily['t2m_min'].resample('1M').min()
    monthly['t2m_max_max'] = daily['t2m_max'].resample('1M').max()
    stats = monthly.groupby(monthly.index.month).mean().round(1)

    return stats


@cache.memoize(86400)
def compute_yearly_accumulation(latitude=53.55,
                                longitude=9.99,
                                model='era5',
                                var='precipitation_sum',
                                year=pd.to_datetime('now', utc=True).year,
                                q1=0.05,
                                q2=0.5,
                                q3=0.95):
    """Compute cumulative sum of some variable over the year"""

    daily = get_historical_daily_data(
        latitude=latitude,
        longitude=longitude,
        model=model,
        start_date='1981-01-01',
        end_date=(pd.to_datetime('now', utc=True) -
                  pd.to_timedelta('1 day')).strftime("%Y-%m-%d"),
        variables=var)

    # Add missing dates and forecasts
    additional = get_forecast_daily_data(
        latitude=latitude,
        longitude=longitude,
        variables=var,
        model='ecmwf_ifs04',
        forecast_days=14,
        past_days=7)
    additional['time'] = additional['time'].dt.tz_localize(
        None, ambiguous='NaT', nonexistent='NaT')
    additional = additional[additional.time > daily.time.max()]

    daily = pd.concat([daily, additional])

    # Remove leap years
    daily = daily[~((daily.time.dt.month == 2) & (daily.time.dt.day == 29))]
    # Compute cumulative sum
    daily[f'{var}_yearly_acc'] = daily.groupby(daily.time.dt.year)[
        var].transform(lambda x: x.cumsum())

    quantiles = daily.groupby([daily.time.dt.day, daily.time.dt.month])[
        f'{var}_yearly_acc'].quantile(q=q1).to_frame().rename(columns={f'{var}_yearly_acc': 'q1'})
    quantiles['q2'] = daily.groupby([daily.time.dt.day, daily.time.dt.month])[
        f'{var}_yearly_acc'].quantile(q=q2)
    quantiles['q3'] = daily.groupby([daily.time.dt.day, daily.time.dt.month])[
        f'{var}_yearly_acc'].quantile(q=q3)

    quantiles.index.set_names(["day", "month"], inplace=True)
    quantiles.reset_index(inplace=True)
    quantiles['dummy_date'] = pd.to_datetime(
        f'{year}-' + quantiles.month.astype(str) + "-" + quantiles.day.astype(str))
    quantiles.sort_values(by='dummy_date', inplace=True)

    daily = daily[daily.time.dt.year == year].merge(
        quantiles, left_on='time', right_on='dummy_date', how='right')

    return daily


@cache.memoize(86400)
def compute_yearly_comparison(latitude=53.55,
                              longitude=9.99,
                              var='temperature_2m_mean',
                              model='era5',
                              year=pd.to_datetime('now', utc=True).year):
    """ Based on daily data compute first a daily climatology and then merge with the observed values
    over a certain year"""

    daily = get_historical_daily_data(
        latitude=latitude,
        longitude=longitude,
        model=model,
        start_date='1981-01-01',
        end_date=(pd.to_datetime('now', utc=True) -
                  pd.to_timedelta('1 day')).strftime("%Y-%m-%d"),
        variables=var)

    # Add missing dates and forecasts
    additional = get_forecast_data(
        latitude=latitude,
        longitude=longitude,
        variables=var,
        model='ecmwf_ifs04',
        from_now=False,
        forecast_days=14,
        past_days=7).resample('1D', on='time').mean().reset_index().rename(columns={var: f'{var}_mean'})
    additional['time'] = additional['time'].dt.tz_localize(
        None, ambiguous='NaT', nonexistent='NaT')
    additional = additional[additional.time > daily.time.max()]

    daily = pd.concat([daily, additional])

    # Remove leap years
    daily = daily[~((daily.time.dt.month == 2) & (daily.time.dt.day == 29))]

    daily['doy'] = daily.time.dt.strftime("%m%d")
    clima = daily.loc[(daily.time >= '1991-01-01') & (daily.time <= '2020-12-31')
                      ].groupby('doy').mean(numeric_only=True).add_suffix("_clima")
    clima['q05'] = daily.loc[(daily.time >= '1991-01-01') & (daily.time <= '2020-12-31')
                             ].groupby('doy').quantile(q=0.05, numeric_only=True).add_suffix("_q05").values
    clima['q95'] = daily.loc[(daily.time >= '1991-01-01') & (daily.time <= '2020-12-31')
                             ].groupby('doy').quantile(q=0.95, numeric_only=True).add_suffix("_q95").values

    clima['dummy_date'] = pd.to_datetime(
        str(year) + clima.index, format='%Y%m%d')
    daily = daily.merge(clima, right_on='dummy_date',
                        left_on='time', how='right')

    return daily


@cache.memoize(3600)
def compute_daily_ensemble_meteogram(latitude=53.55,
                                     longitude=9.99,
                                     model='gfs_seamless'):

    data = get_ensemble_data(
        latitude=latitude,
        longitude=longitude,
        model=model,
        variables="weather_code,temperature_2m,precipitation",
        from_now=False)

    daily_tmin = data.loc[:,data.columns.str.contains('temperature_2m|time')].resample('1D', on='time').min()
    daily_tmax = data.loc[:,data.columns.str.contains('temperature_2m|time')].resample('1D', on='time').max()
    daily_wcode = data.loc[:,data.columns.str.contains('weather_code|time')].resample('1D', on='time').median()
    daily_prec = data.loc[:,data.columns.str.contains('precipitation|time')].resample('1D', on='time').sum()

    daily = daily_tmin.mean(axis=1).to_frame(name='t_min_mean')\
        .merge(daily_tmax.mean(axis=1).to_frame(name='t_max_mean'), left_index=True, right_index=True)\
        .merge(daily_tmin.min(axis=1).to_frame(name='t_min_min'), left_index=True, right_index=True)\
        .merge(daily_tmin.max(axis=1).to_frame(name='t_min_max'), left_index=True, right_index=True)\
        .merge(daily_tmax.max(axis=1).to_frame(name='t_max_max'), left_index=True, right_index=True)\
        .merge(daily_tmax.min(axis=1).to_frame(name='t_max_min'), left_index=True, right_index=True)\
        .merge(daily_wcode.mode(axis=1)[0].to_frame(name='weather_code').astype(int), left_index=True, right_index=True)\
        .merge(daily_prec.mean(axis=1).to_frame(name='daily_prec_mean'), left_index=True, right_index=True)\
        .merge(daily_prec.quantile(0.25,axis=1).to_frame(name='daily_prec_min'), left_index=True, right_index=True)\
        .merge(daily_prec.quantile(0.75,axis=1).to_frame(name='daily_prec_max'), left_index=True, right_index=True)\
        .merge(((daily_prec[daily_prec > 0.1].count(axis=1) / daily_prec.shape[1]) * 100.).to_frame(name='prec_prob'), left_index=True, right_index=True)

    return daily
