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
        "height": "calc(80vh - 132px)",
        "flex-direction": "column-reverse",
    },
)

controls = html.Div(
    children=[
        dmc.Textarea(
            id="user-input",
            placeholder="Write to the chatbot...",
            autosize=True,
            minRows=1,
            maxRows=4,
            radius="md",
            rightSection=dmc.Button(
                DashIconify(icon="formkit:submit", height=30),
                id="submit",
                variant="subtle",
                color="gray",
                loading=False,
                loaderProps={"type": "dots"}
            ),
            rightSectionWidth=60,
            spellCheck=True
        ),
    ],
)

layout = html.Div(
    dbc.Container(
        fluid=False,
        children=[
            dcc.Store(id="store-conversation", data=[]),
            conversation,
            controls
        ],
        style={"padding": "0.5rem"},  # Add padding and limit max width
    ),
    style={
        "display": "flex",
        "justify-content": "center",
        "align-items": "center",
    },  # Center the container
)
