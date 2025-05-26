import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots
import pandas as pd
from .options_selector import acc_vars_options, daily_vars_options
from utils.custom_logger import logging


def make_acc_figure(df, year, var, title=None):
    fig = make_subplots()

    fig.add_trace(
        go.Scatter(
            x=df.dummy_date,
            y=df["q1"],
            mode="lines",
            name="5th Percentile",
            line=dict(width=0, color="gray"),
            showlegend=False,
            hoverinfo="skip"
        ),
    )

    fig.add_trace(
        go.Scatter(
            x=df.dummy_date,
            y=df["q3"],
            mode="lines",
            name="5-95th percentiles range",
            line=dict(width=0, color="gray"),
            showlegend=True,
            fill="tonexty",
        ),
    )

    fig.add_trace(
        go.Scatter(
            x=df.dummy_date,
            y=df["q2"],
            mode="lines",
            name="50th Percentile",
            line=dict(width=0.5, color="gray"),
            showlegend=True,
        ),
    )

    fig.add_trace(
        go.Scatter(
            x=df.dummy_date,
            y=df[f"{var}_yearly_acc"],
            mode="lines",
            name=year,
            line=dict(width=3, color="black"),
            showlegend=True,
        ),
    )

    if year == pd.to_datetime("now", utc=True).year:
        try:
            fig.add_vline(
                x=pd.to_datetime("now", utc=True),
                line_width=2,
                line_dash="dash",
                line_color="rgba(1, 1, 1, 0.2)",
            )
            fig.add_annotation(
                x=pd.to_datetime("now", utc=True) - pd.to_timedelta('2.5 day'),
                y=0.01, text='TODAY', showarrow=False, textangle=-90,
                xref='x', yref='y domain', yanchor='bottom', xanchor='center',
                font=dict(size=13, color='rgba(1, 1, 1, 0.3)'),
            )
            # Add circular marker at current time
            current_value = df[df['time'] == pd.to_datetime("now").normalize()][f"{var}_yearly_acc"].item()
            fig.add_trace(
                go.Scatter(
                    x=[pd.to_datetime("now", utc=True)],
                    y=[current_value],
                    mode='markers',
                    marker=dict(size=10, color='black'),
                    showlegend=False,
                    hoverinfo='y'
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=df.dummy_date,
                    y=df[f"{var}_min_yearly_acc"],
                    mode="lines",
                    name="Forecast q15",
                    line=dict(width=0, color="red"),
                    showlegend=False,
                    hoverinfo="skip"
                ),
            )

            fig.add_trace(
                go.Scatter(
                    x=df.dummy_date,
                    y=df[f"{var}_max_yearly_acc"],
                    mode="lines",
                    name="Forecast q95",
                    line=dict(width=0, color="red"),
                    showlegend=False,
                    fill="tonexty",
                ),
            )
        except Exception as e:
            logging.error(
                f"Cannot add forecast data: {type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}"
            )

    fig.update_layout(
        modebar=dict(orientation="v"),
        dragmode=False,
        margin={"r": 5, "t": 50, "l": 0.1, "b": 0.1},
        barmode="stack",
        legend=dict(orientation="h"),
        yaxis=dict(showgrid=True, title=next(item["label"] for item in acc_vars_options if item["value"] == var),
                   zeroline=True, zerolinewidth=4, autorange='min'),
    )
    if title is not None:
        fig.update_layout(title=dict(text=title, font=dict(size=14), yref='container', y=0.97))

    return fig


def make_daily_figure(df, year, var, title=None):
    fig = make_subplots()

    mask = df[var] > df[f"{var}_clima"]

    df["above"] = np.where(mask, df[var], df[f"{var}_clima"])
    df["below"] = np.where(mask, df[f"{var}_clima"], df[var])

    color_above = "rgba(255, 76, 45, 1)"
    color_below = "rgba(99, 178, 207, 1)"
    if var in [
        "pressure_msl_mean",
        "cloud_cover_mean",
        "relative_humidity_2m_mean",
        "soil_moisture_0_to_7cm_mean",
        "soil_moisture_7_to_28cm_mean",
        "soil_moisture_28_to_100cm_mean",
    ]:
        color_above = "rgba(99, 178, 255, 1)"  # light blue
        color_below = "rgba(205, 133, 63, 1)"  # light brown

    fig.add_trace(
        go.Scatter(
            x=df["time"],
            y=df[f"{var}_clima"],
            mode="lines",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip"
        ),
    )
    fig.add_trace(
        go.Scatter(
            x=df["time"],
            y=df["above"],
            fill="tonexty",
            name="Above average",
            fillcolor=color_above,
            mode="none",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["time"],
            y=df[f"{var}_clima"],
            mode="lines",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip"
        ),
    )
    fig.add_trace(
        go.Scatter(
            x=df["time"],
            y=df["below"],
            fill="tonexty",
            name="Below Average",
            fillcolor=color_below,
            mode="none",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df.dummy_date,
            y=df[f"{var}_clima"],
            mode="lines",
            name="Clima",
            line=dict(width=3, color="black"),
            showlegend=True,
        ),
    )
    fig.add_trace(
        go.Scatter(
            x=df.dummy_date,
            y=df["q05"],
            mode="lines",
            name="5th Percentile",
            line=dict(width=0, color="gray"),
            showlegend=False,
            hoverinfo="skip"
        ),
    )
    fig.add_trace(
        go.Scatter(
            x=df.dummy_date,
            y=df["q95"],
            mode="lines",
            name="5-95th percentiles range",
            line=dict(width=0, color="gray"),
            fillcolor="rgba(0, 0, 0, 0.2)",
            showlegend=True,
            fill="tonexty",
        ),
    )

    if year == pd.to_datetime("now", utc=True).year:
        current_value = df[df['time'] == pd.to_datetime("now").normalize()][var].item()
        fig.add_trace(
            go.Scatter(
                x=[pd.to_datetime("now", utc=True)],
                y=[current_value],
                mode='markers',
                marker=dict(size=10, color='black'),
                showlegend=False,
                hoverinfo='y'
            )
        )
        fig.add_vline(
            x=pd.to_datetime("now", utc=True),
            line_width=2,
            line_dash="dash",
            line_color="rgba(1, 1, 1, 0.2)",
        )
        fig.add_annotation(
            x=pd.to_datetime("now", utc=True) - pd.to_timedelta('2.5 day'),
            y=0.01, text='TODAY', showarrow=False, textangle=-90,
            xref='x', yref='y domain', yanchor='bottom', xanchor='center',
            font=dict(size=13, color='rgba(1, 1, 1, 0.3)'),
        )

    fig.update_layout(
        modebar=dict(orientation="v"),
        dragmode=False,
        margin={"r": 5, "t": 30, "l": 0.1, "b": 0.1},
        barmode="stack",
        legend=dict(orientation="h"),
        yaxis=dict(showgrid=True, title=next(item["label"] for item in daily_vars_options if item["value"] == var), autorange="min",
                   zeroline=True, zerolinewidth=4),
    )
    if title is not None:
        fig.update_layout(title=dict(text=title, font=dict(size=14), yref='container', y=0.97))

    return fig
