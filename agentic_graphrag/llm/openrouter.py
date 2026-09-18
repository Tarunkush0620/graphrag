"""
OpenRouter Multi-Model LLM Adapter for TigerGraph Agentic GraphRAG
Configured with OpenRouter free-tier specialized model roles.
"""

import json
import logging
import time
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

import os
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# ── Specialized Model Roles from Architecture Spec ──
MODEL_ROLES = {
    # 1. Main Orchestrator & Multi-Step Reasoner
    "orchestrator": [
        "nvidia/nemotron-3-ultra-550b-a55b:free",
        "nvidia/nemotron-3.5-lightning:free",
        "nex-agi/nex-n2.5-pro:free",
    ],
    # 2. Tool & Agent Logic
    "tool_agent": [
        "qwen/qwen3-coder-480b-a35b:free",
        "cohere/north-mini-code:free",
        "google/gemma-4-31b-it:free",
    ],
    # 3. Main RAG / GraphRAG LLM
    "main_rag": [
        "qwen/qwen3-next-80b-a3b-instruct:free",
        "google/gemma-4-31b-it:free",
        "nvidia/nemotron-3.5-lightning:free",
    ],
    # 4. Evidence & Answer Generation
    "evidence_generation": [
        "google/gemma-4-31b-it:free",
        "google/gemma-4-26b-a4b-it:free",
        "z-ai/glm-5.2:free",
    ],
    # 5. Lightweight Agents (Fast single-hop / pruning)
    "lightweight_agent": [
        "google/gemma-4-26b-a4b-it:free",
        "liquid/lfm-2.5-2.6b:free",
        "nex-agi/nex-n2.5-mini:free",
    ],
    # 6. Agentic Multi-Hop Reasoning
    "agentic_reasoning": [
        "nex-agi/nex-n2.5-pro:free",
        "nvidia/nemotron-3-ultra-550b-a55b:free",
        "google/gemma-4-31b-it:free",
    ],
    # 7. Baseline General Purpose Comparison
    "baseline": [
        "meta-llama/llama-3.3-70b-instruct:free",
        "z-ai/glm-5.2:free",
        "google/gemma-4-31b-it:free",
    ],
    # 8. Experimental Agent
    "experimental": [
        "dots-studio/dots-3-note-preview:free",
        "thinkingmachines/inkling:free",
    ],
    # 9. Multimodal Sub-Agent
    "multimodal": [
        "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
        "inclusionai/ling-3.0-flash-vl:free",
    ],
}


class OpenRouterClient:
    """Client for querying OpenRouter models with automated role-based fallback."""

    def __init__(self, api_key: str = OPENROUTER_API_KEY):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://tigergraph.com",
            "X-Title": "TigerGraph Agentic GraphRAG",
        }

    def generate(
        self,
        messages: List[Dict[str, str]],
        role: str = "orchestrator",
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        """
        Generate completion using the prioritized model list for the given role,
        with automated fallback across the tier in case of rate-limiting (429).
        """
        candidate_models = MODEL_ROLES.get(role, MODEL_ROLES["orchestrator"])
        
        last_error = None
        for model_id in candidate_models:
            payload = {
                "model": model_id,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            req = urllib.request.Request(
                OPENROUTER_BASE_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers=self.headers,
            )
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    content = data["choices"][0]["message"]["content"]
                    usage = data.get("usage", {})
                    return {
                        "content": content,
                        "model": model_id,
                        "role": role,
                        "usage": usage,
                        "status": "success",
                    }
            except urllib.error.HTTPError as e:
                logger.warning(f"Model {model_id} returned HTTP {e.code}. Falling back...")
                last_error = e
                time.sleep(0.3)
                continue
            except Exception as e:
                logger.warning(f"Error querying {model_id}: {e}. Falling back...")
                last_error = e
                continue

        # If all candidates rate-limited, return structured error
        return {
            "content": "",
            "model": candidate_models[0],
            "role": role,
            "status": "error",
            "error": str(last_error),
        }


# Singleton instance for the repository
openrouter_client = OpenRouterClient()
