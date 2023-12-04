import dash_bootstrap_components as dbc
from dash import dcc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.settings import images_config
from PIL import Image


def make_temp_timeseries(df, showlegend=False):
    traces = []
    traces.append(
        go.Scatter(
            x=df['time'],
            y=df['t_max_mean'],
            mode='markers+lines+text',
            text=df['t_max_mean'].astype(int).astype(str) + ' °C',
            textposition="top right",
            textfont=dict(color='rgba(227, 56, 30, 1)'),
            name='Maximum temperature',
            line=dict(width=2, color='rgba(227, 56, 30, 1)'),
            showlegend=showlegend,),
    )
    traces.append(
        go.Scatter(
            x=df['time'],
            y=df['t_min_mean'],
            mode='markers+lines+text',
            text=df['t_min_mean'].astype(int).astype(str) + ' °C',
            textposition="top right",
            textfont=dict(color='rgba(58, 91, 139, 1)'),
            name='Minimum temperature',
            line=dict(width=2, color='rgba(58, 91, 139, 1)'),
            showlegend=showlegend),
    )
    traces.append(go.Scatter(
        x=df['time'],
        y=df['t_min_min'],
        mode='lines',
        line=dict(color='rgba(0, 0, 0, 0)'),
        name='',
        showlegend=showlegend
    ))
    traces.append(go.Scatter(
        x=df['time'],
        y=df['t_min_max'],
        mode='lines',
        line=dict(color='rgba(0, 0, 0, 0)'),
        fillcolor='rgba(58, 91, 139, 0.2)',
        fill='tonexty',
        name='',
        showlegend=showlegend
    ))
    traces.append(go.Scatter(
        x=df['time'],
        y=df['t_max_min'],
        mode='lines',
        line=dict(color='rgba(0, 0, 0, 0)'),
        name='',
        showlegend=showlegend
    ))
    traces.append(go.Scatter(
        x=df['time'],
        y=df['t_max_max'],
        mode='lines',
        line=dict(color='rgba(0, 0, 0, 0)'),
        fillcolor='rgba(227, 56, 30, 0.2)',
        fill='tonexty',
        name='',
        showlegend=showlegend
    ))
    return traces


def make_barplot_timeseries(df, var, var_text=None,
                            showlegend=False,
                            color='rgb(73, 135, 230)',
                            text_formatting='%{text:.1s}'):
    if var_text is not None:
        text = df[var_text]
    traces = []
    traces.append(go.Bar(
        x=df['time'],
        y=df[var],
        text=text,
        name='',
        textposition='auto',
        texttemplate=text_formatting,
        showlegend=showlegend,
        marker_color=color))

    return traces


def make_subplot_figure(data, title=None):
    traces_temp = make_temp_timeseries(data)
    traces_prec = make_barplot_timeseries(data,
                                          var='daily_prec_mean',
                                          var_text='prec_prob',
                                          text_formatting='%{text:.0f}%')
    traces_sun = make_barplot_timeseries(data,
                                         var='sunshine_mean',
                                         var_text='sunshine_mean',
                                         color='rgba(255, 240, 184, 0.5)',
                                         text_formatting='%{text:.1f} hrs')

    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.1, 0.5, 0.5],
        subplot_titles=['', '<b>Temperature<b>',
                        '<b>Precipitation (mm) / Precipitation probability (%)<b> / Sunshine'],
        specs=[[{"secondary_y": False}],
               [{"secondary_y": False}],
               [{"secondary_y": True}]]
    )

    for trace_temp in traces_temp:
        fig.add_trace(trace_temp, row=2, col=1)
    for trace_prec in traces_prec:
        fig.add_trace(trace_prec, row=3, col=1)
    for trace_sun in traces_sun:
        fig.add_trace(trace_sun, row=3, col=1, secondary_y=True)
    for _, row in data.iterrows():
        fig.add_shape(
            type='line',
            yref="y",
            xref="x",
            x0=row['time'],
            y0=row['daily_prec_min'],
            x1=row['time'],
            y1=row['daily_prec_max'],
            line=dict(color='rgba(0,0,0,0.3)', width=3),
            row=3, col=1)

    fig.add_trace(go.Scatter(
        x=data['time'],
        y=[3] * len(data['time']),
        mode='lines+text',
        text=data['time'].dt.strftime("<b>%a</b><br>%d %b"),
        textposition="top left",
        textfont=dict(color='rgba(1, 1, 1, 1)'),
        line=dict(color='rgba(0, 0, 0, 0)'),
        name='',
        showlegend=False
    ), row=1, col=1)
    for _, row in data.iterrows():
        fig.add_layout_image(dict(
            source=Image.open(row['icons']),
            xref='x',
            x=row['time'],
            yref='y',
            y=1,
            sizex=12*24*10*60*1000,
            sizey=2,
            xanchor="right",
            yanchor="bottom"
        ), row=1, col=1)

    fig.update_layout(
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True,),
        height=700,
        margin={"r": 5, "t": 40, "l": 0.1, "b": 0.1},
        barmode='overlay',
        legend=dict(orientation='h', y=-0.04),
    )

    fig.update_yaxes(title_text="2m Temp [°C]", row=2, col=1)
    fig.update_yaxes(title_text="Prec.", row=3, col=1)
    fig.update_yaxes(showgrid=True, gridwidth=2)
    fig.update_xaxes(minor=dict(showgrid=False),
                     tickformat='%a %d %b\n%H:%M', showgrid=True, gridwidth=2)
    fig.update_yaxes(showgrid=False, row=1, col=1, minor=dict(showgrid=False),
                     range=[1, 6], showticklabels=False)
    fig.update_xaxes(showgrid=False, row=1, col=1, minor=dict(showgrid=False))
    fig.update_yaxes(row=3, col=1, range=[18, 0], title_text='',
                     secondary_y=True, showgrid=False, showticklabels=False)
    if title is not None:
        fig.update_layout(title_text=title)

    return fig


# CARDS for layout

fig_subplots = dbc.Card(
    [
        dcc.Graph(id='meteogram-plot', config=images_config)
    ],
    className="mb-2",
)
