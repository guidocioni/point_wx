import pandas as pd
import requests as r
import os
import re
from .settings import cache, ENSEMBLE_VARS, ENSEMBLE_MODELS, DETERMINISTIC_VARS, DETERMINISTIC_MODELS, ROOT_DIR
from .custom_logger import logging, time_this_func


@time_this_func
def make_request(url, payload):
    logging.info(f"Sending request with payload {payload} to url {url}")

    # Attempt to read a file with the apikey
    api_key = None
    if os.path.exists(f"{ROOT_DIR}/.apikey"):
        try:
            file1 = open(f"{ROOT_DIR}/.apikey", 'r')
            for line in file1.readlines():
                api_key = line.strip()
        except Exception as e:
            logging.warning(".apikey file exists but there was an error reading it")
            logging.warning(f"ERROR: {repr(e)}")
            api_key = None

    if api_key:
        logging.info("Using commercial API key")
        # In this case we have to prepend the 'customer-' string to the url
        # and add &apikey=... at the end
        url = url.replace("https://", "https://customer-")
        payload['apikey'] = api_key

    resp = r.get(url=url, params=payload)
    resp.raise_for_status()

    return resp


@cache.memoize(86400)
def get_locations(name, count=10, language='en'):
    """
    Get a list of locations based on a name
    """
    # First cleanup the input string
    # Remove any number (we don't use the postal code lookup)
    name = re.sub(r'\d', '', name)
    # Replace more than 2 spaces with just one space
    name = re.sub(r'\s{2,}', ' ', name)
    # Remove trailing and leading whitespaces
    name = re.sub(r'^[\s]+|[\s]+$', '', name)
    # Now submit the payload
    payload = {
        "name": name,
        "count": count,
        "language": language,
        "format": 'json'
    }

    resp = make_request(
        "https://geocoding-api.open-meteo.com/v1/search",
        payload)

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

    resp = make_request(
        "https://api.open-meteo.com/v1/forecast",
        payload)

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
    for col in data.columns[data.columns.str.contains('sunshine_duration')]:
        data[col] = data[col] / 3600.  # s to hrs

    # Add metadata (experimental)
    data.attrs = {x: resp.json()[x] for x in resp.json() if x not in ["hourly","daily"]}

    return data


@cache.memoize(1800)
def get_vertical_data(
        latitude=53.55,
        longitude=9.99,
        timezone='auto',
        forecast_days=7,
        model='best_match',
        from_now=True,
        past_days=None,
        start_date=None,
        end_date=None,
        variables=['temperature', 'cloud_cover',
                   'windspeed', 'winddirection'],
        levels=[100, 150, 200,
                250, 300, 400,
                500, 600, 700,
                750, 800, 850,
                900, 925,
                950, 975, 1000]):
    """Wrapper to download vertical data"""
    # Construct the string
    vars = [f'{var}_{lev}hPa' for var in variables for lev in levels]
    df = get_forecast_data(latitude=latitude,
                           longitude=longitude,
                           timezone=timezone,
                           forecast_days=forecast_days,
                           model=model,
                           from_now=from_now,
                           past_days=past_days,
                           start_date=start_date,
                           end_date=end_date,
                           variables=vars)
    # Create array representation useful to plot
    time_axis = df['time'].values
    arrs = []
    for v in variables:
        sub = df.loc[:, df.columns.str.contains(f'{v}|time')].set_index('time')
        sub.columns = sub.columns.str.extract(
            r'(\d+)(?:hPa)').values.astype(int).reshape(-1)
        sub = sub.sort_index(axis=1)
        arrs.append(sub.values)

    vertical_levels = sub.columns.values
    # The resulting array has shape (x, y) = (time_axis, vertical_levels)
    # and we return a list containing all the variables requested

    return df, variables, time_axis, vertical_levels, arrs


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

    resp = make_request(
        "https://api.open-meteo.com/v1/forecast",
        payload)

    data = pd.DataFrame.from_dict(resp.json()['daily'])
    data['time'] = pd.to_datetime(
        data['time']).dt.tz_localize(resp.json()['timezone'], ambiguous='NaT', nonexistent='NaT')

    # Add metadata (experimental)
    data.attrs = {x: resp.json()[x] for x in resp.json() if x not in ["hourly","daily"]}

    return data


@cache.memoize(3600)
def get_ensemble_data(latitude=53.55,
                      longitude=9.99,
                      variables=",".join(ENSEMBLE_VARS),
                      timezone='auto',
                      model=ENSEMBLE_MODELS[0]['value'],
                      from_now=True,
                      decimate=False):
    """
    Get the ensemble data
    """
    # Adjust forecast_days depending on the model
    if model in ['icon_seamless','icon_global']:
        forecast_days = 8
    elif model == 'icon_eu':
        forecast_days = 6
    elif model == 'icon_d2':
        forecast_days = 3
    elif model in ['gfs_seamless', 'gfs05']:
        forecast_days = 15
    elif model == 'gfs025':
        forecast_days = 11
    elif model == 'ecmwf_ifs04':
        forecast_days = 11
    elif model == 'gem_global':
        forecast_days = 15
    else:
        forecast_days = 8

    payload = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": variables,
        "timezone": timezone,
        "models": model,
        "forecast_days": forecast_days
    }

    resp = make_request(
        "https://ensemble-api.open-meteo.com/v1/ensemble",
        payload)

    data = pd.DataFrame.from_dict(resp.json()['hourly'])
    data['time'] = pd.to_datetime(
        data['time']).dt.tz_localize(resp.json()['timezone'], ambiguous='NaT', nonexistent='NaT')

    data = data.dropna(subset=data.columns[data.columns != 'time'],
                       how='all')

    # Optionally subset data to start only from previous hour
    if from_now:
        data = data[data.time >= pd.to_datetime(
            'now', utc=True).tz_convert(resp.json()['timezone']).floor('H')]

    # Optionally decimate data
    if decimate:
        if model in ['gfs_seamless', 'gfs05', 'gfs025', 'ecmwf_ifs04', 'gem_global']:
            # Decimate every 3 hours considering as starting point the first time value
            # which means that, in case the from_now option is activated, it will start
            # resampling every 3 hours from that starting point, otherwise it will resample
            # at the original point 0, 3, 6, 9, 12, 18, as the data always starts at 00
            # Of course, it means that with from_now = True, the resulting data will almost
            # always be interpolated, but we assume this to be ok.
            data = data.resample('3H', on='time', origin=data.iloc[0]['time']).first().reset_index()
        elif model in ['icon_seamless', 'icon_global', 'icon_eu', 'icon_d2']:
            # We leave the first 48 hrs untouched, and then decimate every 3 hours
            # Note that we count from 48 hrs from the first time value, which means
            # it may not correspond to the run start time
            if model != 'icon_d2':
                t48_start_date = data.iloc[0]['time'] + pd.to_timedelta('48H')
                data = pd.concat(
                    [
                        data.loc[data.time <= t48_start_date, :],
                        data.loc[data.time > t48_start_date + pd.to_timedelta('3H'), :].resample(
                            '3H',
                            on='time',
                            origin=t48_start_date + pd.to_timedelta('3H')).first().reset_index()
                    ]
                )

    # Units conversion
    for col in data.columns[data.columns.str.contains('snow_depth')]:
        data[col] = data[col] * 100.  # m to cm
    for col in data.columns[data.columns.str.contains('sunshine_duration')]:
        data[col] = data[col] / 3600.  # s to hrs

    # Add metadata (experimental)
    data.attrs = {x: resp.json()[x] for x in resp.json() if x not in ["hourly","daily"]}

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

    resp = make_request(
        "https://archive-api.open-meteo.com/v1/archive",
        payload)

    data = pd.DataFrame.from_dict(resp.json()['hourly'])
    data['time'] = pd.to_datetime(
        data['time'], format='%Y-%m-%dT%H:%M')

    data = data.dropna()

    # Add metadata (experimental)
    data.attrs = {x: resp.json()[x] for x in resp.json() if x not in ["hourly","daily"]}

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

    resp = make_request(
        "https://archive-api.open-meteo.com/v1/archive",
        payload)

    data = pd.DataFrame.from_dict(resp.json()['daily'])
    data['time'] = pd.to_datetime(data['time'])

    data = data.dropna()

    # Add metadata (experimental)
    data.attrs = {x: resp.json()[x] for x in resp.json() if x not in ["hourly","daily"]}

    return data


@cache.memoize(0)
@time_this_func
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
    # data = data.resample('3H', on='time').first().reset_index()
    # Add doy not as integer but as string to allow for leap years
    data['doy'] = data.time.dt.strftime("%m%d")
    # Compute mean over day of the year AND hour
    mean = data.groupby([data.doy, data.time.dt.hour]).mean(
        numeric_only=True).round(1).rename_axis(['doy', 'hour']).reset_index()

    return mean


@cache.memoize(0)
@time_this_func
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
@time_this_func
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
@time_this_func
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

    if year == pd.to_datetime('now', utc=True).year:
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
@time_this_func
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
    if year == pd.to_datetime('now', utc=True).year:
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
@time_this_func
def compute_daily_ensemble_meteogram(latitude=53.55,
                                     longitude=9.99,
                                     model='gfs_seamless'):
    data = get_ensemble_data(
        latitude=latitude,
        longitude=longitude,
        model=model,
        variables="weather_code,temperature_2m,precipitation,sunshine_duration",
        from_now=False)

    # This computes a daily aggregation for all ensemble members
    daily_tmin = data.loc[:,data.columns.str.contains('temperature_2m|time')].resample('1D', on='time').min()
    daily_tmax = data.loc[:,data.columns.str.contains('temperature_2m|time')].resample('1D', on='time').max()
    daily_wcode = data.loc[:,data.columns.str.contains('weather_code|time')].resample('1D', on='time').median()
    daily_prec = data.loc[:,data.columns.str.contains('precipitation|time')].resample('1D', on='time').sum()
    daily_sunshine = data.loc[:,data.columns.str.contains('sunshine_duration|time')].resample('1D', on='time').sum()

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
        .merge(((daily_prec[daily_prec > 0.1].count(axis=1) / daily_prec.shape[1]) * 100.).to_frame(name='prec_prob'), left_index=True, right_index=True)\
        .merge(daily_sunshine.quantile(0.25,axis=1).to_frame(name='sunshine_min'), left_index=True, right_index=True)\
        .merge(daily_sunshine.quantile(0.75,axis=1).to_frame(name='sunshine_max'), left_index=True, right_index=True)\
        .merge(daily_sunshine.mean(axis=1).to_frame(name='sunshine_mean'), left_index=True, right_index=True)

    daily.attrs = data.attrs

    return daily
