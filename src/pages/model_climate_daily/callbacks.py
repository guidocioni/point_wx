from dash import callback, Output, Input, State, no_update, clientside_callback, dcc
import dash_bootstrap_components as dbc
from utils.openmeteo_api import compute_yearly_accumulation, compute_yearly_comparison
from utils.custom_logger import logging
from .figures import make_acc_figure, make_daily_figure
import pandas as pd
from io import StringIO
from datetime import date
from utils.settings import images_config


@callback(
    [
        Output("prec-climate-daily-container", "children"),
        Output("temp-climate-daily-container", "children"),
        Output("error-message", "children", allow_duplicate=True),
        Output("error-modal", "is_open", allow_duplicate=True),
    ],
    Input({"type": "submit-button", "index": "daily"}, "n_clicks"),
    [
        State("locations-list", "data"),
        State("location-selected", "data"),
        State("models-selection-climate-daily", "value"),
        State("year-selection-climate", "value"),
        State("acc-variable-selection-daily", "value"),
        State("inst-variable-selection-daily", "value"),
    ],
    prevent_initial_call=True,
)
def generate_figure(n_clicks, locations, location, model, year, acc_var, inst_var):
    if n_clicks is None:
        return no_update, no_update, no_update, no_update

    if model == "cerra" and ((year > 2021) or (year < 1985)):
        return (
            no_update,
            no_update,
            "The reanalysis model CERRA only covers dates up to 2021!",
            True,
        )

    # unpack locations data
    locations = pd.read_json(StringIO(locations), orient="split", dtype={"id": str})
    loc = locations[locations["id"] == location[0]["value"]]
    loc_label = location[0]["label"].split("|")[0] + (
        f"| {float(loc['longitude'].item()):.1f}E"
        f", {float(loc['latitude'].item()):.1f}N, {float(loc['elevation'].item()):.0f}m)<br>"
        f"<sup>Model = <b>{model.upper()}</b> | Year = <b>{year}</b></sup>"
    )

    try:
        data = compute_yearly_accumulation(
            latitude=loc["latitude"].item(),
            longitude=loc["longitude"].item(),
            model=model,
            var=acc_var,
            year=year,
        )

        data_2 = compute_yearly_comparison(
            latitude=loc["latitude"].item(),
            longitude=loc["longitude"].item(),
            model=model,
            var=inst_var,
            year=year,
        )

        fig_prec = make_acc_figure(
            data, year=year, var=acc_var, title=loc_label
        )
        fig_temp = make_daily_figure(
            data_2, year=year, var=inst_var, title=loc_label
        )

        graph_prec = dcc.Graph(
                            id=dict(type="figure", id="prec-climate-daily"),
                            figure=fig_prec,
                            config=images_config,
                            style={'height':'45vh', 'minHeight':'300px'}
                        )

        graph_temp = dcc.Graph(
                            figure=fig_temp,
                            config=images_config,
                            style={'height':'45vh', 'minHeight':'300px'}
                        )


        return graph_prec, graph_temp, None, False

    except Exception as e:
        logging.error(
            f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}. Parameters used model={model}, year={year}"
        )
        return no_update, no_update, "An error occurred when processing the data", True


@callback(
    [
        Output("year-selection-climate", "value"),
        Output("year-selection-climate", "max"),
    ],
    Input("year-selection-climate", "id"),
)
def update_max_date(_):
    return date.today().year, date.today().year


# Disable some models
@callback(
    [
        Output("models-selection-climate-daily", "data"),
    ],
    Input("year-selection-climate", "id"),
    State("models-selection-climate-daily", "data"),
)
def disable_models(_, models):
    for model in models:
        if model["value"] in ["ecmwf_ifs", "era5_land"]:
            model["disabled"] = True
        else:
            model["disabled"] = False
    return [models]


clientside_callback(
    """
    function(value) {
        // Remove focus from the dropdown element
        document.activeElement.blur();
    }
    """,
    Input("models-selection-climate-daily", "value"),
    prevent_initial_call=True,
)
