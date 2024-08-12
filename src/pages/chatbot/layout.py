from dash import html, register_page, dcc
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from .callbacks import *

register_page(__name__, path="/chatbot", title="Chat")

conversation = html.Div(
    html.Div(id="display-conversation"),
    style={
        "overflow-y": "auto",
        "display": "flex",
        "height": "calc(70vh - 132px)",
        "flex-direction": "column-reverse",
    },
)

controls = html.Div(
    children=[
        dmc.Textarea(
            id="user-input",
            placeholder="Write to the chatbot...",
            autosize=True,
            minRows=2,
            maxRows=4,
            radius="md",
            rightSection=dmc.Button(
                DashIconify(icon="formkit:submit", height=30),
                id="submit",
                variant="subtle",
                color="gray",
            ),
            rightSectionWidth=60,
            spellCheck=True
        ),
    ],
    style={"margin-bottom": "1rem"},
)

layout = html.Div(
    dbc.Container(
        fluid=False,
        children=[
            dcc.Store(id="store-conversation", data=[]),
            conversation,
            controls,
            dbc.Spinner(html.Div(id="loading-component"), fullscreen=False),
        ],
        style={"padding": "0.5rem"},  # Add padding and limit max width
    ),
    style={
        "display": "flex",
        "justify-content": "center",
        "align-items": "center",
    },  # Center the container
)
