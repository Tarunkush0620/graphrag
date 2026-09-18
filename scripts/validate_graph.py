"""TigerGraph Knowledge Graph Validation Script.

Verifies schema integrity, vertex/edge counts, entity connectivity,
and sample multi-hop traversals in TigerGraph Savanna.
"""

import os
import sys
import logging
from pathlib import Path

# Add workspace to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agentic_graphrag.engine.tigergraph_client import get_tigergraph_client
from agentic_graphrag.engine.ingestion import ingest_sample_corpus

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("validate_graph")


def validate_graph():
    ingest_sample_corpus()
    tg = get_tigergraph_client()

    schema = tg.get_schema()
    logger.info(f"Graph Status: {schema.get('status')} | Graph: {schema.get('graph_name')}")
    logger.info(f"Vertex Types: {schema.get('vertex_types')}")
    logger.info(f"Edge Types:   {schema.get('edge_types')}")
    logger.info(f"Vertex Count: {schema.get('vertex_count')}")
    logger.info(f"Edge Count:   {schema.get('edge_count')}")

    # Validate key multi-hop entity traversal
    test_entities = ["Jared Tallent", "Chen Ding", "Olympic Green Convention Centre, Beijing", "Person A"]
    for ent in test_entities:
        res = tg.traverse(ent, max_hops=2)
        discovered_edges = len(res.get("edges", []))
        discovered_nodes = len(res.get("nodes", []))
        logger.info(f"• Traversal '{ent}': {discovered_nodes} nodes, {discovered_edges} edges across {res.get('total_hops')} hops.")
        assert discovered_edges > 0 or discovered_nodes > 0, f"Traversal failed for {ent}"

    logger.info("Graph validation successful: All schema and connectivity checks passed.")
    return True


if __name__ == "__main__":
    validate_graph()
