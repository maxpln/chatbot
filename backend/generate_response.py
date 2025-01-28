import chainlit as cl
from typing import List
from preprocessing import extract_text

from model import load_llm_model_openai


@cl.step(type="tool")
async def request_llm(lst_messages: List) -> cl.Message:
    """Generate a response to the user's message."""
    model_client = await load_llm_model_openai()
    settings = cl.user_session.get("settings")

    # Call the model to generate a response and stream the response to the user
    msg = cl.Message(content="", author="chatbot")
    stream = await model_client.chat.completions.create(
        messages=lst_messages,
        stream=True,
        **settings,
    )
    async for part in stream:
        if token := part.choices[0].delta.content or "":
            await msg.stream_token(token)
    await msg.update()
    return msg


async def generate_resume(lst_elements: List) -> None:
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
        ]
    )


async def generate_qa(index) -> None:
    keep_qa = True
    while keep_qa:
        rep_user = await cl.AskUserMessage(
            content="Quelle est votre question?", timeout=10
        ).send()
        if rep_user:
            # await cl.Message(content=f"Question: {prompt['content']}").send()
            # await cl.Message(content=f"Recherche de la réponse...").send()
            user_question = rep_user["output"]
            retriever = index.as_retriever(similarity_top_k=2)
            nodes = retriever.retrieve(user_question)
            concat_text = f"""Question : {user_question}\n\nContexte :\n{" ".join([node.text for node in nodes])}"""
            msg = await request_llm(
                lst_messages=[
                    {
                        "content": "You are a helpful assistant. You will answer the user question based on the context provided.",
                        "role": "system",
                    },
                    {"content": concat_text, "role": "user"},
                ]
            )
            msg.elements = [
                cl.Text(name=f"Extrait {i + 1}", content=node.text, display="inline")
                for i, node in enumerate(nodes)
            ]
            await msg.update()
            res = await cl.AskActionMessage(
                content="Choisis une action!",
                actions=[
                    cl.Action(
                        name="continue",
                        payload={"value": True},
                        label="✅ Poser une question sur le document",
                    ),
                    cl.Action(
                        name="cancel",
                        payload={"value": False},
                        label="❌ Arreter les questions sur le document",
                    ),
                ],
            ).send()
            keep_qa = res.get("payload").get("value") if res else False
