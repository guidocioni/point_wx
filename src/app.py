# notes
'''
This file is for housing the main dash application.
This is where we define the various css items to fetch as well as the layout of our application.
'''

# package imports
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

# local imports
from utils.settings import APP_HOST, APP_PORT, APP_DEBUG, URL_BASE_PATHNAME, cache
from components import navbar, footer

app = dash.Dash(
    __name__,
    url_base_pathname=URL_BASE_PATHNAME,
    use_pages=True,    # turn on Dash pages
    external_stylesheets=[
        dbc.themes.FLATLY,
        dbc.icons.FONT_AWESOME
    ],  # fetch the proper css items we want
    meta_tags=[
        {   # check if device is a mobile device. This is a must if you do any mobile styling
            'name': 'viewport',
            'content': 'width=device-width, initial-scale=1'
        }
    ],
    suppress_callback_exceptions=True,
    title='Dash app structure'
)

server = app.server
# Initialize cache
cache.init_app(server)

def serve_layout():
    '''Define the layout of the application'''
    return html.Div(
        [
            navbar(),
            dcc.Store(id='locations-list', data={}),
            dbc.Container(
                dash.page_container,
                class_name='my-2'
            ),
            footer
        ]
    )


app.layout = serve_layout   # set the layout to the serve_layout function

if __name__ == "__main__":
    app.run_server(
        host=APP_HOST,
        port=APP_PORT,
        debug=APP_DEBUG,
    )
