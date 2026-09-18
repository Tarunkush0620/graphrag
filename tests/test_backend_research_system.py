import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agentic_graphrag.engine.state import AgentState, InvestigationStep, EvidenceItem
from agentic_graphrag.engine.vector_store import get_vector_store
from agentic_graphrag.engine.tigergraph_client import get_tigergraph_client
from agentic_graphrag.engine.tools import search_vector_store, link_entities, traverse_graph, evaluate_evidence
from agentic_graphrag.pipelines.rag import run_rag_pipeline
from agentic_graphrag.pipelines.graphrag import run_graphrag_pipeline
from agentic_graphrag.pipelines.agentic import run_agentic_pipeline
from agentic_graphrag.engine.ingestion import ingest_sample_corpus
from agentic_graphrag.agents.critic_agent import CriticVerificationAgent


class TestAgenticGraphRAGSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ingest_sample_corpus()
    def test_vector_search(self):
        res = search_vector_store("Tennis at Olympic Tennis Centre", top_k=2)
        self.assertTrue(res["ok"])
        self.assertGreater(len(res["evidence"]), 0)

    def test_graph_traversal(self):
        tg = get_tigergraph_client()
        res = tg.traverse("Person_A", max_hops=3)
        self.assertGreater(res["visited_node_count"], 1)
        self.assertIn("Company_B", res["nodes"])

    def test_rag_pipeline(self):
        res = run_rag_pipeline("Who won the gold medal in tennis in August 2004?")
        self.assertEqual(res.pipeline_name, "rag")
        self.assertGreater(res.tokens, 0)
        self.assertGreater(len(res.citations), 0)

    def test_graphrag_pipeline(self):
        res = run_graphrag_pipeline("Which companies are connected to Person A?")
        self.assertEqual(res.pipeline_name, "graphrag")
        self.assertGreater(res.tokens, 0)
        self.assertGreaterEqual(res.retrieval_steps, 2)

    def test_agentic_pipeline(self):
        res = run_agentic_pipeline("Determine whether Person A and Company B are connected.")
        self.assertEqual(res.pipeline_name, "agentic_graphrag")
        self.assertGreater(res.tokens, 0)
        self.assertGreater(len(res.tools_used), 1)
        self.assertIsNotNone(res.stopping_reason)
        self.assertIsNotNone(res.trace)

    def test_critic_agent(self):
        critic = CriticVerificationAgent()
        res = critic.verify_candidate(
            question="Who won gold in 2004 tennis?",
            candidate_answer="Nicolás Massú won in 2004.",
            retrieved_evidence=[{"summary": "Nicolás Massú tennis gold 2004 Athens", "context": "Tennis tournament"}],
        )
        self.assertTrue(res["is_verified"])
        self.assertEqual(res["recommendation"], "ACCEPT")


if __name__ == "__main__":
    unittest.main()
