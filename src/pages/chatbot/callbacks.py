from dash import callback, Output, Input, State, html, dcc
from dash.exceptions import PreventUpdate
from utils.settings import OPENAI_KEY, logging
from .system import system_prompt
from .functions import *
from openai import OpenAI
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
import json

client = OpenAI(api_key=OPENAI_KEY)
logging.getLogger("openai").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)


def textbox(text, box="AI"):
    style = {
        "max-width": "80%",
        "width": "max-content",
        "padding": "10px 10px 0px 15px",
        "border-radius": 15,
        "margin-bottom": 15,
        "display": "flex",
    }

    if box == "user":
        style["margin-left"] = "auto"
        style["margin-right"] = 0
        return dbc.Card(
            dcc.Markdown(text), style=style, body=False, color="primary", inverse=True
        )
    elif box == "AI":
        style["margin-left"] = 0
        style["margin-right"] = "auto"
        thumbnail = dmc.Avatar(
            src="https://e7.pngegg.com/pngimages/799/987/png-clipart-computer-icons-avatar-icon-design-avatar-heroes-computer-wallpaper-thumbnail.png",
            size="md",
            radius="xl",
            style={
                "border-radius": 50,
                "height": 36,
                "margin-right": 5,
                "float": "left",
            },
        )

        textbox = dbc.Card(
            dcc.Markdown(text), style=style, body=False, color="light", inverse=False
        )

        return html.Div([thumbnail, textbox])

    else:
        raise ValueError("Incorrect option for `box`.")


# Callback to check the cookie and display the modal
@callback(
    Output("welcome-modal-chatbot", "is_open"),
    [Input("url", "pathname"), Input("close-button-modal-chatbot", "n_clicks")],
    State("client-first-visit-chatbot", "data"),
)
def display_modal(pathname, n_clicks, data):
    if n_clicks:
        return False  # If the close button is clicked, close the modal
    if data is None:  # Check if there's no session data
        return True  # Open the modal if it's the first visit
    raise PreventUpdate  # Prevent callback from updating if data exists


# Callback to set session data after closing the modal
@callback(
    Output("client-first-visit-chatbot", "data"),
    Input("close-button-modal-chatbot", "n_clicks"),
    prevent_initial_call=True,
)
def set_cookie(n_clicks):
    return {"visited": True}  # Set a simple key to indicate the user has visited

@callback(
    Output("display-conversation", "children"), [Input("store-conversation", "data")]
)
def update_display(store_data):
    chat_history = store_data.get("chat_history", [])
    return [
        textbox(message["content"], box="user" if message["role"] == "user" else "AI")
        for message in chat_history
    ]


@callback(
    [Output("user-input", "value"), Output("submit", "loading", allow_duplicate=True)],
    [Input("submit", "n_clicks"), Input("user-input", "n_submit")],
    prevent_initial_call=True,
)
def clear_input(n_clicks, n_submit):
    return "", True


@callback(
    [Output("store-conversation", "data"), Output("submit", "loading")],
    [Input("submit", "n_clicks"), Input("user-input", "n_submit")],
    [
        State("user-input", "value"),
        State("store-conversation", "data"),
        State("client-details", "data"),
    ],
)
def run_chatbot(n_clicks, n_submit, user_input, store_data, client_data):
    """
    There are 2 variables used to store the conversation with the Completion api
    - messages contains ALL messages including system prompts, functions result, user inputs...
    - chat_history only contains the messages that should be shown to the user in the frontend!
    """
    chat_history = store_data["chat_history"]
    messages = store_data["messages"]
    # Initialize the conversation
    if messages is None or len(messages) == 0:
        intro_messages = [
            {"role": "system", "content": system_prompt},
            # Inject time information only at the beginning of the system prompt
            {"role": "system", "content": get_current_datetime()},
            {
                "role": "assistant",
                "content": "Hiya! I'm here to help you with all questions related to weather or climate.\n You can ask me anything about the forecast for tomorrow or the next days, or about how this month (or year) has been so far.",
            },
        ]
        messages.extend(intro_messages)
        chat_history.append(intro_messages[-1])

        store_data = {"chat_history": chat_history, "messages": messages}

    if n_clicks == 0 and n_submit is None:
        return store_data, False

    if user_input is None or user_input == "":
        return store_data, False

    # Add user input to messages
    user_message = {"role": "user", "content": user_input}
    messages.append(user_message)
    logging.info(
        f"Chat SUBMIT => Session {client_data['session_id']}, Message: '{user_input}'"
    )
    # Add the user message to chat history immediately
    chat_history.append(user_message)

    # Step 1: Make the initial call to the model
    response = client.chat.completions.create(
        model="o3-mini",
        messages=messages,
        tools=tools,  # Add tools for function calling
        # max_tokens=300,
        # temperature=0.9,
    )

    # Check the finish_reason to determine how to handle the response
    finish_reason = response.choices[0].finish_reason

    if finish_reason == "tool_calls":
        # Handle the tool call
        handle_tool_calls(response, messages, chat_history, client_data["session_id"])
    elif finish_reason == "stop":
        # Handle normal response (model responded directly to the user)
        handle_normal_response(response, messages, chat_history, client_data["session_id"])
    elif finish_reason == "length":
        # Handle the case where the conversation was too long
        handle_length_error(response, messages, chat_history, client_data["session_id"])
    elif finish_reason == "content_filter":
        # Handle the case where the content was filtered
        handle_content_filter_error(response, messages, chat_history, client_data["session_id"])
    else:
        # Handle unexpected cases
        handle_unexpected_case(response, messages, chat_history, client_data["session_id"])

    store_data = {"chat_history": chat_history, "messages": messages}

    return store_data, False


def handle_tool_calls(response, messages, chat_history, session_id):
    tool_calls = response.choices[0].message.tool_calls
    # With the new API we need to include a message including which tools have been called,
    # before including the results of the tool calls. I haven't found a better way of doing this
    messages.append(
        {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": tool_call.id,
                    "type": tool_call.type,
                    "function": {
                        "arguments": tool_call.function.arguments,
                        "name": tool_call.function.name,
                    },
                }
                for tool_call in tool_calls
            ],
        }
    )

    for tool_call in tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        # Look up the correct function in the tools object
        function_to_call = None
        for tool in tools:
            if tool["function"]["name"] == function_name:
                function_to_call = globals().get(function_name)
                break

        if not function_to_call:
            logging.error(
                f"Chat SUBMIT => Session {session_id}: Function {function_name} is not defined or not found in tools."
            )
            messages.append({"role": "assistant", "content": "There was an error calling the function (function not found in tools), please report this to the author"})
            chat_history.append({"role": "assistant", "content": "There was an error calling the function (function not found in tools), please report this to the author"})
            return
        # Call the function with the extracted arguments
        try:
            logging.info(
                f"Chat SUBMIT => Session {session_id}. Model is calling function {function_name} with parameters {arguments}"
            )
            function_result = function_to_call(**arguments)
        except Exception as e:
            logging.error(
                f"Chat SUBMIT => Session {session_id}: Error calling function {function_name}: {str(e)}"
            )
            messages.append({"role": "assistant", "content": "There was an error calling the function, please report this to the author"})
            chat_history.append({"role": "assistant", "content": "There was an error calling the function, please report this to the author"})
            return

        # Add the function result back into the conversation in response to the tool call
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(function_result),
            }
        )

    # Make another call to the model with the tool's output
    response = client.chat.completions.create(
        model="o3-mini",
        messages=messages,
        # max_tokens=300,
        # temperature=0.9,
    )

    # Handle the model's response after tool usage
    handle_normal_response(response, messages, chat_history, session_id)


def handle_normal_response(response, messages, chat_history, session_id):
    model_output = response.choices[0].message.content.strip()
    # A normal response should go both in the hidden and frontend history
    messages.append({"role": "assistant", "content": model_output})
    chat_history.append({"role": "assistant", "content": model_output})


def handle_length_error(response, messages, chat_history, session_id):
    # Handle the case where the conversation was too long for the context window
    logging.error(
        f"Chat SUBMIT => Session {session_id}: The conversation was too long for the context window."
    )
    messages.append({"role": "assistant", "content": "Error: The conversation was too long for the context window, please retry"})
    chat_history.append({"role": "assistant", "content": "Error: The conversation was too long for the context window, please retry"})


def handle_content_filter_error(response, messages, chat_history, session_id):
    # Handle the case where content was filtered
    logging.error(
        f"Chat SUBMIT => Session {session_id}: The content was filtered due to policy violations."
    )
    messages.append({"role": "assistant", "content": "Error: The content was filtered due to policy violations, please retry"})
    chat_history.append({"role": "assistant", "content": "Error: The content was filtered due to policy violations, please retry"})


def handle_unexpected_case(response, messages, chat_history, session_id):
    # Handle any unexpected cases
    logging.error(
        f"Chat SUBMIT => Session {session_id}: Unexpected finish_reason:",
        response.choices[0].finish_reason,
    )
    messages.append({"role": "assistant", "content": "Error: Unexpected finish_reason, please try again"})
    chat_history.append({"role": "assistant", "content": "Error: Unexpected finish_reason, please try again"})
