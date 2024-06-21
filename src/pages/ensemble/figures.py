from dash import dcc
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots
import pandas as pd
from utils.settings import images_config
from utils.custom_logger import logging, time_this_func


def make_boxplot_timeseries(df, var, clima=None):
    tmp = df.loc[:, df.columns.str.contains(f"{var}|time")].set_index("time")
    traces = []
    for index, row in tmp.iterrows():
        traces.append(
            go.Box(
                x=[index] * len(row),
                y=row,
                showlegend=False,
                boxpoints=False,
                marker_color="gray",
            )
        )

    if clima is not None:
        # Now add climatology
        df["doy"] = df["time"].dt.strftime("%m%d")
        df["hour"] = df["time"].dt.hour
        clima = clima.merge(
            df[["doy", "hour", "time"]],
            left_on=["doy", "hour"],
            right_on=["doy", "hour"],
        )
        clima = clima.sort_values(by="time")
        traces.append(
            go.Scatter(
                x=clima["time"],
                y=clima[var],
                mode="lines",
                name="climatology",
                line=dict(width=4, color="rgba(0, 0, 0, 0.4)", dash="dot"),
                showlegend=False,
            )
        )

    return traces


def make_lineplot_timeseries(df, var, clima=None, break_hours="48h"):
    traces = []
    for col in df.columns[df.columns.str.contains(var)]:
        traces.append(
            go.Scatter(
                x=df.loc[
                    df.time <= df.time.iloc[0] + pd.to_timedelta(break_hours), "time"
                ],
                y=df.loc[
                    df.time <= df.time.iloc[0] + pd.to_timedelta(break_hours), col
                ],
                mode="lines+markers",
                name=col,
                hovertemplate="<extra></extra><b>%{x|%a %d %b %H:%M}</b>, "
                + var
                + " = %{y}",
                marker=dict(size=4),
                line=dict(width=1),
                showlegend=False,
            ),
        )
    for col in df.columns[df.columns.str.contains(var)]:
        traces.append(
            go.Scatter(
                x=df.loc[
                    df.time >= df.time.iloc[0] + pd.to_timedelta(break_hours), "time"
                ],
                y=df.loc[
                    df.time >= df.time.iloc[0] + pd.to_timedelta(break_hours), col
                ],
                mode="lines",
                name=col,
                hovertemplate="<extra></extra><b>%{x|%a %d %b %H:%M}</b>, "
                + var
                + " = %{y}",
                line=dict(width=1),
                showlegend=False,
            ),
        )
    # Additional shading
    traces.append(
        go.Scatter(
            x=df.loc[:, "time"],
            y=df.loc[:, df.columns.str.contains(var)].min(axis=1),
            mode="lines",
            line=dict(color="rgba(0, 0, 0, 0)"),
            hoverinfo="skip",
            showlegend=False,
        )
    )
    traces.append(
        go.Scatter(
            x=df.loc[:, "time"],
            y=df.loc[:, df.columns.str.contains(var)].max(axis=1),
            mode="lines",
            line=dict(color="rgba(0, 0, 0, 0)"),
            fillcolor="rgba(0, 0, 0, 0.1)",
            fill="tonexty",
            hoverinfo="skip",
            showlegend=False,
        )
    )
    if clima is not None:
        # Now add climatology
        df["doy"] = df["time"].dt.strftime("%m%d")
        df["hour"] = df["time"].dt.hour
        clima = clima.merge(
            df[["doy", "hour", "time"]],
            left_on=["doy", "hour"],
            right_on=["doy", "hour"],
        )
        clima = clima.sort_values(by="time")

        traces.append(
            go.Scatter(
                x=clima["time"],
                y=clima[var],
                mode="lines",
                name="climatology",
                line=dict(width=4, color="rgba(0, 0, 0, 0.4)", dash="dot"),
                hovertemplate="<b>%{x|%a %d %b %H:%M}</b>, " + var + " = %{y}",
                showlegend=False,
            )
        )

    return traces


def make_scatterplot_timeseries(df, var):
    df[f"{var}_mean"] = df.iloc[:, df.columns.str.contains(var)].mean(axis=1)
    traces = []
    for col in df.columns[df.columns.str.contains(var)]:
        traces.append(
            go.Scatter(
                x=df.loc[:, "time"],
                y=df.loc[:, col],
                mode="markers",
                name=col,
                marker=dict(size=4),
                line=dict(width=1),
                hovertemplate="<extra></extra><b>%{x|%a %d %b %H:%M}</b>, "
                + var
                + " = %{y:.1f}",
                showlegend=False,
            ),
        )
    # add line with the average
    traces.append(
        go.Scatter(
            x=df.loc[:, "time"],
            y=df.loc[:, f"{var}_mean"],
            mode="lines",
            name="Mean",
            line=dict(width=4, color="black"),
            hovertemplate="<b>%{x|%a %d %b %H:%M}</b>, " + var + " = %{y}",
            showlegend=False,
        ),
    )

    return traces


def make_barplot_timeseries(df, var, color="cadetblue"):
    # Do some pre-processing on the precipitation input
    members = len(df.iloc[:, df.columns.str.contains(var)].columns)

    df[f"{var}_prob"] = (
        ((df.iloc[:, df.columns.str.contains(var)] >= 0.1).sum(axis=1) / members)
        * 100.0
    ).astype(int)

    df[f"{var}_mean"] = df.iloc[:, df.columns.str.contains(var)].mean(axis=1)

    df.loc[df[f"{var}_prob"] < 5, [f"{var}_prob", f"{var}_mean"]] = np.nan

    trace = go.Bar(
        x=df["time"],
        y=df[f"{var}_mean"],
        text=df[f"{var}_prob"],
        name=var,
        textposition="outside",
        hovertemplate="<extra></extra><b>%{x|%a %d %b %H:%M}</b>, "
        + var
        + " = %{y:.1f}",
        showlegend=False,
        width=(df["time"].diff().dt.seconds * 850).bfill().ffill(),
        marker_color=color,
    )

    return trace


def make_barpolar_figure(df, n_partitions=15, bins=np.linspace(0, 360, 15)):
    timeSpan = df.time.iloc[-1] - df.time.iloc[0]
    rule = int((timeSpan.total_seconds() / 3600.0) / n_partitions)
    subset = df.resample(str(rule) + "H", on="time").first()
    subset = subset.loc[:, subset.columns.str.contains("wind_direction")]

    out = []
    for i, row in subset.iterrows():
        out.append(pd.cut(row.values, bins=bins).value_counts().values)
    # Convert to normalized percentage
    for i, o in enumerate(out):
        out[i] = (o / len(subset.columns)) * 100.0
    n_plots = len(out) - 1
    fig = make_subplots(
        rows=1,
        cols=n_plots,
        specs=[[{"type": "polar"} for _ in range(n_plots)]],
        horizontal_spacing=0,
    )
    for i in range(n_plots):
        fig.add_trace(
            go.Barpolar(
                r=out[i - 1],
                theta=bins,
                marker_color="rgb(106,81,163)",
                showlegend=False,
                hoverinfo="skip",
            ),
            row=1,
            col=i + 1,
        )
    fig.update_polars(radialaxis_showticklabels=False, angularaxis_showticklabels=False)
    fig.update_layout(
        margin={"r": 2, "t": 1, "l": 2, "b": 0.1}, height=100, dragmode=False
    )

    return fig


@time_this_func
def make_subplot_figure(data, clima=None, title=None, sun=None):
    traces_temp = make_lineplot_timeseries(
        data, "temperature_2m", clima, break_hours="12h"
    )
    # traces_temp = make_boxplot_timeseries(data, 'temperature_2m', clima)
    height_graph = 0.0
    subplot_title = ""
    if len(data.loc[:, data.columns.str.contains("temperature_850hPa")].dropna() > 0):
        traces_temp_850 = make_lineplot_timeseries(
            data, "temperature_850hPa", break_hours="0h"
        )
        height_graph = 0.4
        subplot_title = "850hPa T"
    trace_rain = make_barplot_timeseries(data, "rain", color="cadetblue")
    trace_snow = make_barplot_timeseries(data, "snowfall", color="rebeccapurple")
    traces_clouds = make_scatterplot_timeseries(data, "cloudcover")

    fig = make_subplots(
        rows=4,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=[
            "",
            subplot_title,
            "Rain [mm] | Snow [cm] | Prob. [%]",
            "Clouds [%]",
        ],
        row_heights=[0.35, height_graph, 0.3, 0.25],
    )

    for trace_temp in traces_temp:
        fig.add_trace(trace_temp, row=1, col=1)
    if len(data.loc[:, data.columns.str.contains("temperature_850hPa")].dropna() > 0):
        for trace_temp_850 in traces_temp_850:
            fig.add_trace(trace_temp_850, row=2, col=1)
    fig.add_trace(trace_rain, row=3, col=1)
    fig.add_trace(trace_snow, row=3, col=1)
    for trace_clouds in traces_clouds:
        fig.add_trace(trace_clouds, row=4, col=1)

    fig.update_layout(
        modebar=dict(orientation="v"),
        dragmode=False,
        height=800,
        margin={"r": 5, "t": 40, "l": 0.1, "b": 0.1},
        barmode="stack",
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
                                "xaxis.range[0]": data["time"].min()
                                - pd.to_timedelta("2h"),
                                "xaxis.range[1]": data["time"].min()
                                + pd.to_timedelta("25h"),
                            }
                        ],
                    ),
                    dict(
                        label="48H",
                        method="relayout",
                        args=[
                            {
                                "xaxis.range[0]": data["time"].min()
                                - pd.to_timedelta("2h"),
                                "xaxis.range[1]": data["time"].min()
                                + pd.to_timedelta("49h"),
                            }
                        ],
                    ),
                    dict(
                        label="Reset",
                        method="relayout",
                        args=[
                            {
                                "xaxis.range[0]": data["time"].min()
                                - pd.to_timedelta("1h"),
                                "xaxis.range[1]": data["time"].max()
                                + pd.to_timedelta("1h"),
                            }
                        ],
                    ),
                ],
                pad=dict(b=5),
            ),
        ],
    )

    if sun is not None:
        for _, s in sun.iterrows():
            fig.add_vrect(
                x0=s["sunrise"],
                x1=s["sunset"],
                fillcolor="rgba(255, 255, 0, 0.3)",
                layer="below",
                line=dict(width=0),
                row=1,
                col=1,
            )

    fig.update_yaxes(
        ticksuffix="°C",
        row=1,
        col=1,
        zeroline=True,
        zerolinewidth=4,
        zerolinecolor="rgba(0,0,0,0.2)",
    )
    fig.update_yaxes(
        ticksuffix="°C",
        row=2,
        col=1,
        zeroline=True,
        zerolinewidth=4,
        zerolinecolor="rgba(0,0,0,0.2)",
    )
    fig.update_yaxes(
        row=3,
        col=1,
        range=[0, (data["rain_mean"].max() + data["snowfall_mean"].max()) * 1.2],
    )
    fig.update_yaxes(range=[0, 100], row=4, col=1)
    # we need to re-set it here otherwise it only applies to the first plot
    fig.update_yaxes(showgrid=True, gridwidth=4)
    fig.update_xaxes(
        showgrid=True,
        gridwidth=4,
        range=[
            data["time"].min() - pd.to_timedelta("1h"),
            data["time"].max() + pd.to_timedelta("1h"),
        ],
        tickformat="%a %d %b\n%H:%M",
        minor=dict(ticks="inside", gridwidth=3),
    )
    if title is not None:
        fig.update_layout(title=dict(text=title, font=dict(size=14)))

    return fig


# Figures for layout


fig_subplots = dcc.Graph(id=dict(type="figure", id="ensemble"), config=images_config)
# fig_polar = dcc.Graph(id='polar-plot',
#                       config={**images_config, 'displayModeBar': False})
