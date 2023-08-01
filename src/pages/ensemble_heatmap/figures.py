import dash_bootstrap_components as dbc
from dash import dcc
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots
import pandas as pd
import plotly.express as px

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


def make_heatmap(df, var):
    fig = px.imshow(
    df.loc[:, df.columns.str.contains(var)].T,
    x=df['time'],
                text_auto=True,
                color_continuous_scale='RdBu_r',
                origin='lower')

    fig.update_yaxes(visible=False, showticklabels=False)

    fig.update_layout(
                xaxis=dict(showgrid=True,
                        range=[df['time'].min(),df['time'].max()]),
                yaxis=dict(showgrid=True),
                margin={"r": 3, "t": 3, "l": 3, "b": 3},
                template='plotly_white',
            )
    fig.update_coloraxes(showscale=False)
    
    return fig


# CARDS for layout

fig_subplots = dbc.Card(
    [
        dcc.Graph(id='ensemble-plot-heatmap')
    ],
    className="mb-2",
    id='ensemble-fig-card-heatmap'
)
