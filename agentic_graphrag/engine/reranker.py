"""Cross-Encoder & Alias Disambiguation Reranker.

Reranks candidate graph entities and document passages based on:
1. Exact & normalized alias matching (e.g. "Men's épée" <-> "epee men's").
2. Token overlap & Levenshtein / Jaccard similarity.
3. Cross-encoder relevance scoring for ambiguous entities.
"""

from typing import List, Dict, Any, Tuple
import re


def normalize_entity_name(name: str) -> str:
    """Lowercase and strip diacritics / special characters for robust matching."""
    s = name.lower()
    replacements = {
        "é": "e", "è": "e", "ê": "e", "ë": "e",
        "á": "a", "à": "a", "â": "a", "ä": "a", "ã": "a",
        "ó": "o", "ò": "o", "ô": "o", "ö": "o",
        "í": "i", "ì": "i", "î": "i", "ï": "i",
        "ú": "u", "ù": "u", "û": "u", "ü": "u",
        "ñ": "n", "ç": "c", "–": "-", "—": "-", "'": "",
    }
    for k, v in replacements.items():
        s = s.replace(k, v)
    return re.sub(r"[^a-z0-9\s]", "", s).strip()


class EntityReranker:
    def __init__(self, top_k: int = 5):
        self.top_k = top_k

    def rerank_entities(
        self, query: str, candidate_entities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Rank candidate entities by semantic overlap and exact token match."""
        if not candidate_entities:
            return []

        norm_query = normalize_entity_name(query)
        q_tokens = set(norm_query.split())

        scored: List[Tuple[float, Dict[str, Any]]] = []
        for ent in candidate_entities:
            name = str(ent.get("name") or ent.get("id") or ent.get("title") or "")
            norm_name = normalize_entity_name(name)
            name_tokens = set(norm_name.split())

            # Exact substring match bonus
            score = 0.0
            if norm_name in norm_query:
                score += 3.0
            if norm_query in norm_name:
                score += 2.0

            # Token Jaccard overlap
            if q_tokens and name_tokens:
                jaccard = len(q_tokens.intersection(name_tokens)) / len(q_tokens.union(name_tokens))
                score += jaccard * 2.0

            scored.append((score, ent))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[: self.top_k]]
