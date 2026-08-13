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
from dash_iconify import DashIconify

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
    try:
        report = create_ai_report(address_search, date_forecast, additional_prompt)
    except Exception as e:
        logging.error(
            f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}"
        )
        return {"error": "An error occurred when generating the AI report"}, 500

    return {"search": address_search, "date": date_forecast, "report": report}


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
                dcc.Store(id="client-first-visit", storage_type="local"),
                dcc.Store(id="figures-store", data={}),  # memory storage (default) - clears on page refresh
                dcc.Store(id='dummy-data'),
                dcc.Store(id='figure-ready-signal'),
                dcc.Store(id='url-location'),
                dbc.Modal(
                    [
                        dbc.ModalHeader(
                            children=[
                                DashIconify(
                                    icon="solar:danger-triangle-bold-duotone", width=30
                                ),
                                dbc.ModalTitle(" Error"),
                            ],
                            className="bg-danger text-white"
                        ),
                        dbc.ModalBody(
                            "", id="error-message"
                        ),  # Placeholder for error message
                    ],
                    id="error-modal",
                    size="md",
                    backdrop="static",
                ),
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("Hello there"), close_button=False),
                        dbc.ModalBody(
                            [
                                "Welcome to my weather application!",
                                html.Br(),
                                DashIconify(icon="meteocons:clear-day-fill", width=60),
                                DashIconify(icon="meteocons:dust-day-fill", width=60),
                                DashIconify(
                                    icon="meteocons:thunderstorms-day-extreme-fill",
                                    width=60,
                                ),
                                DashIconify(icon="meteocons:wind", width=60),
                                DashIconify(
                                    icon="meteocons:partly-cloudy-night-smoke-fill",
                                    width=60,
                                ),
                                DashIconify(icon="meteocons:hurricane-fill", width=60),
                                html.Br(),
                                "It looks like this is your first time here.",
                                html.Br(),
                                "Don't forget to read the help boxes in every page to understand how to use the app. ",
                                html.Br(),
                                "If you would like to see a new feature included (or just want to ask something) don't hesitate to write me at ",
                                html.A(
                                    "this email. ",
                                    title="email_me",
                                    href="mailto:guidocioni@gmail.com",
                                    target="_blank",
                                ),
                                " I need your feedback to make the application even better!",
                            ],
                        ),
                        dbc.ModalFooter(
                            dbc.Button(
                                "Close", id="close-button-modal", className="ml-auto"
                            )
                        ),
                    ],
                    id="welcome-modal",
                    size="md",
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


# Callback to check the cookie and display the modal
@callback(
    Output("welcome-modal", "is_open"),
    [Input("url", "pathname"), Input("close-button-modal", "n_clicks")],
    State("client-first-visit", "data"),
)
def display_modal(pathname, n_clicks, data):
    if n_clicks:
        return False  # If the close button is clicked, close the modal
    if data is None:  # Check if there's no session data
        return True  # Open the modal if it's the first visit
    raise PreventUpdate  # Prevent callback from updating if data exists


# Callback to set session data after closing the modal
@callback(
    Output("client-first-visit", "data"),
    Input("close-button-modal", "n_clicks"),
    prevent_initial_call=True,
)
def set_cookie(n_clicks):
    return {"visited": True}  # Set a simple key to indicate the user has visited


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


'''
The following 2 callbacks for the navbar need to be defined here because
in navbar.py the page_registry.values() is not yet defined globally as app hasn't
run yet. It is only accessible in the navbar() function, because this is called when
the app is initialized.
'''
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


'''
Disable submit button (on all pages) unless
a location has been selected.

Deliberately clientside: the answer is already in the browser, so a round-trip would just
leave the button greyed out for a moment after the user has picked a location.
'''
clientside_callback(
    """
    function(location) {
        return location === null || location === undefined;
    }
    """,
    Output({"type": "submit-button", "index": MATCH}, "disabled"),
    Input("location_search_new", "value"),
)


@callback(
    Output({"type": "fade", "index": MATCH}, "is_open"),
    Input({"type": "submit-button", "index": MATCH}, "n_clicks"),
    State({"type": "fade", "index": MATCH}, "is_open"),
    prevent_initial_call=True,
)
def toggle_fade(n, is_open):
    """
    Open the collapse element containing the plots once
    the submit button has been pressed (on all pages), but do nothing
    if the element is already open.
    TODO: avoid running this if the plot is not correctly generated,
    because if there's an error then an empty plot will be shown anyway.
    """
    if is_open:
        # Do not update if already open.
        raise PreventUpdate
    if n:
        return True
    return False


'''
URL query parameters sync, part 1 of 2 (see utils/url_sync.py for the rest).

Announce that a page has just been mounted, so that its selectors can be filled in from
the query string. This has to go through a store rather than being consumed directly by
the page callbacks: those write to selectors whose ids are shared between pages
(from-now-switch, forecast-days, ...) and therefore must use allow_duplicate, which in
turn forbids them from running on an initial call.

Every page carries exactly one "fade" Collapse with the same index as its stores, so MATCH
pairs them up and only the mounted page fires. Pages without figures (home, chatbot) have
no fade and no stores, and are simply never matched.
'''
@callback(
    Output({"type": "url-sync-trigger", "index": MATCH}, "data"),
    Input({"type": "fade", "index": MATCH}, "id"),
)
def fire_url_sync(_):
    # A fresh token every time, so that mounting the same page twice always re-syncs
    return str(uuid.uuid4())


'''
URL query parameters sync, part 2 of 2: reflect the query string built by the page
writer callbacks into the address bar.

This uses history.replaceState rather than Output("url", "search") on purpose: dcc.Location
pushes a new history entry on every change, which would mean one Back press per switch
toggled. window.location.pathname is used as-is so that URL_BASE_PATHNAME (or any proxy
prefix) is preserved without having to be reconstructed.
Note this leaves the "url" component's own search prop stale, which is harmless: it is only
read when a page mounts, and the writer immediately re-normalises the address bar anyway.

The input is an ALL pattern because the url-query store lives in the page layout (see
url_sync.sync_stores); at most one is mounted at a time, and pages without figures mount
none, which an ALL pattern handles as an empty list.
'''
clientside_callback(
    """
    function(qs_list) {
        var qs = qs_list && qs_list[0];
        if (qs === undefined || qs === null) {
            return window.dash_clientside.no_update;
        }
        window.history.replaceState(null, '', window.location.pathname + qs);
        return null;
    }
    """,
    Output("dummy-data", "data", allow_duplicate=True),
    Input({"type": "url-query", "index": ALL}, "data"),
    prevent_initial_call=True,
)


'''
Only show the back-to-top affix button once the page
is scrolled up to a certain value (y=200 seems to be a pretty good one)
'''
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


'''
Every time a new figure has actually been produced by a page callback, scroll to it.
Note this is driven by "figure-ready-signal" (set explicitly by each page's figure
callback on its success path), NOT by the Graph "figure" prop directly: since Dash
4.4.1, dcc.Graph syncs relayout changes (zoom/pan/reset axes/...) back into the
"figure" prop, which would otherwise retrigger this callback on every plot interaction.
This also means restoring a persisted figure (figures-store) on page mount never
scrolls, since restore_figure() never touches "figure-ready-signal".
This involved some trickery because pattern matching callback does not
really play well with JS, so we needed to extract the right id of the element
for the scrollIntoView function to work.
'''
clientside_callback(
    """
    function(signal, element_ids) {
        // console.log("Triggered clientside callback");
        if (signal === undefined || signal === null) {
            return window.dash_clientside.no_update;
        }
        var element_id = element_ids && element_ids[0];
        if (!element_id) {
            return window.dash_clientside.no_update;
        }
        if (!(typeof element_id === 'string' || element_id instanceof String)) {
            element_id = JSON.stringify(element_id, Object.keys(element_id).sort());
            // console.log(element_id);
        };
        // Delay execution to allow element to load
        setTimeout(function() {
            var targetElement = document.getElementById(element_id);
            // console.log(targetElement);
            if (targetElement) {
                // Optional further delay before scrolling
                setTimeout(function() {
                    targetElement.scrollIntoView({ behavior: 'smooth' });
                }, 200);
            }
        }, 500); // Wait 0.5 second before retrieving the element

        return null;
    }
    """,
    Output("dummy-data", "data"),
    Input("figure-ready-signal", "data"),
    State(dict(type="fade", index=ALL), "id"),
    prevent_initial_call=True,
)

if __name__ == "__main__":
    app.run(
        port=APP_PORT,
    )
