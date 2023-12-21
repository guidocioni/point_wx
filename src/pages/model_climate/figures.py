import dash_bootstrap_components as dbc
from dash import html
from dash import dcc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.settings import images_config


x = ['Jan', 'Feb', 'Mar', 'Apr', 'May',
     'Jun', 'Jul', 'Aug', 'Sep', 'Oct',
     'Nov', 'Dec']


def make_temp_prec_climate_figure(df):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    traces = []
    traces.append(
        go.Bar(
            x=x,
            y=df['monthly_rain'],
            name='Precipitation',
            opacity=0.4,
            marker=dict(color='blue'),
            showlegend=True),
    )
    traces.append(
        go.Scatter(
            x=x,
            y=df['t2m_max_mean'],
            mode='markers+lines+text',
            text=df['t2m_max_mean'].astype(int).astype(str) + ' °C',
            textposition="top center",
            textfont=dict(color='red'),
            name='Mean Daily Maximum',
            line=dict(width=2, color='red'),
            showlegend=True,),
    )
    traces.append(
        go.Scatter(
            x=x,
            y=df['t2m_min_mean'],
            mode='markers+lines+text',
            text=df['t2m_min_mean'].astype(int).astype(str) + ' °C',
            textposition="top center",
            textfont=dict(color='blue'),
            name='Mean Daily Minimum',
            line=dict(width=2, color='blue'),
            showlegend=True),
    )
    traces.append(
        go.Scatter(
            x=x,
            y=df['t2m_min_min'],
            mode='markers+lines',
            name='Cold nights',
            line=dict(width=2, color='blue', dash='dash'),
            showlegend=True),
    )
    traces.append(
        go.Scatter(
            x=x,
            y=df['t2m_max_max'],
            mode='markers+lines',
            name='Hot days',
            line=dict(width=2, color='red', dash='dash'),
            showlegend=True),
    )

    fig.add_trace(traces[0], row=1, col=1, secondary_y=True)
    for trace in traces[1:5]:
        fig.add_trace(trace, row=1, col=1)

    fig.update_layout(
        margin={"r": 0.1, "t": 0.1, "l": 0.1, "b": 0.1},
        barmode='stack',
        legend=dict(orientation='h')
    )

    fig.update_yaxes(row=1, col=1,
                     secondary_y=True, title='mm', showgrid=False)
    fig.update_yaxes(row=1, col=1,
                     secondary_y=False, title='°C', showgrid=False)

    return fig


def make_clouds_climate_figure(df):
    fig = make_subplots()
    traces = []

    traces.append(
        go.Bar(
            x=x,
            y=df['sunny_days'],
            text=df['sunny_days'],
            textfont=dict(color='gold'),
            name='Sunny',
            opacity=0.9,
            marker=dict(color='yellow'),
            showlegend=True,),
    )
    traces.append(
        go.Bar(
            x=x,
            y=df['partly_cloudy_days'],
            name='Partly Cloudy',
            text=df['partly_cloudy_days'],
            textfont=dict(color='yellow'),
            opacity=0.9,
            marker=dict(color='gold'),
            showlegend=True,),
    )
    traces.append(
        go.Bar(
            x=x,
            y=df['overcast_days'],
            name='Overcast',
            text=df['overcast_days'],
            textfont=dict(color='white'),
            opacity=0.9,
            marker=dict(color='gray'),
            showlegend=True,),
    )
    traces.append(
        go.Scatter(
            x=x,
            y=df['wet_days'],
            mode='markers+lines+text',
            text=df['wet_days'].astype(int).astype(str),
            textposition="top center",
            textfont=dict(color='blue'),
            name='Precipitation days',
            line=dict(width=2, color='blue'),
            showlegend=True,),
    )

    for trace in traces:
        fig.add_trace(trace)

    fig.update_layout(
        margin={"r": 0.1, "t": 0.1, "l": 0.1, "b": 0.1},
        barmode='stack',
        legend=dict(orientation='h')
    )

    fig.update_yaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)

    return fig


def make_temperature_climate_figure(df):
    fig = make_subplots()
    traces = []

    traces.append(
        go.Bar(
            x=x,
            y=df['t_max_gt_30_days'],
            name='>30°C',
            text=df['t_max_gt_30_days'],
            textfont=dict(color='white'),
            opacity=0.9,
            marker=dict(color='rgb(241,113,28)'),
            showlegend=True),
    )
    traces.append(
        go.Bar(
            x=x,
            y=df['t_max_gt_25_days'],
            name='>25°C',
            text=df['t_max_gt_25_days'],
            textfont=dict(color='white'),
            opacity=0.9,
            marker=dict(color='rgb(246,204,35)'),
            showlegend=True),
    )
    traces.append(
        go.Bar(
            x=x,
            y=df['t_max_gt_20_days'],
            name='>20°C',
            text=df['t_max_gt_20_days'],
            textfont=dict(color='white'),
            opacity=0.9,
            marker=dict(color='rgb(253,246,33)'),
            showlegend=True),
    )
    traces.append(
        go.Bar(
            x=x,
            y=df['t_max_gt_15_days'],
            name='>15°C',
            text=df['t_max_gt_15_days'],
            textfont=dict(color='white'),
            opacity=0.9,
            marker=dict(color='rgb(193,252,58)'),
            showlegend=True),
    )
    traces.append(
        go.Bar(
            x=x,
            y=df['t_max_gt_10_days'],
            name='>10°C',
            text=df['t_max_gt_10_days'],
            textfont=dict(color='white'),
            opacity=0.9,
            marker=dict(color='rgb(92,223,83)'),
            showlegend=True),
    )
    traces.append(
        go.Bar(
            x=x,
            y=df['t_max_gt_5_days'],
            name='>5°C',
            text=df['t_max_gt_5_days'],
            textfont=dict(color='white'),
            opacity=0.9,
            marker=dict(color='rgb(174,232,246)'),
            showlegend=True),
    )
    traces.append(
        go.Bar(
            x=x,
            y=df['t_max_gt_0_days'],
            name='>0°C',
            text=df['t_max_gt_0_days'],
            textfont=dict(color='white'),
            opacity=0.9,
            marker=dict(color='rgb(96,175,245)'),
            showlegend=True),
    )
    traces.append(
        go.Bar(
            x=x,
            y=df['t_max_lt_0_days'],
            name='<0°C',
            text=df['t_max_lt_0_days'],
            textfont=dict(color='white'),
            opacity=0.9,
            marker=dict(color='rgb(76,139,236)'),
            showlegend=True),
    )
    traces.append(
        go.Bar(
            x=x,
            y=df['t_max_lt_m5_days'],
            name='<-5°C',
            text=df['t_max_lt_m5_days'],
            textfont=dict(color='white'),
            opacity=0.9,
            marker=dict(color='rgb(76,139,236)'),
            showlegend=True,),
    )
    traces.append(
        go.Scatter(
            x=x,
            y=df['frost_days'],
            mode='markers+lines+text',
            text=df['frost_days'].astype(int).astype(str),
            textposition="top center",
            textfont=dict(color='black'),
            name='Frost days',
            line=dict(width=2, color='black'),
            showlegend=True),
    )

    for trace in traces:
        fig.add_trace(trace)

    fig.update_layout(
        margin={"r": 0.1, "t": 0.1, "l": 0.1, "b": 0.1},
        barmode='stack',
        legend=dict(orientation='h')
    )

    fig.update_yaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)

    return fig


def make_precipitation_climate_figure(df):
    fig = make_subplots()
    traces = []

    traces.append(
        go.Bar(
            x=x,
            y=df['p_50_100_days'],
            name='50-100 mm',
            text=df['p_50_100_days'],
            textfont=dict(color='white'),
            opacity=0.9,
            marker=dict(color='rgb(144,18,224)'),
            showlegend=True,),
    )
    traces.append(
        go.Bar(
            x=x,
            y=df['p_20_50_days'],
            name='20-50 mm',
            text=df['p_20_50_days'],
            textfont=dict(color='white'),
            opacity=0.9,
            marker=dict(color='rgb(95,40,239)'),
            showlegend=True,),
    )
    traces.append(
        go.Bar(
            x=x,
            y=df['p_10_20_days'],
            name='10-20 mm',
            text=df['p_10_20_days'],
            textfont=dict(color='white'),
            opacity=0.9,
            marker=dict(color='rgb(48,59,240)'),
            showlegend=True,),
    )
    traces.append(
        go.Bar(
            x=x,
            y=df['p_5_10_days'],
            name='5-10 mm',
            text=df['p_5_10_days'],
            textfont=dict(color='white'),
            opacity=0.9,
            marker=dict(color='rgb(28,142,237)'),
            showlegend=True,),
    )
    traces.append(
        go.Bar(
            x=x,
            y=df['p_2_5_days'],
            name='2-5 mm',
            text=df['p_2_5_days'],
            textfont=dict(color='white'),
            opacity=0.9,
            marker=dict(color='rgb(123,194,245)'),
            showlegend=True,),
    )
    traces.append(
        go.Bar(
            x=x,
            y=df['p_lt_2_days'],
            name='<2 mm',
            text=df['p_lt_2_days'],
            textfont=dict(color='white'),
            opacity=0.9,
            marker=dict(color='rgb(159,224,245)'),
            showlegend=True,),
    )
    traces.append(
        go.Bar(
            x=x,
            y=df['dry_days'],
            name='Dry days',
            text=df['dry_days'],
            textfont=dict(color='white'),
            opacity=0.9,
            marker=dict(color='rgb(224,220,114)'),
            showlegend=True,),
    )
    traces.append(
        go.Scatter(
            x=x,
            y=df['snow_days'],
            mode='markers+lines+text',
            text=df['snow_days'].astype(int),
            textposition="top center",
            textfont=dict(color='black'),
            name='Snow Days',
            line=dict(width=2, color='black'),
            showlegend=True,),
    )

    for trace in traces:
        fig.add_trace(trace)

    fig.update_layout(
        margin={"r": 0.1, "t": 0.1, "l": 0.1, "b": 0.1},
        barmode='stack',
        legend=dict(orientation='h')
    )

    fig.update_yaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)

    return fig


def make_winds_climate_figure(df):
    fig = make_subplots()
    traces = []

    traces.append(
        go.Bar(
            x=x,
            y=df['w_gt_61_days'],
            name='>61 km/h',
            text=df['w_gt_61_days'],
            textfont=dict(color='white'),
            opacity=0.9,
            marker=dict(color='rgb(245,134,38)'),
            showlegend=True,),
    )
    traces.append(
        go.Bar(
            x=x,
            y=df['w_gt_50_days'],
            name='>50 km/h',
            text=df['w_gt_50_days'],
            textfont=dict(color='white'),
            opacity=0.9,
            marker=dict(color='rgb(226,225,53)'),
            showlegend=True,),
    )
    traces.append(
        go.Bar(
            x=x,
            y=df['w_gt_38_days'],
            name='>38 km/h',
            text=df['w_gt_38_days'],
            textfont=dict(color='white'),
            opacity=0.9,
            marker=dict(color='rgb(122,171,36)'),
            showlegend=True,),
    )
    traces.append(
        go.Bar(
            x=x,
            y=df['w_gt_28_days'],
            name='>28 km/h',
            text=df['w_gt_28_days'],
            textfont=dict(color='white'),
            opacity=0.9,
            marker=dict(color='rgb(0,139,85)'),
            showlegend=True,),
    )
    traces.append(
        go.Bar(
            x=x,
            y=df['w_gt_19_days'],
            name='>19 km/h',
            text=df['w_gt_19_days'],
            textfont=dict(color='white'),
            opacity=0.9,
            marker=dict(color='rgb(0,184,44)'),
            showlegend=True,),
    )
    traces.append(
        go.Bar(
            x=x,
            y=df['w_gt_12_days'],
            name='>12 km/h',
            text=df['w_gt_12_days'],
            textfont=dict(color='white'),
            opacity=0.9,
            marker=dict(color='rgb(74,218,102)'),
            showlegend=True,),
    )
    traces.append(
        go.Bar(
            x=x,
            y=df['w_gt_5_days'],
            name='>5 km/h',
            text=df['w_gt_5_days'],
            textfont=dict(color='white'),
            opacity=0.9,
            marker=dict(color='rgb(113,247,153)'),
            showlegend=True,),
    )
    traces.append(
        go.Bar(
            x=x,
            y=df['w_gt_1_days'],
            name='>1 km/h',
            text=df['w_gt_1_days'],
            textfont=dict(color='white'),
            opacity=0.9,
            marker=dict(color='rgb(152,250,206)'),
            showlegend=True,),
    )
    traces.append(
        go.Bar(
            x=x,
            y=df['w_calm_days'],
            name='Calm',
            text=df['w_calm_days'],
            textfont=dict(color='white'),
            opacity=0.9,
            marker=dict(color='rgb(217,209,209)'),
            showlegend=True,),
    )

    for trace in traces:
        fig.add_trace(trace)

    fig.update_layout(
        margin={"r": 0.1, "t": 0.1, "l": 0.1, "b": 0.1},
        barmode='stack',
        legend=dict(orientation='h')
    )

    fig.update_yaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)

    return fig


# CARDS for layout
fig_temp_prec_climate = dbc.Card(
    [
        html.Div([
            "The typical evolution of average minimum and maximum temperatures for every month ",
            "are shown in the red and blue solid lines. ",
            html.Br(),
            "The dashed lines show instead the extremes that you can expect at this location. ",
            html.Br(),
            "The blue bars show the monthly cumulated precipitation as average."
        ], className="mb-2"
        ),
        dcc.Graph(id='temp-prec-climate-figure', config=images_config)
    ],
    className="mb-2",
    body=True,
)

fig_clouds_climate = dbc.Card(
    [
        html.Div([
            "Here we show the number of days with overcast (>80% cloud cover), "
            "partly cloudy (20-80%) and sunny (<20%) days.",
            html.Br(),
            "The number of precipitation days (>= 1 mm) are also shown."
        ], className="mb-2"),
        dcc.Graph(id='clouds-climate-figure', config=images_config)
    ],
    className="mb-2",
    body=True,
)

fig_temperature_climate = dbc.Card(
    [
        html.Div(
            ["The number of days that exceed a certain temperature threshold are shown in this plot.",
             html.Br(),
             "Frost days (daily minimum temperature <= 0°C) are also shown"
             ],
            className="mb-2"
        ),
        dcc.Graph(id='temperature-climate-figure', config=images_config)
    ],
    className="mb-2",
    body=True,
)

fig_precipitation_climate = dbc.Card(
    [
        html.Div(
            ["The number of days that exceed a certain precipitation threshold are shown in this plot.",
             html.Br(),
             "Snow days (>= 1 cm) are also shown"
             ],
            className="mb-2"
        ),
        dcc.Graph(id='precipitation-climate-figure', config=images_config)
    ],
    className="mb-2",
    body=True,
)

fig_winds_climate = dbc.Card(
    [
        html.Div(
            "The number of days that exceed a certain wind speed threshold are shown in this plot. "
            "Note that we use the average of maximum wind speed at 10m. ",
            className="mb-2"
        ),
        dcc.Graph(id='winds-climate-figure', config=images_config)
    ],
    className="mb-2",
    body=True,
)
