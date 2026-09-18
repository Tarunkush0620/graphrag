"""TigerGraph Data Loading Script.

Ingests Olympic athletes, events, venues, medals, predecessor cycles,
and multi-hop corporate network records into TigerGraph Savanna.
"""

import os
import sys
import logging
from pathlib import Path

# Add workspace to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agentic_graphrag.engine.ingestion import ingest_sample_corpus
from agentic_graphrag.engine.tigergraph_client import get_tigergraph_client
from agentic_graphrag.engine.vector_store import get_vector_store

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("load_data")


def load_dataset():
    logger.info("Initializing multi-hop Olympic & Corporate dataset ingestion...")
    ingest_sample_corpus()

    tg = get_tigergraph_client()
    vstore = get_vector_store()

    total_vertices = sum(len(v) for v in tg.vertices.values())
    total_edges = len(tg.edges)
    total_chunks = len(vstore.chunks)

    logger.info("==================================================")
    logger.info("DATA LOADING SUMMARY")
    logger.info(f"• Target Graph:       {tg.graph_name}")
    logger.info(f"• Total Vertices:     {total_vertices}")
    logger.info(f"• Total Edges:        {total_edges}")
    logger.info(f"• Vector Chunks:      {total_chunks}")
    logger.info("==================================================")

    return {
        "vertices": total_vertices,
        "edges": total_edges,
        "vector_chunks": total_chunks,
    }


if __name__ == "__main__":
    load_dataset()
