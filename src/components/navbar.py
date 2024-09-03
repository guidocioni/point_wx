# notes
"""
This file is for creating a navigation bar that will sit at the top of your application.
Much of this page is pulled directly from the Dash Bootstrap Components documentation linked below:
https://dash-bootstrap-components.opensource.faculty.ai/docs/components/navbar/
"""

# package imports
from dash import (
    callback,
    Output,
    Input,
    State,
    ALL,
    clientside_callback,
    html,
    page_registry,
)
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify


def navbar():
    return dbc.Navbar(
        dbc.Container(
            [
                dbc.NavbarBrand(
                    [
                        "PointWx",
                        DashIconify(icon="meteocons:thunderstorms-day-fill", width=60),
                    ],
                    class_name="fs-2",
                ),
                html.Div(
                    id="navbar-title-for-mobile",
                    className="d-xl-none fs-6",  # Show only on mobile devices
                    style={"color": "white"},
                ),
                dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
                dbc.Collapse(
                    dbc.Nav(
                        [
                            dbc.NavItem(
                                dbc.NavLink(
                                    page["title"],
                                    id={
                                        "type": "navbar-link",
                                        "index": page["relative_path"].split("/")[-1],
                                    },
                                    href=page["relative_path"],
                                )
                            )
                            for page in page_registry.values()
                        ],
                        pills=True,
                    ),
                    id="navbar-collapse",
                    navbar=True,
                ),
            ]
        ),
        color="dark",
        dark=True,
        expand="xl",
    )


@callback(
    Output("navbar-collapse", "is_open", allow_duplicate=True),
    Input("navbar-toggler", "n_clicks"),
    State("navbar-collapse", "is_open"),
    prevent_initial_call=True,
)
def toggle_navbar_collapse(n, is_open):
    """
    Toggle the collapse of the navbar if the navbar toggler button
    is pressed. Note that this button will not appear on large screens.
    """
    if n:
        return not is_open
    return is_open


"""
On small devices, when any element of the navbar (navlink) is pressed,
then automatically collapse the navbar again. In fact, the navbar takes too 
much space on small screens so it doesn't make sense to keep that open.
Closing manually would require an extra click plus eventually scrolling.
"""
clientside_callback(
    """
    function toggleCollapse(n_clicks) {
        // Check the viewport width
        var viewportWidth = window.innerWidth;

        // Set a threshold for the viewport width when collapse should not happen
        var threshold = 768;  // Adjust this threshold as needed

        // Conditionally toggle the collapse based on viewport size
        if (viewportWidth <= threshold) {
            return false;
        } else {
            return window.dash_clientside.no_update;
        }
    }
    """,
    Output("navbar-collapse", "is_open"),
    [Input({"type": "navbar-link", "index": ALL}, "n_clicks")],
)
