from pypdf import PdfReader
from vector_db import QdrantStorage
from dotenv import load_dotenv

load_dotenv()

import os
from google import genai
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
EMBED_MODEL = "gemini-embedding-2"
EMBED_DIM = 3072

CHUNK_SIZE = 4000
CHUNK_OVERLAP = 500

def sliding_window_split(text: str, chunk_size: int, overlap: int) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start += (chunk_size - overlap)
    return chunks

def load_and_chunk_pdf(file_path: str) -> list[str]:
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text

    return sliding_window_split(text, CHUNK_SIZE, CHUNK_OVERLAP)

def embed_texts(texts: list[str]) -> list[list[float]]:
    embeddings = []
    for text in texts:
        response = client.models.embed_content(
            model=EMBED_MODEL,
            contents=text,
        )
        embeddings.append(response.embeddings[0].values)
    return embeddings