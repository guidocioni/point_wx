import dash_bootstrap_components as dbc
from dash import dcc
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from plotly.subplots import make_subplots


def make_empty_figure(text="No data (yet 😃)"):
    '''Initialize an empty figure with style and a centered text'''
    fig = go.Figure()

    fig.add_annotation(x=2.5, y=1.5,
                       text=text,
                       showarrow=False,
                       font=dict(size=30))

    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )

    fig.update_layout(
        height=390,
        margin={"r": 0.1, "t": 0.1, "l": 0.1, "b": 0.1},
        template='plotly_white',
    )

    return fig


def make_prec_figure(df, year, var):
    fig = make_subplots()

    fig.add_trace(
        go.Scatter(
            x=df.dummy_date,
            y=df['q1'],
            mode='lines',
            name='5th Percentile',
            line=dict(width=.1, color='gray'),
            showlegend=False,),
    )

    fig.add_trace(
        go.Scatter(
            x=df.dummy_date,
            y=df['q3'],
            mode='lines',
            name='5-95th percentiles range',
            line=dict(width=.1, color='gray'),
            showlegend=True,
            fill='tonexty'),
    )

    fig.add_trace(
        go.Scatter(
            x=df.dummy_date,
            y=df[f'{var}_yearly_acc'],
            mode='lines',
            name=year,
            line=dict(width=3, color='black'),
            showlegend=True,),
    )
    fig.add_trace(
        go.Scatter(
            x=[df.time.max()],
            y=[df[f'{var}_yearly_acc'].max()],
            mode='markers',
            name='Latest',
            marker=dict(size=15, color='black'),
            showlegend=False,),
    )

    fig.add_trace(
        go.Scatter(
            x=df.dummy_date,
            y=df['q2'],
            mode='lines',
            name='50th Percentile',
            line=dict(width=1, color='gray', dash='dash'),
            showlegend=True,),
    )

    fig.update_layout(
        margin={"r": 0.1, "t": 0.1, "l": 0.1, "b": 0.1},
        template='plotly_white',
        barmode='stack',
        legend=dict(orientation='h'),
        yaxis=dict(showgrid=True),
    )

    return fig

# CARDS for layout


fig_prec_climate_daily = dbc.Card(
    [
        dcc.Graph(id='prec-climate-daily-figure')
    ],
    className="mb-2",
)
