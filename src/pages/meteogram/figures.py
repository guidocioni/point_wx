from dash import dcc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.settings import images_config
from PIL import Image
import pandas as pd


def make_temp_timeseries(df, showlegend=False, clima=None):
    traces = []
    traces.append(
        go.Scatter(
            x=df["time"],
            y=df["t_max_mean"],
            mode="markers+lines+text",
            text=df["t_max_mean"].astype(int).astype(str),
            textposition="top right",
            textfont=dict(color="rgba(227, 56, 30, 1)", size=14),
            name="Maximum temperature",
            hovertemplate="<extra></extra><b>%{x|%a %-d %b}</b>, Max. T = %{y:.1f} °C",
            line=dict(width=2, color="rgba(227, 56, 30, 1)"),
            showlegend=showlegend,
        ),
    )
    traces.append(
        go.Scatter(
            x=df["time"],
            y=df["t_min_mean"],
            mode="markers+lines+text",
            text=df["t_min_mean"].astype(int).astype(str),
            textposition="top right",
            textfont=dict(color="rgba(58, 91, 139, 1)", size=14),
            name="Minimum temperature",
            hovertemplate="<extra></extra><b>%{x|%a %-d %b}</b>, Min. T = %{y:.1f} °C",
            line=dict(width=2, color="rgba(58, 91, 139, 1)"),
            showlegend=showlegend,
        ),
    )
    traces.append(
        go.Scatter(
            x=df["time"],
            y=df["t_min_min"],
            mode="lines",
            line=dict(color="rgba(0, 0, 0, 0)"),
            name="",
            hovertemplate="<extra></extra><b>%{x|%a %-d %b}</b>, Min. T = %{y:.1f} °C",
            showlegend=showlegend,
        )
    )
    traces.append(
        go.Scatter(
            x=df["time"],
            y=df["t_min_max"],
            mode="lines",
            line=dict(color="rgba(0, 0, 0, 0)"),
            fillcolor="rgba(58, 91, 139, 0.2)",
            fill="tonexty",
            name="",
            hovertemplate="<extra></extra><b>%{x|%a %-d %b}</b>, Min. T = %{y:.1f} °C",
            showlegend=showlegend,
        )
    )
    traces.append(
        go.Scatter(
            x=df["time"],
            y=df["t_max_min"],
            mode="lines",
            line=dict(color="rgba(0, 0, 0, 0)"),
            name="",
            hovertemplate="<extra></extra><b>%{x|%a %-d %b}</b>, Max. T = %{y:.1f} °C",
            showlegend=showlegend,
        )
    )
    traces.append(
        go.Scatter(
            x=df["time"],
            y=df["t_max_max"],
            mode="lines",
            line=dict(color="rgba(0, 0, 0, 0)"),
            fillcolor="rgba(227, 56, 30, 0.2)",
            fill="tonexty",
            name="",
            hovertemplate="<extra></extra><b>%{x|%a %-d %b}</b>, Max. T = %{y:.1f} °C",
            showlegend=showlegend,
        )
    )
    if clima is not None:
        df["doy"] = df.time.dt.strftime("%m%d")
        df = df.merge(clima, left_on="doy", right_on="doy")
        traces.append(
            go.Scatter(
                x=df["time"],
                y=df["t_min_clima"],
                mode="markers",
                name="Minimum temperature (clima)",
                hovertemplate="<extra></extra><b>%{x|%a %-d %b}</b>, Min. T (clima) = %{y:.1f} °C",
                marker=dict(
                    color="rgba(58, 91, 139, 0.5)",
                    symbol="diamond-tall",
                    size=12,
                    line=dict(width=0.5, color="rgba(0, 0, 0, 0.5)"),
                ),
                showlegend=showlegend,
            ),
        )
        traces.append(
            go.Scatter(
                x=df["time"],
                y=df["t_max_clima"],
                mode="markers",
                name="Maximum temperature (clima)",
                hovertemplate="<extra></extra><b>%{x|%a %-d %b}</b>, Max. T (clima) = %{y:.1f} °C",
                marker=dict(
                    color="rgba(227, 56, 30, 0.5)",
                    symbol="diamond-tall",
                    size=12,
                    line=dict(width=0.5, color="rgba(0, 0, 0, 0.5)"),
                ),
                showlegend=showlegend,
            ),
        )
    return traces


def make_barplot_timeseries(
    df,
    var,
    var_text=None,
    showlegend=False,
    color="rgb(73, 135, 230)",
    text_formatting="%{text:.1s}",
    clima=None,
    clima_x_shift=0,
):
    if var_text is not None:
        text = df[var_text]
    traces = []
    traces.append(
        go.Bar(
            x=df["time"],
            y=df[var],
            text=text,
            name="",
            textposition="auto",
            texttemplate=text_formatting,
            hovertemplate="<extra></extra><b>%{x|%a %-d %b}</b>, " + var + " = %{y:.1f}",
            showlegend=showlegend,
            marker_color=color,
        )
    )
    if clima is not None:
        df["doy"] = df.time.dt.strftime("%m%d")
        df = df.merge(clima, left_on="doy", right_on="doy")
        traces.append(
            go.Scatter(
                x=df["time"] + clima_x_shift,
                y=df[var.replace("_mean", "_clima")],
                mode="markers",
                name="",
                hovertemplate="<extra></extra><b>%{x|%a %-d %b}</b>, "
                + var
                + " (clima) = %{y:.1f}",
                marker=dict(
                    color=color.replace(", 0.5", ", 0.8"),
                    symbol="diamond-tall",
                    size=12,
                    line=dict(width=0.5, color="rgba(0, 0, 0, 0.5)"),
                ),
                showlegend=showlegend,
            ),
        )

    return traces


def make_subplot_figure(data, title=None, clima=None):
    traces_temp = make_temp_timeseries(data, clima=clima)
    traces_prec = make_barplot_timeseries(
        data,
        clima=clima,
        var="daily_prec_mean",
        var_text="prec_prob",
        color="rgba(73, 135, 230, 1.0)",
        text_formatting="%{text:.0f}%",
        clima_x_shift=-pd.to_timedelta("1h"),
    )
    traces_sun = make_barplot_timeseries(
        data,
        clima=clima,
        var="sunshine_mean",
        var_text="sunshine_mean",
        color="rgba(255, 240, 184, 0.5)",
        text_formatting="%{text:.1f} hrs",
        clima_x_shift=pd.to_timedelta("1h"),
    )

    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.15, 0.5, 0.5],
        subplot_titles=[
            "",
            "<b>Temperature (°C)",
            "<b>Precipitation (mm), Probability (%), Sunshine",
        ],
        specs=[
            [{"secondary_y": False, "r": -0.06}],
            [{"secondary_y": False, "r": -0.06}],
            [{"secondary_y": True, "r": -0.06}],
        ],
    )

    for trace_temp in traces_temp:
        fig.add_trace(trace_temp, row=2, col=1)
    for trace_prec in traces_prec:
        fig.add_trace(trace_prec, row=3, col=1)
    for trace_sun in traces_sun:
        fig.add_trace(trace_sun, row=3, col=1, secondary_y=True)
    for _, row in data.iterrows():
        fig.add_shape(
            type="line",
            yref="y",
            xref="x",
            x0=row["time"],
            y0=row["daily_prec_min"],
            x1=row["time"],
            y1=row["daily_prec_max"],
            line=dict(color="rgba(0,0,0,0.3)", width=2),
            row=3,
            col=1,
        )

    fig.add_trace(
        go.Scatter(
            x=data["time"],
            y=[2.5] * len(data["time"]),
            mode="lines+text",
            text=data["time"].dt.strftime("<b>%a</b><br>%-d-%-m"),
            customdata=data["weather_descriptions"],
            hovertemplate="<extra></extra><b>%{x|%a %-d %b}</b><br>%{customdata}",
            textposition="top center",
            textfont=dict(color="rgba(1, 1, 1, 1)", size=12),
            line=dict(color="rgba(0, 0, 0, 0)"),
            name="",
            showlegend=False,
        ),
        row=1,
        col=1,
    )
    for _, row in data.iterrows():
        if row["icons"] != "":
            fig.add_layout_image(
                dict(
                    source=Image.open(row["icons"]),
                    xref="x",
                    x=row["time"],
                    yref="y",
                    y=1,
                    sizex=12 * 24 * 10 * 60 * 1000,
                    sizey=1.5,
                    xanchor="center",
                    yanchor="bottom",
                ),
                row=1,
                col=1,
            )

    fig.update_layout(
        modebar=dict(orientation="v"),
        dragmode=False,
        xaxis=dict(showgrid=True),
        yaxis=dict(
            showgrid=True,
        ),
        height=800,
        margin={"r": 0.1, "t": 40, "l": 0.1, "b": 0.1},
        barmode="overlay",
        legend=dict(orientation="h", y=-0.04),
    )

    fig.update_yaxes(ticksuffix="", row=2, col=1)
    fig.update_yaxes(ticksuffix="", row=3, col=1)
    fig.update_yaxes(showgrid=True, gridwidth=2, fixedrange=True)
    fig.update_xaxes(
        minor=dict(showgrid=False),
        tickformat="%a %-d %b",
        showgrid=True,
        gridwidth=2,
    )
    fig.update_yaxes(
        showgrid=False,
        row=1,
        col=1,
        minor=dict(showgrid=False),
        range=[1, 6],
        showticklabels=False,
    )
    fig.update_xaxes(showgrid=False, row=1, col=1, minor=dict(showgrid=False))
    fig.update_yaxes(
        row=3,
        col=1,
        range=[18, 0],
        title_text="",
        secondary_y=True,
        showgrid=False,
        showticklabels=False,
    )
    if title is not None:
        fig.update_layout(title=dict(text=title, font=dict(size=14)))

    return fig


# CARDS for layout

fig_subplots = dcc.Graph(id=dict(type="figure", id="meteogram"), config=images_config)
