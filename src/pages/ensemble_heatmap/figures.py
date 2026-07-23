from dash import dcc
import plotly.express as px
import pandas as pd
from utils.settings import images_config
from utils.figures_utils import add_attribution
import plotly.graph_objects as go
from copy import deepcopy

def make_heatmap(df, var, title=None):
    if var in [
        "temperature_2m",
        "temperature_850hPa",
        "dew_point_2m",
        "apparent_temperature",
        "surface_temperature",
    ]:
        cmap = "Turbo"
    elif var in ["cloudcover", "visibility"]:
        cmap = "YlGnBu_r"
    elif var == "relative_humidity_2m":
        cmap = "YlGnBu"
    elif var in ["rain", "precipitation", "accumulated_precip", "accumulated_liquid"]:
        cmap = "dense"
    elif var in ["snowfall", "snow_depth", "accumulated_snow"]:
        cmap = "Burgyl"
    elif var in [
        "windgusts_10m",
        "pressure_msl",
        "wind_speed_10m",
        "wind_direction_10m",
        "cape",
    ]:
        cmap = "Hot_r"
    elif var == "sunshine_duration":
        cmap = "solar"
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
            hovertemplate="<extra></extra><b>%{x|%a %-d %b %H:%M}</b><br>%{y}<br>Type = %{customdata}"
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
            hovertemplate="<extra></extra><b>%{x|%a %-d %b %H:%M}</b><br>%{y}<br>Value = %{z}"
        )
    else:
        from PIL import Image
        from utils.figures_utils import get_weather_icons
        import plotly.graph_objects as go

        fig = go.Figure()
        if df.attrs["request"]["models"] == "icon_d2":
            freq = "2h"
        elif (df.shape[0] > 47) & (df.shape[0] <= 100):
            freq = "6h"
        else:
            freq = "12h"
        df = df.resample(freq, on="time").max().reset_index()
        times = df["time"]
        # Loop through members and times to add images dynamically
        members_vars = df.loc[:, df.columns.str.match(columns_regex)].columns.to_list()
        for i, var in enumerate(members_vars):
            # Extract icons for the current model
            df = get_weather_icons(
                df,
                var=var,
            )
            fig.add_trace(
                go.Scatter(
                    x=times,
                    y=[y_positions[i]] * len(times),
                    mode="text",
                    text="",
                    name="",
                    showlegend=False,
                ),
            )
            for _, row in df.iterrows():
                if row["icons"] != "":
                    fig.add_layout_image(
                        dict(
                            source=Image.open(row["icons"]),
                            x=row["time"],
                            y=y_positions[i],
                            sizex=12 * 24 * 10 * 60 * 100,
                            sizey=0.5,
                            xref="x",
                            yref="y",
                            xanchor="center",
                            yanchor="middle",
                            layer="above",
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
                go.Scatter(
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
                go.Scatter(
                    x=df.loc[:, "time"],
                    y=df.loc[:, col],
                    mode="lines",
                    name=col,
                    hovertemplate="<extra></extra><b>%{x|%a %-d %b %H:%M}</b>, "
                    + var
                    + " = %{y}",
                    line=dict(width=1),
                    showlegend=False,
                ),
            )

    for trace in traces:
        fig.add_trace(trace)

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
images_config.update({'toImageButtonOptions': {'width': 1500, 'height': 800}})
fig_subplots = dcc.Graph(
    id=dict(type="figure", id="ensemble-heatmap"),
    config=images_config,
    style={"height": "90vh", "minHeight": "500px"},
)
