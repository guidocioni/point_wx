import dash_bootstrap_components as dbc
from dash import dcc
import plotly.graph_objects as go
import plotly.express as px
from utils.settings import images_config


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


def make_heatmap(df, var, title=None):
    if var == 'temperature_2m':
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

    fig.update_yaxes(visible=False, showticklabels=False)

    fig.update_layout(
        xaxis=dict(showgrid=True,
                   range=[df['time'].min(), df['time'].max()],
                   tickformat='%a %d %b\n%H:%M'),
        yaxis=dict(showgrid=True),
        height=700,
        margin={"r": 5, "t": 30, "l": 5, "b": 5},
        template='plotly_white',
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
