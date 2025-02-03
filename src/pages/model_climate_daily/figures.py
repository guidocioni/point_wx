from dash import dcc
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots
import pandas as pd
from utils.settings import images_config
from .options_selector import acc_vars_options, daily_vars_options


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
            line=dict(width=0.1, color="gray"),
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
            fillcolor="rgba(255, 76, 45, 1)",
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
            fillcolor="rgba(99, 178, 207, 1)",
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


# CARDS for layout

fig_prec_climate_daily = dcc.Graph(
    id=dict(type="figure", id="prec-climate-daily"),
    config=images_config,
    className="mb-3 mt-2",
    style={'height':'45vh', 'min-height': '300px'}
)

fig_temp_climate_daily = dcc.Graph(id="temp-climate-daily-figure", config=images_config, style={'height':'45vh', 'min-height': '300px'})
