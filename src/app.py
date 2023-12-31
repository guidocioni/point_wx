import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from utils.settings import APP_HOST, APP_PORT, URL_BASE_PATHNAME, cache
from components import navbar, footer

app = dash.Dash(
    __name__,
    url_base_pathname=URL_BASE_PATHNAME,
    use_pages=True,
    external_stylesheets=[
        dbc.themes.FLATLY,
        dbc.icons.FONT_AWESOME
    ],
    meta_tags=[
        {   # check if device is a mobile device.
            'name': 'viewport',
            'content': 'width=device-width, initial-scale=1'
        }
    ],
    suppress_callback_exceptions=True,
    title='Point WX'
)

server = app.server
# Initialize cache
cache.init_app(server)

def serve_layout():
    '''Define the layout of the application'''
    return html.Div(
        [
            navbar(),
            dcc.Store(id='locations-list', data={}, storage_type='local'),
            dcc.Store(id='locations-selected', data={}, storage_type='local'),
            dbc.Modal(
                [
                    dbc.ModalHeader("Error"),
                    dbc.ModalBody("", id="error-message"),  # Placeholder for error message
                ],
                id="error-modal",
                size="lg",
                backdrop="static",
            ),
            dbc.Container(
                dash.page_container,
                class_name='my-2'
            ),
            footer
        ]
    )


app.layout = serve_layout

if __name__ == "__main__":
    app.run(
        host=APP_HOST,
        port=APP_PORT,
    )
