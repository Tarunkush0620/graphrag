import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  FileText,
  Search,
  ExternalLink,
  Layers,
  Database,
  Calendar,
  Tag,
  Network,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const SAMPLE_DOCS = [
  {
    doc_id: "DOC_CORP_001",
    title: "Alpha Holdings & Company B Ownership Investigation",
    source: "Corporate Filings & Registry 2021",
    timestamp: "2021-04-10",
    entities: ["Person A", "Alpha Holdings", "Beta Ventures", "Company B"],
    chunks: [
      "Alpha Holdings was founded in 2017 by Person A, who holds a majority controlling stake.",
      "In 2018, Alpha Holdings established an official co-investment partnership with Beta Ventures (founded 2016).",
      "In March 2020, Beta Ventures led the Series A financing round into Company B, establishing direct corporate affiliation.",
    ],
  },
  {
    doc_id: "DOC_OLY_2004_TENNIS",
    title: "Athens 2004 Tennis Tournament Results",
    source: "Official Olympic Report 2004",
    timestamp: "2004-08-25",
    entities: ["Nicolás Massú", "Olympic Tennis Centre", "Athens 2004"],
    chunks: [
      "The tennis tournament at the 2004 Summer Olympics was held at the Olympic Tennis Centre in Athens from 15 to 22 August 2004.",
      "In the Men's Singles final on 22 August 2004, Nicolás Massú of Chile defeated Mardy Fish to win the gold medal.",
    ],
  },
  {
    doc_id: "DOC_OLY_2008_FENCING",
    title: "Beijing 2008 Fencing Overview",
    source: "Beijing 2008 Official Games Record",
    timestamp: "2008-08-18",
    entities: ["Fencing at the 2008 Summer Olympics – Men's épée", "Beijing 2008"],
    chunks: [
      "Fencing at the 2008 Summer Olympics featured 10 distinct events.",
      "The Men's épée competition had the highest number of competitors among all fencing disciplines, with 41 fencers.",
    ],
  },
  {
    doc_id: "DOC_OLY_2008_CHINA",
    title: "China Medal Table Summary 2008",
    source: "Olympic Medal Table Beijing 2008",
    timestamp: "2008-08-24",
    entities: ["China", "Beijing 2008"],
    chunks: [
      "Host nation China achieved a total of 100 medals at the 2008 Beijing Summer Olympic Games.",
      "Consisting of 51 gold medals, 21 silver medals, and 28 bronze medals, topping the gold medal standings.",
    ],
  },
];

export default function Documents() {
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const [selectedDoc, setSelectedDoc] = useState(SAMPLE_DOCS[0]);

  const filteredDocs = SAMPLE_DOCS.filter(
    (d) =>
      d.title.toLowerCase().includes(search.toLowerCase()) ||
      d.doc_id.toLowerCase().includes(search.toLowerCase()) ||
      d.entities.some((e) => e.toLowerCase().includes(search.toLowerCase()))
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
              <span className="text-[10px] text-gray-400 font-mono">Corpus Document Explorer</span>
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
            <button onClick={() => navigate("/graph")} className="px-3 py-1.5 rounded-lg text-gray-300 hover:text-white hover:bg-gray-800 transition">
              Knowledge Graph
            </button>
            <button onClick={() => navigate("/documents")} className="px-3 py-1.5 rounded-lg bg-blue-600 text-white shadow-sm">
              Documents
            </button>
          </nav>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 pt-8 space-y-6">
        <div>
          <h2 className="text-xl font-bold text-white">Indexed Corpus Documents &amp; Chunk Viewer</h2>
          <p className="text-xs text-gray-400">Search and inspect raw text chunks, extracted metadata, and entity anchors.</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Document List */}
          <div className="bg-[#161b22] border border-gray-800 rounded-2xl p-5 space-y-4">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <Input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search documents..."
                className="pl-9 bg-[#0d1117] border-gray-700 text-xs text-white"
              />
            </div>

            <div className="space-y-2 max-h-[500px] overflow-y-auto pr-1">
              {filteredDocs.map((doc) => (
                <div
                  key={doc.doc_id}
                  onClick={() => setSelectedDoc(doc)}
                  className={`p-3.5 rounded-xl border text-xs cursor-pointer transition ${
                    selectedDoc?.doc_id === doc.doc_id
                      ? "bg-blue-950/50 border-blue-500 text-white shadow-md"
                      : "bg-[#0d1117] border-gray-800 text-gray-300 hover:border-gray-700"
                  }`}
                >
                  <span className="font-bold text-white block mb-1">{doc.title}</span>
                  <span className="text-[10px] text-gray-500 font-mono block">{doc.doc_id} · {doc.source}</span>
                  <div className="flex flex-wrap gap-1 mt-2">
                    {doc.entities.slice(0, 2).map((e) => (
                      <span key={e} className="px-1.5 py-0.5 rounded bg-gray-800 text-gray-400 text-[10px]">
                        {e}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Chunks & Metadata Viewer */}
          <div className="lg:col-span-2 space-y-6">
            {selectedDoc && (
              <div className="bg-[#161b22] border border-gray-800 rounded-2xl p-6 space-y-6 shadow-xl">
                <div>
                  <h3 className="text-lg font-bold text-white">{selectedDoc.title}</h3>
                  <div className="flex items-center space-x-4 text-xs text-gray-400 mt-1">
                    <span>Doc ID: <strong className="text-gray-200 font-mono">{selectedDoc.doc_id}</strong></span>
                    <span>Source: <strong className="text-gray-200">{selectedDoc.source}</strong></span>
                    <span>Date: <strong className="text-gray-200">{selectedDoc.timestamp}</strong></span>
                  </div>
                </div>

                {/* Extracted Entities */}
                <div className="space-y-2">
                  <span className="text-xs font-bold text-gray-300 uppercase tracking-wider">Extracted Entity Anchors:</span>
                  <div className="flex flex-wrap gap-2">
                    {selectedDoc.entities.map((e) => (
                      <span key={e} className="px-2.5 py-1 rounded-lg bg-blue-950/60 border border-blue-800 text-blue-300 text-xs font-medium">
                        {e}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Chunks */}
                <div className="space-y-3">
                  <span className="text-xs font-bold text-gray-300 uppercase tracking-wider">
                    Indexed Text Chunks ({selectedDoc.chunks.length}):
                  </span>
                  <div className="space-y-3">
                    {selectedDoc.chunks.map((chunk, i) => (
                      <div key={i} className="p-4 rounded-xl bg-[#0d1117] border border-gray-800/80 space-y-1">
                        <span className="text-[10px] font-mono text-gray-500 uppercase">
                          Chunk #{i + 1} · {selectedDoc.doc_id}_chk_{i}
                        </span>
                        <p className="text-xs text-gray-200 leading-relaxed">{chunk}</p>
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
