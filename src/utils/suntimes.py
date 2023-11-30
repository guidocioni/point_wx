from datetime import datetime, timedelta
from jdcal import gcal2jd, jd2gcal
from math import sin, cos, asin, acos, pi
import pytz
from pytz import timezone
import pandas as pd
import time
from .custom_logger import logging, time_this_func


"""Different constants."""
# Equivalent Julian year of Julian days for 2000, 1, 1.5, noon
JULIAN_DAYS_2000 = 2451545.0

# Fractional Julian Day for leap seconds and terrestrial time
JULIAN_DAYS_LEAP = 0.00084

# Mean Solar Anomaly Constants
MEAN_M0 = 357.5291
MEAN_M1 = 0.98560028

# Equation of Center Constants
CENTER_C0 = 1.9148
CENTER_C1 = 0.0200
CENTER_C2 = 0.0003

# Ecliptic longitude : argument of perihelion
PERIHELION_ARGUMENT = 102.9372

# Equation of time (solar transit)
TIME_0 = 0.0053
TIME_1 = 0.0069

# Earth's maximal tilt toward the sun (degrees)
OBLIQUITY = 23.44

# Hour Angle ; corrections for atmospherical refraction and solar disc diameter (degrees)
# Correction for elevation (altitude : meters ; correction : degrees)
CORRECTION_REFRACTION = -0.833
CORRECTION_ELEVATION = -2.076

# Functions


def fraction_day_to_hms(f):
    # convert a fraction of a day in hours, minutes, seconds
    hms = f * 24 * 3600
    h = hms // 3600
    m = (hms - 3600*h) // 60
    s = hms - 3600*h - 60*m
    return (int(h), int(m), int(s), int(s % 1*1000))


def round_fractionDay_toHM(f):
    # round a fraction of a day into hours and minutes
    h = int(f*24)
    m = round(f*60*24 - h*60)
    if m < 60:
        h = h
        m = m
    else:
        m = 0
        h = h+1
        if h == 24:
            m = 59
            h = 23
    return (h, m)


def hms_to_fraction_day(h, m, s=0):
    # return fraction of a day (float between 0 and 1) from time of the day
    return (h*60*60 + m*60 + s)/(24*60*60)


def is_leap_year(y):
    # Return True if year y is leap, False if not.
    if (y % 4 != 0) or ((y % 100 == 0) and (y % 400 != 0)):
        return False
    else:
        return True


def len_year(year):
    # Return number of days of the year year
    if is_leap_year(year):
        return 366
    else:
        return 365


def length_month(year):
    # Return nombre of days for each month of the year year as a list : [31, 28, 31, 30...]
    if is_leap_year(year):
        return [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    else:
        return [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def days_year(year):
    # Return a list of all the days of the year : list of tuples (year, month, day)
    days = []
    for m in range(12):
        for d in range(length_month(year)[m]):
            day = (year, m+1, d+1)
            days.append(day)
    return days


def seconds_to_hhmm(seconds):
    # return duration of a day (0 <= seconds <= 86400) from seconds to hour and minutes, rounded
    hh = seconds // 3600
    seconds %= 3600
    if seconds % 60 <= 30:
        mm = seconds // 60
    else:
        mm = seconds // 60 + 1
    if mm == 60:
        mm = 0
        hh = hh + 1
    if hh >= 24:
        hh = 24
        mm = 0
    return [hh, mm]


def roundTime(dt=None, roundTo=60):
    """Round a datetime object to any time laps in seconds
    dt : datetime.datetime object, default now.
    roundTo : Closest number of seconds to round to, default 1 minute.
    Author: Thierry Husson 2012 - Use it as you want but don't blame me.
    """
    if dt is None:
        dt = datetime.now()
    seconds = (dt - dt.min).seconds
    rounding = (seconds+roundTo/2) // roundTo * roundTo
    return dt + timedelta(0, rounding-seconds, -dt.microsecond)


class SunTimes():
    """
    A place is characterized by longitude, latitude, altitude
    -longitude: float between -180 and 180; negative for west longitudes, positive for east longitudes
    -latitude: float between -66.56 and +66.56; the calculation is only valid between the two polar circles. Positive if north, negative if south
    - altitude: float, in meters; greater than or equal to zero
    -tz: timezone, eg 'Europe / Paris'
    The date will be a datetimes entered in the format (yyyy, mm, dd), the time not important. Eg : datetime(2020 12 22)
    The timezone list is available on : https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568
    """

    def __init__(self, longitude, latitude, altitude=0):
        if not (-180 <= longitude <= 180):
            raise ValueError("longitude must be between -180 and +180")
        if not (-90 <= latitude <= 90):
            raise ValueError("latitude must be between -90 and +90")
        if not (-66.56 <= latitude <= 66.56):
            print("Au-delà des cercles polaires / Beyond the polar circles ")
        if altitude < 0:
            raise ValueError("altitude must be positive")
        self.longitude = longitude
        self.latitude = latitude
        self.altitude = altitude

    def mean_solar_noon(self, date):
        Jdate = gcal2jd(date.year, date.month, date.day)
        Jdate = Jdate[0] + Jdate[1] + 0.5
        n = Jdate - JULIAN_DAYS_2000 + JULIAN_DAYS_LEAP
        JJ = n - self.longitude/360
        return JJ

    def solar_mean_anomaly(self, date):
        JJ = self.mean_solar_noon(date)
        M = (MEAN_M0 + MEAN_M1 * JJ) % 360
        return M

    def equation_center(self, date):
        M = self.solar_mean_anomaly(date)
        C = CENTER_C0 * sin(M*pi/180) + CENTER_C1 * \
            sin(2*M*pi/180) + CENTER_C2 * sin(3*M*pi/180)
        return C

    def ecliptic_longitude(self, date):
        M = self.solar_mean_anomaly(date)
        C = self.equation_center(date)
        le = (M + C + 180 + PERIHELION_ARGUMENT) % 360
        return le

    def solar_transit(self, date):
        JJ = self.mean_solar_noon(date)
        M = self.solar_mean_anomaly(date)
        le = self.ecliptic_longitude(date)
        J_transit = JULIAN_DAYS_2000 + JJ + TIME_0 * \
            sin(M*pi/180) - TIME_1*sin(2*le*pi/180)
        return J_transit

    def declination_sun(self, date):
        le = self.ecliptic_longitude(date)
        delta = asin(sin(le*pi/180) * sin(OBLIQUITY*pi/180))
        return delta

    def getOmega0(self, date):
        elevation = CORRECTION_REFRACTION + \
            CORRECTION_ELEVATION*(self.altitude**(1/2))/60
        delta = self.declination_sun(date)
        cosOmega0 = (sin(elevation*pi/180) - sin(self.latitude*pi/180)
                     * sin(delta))/(cos(self.latitude*pi/180) * cos(delta))
        return cosOmega0

    def hour_angle(self, date):
        # Return Omega0 angle if cosOmega0 between -1 and 1 ; otherwise return string Polar Night or Polar Day (PN, PD)
        cosOmega0 = self.getOmega0(date)
        if abs(cosOmega0) <= 1:
            return acos(cosOmega0)
        elif cosOmega0 > 1:
            return "PN"
        else:
            return "PD"

    def J_rise_set_greg(self, date):
        # Return julian day (with hour) of sunrise and sunset : tuple (year, month, day, fraction of the day)
        J_transit = self.solar_transit(date)
        omega0 = self.hour_angle(date)
        if not isinstance(omega0, str):
            J_rise = J_transit - (omega0*180/pi)/360
            J_set = J_transit + (omega0*180/pi)/360
            J_rise_greg = jd2gcal(int(J_rise), J_rise - int(J_rise))
            J_set_greg = jd2gcal(int(J_set), J_set - int(J_set))
            return [J_rise_greg, J_set_greg]
        else:
            # Return a list with datetime as first element and string as second
            return [date, omega0]

    # Return a date in the datetime format of the day with h, mn. UTC or local computer time. Minutes are rounded up or down, depending of the seconds. The seconds are not given: the precision of the calculations being beyond the minute. Seconds are zero in the datetime.
    def riseutc(self, date):
        j_greg = self.J_rise_set_greg(date)
        j_day = self.J_rise_set_greg(date)[0]
        if not isinstance(j_greg[-1], str):
            hms = round_fractionDay_toHM(j_day[3])
            date_hms = datetime(int(j_day[0]), int(
                j_day[1]), int(j_day[2]), hms[0], hms[1])
            return date_hms
        else:
            return j_greg[-1]

    def setutc(self, date):
        j_greg = self.J_rise_set_greg(date)
        j_day = self.J_rise_set_greg(date)[1]
        if not isinstance(j_greg[-1], str):
            hms = round_fractionDay_toHM(j_day[3])
            date_hms = datetime(int(j_day[0]), int(
                j_day[1]), int(j_day[2]), hms[0], hms[1])
            return date_hms
        else:
            return j_greg[-1]

    def riselocal(self, date):
        utc_time = self.riseutc(date)
        if not isinstance(utc_time, str):
            local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(
                pytz.timezone('Europe/Berlin'))
            return local_time
        else:
            return utc_time

    def setlocal(self, date):
        utc_time = self.setutc(date)
        if not isinstance(utc_time, str):
            local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(
                pytz.timezone('Europe/Berlin'))
            return local_time
        else:
            return utc_time

    # Return the hours, minutes local computer time for sunrise and sunset
    def hrise(self, date):
        my_date = self.riselocal(date)
        if not isinstance(my_date, str):
            return my_date.hour
        else:
            return my_date

    def hset(self, date):
        my_date = self.setlocal(date)
        if not isinstance(my_date, str):
            return my_date.hour
        else:
            return my_date

    def mrise(self, date):
        my_date = self.riselocal(date)
        if not isinstance(my_date, str):
            return my_date.minute
        else:
            return my_date

    def mset(self, date):
        my_date = self.setlocal(date)
        if not isinstance(my_date, str):
            return my_date.minute
        else:
            return my_date

    # Returns the duration of the day (deltatime or tuple: h, m or verbose)
    def durationdelta(self, date):
        sunrise = self.riseutc(date)
        sunset = self.setutc(date)
        if not isinstance(sunrise, str) and not isinstance(sunset, str):

            return (sunset - sunrise)
        elif isinstance(sunrise, str) and isinstance(sunset, str):
            return 'Not calculable : {sunrise}'
        else:
            return 'Not calculable : changement jour/nuit polaire'

    def durationtuple(self, date):
        delta = self.durationdelta(date)
        if not isinstance(delta, str):
            time = self.durationdelta(date).total_seconds()
            return round_fractionDay_toHM(time / 86400)
        else:
            return delta

    def durationverbose(self, date):
        delta = self.durationtuple(date)
        if not isinstance(delta, str):
            h = delta[0]
            m = delta[1]
            return "{}h {}mn".format(h, m)
        else:
            return delta

    # Return sunrise and sunset of a place by choosing the timezone.
    def risewhere(self, date, elsewhere):
        utc_time = self.riseutc(date)
        if not isinstance(utc_time, str):
            else_time = utc_time.replace(
                tzinfo=pytz.utc).astimezone(timezone(elsewhere))
            return else_time
        else:
            return utc_time

    def setwhere(self, date, elsewhere):
        utc_time = self.setutc(date)

        if not isinstance(utc_time, str):
            else_time = utc_time.replace(
                tzinfo=pytz.utc).astimezone(timezone(elsewhere))
            return else_time
        else:
            return utc_time

@time_this_func
def find_suntimes(df, latitude, longitude, elevation=0):
    """
    Wrapper to use the library to compute suntimes using
    an input dataframe that contains data downloaded with OpenMeteo api
    We just need a column with time, then we're going to resample to daily
    frequency and use that to compute the rise and set times.
    Providing elevation improves the computation.
    """
    sun = SunTimes(longitude, latitude, elevation)

    # Create a dataframe with only daily data, we don't actually care
    # about the time but only about the data
    daily = df[['time']].resample('1D', on='time').first().reset_index()

    # Function to apply to every row of this dataframe
    def find_times(df):
        sunrise = sun.riseutc(df['time']).replace(
            tzinfo=pytz.utc).astimezone(df['time'].tz)
        sunset = sun.setutc(df['time']).replace(
            tzinfo=pytz.utc).astimezone(df['time'].tz)

        return sunrise, sunset

    daily = daily.merge(daily.apply(lambda x: find_times(x), axis=1).apply(pd.Series).rename(columns={0: 'sunrise', 1: 'sunset'}),
                        left_index=True, right_index=True)

    return daily
