import requests as r
import json
from .settings import cache, MAPBOX_API_KEY, MAPBOX_API_PLACES_URL


@cache.memoize(3600)
def get_place_address_reverse(lon, lat):
    url = f"{MAPBOX_API_PLACES_URL}/{lon},{lat}.json?&access_token={MAPBOX_API_KEY}&limit=1"

    response = r.get(url)
    json_data = json.loads(response.text)

    place_name = json_data["features"][0]["place_name"]
    context = json_data["features"][0]["context"]
    country_name = [c["text"] for c in context if "country" in c["id"]]
    if country_name is not None:
        country_name = country_name[0]
    country_code = [c["short_code"].upper() for c in context if "country" in c["id"]]
    if country_code is not None:
        country_code = country_code[0]
    place = [c["text"] for c in context if "place" in c["id"]]
    if place is not None:
        place = place[0]

    return {
        "place_name": place_name,
        "city": place,
        "country_name": country_name,
        "country_code": country_code,
    }
