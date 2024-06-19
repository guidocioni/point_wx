import plotly.graph_objects as go
import json
import dash_leaflet as dl
import os


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
        if str(int(row[var])) in j.keys():
            icons.append(icons_path+j[str(int(row[var]))][time_day]['image'])
            descriptions.append(j[str(int(row[var]))][time_day]['description'])
        else:
            icons.append('')
            descriptions.append('')

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


def make_map(lat_center=45, lon_center=10, zoom=3):
    mapURL = (
        'https://api.mapbox.com/styles/v1/guidocioni/ckmun175t3ejv17k7al4aax4b/tiles/{z}/{x}/{y}{r}'
        f"?access_token={os.environ['MAPBOX_KEY']}"
    )
    attribution = (
        '© <a href="https://www.mapbox.com/feedback/">'
        'Mapbox</a> © <a href="http://www.openstreetmap.org/copyright">'
        'OpenStreetMap</a>'
    )
    return dl.Map(
        [
            dl.FullScreenControl(),
            dl.LayersControl(
                [
                    dl.BaseLayer(
                        name="Map",
                        checked=True,
                        children=dl.TileLayer(
                            url=mapURL,
                            attribution=attribution,
                            tileSize=512,
                            zoomOffset=-1,
                        ),
                    ),
                    dl.Overlay(
                        name="Satellite",
                        checked=False,
                        children=dl.WMSTileLayer(
                            id="wms-layer-sat",
                            url="https://maps.dwd.de/geoserver/ows?",
                            layers="dwd:Satellite_worldmosaic_3km_world_ir108_3h",
                            format="image/png",
                            transparent=True,
                            opacity=0.7,
                            version="1.3.0",
                            detectRetina=True,
                        ),
                    ),
                ]
            ),
            dl.LayerGroup(id="map-scatter-layer"),
        ],
        center=[lat_center, lon_center],
        zoom=zoom,
        style={'width': '100%',
               'height': '35vh',
               'margin': "auto",
               "display": "block"
               },
        dragging=True,
        scrollWheelZoom=True,
        touchZoom=True,
        id='map')
