import dash_bootstrap_components as dbc
from dash import dcc
import plotly.graph_objects as go
import plotly.express as px
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
    else:
        cmap = 'RdBu_r'

    fig = px.imshow(
        df.loc[:, df.columns.str.contains(var)].T,
        x=df['time'],
        text_auto=True,
        color_continuous_scale=cmap,
        origin='lower')

    fig.update_traces(hovertemplate="<extra></extra><b>%{x|%a %d %b %H:%M}</b><br>%{y}<br>Value = %{z}")

    fig.update_yaxes(visible=False, showticklabels=False)

    fig.update_layout(
        xaxis=dict(showgrid=True, tickformat='%a %d %b\n%H:%M'),
        yaxis=dict(showgrid=True, fixedrange=True),
        height=700,
        margin={"r": 5, "t": 40, "l": 5, "b": 5},
    )

    fig.update_coloraxes(showscale=False)
    if title is not None:
        fig.update_layout(title_text=title)

    return fig


# CARDS for layout

fig_subplots = dbc.Card(
    [
        dcc.Graph(id='ensemble-plot-heatmap', config=images_config)
    ],
    className="mb-2",
)
