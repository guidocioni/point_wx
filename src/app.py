import dash
import uuid
from dash import (
    html,
    dcc,
    callback,
    Output,
    Input,
    clientside_callback,
    MATCH,
    State,
    ALL,
)
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from utils.settings import APP_PORT, URL_BASE_PATHNAME, cache
from components import navbar, footer
from flask import request, redirect
from utils.custom_logger import logging
from utils.ai_utils import create_ai_report
from datetime import datetime

app = dash.Dash(
    __name__,
    url_base_pathname=URL_BASE_PATHNAME,
    use_pages=True,
    external_stylesheets=[
        dbc.themes.FLATLY,
        dbc.icons.FONT_AWESOME,
        "https://unpkg.com/@mantine/dates@7/styles.css",
    ],
    meta_tags=[
        {  # check if device is a mobile device.
            "name": "viewport",
            "content": "width=device-width, initial-scale=1",
        }
    ],
    suppress_callback_exceptions=True,
    title="Point WX",
)

server = app.server


# Redirect the root to the home (to be tested)
@server.route("/")
def redirect_to_basepath():
    return redirect(request.url_root.rstrip("/") + URL_BASE_PATHNAME)


@server.route(f"/{URL_BASE_PATHNAME}/report", methods=["GET", "POST"])
def create_weather_report():
    address_search = request.args.get("address")
    date_forecast = request.args.get("date", datetime.now().strftime("%Y-%m-%d"))
    additional_prompt = request.args.get("prompt")
    if (
        address_search is None
        or len(address_search) < 1
        or date_forecast is None
        or len(date_forecast) != 10
    ):
        return {}
    logging.info(
            f"Making request to /report with address={address_search}, date={date_forecast}, prompt={additional_prompt}"
        )
    report = create_ai_report(address_search, date_forecast, additional_prompt)

    return {
        "search": address_search,
        "date": date_forecast,
        "report": report
    }


# Initialize cache
cache.init_app(server)


def serve_layout():
    """Define the layout of the application"""
    return dmc.MantineProvider(
        html.Div(
            [
                navbar(),
                dcc.Store(id="locations-list", data={}, storage_type="local"),
                dcc.Store(id="location-selected", data={}, storage_type="local"),
                dcc.Store(id="locations-favorites", storage_type="local"),
                dcc.Store(id="client-details", data={}, storage_type="session"),
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
                dcc.Location(id="url", refresh=False),
                footer,
            ],
            id="app-div",
        )
    )


app.layout = serve_layout


@callback(Output("client-details", "data"), Input("app-div", "id"))
def ip(id):
    client_details = {}
    client_details["session_id"] = str(uuid.uuid4())
    client_details["real_address"] = request.environ.get(
        "HTTP_X_REAL_IP", request.remote_addr
    )
    logging.info(
        f"New Session {client_details['session_id']} for IP {client_details['real_address']}"
    )

    return client_details


@callback(
    Input({"type": "submit-button", "index": ALL}, "n_clicks"),
    [
        State("location-selected", "data"),
        State("client-details", "data"),
        State("url", "pathname"),
    ],
    prevent_initial_call=True,
)
def log_user_location(n, location, client, pathname):
    if not n:
        raise PreventUpdate
    if location and len(location) > 0:
        logging.info(
            f"SUBMIT => Session {client['session_id']}, Page {pathname}, selected location {location[0]['label']}"
        )


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


@callback(
    Output("navbar-title-for-mobile", "children"),
    [Input("url", "pathname"), Input("navbar-collapse", "is_open")],
)
def update_navbar_title(pathname, is_open):
    """
    Update the navbar title (only on mobile) with the page title every time
    the page is changed. Also check if navbar is collapsed
    """
    if not is_open:
        return page_titles.get(pathname, "")
    else:
        return ""


@callback(
    Output({"type": "submit-button", "index": MATCH}, "disabled"),
    Input("location_search_new", "value"),
)
def activate_submit_button(location):
    """
    Disable submit button (on all pages) unless
    a location has been selected
    """
    if location is None:
        return True
    return False


@callback(
    Output(
        {"type": "fade", "index": MATCH},
        "is_open",
    ),
    Input({"type": "submit-button", "index": MATCH}, "n_clicks"),
    prevent_initial_call=True,
)
def toggle_fade(n):
    """
    Open the collapse element containing the plots once
    the submit button has been pressed (on all pages)
    """
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


clientside_callback(
    """
    function(n_clicks, element_id) {
        element_id = element_id[0];
        if (!(typeof element_id === 'string' || element_id instanceof String)) {
            element_id = JSON.stringify(element_id, Object.keys(element_id).sort());
        };
            var targetElement = document.getElementById(element_id);
            if (targetElement) {
                setTimeout(function() {
                    targetElement.scrollIntoView({ behavior: 'smooth' });
                }, 200); // in milliseconds
            }
        return null;
    }
    """,
    Input(dict(type="figure", id=ALL), "figure"),
    State(dict(type="figure", id=ALL), "id"),
    prevent_initial_call=True,
)

if __name__ == "__main__":
    app.run(
        port=APP_PORT,
    )
