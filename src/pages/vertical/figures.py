import plotly.graph_objects as go
import pandas as pd
from dash import dcc
from utils.settings import images_config


def make_figure_vertical(time_axis, vertical_levels, arrs, title=None):
    traces = []
    # Filled contours of temperature
    traces.append(
        go.Contour(
            z=arrs[0].T,
            x=time_axis,
            y=vertical_levels,
            line_width=0.1,
            colorscale="jet",
            contours=dict(
                start=-60,
                end=30,
                size=2.5,
                showlabels=True,
                labelfont=dict(  # label font properties
                    size=10,
                    color="rgba(0, 0, 0, 0.3)",
                ),
            ),
            showscale=False,
            name="Temp",
            showlegend=True,
            legendgroup="Temp",
            hovertemplate="<extra></extra><b>%{x|%a %-d %b %H:%M}</b><br>%{y}hPa<br>Temperature = %{z}",
        )
    )
    # Contour line for 0 isotherm
    traces.append(
        go.Contour(
            z=arrs[0].T,
            x=time_axis,
            y=vertical_levels,
            line_width=1,
            contours=dict(
                coloring="none",
                type="constraint",
                operation="=",
                value=0,
            ),
            showscale=False,
            hoverinfo="skip",
            legendgroup="Temp",
            showlegend=False,
        )
    )
    # Geopotential height contours
    for lev in [100, 1500, 3000, 5000, 7500, 10000]:
        traces.append(
            go.Contour(
                z=arrs[4].T,
                x=time_axis,
                y=vertical_levels,
                line_width=4,
                line_color="rgba(0, 0, 0, 0.4)",
                contours=dict(
                    coloring="none",
                    type="constraint",
                    operation="=",
                    value=lev,
                    showlabels=True,
                    labelfont=dict(size=15, color="rgba(0, 0, 0, 0.4)"),
                    labelformat="%i",
                ),
                hoverinfo="skip",
                showscale=False,
                legendgroup="Geop",
                name="Geop",
                showlegend=True if lev == 100 else False,
            )
        )
    # Cloud cover filled contours with less opacity
    traces.append(
        go.Contour(
            z=arrs[1].T,
            x=time_axis,
            y=vertical_levels,
            line_width=0,
            colorscale=[
                [0, "rgba(255, 255, 255, 0)"],
                [0.1, "rgba(255, 255, 255, 0)"],
                [0.1, "rgba(240,240,240, 0.35)"],
                [0.3, "rgba(217,217,217,  0.35)"],
                [0.5, "rgba(189,189,189,  0.35)"],
                [0.7, "rgba(150,150,150,  0.35)"],
                [0.9, "rgba(115,115,115,  0.35)"],
                [0.9, "rgba(255, 255, 255, 0)"],
                [1, "rgba(255, 255, 255, 0)"],
            ],
            contours=dict(
                start=10,
                end=100,
                size=20,
                showlabels=True,
                labelfont=dict(  # label font properties
                    size=10, color="rgba(0, 0, 0, 0.7)"
                ),
            ),
            hoverinfo="skip",
            showscale=False,
            line_smoothing=0.95,
            name="Clouds",
            showlegend=True,
        )
    )
    # Wind vectors showing direction and intensity
    every = 4
    for i_level, level in enumerate(vertical_levels):
        traces.append(
            go.Scatter(
                x=time_axis[::4],
                y=[level] * len(time_axis[::every]),
                mode="markers",
                marker=dict(
                    size=10,
                    color=arrs[2][::every, i_level],
                    colorscale="YlOrBr",
                    cmin=0,
                    cmax=100,
                    symbol="arrow",
                    angle=arrs[3][::every, i_level] - 180.0,
                    line=dict(width=0.5, color="DarkSlateGrey"),
                ),
                customdata=[
                    f"Wind = {winddir}°@{windspd:.0f}km/h"
                    for winddir, windspd in zip(
                        arrs[3][::every, i_level], arrs[2][::every, i_level]
                    )
                ],
                hovertemplate="<extra></extra><b>%{x|%a %-d %b %H:%M}</b><br>%{y}hPa<br>%{customdata}",
                legendgroup="Winds",
                name="Winds",
                showlegend=True if i_level == 0 else False,
            )
        )

    fig = go.Figure(traces)

    fig.update_layout(
        modebar=dict(orientation="v"),
        dragmode=False,
        legend=dict(orientation="h"),
        xaxis=dict(
            showgrid=True,
            tickformat="%a %-d %b\n%H:%M",
            range=[
                time_axis.min() - pd.to_timedelta("0.5h"),
                time_axis.max() + pd.to_timedelta("0.5h"),
            ],
        ),
        yaxis=dict(range=[1010, 200], showgrid=True, title_text="", tickangle=-90),
        margin={"r": 5, "t": 40, "l": 5, "b": 5},
        updatemenus=[
            dict(
                type="buttons",
                x=0.5,
                y=-0.05,
                xanchor="center",
                direction="right",
                buttons=[
                    dict(
                        label="24H",
                        method="relayout",
                        args=[
                            {
                                "xaxis.range[0]": time_axis.min()
                                - pd.to_timedelta("0.5h"),
                                "xaxis.range[1]": time_axis.min()
                                + pd.to_timedelta("24.5h"),
                            }
                        ],
                    ),
                    dict(
                        label="48H",
                        method="relayout",
                        args=[
                            {
                                "xaxis.range[0]": time_axis.min()
                                - pd.to_timedelta("0.5h"),
                                "xaxis.range[1]": time_axis.min()
                                + pd.to_timedelta("48.5h"),
                            }
                        ],
                    ),
                    dict(
                        label="Reset",
                        method="relayout",
                        args=[
                            {
                                "xaxis.range[0]": time_axis.min()
                                - pd.to_timedelta("0.5h"),
                                "xaxis.range[1]": time_axis.max()
                                + pd.to_timedelta("0.5h"),
                            }
                        ],
                    ),
                ],
                pad=dict(b=5),
            ),
        ],
    )

    if title is not None:
        fig.update_layout(title=dict(text=title, font=dict(size=14), yref='container', y=0.98))

    return fig


# CARDS for layout

fig_subplots = dcc.Graph(id=dict(type="figure", id="vertical"), config=images_config, style={'height':'90vh'})
