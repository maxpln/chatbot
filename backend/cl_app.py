from typing import List
from fastapi import Request, Response
import chainlit as cl
from openai import AsyncOpenAI
import os
from initialisation import (
    init_chat_settings,
    create_chat_profiles,
    create_starters,
    create_commands,
    ask_action_on_doc,
)
from chainlit.types import ThreadDict
from generate_response import request_llm, generate_resume


@cl.password_auth_callback
def auth_callback(username: str, password: str):
    """Check the username and password provided by the user.
    Basic authentication to enable features with data persistence.
    """
    if (username, password) == ("admin", "admin"):
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return None


@cl.on_logout
def delete_cookie(request: Request, response: Response):
    response.delete_cookie("my_cookie")


@cl.set_chat_profiles
async def set_chat_profile() -> List[cl.ChatProfile]:
    """Initialize chat profiles to choose the LLM to use."""
    return await create_chat_profiles()


@cl.set_starters
async def set_starters() -> List[cl.Starter]:
    """Initialize starter messages to show example to the user."""
    return await create_starters()


@cl.on_chat_start
async def on_chat_start() -> None:
    """Beginning of a new chat session."""
    # Initialize the model
    model_client = AsyncOpenAI(
        base_url=os.getenv("OLLAMA_URL"), api_key=os.getenv("OPENAI_API_KEY")
    )
    cl.user_session.set("model_client", model_client)
    cl.instrument_openai()
    # Initialize the chat settings for inference
    await init_chat_settings()
    await settings_updated()
    # Initialize the commands
    lst_commands = await create_commands()
    await cl.context.emitter.set_commands(lst_commands)
    # Add system prompt to the chat context
    cl.chat_context.add(
        cl.Message(content="You are a helpful assistant.", type="system_message")
    )


@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict) -> None:
    """Resume a chat session."""
    await on_chat_start()


@cl.on_settings_update
async def settings_updated() -> None:
    """Chat settings updated by the user."""
    # Create settings for the inference parameters and add the model name
    settings = cl.user_session.get("chat_settings")
    settings["model"] = cl.user_session.get("chat_profile")
    cl.user_session.set("settings", settings)


@cl.on_message
async def main(message: cl.Message) -> None:
    """Generate a response to the user's message."""

    if message.command == "resume":
        if message.elements:
            await generate_resume(message.elements)
        elif not message.elements:
            files = await cl.AskFileMessage(
                content="Veuillez charger un fichier à résumer :", accept=["text/plain"]
            ).send()
            if files:
                await generate_resume(files)

    elif message.command is None and message.elements != []:
        action = await ask_action_on_doc(files=message.elements)
        if action == "resume":
            await generate_resume(message.elements)

    # No command, no file, just a message
    else:
        # Generate a response to the user's message based on history
        await request_llm(
            lst_messages=cl.chat_context.to_openai(),
            client=cl.user_session.get("model_client"),
            settings=cl.user_session.get("settings"),
        )


@cl.on_stop
def on_stop() -> None:
    print("The user wants to stop the task!")


@cl.on_chat_end
def on_chat_end() -> None:
    print("The user disconnected!")
