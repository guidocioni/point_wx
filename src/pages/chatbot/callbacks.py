from dash import callback, Output, Input, State, html, dcc
from utils.settings import OPENAI_KEY, logging
from .system import system_prompt
from .functions import *
from openai import OpenAI
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
import json

client = OpenAI(api_key=OPENAI_KEY)

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
        return dbc.Card(dcc.Markdown(text), style=style, body=False, color="primary", inverse=True)
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

        textbox = dbc.Card(dcc.Markdown(text), style=style, body=False, color="light", inverse=False)

        return html.Div([thumbnail, textbox])

    else:
        raise ValueError("Incorrect option for `box`.")

@callback(
    Output("display-conversation", "children"), 
    [Input("store-conversation", "data")]
)
def update_display(chat_history):
    return [
        textbox(message["content"], box="user" if message["role"] == "user" else "AI")
        for message in chat_history
    ]


@callback(
    [Output("user-input", "value"), Output("submit", "loading", allow_duplicate=True)],
    [Input("submit", "n_clicks"), Input("user-input", "n_submit")],
    prevent_initial_call=True
)
def clear_input(n_clicks, n_submit):
    return "", True


@callback(
    [Output("store-conversation", "data"), Output("submit", "loading")],
    [Input("submit", "n_clicks"), Input("user-input", "n_submit")],
    [State("user-input", "value"), State("store-conversation", "data"), State("client-details", "data")],
)
def run_chatbot(n_clicks, n_submit, user_input, chat_history, client_data):
    # Initialize the chat history if it is empty
    if chat_history is None or len(chat_history) == 0:
        chat_history = [
            {"role": "assistant", "content": "Hiya! I'm here to help you with all questions related to weather or climate.\n You can ask me anything about the forecast for tomorrow or the next days, or about how this month (or year) has been so far. I'll try to give you some interesting informations."}
        ]

    if n_clicks == 0 and n_submit is None:
        return chat_history, False

    if user_input is None or user_input == "":
        return chat_history, False

    messages = [
        {"role": "system", "content": system_prompt},
        # Inject time information only at the beginning of the system prompt
        {"role": "system", "content": get_current_datetime()}
    ]

    # Add previous chat history
    if chat_history:
        messages.extend(chat_history)  # Add previous messages to the conversation

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
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,  # Add tools for function calling
        max_tokens=250,
        temperature=0.9,
    )
    
    # Check the finish_reason to determine how to handle the response
    finish_reason = response.choices[0].finish_reason

    if finish_reason == "tool_calls":
        # Handle the tool call
        handle_tool_calls(response, messages, chat_history, client_data['session_id'])
    elif finish_reason == "stop":
        # Handle normal response (model responded directly to the user)
        handle_normal_response(response, chat_history)
    elif finish_reason == "length":
        # Handle the case where the conversation was too long
        handle_length_error(response, client_data['session_id'])
    elif finish_reason == "content_filter":
        # Handle the case where the content was filtered
        handle_content_filter_error(response, client_data['session_id'])
    else:
        # Handle unexpected cases
        handle_unexpected_case(response, client_data['session_id'])

    return chat_history, False


def handle_tool_calls(response, messages, chat_history, session_id):
    tool_calls = response.choices[0].message.tool_calls  # This is a list of function calls

    for tool_call in tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        # Look up the correct function in the tools object
        function_to_call = None
        for tool in tools:
            if tool['function']['name'] == function_name:
                function_to_call = globals().get(function_name)
                break

        if not function_to_call:
            logging.error(f"Chat SUBMIT => Session {session_id}: Function {function_name} is not defined or not found in tools.")

        # Call the function with the extracted arguments
        try:
            logging.info(f"Chat SUBMIT => Session {session_id}. Model is calling function {function_name} with parameters {arguments}")
            function_result = function_to_call(**arguments)
        except TypeError as e:
            logging.error(f"Chat SUBMIT => Session {session_id}: Error calling function {function_name}: {str(e)}")

        # Add the function result back into the conversation
        messages.append({
            "role": "function",
            "name": function_name,
            "content": json.dumps(function_result)
        })

        # Make another call to the model with the function's output
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=250,
            temperature=0.9,
            tools=tools,
        )

        # Handle the response again, which might include another tool call
        finish_reason = response.choices[0].finish_reason
        if finish_reason == "tool_calls":
            handle_tool_calls(response, messages, chat_history)
        elif finish_reason == "stop":
            handle_normal_response(response, chat_history)
        else:
            handle_unexpected_case(response)

        # Break out if the model indicates it's done
        if finish_reason == "stop":
            break

def handle_normal_response(response, chat_history):
    model_output = response.choices[0].message.content.strip()

    # Update chat history
    chat_history.append({"role": "assistant", "content": model_output})

def handle_length_error(response, session_id):
    # Handle the case where the conversation was too long for the context window
    logging.error(f"Chat SUBMIT => Session {session_id}: The conversation was too long for the context window.")
    # Implement your logic to handle this, such as truncating the conversation

def handle_content_filter_error(response, session_id):
    # Handle the case where content was filtered
    logging.error(f"Chat SUBMIT => Session {session_id}: The content was filtered due to policy violations.")
    # Implement your logic to handle this, such as modifying the request or notifying the user

def handle_unexpected_case(response, session_id):
    # Handle any unexpected cases
    logging.error(f"Chat SUBMIT => Session {session_id}: Unexpected finish_reason:", response.choices[0].finish_reason)
    # Implement your logic to handle this
