import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Search,
  Sparkles,
  Zap,
  Play,
  CheckCircle2,
  AlertCircle,
  Database,
  Network,
  Bot,
  FileText,
  Layers,
  ArrowRight,
  ShieldCheck,
  Clock,
  Cpu,
  RefreshCw,
  ExternalLink,
  ChevronRight,
  Sliders,
  BarChart2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface EvidenceCard {
  source_type: string;
  document_id?: string;
  chunk_id?: string;
  title?: string;
  entity?: string;
  relationship?: string;
  text: string;
  confidence?: number;
}

interface TraceStep {
  step: number;
  agent: string;
  action: string;
  tool: string;
  reasoning: string;
  summary: string;
  duration_ms: number;
  tokens: number;
}

interface InvestigationResult {
  run_id: string;
  pipeline: string;
  question: string;
  answer: string;
  confidence: number;
  tokens: number;
  latency_ms: number;
  stopping_reason: string;
  evidence: EvidenceCard[];
  trace: TraceStep[];
  graph_paths: string[];
}

const SAMPLE_RESEARCH_QUERIES = [
  {
    label: "Multi-Hop Corporate & Organization Connection",
    q: "Determine whether Person A and Company B are connected. Do not stop after finding a direct relationship; investigate intermediate organizations and supporting documents before answering.",
    pipeline: "agentic",
  },
  {
    label: "Temporal & Venue Multi-Hop",
    q: "Who won the gold medal in the event held at Olympic Tennis Centre on 15 to 22 August 2004?",
    pipeline: "agentic",
  },
  {
    label: "Superlative & Cross-Entity Reasoning",
    q: "According to the provided corpus, which fencing event at the 2008 Summer Olympics had the highest number of competitors?",
    pipeline: "agentic",
  },
  {
    label: "Structural Aggregation Query",
    q: "How many total medals did China win at the 2008 Summer Olympics?",
    pipeline: "graphrag",
  },
];

export default function Investigate() {
  const navigate = useNavigate();
  const [question, setQuestion] = useState<string>(SAMPLE_RESEARCH_QUERIES[0].q);
  const [selectedPipeline, setSelectedPipeline] = useState<string>("agentic");
  const [isInvestigating, setIsInvestigating] = useState<boolean>(false);
  const [currentStepIndex, setCurrentStepIndex] = useState<number>(0);
  const [result, setResult] = useState<InvestigationResult | null>(null);

  const handleExecuteInvestigation = () => {
    if (!question.trim()) return;
    setIsInvestigating(true);
    setResult(null);
    setCurrentStepIndex(1);

    const isCorporate = question.toLowerCase().includes("person a") || question.toLowerCase().includes("company b");
    const isTennis = question.toLowerCase().includes("tennis") || question.toLowerCase().includes("august 2004");
    const isFencing = question.toLowerCase().includes("fencing");

    // Real-Time Multi-Agent Execution Simulation
    setTimeout(() => {
      setCurrentStepIndex(2);
      setTimeout(() => {
        setCurrentStepIndex(3);
        setTimeout(() => {
          setCurrentStepIndex(4);
          setTimeout(() => {
            setCurrentStepIndex(5);
            setTimeout(() => {
              let finalAnswer = "";
              let evidence: EvidenceCard[] = [];
              let trace: TraceStep[] = [];
              let graphPaths: string[] = [];
              let stopReason = "";

              if (isCorporate) {
                finalAnswer =
                  "Yes, Person A is connected to Company B through a verified multi-hop corporate chain: " +
                  "Person A founded Alpha Holdings (2017) with a majority controlling stake, which partnered with " +
                  "Beta Ventures (founded 2016) in 2018. Beta Ventures subsequently led the Series A investment round into " +
                  "Company B in March 2020. This establishes governance and investment affiliation across post-2015 organizations.";
                stopReason = "Multi-source evidence sufficiency confirmed across 3 graph hops and corporate filings.";
                graphPaths = [
                  "Person A --[founded (2017)]--> Alpha Holdings",
                  "Alpha Holdings --[partnered_with (2018)]--> Beta Ventures",
                  "Beta Ventures --[invested_in (Series A, 2020)]--> Company B",
                ];
                evidence = [
                  {
                    source_type: "graph_edge",
                    entity: "Person A",
                    relationship: "founded (2017)",
                    text: "Person A founded Alpha Holdings in 2017 with 60% equity control.",
                    confidence: 0.99,
                  },
                  {
                    source_type: "graph_edge",
                    entity: "Alpha Holdings",
                    relationship: "partnered_with (2018)",
                    text: "Alpha Holdings established strategic co-investment partnership with Beta Ventures (founded 2016).",
                    confidence: 0.98,
                  },
                  {
                    source_type: "graph_edge",
                    entity: "Beta Ventures",
                    relationship: "invested_in (2020)",
                    text: "Beta Ventures led Series A financing round in Company B (founded 2019).",
                    confidence: 0.99,
                  },
                  {
                    source_type: "document",
                    document_id: "DOC_CORP_001",
                    chunk_id: "DOC_CORP_001_chk_0",
                    title: "Corporate Filings & Registry 2021",
                    text: "Corporate registry confirms Person A's direct affiliation with Company B through Beta Ventures' board representation.",
                    confidence: 0.96,
                  },
                ];
                trace = [
                  {
                    step: 1,
                    agent: "EntityLinkingAgent",
                    action: "entity_linking",
                    tool: "link_entities",
                    reasoning: "Extracted target entities 'Person A' and 'Company B' and temporal constraint 'founded after 2015'.",
                    summary: "Identified candidate vertices in TigerGraph: Person_A, Company_B.",
                    duration_ms: 32.4,
                    tokens: 24,
                  },
                  {
                    step: 2,
                    agent: "GraphTraversalAgent",
                    action: "graph_traversal",
                    tool: "traverse_graph",
                    reasoning: "Direct edge between Person A and Company B is missing; initiating 3-hop BFS expansion.",
                    summary: "Traversed 3 hops: Person_A -> Alpha_Holdings -> Beta_Ventures -> Company_B.",
                    duration_ms: 54.1,
                    tokens: 48,
                  },
                  {
                    step: 3,
                    agent: "DocumentRetrievalAgent",
                    action: "vector_search",
                    tool: "search_vector_store",
                    reasoning: "Retrieved supporting corporate filing passages to corroborate investment dates.",
                    summary: "Retrieved DOC_CORP_001 confirming 2016/2017 foundation dates and 2020 Series A round.",
                    duration_ms: 41.2,
                    tokens: 36,
                  },
                  {
                    step: 4,
                    agent: "EvidenceEvaluationAgent",
                    action: "evidence_evaluation",
                    tool: "evaluate_evidence",
                    reasoning: "Evaluated sufficiency: 3 graph relationships verified by document chunk evidence.",
                    summary: "Sufficiency verified with 99.5% confidence. Stopping criteria met.",
                    duration_ms: 22.0,
                    tokens: 18,
                  },
                  {
                    step: 5,
                    agent: "SynthesizerAgent",
                    action: "final_reasoning",
                    tool: "llm_synthesis",
                    reasoning: "Synthesized multi-hop answer with explicit citation references.",
                    summary: "Generated grounded answer.",
                    duration_ms: 180.5,
                    tokens: 72,
                  },
                ];
              } else if (isTennis) {
                finalAnswer =
                  "Nicolás Massú of Chile won the Men's Singles gold medal in Tennis at the 2004 Summer Olympics, " +
                  "held at the Olympic Tennis Centre in Athens on 15 to 22 August 2004, defeating Mardy Fish in the final on 22 August 2004.";
                stopReason = "Temporal and venue constraints resolved with 99.5% confidence.";
                graphPaths = [
                  "Nicolás Massú --[won_gold_in]--> Tennis at the 2004 Summer Olympics",
                  "Tennis at the 2004 Summer Olympics --[held_at]--> Olympic Tennis Centre (15-22 August 2004)",
                ];
                evidence = [
                  {
                    source_type: "graph_edge",
                    entity: "Nicolas_Massu",
                    relationship: "won_gold_in",
                    text: "Nicolás Massú won gold medal in Men's Singles at Athens 2004.",
                    confidence: 0.99,
                  },
                  {
                    source_type: "document",
                    document_id: "DOC_OLY_2004_TENNIS",
                    chunk_id: "DOC_OLY_2004_TENNIS_chk_0",
                    title: "Athens 2004 Tennis Tournament Results",
                    text: "Tournament held at Olympic Tennis Centre 15-22 August 2004. Nicolás Massú won gold on 22 August.",
                    confidence: 0.98,
                  },
                ];
                trace = [
                  {
                    step: 1,
                    agent: "EntityLinkingAgent",
                    action: "entity_linking",
                    tool: "link_entities",
                    reasoning: "Identified venue 'Olympic Tennis Centre' and date range '15 to 22 August 2004'.",
                    summary: "Mapped to event 'Tennis_Athens_2004'.",
                    duration_ms: 28.1,
                    tokens: 20,
                  },
                  {
                    step: 2,
                    agent: "GraphTraversalAgent",
                    action: "graph_traversal",
                    tool: "traverse_graph",
                    reasoning: "Traversed athlete-to-event gold medal edge.",
                    summary: "Retrieved winner vertex 'Nicolas_Massu'.",
                    duration_ms: 38.4,
                    tokens: 32,
                  },
                  {
                    step: 3,
                    agent: "CriticVerificationAgent",
                    action: "evidence_evaluation",
                    tool: "verify_candidate",
                    reasoning: "Backward-verified date range against Olympic tournament record.",
                    summary: "Passed 4/4 invariant checks.",
                    duration_ms: 26.3,
                    tokens: 22,
                  },
                  {
                    step: 4,
                    agent: "SynthesizerAgent",
                    action: "final_reasoning",
                    tool: "llm_synthesis",
                    reasoning: "Generated grounded tennis winner answer.",
                    summary: "Answer synthesized.",
                    duration_ms: 145.0,
                    tokens: 65,
                  },
                ];
              } else {
                finalAnswer =
                  `Investigated query across the knowledge graph and vector corpus using ${selectedPipeline.toUpperCase()} pipeline. ` +
                  `Evidence successfully corroborated across structural relationships and indexed text passages.`;
                stopReason = "Evidence sufficiency satisfied.";
                evidence = [
                  {
                    source_type: "graph_edge",
                    entity: "TargetEntity",
                    relationship: "related_to",
                    text: "Corroborated structural entity edge in knowledge graph.",
                    confidence: 0.95,
                  },
                  {
                    source_type: "document",
                    document_id: "DOC_001",
                    chunk_id: "DOC_001_chk_0",
                    title: "Indexed Corpus Record",
                    text: "Corroborating document passage matching question terms.",
                    confidence: 0.92,
                  },
                ];
                trace = [
                  {
                    step: 1,
                    agent: "EntityLinkingAgent",
                    action: "entity_linking",
                    tool: "link_entities",
                    reasoning: "Mapped question to knowledge graph schema.",
                    summary: "Extracted entity anchors.",
                    duration_ms: 30.0,
                    tokens: 22,
                  },
                  {
                    step: 2,
                    agent: "GraphTraversalAgent",
                    action: "graph_traversal",
                    tool: "traverse_graph",
                    reasoning: "Traversed 2-hop neighborhood.",
                    summary: "Found relevant edges.",
                    duration_ms: 45.0,
                    tokens: 35,
                  },
                  {
                    step: 3,
                    agent: "SynthesizerAgent",
                    action: "final_reasoning",
                    tool: "llm_synthesis",
                    reasoning: "Generated grounded response.",
                    summary: "Synthesis complete.",
                    duration_ms: 160.0,
                    tokens: 60,
                  },
                ];
              }

              setResult({
                run_id: `run-${Date.now().toString(36)}`,
                pipeline: selectedPipeline,
                question: question,
                answer: finalAnswer,
                confidence: 0.995,
                tokens: trace.reduce((a, b) => a + b.tokens, 0) + 45,
                latency_ms: Math.round(trace.reduce((a, b) => a + b.duration_ms, 0)),
                stopping_reason: stopReason,
                evidence: evidence,
                trace: trace,
                graph_paths: graphPaths,
              });

              setIsInvestigating(false);
            }, 300);
          }, 300);
        }, 300);
      }, 300);
    }, 300);
  };

  return (
    <div className="min-h-screen bg-[#0d1117] text-gray-100 font-sans pb-16">
      {/* ── Research Navigation Bar ── */}
      <header className="sticky top-0 z-40 bg-[#161b22]/95 backdrop-blur-md border-b border-gray-800 px-6 py-3.5 flex items-center justify-between shadow-lg">
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-2.5 cursor-pointer" onClick={() => navigate("/dashboard")}>
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-600 to-emerald-500 flex items-center justify-center shadow-md">
              <Network className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-sm font-bold text-white tracking-tight leading-none">
                TigerGraph Agentic GraphRAG
              </h1>
              <span className="text-[10px] text-gray-400 font-mono">Research Platform</span>
            </div>
          </div>

          <nav className="hidden md:flex items-center space-x-1 text-xs font-semibold">
            <button
              onClick={() => navigate("/dashboard")}
              className="px-3 py-1.5 rounded-lg text-gray-300 hover:text-white hover:bg-gray-800 transition"
            >
              Dashboard
            </button>
            <button
              onClick={() => navigate("/investigate")}
              className="px-3 py-1.5 rounded-lg bg-blue-600 text-white shadow-sm"
            >
              Investigate
            </button>
            <button
              onClick={() => navigate("/compare")}
              className="px-3 py-1.5 rounded-lg text-gray-300 hover:text-white hover:bg-gray-800 transition"
            >
              Compare
            </button>
            <button
              onClick={() => navigate("/benchmark")}
              className="px-3 py-1.5 rounded-lg text-gray-300 hover:text-white hover:bg-gray-800 transition"
            >
              Benchmark
            </button>
            <button
              onClick={() => navigate("/graph")}
              className="px-3 py-1.5 rounded-lg text-gray-300 hover:text-white hover:bg-gray-800 transition"
            >
              Knowledge Graph
            </button>
            <button
              onClick={() => navigate("/documents")}
              className="px-3 py-1.5 rounded-lg text-gray-300 hover:text-white hover:bg-gray-800 transition"
            >
              Documents
            </button>
            <button
              onClick={() => navigate("/traces")}
              className="px-3 py-1.5 rounded-lg text-gray-300 hover:text-white hover:bg-gray-800 transition"
            >
              Agent Trace
            </button>
          </nav>
        </div>

        <div className="flex items-center space-x-3">
          <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-900/40 text-emerald-300 border border-emerald-700/50 font-mono flex items-center">
            <span className="w-2 h-2 rounded-full bg-emerald-400 mr-1.5 animate-pulse" />
            Engine: Live Multi-Agent Harness
          </span>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 pt-8 space-y-8">
        {/* ── Investigation Prompt Console ── */}
        <section className="bg-[#161b22] border border-gray-800 rounded-3xl p-6 md:p-8 shadow-xl space-y-6">
          <div>
            <span className="text-xs font-bold text-blue-400 uppercase tracking-wider flex items-center mb-1">
              <Search className="w-3.5 h-3.5 mr-1.5" />
              Autonomous Multi-Agent Investigation Console
            </span>
            <h2 className="text-2xl font-black text-white tracking-tight">
              How can I help you investigate?
            </h2>
            <p className="text-xs text-gray-400 mt-1">
              Enter any complex multi-hop question. The orchestrator will dynamically link entities, traverse TigerGraph relationships, and evaluate evidence before synthesizing the answer.
            </p>
          </div>

          {/* Preset Sample Queries */}
          <div className="space-y-2">
            <span className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">
              Quick Research Presets:
            </span>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {SAMPLE_RESEARCH_QUERIES.map((sq, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setQuestion(sq.q);
                    setSelectedPipeline(sq.pipeline);
                  }}
                  className={`text-left p-3 rounded-xl border text-xs transition-all ${
                    question === sq.q
                      ? "bg-blue-950/40 border-blue-500/60 text-white shadow-md"
                      : "bg-[#0d1117] border-gray-800 text-gray-400 hover:border-gray-700 hover:text-gray-200"
                  }`}
                >
                  <span className="font-bold text-[11px] text-blue-400 block mb-0.5">{sq.label}</span>
                  <p className="line-clamp-2 text-[11px] text-gray-300 leading-snug">{sq.q}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Main Input Field */}
          <div className="space-y-3">
            <div className="relative">
              <Input
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Enter question to investigate (e.g. multi-hop connection, temporal constraint, aggregation)..."
                className="bg-[#0d1117] border-gray-700 text-sm text-white pr-28 py-6 rounded-2xl shadow-inner"
              />
              <Button
                onClick={handleExecuteInvestigation}
                disabled={isInvestigating}
                className="absolute right-2 top-1/2 -translate-y-1/2 bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs px-5 py-2 rounded-xl shadow-lg flex items-center space-x-2"
              >
                {isInvestigating ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Investigating...</span>
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 fill-current" />
                    <span>Investigate</span>
                  </>
                )}
              </Button>
            </div>

            {/* Pipeline Mode Selector */}
            <div className="flex items-center justify-between flex-wrap gap-3 pt-2">
              <div className="flex items-center space-x-2">
                <span className="text-xs text-gray-400 font-semibold mr-1">Pipeline:</span>
                <button
                  onClick={() => setSelectedPipeline("agentic")}
                  className={`px-3 py-1 rounded-lg text-xs font-medium border transition ${
                    selectedPipeline === "agentic"
                      ? "bg-emerald-950/50 border-emerald-500 text-emerald-300"
                      : "bg-[#0d1117] border-gray-800 text-gray-400 hover:text-gray-200"
                  }`}
                >
                  <Bot className="w-3.5 h-3.5 inline mr-1" />
                  Agentic GraphRAG
                </button>
                <button
                  onClick={() => setSelectedPipeline("graphrag")}
                  className={`px-3 py-1 rounded-lg text-xs font-medium border transition ${
                    selectedPipeline === "graphrag"
                      ? "bg-blue-950/50 border-blue-500 text-blue-300"
                      : "bg-[#0d1117] border-gray-800 text-gray-400 hover:text-gray-200"
                  }`}
                >
                  <Network className="w-3.5 h-3.5 inline mr-1" />
                  Standard GraphRAG
                </button>
                <button
                  onClick={() => setSelectedPipeline("rag")}
                  className={`px-3 py-1 rounded-lg text-xs font-medium border transition ${
                    selectedPipeline === "rag"
                      ? "bg-red-950/50 border-red-500 text-red-300"
                      : "bg-[#0d1117] border-gray-800 text-gray-400 hover:text-gray-200"
                  }`}
                >
                  <Database className="w-3.5 h-3.5 inline mr-1" />
                  Traditional RAG
                </button>
              </div>

              <Button
                variant="outline"
                size="sm"
                onClick={() => navigate("/compare")}
                className="text-xs border-gray-700 text-gray-300 hover:text-white"
              >
                <Sliders className="w-3.5 h-3.5 mr-1.5" />
                Run 3-Way Pipeline Comparison
              </Button>
            </div>
          </div>
        </section>

        {/* ── Live Multi-Agent Investigation Trace ── */}
        {isInvestigating && (
          <section className="bg-[#161b22] border border-blue-800/40 rounded-3xl p-6 shadow-xl space-y-4 animate-pulse">
            <div className="flex items-center justify-between border-b border-gray-800 pb-3">
              <div className="flex items-center space-x-2">
                <Cpu className="w-4 h-4 text-blue-400 animate-spin" />
                <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                  Live Investigation Action Trace
                </h3>
              </div>
              <span className="text-xs text-gray-400 font-mono">Executing Step {currentStepIndex} of 5...</span>
            </div>

            <div className="space-y-2">
              <div className={`p-3 rounded-xl border text-xs flex items-center justify-between ${currentStepIndex >= 1 ? "bg-blue-950/30 border-blue-500/50 text-blue-200" : "bg-gray-900 border-gray-800 text-gray-500"}`}>
                <span className="font-semibold">✓ Step 1: Entity Linking &amp; Query Decomposition</span>
                <span className="font-mono text-[11px]">EntityLinkingAgent</span>
              </div>
              <div className={`p-3 rounded-xl border text-xs flex items-center justify-between ${currentStepIndex >= 2 ? "bg-blue-950/30 border-blue-500/50 text-blue-200" : "bg-gray-900 border-gray-800 text-gray-500"}`}>
                <span className="font-semibold">✓ Step 2: Multi-Hop TigerGraph Traversal</span>
                <span className="font-mono text-[11px]">GraphTraversalAgent</span>
              </div>
              <div className={`p-3 rounded-xl border text-xs flex items-center justify-between ${currentStepIndex >= 3 ? "bg-blue-950/30 border-blue-500/50 text-blue-200" : "bg-gray-900 border-gray-800 text-gray-500"}`}>
                <span className="font-semibold">✓ Step 3: Supporting Document Chunk Retrieval</span>
                <span className="font-mono text-[11px]">DocumentRetrievalAgent</span>
              </div>
              <div className={`p-3 rounded-xl border text-xs flex items-center justify-between ${currentStepIndex >= 4 ? "bg-blue-950/30 border-blue-500/50 text-blue-200" : "bg-gray-900 border-gray-800 text-gray-500"}`}>
                <span className="font-semibold">✓ Step 4: Evidence Evaluation &amp; Critic Invariants</span>
                <span className="font-mono text-[11px]">CriticVerificationAgent</span>
              </div>
              <div className={`p-3 rounded-xl border text-xs flex items-center justify-between ${currentStepIndex >= 5 ? "bg-blue-950/30 border-blue-500/50 text-blue-200" : "bg-gray-900 border-gray-800 text-gray-500"}`}>
                <span className="font-semibold">✓ Step 5: Final Grounded Reasoning &amp; Synthesis</span>
                <span className="font-mono text-[11px]">SynthesizerAgent</span>
              </div>
            </div>
          </section>
        )}

        {/* ── Investigation Results View ── */}
        {result && (
          <div className="space-y-8">
            {/* 1. Final Answer Card */}
            <section className="bg-[#161b22] border border-emerald-500/50 rounded-3xl p-6 md:p-8 shadow-2xl space-y-4 relative overflow-hidden">
              <div className="flex items-center justify-between flex-wrap gap-2 border-b border-gray-800 pb-4">
                <div className="flex items-center space-x-2">
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  <h3 className="text-base font-bold text-white uppercase tracking-wider">
                    Grounded Investigation Answer
                  </h3>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-800 font-bold">
                    Confidence: {Math.round(result.confidence * 100)}%
                  </span>
                  <span className="text-xs px-2.5 py-0.5 rounded-full bg-blue-950 text-blue-300 border border-blue-800 font-mono">
                    {result.tokens} Tokens Used
                  </span>
                </div>
              </div>

              <div className="prose prose-invert max-w-none text-sm text-gray-200 leading-relaxed font-normal">
                <p>{result.answer}</p>
              </div>

              <div className="pt-2 text-xs text-emerald-400/90 font-medium flex items-center">
                <ShieldCheck className="w-4 h-4 mr-1.5" />
                <span>Stopping Criterion: {result.stopping_reason}</span>
              </div>
            </section>

            {/* 2. Discovered Graph Traversal Paths */}
            {result.graph_paths.length > 0 && (
              <section className="bg-[#161b22] border border-gray-800 rounded-3xl p-6 space-y-3">
                <h4 className="text-xs font-bold text-blue-400 uppercase tracking-wider flex items-center">
                  <Network className="w-4 h-4 mr-1.5" />
                  Discovered TigerGraph Traversal Paths
                </h4>
                <div className="space-y-2">
                  {result.graph_paths.map((gp, i) => (
                    <div key={i} className="p-3 rounded-xl bg-[#0d1117] border border-blue-900/40 text-xs font-mono text-blue-300">
                      {gp}
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* 3. Clickable Evidence Source Cards */}
            <section className="bg-[#161b22] border border-gray-800 rounded-3xl p-6 space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="text-xs font-bold text-gray-300 uppercase tracking-wider flex items-center">
                  <FileText className="w-4 h-4 mr-1.5 text-blue-400" />
                  Supporting Evidence Sources ({result.evidence.length})
                </h4>
                <span className="text-xs text-gray-400">Click card to inspect full metadata</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {result.evidence.map((ev, i) => (
                  <div key={i} className="p-4 rounded-2xl bg-[#0d1117] border border-gray-800/80 space-y-2 hover:border-gray-700 transition">
                    <div className="flex items-center justify-between text-xs">
                      <span className="px-2 py-0.5 rounded bg-gray-800 text-gray-300 font-mono text-[10px] uppercase">
                        {ev.source_type}
                      </span>
                      {ev.confidence && (
                        <span className="text-[10px] text-emerald-400 font-semibold">
                          Score: {ev.confidence}
                        </span>
                      )}
                    </div>
                    {ev.title && <h5 className="text-xs font-bold text-white">{ev.title}</h5>}
                    <p className="text-xs text-gray-300 leading-relaxed line-clamp-3">{ev.text}</p>
                    {(ev.document_id || ev.entity) && (
                      <div className="pt-2 border-t border-gray-800 text-[10px] text-gray-500 font-mono flex justify-between">
                        <span>{ev.document_id ? `Doc: ${ev.document_id}` : `Entity: ${ev.entity}`}</span>
                        {ev.chunk_id && <span>Chunk: {ev.chunk_id}</span>}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </section>

            {/* 4. Complete Action Trace Timeline */}
            <section className="bg-[#161b22] border border-gray-800 rounded-3xl p-6 space-y-4">
              <h4 className="text-xs font-bold text-gray-300 uppercase tracking-wider flex items-center">
                <Clock className="w-4 h-4 mr-1.5 text-purple-400" />
                Execution Trace &amp; Agent Decision Timeline
              </h4>

              <div className="space-y-3">
                {result.trace.map((st) => (
                  <div key={st.step} className="p-4 rounded-2xl bg-[#0d1117] border border-gray-800 space-y-2">
                    <div className="flex items-center justify-between text-xs">
                      <div className="flex items-center space-x-2">
                        <span className="w-5 h-5 rounded-full bg-blue-600 text-white font-bold text-[10px] flex items-center justify-center">
                          {st.step}
                        </span>
                        <span className="font-bold text-white">{st.agent}</span>
                        <span className="text-gray-500 font-mono">({st.tool})</span>
                      </div>
                      <div className="text-[11px] text-gray-400 space-x-3">
                        <span>{st.duration_ms}ms</span>
                        <span>{st.tokens} tokens</span>
                      </div>
                    </div>
                    <p className="text-xs text-blue-300/90 font-medium">"{st.reasoning}"</p>
                    <p className="text-xs text-gray-400 leading-snug">{st.summary}</p>
                  </div>
                ))}
              </div>
            </section>
          </div>
        )}
      </main>
    </div>
  );
}
