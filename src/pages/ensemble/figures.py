from dash import dcc
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots
import pandas as pd
from utils.settings import images_config


def make_boxplot_timeseries(df, var, clima=None):
    columns_regex = rf'{var}$|{var}_member(0[1-9]|[1-9][0-9])$|time'
    tmp = df.loc[:, df.columns.str.match(columns_regex)].set_index("time")
    traces = []
    for index, row in tmp.iterrows():
        traces.append(
            go.Box(
                x=[index] * len(row),
                y=row,
                showlegend=False,
                boxpoints=False,
                marker_color="gray",
            )
        )

    if clima is not None:
        # Now add climatology
        df["doy"] = df["time"].dt.strftime("%m%d")
        df["hour"] = df["time"].dt.hour
        clima = clima.merge(
            df[["doy", "hour", "time"]],
            left_on=["doy", "hour"],
            right_on=["doy", "hour"],
        )
        clima = clima.sort_values(by="time")
        traces.append(
            go.Scattergl(
                x=clima["time"],
                y=clima[var],
                mode="lines",
                name="climatology",
                line=dict(width=4, color="rgba(0, 0, 0, 0.4)", dash="dot"),
                showlegend=False,
            )
        )

    return traces


def make_lineplot_timeseries(df, var, clima=None, break_hours="48h"):
    traces = []
    columns_regex = rf'{var}$|{var}_member(0[1-9]|[1-9][0-9])$'
    for col in df.columns[df.columns.str.match(columns_regex)]:
        traces.append(
            go.Scattergl(
                x=df.loc[
                    df.time <= df.time.iloc[0] + pd.to_timedelta(break_hours), "time"
                ],
                y=df.loc[
                    df.time <= df.time.iloc[0] + pd.to_timedelta(break_hours), col
                ],
                mode="lines+markers",
                name=col,
                hovertemplate="<extra></extra><b>%{x|%a %-d %b %H:%M}</b>, "
                + var
                + " = %{y}",
                marker=dict(size=4),
                line=dict(width=1),
                showlegend=False,
            ),
        )
    for col in df.columns[df.columns.str.match(columns_regex)]:
        traces.append(
            go.Scattergl(
                x=df.loc[
                    df.time >= df.time.iloc[0] + pd.to_timedelta(break_hours), "time"
                ],
                y=df.loc[
                    df.time >= df.time.iloc[0] + pd.to_timedelta(break_hours), col
                ],
                mode="lines",
                name=col,
                hovertemplate="<extra></extra><b>%{x|%a %-d %b %H:%M}</b>, "
                + var
                + " = %{y}",
                line=dict(width=1),
                showlegend=False,
            ),
        )
    # Additional shading
    traces.append(
        go.Scattergl(
            x=df.loc[:, "time"],
            y=df.loc[:, df.columns.str.match(columns_regex)].min(axis=1),
            mode="lines",
            line=dict(color="rgba(0, 0, 0, 0)"),
            hoverinfo="skip",
            showlegend=False,
        )
    )
    traces.append(
        go.Scattergl(
            x=df.loc[:, "time"],
            y=df.loc[:, df.columns.str.match(columns_regex)].max(axis=1),
            mode="lines",
            line=dict(color="rgba(0, 0, 0, 0)"),
            fillcolor="rgba(0, 0, 0, 0.1)",
            fill="tonexty",
            hoverinfo="skip",
            showlegend=False,
        )
    )
    if clima is not None and var in clima.columns:
        # Now add climatology
        # Create a hourly array that matchest the start and end of the real data
        # Doesn't matter if that data is 1, 3 or 6 hourly. As the climatology
        # will be hourly we do this
        # Create a pandas DataFrame with the new time axis
        # Needs to be every hour, starting and ending on the bounds given
        # by our input dataframe
        time_sel = pd.DataFrame(
            {
                "time_selection": pd.date_range(
                    df["time"].min(), df["time"].max(), freq="1h", tz=df.attrs["timezone"]
                )
            }
        )
        time_sel["time_selection_str"] = time_sel["time_selection"].dt.strftime(
            "%m%d"
        ) + time_sel["time_selection"].dt.strftime("%H")

        clima["doy_hour"] = clima["doy"] + clima["hour"].astype(str).str.zfill(2)
        clima = clima.merge(time_sel, left_on="doy_hour", right_on="time_selection_str")
        clima = (
            clima.drop(columns=["doy_hour", "doy", "hour", "time_selection_str"])
            .sort_values(by="time_selection")
            .rename(columns={"time_selection": "time"})
            .interpolate()
            .round(1)
        )

        traces.append(
            go.Scattergl(
                x=clima["time"],
                y=clima[var],
                mode="lines",
                name="ERA5 Climatology",
                line=dict(width=4, color="rgba(0, 0, 0, 0.3)"),
                hovertemplate="<b>%{x|%a %-d %b %H:%M}</b>, " + var + " = %{y}",
                showlegend=False,
            )
        )

    return traces


def make_scatterplot_timeseries(df, var):
    columns_regex = rf'{var}$|{var}_member(0[1-9]|[1-9][0-9])$'
    df[f"{var}_mean"] = df.loc[:, df.columns.str.match(columns_regex)].mean(axis=1)
    traces = []
    # for col in df.columns[df.columns.str.contains(var)]:
    #     traces.append(
    #         go.Scattergl(
    #             x=df.loc[:, "time"],
    #             y=df.loc[:, col],
    #             mode="markers",
    #             name=col,
    #             marker=dict(size=4),
    #             line=dict(width=1),
    #             hovertemplate="<extra></extra><b>%{x|%a %-d %b %H:%M}</b>, "
    #             + var
    #             + " = %{y:.1f}",
    #             showlegend=False,
    #         ),
    #     )
    # Define the bins
    if var == 'cloudcover':
        bins = list(np.linspace(0, 100, 11))
    elif var == 'wind_speed_10m':
        bins = list(np.linspace(0, df.loc[:, df.columns.str.match(columns_regex)].max().max(), 11))

    # Create a function to compute the percentage of values in each bin
    def compute_bin_percentages(row, bins):
        bin_counts = np.histogram(row, bins=bins)[0]
        bin_percentages = bin_counts / len(row) * 100
        return bin_percentages

    # Apply the function to each row
    bin_percentages_df = df.loc[:, df.columns.str.match(columns_regex)].apply(
        lambda row: compute_bin_percentages(row, bins), axis=1, result_type="expand"
    )
    traces.append(
        go.Heatmap(
            x=df.loc[:, "time"],
            colorscale="YlGnBu_r",
            hoverinfo="skip",
            y=bins,
            z=bin_percentages_df.values.T,
            showscale=False,
        ),
    )
    # add line with the average
    traces.append(
        go.Scattergl(
            x=df.loc[:, "time"],
            y=df.loc[:, f"{var}_mean"],
            mode="lines",
            name="Mean",
            line=dict(width=2, color="white"),
            hovertemplate="<b>%{x|%a %-d %b %H:%M}</b>, " + var + " = %{y}",
            showlegend=False,
        ),
    )

    return traces


def make_barplot_timeseries(df, var, color="cadetblue"):
    columns_regex = rf'{var}$|{var}_member(0[1-9]|[1-9][0-9])$'
    # Do some pre-processing on the input
    members = len(df.loc[:, df.columns.str.match(columns_regex)].columns)

    df[f"{var}_prob"] = (
        ((df.iloc[:, df.columns.str.match(columns_regex)] >= 0.1).sum(axis=1) / members)
        * 100.0
    ).astype(int)

    df[f"{var}_mean"] = df.iloc[:, df.columns.str.match(columns_regex)].mean(axis=1)

    df.loc[df[f"{var}_prob"] < 5, [f"{var}_prob", f"{var}_mean"]] = np.nan

    trace = go.Bar(
        x=df["time"],
        y=df[f"{var}_mean"],
        text=df[f"{var}_prob"],
        name=var,
        textposition="outside",
        hovertemplate="<extra></extra><b>%{x|%a %-d %b %H:%M}</b>, "
        + var
        + " = %{y:.1f}",
        showlegend=False,
        width=(df["time"].diff().dt.seconds * 850).bfill().ffill(),
        marker_color=color,
    )

    return trace


def make_barpolar_figure(df, n_partitions=15, bins=np.linspace(0, 360, 15)):
    columns_regex = r'wind_direction$|wind_direction_member(0[1-9]|[1-9][0-9])$'
    timeSpan = df.time.iloc[-1] - df.time.iloc[0]
    rule = int((timeSpan.total_seconds() / 3600.0) / n_partitions)
    subset = df.resample(str(rule) + "H", on="time").first()
    subset = subset.loc[:, subset.columns.str.match(columns_regex)]

    out = []
    for i, row in subset.iterrows():
        out.append(pd.cut(row.values, bins=bins).value_counts().values)
    # Convert to normalized percentage
    for i, o in enumerate(out):
        out[i] = (o / len(subset.columns)) * 100.0
    n_plots = len(out) - 1
    fig = make_subplots(
        rows=1,
        cols=n_plots,
        specs=[[{"type": "polar"} for _ in range(n_plots)]],
        horizontal_spacing=0,
    )
    for i in range(n_plots):
        fig.add_trace(
            go.Barpolar(
                r=out[i - 1],
                theta=bins,
                marker_color="rgb(106,81,163)",
                showlegend=False,
                hoverinfo="skip",
            ),
            row=1,
            col=i + 1,
        )
    fig.update_polars(radialaxis_showticklabels=False, angularaxis_showticklabels=False)
    fig.update_layout(
        margin={"r": 2, "t": 1, "l": 2, "b": 0.1}, height=100, dragmode=False
    )

    return fig


def make_subplot_figure(data, clima=None, title=None, sun=None, additional_plot='clouds'):
    traces_temp = make_lineplot_timeseries(
        data, "temperature_2m", clima, break_hours="12h"
    )
    # traces_temp = make_boxplot_timeseries(data, 'temperature_2m', clima)
    height_graph = 0.0
    subplot_title = ""
    if len(data.loc[:, data.columns.str.match(r'temperature_850hPa$|temperature_850hPa_member(0[1-9]|[1-9][0-9])$')].dropna() > 0):
        traces_temp_850 = make_lineplot_timeseries(
            data, "temperature_850hPa", clima, break_hours="0h"
        )
        height_graph = 0.4
        subplot_title = "<b>850hPa Temp"
    trace_rain = make_barplot_timeseries(data, "rain", color="cadetblue")
    if data.loc[:, data.columns.str.match(r'snowfall$|snowfall_member(0[1-9]|[1-9][0-9])$')].max().max() >= 0.1:
        trace_snow = make_barplot_timeseries(data, "snowfall", color="rebeccapurple")
    if additional_plot == 'clouds':
        traces_clouds = make_scatterplot_timeseries(data, "cloudcover")
        additional_title = 'Cloud Cover [%]'
    elif additional_plot == 'winds':
        traces_winds = make_scatterplot_timeseries(data, "wind_speed_10m")
        additional_title = 'Winds [km/h]'

    fig = make_subplots(
        rows=4,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.032,
        subplot_titles=[
            "<b>2m Temp",
            subplot_title,
            "<b>Rain [mm] | Snow [cm] | Prob. [%]",
            f"<b>{additional_title}",
        ],
        row_heights=[0.35, height_graph, 0.3, 0.25],
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
            font=dict(size=11, color='rgba(1, 1, 1, 0.3)'),
        )

    for i, tick in enumerate(tickvals):
        fig.add_annotation(
            x=tick, y=1, text=ticktext[i], showarrow=False, textangle=-90,
            xref='x', yref='y3 domain', yanchor='top', xanchor='center',
            font=dict(size=11, color='rgba(1, 1, 1, 0.3)')
        )

    for trace_temp in traces_temp:
        fig.add_trace(trace_temp, row=1, col=1)
    if len(data.loc[:, data.columns.str.match(r'temperature_850hPa$|temperature_850hPa_member(0[1-9]|[1-9][0-9])$')].dropna() > 0):
        for trace_temp_850 in traces_temp_850:
            fig.add_trace(trace_temp_850, row=2, col=1)
    fig.add_trace(trace_rain, row=3, col=1)
    if data.loc[:, data.columns.str.match(r'snowfall$|snowfall_member(0[1-9]|[1-9][0-9])$')].max().max() >= 0.1:
        fig.add_trace(trace_snow, row=3, col=1)
    if additional_plot == 'clouds':
        for trace_clouds in traces_clouds:
            fig.add_trace(trace_clouds, row=4, col=1)
    elif additional_plot == 'winds':
        for trace_winds in traces_winds:
            fig.add_trace(trace_winds, row=4, col=1)

    fig.update_layout(
        modebar=dict(orientation="v"),
        dragmode=False,
        margin={"r": 5, "t": 50, "l": 0.1, "b": 0.1},
        barmode="stack",
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
                                - pd.to_timedelta("2h"),
                                "xaxis.range[1]": data["time"].min()
                                + pd.to_timedelta("25h"),
                            }
                        ],
                    ),
                    dict(
                        label="48H",
                        method="relayout",
                        args=[
                            {
                                "xaxis.range[0]": data["time"].min()
                                - pd.to_timedelta("2h"),
                                "xaxis.range[1]": data["time"].min()
                                + pd.to_timedelta("49h"),
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
        ticksuffix="",
        row=1,
        col=1,
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor="rgba(0,0,0,0.5)",
    )
    fig.update_yaxes(
        ticksuffix="",
        row=2,
        col=1,
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor="rgba(0,0,0,0.5)",
    )
    fig.update_yaxes(
        row=3,
        col=1,
        range=[0, max((data["rain_mean"].max()) * 1.5, 1)],
    )
    if additional_plot == 'clouds':
        fig.update_yaxes(range=[0, 100], row=4, col=1)
    # we need to re-set it here otherwise it only applies to the first plot
    fig.update_yaxes(showgrid=True, gridwidth=4)
    fig.update_xaxes(
        showgrid=True,
        gridwidth=4,
        range=[
            data["time"].min() - pd.to_timedelta("1h"),
            data["time"].max() + pd.to_timedelta("1h"),
        ],
        tickformat="%a %-d %b\n%H:%M",
        minor=dict(ticks="inside", gridwidth=3),
    )
    if title is not None:
        fig.update_layout(title=dict(text=title, font=dict(size=14), yref='container', y=0.98))

    return fig


# Figures for layout


fig_subplots = dcc.Graph(id=dict(type="figure", id="ensemble"),
                         config=images_config, style={'height':'90vh', 'min-height': '650px'})
# fig_polar = dcc.Graph(id='polar-plot',
#                       config={**images_config, 'displayModeBar': False})
