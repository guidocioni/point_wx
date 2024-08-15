from dash import dcc
import pandas as pd
from utils.settings import images_config, ASSETS_DIR
import plotly.graph_objects as go
import plotly.express as px


def make_heatmap(df, var, models, title=None):
    if var in ['temperature_2m', 'temperature_850hPa', 'dew_point_2m', 'apparent_temperature', 'surface_temperature']:
        cmap = 'RdBu_r'
    elif var in ['cloudcover', 'relative_humidity_2m']:
        cmap = 'YlGnBu_r'
    elif var in ['rain', 'precipitation',
                 'accumulated_precip', 'accumulated_liquid']:
        cmap = 'dense'
    elif var in ['snowfall', 'snow_depth', 'accumulated_snow']:
        cmap = 'Burgyl'
    elif var in ['windgusts_10m', 'pressure_msl', 'wind_speed_10m' ,'wind_direction_10m']:
        cmap = 'Hot_r'
    elif var == 'sunshine_duration':
        cmap = 'solar'
    else:
        cmap = 'RdBu_r'
    
    y_positions = list(range(len(models)))
    if var!='weather_code':
        fig = px.imshow(
            df.loc[:, df.columns.str.contains(var)].T,
            x=df['time'],
            y=y_positions,
            text_auto=True,
            aspect='equal',
            color_continuous_scale=cmap,
            origin='lower')
        fig.update_traces(
            hovertemplate="<extra></extra><b>%{x|%a %-d %b %H:%M}</b><br>%{y}<br>Value = %{z}")
        height=600
        showgrid=True
    else:
        from PIL import Image
        from utils.figures_utils import get_weather_icons
        fig = go.Figure()
        # TODO, adjust the interval here so that it uses the best option for the range of time!
        df = df.resample("6h", on="time").max().reset_index()
        times = df['time']
        # Loop through models and times to add images dynamically
        for i, model in enumerate(models):
            if len(models) > 1:
                var_weather_model = "weather_code_" + model
            else:
                var_weather_model = "weather_code"
            # Extract icons for the current model
            df = get_weather_icons(
                df,
                var=var_weather_model,
            )
            fig.add_trace(
                go.Scatter(
                    x=times,
                    y=[y_positions[i]] * len(times),
                    mode="text",
                    text="",
                    name="",
                    showlegend=False,
                ),
            )
            for _, row in df.iterrows():
                if row["icons"] != "":
                    fig.add_layout_image(
                        dict(
                            source=Image.open(row["icons"]),
                            x=row["time"],
                            y=y_positions[i],
                            sizex=12 * 24 * 10 * 60 * 100,
                            sizey=.5,
                            xref="x",
                            yref="y",
                            xanchor="center",
                            yanchor="middle",
                            layer='above'
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
        yaxis=dict(showgrid=showgrid, fixedrange=True, showticklabels=True,
                   zeroline=False, ticktext=models, tickmode='array', tickvals=y_positions),
        height=height,
        margin={"r": 5, "t": 40, "l": 5, "b": 5},
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
    if title is not None:
        fig.update_layout(title=dict(text=title, font=dict(size=14), yref='container', y=0.97))

    return fig

# CARDS for layout
fig_subplots = dcc.Graph(
    id=dict(type="figure", id="deterministic-heatmap"), config=images_config
)
