# notes
'''
This file is for creating a navigation bar that will sit at the top of your application.
Much of this page is pulled directly from the Dash Bootstrap Components documentation linked below:
https://dash-bootstrap-components.opensource.faculty.ai/docs/components/navbar/
'''

# package imports
import dash
from dash import callback, Output, Input, State, ALL, clientside_callback
import dash_bootstrap_components as dbc


def navbar():
    return dbc.Navbar(
        dbc.Container(
            [
                dbc.NavbarToggler(id='navbar-toggler', n_clicks=0),
                dbc.Collapse(
                    dbc.Nav(
                        [
                            dbc.NavItem(
                                dbc.NavLink(
                                    page['title'],
                                    id={'type': 'navbar-link', 'index': page["relative_path"].split("/")[-1]},
                                    href=page["relative_path"]
                                )
                            ) for page in dash.page_registry.values()
                        ],
                    ),
                    id='navbar-collapse',
                    navbar=True
                ),
            ]
        ),
        color='dark',
        dark=True,
    )

# add callback for toggling the collapse on small screens


@callback(
    Output('navbar-collapse', 'is_open', allow_duplicate=True),
    Input('navbar-toggler', 'n_clicks'),
    State('navbar-collapse', 'is_open'),
    prevent_initial_call=True
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


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
    Output('navbar-collapse', 'is_open'),
    [Input({'type': 'navbar-link', 'index': ALL}, 'n_clicks')],
)
