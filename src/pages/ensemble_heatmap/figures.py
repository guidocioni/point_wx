import dash_bootstrap_components as dbc
from dash import dcc
import plotly.express as px
import pandas as pd
from utils.settings import images_config


def make_heatmap(df, var, title=None):
    if var in ['temperature_2m', 'temperature_850hPa']:
        cmap = 'RdBu_r'
    elif var == 'cloudcover':
        cmap = 'YlGnBu_r'
    elif var in ['rain', 'precipitation']:
        cmap = 'dense'
    elif var in ['snowfall', 'snow_depth']:
        cmap = 'Burgyl'
    elif var == 'windgusts_10m':
        cmap = 'Hot_r'
    elif var == 'sunshine_duration':
        cmap = 'solar'
    else:
        cmap = 'RdBu_r'

    fig = px.imshow(
        df.loc[:, df.columns.str.contains(var)].T,
        x=df['time'],
        text_auto=True,
        color_continuous_scale=cmap,
        origin='lower')

    fig.update_traces(hovertemplate="<extra></extra><b>%{x|%a %d %b %H:%M}</b><br>%{y}<br>Value = %{z}")

    fig.update_layout(
        xaxis=dict(showgrid=True, tickformat='%a %d %b\n%H:%M'),
        yaxis=dict(showgrid=True, fixedrange=True, showticklabels=False,
                   title_text="Members"),
        height=700,
        margin={"r": 5, "t": 40, "l": 5, "b": 5},
        updatemenus=[
            dict(
                type="buttons",
                x=0.5,
                y=-0.05,
                xanchor='center',
                direction='right',
                buttons=[
                    dict(label="24H",
                         method="relayout",
                         args=[{"xaxis.range[0]": df['time'].min() - pd.to_timedelta('0.5H'),
                                "xaxis.range[1]": df['time'].min() + pd.to_timedelta('24.5H')}]),
                    dict(label="48H",
                         method="relayout",
                         args=[{"xaxis.range[0]": df['time'].min() - pd.to_timedelta('0.5H'),
                                "xaxis.range[1]": df['time'].min() + pd.to_timedelta('48.5H')}]),
                    dict(label="Reset",
                         method="relayout",
                         args=[{"xaxis.range[0]": df['time'].min() - pd.to_timedelta('0.5H'),
                                "xaxis.range[1]": df['time'].max() + pd.to_timedelta('0.5H')}]),
                ],
                pad=dict(b=5),
            ),
        ],
    )

    fig.update_coloraxes(showscale=False)
    if title is not None:
        fig.update_layout(title=dict(text=title, font=dict(size=14)))

    return fig


# CARDS for layout

fig_subplots = dbc.Card(
    [
        dcc.Graph(id='ensemble-plot-heatmap', config=images_config)
    ],
    className="mb-2",
)
