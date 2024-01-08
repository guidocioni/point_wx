from dash import dcc
import plotly.graph_objects as go
import pandas as pd
from utils.settings import images_config


def make_figure_vertical(time_axis, vertical_levels, arrs, title=None):

    fig = go.Figure(data=[
        go.Contour(
            z=arrs[0].T,
            x=time_axis,  # horizontal axis
            y=vertical_levels,  # vertical axis,
            line_width=0,
            colorscale='jet',
            contours=dict(
                start=-50,
                end=30,
                size=2.5,
            )
        ),
        go.Contour(
            z=arrs[1].T,
            x=time_axis,  # horizontal axis
            y=vertical_levels,  # vertical axis,
            line_width=1,
            contours_coloring='none',
            contours=dict(
                start=0,
                end=100,
                size=25,
                showlabels=True,
            ),
        ),
    ])

    fig.update_traces(
        hovertemplate="<extra></extra><b>%{x|%a %d %b %H:%M}</b><br>%{y}<br>Value = %{z}")

    fig.update_layout(
        xaxis=dict(showgrid=True, tickformat='%a %d %b\n%H:%M'),
        yaxis=dict(range=[vertical_levels.max(),
                          vertical_levels.min()],
                   showgrid=True,
                   title_text="Pressure [hPa]"),
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
                         args=[{"xaxis.range[0]": time_axis.min() - pd.to_timedelta('0.5H'),
                                "xaxis.range[1]": time_axis.min() + pd.to_timedelta('24.5H')}]),
                    dict(label="48H",
                         method="relayout",
                         args=[{"xaxis.range[0]": time_axis.min() - pd.to_timedelta('0.5H'),
                                "xaxis.range[1]": time_axis.min() + pd.to_timedelta('48.5H')}]),
                    dict(label="Reset",
                         method="relayout",
                         args=[{"xaxis.range[0]": time_axis.min() - pd.to_timedelta('0.5H'),
                                "xaxis.range[1]": time_axis.max() + pd.to_timedelta('0.5H')}]),
                ],
                pad=dict(b=5),
            ),
        ],
    )

    if title is not None:
        fig.update_layout(title=dict(text=title, font=dict(size=14)))

    return fig


# CARDS for layout

fig_subplots = dcc.Graph(id='plot-vertical', config=images_config)
