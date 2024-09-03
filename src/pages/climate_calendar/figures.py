from dash import dcc
import plotly.express as px
import pandas as pd
from utils.settings import images_config


def make_calendar_figure(df, graph_type, title=None):
    cmap = "RdBu_r"

    if graph_type == "accumulated_precipitation":
        out = df.pivot_table(
            index=df.time.dt.month,
            columns=df.time.dt.year,
            values="precipitation_sum",
            aggfunc="sum",
        )
    else:
        raise ValueError()

    fig = px.imshow(
        out.values,
        x=out.columns.values,
        y=out.index.values,
        text_auto=True,
        aspect="auto",
        color_continuous_scale=cmap,
        origin="upper",
    )
    fig.update_traces(
        hovertemplate="<extra></extra><b>%{y}/%{x}</b><br>Value = %{z}"
    )

    fig.update_layout(
        modebar=dict(orientation="v"),
        dragmode=False,
        xaxis=dict(showgrid=True, title_text="Year"),
        yaxis=dict(
            showgrid=True, fixedrange=True, showticklabels=True, title_text="Month"
        ),
        margin={"r": 5, "t": 40, "l": 5, "b": 5},
    )

    fig.update_coloraxes(showscale=False)
    if title is not None:
        fig.update_layout(
            title=dict(text=title, font=dict(size=14), yref="container", y=0.98)
        )


    return fig


# CARDS for layout

fig_subplots = dcc.Graph(
    id=dict(type="figure", id="calendar"),
    config=images_config,
    style={"height": "95vh"},
)
