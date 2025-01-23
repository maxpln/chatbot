import chainlit as cl
from markitdown import MarkItDown


@cl.step(type="tool")
async def extract_text(file_name) -> str:
    md = MarkItDown()
    result = md.convert(file_name)
    return result.text_content
