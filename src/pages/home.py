import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify

dash.register_page(__name__, path="/", redirect_from=["/home"], title="Home")

PAGES = [
    {
        "path": "/forecasts",
        "title": "Deterministic",
        "icon": "ion:analytics-outline",
        "description": "Single-scenario forecasts from individual weather models, at high resolution.",
    },
    {
        "path": "/forecasts-heatmap",
        "title": "Multimodel",
        "icon": "ion:grid-outline",
        "description": "Compare one variable across several deterministic models at once.",
    },
    {
        "path": "/ensemble",
        "title": "Ensemble",
        "icon": "ion:git-network-outline",
        "description": "See the full spread of possible outcomes across many forecast scenarios.",
    },
    {
        "path": "/ensemble-heatmap",
        "title": "Ensemble heatmap",
        "icon": "ion:layers-outline",
        "description": "Visualize ensemble member spread as a time-vs-member heatmap.",
    },
    {
        "path": "/meteogram",
        "title": "Meteogram",
        "icon": "ion:partly-sunny-outline",
        "description": "A quick daily overview of temperature, sunshine and precipitation.",
    },
    {
        "path": "/vertical",
        "title": "Vertical",
        "icon": "ion:swap-vertical-outline",
        "description": "Explore the vertical structure of the atmosphere above a location.",
    },
    {
        "path": "/climate",
        "title": "Climate (monthly)",
        "icon": "ion:bar-chart-outline",
        "description": "Reconstruct the typical monthly climate of a location in detail.",
    },
    {
        "path": "/dailyclimate",
        "title": "Climate (daily)",
        "icon": "ion:stats-chart-outline",
        "description": "Compare a chosen year's daily values against historical statistics.",
    },
    {
        "path": "/calendar",
        "title": "Climate calendar",
        "icon": "ion:calendar-number-outline",
        "description": "Spot long-term trends and anomalies in a year-by-year heatmap.",
    },
    {
        "path": "/chatbot",
        "title": "Chat",
        "icon": "ion:chatbubbles-outline",
        "description": "Ask a weather chatbot about forecasts and conditions in plain language.",
    },
]


def _page_card(page):
    return dbc.Col(
        dcc.Link(
            dbc.Card(
                [
                    DashIconify(icon=page["icon"], width=28, className="page-card-icon"),
                    html.Div(page["title"], className="page-card-title"),
                    html.Div(page["description"], className="page-card-description"),
                ],
                body=True,
                className="selector-card page-card h-100",
            ),
            href=dash.get_relative_path(page["path"]),
            className="text-decoration-none",
        ),
        sm=12,
        md=6,
        lg=4,
        className="mb-3",
    )


layout = html.Div(
    [
        html.H3("Introduction", className="mb-2"),
        html.P(
            "This application lets you explore the weather (wx) for any place (point) in the "
            "world — from the next few days of forecasts to decades of historical climate.",
            className="mb-3",
        ),
        html.Hr(),
        html.H3("Explore", className="mb-2"),
        html.P(
            "Pick a page below, or use the menu at the top. Each page has its own info box "
            "explaining what it shows, plus tooltips on the individual options.",
            className="mb-3",
        ),
        dbc.Row([_page_card(page) for page in PAGES]),
        html.H4("Good to know", className="mt-2 mb-2"),
        dbc.Alert(
            [
                DashIconify(
                    icon="ion:phone-portrait-outline", width=20, className="me-2"
                ),
                "This app also works on mobile devices, though some plots may not be optimized for "
                "very small screens.",
            ],
            color="info",
        ),
    ]
)
