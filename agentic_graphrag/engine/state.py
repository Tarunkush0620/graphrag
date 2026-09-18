"""Central Agent State Harness and Data Models for Agentic GraphRAG.

Maintains immutable investigation state, evidence accumulation, tool traces,
token tracking, facts tracking, decision logs, and stopping criteria for full traceability.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import time
import uuid


class EvidenceItem(BaseModel):
    id: str = Field(default_factory=lambda: f"ev-{uuid.uuid4().hex[:8]}")
    source_type: str = "document"  # "document", "graph_edge", "graph_vertex", "temporal_rule", "computed"
    doc_id: Optional[str] = None
    chunk_id: Optional[str] = None
    title: Optional[str] = None
    text: str
    entity: Optional[str] = None
    relationship: Optional[str] = None
    confidence: float = 1.0
    timestamp: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class InvestigationStep(BaseModel):
    step_number: int
    agent_name: str
    action: str  # "query_analysis", "entity_linking", "temporal_reasoning", "vector_search", "graph_traversal", "document_retrieval", "evidence_evaluation", "final_answer"
    reasoning: str  # Operational rationale
    tool_name: str
    tool_input: Dict[str, Any] = Field(default_factory=dict)
    tool_output_summary: str = ""
    evidence_gathered: List[EvidenceItem] = Field(default_factory=list)
    tokens_used: int = 0
    duration_ms: float = 0.0
    status: str = "completed"  # "completed", "failed", "skipped"


class AgentDecision(BaseModel):
    step_number: int
    current_evidence_count: int
    facts_supported: int
    total_facts_required: int
    missing_facts: List[str] = Field(default_factory=list)
    decision: str
    reason: str
    next_action: str


class ToolLogEntry(BaseModel):
    step_number: int
    tool: str
    tool_input: str
    result_summary: str
    latency_ms: float
    tokens: int


class GraphTraversalPath(BaseModel):
    hop: int
    from_entity: str
    edge_type: str
    to_entity: str
    attributes: Dict[str, Any] = Field(default_factory=dict)


class EvidenceEvaluationResult(BaseModel):
    sufficient: bool = False
    confidence: float = 0.0
    facts_required: List[str] = Field(default_factory=list)
    facts_found: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    supported_claims: List[str] = Field(default_factory=list)
    unsupported_claims: List[str] = Field(default_factory=list)
    contradictions: List[str] = Field(default_factory=list)
    recommendation: str = "CONTINUE"  # "STOP_SUFFICIENT", "CONTINUE", "FALLBACK"


class AgentState(BaseModel):
    run_id: str = Field(default_factory=lambda: f"run-{uuid.uuid4().hex[:8]}")
    query: str
    question: str = ""
    target_pipeline: str = "agentic_graphrag"
    entities: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    facts_required: List[str] = Field(default_factory=list)
    facts_found: List[str] = Field(default_factory=list)
    missing_facts: List[str] = Field(default_factory=list)
    retrieved_documents: List[Dict[str, Any]] = Field(default_factory=list)
    graph_results: List[Dict[str, Any]] = Field(default_factory=list)
    graph_paths: List[GraphTraversalPath] = Field(default_factory=list)
    graph_hops: int = 0
    evidence: List[EvidenceItem] = Field(default_factory=list)
    actions_taken: List[str] = Field(default_factory=list)
    investigation_steps: List[InvestigationStep] = Field(default_factory=list)
    decision_log: List[AgentDecision] = Field(default_factory=list)
    tool_log: List[ToolLogEntry] = Field(default_factory=list)
    tools_called: List[str] = Field(default_factory=list)
    agents_invoked: List[str] = Field(default_factory=list)
    retrieval_steps: int = 0
    max_steps: int = 6
    confidence: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    latency_ms: float = 0.0
    is_stopped: bool = False
    stopping_reason: str = ""
    final_answer: str = ""
    critic_verification: Optional[Dict[str, Any]] = None
    citations: List[Dict[str, Any]] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        if not self.question:
            self.question = self.query

    @property
    def steps(self) -> List[InvestigationStep]:
        return self.investigation_steps

    def add_step(self, step: InvestigationStep):
        self.investigation_steps.append(step)
        self.tools_called.append(step.tool_name)
        self.actions_taken.append(step.action)
        self.retrieval_steps += 1
        if step.agent_name not in self.agents_invoked:
            self.agents_invoked.append(step.agent_name)
        self.total_tokens += step.tokens_used
        for ev in step.evidence_gathered:
            if not any(e.id == ev.id for e in self.evidence):
                self.evidence.append(ev)

        # Tool log entry
        self.tool_log.append(
            ToolLogEntry(
                step_number=step.step_number,
                tool=step.tool_name,
                tool_input=str(step.tool_input.get("target") or step.tool_input.get("query") or step.tool_input),
                result_summary=step.tool_output_summary,
                latency_ms=step.duration_ms,
                tokens=step.tokens_used,
            )
        )


class PipelineResult(BaseModel):
    pipeline_name: str  # "rag", "graphrag", "agentic_graphrag"
    run_id: str
    question: str
    answer: str
    exact_match: bool = False
    f1_score: float = 0.0
    completeness_score: float = 0.0
    grounding_score: float = 0.0
    tokens: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: float = 0.0
    retrieval_steps: int = 1
    graph_hops: int = 0
    tools_used: List[str] = Field(default_factory=list)
    agents_invoked: List[str] = Field(default_factory=list)
    citations: List[Dict[str, Any]] = Field(default_factory=list)
    evidence_count: int = 0
    stopping_reason: Optional[str] = None
    trace: Optional[List[Dict[str, Any]]] = None
    decision_log: Optional[List[Dict[str, Any]]] = None
    tool_log: Optional[List[Dict[str, Any]]] = None
    graph_paths: Optional[List[Dict[str, Any]]] = None
    facts_required: Optional[List[str]] = None
    facts_found: Optional[List[str]] = None
    missing_facts: Optional[List[str]] = None
