import pandas as pd
import requests as r
import numpy as np
import re
from functools import reduce
from .settings import cache, OPENMETEO_KEY, ENSEMBLE_VARS
from .custom_logger import logging, time_this_func

def make_request(url, payload):
    if OPENMETEO_KEY:
        # In this case we have to prepend the 'customer-' string to the url
        # and add &apikey=... at the end
        url = url.replace("https://", "https://customer-")
        payload['apikey'] = OPENMETEO_KEY

    logging.debug(f"{'Commercial' if OPENMETEO_KEY else 'Free'} API | Sending request, payload={payload}, url={url}")
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
        payload).json()

    if 'results' in resp:
        data = pd.DataFrame.from_dict(resp['results'])
        data.loc[data['elevation'] == 9999, 'elevation'] = np.nan
    else:
        data = pd.DataFrame()


    return data


@cache.memoize(86400)
def get_elevation(latitude=53.55, longitude=9.99):
    """
    Get the elevation of a certain point using the API
    """
    # Now submit the payload
    payload = {
        "latitude": latitude,
        "longitude": longitude,
    }

    resp = make_request(
        "https://api.open-meteo.com/v1/elevation",
        payload).json()

    if 'elevation' in resp:
        return resp['elevation'][0]
    else:
        return None


@cache.memoize(1800)
def get_forecast_data(latitude=53.55,
                      longitude=9.99,
                      variables="temperature_2m",
                      timezone='auto',
                      model="best_match",
                      forecast_days=7,
                      from_now=True,
                      past_days=None,
                      start_date=None,
                      end_date=None,
                      minutes_15=False):
    payload = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly" if not minutes_15 else "minutely_15": variables,
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
        payload).json()

    data = pd.DataFrame.from_dict(resp["hourly" if not minutes_15 else "minutely_15"])
    data['time'] = pd.to_datetime(
        data['time']).dt.tz_localize(resp['timezone'], ambiguous='NaT', nonexistent='NaT')

    data = data.dropna(subset=data.columns[data.columns != 'time'],
                       how='all')
    # Optionally subset data to start only from previous hour
    if from_now:
        data = data[
            data.time
            >= (pd.to_datetime("now", utc=True) - pd.to_timedelta("1hour"))
            .tz_convert(resp["timezone"])
            .floor("h")
        ]

    # Units conversion
    for col in data.columns[data.columns.str.contains('snow_depth')]:
        data[col] = data[col] * 100.  # m to cm
    for col in data.columns[data.columns.str.contains('sunshine_duration')]:
        data[col] = data[col] / 3600.  # s to hrs


    # Compute accumulated variables
    # Comment if not needed
    # Note that we have to change the name of the resulting accumulated variables
    # so as not to conflict with the functions that always request data using columns.str.contains()
    if data.columns.str.contains("precipitation").any():
        prec_acc = data.loc[:, data.columns.str.contains("precipitation")].cumsum()
        prec_acc.columns = prec_acc.columns.str.replace(
            "precipitation", "accumulated_precip"
        )
        data = data.merge(prec_acc, left_index=True, right_index=True)
    if data.columns.str.contains("rain").any():
        rain_acc = data.loc[:, data.columns.str.contains("rain")].cumsum()
        rain_acc.columns = rain_acc.columns.str.replace("rain", "accumulated_liquid")
        data = data.merge(rain_acc, left_index=True, right_index=True)
    if data.columns.str.contains("snowfall").any():
        snowfall_acc = data.loc[:, data.columns.str.contains("snowfall")].cumsum()
        snowfall_acc.columns = snowfall_acc.columns.str.replace(
            "snowfall", "accumulated_snow"
        )
        data = data.merge(snowfall_acc, left_index=True, right_index=True)


    # Add metadata (experimental)
    data.attrs = {x: resp[x] for x in resp if x not in [
        "hourly", "daily"]}

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
                   'windspeed', 'winddirection',
                   'geopotential_height'],
        levels=[200, 250, 300, 400,
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
    # Drop columns that contain all missing values
    df = df.dropna(axis=1, how='all')
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
                            model="best_match",
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
        payload).json()

    data = pd.DataFrame.from_dict(resp['daily'])
    data['time'] = pd.to_datetime(
        data['time']).dt.tz_localize(resp['timezone'], ambiguous='NaT', nonexistent='NaT')
    
    # Units conversion
    for col in data.columns[data.columns.str.contains('snowfall_sum')]:
        data[col] = data[col] * 100.  # m to cm
    for col in data.columns[data.columns.str.contains('sunshine_duration')]:
        data[col] = data[col] / 3600.  # s to hrs

    # Add metadata (experimental)
    data.attrs = {x: resp[x] for x in resp if x not in [
        "hourly", "daily"]}

    return data


@cache.memoize(3600)
def get_ensemble_data(
    latitude=53.55,
    longitude=9.99,
    variables="temperature_2m",
    timezone="auto",
    model="icon_seamless",
    from_now=False,
    decimate=False,
):
    """
    Get the ensemble data
    """
    # Adjust forecast_days depending on the model
    if model in ["icon_seamless", "icon_global"]:
        forecast_days = 8
    elif model == "icon_eu":
        forecast_days = 6
    elif model == "icon_d2":
        forecast_days = 3
    elif model in ["gfs_seamless", "gfs05"]:
        forecast_days = 16
    elif model == "gfs025":
        forecast_days = 11
    elif model in ["ecmwf_ifs04", "ecmwf_ifs025"]:
        forecast_days = 11
    elif model == "gem_global":
        forecast_days = 17
    elif model == "bom_access_global_ensemble":
        forecast_days = 11
    else:
        forecast_days = 8
    # For the accumulated variables
    if "accumulated_precip" in variables:
        variables = variables.replace("accumulated_precip", "precipitation")
    if "accumulated_liquid" in variables:
        variables = variables.replace("accumulated_liquid", "rain")
    if "accumulated_snow" in variables:
        variables = variables.replace("accumulated_snow", "snowfall")

    payload = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": variables,
        "timezone": timezone,
        "models": model,
        "forecast_days": forecast_days,
    }

    resp = make_request("https://ensemble-api.open-meteo.com/v1/ensemble", payload).json()

    data = pd.DataFrame.from_dict(resp["hourly"])
    data["time"] = pd.to_datetime(data["time"]).dt.tz_localize(
        resp["timezone"], ambiguous="NaT", nonexistent="NaT"
    )

    data = data.dropna(subset=data.columns[data.columns != "time"], how="all")

    # Optionally subset data to start only from previous hour
    if from_now:
        data = data[
            data.time
            >= (pd.to_datetime("now", utc=True) - pd.to_timedelta('1hour'))
            .tz_convert(resp["timezone"])
            .floor("h")
        ]

    # Optionally decimate data to a 3 hourly resolution
    # This is useful when visualising a long timeseries
    if decimate:
        if model in [
            "gfs_seamless",
            "gfs05",
            "gfs025",
            "ecmwf_ifs04",
            "ecmwf_ifs025",
            "gem_global",
            "bom_access_global_ensemble",
        ]:
            # The original data for all these models is 3 hourly, so there is no added
            # value in showing hourly data. Here we decimate every 3 hours considering
            # as starting point the first time value
            # which means that, in case the from_now option is activated, it will start
            # resampling every 3 hours from that starting point, otherwise it will resample
            # at 0, 3, 6, 9, 12, 18, as the data always starts at 00 UTC.
            #
            acc_vars = None
            acc_vars_regex = "|".join(
                [
                    item["value"]
                    for group in ENSEMBLE_VARS
                    if group["group"] == "Accumulated"
                    for item in group["items"]
                ]
            )
            if any(data.columns.str.contains(acc_vars_regex)):
                # Consider only the variables that are defined as accumulation over the last hour
                # First we do a rolling sum over the same period (3 hours) and then take only the
                # first value
                acc_vars = (
                    data.loc[
                        :,
                        data.columns.str.contains("time|" + acc_vars_regex),
                    ]
                    .rolling(window="3h", on="time")
                    .sum()
                    .resample("3h", on="time", origin=data.iloc[0]["time"])
                    .first()
                )
            inst_vars = None
            inst_vars_regex = "|".join(
                [
                    item["value"]
                    for group in ENSEMBLE_VARS
                    if group["group"] == "Instantaneous"
                    for item in group["items"]
                ]
            )
            if any(data.columns.str.contains(inst_vars_regex)):
                # Now the variables that are instantaneous
                # In this case we can just take the first value directly every 3 hours
                inst_vars = (
                    data.loc[
                        :,
                        data.columns.str.contains(
                            "time|" + inst_vars_regex
                        ),
                    ]
                    .resample("3h", on="time", origin=data.iloc[0]["time"])
                    .first()
                )
            max_vars = None
            max_vars_regex = "|".join(
                [
                    item["value"]
                    for group in ENSEMBLE_VARS
                    if group["group"] == "Preceding hour maximum"
                    for item in group["items"]
                ]
            )
            if any(data.columns.str.contains(max_vars_regex)):
                # Now variables with different aggregations (like preceding hour maximum)
                max_vars = (
                    data.loc[:, data.columns.str.contains("time|" + max_vars_regex)]
                    .rolling(window="3h", on="time")
                    .max()
                    .resample("3h", on="time", origin=data.iloc[0]["time"])
                    .first()
                )
            # Now merge everything together and overwrite the original data
            dfs = [inst_vars, acc_vars, max_vars]
            # Remove None objects
            dfs = [df for df in dfs if df is not None]
            # Merge all dataframes
            data = reduce(
                lambda left, right: pd.merge(
                    left, right, left_index=True, right_index=True
                ),
                dfs,
            )
            data = data.reset_index()
        elif model in ["icon_seamless", "icon_global", "icon_eu"]:
            # For these models we want to preserve the original hourly resolution
            # because it is the original one! Actually, for ICON-EPS the data
            # is every 6 hours, but I don't want to implement a different logic
            # just for that....
            # We leave the first 48 hrs untouched, and then decimate every 3 hours
            # NOTE that we count 48 hrs from the first time value. In case from_now = True
            # is activated, it could mean
            # NOTE icon_d2 is not here because we don't need to do anything in that case
            t48_start_date = data.iloc[0]["time"] + pd.to_timedelta("48h")
            after_48_hrs = data.loc[
                data.time >= t48_start_date + pd.to_timedelta("3h"), :
            ]
            # For this section does the same trick as before
            acc_vars = None
            acc_vars_regex = "|".join(
                [
                    item["value"]
                    for group in ENSEMBLE_VARS
                    if group["group"] == "Accumulated"
                    for item in group["items"]
                ]
            )
            if any(
                after_48_hrs.columns.str.contains(
                    acc_vars_regex
                )
            ):
                acc_vars = (
                    after_48_hrs.loc[
                        :,
                        after_48_hrs.columns.str.contains(
                            "time|" + acc_vars_regex
                        ),
                    ]
                    .rolling(window="3h", on="time")
                    .sum()
                    .resample("3h", on="time", origin=after_48_hrs.iloc[0]["time"])
                    .first()
                )
            inst_vars = None
            inst_vars_regex = "|".join(
                [
                    item["value"]
                    for group in ENSEMBLE_VARS
                    if group["group"] == "Instantaneous"
                    for item in group["items"]
                ]
            )
            if any(
                after_48_hrs.columns.str.contains(
                    inst_vars_regex
                )
            ):
                inst_vars = (
                    after_48_hrs.loc[
                        :,
                        after_48_hrs.columns.str.contains(
                            "time|" + inst_vars_regex
                        ),
                    ]
                    .resample("3h", on="time", origin=after_48_hrs.iloc[0]["time"])
                    .first()
                )
            max_vars = None
            max_vars_regex = "|".join(
                [
                    item["value"]
                    for group in ENSEMBLE_VARS
                    if group["group"] == "Preceding hour maximum"
                    for item in group["items"]
                ]
            )
            if any(after_48_hrs.columns.str.contains(max_vars_regex)):
                max_vars = (
                    after_48_hrs.loc[
                        :, after_48_hrs.columns.str.contains("time|" + max_vars_regex)
                    ]
                    .rolling(window="3h", on="time")
                    .max()
                    .resample("3h", on="time", origin=after_48_hrs.iloc[0]["time"])
                    .first()
                )
            # Now merge everything together and overwrite the original data
            dfs = [inst_vars, acc_vars, max_vars]
            # Remove None objects
            dfs = [df for df in dfs if df is not None]
            # Merge all dataframes
            after_48_hrs = reduce(
                lambda left, right: pd.merge(
                    left, right, left_index=True, right_index=True
                ),
                dfs,
            )
            after_48_hrs = after_48_hrs.reset_index()
            data = pd.concat(
                [data.loc[data.time <= t48_start_date, :], after_48_hrs]
            ).reset_index(drop=True)

    # Units conversion
    for col in data.columns[data.columns.str.contains("snow_depth")]:
        data[col] = data[col] * 100.0  # m to cm
    for col in data.columns[data.columns.str.contains("sunshine_duration")]:
        data[col] = data[col] / 3600.0  # s to hrs

    # Compute accumulated variables
    # Comment if not needed
    # Note that we have to change the name of the resulting accumulated variables
    # so as not to conflict with the functions that always request data using columns.str.contains()
    if data.columns.str.contains("precipitation").any():
        prec_acc = data.loc[:, data.columns.str.contains("precipitation")].cumsum()
        prec_acc.columns = prec_acc.columns.str.replace(
            "precipitation", "accumulated_precip"
        )
        data = data.merge(prec_acc, left_index=True, right_index=True)
    if data.columns.str.contains("rain").any():
        rain_acc = data.loc[:, data.columns.str.contains("rain")].cumsum()
        rain_acc.columns = rain_acc.columns.str.replace("rain", "accumulated_liquid")
        data = data.merge(rain_acc, left_index=True, right_index=True)
    if data.columns.str.contains("snowfall").any():
        snowfall_acc = data.loc[:, data.columns.str.contains("snowfall")].cumsum()
        snowfall_acc.columns = snowfall_acc.columns.str.replace(
            "snowfall", "accumulated_snow"
        )
        data = data.merge(snowfall_acc, left_index=True, right_index=True)

    # Add metadata (experimental)
    data.attrs = {
        x: resp[x] for x in resp if x not in ["hourly", "daily"]
    }

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
        payload).json()

    data = pd.DataFrame.from_dict(resp['hourly'])
    data['time'] = pd.to_datetime(
        data['time'], format='%Y-%m-%dT%H:%M')

    data = data.dropna()

    for col in data.columns[data.columns.str.contains('snow_depth')]:
        data[col] = data[col] * 100.  # m to cm
    for col in data.columns[data.columns.str.contains('sunshine_duration')]:
        data[col] = data[col] / 3600.  # s to hrs

    # Add metadata (experimental)
    data.attrs = {x: resp[x] for x in resp if x not in [
        "hourly", "daily"]}

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
        payload).json()

    data = pd.DataFrame.from_dict(resp['daily'])
    data['time'] = pd.to_datetime(data['time'])

    data = data.dropna()

    for col in data.columns[data.columns.str.contains('sunshine_duration')]:
        data[col] = data[col] / 3600.  # s to hrs

    # Add metadata (experimental)
    data.attrs = {x: resp[x] for x in resp if x not in [
        "hourly", "daily"]}

    return data


@cache.memoize(0)
@time_this_func
def compute_climatology(latitude=53.55,
                        longitude=9.99,
                        variables='temperature_2m',
                        timezone='auto',
                        model='best_match',
                        start_date='1991-01-01',
                        end_date='2020-12-31',
                        daily=False):
    """
    Compute climatology.
    This is a very expensive operation (5-6 seconds for the full 30 years)
    so it should be cached!
    """
    if daily:
        data = get_historical_daily_data(latitude, longitude, variables,
                                         timezone, model, start_date, end_date)
    else:
        data = get_historical_data(latitude, longitude, variables,
                                   timezone, model, start_date, end_date)

    # Add doy not as integer but as string to allow for leap years
    data['doy'] = data.time.dt.strftime("%m%d")
    if daily:
        mean = data.groupby(data.doy).mean(
            numeric_only=True).round(1).rename_axis(['doy']).reset_index()
    else:
        # Compute mean over day of the year AND hour
        mean = data.groupby([data.doy, data.time.dt.hour]).mean(
            numeric_only=True).round(1).rename_axis(['doy', 'hour']).reset_index()

    return mean


@cache.memoize(0)
@time_this_func
def compute_monthly_clima(latitude=53.55, longitude=9.99, model='era5',
                          start_date='1991-01-01', end_date='2020-12-31'):
    """Takes a 30 years hourly dataframe as input and compute
    some monthly statistics by aggregating many times"""
    daily = get_historical_daily_data(
        latitude=latitude,
        longitude=longitude,
        model=model,
        start_date=start_date,
        end_date=end_date,
        variables=(
            'temperature_2m_max,temperature_2m_min,temperature_2m_mean,'
            'precipitation_sum,snowfall_sum,wind_speed_10m_max,cloudcover_mean'
        ) 
    ).set_index('time')

    daily['overcast'] = daily['cloudcover_mean'] >= 80
    daily['partly_cloudy'] = (daily['cloudcover_mean'] < 80) & (
        daily['cloudcover_mean'] > 20)
    daily['sunny'] = daily['cloudcover_mean'] <= 20
    daily['t_max_gt_30'] = daily['temperature_2m_max'] > 30
    daily['t_max_gt_25'] = (daily['temperature_2m_max'] > 25) & (daily['temperature_2m_max'] <= 30)
    daily['t_max_gt_20'] = (daily['temperature_2m_max'] > 20) & (daily['temperature_2m_max'] <= 25)
    daily['t_max_gt_15'] = (daily['temperature_2m_max'] > 15) & (daily['temperature_2m_max'] <= 20)
    daily['t_max_gt_10'] = (daily['temperature_2m_max'] > 10) & (daily['temperature_2m_max'] <= 15)
    daily['t_max_gt_5'] = (daily['temperature_2m_max'] > 5) & (daily['temperature_2m_max'] <= 10)
    daily['t_max_gt_0'] = (daily['temperature_2m_max'] >= 0) & (daily['temperature_2m_max'] <= 5)
    daily['t_max_lt_0'] = (daily['temperature_2m_max'] >= -5) & (daily['temperature_2m_max'] < 0)
    daily['t_max_lt_m5'] = daily['temperature_2m_max'] < -5
    daily['frost'] = daily['temperature_2m_min'] <= 0
    daily['wet'] = daily['precipitation_sum'] >= 1.0  # mm
    daily['dry'] = daily['precipitation_sum'] < 1.0  # mm
    daily['snow'] = daily['snowfall_sum'] >= 1.0  # cm
    daily['p_50_100'] = (daily['precipitation_sum'] <= 100) & (
        daily['precipitation_sum'] > 50)
    daily['p_20_50'] = (daily['precipitation_sum'] <= 50) & (daily['precipitation_sum'] > 20)
    daily['p_10_20'] = (daily['precipitation_sum'] <= 20) & (daily['precipitation_sum'] > 10)
    daily['p_5_10'] = (daily['precipitation_sum'] <= 10) & (daily['precipitation_sum'] > 5)
    daily['p_2_5'] = (daily['precipitation_sum'] <= 5) & (daily['precipitation_sum'] > 2)
    daily['p_lt_2'] = (daily['precipitation_sum'] <= 2) & (daily['precipitation_sum'] > 1)
    daily['w_gt_61'] = (daily['wind_speed_10m_max'] >= 61)
    daily['w_gt_50'] = (daily['wind_speed_10m_max'] >= 50) & (
        daily['wind_speed_10m_max'] < 61)
    daily['w_gt_38'] = (daily['wind_speed_10m_max'] >= 38) & (
        daily['wind_speed_10m_max'] < 50)
    daily['w_gt_28'] = (daily['wind_speed_10m_max'] >= 28) & (
        daily['wind_speed_10m_max'] < 38)
    daily['w_gt_19'] = (daily['wind_speed_10m_max'] >= 19) & (
        daily['wind_speed_10m_max'] < 28)
    daily['w_gt_12'] = (daily['wind_speed_10m_max'] >= 12) & (
        daily['wind_speed_10m_max'] < 19)
    daily['w_gt_5'] = (daily['wind_speed_10m_max'] >= 5) & (
        daily['wind_speed_10m_max'] < 12)
    daily['w_gt_1'] = (daily['wind_speed_10m_max'] >= 1) & (
        daily['wind_speed_10m_max'] < 5)
    daily['w_calm'] = daily['wind_speed_10m_max'] <= 0.1
    #
    bool_cols = daily.dtypes[daily.dtypes == bool].index
    # Compute monthly stats
    monthly = daily[bool_cols].resample('1ME').sum().add_suffix('_days')
    monthly['monthly_rain'] = daily['precipitation_sum'].resample('1ME').sum()
    monthly['t2m_max_mean'] = daily['temperature_2m_max'].resample('1ME').mean()
    monthly['t2m_min_mean'] = daily['temperature_2m_min'].resample('1ME').mean()
    monthly['t2m_min_min'] = daily['temperature_2m_min'].resample('1ME').min()
    monthly['t2m_max_max'] = daily['temperature_2m_max'].resample('1ME').max()
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
            model='ecmwf_ifs025',
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
            model='ecmwf_ifs025',
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
        from_now=False,
        decimate=False)

    # This computes a daily aggregation for all ensemble members
    daily_tmin = data.loc[:, data.columns.str.contains(
        'temperature_2m|time')].resample('1D', on='time').min()
    daily_tmax = data.loc[:, data.columns.str.contains(
        'temperature_2m|time')].resample('1D', on='time').max()
    daily_wcode = data.loc[:, data.columns.str.contains(
        'weather_code|time')].resample('1D', on='time').median()
    daily_prec = data.loc[:, data.columns.str.contains(
        'precipitation|time')].resample('1D', on='time').sum()
    daily_sunshine = data.loc[:, data.columns.str.contains(
        'sunshine_duration|time')].resample('1D', on='time').sum()

    daily = daily_tmin.mean(axis=1).to_frame(name='t_min_mean')\
        .merge(daily_tmax.mean(axis=1).to_frame(name='t_max_mean'), left_index=True, right_index=True)\
        .merge(daily_tmin.min(axis=1).to_frame(name='t_min_min'), left_index=True, right_index=True)\
        .merge(daily_tmin.max(axis=1).to_frame(name='t_min_max'), left_index=True, right_index=True)\
        .merge(daily_tmax.max(axis=1).to_frame(name='t_max_max'), left_index=True, right_index=True)\
        .merge(daily_tmax.min(axis=1).to_frame(name='t_max_min'), left_index=True, right_index=True)\
        .merge(daily_wcode.mode(axis=1)[0].to_frame(name='weather_code').fillna(1).astype(int), left_index=True, right_index=True)\
        .merge(daily_prec.mean(axis=1).to_frame(name='daily_prec_mean'), left_index=True, right_index=True)\
        .merge(daily_prec.quantile(0.15, axis=1).to_frame(name='daily_prec_min'), left_index=True, right_index=True)\
        .merge(daily_prec.quantile(0.95, axis=1).to_frame(name='daily_prec_max'), left_index=True, right_index=True)\
        .merge(((daily_prec[daily_prec > 0.1].count(axis=1) / daily_prec.shape[1]) * 100.).to_frame(name='prec_prob'), left_index=True, right_index=True)\
        .merge(daily_sunshine.mean(axis=1).to_frame(name='sunshine_mean'), left_index=True, right_index=True)

    daily.attrs = data.attrs

    return daily
