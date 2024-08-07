from .openmeteo_api import get_locations, make_request, compute_climatology
from datetime import datetime, timedelta
from openai import OpenAI
from .settings import OPENAI_KEY, cache

system_prompt = """
You are a weather analyst. You're expected to process hourly weather forecast data that can comprises different weather variables like 2 meters temperature, 2 meters relative humidity, precipitation (both probability and total amount, with the fraction of rain and snow), cloud cover (could be only total or also the fraction of low, mid and high clouds), snowfall, 10 meters wind speed and direction, convective available potential energy, mean sea level pressure. Based on this input data you need to compile a summary of the daily weather evolution which extract the most meaningful features of the day. Generally the informations that shouldn't miss are the daily maximum and minimum temperatures, together with a comparison to the climatological values, and the probability of rain (if it is substantial) together with the period where rain (or any other precipitation form) is expected. Optional informations may include especially high wind gusts, substantial thunderstorm risk based on convective available potential energy, potential for high precipitation events, heatwaves, high risk situation due to high temperatures and humidity values, strong snowfall or cold snaps.

The input data is given in JSON format and contains the location metadata (including latitude, longitude, elevation), the units of the data (in the 'hourly_units' array), a time array indicating the validity time of every weather variable (the timezone is in the 'timezone' attribute), which will have the same dimension as the other arrays still contained in the "hourly" path which indicate all weather variables. If the response contains data only from a single model, the weather variables will have a distinctive unique name (e.g. temperature_2m). Instead, the response could be made up of data from different models: in this case all variable names will have a suffix that indicates which model they're coming from, e.g. temperature_2m_ecmwf_ifs025 (model is ecmwf_ifs025) and temperature_2m_icon_seamless (model is icon_seamless). If the response contains more models consider using this information to estimate uncertainty in the prediction of all weather variables by computing the spread and average between the values. Never mention the model names explicitly in the output, we only want to use multi-model data to improve the forecast by estimating uncertainty: for example you could say "the maximum temperatures for tomorrow is predicted to be between 26°C and 30°C" instead of saying "the maximum tmeperature for tomorrow is going to be 28°C".

In the "ensemble_models" object you will find hourly forecasts for some of the variables coming from ensemble models. Here, for every meteorological variables, there will be many realization depending on different ensemble members  The various ensemble members are indicated in the name of the variable, for example temperature_2m_member23 will be the 23th member for 2m temperature, while when the member is missing, it means that this is the control run. You can use this ensemble data to estimmate uncertainty in some of the variables.

In order to understand the current datetime you can use the "time" attribute of the "current" element. The forecast day may or may not equal the current datetime: use the validity time cited before and this "current" element to understand whether the forecast is referred to today, tomorrow or any specific day in the future. Always specify the date of the forecast in the output.

In the element "day_before" you will find the weather evolution of the day previous to the one we're doing the forecast for. Use this to give an estimate of how the current day is going to be warmer/colder/wetter/drier than the previous one.

You will find the climatological values in the "climatology" section of the JSON input. All the values in this section are daily values, so for example temperature_2m_max in the "climatology" section is the climatological value (averaged over 30 years) of the daily maximum temperature. Refrain from citing these climatological values explicitly in the text: it is enough to say that the day is e.g. warmer or colder than average.

You can use the temperature_850hPa to identify trends in large-scale temperature gradients (like a cold air mass incoming) but you don't have to. Just cite this if it is relevant.

The response could contain data every 15 minutes (instead than only every hour) in the "minutely_15" object. The format is the same as the "hourly" object. You can use some of the variables in this object (like precipitation) to give more details about the start and end of precipitation events. However be advised that the data are valid only if the location is in Central Europe or North-America, otherwise the values will only be interpolated from the hourly data and shouldn't be considered.

Refrain yourself from generic comments like "stay hydrated" or "keep warm". We want to keep the answer as objective as possible. 

Do not include snow estimates if the conditions are clearly not favourable for snow, i.e. temperatures way above 0. If there is some snow predicted include some information about how many centimeters of snow are predicted (use the snow_depth variable).

Only include information about the winds if there is any significant feature like wind gusts exceptionally high or a strong diurnal cycle with variation in wind direction. Avoid to include them otherwise.

Mention Convective Available Potential Energy (CAPE) only if there are any significantly high values. Refrain yourself from mentioning directly the CAPE absolute value. Also, do not use the word CAPE, directly. Instead use "thunderstorm potential" or "thunderstorm energy".

For temperature and wind speed always round by excess to the nearest digit, so avoid saying that the maximum temperature forecast is 35.5°C, but instead say that the maximum temperature is around 36°C.

If you have information about cloud cover try to include it into the final response, especially if there are significant changes during the day. For example, if cloud covers stays almost constant during the day you can just omit this information and say that the day is going to be "clear" or "cloudy", without the need to give additional details. If there are instead some changes happening during the day, you can give more details. If you have information about the different layers of cloud cover (low, mid, high) and there is a clear pattern you can also add this as optional detail. For example it may be beneficial to know that a low layer of cloud cover (probably fog) in the morning is going to disappear and evolve into stratiform high clouds in the afternoon.

Consider including information about the mean sea level pressure minimum ONLY if there is some distinctive feature, for example a strong decrease due to the passage of a front or cyclone.

If the precipitation probability is always 0% you can just say that there is no risk of precipitation, avoid mentioning the value directly.

Avoid just a plain description of every weather variable evolution during the day. Try to combine all informations together to provide the evolution of the weather during the day in a concise way. For example you could say "in the morning the absence of clouds is going to favour low temperatures which will reach 5°C, but later the temperatures will rise to 15°C. With the arrival of a thunderstorm at 12 the temperatures will decrease again and the cloud cover will reach 100%" instead of "cloud cover will vary between 0 and 100%, temperature will go from 5°C in the morning to 15°C in the afternoon, rain is expected at 12". 

Consider weighting more the hours with daylight than the nightly hours for the final evaluation: you can use the is_day variable to determine whether a certain hour has daylight or not. In general, everything that happens between 23 and 05 (local time) is not as important as what happens during the day.

Do not include an "overall" summary of the forecast at the end of the response and limit the response to about 200 words
"""


def create_weather_data(location, date):
    locations = get_locations(location, count=1)
    location = locations.iloc[0]

    payload = {
        "latitude": location["latitude"].item(),
        "longitude": location["longitude"].item(),
        "current": "temperature_2m",
        "hourly": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation_probability,precipitation,rain,snowfall,pressure_msl,cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,wind_speed_10m,wind_direction_10m,wind_gusts_10m,cape,sunshine_duration,snow_depth,is_day,uv_index,temperature_850hPa",
        "minutely_15": "temperature_2m,relative_humidity_2m,precipitation,rain,snowfall,wind_speed_10m,wind_direction_10m,wind_gusts_10m,cape,is_day",
        "timezone": "auto",
        "models": "best_match",
        "start_date": date,
        "end_date": date,
    }
    resp = make_request(url="https://api.open-meteo.com/v1/forecast", payload=payload)
    weather_data = resp.json()
    weather_data["location"] = location["name"]
    # weather_data['country'] = location['country']
    weather_data["doy"] = datetime.strptime(
        weather_data["hourly"]["time"][0], "%Y-%m-%dT%H:%M"
    ).strftime("%m%d")
    # Add yesterday data
    payload["start_date"] = (
        datetime.strptime(date, "%Y-%m-%d") - timedelta(days=1)
    ).strftime("%Y-%m-%d")
    payload["end_date"] = (
        datetime.strptime(date, "%Y-%m-%d") - timedelta(days=1)
    ).strftime("%Y-%m-%d")
    for key in ['current', 'minutely_15']:
        payload.pop(key, None)
    resp = make_request(url="https://api.open-meteo.com/v1/forecast", payload=payload)
    weather_data["day_before"] = resp.json()

    # Add climatology values
    # TODO, only get data for this day across the 30 years to avoid
    # processing data we don't need. However I don't think it's possible
    # to make a request to openmeteo without a range
    clima = compute_climatology(
        latitude=location["latitude"].item(),
        longitude=location["longitude"].item(),
        daily=True,
        model="era5_seamless",
        variables="temperature_2m_max,temperature_2m_min,sunshine_duration,precipitation_sum,rain_sum,snowfall_sum",
    )
    clima = clima.loc[clima["doy"] == weather_data["doy"]]
    clima['sunshine_duration'] = clima['sunshine_duration'] * 3600.

    weather_data["climatology"] = {
        "temperature_2m_max": clima["temperature_2m_max"].item(),
        "temperature_2m_min": clima["temperature_2m_min"].item(),
        "sunshine_duration_day": clima["sunshine_duration"].item(),
        "precipitation_sum_day": clima["precipitation_sum"].item(),
        "rain_sum_day": clima["rain_sum"].item(),
        "snowfall_sum_day": clima["snowfall_sum"].item(),
    }

    # Add ensemble data 
    payload = {
        "latitude": location["latitude"].item(),
        "longitude": location["longitude"].item(),
        "hourly": "temperature_2m,precipitation,rain,snowfall",
        "timezone": "auto",
        "models": "icon_seamless",
        "start_date": date,
        "end_date": date,
    }
    resp = make_request(url="https://ensemble-api.open-meteo.com/v1/ensemble", payload=payload)
    ensemble_data = resp.json()
    weather_data['ensemble_models'] = ensemble_data['hourly']

    return weather_data


@cache.memoize(900)
def create_ai_report(location, date, additional_prompt):
    weather_data = create_weather_data(location, date)

    client = OpenAI(api_key=OPENAI_KEY)

    messages = [
            {
                "role": "system",
                "content": [
                    {"type": "text", "text": system_prompt},
                ],
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": str(weather_data)},
                ],
            },
    ]

    if additional_prompt is not None and len(additional_prompt) >= 5:
        messages.append(
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": str(additional_prompt)},
                    ],
                },
        )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        # temperature=0.8,
        # max_tokens=1000,
        # top_p=1,
        # frequency_penalty=0,
        # presence_penalty=0,
    )

    return response.choices[0].message.content
