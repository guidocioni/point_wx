"""Climatology variable definitions."""

# Subset of ENSEMBLE_VARS with a matching (same units) hourly variable in the
# ERA5 archive API, used to gate the climatology overlay in ensemble_heatmap.
# Pressure-level fields (temperature_850hPa/500hPa, geopotential heights) and
# freezinglevel_height are not exposed by the archive API (always null) and
# are excluded here; temperature_850hPa climatology is instead sourced from a
# local zarr archive (see compute_climatology_zarr), same as the ensemble page.
CLIMATOLOGY_VARS = [
    "temperature_2m",
    "pressure_msl",
    "sunshine_duration",
]
