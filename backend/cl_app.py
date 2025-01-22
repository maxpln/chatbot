import chainlit as cl
from chainlit.types import ThreadDict
from openai import AsyncOpenAI
import os
from initialisation import *


@cl.on_chat_start
async def on_chat_start():
    """Initialize the chat session."""
    # Initialize the model
    cl.user_session.set("model_client", AsyncOpenAI(base_url=os.getenv("OLLAMA_URL"), api_key=os.getenv("OPENAI_API_KEY")))
    cl.user_session.set("model_name", os.getenv("OLLAMA_MODEL_NAME"))
    # Initialize the chat settings for inference
    settings = await init_chat_setting()
    await settings_update(settings)


@cl.on_settings_update
async def settings_update(settings):
    """Chat settings updated by the user."""
    cl.user_session.set("settings", settings)


@cl.on_message
async def main(message: cl.Message):
    """Generate a response to the user's message."""
    client = cl.user_session.get("model_client")
    model_name = cl.user_session.get("model_name")
    settings = cl.user_session.get("settings")

    # Call the model to generate a response and stream the response to the user
    msg = cl.Message(content="")
    stream = await client.chat.completions.create(
        messages=cl.chat_context.to_openai(), model=model_name, stream=True, **settings
    )
    async for part in stream:
        if token := part.choices[0].delta.content or "":
            await msg.stream_token(token)
    await msg.update()


@cl.on_stop
def on_stop():
    print("The user wants to stop the task!")


@cl.on_chat_end
def on_chat_end():
    print("The user disconnected!")


@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    print("The user resumed a previous chat session!")
