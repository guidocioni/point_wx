"""
Helper utilities for filtering model options based on location domains.
Provides a callback factory to avoid duplicating the location-based model filtering logic across pages.
"""

from dash import callback, Output, Input, State, no_update
from utils.model_domains import filter_models_by_location
from utils.custom_logger import logging
import pandas as pd
from io import StringIO


def create_location_model_filter_callback(
    model_dropdown_id,
    model_options,
    model_type="ensemble"
):
    """
    Factory function to create a location-based model filtering callback.

    This avoids duplicating the same callback logic across multiple pages.
    Each page can call this function with their specific dropdown ID and model list.

    Args:
        model_dropdown_id: The component ID of the model dropdown (e.g., "models-selection")
        model_options: The model options list (e.g., ENSEMBLE_MODELS, DETERMINISTIC_MODELS)
        model_type: Either "ensemble" or "deterministic" for domain lookup

    Returns:
        The registered callback function
    """

    @callback(
        [
            Output(model_dropdown_id, "data"),
            Output(model_dropdown_id, "value"),
        ],
        [
            Input("locations-list", "data"),
            Input("location-selected", "data"),
        ],
        State(model_dropdown_id, "value"),
        prevent_initial_call=True,
    )
    def update_model_options_and_selection(locations, location, current_model):
        """
        Filter model options based on selected location's geographic domain.
        Models that don't cover the location will be disabled (grayed out) but still visible.
        If the currently selected model becomes disabled, auto-switch to the first enabled model.
        """
        if not locations or not location:
            # Return default options with no disabled items
            return model_options, no_update

        try:
            # Parse locations data
            locations_df = pd.read_json(StringIO(locations), orient="split", dtype={"id": str})
            loc = locations_df[locations_df["id"] == location[0]["value"]]

            if loc.empty:
                return model_options, no_update

            # Get location coordinates
            latitude = loc["latitude"].item()
            longitude = loc["longitude"].item()

            # Filter models based on domain coverage
            filtered_options = filter_models_by_location(
                latitude=latitude,
                longitude=longitude,
                model_options=model_options,
                model_type=model_type
            )

            # Build a set of disabled model values for quick lookup
            disabled_models = set()
            for group in filtered_options:
                for item in group["items"]:
                    if item.get("disabled", False):
                        disabled_models.add(item["value"])

            # Handle multi-select (list of values) vs single-select (single value)
            if isinstance(current_model, list):
                # Multi-select: filter out disabled models from the selection
                valid_models = [m for m in current_model if m not in disabled_models]

                if len(valid_models) < len(current_model):
                    # Some models were removed
                    removed = [m for m in current_model if m in disabled_models]
                    logging.debug(
                        f"[{model_dropdown_id}] Removed incompatible models for "
                        f"location ({latitude:.2f}, {longitude:.2f}): {removed}"
                    )
                    return filtered_options, valid_models

                # No change needed
                return filtered_options, no_update

            else:
                # Single-select: replace with first enabled model if current is disabled
                if current_model and current_model in disabled_models:
                    # Find first enabled model as fallback
                    for group in filtered_options:
                        for item in group["items"]:
                            if not item.get("disabled", False):
                                logging.debug(
                                    f"[{model_dropdown_id}] Model {current_model} disabled for "
                                    f"location ({latitude:.2f}, {longitude:.2f}), switching to {item['value']}"
                                )
                                return filtered_options, item["value"]

                    # Fallback to first available model if somehow all are disabled
                    # (shouldn't happen with global models in the list)
                    first_model = filtered_options[0]["items"][0]["value"]
                    logging.warning(
                        f"[{model_dropdown_id}] All models disabled, falling back to {first_model}"
                    )
                    return filtered_options, first_model

                # Current selection is still valid
                return filtered_options, no_update

        except Exception as e:
            logging.error(f"Error filtering model options by location for {model_dropdown_id}: {e}")
            # On error, return default options
            return model_options, no_update

    return update_model_options_and_selection
