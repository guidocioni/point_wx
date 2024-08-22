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
            dcc.Store(id="store-conversation", data={"chat_history": [], "messages": []}),
            dcc.Store(id="client-first-visit-chatbot", storage_type="local"),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("The chat feature is a BETA"), close_button=False),
                    dbc.ModalBody(
                        [
                            html.P(
                                "This page contains a chatgpt-like agent which can answer questions regarding weather and climate. "
                                "The chatbot has access to most of the functions used throughout the application and can decide when and how to call them."
                            ),
                            html.P(
                                [
                                    "You can talk with the chatbot in whatever language you want. ",
                                    "Here are some examples of questions that you can ask:",
                                    html.Ul(children=[
                                        html.Li("What are the current conditions in New York? Is it raining?"),
                                        html.Li("What is the weather going to be like tomorrow in Berlin?"),
                                        html.Li("Is the coming week going to be hot in Rome?"),
                                        html.Li("Tomorrow morning I want to have a walk outside here in Florence. Is there any probability of rain?"),
                                        html.Li("I was curious to know how many days of rain Dubai gets on average"),
                                        html.Li("Was this month hotter or colder than normal until now in Hamburg?"),
                                        html.Li("I know today is going to be cold in Tromso. Could you tell me the range of minimum temperatures I can expect?")
                                        ]),
                                    "The chatbot CAN and WILL make mistakes, especially in this early development phase. Try to be as specific as possible."
                                    ]
                                ),
                            html.P("Under the hood it uses the OpenAI API, which means that the entire conversation (including the data fetched) is transmitted to OpenAI.")
                        ],
                    ),
                    dbc.ModalFooter(
                        dbc.Button(
                            "Close", id="close-button-modal-chatbot", className="ml-auto"
                        )
                    ),
                ],
                id="welcome-modal-chatbot",
                size="lg",
                backdrop="static",
            ),
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
