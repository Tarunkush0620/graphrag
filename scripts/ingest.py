"""Master Knowledge Graph Ingestion Pipeline for TigerGraph Savanna.

Orchestrates the complete ingestion workflow:
1. Connect to TigerGraph Savanna / initialize graph schema (`create_schema.py`).
2. Load athletes, venues, events, medals, and enterprise entities (`load_data.py`).
3. Install and register GSQL multi-hop queries (`create_queries.py`).
4. Validate schema and graph traversals (`validate_graph.py`).
"""

import sys
import logging
from pathlib import Path

# Add workspace to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.create_schema import create_schema
from scripts.load_data import load_dataset
from scripts.create_queries import create_queries
from scripts.validate_graph import validate_graph

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ingest")


def run_full_ingestion():
    logger.info("==================================================")
    logger.info("STARTING MASTER TIGERGRAPH INGESTION PIPELINE")
    logger.info("==================================================")

    logger.info("\n[STEP 1/4] Creating TigerGraph Schema...")
    create_schema()

    logger.info("\n[STEP 2/4] Loading Multi-Hop Olympic & Enterprise Dataset...")
    load_dataset()

    logger.info("\n[STEP 3/4] Registering GSQL Traversal Queries...")
    create_queries()

    logger.info("\n[STEP 4/4] Validating Graph Integrity and Traversals...")
    validate_graph()

    logger.info("\n==================================================")
    logger.info("MASTER INGESTION PIPELINE COMPLETED SUCCESSFULLY")
    logger.info("==================================================")


if __name__ == "__main__":
    run_full_ingestion()
