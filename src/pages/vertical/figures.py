import plotly.graph_objects as go
import pandas as pd
import numpy as np
from dash import dcc
from utils.settings import images_config
from metpy.calc import parcel_profile, moist_lapse, dry_lapse
from metpy.units import units


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
        fig.update_layout(
            title=dict(text=title, font=dict(size=14), yref="container", y=0.98)
        )

    return fig


def make_figure_skewt(df, title=None):
    skew = 100.0

    def skew_transform(temp, pres):
        """Transform temperature based on pressure level for skewed coordinates"""
        # Convert pressure to log scale and normalize
        log_p = np.log(pres)
        log_p_norm = (np.log(1050) - log_p) / (np.log(1050) - np.log(100))
        # Apply skew transformation
        return temp + skew * log_p_norm

    def create_background_lines(fig):
        """Add background lines for isotherms, dry adiabats, and moist adiabats"""
        # Pressure levels for background lines (log-spaced)
        pres = np.logspace(np.log10(100), np.log10(1000), 100)

        # Isotherms
        for temp in range(-70, 41, 10):
            skewed_temps = skew_transform([temp] * len(pres), pres)
            fig.add_trace(
                go.Scatter(
                    x=skewed_temps,
                    y=pres,
                    mode="lines",
                    line=dict(color="gray", width=0.5),
                    showlegend=False,
                    hoverinfo="none",
                )
            )
            # Add label at the top of each isotherm line
            fig.add_annotation(
                x=skew_transform(temp, 300),
                y=np.log10(300),
                text=f"{temp}°C",
                showarrow=False,
                yshift=-5,  # Shift label slightly below the top
                font=dict(size=10),
                bgcolor="white",
                bordercolor="gray",
                borderwidth=1,
                borderpad=2,
                textangle=320
            )
            fig.add_annotation(
                x=skew_transform(temp, 500),
                y=np.log10(500),
                text=f"{temp}°C",
                showarrow=False,
                yshift=-5,  # Shift label slightly below the top
                font=dict(size=10),
                bgcolor="white",
                bordercolor="gray",
                borderwidth=1,
                borderpad=2,
                textangle=320
            )
            fig.add_annotation(
                x=skew_transform(temp, 900),
                y=np.log10(900),
                text=f"{temp}°C",
                showarrow=False,
                yshift=-5,  # Shift label slightly below the top
                font=dict(size=10),
                bgcolor="white",
                bordercolor="gray",
                borderwidth=1,
                borderpad=2,
                textangle=320
            )
        # Dry adiabats (simplified calculation)
        for temp in range(-150, 31, 5):
            dry_adiabat = (
                dry_lapse(pres * units.hPa, temp * units.degC).to("degC").magnitude
            )
            skewed_temps = skew_transform(dry_adiabat, pres)
            fig.add_trace(
                go.Scatter(
                    x=skewed_temps,
                    y=pres,
                    mode="lines",
                    line=dict(color="rgba(165, 42, 42, 1)", width=0.5),
                    showlegend=False,
                    hoverinfo="none",
                )
            )

        # Moist adiabats (simplified calculation)
        for temp in range(-150, -31, 10):
            moist_adiabat = (
                moist_lapse(pres * units.hPa, temp * units.degC).to("degC").magnitude
            )
            skewed_temps = skew_transform(moist_adiabat, pres)
            fig.add_trace(
                go.Scatter(
                    x=skewed_temps,
                    y=pres,
                    mode="lines",
                    line=dict(color="rgba(0, 128, 0, 1)", width=0.5),
                    showlegend=False,
                    hoverinfo="none",
                )
            )

    # Calculate and add surface parcel profile
    def add_parcel_profile(df_time):
        # Order by decreasing pressure to avoid issues
        df_time = df_time.sort_values(by="pressure", ascending=False)
        # Get surface temperature and pressure
        surface_p = df_time["pressure"].max()
        surface_t = df_time[df_time["pressure"] == surface_p]["temperature"].iloc[0]
        surface_td = df_time[df_time["pressure"] == surface_p]["dewpoint"].iloc[0]

        # Calculate parcel profile
        pressure_levels = df_time["pressure"].values * units.hPa
        parcel_temps = (
            parcel_profile(
                pressure_levels, surface_t * units.degC, surface_td * units.degC
            )
            .to("degC")
            .magnitude
        )

        # Transform and add to plot
        skewed_temps = skew_transform(parcel_temps, pressure_levels.magnitude)

        return go.Scatter(
            x=skewed_temps,
            y=pressure_levels.magnitude,
            mode="lines",
            name="Parcel Profile",
            line=dict(color="black", dash="dash", width=3),
            showlegend=True,
            customdata=np.vectorize(lambda t, p: f"Pressure={p:.0f} hPa, Temperature={t:.1f}°C")(
                parcel_temps, pressure_levels.magnitude
            ),
            hovertemplate="<extra></extra>%{customdata}",
        )

    # Create figure
    fig = go.Figure()
    # Add background lines
    create_background_lines(fig)

    # Get the number of background traces
    base_trace_index = len(fig.data)

    # Add traces for temperature and dewpoint
    colors = {"temperature": "red", "dewpoint": "green"}
    names = {"temperature": "Temperature", "dewpoint": "Dewpoint"}
    variables_to_plot = ["temperature", "dewpoint"]

    # Transform variables for skewed coordinate system
    for var in variables_to_plot:
        df[f"{var}_skewed"] = skew_transform(df[var].values, df["pressure"].values)
    # Create initial traces
    for var in variables_to_plot:
        fig.add_trace(
            go.Scatter(
                x=df[df["time"] == df["time"].iloc[0]][f"{var}_skewed"],
                y=df[df["time"] == df["time"].iloc[0]]["pressure"],
                mode="lines+markers",
                name=names[var],
                line=dict(color=colors[var], width=3),
                marker=dict(size=8),
                showlegend=True,
                customdata=np.vectorize(
                    lambda t, p: f"Pressure={p:.0f} hPa, Temperature={t:.1f}°C"
                )(
                    df[df["time"] == df["time"].iloc[0]][f"{var}"],
                    df[df["time"] == df["time"].iloc[0]]["pressure"],
                ),
                hovertemplate="<extra></extra>%{customdata}",
            )
        )

    fig.add_trace(
        go.Scatter(
            x=[36] * len(df[df["time"] == df["time"].iloc[0]]["pressure"]),
            y=df[df["time"] == df["time"].iloc[0]]["pressure"],
            mode="markers",
            name="Winds",
            showlegend=True,
            marker=dict(
                size=15,
                color=df[df["time"] == df["time"].iloc[0]]["windspeed"],
                colorscale="YlOrBr",
                cmin=0,
                cmax=100,
                symbol="arrow",
                angle=df[df["time"] == df["time"].iloc[0]]["winddirection"] - 180.0,
                line=dict(width=0.5, color="DarkSlateGrey"),
            ),
        )
    )
    # Add initial parcel profile
    initial_time = df["time"].iloc[0]
    df_initial = df[df["time"] == initial_time]
    fig.add_trace(add_parcel_profile(df_initial))

    # Create frames for animation
    frames = []
    for time in df["time"].unique():
        df_time = df[df["time"] == time]
        frame_data = []
        for var in variables_to_plot:
            frame_data.append(
                go.Scatter(
                    x=df_time[f"{var}_skewed"],
                    y=df_time["pressure"],
                    mode="lines+markers",
                    name=names[var],
                    line=dict(color=colors[var]),  # Explicit color definition
                    showlegend=True,
                    customdata=np.vectorize(lambda t, p: f"Pressure={p:.0f} hPa, Temperature={t:.1f}°C")(df_time[f"{var}"], df_time["pressure"]),
                    hovertemplate="<extra></extra>%{customdata}",
                )
            )
        # Add parcel profile trace
        frame_data.append(add_parcel_profile(df_time))
        # add winds
        frame_data.append(
            go.Scatter(
                x=[36] * len(df_time["pressure"]),
                y=df_time["pressure"],
                mode="markers",
                name="Winds",
                showlegend=True,
                marker=dict(
                    size=15,
                    color=df_time["windspeed"],
                    colorscale="YlOrBr",
                    cmin=0,
                    cmax=100,
                    symbol="arrow",
                    angle=df_time["winddirection"] - 180.0,
                    line=dict(width=0.5, color="DarkSlateGrey"),
                ),
            )
        )
        frames.append(
            go.Frame(
                data=frame_data,
                name=str(time),
                layout=go.Layout(title=str(time)),
                traces=[
                    base_trace_index + i for i in range(len(variables_to_plot) + 2)
                ],
            )
        )

    fig.frames = frames

    # Update layout
    fig.update_layout(
        margin={"r": 50, "t": 80, "l": 50, "b": 5},
        title={
            "text": str(df["time"].iloc[0]),  # Initial time
            "y": 0.95,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        },
        xaxis_title="",
        xaxis_showticklabels=False,
        yaxis_title="Pressure (hPa)",
        yaxis_type="log",
        yaxis_showgrid=True,
        yaxis_range=[np.log10(1050), np.log10(195)],
        xaxis_range=[df['dewpoint'].min() + 60, df['temperature'].max() + 20],
        xaxis_showgrid=False,
        xaxis_zeroline=False,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99,
            bgcolor="rgba(255, 255, 255, 0.7)",
        ),
        sliders=[
            {
                "currentvalue": {"visible": False},
                "tickwidth": 0,
                "steps": [
                    {
                        "method": "animate",
                        "args": [
                            [str(time)],
                            {
                                "frame": {"duration": 0, "redraw": True},
                                "mode": "immediate",
                                "transition": {"duration": 0},
                            },
                        ],
                        "label": "",
                    }
                    for time in df["time"].unique()
                ],
            }
        ],
    )

    return fig


# CARDS for layout

fig_subplots = dcc.Graph(
    id=dict(type="figure", id="vertical"),
    config=images_config,
    style={"height": "90vh"},
)
