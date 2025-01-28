import os
from typing import List
from fastapi import Request, Response
import chainlit as cl
from initialisation import (
    init_chat_settings,
    create_chat_profiles,
    create_starters,
    create_commands,
    ask_action_on_doc,
    ask_files,
)
from chainlit.types import ThreadDict
from generate_response import request_llm, generate_resume, generate_qa
from preprocessing import create_index


@cl.password_auth_callback
def auth_callback(username: str, password: str) -> [cl.User, None]:
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
def delete_cookie(request: Request, response: Response) -> None:
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
    # Initialize the chat settings for inference
    await init_chat_settings()
    await settings_updated()
    # Initialize the commands
    lst_commands = await create_commands()
    await cl.context.emitter.set_commands(lst_commands)
    # Add system prompt to the chat context
    cl.chat_context.add(
        cl.Message(content=os.getenv("SYSTEM_PROMPT"), type="system_message")
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
    settings["max_tokens"] = int(settings["max_tokens"])
    cl.user_session.set("settings", settings)


@cl.on_message
async def main(message: cl.Message) -> None:
    """Generate a response to the user's message."""

    if message.command == "resume":
        if len(message.elements) != 0:
            await generate_resume(message.elements)
        else:
            lst_files = await ask_files("Veuillez charger un fichier à résumer :")
            if lst_files:
                await generate_resume(lst_files)

    elif message.command == "qa":
        index = None
        if len(message.elements) != 0:
            index = await create_index(message.elements)
        else:
            lst_files = await ask_files(
                "Veuillez charger un fichier sur lequel poser des questions :"
            )
            if lst_files:
                index = await create_index(lst_files)
        if index:
            await generate_qa(index)

    # No command, but files
    elif message.command is None and message.elements != []:
        action = await ask_action_on_doc(files=message.elements)
        if action == "resume":
            await generate_resume(message.elements)
        elif action == "qa":
            index = await create_index(message.elements)
            await generate_qa(index)

    # No command, no file, just a message
    else:
        # Generate a response to the user's message based on history
        await request_llm(
            lst_messages=cl.chat_context.to_openai(),
        )


@cl.on_stop
def on_stop() -> None:
    print("The user wants to stop the task!")


@cl.on_chat_end
def on_chat_end() -> None:
    print("The user disconnected!")
