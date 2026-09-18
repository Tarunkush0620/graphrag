import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Network,
  Search,
  Plus,
  Layers,
  ChevronRight,
  Database,
  ArrowRight,
  FileText,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface GraphNode {
  id: string;
  name: string;
  type: string;
  attributes: Record<string, any>;
}

interface GraphEdge {
  from: string;
  to: string;
  type: string;
  attributes: Record<string, any>;
}

const SAMPLE_NODES: GraphNode[] = [
  { id: "Person_A", name: "Person A", type: "Person", attributes: { role: "Founder", stake: "60%" } },
  { id: "Alpha_Holdings", name: "Alpha Holdings", type: "Organization", attributes: { founded_year: 2017, industry: "Technology" } },
  { id: "Beta_Ventures", name: "Beta Ventures", type: "Organization", attributes: { founded_year: 2016, industry: "Venture Capital" } },
  { id: "Company_B", name: "Company B", type: "Company", attributes: { founded_year: 2019, industry: "AI" } },
  { id: "Nicolas_Massu", name: "Nicolás Massú", type: "Athlete", attributes: { country: "Chile", sport: "Tennis" } },
  { id: "Tennis_Athens_2004", name: "Tennis Athens 2004", type: "Event", attributes: { venue: "Olympic Tennis Centre", dates: "15-22 Aug 2004" } },
];

const SAMPLE_EDGES: GraphEdge[] = [
  { from: "Person_A", to: "Alpha_Holdings", type: "founded", attributes: { year: 2017 } },
  { from: "Alpha_Holdings", to: "Beta_Ventures", type: "partnered_with", attributes: { since: 2018 } },
  { from: "Beta_Ventures", to: "Company_B", type: "invested_in", attributes: { round: "Series A", year: 2020 } },
  { from: "Nicolas_Massu", to: "Tennis_Athens_2004", type: "won_gold_in", attributes: { medal: "Gold", event: "Men's Singles" } },
];

export default function KnowledgeGraph() {
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(SAMPLE_NODES[0]);

  const filteredNodes = SAMPLE_NODES.filter((n) =>
    n.name.toLowerCase().includes(search.toLowerCase()) || n.type.toLowerCase().includes(search.toLowerCase())
  );

  const connectedEdges = SAMPLE_EDGES.filter(
    (e) => selectedNode && (e.from === selectedNode.id || e.to === selectedNode.id)
  );

  return (
    <div className="min-h-screen bg-[#0d1117] text-gray-100 font-sans pb-16">
      {/* ── Navigation Bar ── */}
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
              <span className="text-[10px] text-gray-400 font-mono">Knowledge Graph Explorer</span>
            </div>
          </div>

          <nav className="hidden md:flex items-center space-x-1 text-xs font-semibold">
            <button onClick={() => navigate("/dashboard")} className="px-3 py-1.5 rounded-lg text-gray-300 hover:text-white hover:bg-gray-800 transition">
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
            <button onClick={() => navigate("/graph")} className="px-3 py-1.5 rounded-lg bg-blue-600 text-white shadow-sm">
              Knowledge Graph
            </button>
            <button onClick={() => navigate("/documents")} className="px-3 py-1.5 rounded-lg text-gray-300 hover:text-white hover:bg-gray-800 transition">
              Documents
            </button>
          </nav>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 pt-8 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-white">TigerGraph Knowledge Graph Schema &amp; Entities</h2>
            <p className="text-xs text-gray-400">Inspect graph vertices, multi-hop relationship paths, and linked document evidence.</p>
          </div>
          <span className="text-xs px-3 py-1 rounded-full bg-blue-900/40 text-blue-300 border border-blue-700/50 font-mono">
            Graph: olympic_qa_graph ({SAMPLE_NODES.length} Vertices, {SAMPLE_EDGES.length} Edges)
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Entity List & Search */}
          <div className="bg-[#161b22] border border-gray-800 rounded-2xl p-5 space-y-4">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <Input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search vertices..."
                className="pl-9 bg-[#0d1117] border-gray-700 text-xs text-white"
              />
            </div>

            <div className="space-y-2 max-h-[450px] overflow-y-auto pr-1">
              {filteredNodes.map((node) => (
                <div
                  key={node.id}
                  onClick={() => setSelectedNode(node)}
                  className={`p-3 rounded-xl border text-xs cursor-pointer transition flex items-center justify-between ${
                    selectedNode?.id === node.id
                      ? "bg-blue-950/50 border-blue-500 text-white"
                      : "bg-[#0d1117] border-gray-800 text-gray-300 hover:border-gray-700"
                  }`}
                >
                  <div>
                    <span className="font-bold block">{node.name}</span>
                    <span className="text-[10px] text-gray-400 font-mono">{node.type}</span>
                  </div>
                  <ChevronRight className="w-4 h-4 text-gray-500" />
                </div>
              ))}
            </div>
          </div>

          {/* Node Inspector & Multi-Hop Path Visualizer */}
          <div className="lg:col-span-2 space-y-6">
            {selectedNode && (
              <div className="bg-[#161b22] border border-gray-800 rounded-2xl p-6 space-y-6 shadow-xl">
                <div>
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="px-2 py-0.5 rounded bg-blue-900/50 text-blue-300 font-mono text-[10px] uppercase">
                      {selectedNode.type}
                    </span>
                    <h3 className="text-lg font-bold text-white">{selectedNode.name}</h3>
                  </div>
                  <span className="text-xs text-gray-400 font-mono">Vertex ID: {selectedNode.id}</span>
                </div>

                {/* Attributes */}
                <div className="space-y-2">
                  <span className="text-xs font-bold text-gray-300 uppercase tracking-wider">Vertex Attributes:</span>
                  <div className="grid grid-cols-2 gap-2">
                    {Object.entries(selectedNode.attributes).map(([k, v]) => (
                      <div key={k} className="p-3 rounded-xl bg-[#0d1117] border border-gray-800/80 text-xs">
                        <span className="text-gray-400 block text-[10px] uppercase">{k}</span>
                        <span className="font-semibold text-white">{String(v)}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Connected Relationships */}
                <div className="space-y-2">
                  <span className="text-xs font-bold text-gray-300 uppercase tracking-wider">
                    Connected Relationships ({connectedEdges.length}):
                  </span>
                  <div className="space-y-2">
                    {connectedEdges.map((edge, i) => (
                      <div key={i} className="p-3 rounded-xl bg-[#0d1117] border border-blue-900/40 text-xs font-mono text-blue-200 flex items-center justify-between">
                        <span>
                          <strong>{edge.from}</strong> --[{edge.type}]--&gt; <strong>{edge.to}</strong>
                        </span>
                        <span className="text-[10px] text-gray-500">Attributes: {JSON.stringify(edge.attributes)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
