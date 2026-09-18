import React from "react";
import { useNavigate } from "react-router-dom";
import {
  Network,
  Zap,
  BarChart3,
  Search,
  CheckCircle2,
  Sliders,
  FileText,
  Clock,
  Layers,
  ShieldCheck,
  Sparkles,
  ArrowRight,
  Database,
  Cpu,
} from "lucide-react";
import { Button } from "@/components/ui/button";

export default function Dashboard() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[#0d1117] text-gray-100 font-sans pb-16">
      {/* ── Top Navigation Bar ── */}
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
              <span className="text-[10px] text-gray-400 font-mono">Executive Research Dashboard</span>
            </div>
          </div>

          <nav className="hidden md:flex items-center space-x-1 text-xs font-semibold">
            <button onClick={() => navigate("/dashboard")} className="px-3 py-1.5 rounded-lg bg-blue-600 text-white shadow-sm">
              Dashboard
            </button>
            <button onClick={() => navigate("/investigate")} className="px-3 py-1.5 rounded-lg text-gray-300 hover:text-white hover:bg-gray-800 transition">
              Investigate
            </button>
            <button onClick={() => navigate("/compare")} className="px-3 py-1.5 rounded-lg text-gray-300 hover:text-white hover:bg-gray-800 transition">
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

        <div className="flex items-center space-x-3">
          <Button
            size="sm"
            onClick={() => navigate("/investigate")}
            className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold px-3.5 py-1.5 rounded-xl shadow-md flex items-center"
          >
            <Sparkles className="w-3.5 h-3.5 mr-1.5" />
            Start Investigation
          </Button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 pt-8 space-y-8">
        {/* Hero Banner */}
        <section className="bg-gradient-to-r from-blue-950/60 via-indigo-950/40 to-[#161b22] border border-blue-800/40 rounded-3xl p-6 md:p-8 shadow-2xl relative overflow-hidden">
          <div className="space-y-3 max-w-3xl">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-500/20 text-blue-300 text-xs font-semibold border border-blue-400/30">
              <Zap className="w-3.5 h-3.5" />
              <span>TigerGraph Hackathon Research Core</span>
            </div>
            <h2 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
              When Does Agentic Reasoning Outperform RAG &amp; GraphRAG?
            </h2>
            <p className="text-xs md:text-sm text-gray-300 leading-relaxed">
              Agentic GraphRAG achieves <strong>96.0% accuracy</strong> with a <strong>9.5× token reduction</strong> on multi-hop and temporal reasoning queries by dynamically planning multi-step graph traversals instead of dumping monolithic subgraphs.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-6">
            <div className="bg-[#0d1117]/80 border border-red-900/40 rounded-2xl p-4 text-center">
              <span className="text-xs text-red-400 font-semibold block uppercase">Standard RAG</span>
              <span className="text-2xl font-bold text-white mt-1 block">50.0%</span>
              <span className="text-[11px] text-gray-400">Exact Match (1,240 tokens avg)</span>
            </div>
            <div className="bg-[#0d1117]/80 border border-blue-900/40 rounded-2xl p-4 text-center">
              <span className="text-xs text-blue-400 font-semibold block uppercase">Standard GraphRAG</span>
              <span className="text-2xl font-bold text-white mt-1 block">58.0%</span>
              <span className="text-[11px] text-gray-400">Exact Match (1,948 tokens avg)</span>
            </div>
            <div className="bg-[#0d1117]/80 border border-emerald-500/50 rounded-2xl p-4 text-center shadow-lg">
              <span className="text-xs text-emerald-400 font-semibold block uppercase">Agentic GraphRAG</span>
              <span className="text-2xl font-bold text-emerald-300 mt-1 block">96.0% (+62% Lift)</span>
              <span className="text-[11px] text-emerald-400/80">205 tokens (9.5× less cost)</span>
            </div>
          </div>
        </section>

        {/* Quick Action Hub */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div
            onClick={() => navigate("/investigate")}
            className="bg-[#161b22] border border-gray-800 rounded-2xl p-6 space-y-3 cursor-pointer hover:border-blue-500 transition shadow-md"
          >
            <div className="w-10 h-10 rounded-xl bg-blue-950 flex items-center justify-center border border-blue-800 text-blue-400">
              <Search className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white">Investigate Console</h3>
            <p className="text-xs text-gray-400 leading-relaxed">
              Execute live multi-agent investigations on custom multi-hop queries with live step-by-step action traces and citations.
            </p>
            <div className="pt-2 text-xs font-semibold text-blue-400 flex items-center">
              <span>Launch Investigator</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </div>
          </div>

          <div
            onClick={() => navigate("/compare")}
            className="bg-[#161b22] border border-gray-800 rounded-2xl p-6 space-y-3 cursor-pointer hover:border-purple-500 transition shadow-md"
          >
            <div className="w-10 h-10 rounded-xl bg-purple-950 flex items-center justify-center border border-purple-800 text-purple-400">
              <Sliders className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white">3-Way Pipeline Compare</h3>
            <p className="text-xs text-gray-400 leading-relaxed">
              Compare Traditional RAG, Standard GraphRAG, and Agentic GraphRAG simultaneously side-by-side on identical queries.
            </p>
            <div className="pt-2 text-xs font-semibold text-purple-400 flex items-center">
              <span>Open 3-Way Arena</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </div>
          </div>

          <div
            onClick={() => navigate("/benchmark")}
            className="bg-[#161b22] border border-gray-800 rounded-2xl p-6 space-y-3 cursor-pointer hover:border-emerald-500 transition shadow-md"
          >
            <div className="w-10 h-10 rounded-xl bg-emerald-950 flex items-center justify-center border border-emerald-800 text-emerald-400">
              <BarChart3 className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white">Benchmark Suite</h3>
            <p className="text-xs text-gray-400 leading-relaxed">
              Explore the 100-question comparative evaluation, token efficiency scatter plots, radar charts, and decision matrix.
            </p>
            <div className="pt-2 text-xs font-semibold text-emerald-400 flex items-center">
              <span>View Benchmark</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </div>
          </div>
        </section>

        {/* Complexity Breakdown */}
        <section className="bg-[#161b22] border border-gray-800 rounded-3xl p-6 space-y-4">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">
            Performance Breakdown by Question Complexity
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 rounded-2xl bg-[#0d1117] border border-gray-800 space-y-2">
              <span className="text-xs font-bold text-emerald-400 uppercase block">Simple Lookups (1-Hop)</span>
              <p className="text-xs text-gray-300">Standard GraphRAG &amp; RAG are sufficient (80-100% accuracy) with zero agent overhead.</p>
              <span className="text-[11px] text-gray-500 block font-mono">Recommended: Standard GraphRAG</span>
            </div>
            <div className="p-4 rounded-2xl bg-[#0d1117] border border-gray-800 space-y-2">
              <span className="text-xs font-bold text-blue-400 uppercase block">Medium (Aggregations)</span>
              <p className="text-xs text-gray-300">Deterministic GSQL queries execute sum/count in &lt;10ms, matching agent reasoning (96%).</p>
              <span className="text-[11px] text-gray-500 block font-mono">Recommended: Standard GraphRAG</span>
            </div>
            <div className="p-4 rounded-2xl bg-[#0d1117] border border-emerald-500/40 space-y-2">
              <span className="text-xs font-bold text-emerald-300 uppercase block">Complex (Multi-Hop / Temporal)</span>
              <p className="text-xs text-emerald-100 font-medium">Agentic reasoning is essential (+96% vs 48%), dynamically linking disjoint paths.</p>
              <span className="text-[11px] text-emerald-400 block font-mono">Recommended: Agentic GraphRAG</span>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
