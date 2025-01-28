from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from openai import AsyncOpenAI
import os
import chainlit as cl


async def load_embed_model_hf() -> HuggingFaceEmbedding:
    """Load an embedding model from HuggingFace."""
    embed_model = HuggingFaceEmbedding(model_name=os.getenv("EMBEDDING_MODEL_PATH"))
    return embed_model


async def load_llm_model_openai() -> AsyncOpenAI:
    """Load an LLM model from OpenAI client."""
    client = AsyncOpenAI(
        base_url=os.getenv("OLLAMA_URL"), api_key=os.getenv("OPENAI_API_KEY")
    )
    cl.instrument_openai()  # To monitor the generation of the response with literalai
    return client
