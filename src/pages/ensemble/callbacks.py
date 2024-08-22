from dash import callback, Output, Input, State, no_update, clientside_callback
from utils.openmeteo_api import (
    get_ensemble_data,
    compute_climatology,
    compute_climatology_zarr,
)
from utils.suntimes import find_suntimes
from utils.custom_logger import logging
from .figures import make_subplot_figure, make_barpolar_figure
from components import location_selector_callbacks
import pandas as pd
from io import StringIO


@callback(
    [
        Output(dict(type="figure", id="ensemble"), "figure"),
        #  Output("polar-plot", "figure"),
        Output("error-message", "children", allow_duplicate=True),
        Output("error-modal", "is_open", allow_duplicate=True),
    ],
    Input({"type": "submit-button", "index": "ensemble"}, "n_clicks"),
    [
        State("locations-list", "data"),
        State("location-selected", "data"),
        State("models-selection", "value"),
        State("clima-switch", "checked"),
        State("from-now-switch", "checked"),
        State("wind-cloud-plot-switch", "checked"),
    ],
    prevent_initial_call=True,
)
def generate_figure(
    n_clicks, locations, location, model, clima_, from_now_, clouds_plot_
):
    if n_clicks is None:
        return no_update, no_update, no_update

    # unpack locations data
    locations = pd.read_json(StringIO(locations), orient="split", dtype={"id": str})
    loc = locations[locations["id"] == location[0]["value"]]

    try:
        data = get_ensemble_data(
            latitude=loc["latitude"].item(),
            longitude=loc["longitude"].item(),
            model=model,
            decimate=True,
            from_now=from_now_,
            variables="temperature_2m,temperature_850hPa,rain,snowfall,cloudcover,wind_speed_10m",
        )
        if clouds_plot_:
            additional_plot = "clouds"
        else:
            additional_plot = "winds"

        clima = None
        if clima_:
            clima = compute_climatology(
                latitude=loc["latitude"].item(),
                longitude=loc["longitude"].item(),
                variables="temperature_2m",
            )
            # BETA, load the climatology of 850hPa T from  a zarr
            try:
                clima_t850 = compute_climatology_zarr(latitude=loc["latitude"].item(),
                                                      longitude=loc["longitude"].item())
                # Convert clima time to the timezone used for the other data
                # In theory both ensemble data and climatology computed from open-meteo
                clima_t850["time"] = (
                    clima_t850["time"]
                    .dt.tz_localize("UTC")
                    .dt.tz_convert(data.attrs["timezone"])
                )
                clima_t850["doy"] = clima_t850["time"].dt.strftime("%m%d")
                clima_t850["hour"] = clima_t850["time"].dt.hour
                # should share the same timezone, as the parameter is set to auto
                clima = clima.merge(
                    clima_t850.drop(columns=["time"]),
                    left_on=["doy", "hour"],
                    right_on=["doy", "hour"],
                    how="left",
                )
            except Exception as e:
                logging.error(f"Could not add t850hPa climatology {e}")

        sun = find_suntimes(
            df=data,
            latitude=loc["latitude"].item(),
            longitude=loc["longitude"].item(),
            elevation=loc["elevation"].item(),
        )

        loc_label = location[0]["label"].split("|")[0] + (
            f"|📍 {float(data.attrs['longitude']):.1f}E"
            f", {float(data.attrs['latitude']):.1f}N, {float(data.attrs['elevation']):.0f}m)<br>"
            f"<sup>Ens = <b>{model.upper()}</b></sup>"
        )

        return (
            make_subplot_figure(data, clima, loc_label, sun, additional_plot),
            # make_barpolar_figure(data),
            None,
            False,  # deactivate error popup
        )

    except Exception as e:
        logging.error(
            f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}.  Parameters used model={model}, from_now={from_now_}, clima={clima_}, clouds_plot={clouds_plot_}"
        )
        return (
            no_update,
            "An error occurred when processing the data",
            True,  # Error message
        )


# Remove focus from dropdown once an element has been selected
clientside_callback(
    """
    function(value) {
        // Remove focus from the dropdown element
        document.activeElement.blur();
    }
    """,
    Input("models-selection", "value"),
    prevent_initial_call=True,
)
