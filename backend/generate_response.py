import chainlit as cl
from typing import List, Dict
from openai import AsyncOpenAI
from extract_text import extract_text


@cl.step(type="tool")
async def request_llm(lst_messages: List, client: AsyncOpenAI, settings: Dict):
    """Generate a response to the user's message.""" ""

    # Call the model to generate a response and stream the response to the user
    msg = cl.Message(content="", author="chatbot")
    stream = await client.chat.completions.create(
        messages=lst_messages,
        stream=True,
        **settings,
    )
    async for part in stream:
        if token := part.choices[0].delta.content or "":
            await msg.stream_token(token)
    await msg.update()


async def generate_resume(lst_elements: List):
    """Generate a resume from a list of files."""
    # Concatenate all the extracted text from the files
    concat_text = ""
    for file in lst_elements:
        filepath = file.path
        text = await extract_text(filepath)
        concat_text += text
    # Generate a resume from the concatenated text
    await request_llm(
        lst_messages=[
            {
                "content": "You are a helpful assistant. You will generate a summary from the text provided.",
                "role": "system",
            },
            {"content": concat_text, "role": "user"},
        ],
        client=cl.user_session.get("model_client"),
        settings=cl.user_session.get("settings"),
    )
