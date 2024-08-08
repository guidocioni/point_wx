from dash import callback, Output, Input, State, html
from utils.settings import OPENAI_KEY, logging
from utils.ai_utils import create_weather_data
from .system import system_prompt
from openai import OpenAI
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
import json

client = OpenAI(api_key=OPENAI_KEY)


tools = [
    {
        "type": "function",
        "function": {
            "name": "create_weather_data",
            "description": "Get the weather data for a specific location and date as JSON. Use it to get the input data for your analysis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The location used to get the weather data",
                    },
                    "date": {
                        "type": "string",
                        "description": "The date for which the weather data is requested",
                    },
                },
                "required": ["location", "date"],
                "additionalProperties": False,
            },
        },
        "strict": True,
    }
]

def textbox(text, box="AI"):
    style = {
        "max-width": "80%",
        "width": "max-content",
        "padding": "5px 10px",
        "border-radius": 25,
        "margin-bottom": 20,
        "display": "flex",
    }

    if box == "user":
        style["margin-left"] = "auto"
        style["margin-right"] = 0
        return dbc.Card(text, style=style, body=True, color="primary", inverse=True)
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

        textbox = dbc.Card(text, style=style, body=True, color="light", inverse=False)

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
    Output("user-input", "value"),
    [Input("submit", "n_clicks"), Input("user-input", "n_submit")],
)
def clear_input(n_clicks, n_submit):
    return ""


@callback(
    [Output("store-conversation", "data"), Output("loading-component", "children")],
    [Input("submit", "n_clicks"), Input("user-input", "n_submit")],
    [State("user-input", "value"), State("store-conversation", "data")],
)
def run_chatbot(n_clicks, n_submit, user_input, chat_history):
    if n_clicks == 0 and n_submit is None:
        return chat_history, None

    if user_input is None or user_input == "":
        return chat_history, None

    messages = [
        {"role": "system", "content": system_prompt},
    ]

    # Add previous chat history
    if chat_history:
        messages.extend(chat_history)  # Add previous messages to the conversation

    # Add user input to messages
    user_message = {"role": "user", "content": user_input}
    messages.append(user_message)

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
        handle_tool_call(response, messages, chat_history)
    elif finish_reason == "stop":
        # Handle normal response (model responded directly to the user)
        handle_normal_response(response, chat_history)
    elif finish_reason == "length":
        # Handle the case where the conversation was too long
        handle_length_error(response)
    elif finish_reason == "content_filter":
        # Handle the case where the content was filtered
        handle_content_filter_error(response)
    else:
        # Handle unexpected cases
        handle_unexpected_case(response)

    return chat_history, None


def handle_tool_call(response, messages, chat_history):
    tool_call = response.choices[0].message.tool_calls[0]
    
    if tool_call.function.name == "create_weather_data":
        # Extract the arguments
        arguments = json.loads(tool_call.function.arguments)
        location = arguments["location"]
        date = arguments["date"]

        # Call the actual Python function
        weather_data = create_weather_data(location, date)

        # Add the function result back into the conversation
        messages.append({
            "role": "function",
            "name": "create_weather_data",
            "content": json.dumps(weather_data)  # Format as needed
        })

        # Make another call to the model with the function's output
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=250,
            temperature=0.9,
        )

        # Handle the normal response after the tool call
        handle_normal_response(response, chat_history)

def handle_normal_response(response, chat_history):
    model_output = response.choices[0].message.content.strip()

    # Update chat history
    chat_history.append({"role": "assistant", "content": model_output})

def handle_length_error(response):
    # Handle the case where the conversation was too long for the context window
    logging.error("The conversation was too long for the context window.")
    # Implement your logic to handle this, such as truncating the conversation

def handle_content_filter_error(response):
    # Handle the case where content was filtered
    logging.error("The content was filtered due to policy violations.")
    # Implement your logic to handle this, such as modifying the request or notifying the user

def handle_unexpected_case(response):
    # Handle any unexpected cases
    logging.error("Unexpected finish_reason:", response.choices[0].finish_reason)
    # Implement your logic to handle this
