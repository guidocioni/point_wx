from dash import dcc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.settings import images_config
from utils.figures_utils import add_attribution
from PIL import Image
import pandas as pd

# Beaufort-style wind speed/gust color scale (km/h), mapped over cmin=0/cmax=100
WIND_COLORSCALE = [
    [0.00, "#80d4ff"],
    [0.15, "#5cd65c"],
    [0.30, "#c8e639"],
    [0.45, "#ffeb3b"],
    [0.60, "#ff9800"],
    [0.75, "#f44336"],
    [0.90, "#9c27b0"],
    [1.00, "#4a0072"],
]


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
            hovertemplate="<extra></extra><b>%{x|%a %-d %b}</b>, Max. Temp. (average) = %{y:.1f} °C",
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
            hovertemplate="<extra></extra><b>%{x|%a %-d %b}</b>, Min. Temp. (average) = %{y:.1f} °C",
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
            hovertemplate="<extra></extra><b>%{x|%a %-d %b}</b>, Min. Temp. (Minimum) = %{y:.1f} °C",
            showlegend=showlegend,
        )
    )
    traces.append(
        go.Scatter(
            x=df["time"],
            y=df["t_min_max"],
            mode="lines",
            line=dict(color="rgba(0, 0, 0, 0)"),
            fillcolor="rgba(58, 91, 139, 0.1)",
            fill="tonexty",
            name="",
            hovertemplate="<extra></extra><b>%{x|%a %-d %b}</b>, Min. Temp. (Maximum) = %{y:.1f} °C",
            showlegend=showlegend,
        )
    )
    traces.append(
        go.Scatter(
            x=df["time"],
            y=df["t_min_q25"],
            mode="lines",
            line=dict(color="rgba(0, 0, 0, 0)"),
            name="",
            hovertemplate="<extra></extra><b>%{x|%a %-d %b}</b>, Min. Temp. (25th quantile) = %{y:.1f} °C",
            showlegend=showlegend,
        )
    )
    traces.append(
        go.Scatter(
            x=df["time"],
            y=df["t_min_q75"],
            mode="lines",
            line=dict(color="rgba(0, 0, 0, 0)"),
            fillcolor="rgba(58, 91, 139, 0.2)",
            fill="tonexty",
            name="",
            hovertemplate="<extra></extra><b>%{x|%a %-d %b}</b>, Min. Temp. (75th quantile) = %{y:.1f} °C",
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
            hovertemplate="<extra></extra><b>%{x|%a %-d %b}</b>, Max. Temp. (Minimum) = %{y:.1f} °C",
            showlegend=showlegend,
        )
    )
    traces.append(
        go.Scatter(
            x=df["time"],
            y=df["t_max_max"],
            mode="lines",
            line=dict(color="rgba(0, 0, 0, 0)"),
            fillcolor="rgba(227, 56, 30, 0.1)",
            fill="tonexty",
            name="",
            hovertemplate="<extra></extra><b>%{x|%a %-d %b}</b>, Max. Temp. (Maximum) = %{y:.1f} °C",
            showlegend=showlegend,
        )
    )
    traces.append(
        go.Scatter(
            x=df["time"],
            y=df["t_max_q25"],
            mode="lines",
            line=dict(color="rgba(0, 0, 0, 0)"),
            name="",
            hovertemplate="<extra></extra><b>%{x|%a %-d %b}</b>, Max. Temp. (25th quantile) = %{y:.1f} °C",
            showlegend=showlegend,
        )
    )
    traces.append(
        go.Scatter(
            x=df["time"],
            y=df["t_max_q75"],
            mode="lines",
            line=dict(color="rgba(0, 0, 0, 0)"),
            fillcolor="rgba(227, 56, 30, 0.2)",
            fill="tonexty",
            name="",
            hovertemplate="<extra></extra><b>%{x|%a %-d %b}</b>, Max. Temp. (75th quantile) = %{y:.1f} °C",
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
    textposition="auto",
    outside_on_zero=False,
    clima=None,
    clima_x_shift=0,
    show_clima=True,
    bar_x_shift=pd.to_timedelta(0),
    bar_width=None,
):
    if var_text is not None:
        text = df[var_text]
    if outside_on_zero:
        textposition = ["inside" if v > 0 else "outside" for v in df[var]]

    # For bars with zero values, we need to ensure text is visible by setting a minimal y position
    y_values = df[var].copy()
    if outside_on_zero:
        # Set a small positive value for zero bars so the "outside" text has a base to sit on
        y_values = [v if v > 0 else 0.01 for v in y_values]

    traces = []
    traces.append(
        go.Bar(
            x=df["time"] + bar_x_shift,
            y=y_values,
            width=bar_width,
            text=text,
            name="",
            textposition=textposition,
            texttemplate=text_formatting,
            showlegend=showlegend,
            marker_color=color,
            zorder=2,
            # Make sure zero values still show as 0 in hover, not 0.01
            customdata=df[var],
            hovertemplate="<extra></extra><b>%{x|%a %-d %b}</b>, " + var + " = %{customdata:.1f}",
        )
    )
    if clima is not None and show_clima:
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
                zorder=1,
            ),
        )

    return traces


def make_subplot_figure(data, title=None, clima=None):
    traces_temp = make_temp_timeseries(data, clima=clima)
    traces_prec = make_barplot_timeseries(
        data,
        clima=clima,
        show_clima=False,
        var="daily_prec_mean",
        var_text="prec_prob",
        color="rgba(73, 135, 230, 1.0)",
        text_formatting="%{text:.0f}%",
    )
    traces_sun = make_barplot_timeseries(
        data,
        clima=clima,
        var="sunshine_mean",
        var_text="sunshine_mean",
        color="rgba(255, 240, 184, 0.5)",
        text_formatting="%{text:.1f} hrs",
        outside_on_zero=True,
        clima_x_shift=pd.to_timedelta("1h"),
    )

    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.17, 0.48, 0.5],
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
    cap_halfwidth = pd.to_timedelta("2h")
    whisker_line = dict(color="rgba(0,0,0,0.3)", width=2)
    for _, row in data.iterrows():
        if row["daily_prec_max"] <= 0:
            continue
        fig.add_shape(
            type="line",
            yref="y",
            xref="x",
            x0=row["time"],
            y0=row["daily_prec_min"],
            x1=row["time"],
            y1=row["daily_prec_max"],
            line=whisker_line,
            row=3,
            col=1,
        )
        if row["daily_prec_min"] > 0:
            fig.add_shape(
                type="line",
                yref="y",
                xref="x",
                x0=row["time"] - cap_halfwidth,
                y0=row["daily_prec_min"],
                x1=row["time"] + cap_halfwidth,
                y1=row["daily_prec_min"],
                line=whisker_line,
                row=3,
                col=1,
            )
        fig.add_shape(
            type="line",
            yref="y",
            xref="x",
            x0=row["time"] - cap_halfwidth,
            y0=row["daily_prec_max"],
            x1=row["time"] + cap_halfwidth,
            y1=row["daily_prec_max"],
            line=whisker_line,
            row=3,
            col=1,
        )

    fig.add_trace(
        go.Scatter(
            x=data["time"],
            y=data["daily_prec_mean"],
            mode="text",
            text=data["snow_prob"].apply(lambda p: f"❄ {p:.0f}%" if p > 0 else ""),
            textposition="top center",
            textfont=dict(color="rgba(90,90,200,1)", size=11),
            name="",
            hoverinfo="skip",
            showlegend=False,
        ),
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

    # Wind direction arrow, colored by gust intensity (Beaufort-style banding)
    wind_y = 0.0
    fig.add_trace(
        go.Scatter(
            x=data["time"],
            y=[wind_y] * len(data["time"]),
            mode="markers",
            name="Dominant direction",
            marker=dict(
                size=18,
                symbol="arrow-wide",
                angle=data["wind_direction_10m_dominant"] - 180.0,
                color=data["wind_gusts_10m_max"],
                colorscale=WIND_COLORSCALE,
                cmin=0,
                cmax=100,
                line=dict(width=0.5, color="DarkSlateGrey"),
                showscale=False,
            ),
            customdata=data[
                [
                    "wind_direction_10m_dominant",
                    "wind_speed_min",
                    "wind_speed_max",
                    "wind_gusts_min",
                    "wind_gusts_max",
                ]
            ].values,
            hovertemplate=(
                "<extra></extra>Dominant wind direction = %{customdata[0]:.0f}°"
                "<br>Wind speed = %{customdata[1]:.0f}-%{customdata[2]:.0f} km/h"
                "<br>Wind gusts = %{customdata[3]:.0f}-%{customdata[4]:.0f} km/h"
            ),
            showlegend=False,
        ),
        row=1,
        col=1,
    )

    # Predictability index icons - positioned to the right of weather icons
    def get_predictability_icon(category):
        icons = {
            'high': '🎯',
            'medium': '⚠️',
            'low': '❓'
        }
        return icons.get(category, '')

    # Shift right by 5 hours to place icons next to weather icons
    x_offset = pd.to_timedelta("5h")
    predictability_y = 1.7
    fig.add_trace(
        go.Scatter(
            x=data["time"] + x_offset,
            y=[predictability_y] * len(data["time"]),
            mode="text",
            text=data["predictability_category"].apply(get_predictability_icon),
            textposition="middle center",
            textfont=dict(size=14),
            name="Predictability",
            customdata=data[["predictability_score", "predictability_category"]].values,
            hovertemplate=(
                "<extra></extra><b>%{x|%a %-d %b}</b>"
                "<br>Predictability: %{customdata[1]} (%{customdata[0]}/100)"
            ),
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
        margin={"r": 0.1, "t": 10, "l": 0.1, "b": 0.1},
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
        range=[-0.9, 6],
        showticklabels=False,
        zeroline=False
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
        fig.update_layout(title=dict(text=title, font=dict(size=14), yref='container', y=0.98))

    return add_attribution(fig)


# CARDS for layout

fig_subplots = dcc.Graph(id=dict(type="figure", id="meteogram"), config=images_config, style={'height':'90vh', 'minHeight': '650px'})