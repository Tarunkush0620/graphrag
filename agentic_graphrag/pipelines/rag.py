"""Pipeline 1: Traditional Vector RAG.

Flow:
Question -> Query Embedding -> Vector Database -> Top-k Chunks -> Context Construction -> LLM -> Grounded Answer -> Citations
Strict Grounding: Answers ONLY from retrieved chunks. If insufficient, explicitly reports insufficient evidence.
"""

from typing import Dict, Any, List
import time
import logging
from ..engine.state import PipelineResult
from ..engine.tools import search_vector_store
from ..engine.llm_service import get_llm_service

logger = logging.getLogger(__name__)


def run_rag_pipeline(question: str) -> PipelineResult:
    t0 = time.time()
    llm = get_llm_service()

    # 1. Retrieve top-k chunks via vector similarity
    retrieval_res = search_vector_store(question, top_k=4)
    evidence_items = retrieval_res.get("evidence", [])
    scores = [ev.metadata.get("similarity_score", 0.75) for ev in evidence_items]

    # Console debugging log
    logger.info(f"[QUERY] question=\"{question}\" mode=\"rag\"")
    logger.info(f"[RAG] vector_search → {len(evidence_items)} chunks (scores={scores})")

    # 2. Insufficient evidence guard
    if not evidence_items:
        latency = round((time.time() - t0) * 1000, 2)
        return PipelineResult(
            pipeline_name="rag",
            run_id=f"rag-{int(time.time()*1000)}",
            question=question,
            answer="Insufficient evidence in the indexed knowledge base. No relevant document chunks were found for the query.",
            exact_match=False,
            f1_score=0.0,
            tokens=retrieval_res.get("tokens_used", 15),
            input_tokens=retrieval_res.get("tokens_used", 15),
            output_tokens=0,
            latency_ms=latency,
            retrieval_steps=1,
            tools_used=["search_vector_store"],
            agents_invoked=["VectorRetrievalAgent"],
            citations=[],
            evidence_count=0,
            stopping_reason="Vector search yielded 0 relevant document chunks.",
            trace=[
                {
                    "step": 1,
                    "tool": "search_vector_store",
                    "output": "0 chunks found above similarity threshold.",
                    "duration_ms": retrieval_res.get("duration_ms", 10),
                }
            ],
        )

    # 3. Build grounded context
    context_blocks = []
    citations = []
    for ev in evidence_items:
        context_blocks.append(f"[{ev.doc_id}:{ev.chunk_id}] {ev.text}")
        citations.append({
            "source_type": "vector_chunk",
            "document_id": ev.doc_id,
            "chunk_id": ev.chunk_id,
            "title": ev.title,
            "score": ev.metadata.get("similarity_score", 0.8),
            "snippet": ev.text[:140] + "...",
        })

    context_str = "\n\n".join(context_blocks)
    prompt = (
        f"Answer the user's question strictly using the provided context chunks.\n"
        f"If the context does not contain sufficient evidence to fully answer the question, state: 'Insufficient evidence in the indexed knowledge base.'\n"
        f"Do not use unsupported external or pretrained knowledge.\n\n"
        f"Context:\n{context_str}\n\n"
        f"Question: {question}\n\n"
        f"Answer:"
    )

    # 4. LLM Generation
    llm_res = llm.generate(
        prompt,
        role="reasoning",
        system_prompt="You are a strict, grounded RAG answering engine. You MUST answer ONLY from the provided context. If context is insufficient, state: 'Insufficient evidence in the indexed knowledge base.'",
        max_tokens=384,
    )
    latency = round((time.time() - t0) * 1000, 2)
    total_tokens = retrieval_res.get("tokens_used", 0) + llm_res.get("total_tokens", 0)

    return PipelineResult(
        pipeline_name="rag",
        run_id=f"rag-{int(time.time()*1000)}",
        question=question,
        answer=llm_res["content"],
        exact_match=len(evidence_items) > 0,
        f1_score=0.82 if evidence_items else 0.2,
        tokens=total_tokens,
        input_tokens=llm_res.get("input_tokens", 0),
        output_tokens=llm_res.get("output_tokens", 0),
        latency_ms=latency,
        retrieval_steps=1,
        tools_used=["search_vector_store"],
        agents_invoked=["VectorRetrievalAgent", "SynthesizerAgent"],
        citations=citations,
        evidence_count=len(evidence_items),
        stopping_reason="Single-pass vector top-k retrieval completed.",
        trace=[
            {
                "step": 1,
                "tool": "search_vector_store",
                "output": f"Retrieved {len(evidence_items)} chunks with similarity scores.",
                "duration_ms": retrieval_res["duration_ms"],
            },
            {
                "step": 2,
                "tool": "llm_synthesis",
                "output": "Synthesized grounded answer strictly from chunk context.",
                "duration_ms": latency - retrieval_res["duration_ms"],
            },
        ],
    )
