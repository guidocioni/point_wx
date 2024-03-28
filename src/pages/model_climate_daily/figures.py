from dash import dcc
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots
import pandas as pd
from utils.settings import images_config


def make_prec_figure(df, year, var, title=None):
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
            y=df['q2'],
            mode='lines',
            name='50th Percentile',
            line=dict(width=.5, color='gray'),
            showlegend=True,),
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

    if year == pd.to_datetime('now', utc=True).year:
        fig.add_vline(x=pd.to_datetime('now', utc=True),
                      line_width=2, line_dash="dash",
                      line_color="gray")

    fig.update_layout(
        margin={"r": 5, "t": 30, "l": 0.1, "b": 0.1},
        barmode='stack',
        legend=dict(orientation='h'),
        yaxis=dict(showgrid=True,
                   title='Yearly accumulated precipitation [mm]'),
    )
    if title is not None:
        fig.update_layout(title_text=title)

    return fig


def make_temp_figure(df, year, var, title=None):
    fig = make_subplots()

    mask = df[var] > df[f'{var}_clima']

    df['above'] = np.where(
        mask, df[var], df[f'{var}_clima'])
    df['below'] = np.where(
        mask, df[f'{var}_clima'], df[var])

    fig.add_trace(
        go.Scatter(
            x=df['time'],
            y=df[f'{var}_clima'],
            mode='lines',
            line=dict(width=.01),
            showlegend=False),
    )
    fig.add_trace(
        go.Scatter(x=df['time'],
                   y=df['above'],
                   fill='tonexty',
                   name='Hotter',
                   fillcolor='rgba(255, 76, 45, 1)',
                   mode='none')
    )
    fig.add_trace(
        go.Scatter(
            x=df['time'],
            y=df[f'{var}_clima'],
            mode='lines',
            line=dict(width=.01),
            showlegend=False),
    )
    fig.add_trace(
        go.Scatter(x=df['time'],
                   y=df['below'],
                   fill='tonexty',
                   name='Colder',
                   fillcolor='rgba(99, 178, 207, 1)',
                   mode='none')
    )
    fig.add_trace(
        go.Scatter(
            x=df.dummy_date,
            y=df[f'{var}_clima'],
            mode='lines',
            name='Mean',
            line=dict(width=3, color='black'),
            showlegend=True),
    )
    fig.add_trace(
        go.Scatter(
            x=df.dummy_date,
            y=df['q05'],
            mode='lines',
            name='5th Percentile',
            line=dict(width=.1, color='gray'),
            showlegend=False,),
    )
    fig.add_trace(
        go.Scatter(
            x=df.dummy_date,
            y=df['q95'],
            mode='lines',
            name='5-95th percentiles range',
            line=dict(width=.1, color='gray'),
            fillcolor='rgba(0, 0, 0, 0.2)',
            showlegend=True,
            fill='tonexty'),
    )

    if year == pd.to_datetime('now', utc=True).year:
        fig.add_vline(x=pd.to_datetime('now', utc=True),
                      line_width=2, line_dash="dash", line_color="gray")

    fig.update_layout(
        margin={"r": 5, "t": 30, "l": 0.1, "b": 0.1},
        barmode='stack',
        legend=dict(orientation='h'),
        yaxis=dict(showgrid=True, title='Temperature [°C]'),
    )
    if title is not None:
        fig.update_layout(title_text=title)

    return fig


# CARDS for layout

fig_prec_climate_daily = dcc.Graph(id='prec-climate-daily-figure',
                                   config=images_config,
                                   className='mb-3 mt-2')

fig_temp_climate_daily = dcc.Graph(id='temp-climate-daily-figure',
                                   config=images_config)
