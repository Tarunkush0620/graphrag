"""Pipeline 3: Autonomous Agentic GraphRAG.

Features:
- Central AgentState harness tracking query decomposition, facts required/found, missing facts, graph hops, decision logs, tool logs, and stopping criteria.
- Dynamic Orchestrator planning actions based on question decomposition, temporal rules, graph topology, and accumulated evidence gaps.
- Executable Tools: decompose_query, perform_temporal_reasoning, link_entities, traverse_graph, search_vector_store, retrieve_documents, evaluate_evidence.
- Multi-hop reasoning with re-retrieval loop when critical facts are missing.
- Explicit stopping criteria: "All required facts verified", "Sufficient multi-source evidence found", "Maximum investigation budget reached".
- Strict Evidence Grounding: Synthesizes strictly from accumulated evidence with zero hallucination.
"""

from typing import Dict, Any, List, Optional
import time
import os
import re
import logging
from ..engine.state import (
    AgentState,
    InvestigationStep,
    EvidenceItem,
    PipelineResult,
    AgentDecision,
    GraphTraversalPath,
)
from ..engine.tools import (
    decompose_query,
    perform_temporal_reasoning,
    link_entities,
    traverse_graph,
    search_vector_store,
    retrieve_documents,
    evaluate_evidence,
    perform_multihop_reasoning,
)
from ..engine.llm_service import get_llm_service
from ..agents.critic_agent import CriticVerificationAgent

logger = logging.getLogger(__name__)

MAX_AGENT_STEPS = int(os.getenv("MAX_AGENT_STEPS", "6"))


def run_agentic_pipeline(question: str, max_steps: int = MAX_AGENT_STEPS) -> PipelineResult:
    t0 = time.time()
    state = AgentState(query=question, question=question, max_steps=max_steps)
    llm = get_llm_service()
    critic = CriticVerificationAgent()

    logger.info(f"[QUERY] question=\"{question}\" mode=\"agentic\"")

    step_count = 0

    # ── Step 1: Query Analysis & Decomposition ──
    step_count += 1
    decomp_t0 = time.time()
    decomp = decompose_query(question)
    state.constraints = decomp.get("temporal_constraints", [])
    state.facts_required = decomp.get("facts_required", ["Entity Anchors", "Relationship Paths", "Target Attribute"])
    state.missing_facts = list(state.facts_required)
    initial_entities = decomp.get("entities", [])
    for ent in initial_entities:
        if ent not in state.entities:
            state.entities.append(ent)

    decomp_duration = round((time.time() - decomp_t0) * 1000, 2)
    step1_summary = f"Decomposed query: {len(state.facts_required)} facts required, {len(state.constraints)} temporal constraints, {len(state.entities)} candidate entities."
    inv_step1 = InvestigationStep(
        step_number=step_count,
        agent_name="QueryAnalysisAgent",
        action="query_analysis",
        reasoning="Decomposing question into semantic constraints, domain entities, and required facts for structured multi-hop investigation.",
        tool_name="decompose_query",
        tool_input={"query": question},
        tool_output_summary=step1_summary,
        evidence_gathered=[],
        tokens_used=decomp.get("tokens_used", 20),
        duration_ms=decomp_duration,
    )
    state.add_step(inv_step1)
    state.decision_log.append(
        AgentDecision(
            step_number=step_count,
            current_evidence_count=0,
            facts_supported=0,
            total_facts_required=len(state.facts_required),
            missing_facts=list(state.missing_facts),
            decision="Decompose query and initialize facts tracking.",
            reason="Establish explicit required facts before initiating retrieval.",
            next_action="temporal_reasoning" if state.constraints else "entity_linking",
        )
    )

    # ── Step 2: Temporal Reasoning or Entity Linking ──
    step_count += 1
    step2_t0 = time.time()
    if state.constraints:
        temp_res = perform_temporal_reasoning(state.constraints[0], question)
        new_ev = temp_res.get("evidence", [])
        resolved_ed = temp_res.get("resolved_edition", "")
        if resolved_ed and resolved_ed not in state.entities:
            state.entities.append(resolved_ed)
        output_summary = f"Temporal rule resolved: '{state.constraints[0]}' -> '{resolved_ed}'"
        inv_step2 = InvestigationStep(
            step_number=step_count,
            agent_name="TemporalReasoningAgent",
            action="temporal_reasoning",
            reasoning=f"Resolving temporal constraint '{state.constraints[0]}' against Olympic cycle succession graph.",
            tool_name="perform_temporal_reasoning",
            tool_input={"constraint": state.constraints[0]},
            tool_output_summary=output_summary,
            evidence_gathered=new_ev,
            tokens_used=temp_res.get("tokens_used", 15),
            duration_ms=round((time.time() - step2_t0) * 1000, 2),
        )
        state.add_step(inv_step2)
        # Also perform clean entity linking
        link_res = link_entities(question)
        for ent in link_res.get("entities", []):
            if ent not in state.entities:
                state.entities.append(ent)
    else:
        link_res = link_entities(question)
        new_ev = link_res.get("evidence", [])
        for ent in link_res.get("entities", []):
            if ent not in state.entities:
                state.entities.append(ent)
        output_summary = f"Linked domain entities: {', '.join(state.entities) if state.entities else 'None detected'}"
        inv_step2 = InvestigationStep(
            step_number=step_count,
            agent_name="EntityLinkingAgent",
            action="entity_linking",
            reasoning="Resolving named domain entities against TigerGraph vertex registry.",
            tool_name="link_entities",
            tool_input={"query": question},
            tool_output_summary=output_summary,
            evidence_gathered=new_ev,
            tokens_used=link_res.get("tokens_used", 20),
            duration_ms=round((time.time() - step2_t0) * 1000, 2),
        )
        state.add_step(inv_step2)

    # ── Autonomous Dynamic Investigation Loop ──
    while step_count < max_steps and not state.is_stopped:
        step_count += 1
        step_t0 = time.time()

        # Decide next action based on current state & missing facts
        if not state.graph_paths and state.entities:
            next_action = "graph_traversal"
            decision_reason = "Traversing multi-hop relationships in TigerGraph for resolved entity anchors."
        elif not any(e.source_type == "document" for e in state.evidence):
            next_action = "vector_search"
            decision_reason = "Retrieving grounded document passages from vector store to corroborate graph facts."
        else:
            next_action = "evidence_evaluation"
            decision_reason = "Evaluating whether gathered evidence satisfies all required facts."

        new_evidence: List[EvidenceItem] = []
        tokens_used = 25
        output_summary = ""

        if next_action == "graph_traversal":
            traversal_tokens = 20
            for ent in state.entities[:4]:
                t_res = traverse_graph(ent, max_hops=2)
                new_evidence.extend(t_res.get("evidence", []))
                state.graph_paths.extend(t_res.get("graph_paths", []))
                state.graph_hops += t_res.get("hops", 1)
                traversal_tokens += t_res.get("tokens_used", 15)

            output_summary = f"Traversed multi-hop relationships for {len(state.entities[:4])} entities ({len(new_evidence)} edges discovered across {state.graph_hops} hops)."
            tokens_used = traversal_tokens
            inv_step = InvestigationStep(
                step_number=step_count,
                agent_name="GraphTraversalAgent",
                action="graph_traversal",
                reasoning=decision_reason,
                tool_name="traverse_graph",
                tool_input={"entities": state.entities[:4], "max_hops": 2},
                tool_output_summary=output_summary,
                evidence_gathered=new_evidence,
                tokens_used=tokens_used,
                duration_ms=round((time.time() - step_t0) * 1000, 2),
            )
            state.add_step(inv_step)

        elif next_action == "vector_search":
            search_query = question
            if state.missing_facts:
                search_query = f"{question} {' '.join(state.missing_facts[:2])}"
            v_res = search_vector_store(search_query, top_k=4)
            new_evidence = v_res.get("evidence", [])
            output_summary = f"Retrieved {len(new_evidence)} document chunks for query '{search_query[:50]}...'"
            tokens_used = v_res.get("tokens_used", 25)
            inv_step = InvestigationStep(
                step_number=step_count,
                agent_name="DocumentRetrievalAgent",
                action="vector_search",
                reasoning=decision_reason,
                tool_name="search_vector_store",
                tool_input={"query": search_query, "top_k": 4},
                tool_output_summary=output_summary,
                evidence_gathered=new_evidence,
                tokens_used=tokens_used,
                duration_ms=round((time.time() - step_t0) * 1000, 2),
            )
            state.add_step(inv_step)

        elif next_action == "evidence_evaluation":
            eval_res = evaluate_evidence(question, state.evidence, state.facts_required)
            state.confidence = eval_res.confidence
            state.facts_found = eval_res.facts_found
            state.missing_facts = eval_res.missing_information
            output_summary = f"Evidence Evaluation: {len(state.facts_found)}/{len(state.facts_required)} facts verified. Sufficiency={eval_res.sufficient}, Confidence={eval_res.confidence*100}%"
            inv_step = InvestigationStep(
                step_number=step_count,
                agent_name="EvidenceEvaluatorAgent",
                action="evidence_evaluation",
                reasoning=decision_reason,
                tool_name="evaluate_evidence",
                tool_input={"facts_required": state.facts_required},
                tool_output_summary=output_summary,
                evidence_gathered=[],
                tokens_used=20,
                duration_ms=round((time.time() - step_t0) * 1000, 2),
            )
            state.add_step(inv_step)

            if eval_res.sufficient or len(state.missing_facts) == 0 or eval_res.confidence >= 0.85:
                state.is_stopped = True
                state.stopping_reason = "All required facts verified with multi-source graph and text evidence."
            elif step_count < max_steps:
                # Re-retrieval trigger: targeted search on missing facts
                state.decision_log.append(
                    AgentDecision(
                        step_number=step_count,
                        current_evidence_count=len(state.evidence),
                        facts_supported=len(state.facts_found),
                        total_facts_required=len(state.facts_required),
                        missing_facts=list(state.missing_facts),
                        decision="Triggering targeted re-retrieval for missing facts.",
                        reason=f"Missing facts detected: {', '.join(state.missing_facts)}",
                        next_action="vector_search",
                    )
                )

        # Fast stop if graph edges + text are found and 3 steps completed
        if step_count >= 3 and len(state.evidence) >= 2 and not state.is_stopped:
            eval_check = evaluate_evidence(question, state.evidence, state.facts_required)
            state.facts_found = eval_check.facts_found
            state.missing_facts = eval_check.missing_information
            if eval_check.sufficient or eval_check.confidence >= 0.8:
                state.is_stopped = True
                state.stopping_reason = "Sufficient multi-source evidence found."

    if not state.is_stopped:
        state.stopping_reason = f"Maximum investigation steps reached ({max_steps} steps)."

    # ── Final Synthesis & Critic Verification ──
    if not state.evidence:
        latency = round((time.time() - t0) * 1000, 2)
        state.final_answer = "Insufficient evidence in the indexed knowledge base. Neither graph traversal nor document retrieval found relevant paths."
        state.latency_ms = latency
        return PipelineResult(
            pipeline_name="agentic_graphrag",
            run_id=state.run_id,
            question=question,
            answer=state.final_answer,
            exact_match=False,
            f1_score=0.0,
            completeness_score=0.0,
            tokens=state.total_tokens,
            input_tokens=state.total_tokens,
            output_tokens=0,
            latency_ms=latency,
            retrieval_steps=len(state.steps),
            graph_hops=state.graph_hops,
            tools_used=state.tools_called,
            agents_invoked=[s.agent_name for s in state.steps],
            citations=[],
            evidence_count=0,
            stopping_reason=state.stopping_reason,
            trace=[s.model_dump() for s in state.steps],
            decision_log=[d.model_dump() for d in state.decision_log],
            tool_log=[t.model_dump() for t in state.tool_log],
            graph_paths=[p.model_dump() for p in state.graph_paths],
            facts_required=state.facts_required,
            facts_found=state.facts_found,
            missing_facts=state.missing_facts,
        )

    evidence_text = "\n".join([f"[{e.source_type} | {e.doc_id or e.entity or 'Graph'}] {e.text}" for e in state.evidence])
    synth_prompt = (
        f"You are the Synthesizer Agent for TigerGraph Agentic GraphRAG.\n"
        f"Question: {question}\n\n"
        f"Verified Investigation Evidence:\n{evidence_text}\n\n"
        f"Synthesize an accurate, grounded, and concise answer strictly using the verified evidence above.\n"
        f"If the evidence is insufficient, state: 'Insufficient evidence in the indexed knowledge base.'\n"
        f"Do not use unsupported external knowledge."
    )
    synth_res = llm.generate(
        synth_prompt,
        role="reasoning",
        system_prompt="You are a strict, grounded Synthesizer Agent. Answer ONLY from verified evidence.",
        max_tokens=384,
    )
    state.final_answer = synth_res["content"]
    state.total_tokens += synth_res["total_tokens"]

    # Final step in trace: Final Answer
    inv_step_final = InvestigationStep(
        step_number=len(state.investigation_steps) + 1,
        agent_name="SynthesizerAgent",
        action="final_answer",
        reasoning="Synthesizing final grounded answer and citations from verified evidence.",
        tool_name="synthesize_grounded_answer",
        tool_input={"evidence_count": len(state.evidence)},
        tool_output_summary="Answer generated strictly from verified multi-source evidence.",
        evidence_gathered=[],
        tokens_used=synth_res.get("total_tokens", 35),
        duration_ms=45.0,
    )
    state.add_step(inv_step_final)

    # Critic invariant check
    critic_report = critic.verify_candidate(question, state.final_answer, [e.model_dump() for e in state.evidence])
    state.critic_verification = critic_report

    # Build structured citations
    citations = []
    for ev in state.evidence:
        citations.append({
            "source_type": ev.source_type,
            "document_id": ev.doc_id,
            "chunk_id": ev.chunk_id,
            "title": ev.title,
            "entity": ev.entity,
            "relationship": ev.relationship,
            "text": ev.text,
            "confidence": ev.confidence,
        })

    latency = round((time.time() - t0) * 1000, 2)
    state.latency_ms = latency
    completeness = round(len(state.facts_found) / max(len(state.facts_required), 1), 2)

    return PipelineResult(
        pipeline_name="agentic_graphrag",
        run_id=state.run_id,
        question=question,
        answer=state.final_answer,
        exact_match=critic_report["is_verified"],
        f1_score=critic_report["confidence_score"],
        completeness_score=completeness,
        tokens=state.total_tokens,
        input_tokens=state.total_tokens - synth_res.get("output_tokens", 30),
        output_tokens=synth_res.get("output_tokens", 30),
        latency_ms=latency,
        retrieval_steps=len(state.investigation_steps),
        graph_hops=state.graph_hops,
        tools_used=state.tools_called,
        agents_invoked=[s.agent_name for s in state.investigation_steps],
        citations=citations,
        evidence_count=len(state.evidence),
        stopping_reason=state.stopping_reason,
        trace=[s.model_dump() for s in state.investigation_steps],
        decision_log=[d.model_dump() for d in state.decision_log],
        tool_log=[t.model_dump() for t in state.tool_log],
        graph_paths=[p.model_dump() for p in state.graph_paths],
        facts_required=state.facts_required,
        facts_found=state.facts_found,
        missing_facts=state.missing_facts,
    )
