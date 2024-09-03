from dash import dcc
import plotly.express as px
import pandas as pd
from utils.settings import images_config

def make_heatmap(df, var, title=None):
    if var in ['temperature_2m', 'temperature_850hPa', 'dew_point_2m', 'apparent_temperature', 'surface_temperature']:
        cmap = 'RdBu_r'
    elif var in ['cloudcover', 'visibility']:
        cmap = 'YlGnBu_r'
    elif var == 'relative_humidity_2m':
        cmap = 'YlGnBu'
    elif var in ['rain', 'precipitation',
                 'accumulated_precip', 'accumulated_liquid']:
        cmap = 'dense'
    elif var in ['snowfall', 'snow_depth', 'accumulated_snow']:
        cmap = 'Burgyl'
    elif var in ['windgusts_10m', 'pressure_msl', 'wind_speed_10m' ,'wind_direction_10m', 'cape']:
        cmap = 'Hot_r'
    elif var == 'sunshine_duration':
        cmap = 'solar'
    else:
        cmap = 'RdBu_r'

    columns_regex = rf'{var}$|{var}_member(0[1-9]|[1-9][0-9])$'
    y_positions = list(range(df.loc[:, df.columns.str.match(columns_regex)].shape[1]))
    if var!='weather_code':
        fig = px.imshow(
            df.loc[:, df.columns.str.match(columns_regex)].T,
            x=df['time'],
            y=y_positions,
            text_auto=True,
            aspect='auto',
            color_continuous_scale=cmap,
            origin='lower')
        fig.update_traces(
            hovertemplate="<extra></extra><b>%{x|%a %-d %b %H:%M}</b><br>%{y}<br>Value = %{z}")
    else:
        from PIL import Image
        from utils.figures_utils import get_weather_icons
        import plotly.graph_objects as go
        fig = go.Figure()
        if df.shape[0] <= 46:
            freq = "3h"
        elif (df.shape[0] > 46) & (df.shape[0] <= 100):
            freq = "6h"
        else:
            freq = "12h"
        df = df.resample(freq, on="time").max().reset_index()
        times = df['time']
        # Loop through members and times to add images dynamically
        members_vars = df.loc[:, df.columns.str.match(columns_regex)].columns.to_list()
        for i, var in enumerate(members_vars):
            # Extract icons for the current model
            df = get_weather_icons(
                df,
                var=var,
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
                    
        fig.update_yaxes(
            range=[y_positions[0]-.5, y_positions[-1]+.2]
        )

    fig.update_layout(
        modebar=dict(orientation='v'),
        dragmode=False,
        xaxis=dict(showgrid=True, tickformat='%a %-d %b\n%H:%M'),
        yaxis=dict(showgrid=True, fixedrange=True, showticklabels=False,
                   title_text="Members"),
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
        fig.update_layout(title=dict(text=title, font=dict(size=14), yref='container', y=0.98))

    return fig


# CARDS for layout

fig_subplots = dcc.Graph(id=dict(type='figure', id='ensemble-heatmap'), config=images_config, style={'height':'95vh'})
