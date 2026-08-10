from dash import dcc
import pandas as pd
from utils.settings import images_config, DEFAULT_TEMPLATE
from utils.figures_utils import (
    attach_alpha_to_hex_color, hex2rgba, add_attribution, wrap_comma_separated,
    estimate_legend_rows,
)
from utils.weather_emoji import get_weather_emoji_series
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio


def make_heatmap(df, var, models, title=None):
    # Create readable variable name for hover
    var_display = var.replace("_", " ").title()
    if var in ['temperature_2m', 'temperature_850hPa', 'dew_point_2m', 'apparent_temperature', 'surface_temperature', 'temperature_500hPa', 'soil_temperature_0cm', 'soil_temperature_6cm', 'soil_temperature_18cm', 'soil_temperature_54cm']:
        cmap = 'RdBu_r'
    elif var in ['cloudcover', 'cloud_cover_low', 'cloud_cover_mid', 'cloud_cover_high']:
        cmap = 'YlGnBu_r'
    elif var in ['relative_humidity_2m', 'relative_humidity_850hPa', 'relative_humidity_500hPa']:
        cmap = 'YlGnBu'
    elif var in ['rain', 'precipitation',
                 'accumulated_precip', 'accumulated_liquid', 'showers', 'soil_moisture_0_to_1cm', 'soil_moisture_1_to_3cm' ,'soil_moisture_3_to_9cm', 'soil_moisture_9_to_27cm', 'soil_moisture_27_to_81cm']:
        cmap = 'dense'
    elif var in ['snowfall', 'snow_depth', 'accumulated_snow']:
        cmap = 'Burgyl'
    elif var in ['windgusts_10m', 'pressure_msl', 'wind_speed_10m' ,'wind_direction_10m', 'wind_speed_120m', 'wind_direction_120m', 'cape']:
        cmap = 'Hot_r'
    elif var in ['sunshine_duration', 'visibility']:
        cmap = 'solar'
    else:
        cmap = 'RdBu_r'

    # Models are shown as y-axis labels, no need to duplicate in subtitle
    if title is not None:
        title_text = f"{title}<br><sup>Variable = <b>{var}</b></sup>"
        margin_t = 40
    else:
        margin_t = 40
        title_text = None

    y_positions = list(range(len(models)))
    if var!='weather_code':
        z = df.loc[:, df.columns.str.contains(var)].T
        fig = px.imshow(
            z,
            x=df['time'],
            y=y_positions,
            text_auto=True,
            aspect='auto',  # Use auto to allow dynamic height based on number of models
            color_continuous_scale=cmap,
            origin='lower')
        # customdata carries the model name per row since y is numeric (row index), not the label
        fig.update_traces(
            customdata=[[model] * z.shape[1] for model in models],
            hovertemplate=f"<extra></extra><b>%{{x|%a %-d %b %H:%M}}</b><br>Model: %{{customdata}}<br>{var_display} = %{{z}}")
        # Dynamic height based on number of models
        # Compact rows since model info is shown in hover, not y-axis labels
        height = 300 + len(models) * 35
        showgrid=True
    else:
        # Weather code heatmap with unicode emoji (much faster than PNG loop)
        from utils.figures_utils import get_weather_icons

        fig = go.Figure()

        n_models = len(models)

        # Adaptive resampling - more aggressive for many models
        if n_models > 10:
            df = df.resample("12h", on="time").max().reset_index()
        else:
            df = df.resample("6h", on="time").max().reset_index()

        times = df['time']

        # Adaptive emoji size based on number of models
        if n_models <= 5:
            emoji_size = 24
        elif n_models <= 10:
            emoji_size = 20
        elif n_models <= 15:
            emoji_size = 16
        else:
            emoji_size = 14

        # Add one scatter trace per model row with emoji text
        for i, model in enumerate(models):
            if len(models) > 1:
                var_weather_model = "weather_code_" + model
            else:
                var_weather_model = "weather_code"

            # Get weather descriptions for hover
            df_with_descriptions = get_weather_icons(df.copy(), var=var_weather_model)

            # Convert weather codes to emoji
            weather_emoji = get_weather_emoji_series(df[var_weather_model])

            fig.add_trace(
                go.Scatter(
                    x=times,
                    y=[y_positions[i]] * len(times),
                    mode="text",
                    text=weather_emoji,
                    textfont=dict(size=emoji_size),
                    customdata=df_with_descriptions["weather_descriptions"],
                    name="",
                    showlegend=False,
                    hovertemplate=f"<extra></extra><b>%{{x|%a %-d %b %H:%M}}</b><br>Model: {model}<br>%{{customdata}}",
                ),
            )

        height=len(y_positions) * 120
        showgrid=False
        fig.update_yaxes(
            range=[y_positions[0]-.5, y_positions[-1]+.2]
        )

    fig.update_layout(
        modebar=dict(orientation='v'),
        dragmode=False,
        xaxis=dict(showgrid=showgrid, tickformat='%a %-d %b\n%H:%M'),
        yaxis=dict(showgrid=showgrid, fixedrange=True, showticklabels=False,
                   zeroline=False, title_text=f"{len(models)} models"),
        height=height,
        margin={"r": 5, "t": margin_t, "l": 5, "b": 5},
        updatemenus=[
            dict(
                type="buttons",
                x=0.5,
                y=-0.09,
                xanchor='center',
                direction='right',
                buttons=[
                    dict(label="24H",
                         method="relayout",
                         args=[{"xaxis.range[0]": df['time'].min() - pd.to_timedelta('0.5h'),
                                "xaxis.range[1]": df['time'].min() + pd.to_timedelta('24.5h')}]),
                    dict(label="48H",
                         method="relayout",
                         args=[{"xaxis.range[0]": df['time'].min() - pd.to_timedelta('0.5h'),
                                "xaxis.range[1]": df['time'].min() + pd.to_timedelta('48.5h')}]),
                    dict(label="Reset",
                         method="relayout",
                         args=[{"xaxis.range[0]": df['time'].min() - pd.to_timedelta('0.5h'),
                                "xaxis.range[1]": df['time'].max() + pd.to_timedelta('0.5h')}]),
                ],
                pad=dict(b=5),
            ),
        ],
    )

    fig.update_coloraxes(showscale=False)
    if title_text is not None:
        fig.update_layout(title=dict(text=title_text, font=dict(size=14), yref='container', y=0.97))

    return add_attribution(fig)


def make_lineplot(
    df, var, models, mode="lines+markers", showlegend=True, fill="none", alpha=1, title=None, showgrid=True, clima=None
):
    fig = go.Figure()
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
                    legendgroup=model,
                    fill=fill,
                ),
            )
        i += 1
    for trace in traces:
        fig.add_trace(trace)

    if clima is not None and var in clima.columns:
        # Match climatology's (doy, hour) rows onto an hourly time axis
        # spanning the actual data's bounds, then add a single overlay trace
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

        clima = clima.copy()
        clima["doy_hour"] = clima["doy"] + clima["hour"].astype(str).str.zfill(2)
        clima = clima.merge(time_sel, left_on="doy_hour", right_on="time_selection_str")
        clima = (
            clima.drop(columns=["doy_hour", "doy", "hour", "time_selection_str"])
            .sort_values(by="time_selection")
            .rename(columns={"time_selection": "time"})
            .interpolate()
            .round(1)
        )

        fig.add_trace(
            go.Scatter(
                x=clima["time"],
                y=clima[var],
                mode="lines",
                name="ERA5 Climatology",
                line=dict(width=4, color="rgba(0, 0, 0, 0.3)"),
                hovertemplate="<b>%{x|%a %-d %b %H:%M}</b>, " + var + " = %{y}",
                showlegend=False,
            )
        )

    legend = dict(
        orientation="h",
        yref="container",
        yanchor="top", y=0.965, xanchor="left", x=0,
        font=dict(size=10),
        groupclick="togglegroup",
        tracegroupgap=0,
        bgcolor="rgba(255,255,255,0)",
    )
    margin_t = 55 + estimate_legend_rows(models) * 22 if showlegend else 40

    fig.update_layout(
        modebar=dict(orientation='v'),
        dragmode=False,
        xaxis=dict(showgrid=showgrid, tickformat='%a %-d %b\n%H:%M'),
        yaxis=dict(showgrid=showgrid, fixedrange=True),
        margin={"r": 5, "t": margin_t, "l": 5, "b": 5},
        legend=legend,
        updatemenus=[
            dict(
                type="buttons",
                x=0.5,
                y=-0.09,
                xanchor='center',
                direction='right',
                buttons=[
                    dict(label="24H",
                         method="relayout",
                         args=[{"xaxis.range[0]": df['time'].min() - pd.to_timedelta('0.5h'),
                                "xaxis.range[1]": df['time'].min() + pd.to_timedelta('24.5h')}]),
                    dict(label="48H",
                         method="relayout",
                         args=[{"xaxis.range[0]": df['time'].min() - pd.to_timedelta('0.5h'),
                                "xaxis.range[1]": df['time'].min() + pd.to_timedelta('48.5h')}]),
                    dict(label="Reset",
                         method="relayout",
                         args=[{"xaxis.range[0]": df['time'].min() - pd.to_timedelta('0.5h'),
                                "xaxis.range[1]": df['time'].max() + pd.to_timedelta('0.5h')}]),
                ],
                pad=dict(b=5),
            ),
        ],
    )
    if title is not None:
        title_text = f"{title}<br><sup>Variable = <b>{var}</b></sup>"
        fig.update_layout(title=dict(text=title_text, font=dict(size=14), yref='container', y=0.98))

    return add_attribution(fig)


# CARDS for layout
images_config['toImageButtonOptions'].update({'width': 1100, 'height': 600})
fig_subplots = dcc.Graph(
    id=dict(type="figure", id="deterministic-heatmap"), config=images_config
)
