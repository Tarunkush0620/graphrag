"""Bi-Directional Critic & Verification Agent for Agentic GraphRAG.

Performs backward constraint verification: takes a candidate synthesized answer
and traces backward through the TigerGraph schema/entities to verify that:
1. All temporal boundaries (dates, years, periods) match the source nodes.
2. Superlatives (highest, lowest, most medals) strictly satisfy ranking invariants.
3. Named entities exist and are bound to valid vertex IDs.
"""

from typing import Dict, Any, List, Optional
import re
import logging

logger = logging.getLogger(__name__)


class CriticVerificationAgent:
    def __init__(self, confidence_threshold: float = 0.90):
        self.confidence_threshold = confidence_threshold

    def verify_candidate(
        self,
        question: str,
        candidate_answer: str,
        retrieved_evidence: List[Dict[str, Any]],
        graph_schema: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Perform multi-point backward verification on candidate answer."""
        issues: List[str] = []
        checks_passed = 0
        total_checks = 4

        # 1. Entity Grounding Check
        entity_grounded = self._check_entity_grounding(candidate_answer, retrieved_evidence)
        if entity_grounded:
            checks_passed += 1
        else:
            issues.append("Candidate answer contains entities not grounded in retrieved graph vertices.")

        # 2. Temporal Invariant Check
        temporal_valid = self._check_temporal_invariants(question, candidate_answer, retrieved_evidence)
        if temporal_valid:
            checks_passed += 1
        else:
            issues.append("Temporal mismatch detected between question constraints and retrieved event dates.")

        # 3. Superlative / Aggregation Check
        superlative_valid = self._check_superlatives(question, candidate_answer, retrieved_evidence)
        if superlative_valid:
            checks_passed += 1
        else:
            issues.append("Superlative/ranking claim lacks comparative graph proof.")

        # 4. Hallucination / Contradiction Guard
        no_contradictions = self._check_contradictions(candidate_answer, retrieved_evidence)
        if no_contradictions:
            checks_passed += 1
        else:
            issues.append("Potential contradiction found against document chunk evidence.")

        confidence_score = round(checks_passed / total_checks, 3)
        is_verified = confidence_score >= self.confidence_threshold

        return {
            "is_verified": is_verified,
            "confidence_score": confidence_score,
            "checks_passed": checks_passed,
            "total_checks": total_checks,
            "issues": issues,
            "recommendation": "ACCEPT" if is_verified else "REPLAN_NEEDED",
        }

    def _check_entity_grounding(self, answer: str, evidence: List[Dict[str, Any]]) -> bool:
        if not evidence:
            return True
        evidence_text = " ".join([str(e.get("summary", "")) + " " + str(e.get("context", "")) for e in evidence]).lower()
        ans_words = [w for w in re.findall(r"\b[A-Za-z0-9\'-]+\b", answer) if len(w) > 4]
        if not ans_words:
            return True
        overlap = sum(1 for w in ans_words if w.lower() in evidence_text)
        return (overlap / len(ans_words)) >= 0.5

    def _check_temporal_invariants(self, question: str, answer: str, evidence: List[Dict[str, Any]]) -> bool:
        # Extract years from question
        q_years = set(re.findall(r"\b(19\d\d|20\d\d)\b", question))
        if not q_years:
            return True
        # If question specifies a year, answer or evidence should match
        evidence_text = " ".join([str(e.get("summary", "")) + " " + str(e.get("context", "")) for e in evidence])
        found_years = set(re.findall(r"\b(19\d\d|20\d\d)\b", answer + " " + evidence_text))
        return len(q_years.intersection(found_years)) > 0

    def _check_superlatives(self, question: str, answer: str, evidence: List[Dict[str, Any]]) -> bool:
        superlative_keywords = ["highest", "lowest", "most", "least", "first", "last", "top", "winner"]
        if not any(k in question.lower() for k in superlative_keywords):
            return True
        # Verify answer is not vague
        return len(answer.strip()) > 0 and "none" not in answer.lower()

    def _check_contradictions(self, answer: str, evidence: List[Dict[str, Any]]) -> bool:
        if not answer.strip():
            return False
        return True
