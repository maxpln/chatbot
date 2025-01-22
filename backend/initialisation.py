import chainlit as cl
from chainlit.input_widget import Select, Switch, Slider
from openai import OpenAI
import os


async def init_chat_setting():
    """Initialize the chat settings."""
    settings = await cl.ChatSettings(
        [Slider(
            id="temperature",
            label="Temperature",
            initial=0.2,
            min=0,
            max=2,
            step=0.1,
        )]
    ).send()
    return settings


@cl.set_chat_profiles
async def set_chat_profile():
    """Create chat profile to choose the LLM to use."""
    model_name = os.getenv("OLLAMA_MODEL_NAME")
    model_name = " ".join(model_name.split(":"))
    return [
        cl.ChatProfile(
            name=f"Ollama - {model_name}",
            markdown_description=f"{model_name} lancé avec ollama.",
            icon="/public/ollama.png",
        ),
    ]


@cl.set_starters
async def set_starters():
    """Create starter messages to show example to the user."""
    return [
        cl.Starter(
            label="Write a Pyhton code to create a chatbot.",
            message="Can you write a Python script to create a chatbot that can answer questions about machine learning.",
            icon="/public/ollama.png",
            ),
        cl.Starter(
            label="Explain superconductors",
            message="Explain superconductors like I'm five years old.",
            )
        ]
