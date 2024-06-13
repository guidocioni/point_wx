import requests as r
import json
import hashlib
from .settings import cache, MAPBOX_API_KEY, MAPBOX_API_PLACES_URL


@cache.memoize(3600)
def get_place_address_reverse(lon, lat):
    url = f"{MAPBOX_API_PLACES_URL}/{lon},{lat}.json?&access_token={MAPBOX_API_KEY}&limit=1"
    response = r.get(url)
    json_data = json.loads(response.text)

    # Latitude and longitude will always be in the response
    res = {}
    res["lon"], res["lat"] = json_data["query"]
    res['name'] = 'Custom Location'

    # Now start extracting features
    # As we're using limit = 1 it will only be 1
    if len(json_data["features"]) >= 1:
        feature = json_data["features"][0]
    else:
        # No feature found, we just return the coordinates
        # used in the query
        return res
    # We start extracting information
    # These properties should always be defined
    res["place_type"] = feature["place_type"][0]
    res["text"] = feature["text"]
    # Now start extracting the context information
    context = feature["context"]
    # Country is always present
    country = [c for c in context if "country" in c["id"]][0]
    res["country_name"] = country["text"]
    res["country_code"] = country["short_code"].upper()
    # All the rest now is optional
    region = [c for c in context if "region" in c["id"]]
    if len(region) > 0:
        res["region_name"] = region[0]["text"]
    district = [c for c in context if "district" in c["id"]]
    if len(district) > 0:
        res["district_name"] = district[0]["text"]
    place = [c for c in context if "place" in c["id"]]
    if len(place) > 0:
        res["place_name"] = place[0]["text"]
    locality = [c for c in context if "locality" in c["id"]]
    if len(locality) > 0:
        res["locality_name"] = locality[0]["text"]
    # Create a friendly name for this point which includes the closest city
    if 'locality_name' in res:
        res['name'] = res['locality_name']
    elif 'place_name' in res:
        res['name'] = res['place_name']
    elif 'region_name' in res:
        res['name'] = res['region_name']
    else:
        # In this case usually we're left with the country only
        # so the text attribute works just fine
        res['name'] = res['text']

    return res


def create_unique_id(latitude, longitude, place_name):
    '''Useful to create a location unique id
    based on latitude, longitude and place_name'''
    # Normalize inputs
    normalized_string = f"{latitude:.4f}{longitude:.4f}{place_name}"
    
    # Create a hash of the concatenated string
    hash_object = hashlib.md5(normalized_string.encode())
    hash_hex = hash_object.hexdigest()
    
    # Convert hash to an integer and take the first 6 digits
    unique_id = int(hash_hex, 16) % 1000000
    
    # Ensure the unique_id is 6 digits long
    return f"{unique_id:06d}"
