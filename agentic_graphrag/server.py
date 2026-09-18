"""Unified FastAPI Server for TigerGraph Agentic GraphRAG Research & Benchmarking System.

Endpoints:
- POST /api/query (Unified entry point for RAG, GraphRAG, Agentic GraphRAG, and Comparative mode)
- POST /api/rag/query (Direct Pipeline 1: Traditional RAG)
- POST /api/graphrag/query (Direct Pipeline 2: Standard GraphRAG)
- POST /api/agentic/query (Direct Pipeline 3: Autonomous Agentic GraphRAG)
- GET  /api/health (Health check)
- GET  /api/graph/schema (TigerGraph Schema)
- POST /api/graph/search (Entity lookup)
- POST /api/graph/traverse (Multi-hop BFS)
- POST /api/vector/search (Semantic Chunk Search)
- GET  /api/documents (Corpus Documents & Chunks)
- POST /api/benchmark/run (Automated benchmark suite)
- GET  /api/benchmark/results (Saved benchmark runs)
- GET  /api/trace/{trace_id} (Execution trace lookup)
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
import logging
import uvicorn

from .pipelines.rag import run_rag_pipeline
from .pipelines.graphrag import run_graphrag_pipeline
from .pipelines.agentic import run_agentic_pipeline
from .engine.tigergraph_client import get_tigergraph_client
from .engine.vector_store import get_vector_store
from .engine.tools import search_vector_store
from .engine.ingestion import ingest_sample_corpus

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Initialize FastAPI App
app = FastAPI(
    title="TigerGraph Agentic GraphRAG Research API",
    description="Benchmarking & Investigation Engine for Traditional RAG, GraphRAG, and Agentic GraphRAG",
    version="2.0.2",
)

# Enable CORS for React frontend (port 5173, 3000, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory execution store for real-time trace inspection
_EXECUTION_TRACES: Dict[str, Any] = {}
_BENCHMARK_RESULTS: List[Dict[str, Any]] = []

# Ensure sample data is ingested on server startup
ingest_sample_corpus()


# ── Request / Response Models ──
class QueryRequest(BaseModel):
    question: str = Field(..., description="Research or inquiry question to investigate")
    pipeline: Optional[str] = Field("agentic", description="rag | graphrag | agentic | compare | all")
    mode: Optional[str] = Field(None, description="Alias for pipeline: rag | graphrag | agentic | compare")
    max_steps: Optional[int] = Field(8, description="Maximum investigation steps for agentic pipeline")


class TraverseRequest(BaseModel):
    start_entity: str
    max_hops: Optional[int] = 2
    edge_filter: Optional[List[str]] = None


class VectorSearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5


class IngestRequest(BaseModel):
    documents: List[Dict[str, Any]]


# ── Health & Status ──
@app.get("/api/health")
def health_check():
    tg = get_tigergraph_client()
    vstore = get_vector_store()
    return {
        "status": "healthy",
        "tigergraph": {
            "connected": tg.is_connected,
            "mode": "LIVE_SERVER" if tg.is_connected else "EMBEDDED_GRAPH_ENGINE",
            "graph_name": tg.graph_name,
            "vertex_types": len(tg.vertices),
            "edges": len(tg.edges),
        },
        "vector_store": {
            "total_chunks": len(vstore.chunks),
        },
    }


# ── Unified Query Endpoint ──
@app.post("/api/query")
def execute_query(req: QueryRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    p_type = (req.mode or req.pipeline or "agentic").lower()
    logger.info(f"\n==================================================")
    logger.info(f"[QUERY] question=\"{req.question}\" mode=\"{p_type}\"")
    logger.info(f"==================================================")

    if p_type in ["all", "compare", "comparative_3_way"]:
        res_rag = run_rag_pipeline(req.question)
        res_graph = run_graphrag_pipeline(req.question)
        res_agentic = run_agentic_pipeline(req.question, max_steps=req.max_steps or 8)

        _EXECUTION_TRACES[res_rag.run_id] = res_rag
        _EXECUTION_TRACES[res_graph.run_id] = res_graph
        _EXECUTION_TRACES[res_agentic.run_id] = res_agentic

        # Structured sources & metrics for RAG
        rag_payload = {
            "pipeline": "rag",
            "answer": res_rag.answer,
            "sources": res_rag.citations,
            "retrieved_chunks": [c.get("document_id") for c in res_rag.citations],
            "scores": [c.get("score", 0.8) for c in res_rag.citations],
            "input_tokens": res_rag.input_tokens,
            "output_tokens": res_rag.output_tokens,
            "latency_ms": res_rag.latency_ms,
            "tokens": res_rag.tokens,
            "metrics": {
                "tokens": res_rag.tokens,
                "latency_ms": res_rag.latency_ms,
                "steps": res_rag.retrieval_steps,
                "exact_match": res_rag.exact_match,
            },
        }

        # Structured graph paths & metrics for GraphRAG
        graphrag_payload = {
            "pipeline": "graphrag",
            "answer": res_graph.answer,
            "entities": [c.get("entity") for c in res_graph.citations if c.get("entity")],
            "graph_paths": [c.get("detail") for c in res_graph.citations if c.get("source_type") == "graph_relationship"],
            "relationships": [c.get("relationship") for c in res_graph.citations if c.get("relationship")],
            "sources": res_graph.citations,
            "tokens": {
                "total": res_graph.tokens,
                "input": res_graph.input_tokens,
                "output": res_graph.output_tokens,
            },
            "latency_ms": res_graph.latency_ms,
            "metrics": {
                "tokens": res_graph.tokens,
                "latency_ms": res_graph.latency_ms,
                "steps": res_graph.retrieval_steps,
                "exact_match": res_graph.exact_match,
            },
        }

        # Structured trace & metrics for Agentic GraphRAG
        agentic_payload = {
            "pipeline": "agentic_graphrag",
            "answer": res_agentic.answer,
            "sources": res_agentic.citations,
            "trace": res_agentic.trace,
            "stopping_reason": res_agentic.stopping_reason,
            "tokens": res_agentic.tokens,
            "latency_ms": res_agentic.latency_ms,
            "metrics": {
                "tokens": res_agentic.tokens,
                "latency_ms": res_agentic.latency_ms,
                "steps": res_agentic.retrieval_steps,
                "tools_used": res_agentic.tools_used,
                "exact_match": res_agentic.exact_match,
                "f1_score": res_agentic.f1_score,
            },
        }

        return {
            "question": req.question,
            "mode": "compare",
            "rag": rag_payload,
            "graphrag": graphrag_payload,
            "agentic_graphrag": agentic_payload,
            # Backward compatibility aliases
            "agentic": agentic_payload,
        }

    elif p_type == "rag":
        res = run_rag_pipeline(req.question)
    elif p_type == "graphrag":
        res = run_graphrag_pipeline(req.question)
    else:
        res = run_agentic_pipeline(req.question, max_steps=req.max_steps or 8)

    _EXECUTION_TRACES[res.run_id] = res
    return res.model_dump()


@app.post("/api/rag/query")
def execute_rag(req: QueryRequest):
    res = run_rag_pipeline(req.question)
    _EXECUTION_TRACES[res.run_id] = res
    return res.model_dump()


@app.post("/api/graphrag/query")
def execute_graphrag(req: QueryRequest):
    res = run_graphrag_pipeline(req.question)
    _EXECUTION_TRACES[res.run_id] = res
    return res.model_dump()


@app.post("/api/agentic/query")
@app.post("/api/agentic-graphrag/query")
def execute_agentic(req: QueryRequest):
    res = run_agentic_pipeline(req.question, max_steps=req.max_steps or 8)
    _EXECUTION_TRACES[res.run_id] = res
    return res.model_dump()


# ── Graph Inspection APIs ──
@app.get("/api/graph/schema")
def get_graph_schema():
    tg = get_tigergraph_client()
    return tg.get_schema()


@app.post("/api/graph/search")
def search_graph(q: str = Query(..., description="Entity search string")):
    tg = get_tigergraph_client()
    return {"entities": tg.search_entities(q)}


@app.post("/api/graph/traverse")
def traverse(req: TraverseRequest):
    tg = get_tigergraph_client()
    return tg.traverse(req.start_entity, max_hops=req.max_hops, edge_filter=req.edge_filter)


@app.get("/api/graph/all")
def get_all_graph():
    tg = get_tigergraph_client()
    return {
        "vertices": tg.vertices,
        "edges": tg.edges,
        "summary": {
            "vertex_count": sum(len(v) for v in tg.vertices.values()),
            "edge_count": len(tg.edges),
        },
    }


# ── Vector Search & Documents ──
@app.post("/api/vector/search")
def vector_search(req: VectorSearchRequest):
    return search_vector_store(req.query, top_k=req.top_k)


@app.get("/api/documents")
def get_documents():
    vstore = get_vector_store()
    return {
        "total_chunks": len(vstore.chunks),
        "chunks": [c.model_dump() for c in list(vstore.chunks.values())[:50]],
    }


@app.post("/api/ingest")
def ingest_documents(req: IngestRequest):
    vstore = get_vector_store()
    vstore.add_documents(req.documents)
    return {"status": "success", "ingested_count": len(req.documents)}


# ── Trace Lookup ──
@app.get("/api/trace/{trace_id}")
def get_trace(trace_id: str):
    res = _EXECUTION_TRACES.get(trace_id)
    if not res:
        raise HTTPException(status_code=404, detail="Trace not found.")
    return res.model_dump()


# ── Benchmark Suite Runner ──
@app.post("/api/benchmark/run")
def run_benchmark(questions_count: int = Query(5, description="Number of questions to benchmark")):
    data_path = Path(__file__).resolve().parent.parent / "graphrag-ui" / "src" / "data" / "benchmark.json"
    if not data_path.exists():
        raise HTTPException(status_code=404, detail="Benchmark dataset not found.")

    with open(data_path, "r", encoding="utf-8") as f:
        bench_data = json.load(f)

    q_list = bench_data.get("questions", [])[:questions_count]
    results = []

    for item in q_list:
        q_text = item.get("question")
        gold = item.get("gold")
        qtype = item.get("qtype")

        r_rag = run_rag_pipeline(q_text)
        r_graph = run_graphrag_pipeline(q_text)
        r_agentic = run_agentic_pipeline(q_text)

        entry = {
            "qid": item.get("qid"),
            "question": q_text,
            "qtype": qtype,
            "gold": gold,
            "rag": r_rag.model_dump(),
            "graphrag": r_graph.model_dump(),
            "agentic": r_agentic.model_dump(),
        }
        results.append(entry)
        _BENCHMARK_RESULTS.append(entry)

    return {
        "status": "completed",
        "evaluated_questions": len(results),
        "results": results,
    }


@app.get("/api/benchmark/results")
def get_benchmark_results():
    if not _BENCHMARK_RESULTS:
        return {
            "status": "empty",
            "message": "No benchmark runs available.",
            "total_runs": 0,
            "results": [],
        }
    return {
        "status": "available",
        "total_runs": len(_BENCHMARK_RESULTS),
        "results": _BENCHMARK_RESULTS,
    }


@app.get("/api/metrics")
def get_metrics_summary():
    if not _BENCHMARK_RESULTS:
        return {
            "status": "empty",
            "message": "No benchmark runs available.",
        }

    # Calculate real dynamic metrics over actual runs
    rag_em = sum(1 for r in _BENCHMARK_RESULTS if r["rag"].get("exact_match", False)) / len(_BENCHMARK_RESULTS)
    graph_em = sum(1 for r in _BENCHMARK_RESULTS if r["graphrag"].get("exact_match", False)) / len(_BENCHMARK_RESULTS)
    agent_em = sum(1 for r in _BENCHMARK_RESULTS if r["agentic"].get("exact_match", False)) / len(_BENCHMARK_RESULTS)

    rag_tok = sum(r["rag"].get("tokens", 0) for r in _BENCHMARK_RESULTS) / len(_BENCHMARK_RESULTS)
    graph_tok = sum(r["graphrag"].get("tokens", 0) for r in _BENCHMARK_RESULTS) / len(_BENCHMARK_RESULTS)
    agent_tok = sum(r["agentic"].get("tokens", 0) for r in _BENCHMARK_RESULTS) / len(_BENCHMARK_RESULTS)

    return {
        "total_evaluated": len(_BENCHMARK_RESULTS),
        "rag": {
            "exact_match": round(rag_em, 3),
            "avg_tokens": round(rag_tok, 1),
        },
        "graphrag": {
            "exact_match": round(graph_em, 3),
            "avg_tokens": round(graph_tok, 1),
        },
        "agentic": {
            "exact_match": round(agent_em, 3),
            "avg_tokens": round(agent_tok, 1),
            "token_reduction_factor": round(rag_tok / max(1, agent_tok), 1),
        },
    }


if __name__ == "__main__":
    uvicorn.run("agentic_graphrag.server:app", host="0.0.0.0", port=8000, reload=False)
