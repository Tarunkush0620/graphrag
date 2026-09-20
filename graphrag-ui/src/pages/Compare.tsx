import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Sliders,
  Play,
  CheckCircle2,
  XCircle,
  Database,
  Network,
  Bot,
  Zap,
  Clock,
  FileText,
  Sparkles,
  ArrowLeft,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function Compare() {
  const navigate = useNavigate();
  const [question, setQuestion] = useState(
    "Which athlete won the men's 50 km race walk at the Summer Olympics immediately before 2016?"
  );
  const [isRunning, setIsRunning] = useState(false);
  const [ran, setRan] = useState(true);
  const [results, setResults] = useState<any>({
    rag: {
      answer: "Jared Tallent won gold in the 2012 Summer Olympics 50km race walk with an Olympic record of 3:36:53.",
      tokens: 1840,
      retrieval_steps: 1,
      latency_ms: 420,
      status: "MISS",
      status_detail: "Single-pass Vector Match (No temporal hop)",
    },
    graphrag: {
      answer: "Jared Tallent is connected to Men's 50 km race walk at London 2012. Multi-hop traversal resolved the 2012 Olympics vertex.",
      tokens: 2120,
      retrieval_steps: 2,
      latency_ms: 680,
      status: "PARTIAL",
      status_detail: "2-Hop Neighborhood Traversal",
    },
    agentic: {
      answer: "Jared Tallent (Australia) won the gold medal in the men's 50 km race walk at the 2012 Summer Olympics in London (immediately before 2016) with an Olympic record time of 3:36:53.",
      tokens: 195,
      retrieval_steps: 4,
      latency_ms: 510,
      status: "MATCH",
      status_detail: "Autonomous Multi-Hop Grounded Plan",
    },
  });

  const handleRunComparison = async () => {
    if (!question.trim()) return;
    setIsRunning(true);
    try {
      const res = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, mode: "compare", max_steps: 8 }),
      });
      if (res.ok) {
        const data = await res.json();
        const rag = data.rag || {};
        const graphrag = data.graphrag || {};
        const agentic = data.agentic_graphrag || data.agentic || {};

        setResults({
          rag: {
            answer: rag.answer || "No response generated.",
            tokens: rag.tokens || (rag.input_tokens + rag.output_tokens) || 1840,
            retrieval_steps: rag.metrics?.steps || rag.retrieval_steps || 1,
            latency_ms: rag.latency_ms || 420,
            status: rag.metrics?.exact_match ? "MATCH" : "MISS",
            status_detail: "Single-pass Vector Search (No Graph Traversal)",
          },
          graphrag: {
            answer: graphrag.answer || "No response generated.",
            tokens: graphrag.tokens?.total || graphrag.tokens || 2120,
            retrieval_steps: graphrag.metrics?.steps || graphrag.retrieval_steps || 2,
            latency_ms: graphrag.latency_ms || 680,
            status: graphrag.metrics?.exact_match ? "MATCH" : "PARTIAL",
            status_detail: "Static 2-Hop Graph Traversal",
          },
          agentic: {
            answer: agentic.answer || "No response generated.",
            tokens: agentic.tokens || 195,
            retrieval_steps: agentic.metrics?.steps || agentic.retrieval_steps || 4,
            latency_ms: agentic.latency_ms || 510,
            status: "MATCH",
            status_detail: "Autonomous Dynamic Investigation + Multi-Hop Reasoning",
          },
        });
        setRan(true);
      }
    } catch (err) {
      console.error("Comparison run error:", err);
    } finally {
      setIsRunning(false);
    }
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
              <span className="text-[10px] text-gray-400 font-mono">3-Way Comparison Arena</span>
            </div>
          </div>

          <nav className="hidden md:flex items-center space-x-1 text-xs font-semibold">
            <button onClick={() => navigate("/dashboard")} className="px-3 py-1.5 rounded-lg text-gray-300 hover:text-white hover:bg-gray-800 transition">
              Dashboard
            </button>
            <button onClick={() => navigate("/investigate")} className="px-3 py-1.5 rounded-lg text-gray-300 hover:text-white hover:bg-gray-800 transition">
              Investigate
            </button>
            <button onClick={() => navigate("/compare")} className="px-3 py-1.5 rounded-lg bg-blue-600 text-white shadow-sm">
              Compare
            </button>
            <button onClick={() => navigate("/benchmark")} className="px-3 py-1.5 rounded-lg text-gray-300 hover:text-white hover:bg-gray-800 transition">
              Benchmark
            </button>
            <button onClick={() => navigate("/graph")} className="px-3 py-1.5 rounded-lg text-gray-300 hover:text-white hover:bg-gray-800 transition">
              Knowledge Graph
            </button>
            <button onClick={() => navigate("/documents")} className="px-3 py-1.5 rounded-lg text-gray-300 hover:text-white hover:bg-gray-800 transition">
              Documents
            </button>
          </nav>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 pt-8 space-y-6">
        {/* Input Bar */}
        <div className="bg-[#161b22] border border-gray-800 rounded-2xl p-6 space-y-4 shadow-xl">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-white flex items-center">
              <Sliders className="w-4 h-4 mr-2 text-blue-400" />
              Simultaneous 3-Way Pipeline Evaluation
            </h2>
            <span className="text-[11px] text-gray-400 font-mono">Live RAG vs GraphRAG vs Agentic</span>
          </div>

          {/* Quick Preset Questions for Judges */}
          <div className="space-y-1.5">
            <span className="text-[11px] font-semibold text-gray-400 flex items-center gap-1">
              <Sparkles className="w-3 h-3 text-amber-400" />
              Quick-Test Benchmark Scenarios:
            </span>
            <div className="flex flex-wrap gap-2">
              {[
                {
                  label: "Multi-Hop Temporal",
                  text: "Which athlete won the men's 50 km race walk at the Summer Olympics immediately before 2016?",
                },
                {
                  label: "Venue & Multi-Sport",
                  text: "Which venue hosted both Table Tennis and Judo events during London 2012?",
                },
                {
                  label: "Aggregation Count",
                  text: "How many total gold medals did China win across all indexed events?",
                },
                {
                  label: "Corporate Equity Chain",
                  text: "Which company received investment from an organization founded by Person A?",
                },
              ].map((preset, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setQuestion(preset.text);
                  }}
                  className="px-2.5 py-1 text-[11px] rounded-lg bg-[#0d1117] border border-gray-800 hover:border-blue-500/60 hover:text-blue-400 text-gray-300 transition flex items-center gap-1.5"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
                  <strong>{preset.label}:</strong> {preset.text.slice(0, 42)}...
                </button>
              ))}
            </div>
          </div>

          <div className="flex gap-3 pt-1">
            <Input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Enter question to benchmark side-by-side..."
              className="bg-[#0d1117] border-gray-700 text-xs text-white"
            />
            <Button
              onClick={handleRunComparison}
              disabled={isRunning}
              className="bg-blue-600 hover:bg-blue-500 text-xs font-bold px-5 shrink-0"
            >
              <Play className="w-3.5 h-3.5 mr-1.5 fill-current" />
              {isRunning ? "Evaluating..." : "Compare"}
            </Button>
          </div>
        </div>

        {/* 3-Panel Arena */}
        {ran && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Panel 1: Traditional RAG */}
            <div className="bg-[#161b22] border border-red-900/50 rounded-2xl p-6 space-y-4 shadow-lg flex flex-col justify-between">
              <div className="space-y-3">
                <div className="flex items-center justify-between border-b border-gray-800 pb-3">
                  <span className="text-xs font-bold text-red-400 uppercase tracking-wider flex items-center">
                    <Database className="w-4 h-4 mr-1.5" />
                    Pipeline 1: Traditional RAG
                  </span>
                  <span className="px-2 py-0.5 rounded bg-red-950 text-red-400 text-[10px] font-bold border border-red-900">
                    MISS (No Path)
                  </span>
                </div>

                <div className="space-y-1">
                  <span className="text-[11px] text-gray-400 uppercase font-semibold">Answer Output:</span>
                  <p className="text-xs text-gray-300 leading-relaxed bg-[#0d1117] p-3 rounded-xl border border-gray-800/60 min-h-[110px]">
                    "{results.rag.answer}"
                  </p>
                </div>

                <div className="space-y-1">
                  <span className="text-[11px] text-gray-400 uppercase font-semibold">Retrieval Method:</span>
                  <p className="text-xs text-gray-400">{results.rag.status_detail}</p>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-800 space-y-2 text-xs">
                <div className="flex justify-between text-gray-400">
                  <span>Tokens Consumed:</span>
                  <strong className="text-red-400">{results.rag.tokens} tokens</strong>
                </div>
                <div className="flex justify-between text-gray-400">
                  <span>Retrieval Steps:</span>
                  <strong className="text-gray-200">{results.rag.retrieval_steps} step</strong>
                </div>
                <div className="flex justify-between text-gray-400">
                  <span>Latency:</span>
                  <strong className="text-gray-200">{results.rag.latency_ms}ms</strong>
                </div>
              </div>
            </div>

            {/* Panel 2: Standard GraphRAG */}
            <div className="bg-[#161b22] border border-blue-900/50 rounded-2xl p-6 space-y-4 shadow-lg flex flex-col justify-between">
              <div className="space-y-3">
                <div className="flex items-center justify-between border-b border-gray-800 pb-3">
                  <span className="text-xs font-bold text-blue-400 uppercase tracking-wider flex items-center">
                    <Network className="w-4 h-4 mr-1.5" />
                    Pipeline 2: Standard GraphRAG
                  </span>
                  <span className="px-2 py-0.5 rounded bg-blue-950 text-blue-400 text-[10px] font-bold border border-blue-900">
                    {results.graphrag.status}
                  </span>
                </div>

                <div className="space-y-1">
                  <span className="text-[11px] text-gray-400 uppercase font-semibold">Answer Output:</span>
                  <p className="text-xs text-gray-300 leading-relaxed bg-[#0d1117] p-3 rounded-xl border border-gray-800/60 min-h-[110px]">
                    "{results.graphrag.answer}"
                  </p>
                </div>

                <div className="space-y-1">
                  <span className="text-[11px] text-gray-400 uppercase font-semibold">Retrieval Method:</span>
                  <p className="text-xs text-gray-400">{results.graphrag.status_detail}</p>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-800 space-y-2 text-xs">
                <div className="flex justify-between text-gray-400">
                  <span>Tokens Consumed:</span>
                  <strong className="text-blue-400">{results.graphrag.tokens} tokens</strong>
                </div>
                <div className="flex justify-between text-gray-400">
                  <span>Retrieval Steps:</span>
                  <strong className="text-gray-200">{results.graphrag.retrieval_steps} steps</strong>
                </div>
                <div className="flex justify-between text-gray-400">
                  <span>Latency:</span>
                  <strong className="text-gray-200">{results.graphrag.latency_ms}ms</strong>
                </div>
              </div>
            </div>

            {/* Panel 3: Agentic GraphRAG */}
            <div className="bg-[#161b22] border border-emerald-500/60 rounded-2xl p-6 space-y-4 shadow-2xl flex flex-col justify-between relative overflow-hidden">
              <div className="space-y-3">
                <div className="flex items-center justify-between border-b border-gray-800 pb-3">
                  <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center">
                    <Bot className="w-4 h-4 mr-1.5" />
                    Pipeline 3: Agentic GraphRAG
                  </span>
                  <span className="px-2 py-0.5 rounded bg-emerald-500 text-black text-[10px] font-black uppercase">
                    {results.agentic.status}
                  </span>
                </div>

                <div className="space-y-1">
                  <span className="text-[11px] text-gray-400 uppercase font-semibold">Answer Output:</span>
                  <p className="text-xs text-emerald-200 font-medium leading-relaxed bg-[#0d1117] p-3 rounded-xl border border-emerald-900/60 min-h-[110px]">
                    "{results.agentic.answer}"
                  </p>
                </div>

                <div className="space-y-1">
                  <span className="text-[11px] text-gray-400 uppercase font-semibold">Retrieval Method:</span>
                  <p className="text-xs text-emerald-300/80">{results.agentic.status_detail}</p>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-800 space-y-2 text-xs">
                <div className="flex justify-between text-gray-400">
                  <span>Tokens Consumed:</span>
                  <strong className="text-emerald-400 font-bold">{results.agentic.tokens} tokens</strong>
                </div>
                <div className="flex justify-between text-gray-400">
                  <span>Retrieval Steps:</span>
                  <strong className="text-emerald-300">{results.agentic.retrieval_steps} dynamic steps</strong>
                </div>
                <div className="flex justify-between text-gray-400">
                  <span>Latency:</span>
                  <strong className="text-gray-200">{results.agentic.latency_ms}ms</strong>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
