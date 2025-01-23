import chainlit as cl
from chainlit.input_widget import Slider
import os
from typing import List, Dict


async def create_chat_profiles() -> List[cl.ChatProfile]:
    """Create list of chat profiles for the models available."""
    model_name = os.getenv("OLLAMA_MODEL_NAME")
    lst_chat_profiles = [
        cl.ChatProfile(
            name=f"{model_name}",
            markdown_description=f"{model_name} lancé avec ollama.",
            icon="/public/ollama.png",
        ),
    ]
    return lst_chat_profiles


async def create_starters() -> List[cl.Starter]:
    """Create a list of starter messages."""
    lst_starters = [
        cl.Starter(
            label="Hello",
            message="Hello, who are you ?",
            icon="/public/ollama.png",
        ),
        cl.Starter(
            label="Write a Pyhton code to create a chatbot.",
            message="Can you write a Python script to create a chatbot that can answer questions about machine learning.",
        ),
        cl.Starter(
            label="Explain superconductors",
            message="Explain superconductors like I'm five years old.",
        ),
    ]
    return lst_starters


async def init_chat_settings() -> cl.ChatSettings:
    """Initialize the chat settings."""
    settings = await cl.ChatSettings(
        [
            Slider(
                id="temperature",
                label="Temperature",
                initial=0.2,
                min=0,
                max=2,
                step=0.1,
            ),
            Slider(
                id="top_p",
                label="Top P",
                initial=0.9,
                min=0,
                max=1,
                step=0.1,
            ),
        ]
    ).send()
    return settings


async def create_actions() -> List[cl.Action]:
    """Create a list of possible actions."""
    lst_actions = [
        cl.Action(
            name="resume",
            icon="mouse-pointer-click",
            tooltip="Pour générer un résumé d'un document.",
            payload={},
            label="Résumé",
        )
    ]
    return lst_actions


async def create_commands() -> List[Dict[str, str]]:
    """Create a list of possible actions."""
    lst_commands = [
        {"id": "resume", "icon": "pen-line", "description": "Résumer un document."},
    ]
    return lst_commands
