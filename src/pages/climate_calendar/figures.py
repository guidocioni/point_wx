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
        cmap = 'dense'
    elif graph_type == 'precipitation_days':
        df['precipitation_days'] = df['precipitation_sum'] >= 1.0
        out = df.pivot_table(
            index=df.time.dt.month,
            columns=df.time.dt.year,
            values="precipitation_days",
            aggfunc="sum",
        )
        cmap = 'Burgyl'
    elif graph_type == 'snow_days':
        df['snow_days'] = df['snowfall_sum'] >= 1.0
        out = df.pivot_table(
            index=df.time.dt.month,
            columns=df.time.dt.year,
            values="snow_days",
            aggfunc="sum",
        )
        cmap = 'Burgyl'
    elif graph_type == 'dry_days':
        df['dry_days'] = df['precipitation_sum'] < 1.0
        out = df.pivot_table(
            index=df.time.dt.month,
            columns=df.time.dt.year,
            values="dry_days",
            aggfunc="sum",
        )
        cmap = 'Burgyl'
    elif graph_type == 'frost_days':
        df['frost_days'] = df['temperature_2m_min'] <= 0
        out = df.pivot_table(
            index=df.time.dt.month,
            columns=df.time.dt.year,
            values="frost_days",
            aggfunc="sum",
        )
        cmap = "RdBu"
    elif graph_type == 'overcast_days':
        df['overcast_days'] = df['cloudcover_mean'] >= 80
        out = df.pivot_table(
            index=df.time.dt.month,
            columns=df.time.dt.year,
            values="overcast_days",
            aggfunc="sum",
        )
        cmap = 'YlGnBu_r'
    elif graph_type == 'partly_cloudy_days':
        df['partly_cloudy_days'] = (df['cloudcover_mean'] < 80) & (
        df['cloudcover_mean'] > 20)
        out = df.pivot_table(
            index=df.time.dt.month,
            columns=df.time.dt.year,
            values="partly_cloudy_days",
            aggfunc="sum",
        )
        cmap = 'YlGnBu'
    elif graph_type == 'sunny_days':
        df['sunny_days'] = df['cloudcover_mean'] <= 20
        out = df.pivot_table(
            index=df.time.dt.month,
            columns=df.time.dt.year,
            values="sunny_days",
            aggfunc="sum",
        )
        cmap = 'YlGnBu'
    elif graph_type == 'hot_days':
        df['hot_days'] = df['temperature_2m_max'] >= 30
        out = df.pivot_table(
            index=df.time.dt.month,
            columns=df.time.dt.year,
            values="hot_days",
            aggfunc="sum",
        )
        cmap = "RdBu_r"
    elif graph_type == 'tropical_nights':
        df['tropical_nights'] = df['temperature_2m_min'] >= 20
        out = df.pivot_table(
            index=df.time.dt.month,
            columns=df.time.dt.year,
            values="tropical_nights",
            aggfunc="sum",
        )
        cmap = "RdBu_r"
    elif graph_type == 'temperature_anomaly':
        df['temperature_anomaly'] = (df['temperature_2m_mean'] - df['temperature_2m_mean_clima'])
        out = df.pivot_table(
            index=df.time.dt.month,
            columns=df.time.dt.year,
            values="temperature_anomaly",
            aggfunc="mean",
        )
        out = out.round(1)
        cmap = "RdBu_r"
    elif graph_type == 'precipitation_anomaly':
        values = df.pivot_table(
            index=df.time.dt.month,
            columns=df.time.dt.year,
            values="precipitation_sum",
            aggfunc="sum",
        )
        clima = df.pivot_table(
            index=df.time.dt.month,
            columns=df.time.dt.year,
            values="precipitation_sum_clima",
            aggfunc="sum",
        )
        out = 100 * (values - clima) / clima
        out = out.round(1)
        cmap = "BrBg"
    else:
        raise ValueError()

    fig = px.imshow(
        out.values,
        x=out.columns.values,
        y=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        text_auto=True,
        aspect="auto",
        color_continuous_scale=cmap,
        origin="upper",
    )
    fig.update_traces(
        hovertemplate="<extra></extra><b>%{y} %{x}</b><br>Value = %{z}"
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
