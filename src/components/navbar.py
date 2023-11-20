# notes
'''
This file is for creating a navigation bar that will sit at the top of your application.
Much of this page is pulled directly from the Dash Bootstrap Components documentation linked below:
https://dash-bootstrap-components.opensource.faculty.ai/docs/components/navbar/
'''

# package imports
import dash
from dash import callback, Output, Input, State, ALL
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
    Output('navbar-collapse', 'is_open'),
    Input('navbar-toggler', 'n_clicks'),
    State('navbar-collapse', 'is_open'),
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@callback(
    Output('navbar-collapse', 'is_open', allow_duplicate=True),
    Input({'type': 'navbar-link', 'index': ALL}, 'n_clicks'),
    State('navbar-collapse', 'is_open'),
    prevent_initial_call=True
)
def toggle_navbar_collapse_from_navlink(navlink_clicks, is_open):
    return False if is_open else any(navlink_clicks)
