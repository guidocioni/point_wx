import plotly.graph_objects as go
import json
import dash_leaflet as dl
import os


def make_empty_figure(text="No data (yet 😃)"):
    '''Initialize an empty figure with style and a centered text'''
    fig = go.Figure()

    fig.add_annotation(x=2.5, y=1.5,
                       text=text,
                       showarrow=False,
                       font=dict(size=30))

    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )

    fig.update_layout(
        height=390,
        margin={"r": 0.1, "t": 0.1, "l": 0.1, "b": 0.1},
        template='plotly_white',
    )

    return fig


def get_weather_icons(df,
                      icons_path="../src/assets/yrno_png/",
                      mapping_path="../src/assets/weather_codes.json",
                      var='weather_code'):
    """
    Given an input dataframe with columns 'weather_code' and 'is_day'
    creates two new columns containing the path to the image describing
    that condition.
    """
    with open(mapping_path) as f:
        j = json.load(f)

    icons = []
    descriptions = []
    for _, row in df.iterrows():
        time_day = 'day'
        if 'is_day' in df.columns:
            if row['is_day'] == 1:
                time_day = 'day'
            else:
                time_day = 'night'
        icons.append(icons_path+j[str(int(row[var]))][time_day]['image'])
        descriptions.append(j[str(int(row[var]))][time_day]['description'])

    df['icons'] = icons
    df['weather_descriptions'] = descriptions

    return df


def attach_alpha_to_hex_color(alpha, color):
    """Apply opacity to an hex color

    Args:
        alpha (float): Between 0 and 1
        color (str): Hex color string

    Returns:
        str: New hex color string with opacity
    """
    # Calculate the equivalent alpha value in the range of 0 to 255
    alphaInt = (alpha * 255).__round__()
    # Convert alphaInt to hexadecimal string
    alphaHex = hex(alphaInt)[2:].upper().zfill(2)
    #
    return color + alphaHex


def hex2rgba(x):
    if len(x) < 6:
        return "rgba" + str(tuple(17 * int(x[n+1], 16) * (1 if n < 3 else 1/255) for n in range(len(x) - 1)))
    else:
        return "rgba" + str(tuple(int(x[2*n+1:2*n+3], 16) * (1 if n < 3 else 1/255) for n in range(len(x) // 2)))


def make_map(lat_center=45, lon_center=10, zoom=2):
    mapURL = (
        'https://api.mapbox.com/styles/v1/mapbox/dark-v10/tiles/{z}/{x}/{y}{r}'
        f"?access_token={os.environ['MAPBOX_KEY']}"
    )
    attribution = (
        '© <a href="https://www.mapbox.com/feedback/">'
        'Mapbox</a> © <a href="http://www.openstreetmap.org/copyright">'
        'OpenStreetMap</a>'
    )
    return dl.Map(
        [
            dl.TileLayer(url=mapURL,
                         attribution=attribution,
                         tileSize=512,
                         zoomOffset=-1),
            dl.LayerGroup(id="map-scatter-layer"),
        ],
        center=[lat_center, lon_center],
        zoom=zoom,
        style={'width': '100%',
               'height': '30vh',
               'margin': "auto",
               "display": "block"
               },
        dragging=True,
        scrollWheelZoom=False,
        id='map')
