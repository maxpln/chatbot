import os

import chainlit as cl
from markitdown import MarkItDown
from llama_index.core import SimpleDirectoryReader
from typing import List, Sequence
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
from model import load_embed_model_hf
from llama_index.core import VectorStoreIndex
from llama_index.core.schema import Document
from llama_index.core.schema import BaseNode
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


@cl.step(type="tool")
async def extract_text(file_name) -> str:
    """Extract text from file in Markdown format."""
    md = MarkItDown()
    result = md.convert(file_name)
    return result.text_content


@cl.step(type="tool")
async def extract_text_and_metadata(lst_file_path: List) -> List[Document]:
    """Extract text and metadata from file in Markdown format."""
    reader = SimpleDirectoryReader(input_files=lst_file_path)
    docs = reader.load_data()
    return docs


@cl.step(type="tool")
async def chunking(
    lst_documents: List[Document],
) -> (Sequence[BaseNode], HuggingFaceEmbedding):
    embeb_model = await load_embed_model_hf()
    pipeline = IngestionPipeline(
        transformations=[
            SentenceSplitter(
                chunk_size=os.getenv("CHUNK_SIZE", 512),
                chunk_overlap=os.getenv("CHUNK_OVERLAP", 10),
            ),
            embeb_model,
        ],
    )
    nodes = pipeline.run(documents=lst_documents)
    return nodes, embeb_model


@cl.step(type="tool")
async def create_index(lst_elements: List) -> VectorStoreIndex:
    lst_file_path = [file.path for file in lst_elements]
    docs = await extract_text_and_metadata(lst_file_path)
    nodes, embeb_model = await chunking(docs)
    print(f"Nombre de nodes traités par le pipeline : {len(nodes)}")
    index = VectorStoreIndex(nodes, embed_model=embeb_model)
    return index
