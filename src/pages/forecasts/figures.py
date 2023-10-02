import dash_bootstrap_components as dbc
from dash import dcc
import plotly.graph_objects as go
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


def make_lineplot_timeseries(df, var, mode='lines+markers'):
    traces = []
    for col in df.columns[df.columns.str.contains(var)]:
        # First do the first 48 hrs
        traces.append(
            go.Scatter(
                x=df.loc[:, 'time'],
                y=df.loc[:, col],
                mode=mode,
                name=col,
                marker=dict(size=5),
                line=dict(width=2),
                showlegend=False),
        )

    return traces


def make_barplot_timeseries(df, var):
    traces = []
    for col in df.columns[df.columns.str.contains(var)]:
        traces.append(
            go.Bar(
                x=df['time'],
                y=df[col],
                name=col,
                opacity=0.6,
                marker=dict(color='rgb(26, 118, 255)'),
                showlegend=False),
        )

    return traces

def make_subplot_figure(data):
    traces_temp = make_lineplot_timeseries(data, 'temperature_2m')
    traces_precipitation = make_barplot_timeseries(data, 'precipitation')
    traces_wind = make_lineplot_timeseries(data, 'windspeed_10m')
    traces_cloud = make_lineplot_timeseries(data, 'cloudcover', mode='markers')

    fig = make_subplots(
        rows=4,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.5, 0.4, 0.3, 0.3])

    for trace_temp in traces_temp:
        fig.add_trace(trace_temp, row=1, col=1)
    for trace_precipitation in traces_precipitation:
        fig.add_trace(trace_precipitation, row=2, col=1)
    for trace_wind in traces_wind:
        fig.add_trace(trace_wind, row=3, col=1)
    for trace_cloud in traces_cloud:
        fig.add_trace(trace_cloud, row=4, col=1)

    fig.update_layout(
        xaxis=dict(showgrid=True,
                   range=[data['time'].min(),
                          data['time'].max()]),
        yaxis=dict(showgrid=True,),
        height=1000,
        margin={"r": 0.1, "t": 0.1, "l": 0.1, "b": 0.1},
        template='plotly_white',
        barmode='overlay'
    )

    fig.update_yaxes(title_text="2m Temp [°C]", row=1, col=1)
    fig.update_yaxes(title_text="Prec. [mm]", row=2, col=1)
    fig.update_yaxes(title_text="Wind. [kph]", row=3, col=1)
    fig.update_yaxes(title_text="Cloud cover [%]", row=4, col=1)
    fig.update_yaxes(showgrid=True, gridwidth=4)
    fig.update_xaxes(minor=dict(ticks="inside", showgrid=True,
                     gridwidth=3), showgrid=True, gridwidth=4)

    return fig

# CARDS for layout


fig_subplots = dbc.Card(
    [
        dcc.Graph(id='forecast-plot')
    ],
    className="mb-2",
)
