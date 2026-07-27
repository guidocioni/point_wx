import requests as r
import json
import hashlib
import pandas as pd
import re
import logging
from .settings import cache, MAPBOX_API_KEY, MAPBOX_API_PLACES_URL
from .openmeteo_api import get_elevation


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

    # We start extracting information using helper functions
    res["place_type"] = feature["place_type"][0]
    res["text"] = feature["text"]

    # Extract country and admin levels using helper functions
    res["country_name"] = _extract_country_name(feature)
    res["country_code"] = _extract_country_code(feature)

    # Extract optional admin levels
    region_name = _extract_admin_level(feature, 'region')
    if region_name:
        res["region_name"] = region_name
    district_name = _extract_admin_level(feature, 'district')
    if district_name:
        res["district_name"] = district_name
    place_name = _extract_admin_level(feature, 'place')
    if place_name:
        res["place_name"] = place_name
    locality_name = _extract_admin_level(feature, 'locality')
    if locality_name:
        res["locality_name"] = locality_name

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


def _extract_from_context(feature, id_prefix):
    """Extract value from feature context by id prefix"""
    if 'context' not in feature:
        return None
    for item in feature['context']:
        if item['id'].startswith(id_prefix):
            return item
    return None


def _extract_country_code(feature):
    """Extract uppercase country code"""
    country = _extract_from_context(feature, 'country')
    return country['short_code'].upper() if country else ''


def _extract_country_name(feature):
    """Extract country name"""
    country = _extract_from_context(feature, 'country')
    return country['text'] if country else ''


def _extract_admin_level(feature, level):
    """Extract administrative level (region, district, place, locality)"""
    admin = _extract_from_context(feature, level)
    return admin['text'] if admin else ''


@cache.memoize(3600)
def get_locations_mapbox(name, count=10, proximity=None):
    """
    Search for locations using Mapbox forward geocoding API.

    Returns a pandas DataFrame compatible with location_selector callbacks,
    matching the schema of open-meteo's get_locations().

    Parameters:
    -----------
    name : str
        Search query (location name)
    count : int
        Maximum number of results to return (default 10, Mapbox max is 10)
    proximity : tuple, optional
        (longitude, latitude) tuple to bias results toward a location.
        E.g., proximity=(12.4964, 41.9028) biases toward Rome.

    Returns:
    --------
    pd.DataFrame with columns: id, name, latitude, longitude, elevation,
    country_code, country, admin1, admin2, admin3, admin4, timezone,
    population, postcodes, feature_code

    Returns empty DataFrame if no results or error occurs.
    """
    # Check if API key is configured
    if not MAPBOX_API_KEY:
        logging.error("MAPBOX_API_KEY not configured")
        return pd.DataFrame()

    # Input sanitization - match open-meteo's logic
    # Remove any number (we don't use the postal code lookup)
    name = re.sub(r'\d', '', name)
    # Replace more than 2 spaces with just one space
    name = re.sub(r'\s{2,}', ' ', name)
    # Remove trailing and leading whitespaces
    name = re.sub(r'^[\s]+|[\s]+$', '', name)

    # Return empty DataFrame if query is empty after sanitization
    if not name:
        return pd.DataFrame()

    # Make API request to Mapbox
    try:
        url = f"{MAPBOX_API_PLACES_URL}/{name}.json"
        params = {
            "access_token": MAPBOX_API_KEY,
            "limit": min(count, 10),  # Mapbox max is 10
            "autocomplete": True,
            "types": "country,region,district,place,locality,neighborhood,address"
        }
        # Note: No language parameter - lets Mapbox match native place names
        # This fixes "milano" -> Milan, Italy (instead of forcing English "Milan")

        # Add proximity bias if provided
        if proximity:
            params["proximity"] = f"{proximity[0]},{proximity[1]}"

        response = r.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # Extract features
        features = data.get('features', [])

        if not features:
            return pd.DataFrame()

        # Build location list with coordinates
        locations = []
        lats = []
        lons = []

        for feature in features:
            latitude = feature['center'][1]
            longitude = feature['center'][0]
            lats.append(latitude)
            lons.append(longitude)

            # Store matching_text for search purposes (Latin transliteration)
            # Keeps native name for display, but allows "Sapporo" to find "札幌市"
            matching_name = feature.get('matching_text', '')

            loc = {
                'id': feature['id'],
                'name': feature['text'],
                'matching_name': matching_name,  # For dropdown search field
                'longitude': longitude,
                'latitude': latitude,
                'elevation': 0,  # Will be filled in batch below
                'feature_code': feature['place_type'][0] if feature.get('place_type') else '',
                'country_code': _extract_country_code(feature),
                'country': _extract_country_name(feature),
                'country_id': '',  # Not available from Mapbox, set empty for compatibility
                'admin1': _extract_admin_level(feature, 'region'),
                'admin1_id': '',  # Not available from Mapbox, set empty for compatibility
                'admin2': _extract_admin_level(feature, 'district'),
                'admin3': _extract_admin_level(feature, 'place'),
                'admin3_id': '',  # Not available from Mapbox, set empty for compatibility
                'admin4': _extract_admin_level(feature, 'locality'),
                'admin4_id': '',  # Not available from Mapbox, set empty for compatibility
                'timezone': '',  # Not available from Mapbox
                'population': 0,  # Not available from Mapbox
                'postcodes': ['']  # Not used
            }
            locations.append(loc)

        # Batch fetch elevations for all locations at once (much faster!)
        if lats and lons:
            lat_str = ','.join(str(lat) for lat in lats)
            lon_str = ','.join(str(lon) for lon in lons)
            elevations = get_elevation(lat_str, lon_str)

            # Fill in elevations
            if elevations and isinstance(elevations, list):
                for i, elev in enumerate(elevations):
                    if i < len(locations):
                        locations[i]['elevation'] = elev if elev is not None else 0

        return pd.DataFrame(locations)

    except (r.RequestException, json.JSONDecodeError, KeyError) as e:
        logging.warning(f"Mapbox geocoding failed for '{name}': {e}")
        return pd.DataFrame()
