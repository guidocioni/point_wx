from dash import dcc
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import pandas as pd
from utils.settings import images_config, DEFAULT_TEMPLATE, ASSETS_DIR
from utils.figures_utils import attach_alpha_to_hex_color, hex2rgba


def make_lineplot_timeseries(
    df, var, models, mode="lines+markers", showlegend=False, fill="none", alpha=1
):
    traces = []
    # Define cyclical colors to be used
    colors = pio.templates[DEFAULT_TEMPLATE]["layout"]["colorway"] * 5
    i = 0
    for model in models:
        if len(models) > 1:
            var_model = var + "_" + model
        else:
            var_model = var
        if var_model in df.columns:
            color = attach_alpha_to_hex_color(alpha, colors[i])
            color = hex2rgba(color)
            traces.append(
                go.Scatter(
                    x=df.loc[:, "time"],
                    y=df.loc[:, var_model],
                    mode=mode,
                    name=model,
                    marker=dict(size=5, color=color),
                    line=dict(width=2, color=color),
                    fillcolor=color,
                    hovertemplate="<b>%{x|%a %-d %b %H:%M}</b>, " + var + " = %{y}",
                    showlegend=showlegend,
                    fill=fill,
                ),
            )
        i += 1

    return traces


def make_windarrow_timeseries(
    df, models, var_speed="windgusts_10m", var_dir="winddirection_10m", showlegend=False
):
    df = df.resample("3h", on="time").mean().reset_index()
    traces = []
    # Define cyclical colors to be used
    colors = pio.templates[DEFAULT_TEMPLATE]["layout"]["colorway"] * 5
    i = 0
    for model in models:
        if len(models) > 1:
            var_speed_model = var_speed + "_" + model
            var_dir_model = var_dir + "_" + model
        else:
            var_speed_model = var_speed
            var_dir_model = var_dir
        if var_speed_model in df.columns and var_dir_model in df.columns:
            marker = dict(
                size=10,
                color=colors[i],
                symbol="arrow",
                line=dict(width=1, color="DarkSlateGrey"),
            )
            # If there's any NaNs in the direction prevents an error
            if not df.loc[:, var_dir_model].isnull().any():
                marker["angle"] = df.loc[:, var_dir_model] - 180.0
            traces.append(
                go.Scatter(
                    x=df.loc[:, "time"],
                    y=df.loc[:, var_speed_model],
                    mode="markers",
                    name=model,
                    marker=marker,
                    hoverinfo="skip",
                    showlegend=showlegend,
                ),
            )
            # we always add to respect the colors order
        i += 1

    return traces


def make_barplot_timeseries(df, var, models, color="rgb(26, 118, 255)"):
    traces = []
    # Define cyclical colors to be used
    colors = pio.templates[DEFAULT_TEMPLATE]["layout"]["colorway"] * 5
    i = 0
    for model in models:
        if len(models) > 1:
            var_model = var + "_" + model
        else:
            var_model = var
        if var_model in df.columns:
            traces.append(
                go.Bar(
                    x=df["time"],
                    y=df[var_model],
                    name=model,
                    opacity=0.6,
                    marker=dict(color=color),
                    hovertemplate="<b>%{x|%a %-d %b %H:%M}</b>, " + var + " = %{y:.1f}",
                    showlegend=False,
                ),
            )
            # Add marker to identify model
            traces.append(
                go.Scatter(
                    x=df.loc[df[var_model] >= 0.05, "time"],
                    y=df.loc[df[var_model] >= 0.05, var_model],
                    mode="markers",
                    name=model,
                    hovertemplate="<b>%{x|%a %-d %b %H:%M}</b>, " + var + " = %{y:.1f}",
                    marker=dict(size=5, color=colors[i]),
                    showlegend=False,
                ),
            )
        i += 1

    return traces


def add_weather_icons(data, fig, row_fig, col_fig, var, models):
    from PIL import Image
    from utils.figures_utils import get_weather_icons

    for model in models:
        if len(models) > 1:
            var_model = var + "_" + model
            var_weather_model = "weather_code_" + model
        else:
            var_weather_model = "weather_code"
            var_model = var
        if var_weather_model in data:
            data = data.resample("12h", on="time").max().reset_index()
            data = get_weather_icons(
                data,
                var=var_weather_model,
            )
            for _, row in data.iterrows():
                fig.add_layout_image(
                    dict(
                        source=Image.open(row["icons"]),
                        xref="x",
                        x=row["time"],
                        yref="y",
                        y=row[var_model],
                        sizex=12 * 24 * 10 * 60 * 1000,
                        sizey=1,
                    ),
                    row=row_fig,
                    col=col_fig,
                )


def make_subplot_figure(data, models, title=None, sun=None):
    traces_temp = make_lineplot_timeseries(
        data, "temperature_2m", showlegend=False, models=models
    )
    # traces_sunshine = make_lineplot_timeseries(
    #     data, 'sunshine_duration', models=models,
    #     fill="tozeroy", alpha=0.3)
    traces_precipitation = make_barplot_timeseries(data, "precipitation", models=models)
    if data.loc[:,data.columns.str.contains('snowfall')].max().max() >= 0.1:
        traces_snow = make_barplot_timeseries(
            data, "snowfall", models=models, color="rgb(214, 138, 219)"
        )
    traces_wind = make_lineplot_timeseries(
        data, "windgusts_10m", mode="lines", models=models
    )
    traces_wind_dir = make_windarrow_timeseries(data, models=models,
                                                var_speed="windgusts_10m",
                                                var_dir="winddirection_10m")
    traces_cloud = make_lineplot_timeseries(
        data, "cloudcover", mode="markers", models=models
    )

    fig = make_subplots(
        rows=4,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.032,
        row_heights=[0.44, 0.25, 0.3, 0.2],
        subplot_titles=[
            "<b>2m Temp",
            "<b>Precip[mm] / Snow[cm]",
            "<b>Winds [km/h]",
            "<b>Clouds [%]",
        ],
        specs=[
            [{"secondary_y": False, "r": -0.05}],
            [{"secondary_y": True, "r": -0.05}],
            [{"secondary_y": False, "r": -0.05}],
            [{"secondary_y": False, "r": -0.05}],
        ],
    )
    # Update subplot titles font size
    fig.update_annotations(font=dict(size=13))

    # Manually calculate tick values and labels
    tickvals = pd.date_range(start=data["time"].min().normalize() + pd.Timedelta('1 day'),
                             end=data["time"].max().normalize(),
                             freq='D')
    ticktext = [date.strftime('%a %d %b') for date in tickvals]

    # Add annotations for the first subplot
    for i, tick in enumerate(tickvals):
        fig.add_annotation(
            x=tick, y=1, text=ticktext[i], showarrow=False, textangle=-90,
            xref='x', yref='y domain', yanchor='top', xanchor='center',
            font=dict(size=12, color='rgba(1, 1, 1, 0.3)'),
        )

    for i, tick in enumerate(tickvals):
        fig.add_annotation(
            x=tick, y=1, text=ticktext[i], showarrow=False, textangle=-90,
            xref='x', yref='y5 domain', yanchor='top', xanchor='center',
            font=dict(size=12, color='rgba(1, 1, 1, 0.3)')
        )

    for trace_temp in traces_temp:
        fig.add_trace(trace_temp, row=1, col=1)
        # add_weather_icons(data, fig, row_fig=1, col_fig=1, var='temperature_2m', models=models)
    # for trace_sunshine in traces_sunshine:
    #     fig.add_trace(trace_sunshine, row=1, col=1, secondary_y=True)
    for trace_precipitation in traces_precipitation:
        fig.add_trace(trace_precipitation, row=2, col=1)
    if data.loc[:,data.columns.str.contains('snowfall')].max().max() >= 0.1:
        for trace_snow in traces_snow:
            fig.add_trace(trace_snow, row=2, col=1, secondary_y=True)
    for trace_wind in traces_wind:
        fig.add_trace(trace_wind, row=3, col=1)
    for trace_wind_dir in traces_wind_dir:
        fig.add_trace(trace_wind_dir, row=3, col=1)
    for trace_cloud in traces_cloud:
        fig.add_trace(trace_cloud, row=4, col=1)

    fig.update_layout(
        modebar=dict(orientation="v"),
        dragmode=False,
        xaxis=dict(showgrid=True),
        margin={"r": 1, "t": 50, "l": 1, "b": 0.1},
        barmode="overlay",
        # legend=dict(orientation="h", y=-0.04),
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
                                "xaxis.range[0]": data["time"].min()
                                - pd.to_timedelta("1h"),
                                "xaxis.range[1]": data["time"].min()
                                + pd.to_timedelta("24h"),
                            }
                        ],
                    ),
                    dict(
                        label="48H",
                        method="relayout",
                        args=[
                            {
                                "xaxis.range[0]": data["time"].min()
                                - pd.to_timedelta("1h"),
                                "xaxis.range[1]": data["time"].min()
                                + pd.to_timedelta("48h"),
                            }
                        ],
                    ),
                    dict(
                        label="Reset",
                        method="relayout",
                        args=[
                            {
                                "xaxis.range[0]": data["time"].min()
                                - pd.to_timedelta("1h"),
                                "xaxis.range[1]": data["time"].max()
                                + pd.to_timedelta("1h"),
                            }
                        ],
                    ),
                ],
                pad=dict(b=5),
            ),
        ],
    )

    if sun is not None:
        for i, s in sun.iterrows():
            fig.add_vrect(
                x0=s["sunrise"] if i != 0 else max(s["sunrise"], data["time"].min()),
                x1=s["sunset"] if i != len(sun) - 1 else min(s["sunset"], data["time"].max()),
                fillcolor="rgba(255, 255, 0, 0.3)",
                layer="below",
                line=dict(width=0),
                row=1,
                col=1,
            )

    fig.update_yaxes(
        ticksuffix="°C",
        row=1,
        col=1,
        zeroline=True,
        zerolinewidth=4,
        zerolinecolor="rgba(0,0,0,0.2)",
    )
    fig.update_yaxes(
        tickangle=-90, color="rgb(26, 118, 255)", row=2, col=1, secondary_y=False,
        range=[0, max(data.loc[:,data.columns.str.contains('precipitation')].max().max() * 1.5, 1)]
    )
    fig.update_yaxes(tickangle=-90, row=3, col=1)
    fig.update_yaxes(row=4, col=1, tickangle=-90)
    if data.loc[:,data.columns.str.contains('snowfall')].max().max() >= 0.1:
        fig.update_yaxes(
            tickangle=-90,
            row=2,
            col=1,
            secondary_y=True,
            autorange="reversed",
            color="rgb(214, 138, 219)",
            showgrid=False,
            minor=dict(showgrid=False),
        )
    fig.update_xaxes(
        minor=dict(ticks="inside", showgrid=True, gridwidth=1),
        tickformat="%a %-d %b\n%H:%M",
        showgrid=True,
        gridwidth=4,
        range=[
            data["time"].min() - pd.to_timedelta("1h"),
            data["time"].max() + pd.to_timedelta("1h"),
        ],
    )
    if title is not None:
        fig.update_layout(title=dict(text=title, font=dict(size=14), yref='container', y=0.98))

    return fig


# CARDS for layout


fig_subplots = dcc.Graph(
    id=dict(type="figure", id="deterministic"), config=images_config, style={'height':'90vh', 'min-height': '680px'}
)
