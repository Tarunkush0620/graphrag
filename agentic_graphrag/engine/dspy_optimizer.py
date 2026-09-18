"""DSPy-Compatible Prompt Optimization Engine.

Compiles and bootstraps optimized few-shot demonstrations for:
- Orchestrator Planning & Decomposition
- Dynamic GSQL / Cypher Query Generation
- Multi-Hop Verification Prompts
"""

from typing import List, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)


class AgenticDSPyOptimizer:
    def __init__(self, metric_threshold: float = 0.95):
        self.metric_threshold = metric_threshold
        self.optimized_signatures: Dict[str, Dict[str, Any]] = {}

    def compile_few_shot_examples(
        self, benchmark_questions: List[Dict[str, Any]], max_demos_per_type: int = 2
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group high-confidence benchmark traces into typed few-shot demonstrations."""
        demos_by_type: Dict[str, List[Dict[str, Any]]] = {}

        for q in benchmark_questions:
            qtype = q.get("qtype", "general")
            agentic = q.get("agentic", {})
            trace = q.get("trace", {})

            # Only select perfect exact matches with high confidence
            if agentic.get("em") and trace.get("confidence", 0) >= 0.95:
                if qtype not in demos_by_type:
                    demos_by_type[qtype] = []

                if len(demos_by_type[qtype]) < max_demos_per_type:
                    demos_by_type[qtype].append({
                        "question": q.get("question"),
                        "rationale": f"Decomposed into {trace.get('steps')} steps using {', '.join(trace.get('agents', []))}",
                        "tools": trace.get("tools", []),
                        "answer": agentic.get("answer"),
                    })

        self.optimized_signatures["compiled_demos"] = demos_by_type
        return demos_by_type

    def get_prompt_prefix(self, qtype: str) -> str:
        """Render few-shot context to prepend to planner prompts."""
        demos = self.optimized_signatures.get("compiled_demos", {}).get(qtype, [])
        if not demos:
            return ""

        lines = ["\n### Exemplar Multi-Agent Reasoning Chains:"]
        for i, d in enumerate(demos, 1):
            lines.append(f"Example {i}:")
            lines.append(f"Question: {d['question']}")
            lines.append(f"Plan: {d['rationale']}")
            lines.append(f"Answer: {d['answer']}\n")
        return "\n".join(lines)
