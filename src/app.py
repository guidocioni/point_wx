import dash
from dash import html, dcc, callback, Output, Input, clientside_callback, MATCH
import dash_bootstrap_components as dbc
from utils.settings import APP_HOST, APP_PORT, URL_BASE_PATHNAME, cache
from components import navbar, footer
from flask import request
from utils.custom_logger import logging

app = dash.Dash(
    __name__,
    url_base_pathname=URL_BASE_PATHNAME,
    use_pages=True,
    external_stylesheets=[dbc.themes.FLATLY, dbc.icons.FONT_AWESOME],
    # meta_tags=[
    #     {   # check if device is a mobile device.
    #         'name': 'viewport',
    #         'content': 'width=device-width, initial-scale=1'
    #     }
    # ],
    suppress_callback_exceptions=True,
    title="Point WX",
)

server = app.server
# Initialize cache
cache.init_app(server)


def serve_layout():
    """Define the layout of the application"""
    return html.Div(
        [
            navbar(),
            dcc.Location(id="url", refresh=False),
            dcc.Store(id="locations-list", data={}, storage_type="local"),
            dcc.Store(id="location-selected", data={}, storage_type="local"),
            dcc.Store(id='location-favorites', data=[], storage_type="local"),
            dcc.Store(id="client-details", data={}, storage_type="session"),
            dcc.Store(id="garbage"),
            dbc.Modal(
                [
                    dbc.ModalHeader("Error"),
                    dbc.ModalBody(
                        "", id="error-message"
                    ),  # Placeholder for error message
                ],
                id="error-modal",
                size="lg",
                backdrop="static",
            ),
            dbc.Container(dash.page_container, class_name="my-2", id="content"),
            footer,
        ],
        id="app-div",
    )


app.layout = serve_layout


@callback(Output("client-details", "data"), Input("app-div", "id"))
def ip(id):
    # client_details = request.__dict__
    client_address = request.environ.get("HTTP_X_REAL_IP", request.remote_addr)
    logging.info(f"New session for IP {client_address}")

    return str(request.__dict__)


@callback(
    [
        Output(
            {"type": "navbar-link", "index": page["relative_path"].split("/")[-1]},
            "active",
        )
        for page in dash.page_registry.values()
    ],
    [Input("url", "pathname")],
)
def update_navbar_links(pathname):
    """
    Update the "active" property of the Navbar items to highlight which
    element is active
    """
    return [pathname == page["relative_path"] for page in dash.page_registry.values()]


page_titles = {
    page["relative_path"]: page["title"] for page in dash.page_registry.values()
}


@callback(Output("navbar-title-for-mobile", "children"),
          [Input("url", "pathname"),
           Input("navbar-collapse", "is_open")]
          )
def update_navbar_title(pathname, is_open):
    '''
    Update the navbar title (only on mobile) with the page title every time 
    the page is changed. Also check if navbar is collapsed
    '''
    if not is_open:
        return page_titles.get(pathname, "")
    else:
        return ""


@callback(
    Output({"type":"submit-button", "index": MATCH}, "disabled"),
    Input("location_search_new", "value"),
)
def activate_submit_button(location):
    '''
    Disable submit button (on all pages) unless
    a location has been selected
    '''
    if location is None:
        return True
    return False


@callback(
    Output({"type":"fade", "index": MATCH}, 'is_open',),
    Input({"type":"submit-button", "index": MATCH}, "n_clicks"),
    prevent_initial_call=True
)
def toggle_fade(n):
    '''
    Open the collapse element containing the plots once 
    the submit button has been pressed (on all pages)
    '''
    if not n:
        # Button has never been clicked
        return False
    return True


clientside_callback(
    """function (id) {
        var myID = document.getElementById(id)
        var myScrollFunc = function() {
          var y = window.scrollY;
          if (y >= 200) {
            myID.style.display = ""
          } else {
            myID.style.display = "none"
          }
        };
        window.addEventListener("scroll", myScrollFunc);
        return window.dash_clientside.no_update
    }""",
    Output("back-to-top-button", "id"),
    Input("back-to-top-button", "id"),
)

if __name__ == "__main__":
    app.run(
        host=APP_HOST,
        port=APP_PORT,
    )
