from dash import dcc
import plotly.express as px
import pandas as pd
from utils.constants import images_config
from utils.figures_utils import add_attribution, blank_figure
from utils.weather_emoji import get_weather_emoji_series
import plotly.graph_objects as go
from copy import deepcopy

def make_heatmap(df, var, title=None):
    # Create readable variable name for hover
    var_display = var.replace("_", " ").title()
    if var in [
        "temperature_2m",
        "temperature_500hPa",
        "temperature_850hPa",
        "temperature_2m_max",
        "temperature_2m_min",
        "dew_point_2m",
        "apparent_temperature",
        "surface_temperature",
    ]:
        cmap = "Turbo"
    elif var in ["cloudcover", "visibility", "cloud_cover_high", "cloud_cover_mid", "cloud_cover_low"]:
        cmap = "YlGnBu_r"
    elif var == "relative_humidity_2m":
        cmap = "YlGnBu"
    elif var in ["rain", "precipitation", "accumulated_precip", "accumulated_liquid"]:
        cmap = "dense"
    elif var in ["snowfall", "snow_depth", "accumulated_snow", "snow_depth_water_equivalent", "snowfall_water_equivalent"]:
        cmap = "Burgyl"
    elif var in [
        "wind_gusts_10m",
        "pressure_msl",
        "wind_speed_10m",
        "cape",
    ]:
        cmap = "Hot_r"
    elif var in ["wind_direction_10m"]:
        cmap = "IceFire"
    elif var == "sunshine_duration":
        cmap = "solar"
    elif var in ["geopotential_height_500hPa", "geopotential_height_850hPa", "freezinglevel_height", "snowfall_height"]:
        cmap = "viridis"
    elif var == "precipitation_type":
        # Custom discrete colormap for precipitation types
        # 1=Rain (blue), 2=Snow (purple), 3=Freezing (red/purple), 4=Hail (orange)
        cmap = [[0, "rgba(0,0,0,0)"],      # NaN/0 = transparent (no precip)
                [0.25, "#2E86DE"],          # 1 = Rain (blue)
                [0.5, "#8B5CF6"],           # 2 = Snow (purple)
                [0.75, "#C53030"],          # 3 = Freezing (red)
                [1.0, "#ED8936"]]           # 4 = Hail (orange)
    else:
        cmap = "RdBu_r"

    columns_regex = rf"{var}$|{var}_member(0[1-9]|[1-9][0-9])$"
    y_positions = list(range(df.loc[:, df.columns.str.match(columns_regex)].shape[1]))

    if var == "precipitation_type":
        # Special handling for categorical precipitation type
        fig = px.imshow(
            df.loc[:, df.columns.str.match(columns_regex)].T,
            x=df["time"],
            y=y_positions,
            text_auto=False,  # Don't show numbers for categories
            aspect="auto",
            color_continuous_scale=cmap,
            origin="lower",
            zmin=0,
            zmax=4,
        )
        # Custom hover template with category names
        hover_text = df.loc[:, df.columns.str.match(columns_regex)].T.map(
            lambda x: {
                1: "Rain",
                2: "Snow",
                3: "Freezing",
                4: "Hail"
            }.get(x, "No precipitation") if not pd.isna(x) else "No precipitation"
        )
        fig.update_traces(
            customdata=hover_text,
            hovertemplate="<extra></extra><b>%{x|%a %-d %b %H:%M}</b><br>Member %{y}<br>Type = %{customdata}"
        )
    elif var != "weather_code":
        fig = px.imshow(
            df.loc[:, df.columns.str.match(columns_regex)].T,
            x=df["time"],
            y=y_positions,
            text_auto=True,
            aspect="auto",
            color_continuous_scale=cmap,
            origin="lower",
        )
        fig.update_traces(
            hovertemplate=f"<extra></extra><b>%{{x|%a %-d %b %H:%M}}</b><br>Member %{{y}}<br>{var_display} = %{{z}}"
        )
    else:
        # Weather code heatmap with unicode emoji (much faster than PNG loop)
        from utils.figures_utils import get_weather_icons

        fig = go.Figure()

        # Get weather code columns for all members
        members_vars = df.loc[:, df.columns.str.match(columns_regex)].columns.to_list()
        n_members = len(members_vars)

        # Adaptive resampling based on data size and number of members
        if df.attrs["request"]["models"] == "icon_d2":
            freq = "2h"
        elif (df.shape[0] > 47) & (df.shape[0] <= 100):
            freq = "6h"
        else:
            freq = "12h"

        # Further decimation for many members to prevent overlap
        if n_members > 30:
            freq = "12h"  # More aggressive for large ensembles

        df = df.resample(freq, on="time").max().reset_index()
        times = df["time"]

        # Adaptive emoji size based on number of members
        if n_members <= 10:
            emoji_size = 24
        elif n_members <= 30:
            emoji_size = 18
        elif n_members <= 50:
            emoji_size = 14
        else:
            emoji_size = 12

        # Add one scatter trace per member row with emoji text
        for i, var in enumerate(members_vars):
            # Get weather descriptions for hover
            df_with_descriptions = get_weather_icons(df.copy(), var=var)

            # Convert weather codes to emoji
            weather_emoji = get_weather_emoji_series(df[var])

            fig.add_trace(
                go.Scatter(
                    x=times,
                    y=[y_positions[i]] * len(times),
                    mode="text",
                    text=weather_emoji,
                    textfont=dict(size=emoji_size),
                    customdata=df_with_descriptions["weather_descriptions"],
                    name="",
                    showlegend=False,
                    hovertemplate="<extra></extra><b>%{x|%a %-d %b %H:%M}</b><br>Member %{y}<br>%{customdata}",
                ),
            )

        fig.update_yaxes(range=[y_positions[0] - 0.5, y_positions[-1] + 0.2])

    fig.update_layout(
        modebar=dict(orientation="v"),
        dragmode=False,
        xaxis=dict(showgrid=True, tickformat="%a %-d %b\n%H:%M"),
        yaxis=dict(
            showgrid=True, fixedrange=True, showticklabels=False, title_text="Members"
        ),
        margin={"r": 5, "t": 40, "l": 5, "b": 5},
        updatemenus=[
            dict(
                type="buttons",
                x=0.5,
                y=-0.05,
                xanchor="center",
                direction="right",
                buttons=[
                    dict(
                        label="24H",
                        method="relayout",
                        args=[
                            {
                                "xaxis.range[0]": df["time"].min()
                                - pd.to_timedelta("0.5h"),
                                "xaxis.range[1]": df["time"].min()
                                + pd.to_timedelta("24.5h"),
                            }
                        ],
                    ),
                    dict(
                        label="48H",
                        method="relayout",
                        args=[
                            {
                                "xaxis.range[0]": df["time"].min()
                                - pd.to_timedelta("0.5h"),
                                "xaxis.range[1]": df["time"].min()
                                + pd.to_timedelta("48.5h"),
                            }
                        ],
                    ),
                    dict(
                        label="Reset",
                        method="relayout",
                        args=[
                            {
                                "xaxis.range[0]": df["time"].min()
                                - pd.to_timedelta("0.5h"),
                                "xaxis.range[1]": df["time"].max()
                                + pd.to_timedelta("0.5h"),
                            }
                        ],
                    ),
                ],
                pad=dict(b=5),
            ),
        ],
    )

    fig.update_coloraxes(showscale=False)
    if title is not None:
        fig.update_layout(
            title=dict(text=title, font=dict(size=14), yref="container", y=0.98)
        )

    return add_attribution(fig)


def make_lineplot(
    df,
    var,
    title=None,
    clima=None,
):
    fig = go.Figure()
    traces = []
    columns_regex = rf"{var}$|{var}_member(0[1-9]|[1-9][0-9])$"

    # Special handling for precipitation_type categorical variable
    if var == "precipitation_type":
        category_names = {
            0: "No precip",
            1: "Rain",
            2: "Snow",
            3: "Freezing",
            4: "Hail"
        }
        for col in df.columns[df.columns.str.match(columns_regex)]:
            # Map numeric values to category names for hover
            hover_text = df.loc[:, col].map(
                lambda x: category_names.get(x, "No precip") if not pd.isna(x) else "No precip"
            )
            traces.append(
                go.Scattergl(
                    x=df.loc[:, "time"],
                    y=df.loc[:, col],
                    mode="lines",
                    name=col,
                    customdata=hover_text,
                    hovertemplate="<extra></extra><b>%{x|%a %-d %b %H:%M}</b>, Type = %{customdata}",
                    line=dict(width=1),
                    showlegend=False,
                ),
            )
    else:
        for col in df.columns[df.columns.str.match(columns_regex)]:
            traces.append(
                go.Scattergl(
                    x=df.loc[:, "time"],
                    y=df.loc[:, col],
                    mode="lines",
                    name=col,
                    hovertemplate="<extra></extra><b>%{x|%a %-d %b %H:%M}</b>, "
                    + var
                    + " = %{y}",
                    line=dict(width=2),
                    showlegend=False,
                ),
            )

    for trace in traces:
        fig.add_trace(trace)

    if clima is not None and var in clima.columns:
        # Match climatology's (doy, hour) rows onto an hourly time axis
        # spanning the actual data's bounds, then add a single overlay trace
        time_sel = pd.DataFrame(
            {
                "time_selection": pd.date_range(
                    df["time"].min(), df["time"].max(), freq="1h", tz=df.attrs["timezone"]
                )
            }
        )
        time_sel["time_selection_str"] = time_sel["time_selection"].dt.strftime(
            "%m%d"
        ) + time_sel["time_selection"].dt.strftime("%H")

        clima = clima.copy()
        clima["doy_hour"] = clima["doy"] + clima["hour"].astype(str).str.zfill(2)
        clima = clima.merge(time_sel, left_on="doy_hour", right_on="time_selection_str")
        clima = (
            clima.drop(columns=["doy_hour", "doy", "hour", "time_selection_str"])
            .sort_values(by="time_selection")
            .rename(columns={"time_selection": "time"})
            .interpolate()
            .round(1)
        )

        fig.add_trace(
            go.Scatter(
                x=clima["time"],
                y=clima[var],
                mode="lines",
                name="ERA5 Climatology",
                line=dict(width=4, color="rgba(0, 0, 0, 0.3)"),
                hovertemplate="<b>%{x|%a %-d %b %H:%M}</b>, " + var + " = %{y}",
                showlegend=False,
            )
        )

    # Special y-axis handling for precipitation_type
    if var == "precipitation_type":
        yaxis_config = dict(
            showgrid=True,
            fixedrange=True,
            tickmode="array",
            tickvals=[0, 1, 2, 3, 4],
            ticktext=["No precip", "Rain", "Snow", "Freezing", "Hail"]
        )
    else:
        yaxis_config = dict(showgrid=True, fixedrange=True)

    fig.update_layout(
        modebar=dict(orientation="v"),
        dragmode=False,
        xaxis=dict(showgrid=True, tickformat="%a %-d %b\n%H:%M"),
        yaxis=yaxis_config,
        margin={"r": 5, "t": 40, "l": 5, "b": 5},
        updatemenus=[
            dict(
                type="buttons",
                x=0.5,
                y=-0.09,
                xanchor="center",
                direction="right",
                buttons=[
                    dict(
                        label="24H",
                        method="relayout",
                        args=[
                            {
                                "xaxis.range[0]": df["time"].min()
                                - pd.to_timedelta("0.5h"),
                                "xaxis.range[1]": df["time"].min()
                                + pd.to_timedelta("24.5h"),
                            }
                        ],
                    ),
                    dict(
                        label="48H",
                        method="relayout",
                        args=[
                            {
                                "xaxis.range[0]": df["time"].min()
                                - pd.to_timedelta("0.5h"),
                                "xaxis.range[1]": df["time"].min()
                                + pd.to_timedelta("48.5h"),
                            }
                        ],
                    ),
                    dict(
                        label="Reset",
                        method="relayout",
                        args=[
                            {
                                "xaxis.range[0]": df["time"].min()
                                - pd.to_timedelta("0.5h"),
                                "xaxis.range[1]": df["time"].max()
                                + pd.to_timedelta("0.5h"),
                            }
                        ],
                    ),
                ],
                pad=dict(b=5),
            ),
        ],
    )
    if title is not None:
        fig.update_layout(
            title=dict(text=title, font=dict(size=14), yref="container", y=0.97)
        )

    return add_attribution(fig)


# CARDS for layout
images_config = deepcopy(images_config)
images_config['toImageButtonOptions'].update({'width': 1200, 'height': 700})
fig_subplots = dcc.Graph(
    id=dict(type="figure", id="ensemble-heatmap"),
    figure=blank_figure(),
    config=images_config,
    style={"height": "90vh", "minHeight": "500px"},
)
