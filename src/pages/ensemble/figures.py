import dash_bootstrap_components as dbc
from dash import dcc
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots
import pandas as pd
from utils.settings import images_config


def make_lineplot_timeseries(df, var, clima=None, break_hours='72H'):
    traces = []
    for col in df.columns[df.columns.str.contains(var)]:
        traces.append(
            go.Scatter(
                x=df.loc[df.time <= df.time.iloc[0] +
                         pd.to_timedelta(break_hours), 'time'],
                y=df.loc[df.time <= df.time.iloc[0] +
                         pd.to_timedelta(break_hours), col],
                mode='lines+markers',
                name=col,
                marker=dict(size=4),
                line=dict(width=1),
                showlegend=False),
        )
    for col in df.columns[df.columns.str.contains(var)]:
        traces.append(
            go.Scatter(
                x=df.loc[df.time >= df.time.iloc[0] +
                         pd.to_timedelta(break_hours), 'time'],
                y=df.loc[df.time >= df.time.iloc[0] +
                         pd.to_timedelta(break_hours), col],
                mode='lines',
                name=col,
                line=dict(width=1),
                showlegend=False),
        )
    # Additional shading
    traces.append(go.Scatter(
        x=df.loc[:, 'time'],
        y=df.loc[:, df.columns.str.contains(var)].min(axis=1),
        mode='lines',
        line=dict(color='rgba(0, 0, 0, 0)'),
        name='Minimum',
        showlegend=False
    ))
    traces.append(go.Scatter(
        x=df.loc[:, 'time'],
        y=df.loc[:, df.columns.str.contains(var)].max(axis=1),
        mode='lines',
        line=dict(color='rgba(0, 0, 0, 0)'),
        fillcolor='rgba(0, 0, 0, 0.1)',
        fill='tonexty',
        name='Maximum',
        showlegend=False
    ))
    if clima is not None:
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
                line=dict(width=4, color='rgba(0, 0, 0, 0.4)', dash='dot'),
                showlegend=False)
        )

    return traces


def make_scatterplot_timeseries(df, var):
    df[f'{var}_mean'] = df.iloc[:, df.columns.str.contains(var)].mean(axis=1)
    traces = []
    for col in df.columns[df.columns.str.contains(var)]:
        traces.append(
            go.Scatter(
                x=df.loc[:, 'time'],
                y=df.loc[:, col],
                mode='markers',
                name=col,
                marker=dict(size=4),
                line=dict(width=1),
                showlegend=False),
        )
    # add line with the average
    traces.append(
        go.Scatter(
            x=df.loc[:, 'time'],
            y=df.loc[:, f'{var}_mean'],
            mode='lines',
            name='Mean',
            line=dict(width=4, color='black'),
            showlegend=False),
    )

    return traces


def make_barplot_timeseries(df, var, color='cadetblue'):
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
        marker_color=color)

    return trace


def make_barpolar_figure(df, n_partitions=15, bins=np.linspace(0, 360, 15)):
    timeSpan = (df.time.iloc[-1]-df.time.iloc[0])
    rule = int((timeSpan.total_seconds()/3600.)/n_partitions)
    subset = df.resample(str(rule)+"H", on='time').first()
    subset = subset.loc[:, subset.columns.str.contains('wind_direction')]

    out = []
    for i, row in subset.iterrows():
        out.append(pd.cut(row.values, bins=bins).value_counts().values)
    # Convert to normalized percentage
    for i, o in enumerate(out):
        out[i] = (o / len(subset.columns)) * 100.
    n_plots = len(out) - 1
    fig = make_subplots(rows=1,
                        cols=n_plots,
                        specs=[[{'type': 'polar'} for _ in range(n_plots)]],
                        horizontal_spacing=0)
    for i in range(n_plots):
        fig.add_trace(go.Barpolar(
            r=out[i-1],
            theta=bins,
            marker_color='rgb(106,81,163)',
            showlegend=False), row=1, col=i+1)
    fig.update_polars(radialaxis_showticklabels=False,
                      angularaxis_showticklabels=False)
    fig.update_layout(margin={"r": 2, "t": 1, "l": 2, "b": 0.1},
                      height=100,
                      )

    return fig


def make_subplot_figure(data, clima, title=None):
    traces_temp = make_lineplot_timeseries(data, 'temperature_2m', clima)
    trace_rain = make_barplot_timeseries(data, 'rain', color='cadetblue')
    trace_snow = make_barplot_timeseries(
        data, 'snowfall', color='rebeccapurple')
    traces_clouds = make_scatterplot_timeseries(data, 'cloudcover')

    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.5, 0.4, 0.3])

    for trace_temp in traces_temp:
        fig.add_trace(trace_temp, row=1, col=1)
    fig.add_trace(trace_rain, row=2, col=1)
    fig.add_trace(trace_snow, row=2, col=1)
    for trace_clouds in traces_clouds:
        fig.add_trace(trace_clouds, row=3, col=1)

    fig.update_layout(
        xaxis=dict(showgrid=True,
                   range=[data['time'].min(),
                          data['time'].max()]),
        yaxis=dict(showgrid=True,),
        height=900,
        margin={"r": 5, "t": 40, "l": 0.1, "b": 0.1},
        template='plotly_white',
        barmode='stack'
    )

    fig.update_yaxes(title_text="2m Temp [°C]", row=1, col=1)
    fig.update_yaxes(
        title_text="Rain [mm] | Snow [cm] | Prob. [%]", row=2, col=1)
    fig.update_yaxes(title_text="Cloud Cover", row=3, col=1)
    fig.update_yaxes(showgrid=True, gridwidth=4)
    fig.update_xaxes(minor=dict(ticks="inside", showgrid=True, gridwidth=3),
                     showgrid=True,
                     gridwidth=4,
                     tickformat='%a %d %b\n%H:%M')
    if title is not None:
        fig.update_layout(title_text=title)

    return fig

# CARDS for layout


fig_subplots = dbc.Card(
    [
        dcc.Graph(id='ensemble-plot', config=images_config)
    ],
    className="mb-2",
)

fig_polar = dbc.Card(
    [
        dcc.Graph(id='polar-plot',
                  config={**images_config, 'displayModeBar': False})
    ],
    className="mb-2",
)
