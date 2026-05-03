import datetime
import logging
import os
import uuid

from dotenv import load_dotenv
from fastapi import FastAPI
import inngest
import inngest.fast_api
from inngest.experimental import ai

from data_loader import load_and_chunk_pdf, embed_texts
from vector_db import QdrantStorage
from custom_types import RAGSearchResult, RAGUpsertResult, RAGChunkAndSrc

load_dotenv()

inngest_client = inngest.Inngest(
    app_id="rag_app",
    logger=logging.getLogger("uvicorn"),
    is_production=False,
    serializer=inngest.PydanticSerializer(),
)


@inngest_client.create_function(
    fn_id="RAG: Ingest PDF",
    trigger=inngest.TriggerEvent(event="rag/ingest_pdf"),
    rate_limit=inngest.RateLimit(
        limit=1,
        period=datetime.timedelta(hours=4),
        key="event.data.source_id",
    ),
)
async def rag_ingest_pdf(ctx: inngest.Context):
    try:
        def _load() -> RAGChunkAndSrc:
            pdf_path = ctx.event.data["pdf_path"]
            source_id = ctx.event.data.get(
                "source_id",
                os.path.basename(pdf_path),
            )

            chunks = load_and_chunk_pdf(pdf_path)

            return RAGChunkAndSrc(
                chunks=chunks,
                source_id=source_id,
            )

        def _upsert(chunks_and_src: RAGChunkAndSrc) -> RAGUpsertResult:
            chunks = chunks_and_src.chunks
            source_id = chunks_and_src.source_id

            if not chunks:
                return RAGUpsertResult(ingested=0)

            vecs = embed_texts(chunks)

            ids = [
                str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source_id}:{i}"))
                for i in range(len(chunks))
            ]

            payloads = [
                {
                    "source": source_id,
                    "text": chunks[i],
                }
                for i in range(len(chunks))
            ]

            QdrantStorage().upsert(ids, vecs, payloads)

            return RAGUpsertResult(ingested=len(chunks))

        chunks_and_src = await ctx.step.run(
            "load-and-chunk",
            _load,
            output_type=RAGChunkAndSrc,
        )

        ingested = await ctx.step.run(
            "embed-and-upsert",
            lambda: _upsert(chunks_and_src),
            output_type=RAGUpsertResult,
        )

        return ingested.model_dump()
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise e


@inngest_client.create_function(
    fn_id="RAG: Query PDF",
    trigger=inngest.TriggerEvent(event="rag/query_pdf_ai"),
)
async def rag_query_pdf_ai(ctx: inngest.Context):
    try:
        def _search(question: str, top_k: int = 5) -> RAGSearchResult:
            query_vec = embed_texts([question])[0]

            store = QdrantStorage()
            found = store.search(query_vec, top_k)

            return RAGSearchResult(
                contexts=found["contexts"],
                sources=found["sources"],
            )

        question = ctx.event.data["question"]
        top_k = int(ctx.event.data.get("top_k", 5))

        found = _search(question, top_k)

        context_block = "\n\n".join(
            f"- {context}" for context in found.contexts
        )

        user_content = (
            "Use the following context to answer the question.\n\n"
            f"Context:\n{context_block}\n\n"
            f"Question: {question}\n\n"
            "Answer concisely using only the context above."
        )

        from google import genai
        from google.genai import types
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY", ""))
        resp = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"System: You are an expert analyst. Answer the user's question clearly, comprehensively, and completely accurately based ONLY on the provided context. If the context does not contain the answer, say so directly. Use formatting like bullet points or bold text to make your answer highly readable.\n\nUser: {user_content}",
            config=types.GenerateContentConfig(temperature=0.1)
        )
        answer = resp.text.strip()

        return {
            "answer": answer,
            "sources": found.sources,
            "num_contexts": len(found.contexts),
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise e


app = FastAPI()

inngest.fast_api.serve(
    app,
    inngest_client,
    [
        rag_ingest_pdf,
        rag_query_pdf_ai,
    ],
)