import dash_bootstrap_components as dbc
from dash import dcc
import plotly.graph_objects as go
import numpy as np
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


def make_lineplot_timeseries(df, var):
    traces = []
    for col in df.columns[df.columns.str.contains(var)]:
        traces.append(
            go.Scatter(
                x=df['time'],
                y=df[col],
                mode='lines',
                name=col,
                showlegend=False),
        )
    
    return traces


def make_barplot_timeseries(df, var):
    # Do some pre-processing on the precipitation input
    members = len(df.iloc[:, df.columns.str.contains(var)].columns)

    df[f'{var}_prob'] = (((df.iloc[:, df.columns.str.contains(
        var)] >= 0.1).sum(axis=1) / members) * 100.).astype(int)

    df[f'{var}_mean'] = df.iloc[:, df.columns.str.contains(var)].mean(axis=1)

    df.loc[df[f'{var}_prob'] < 5, [f'{var}_prob',f'{var}_mean']] = np.nan
    
    trace = go.Bar(
    x=df['time'],
    y=df[f'{var}_mean'],
    text=df[f'{var}_prob'],
    name=var,
    textposition='outside',
    showlegend=False,
    marker_color='cadetblue')

    return trace


def make_subplot_figure(data):
    traces_temp = make_lineplot_timeseries(data, 'temperature_2m')
    trace_rain = make_barplot_timeseries(data, 'rain')

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        row_heights=[0.6, 0.4])
    
    for trace_temp in traces_temp:
        fig.add_trace(trace_temp, row=1, col=1)
    fig.add_trace(trace_rain, row=2, col=1)

    fig.update_layout(
            xaxis=dict(showgrid=True),
            yaxis=dict(showgrid=True, zeroline=True),
            height=800,
            margin={"r": 0.1, "t": 0.1, "l": 0.1, "b": 0.1},
            template='plotly_white',
        )
    
    return fig

# CARDS for layout

fig_subplots = dbc.Card(
    [
        dcc.Graph(id='ensemble-plot')
    ],
    className="mb-2",
    id='ensemble-fig-card'
)

