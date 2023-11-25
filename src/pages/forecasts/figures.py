import dash_bootstrap_components as dbc
from dash import dcc
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
from utils.settings import images_config, DEFAULT_TEMPLATE


def make_lineplot_timeseries(df, var, models, mode='lines+markers', showlegend=False):
    traces = []
    # Define cyclical colors to be used
    colors = pio.templates[DEFAULT_TEMPLATE]['layout']['colorway'] * 5
    i = 0
    for model in models:
        if len(models) > 1:
            var_model = var + "_" + model
        else:
            var_model = var
        if var_model in df.columns:
            traces.append(
                go.Scatter(
                    x=df.loc[:, 'time'],
                    y=df.loc[:, var_model],
                    mode=mode,
                    name=model,
                    marker=dict(size=5, color=colors[i]),
                    line=dict(width=2, color=colors[i]),
                    showlegend=showlegend),
            )
        i += 1

    return traces


def make_windarrow_timeseries(df, models, var_speed='windgusts_10m', var_dir='winddirection_10m', showlegend=False):
    df = df.resample('3H', on='time').mean().reset_index()
    traces = []
    # Define cyclical colors to be used
    colors = pio.templates[DEFAULT_TEMPLATE]['layout']['colorway'] * 5
    i = 0
    for model in models:
        if len(models) > 1:
            var_speed_model = var_speed + "_" + model
            var_dir_model = var_dir + "_" + model
        else:
            var_speed_model = var_speed
            var_dir_model = var_dir
        if var_speed_model in df.columns and var_dir_model in df.columns:
            traces.append(
                go.Scatter(
                    x=df.loc[:, 'time'],
                    y=df.loc[:, var_speed_model],
                    mode='markers',
                    name=model,
                    marker=dict(size=10, color=colors[i],
                                symbol='arrow',
                                angle=df.loc[:, var_dir_model] - 180.,
                                line=dict(width=1, color="DarkSlateGrey"),
                                ),
                    showlegend=showlegend),
            )
            # we always add to respect the colors order
        i += 1

    return traces


def make_barplot_timeseries(df, var, models):
    traces = []
    # Define cyclical colors to be used
    colors = pio.templates[DEFAULT_TEMPLATE]['layout']['colorway'] * 5
    i = 0
    for model in models:
        if len(models) > 1:
            var_model = var + "_" + model
        else:
            var_model = var
        if var_model in df.columns:
            traces.append(
                go.Bar(
                    x=df['time'],
                    y=df[var_model],
                    name=model,
                    opacity=0.6,
                    marker=dict(color='rgb(26, 118, 255)'),
                    showlegend=False),
            )
            traces.append(
                go.Scatter(
                    x=df.loc[df[var_model] >= 0.1, 'time'],
                    y=df.loc[df[var_model] >= 0.1, var_model],
                    mode='markers',
                    name=model,
                    marker=dict(size=3, color=colors[i]),
                    showlegend=False),
            )
        i += 1

    return traces


def make_subplot_figure(data, models, title=None, sun=None):
    traces_temp = make_lineplot_timeseries(
        data, 'temperature_2m', showlegend=True, models=models)
    traces_precipitation = make_barplot_timeseries(data, 'precipitation', models=models)
    traces_wind = make_lineplot_timeseries(data, 'windgusts_10m', mode='lines', models=models)
    traces_wind_dir = make_windarrow_timeseries(data, models=models)
    traces_cloud = make_lineplot_timeseries(data, 'cloudcover', mode='markers', models=models)

    fig = make_subplots(
        rows=4,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.5, 0.3, 0.3, 0.3])

    for trace_temp in traces_temp:
        fig.add_trace(trace_temp, row=1, col=1)
    for trace_precipitation in traces_precipitation:
        fig.add_trace(trace_precipitation, row=2, col=1)
    for trace_wind in traces_wind:
        fig.add_trace(trace_wind, row=3, col=1)
    for trace_wind_dir in traces_wind_dir:
        fig.add_trace(trace_wind_dir, row=3, col=1)
    for trace_cloud in traces_cloud:
        fig.add_trace(trace_cloud, row=4, col=1)

    fig.update_layout(
        xaxis=dict(showgrid=True,
                   range=[data['time'].min(),
                          data['time'].max()]),
        yaxis=dict(showgrid=True,),
        height=1000,
        margin={"r": 5, "t": 40, "l": 0.1, "b": 0.1},
        barmode='overlay',
        legend=dict(orientation='h', y=-0.04),
    )

    if sun is not None:
        for i, s in sun.iterrows():
            fig.add_vrect(
                x0=s['sunrise'],
                x1=s['sunset'],
                fillcolor="rgba(255, 255, 0, 0.3)",
                layer="below",
                line=dict(width=0),
                row=1, col=1
            )

    fig.update_yaxes(title_text="2m Temp [°C]", row=1, col=1)
    fig.update_yaxes(title_text="Prec. [mm]", row=2, col=1)
    fig.update_yaxes(title_text="Wind Gusts [kph]", row=3, col=1)
    fig.update_yaxes(title_text="Cloud cover [%]", row=4, col=1)
    fig.update_yaxes(showgrid=True, gridwidth=4)
    fig.update_xaxes(minor=dict(ticks="inside", showgrid=True,
                     gridwidth=1),
                     tickformat='%a %d %b\n%H:%M', showgrid=True, gridwidth=4)
    if title is not None:
        fig.update_layout(title_text=title)

    return fig

# CARDS for layout


fig_subplots = dbc.Card(
    [
        dcc.Graph(id='forecast-plot', config=images_config)
    ],
    className="mb-2",
)
