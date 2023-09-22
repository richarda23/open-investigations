import json
import openai
import requests
from tenacity import retry, wait_random_exponential, stop_after_attempt
from termcolor import colored

GPT_MODEL = "gpt-4"

role_to_color = {
    "system": "red",
    "user": "green",
    "assistant": "blue",
    "function": "magenta",
}


def pretty_print_conversation(messages):
    """
    Prints color-coded messages according to their tole
    """

    for message in messages:
        if message["role"] == "system":
            print(
                colored(
                    f"system: {message['content']}\n", role_to_color[message["role"]]
                )
            )
        elif message["role"] == "user":
            print(
                colored(f"user: {message['content']}\n", role_to_color[message["role"]])
            )
        elif message["role"] == "assistant" and message.get("function_call"):
            print(
                colored(
                    f"assistant: {message['function_call']}\n",
                    role_to_color[message["role"]],
                )
            )
        elif message["role"] == "assistant" and not message.get("function_call"):
            print(
                colored(
                    f"assistant: {message['content']}\n", role_to_color[message["role"]]
                )
            )
        elif message["role"] == "function":
            print(
                colored(
                    f"function ({message['name']}): {message['content']}\n",
                    role_to_color[message["role"]],
                )
            )


def pretty_print_conversation2(messages):
    """
    Prints color-coded messages according to their tole
    """
    rc = []
    ## add color

    for message in messages:
        if message["role"] == "system":
            rc.append(
                {
                    "m": f"system: {message['content']}",
                    "c": role_to_color[message["role"]],
                }
            )
        elif message["role"] == "user":
            rc.append(
                {
                    "m": f"user: {message['content']}",
                    "c": role_to_color[message["role"]],
                }
            )
        elif message["role"] == "assistant" and message.get("function_call"):
            rc.append(
                {
                    "m": f"assistant: {message['function_call']}",
                    "c": role_to_color[message["role"]],
                }
            )
        elif message["role"] == "assistant" and not message.get("function_call"):
            rc.append(
                {
                    "m": f"assistant: {message['content']}",
                    "c": role_to_color[message["role"]],
                }
            )
        elif message["role"] == "function":
            rc.append(
                {
                    "m": f"function ({message['name']}): {message['content']}",
                    "c": role_to_color[message["role"]],
                }
            )
    return rc


@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(
    messages, functions=None, function_call=None, model=GPT_MODEL, key=openai.api_key
):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + key,
    }
    json_data = {"model": model, "messages": messages}

    if functions is not None:
        json_data.update({"functions": functions})
    if function_call is not None:
        json_data.update({"function_call": function_call})
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=json_data,
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e
