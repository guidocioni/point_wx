"""
Model geographic domain utility functions.

Domain data has been moved to utils.constants.domains.
This module provides helper functions for working with those domains.
"""

from utils.constants.domains import ENSEMBLE_DOMAINS, DETERMINISTIC_DOMAINS


def is_location_in_domain(latitude, longitude, domain):
    """
    Check if a location (lat, lon) falls within a domain bounding box.

    Args:
        latitude: Location latitude in decimal degrees
        longitude: Location longitude in decimal degrees
        domain: Tuple of (lat_min, lat_max, lon_min, lon_max)

    Returns:
        bool: True if location is within domain, False otherwise
    """
    lat_min, lat_max, lon_min, lon_max = domain
    return lat_min <= latitude <= lat_max and lon_min <= longitude <= lon_max


def filter_models_by_location(latitude, longitude, model_options, model_type="ensemble"):
    """
    Filter model options based on location, disabling models that don't cover the area.

    Args:
        latitude: Location latitude in decimal degrees
        longitude: Location longitude in decimal degrees
        model_options: List of model option groups (as defined in settings.ENSEMBLE_MODELS)
        model_type: Type of models ("ensemble" or "deterministic")

    Returns:
        List of model option groups with 'disabled' key added to each item
    """
    # Select the appropriate domain dictionary
    domains = ENSEMBLE_DOMAINS if model_type == "ensemble" else DETERMINISTIC_DOMAINS

    # Deep copy the model options and add disabled flag
    filtered_options = []
    for group in model_options:
        filtered_group = {
            "group": group["group"],
            "items": []
        }

        for item in group["items"]:
            model_value = item["value"]
            # Check if model covers this location
            if model_value in domains:
                domain = domains[model_value]
                is_covered = is_location_in_domain(latitude, longitude, domain)

                # Create new item dict with disabled flag
                filtered_item = {
                    "label": item["label"],
                    "value": item["value"],
                    "disabled": not is_covered
                }
            else:
                # If domain not defined, assume global coverage and enable it
                filtered_item = {
                    "label": item["label"],
                    "value": item["value"],
                    "disabled": False
                }

            filtered_group["items"].append(filtered_item)

        filtered_options.append(filtered_group)

    return filtered_options


def get_compatible_models(latitude, longitude, model_options, model_type="ensemble"):
    """
    Get list of compatible model values for a location.

    Args:
        latitude: Location latitude in decimal degrees
        longitude: Location longitude in decimal degrees
        model_options: List of model option groups
        model_type: Type of models ("ensemble" or "deterministic")

    Returns:
        List of compatible model value strings
    """
    domains = ENSEMBLE_DOMAINS if model_type == "ensemble" else DETERMINISTIC_DOMAINS
    compatible = []

    for group in model_options:
        for item in group["items"]:
            model_value = item["value"]
            if model_value in domains:
                domain = domains[model_value]
                if is_location_in_domain(latitude, longitude, domain):
                    compatible.append(model_value)
            else:
                # If domain not defined, assume compatible
                compatible.append(model_value)

    return compatible
