import dash_bootstrap_components as dbc
from dash import dcc
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots
import pandas as pd


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


def make_lineplot_timeseries(df, clima, var):
    traces = []
    for col in df.columns[df.columns.str.contains(var)]:
        # First do the first 48 hrs
        traces.append(
            go.Scatter(
                x=df.loc[df.time <= df.time.iloc[0] +
                         pd.to_timedelta('48H'), 'time'],
                y=df.loc[df.time <= df.time.iloc[0] +
                         pd.to_timedelta('48H'), col],
                mode='lines+markers',
                name=col,
                marker=dict(size=4),
                line=dict(width=1),
                showlegend=False),
        )
    # Then the remaining as shade
    traces.append(go.Scatter(
        x=df.loc[df.time >= df.time.iloc[0] + pd.to_timedelta('48H'), 'time'],
        y=df.loc[df.time >= df.time.iloc[0] +
                 pd.to_timedelta('48H'), df.columns.str.contains(var)].min(axis=1),
        mode='lines',
        line=dict(color='grey'),
        name='Minimum',
        showlegend=False
    ))
    traces.append(go.Scatter(
        x=df.loc[df.time >= df.time.iloc[0] + pd.to_timedelta('48H'), 'time'],
        y=df.loc[df.time >= df.time.iloc[0] +
                 pd.to_timedelta('48H'), df.columns.str.contains(var)].max(axis=1),
        mode='lines',
        line=dict(color='grey'),
        fill='tonexty',
        name='Maximum',
        showlegend=False
    ))
    # Now add climatology
    df['doy'] = df['time'].dt.strftime("%m%d")
    df['hour'] = df['time'].dt.hour
    clima = clima.merge(df[['doy', 'hour', 'time']],
                        left_on=['doy', 'hour'],
                        right_on=['doy', 'hour'])

    traces.append(
        go.Scatter(
            x=clima['time'],
            y=clima[var],
            mode='lines',
            name='climatology',
            line=dict(width=4, color='rgba(0, 0, 0, 0.2)', dash='dot'),
            showlegend=False)
    )

    return traces


def make_barplot_timeseries(df, var):
    # Do some pre-processing on the precipitation input
    members = len(df.iloc[:, df.columns.str.contains(var)].columns)

    df[f'{var}_prob'] = (((df.iloc[:, df.columns.str.contains(
        var)] >= 0.1).sum(axis=1) / members) * 100.).astype(int)

    df[f'{var}_mean'] = df.iloc[:, df.columns.str.contains(var)].mean(axis=1)

    df.loc[df[f'{var}_prob'] < 5, [f'{var}_prob', f'{var}_mean']] = np.nan

    trace = go.Bar(
        x=df['time'],
        y=df[f'{var}_mean'],
        text=df[f'{var}_prob'],
        name=var,
        textposition='outside',
        showlegend=False,
        marker_color='cadetblue')

    return trace


def make_subplot_figure(data, clima):
    traces_temp = make_lineplot_timeseries(data, clima, 'temperature_2m')
    trace_rain = make_barplot_timeseries(data, 'rain')

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.6, 0.4])

    for trace_temp in traces_temp:
        fig.add_trace(trace_temp, row=1, col=1)
    fig.add_trace(trace_rain, row=2, col=1)

    fig.update_layout(
        xaxis=dict(showgrid=True,
                   range=[data['time'].min(),
                          data['time'].max()]),
        yaxis=dict(showgrid=True,),
        height=800,
        margin={"r": 0.1, "t": 0.1, "l": 0.1, "b": 0.1},
        template='plotly_white',
    )

    fig.update_yaxes(title_text="2m Temp [°C]", row=1, col=1)
    fig.update_yaxes(title_text="Prec. [mm] and prob. [%]", row=2, col=1)
    fig.update_yaxes(showgrid=True, gridwidth=4)
    fig.update_xaxes(minor=dict(ticks="inside", showgrid=True,
                     gridwidth=3), showgrid=True, gridwidth=4)

    return fig

# CARDS for layout


fig_subplots = dbc.Card(
    [
        dcc.Graph(id='ensemble-plot')
    ],
    className="mb-2",
)
