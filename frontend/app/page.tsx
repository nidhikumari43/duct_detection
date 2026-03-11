"use client";

import { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface Duct {
  id: number;
  dimension: string;
  pressure: string;
  coords: { cx: number; cy: number; r: number };
  description: string;
  duct_box?: number[][];
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [processedData, setProcessedData] = useState<{ image: string, ducts: Duct[] } | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedDuct, setSelectedDuct] = useState<Duct | null>(null);
  const [hoveredDuct, setHoveredDuct] = useState<Duct | null>(null);
  const viewportRef = useRef<HTMLDivElement>(null);

  const scrollToDuct = (duct: Duct) => {
    setSelectedDuct(duct);
    if (viewportRef.current) {
      const x = duct.coords.cx - viewportRef.current.clientWidth / 2;
      const y = duct.coords.cy - viewportRef.current.clientHeight / 2;
      viewportRef.current.scrollTo({
        left: Math.max(0, x),
        top: Math.max(0, y),
        behavior: "smooth"
      });
    }
  };

  const startDemo = async () => {
    setLoading(true);
    await new Promise(r => setTimeout(r, 1200)); // Simulate AI processing
    try {
      const response = await fetch("http://localhost:8001/processed/duct_data.json");
      const data = await response.json();
      setProcessedData({ image: "http://localhost:8001/processed/annotated.png", ducts: data.ducts });
    } catch (e) {
      setProcessedData({ image: "/annotated.png", ducts: [] });
    }
    setLoading(false);
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8001/upload", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      setProcessedData(data);
    } catch (error) {
      console.error("Error uploading:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-[#020617] text-slate-200 p-6 lg:p-12 font-sans selection:bg-blue-500/30">
      <div className="max-w-[1600px] mx-auto space-y-12">
        {/* Header - Premium Animated Gradient */}
        <motion.section
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center space-y-6"
        >
          <h1 className="text-6xl font-black tracking-tight bg-gradient-to-b from-white to-slate-500 bg-clip-text text-transparent">
            DuctSense AI
          </h1>
          <p className="text-slate-400 text-xl font-medium max-w-2xl mx-auto leading-relaxed">
            Intelligent ductwork detection & pressure class analysis for mechanical floor plans.
          </p>
        </motion.section>

        {!processedData ? (
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className={`max-w-xl mx-auto p-1 rounded-[2.5rem] bg-gradient-to-br from-blue-500/20 via-transparent to-purple-500/20`}
          >
            <div className="bg-slate-900/90 backdrop-blur-3xl p-12 rounded-[2.4rem] border border-slate-800 space-y-8">
              <form onSubmit={handleUpload} className="space-y-8 text-center">
                <div
                  className="relative group cursor-pointer"
                  onClick={() => document.getElementById('file-upload')?.click()}
                >
                  <input type="file" id="file-upload" className="hidden" onChange={(e) => setFile(e.target.files?.[0] || null)} />
                  <div className="p-10 border-2 border-dashed border-slate-700/50 rounded-3xl group-hover:border-blue-500/50 transition-all bg-slate-800/20 group-hover:bg-slate-800/40">
                    <div className="text-5xl mb-4 group-hover:scale-110 transition-transform duration-300">📁</div>
                    <div className="font-bold text-lg text-slate-300 whitespace-nowrap overflow-hidden text-ellipsis">
                      {file ? file.name : "Drop drawing file here"}
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <button
                    type="submit"
                    disabled={!file || loading}
                    className="w-full py-5 bg-blue-600 hover:bg-blue-500 text-white rounded-2xl font-bold text-lg shadow-xl shadow-blue-500/20 transition-all active:scale-95 disabled:opacity-50"
                  >
                    {loading ? "Analyzing Geometry..." : "Start Analysis"}
                  </button>
                  <button
                    type="button"
                    onClick={startDemo}
                    className="w-full py-4 text-slate-400 hover:text-white font-bold transition-colors"
                  >
                    Try Sample Drawing →
                  </button>
                </div>
              </form>
            </div>
          </motion.div>
        ) : (
          <div className="grid grid-cols-1 xl:grid-cols-4 gap-8">
            {/* Viewport - The Big Drawing Area */}
            <div className="xl:col-span-3 space-y-4 h-[80vh] flex flex-col">
              <div
                ref={viewportRef}
                className="flex-1 bg-slate-950 rounded-[2rem] border border-slate-800/50 overflow-auto relative shadow-inner custom-scrollbar"
              >
                <div className="relative inline-block">
                  <img
                    src={processedData.image.startsWith("http") ? processedData.image : processedData.image}
                    alt="Drawing"
                    className="max-w-none block opacity-90"
                  />

                  {/* SVG Overlay */}
                  <svg className="absolute inset-0 w-full h-full pointer-events-none">
                    <AnimatePresence>
                      {processedData.ducts.map((duct, idx) => (
                        <g key={idx}>
                          {/* Pulsing Selection Highlight */}
                          {selectedDuct?.coords.cx === duct.coords.cx && (
                            <motion.circle
                              initial={{ r: duct.coords.r * 2 }}
                              animate={{ r: [duct.coords.r * 2, duct.coords.r * 2.5, duct.coords.r * 2] }}
                              transition={{ repeat: Infinity, duration: 1.5 }}
                              cx={duct.coords.cx}
                              cy={duct.coords.cy}
                              fill="rgba(59, 130, 246, 0.15)"
                              stroke="rgba(59, 130, 246, 0.4)"
                              strokeWidth="2"
                            />
                          )}

                          <motion.circle
                            whileHover={{ scale: 1.1 }}
                            cx={duct.coords.cx}
                            cy={duct.coords.cy}
                            r={duct.coords.r * 1.4}
                            fill={hoveredDuct?.coords.cx === duct.coords.cx ? "rgba(59, 130, 246, 0.3)" : "rgba(59, 130, 246, 0.05)"}
                            stroke={selectedDuct?.coords.cx === duct.coords.cx ? "#60a5fa" : "#3b82f6"}
                            strokeWidth={selectedDuct?.coords.cx === duct.coords.cx ? "4" : "2"}
                            className="cursor-pointer pointer-events-auto transition-all"
                            onClick={() => setSelectedDuct(duct)}
                            onMouseEnter={() => setHoveredDuct(duct)}
                            onMouseLeave={() => setHoveredDuct(null)}
                          />

                          {duct.duct_box && (
                            <polygon
                              points={duct.duct_box.map(p => `${p[0]},${p[1]}`).join(' ')}
                              fill={hoveredDuct?.coords.cx === duct.coords.cx ? "rgba(251, 191, 36, 0.3)" : "rgba(251, 191, 36, 0.08)"}
                              stroke="#fbbf24"
                              strokeWidth="2"
                              strokeDasharray="8,4"
                            />
                          )}
                        </g>
                      ))}
                    </AnimatePresence>
                  </svg>
                </div>
              </div>

              {/* Legend & Tooltip */}
              <div className="flex justify-between items-center px-4">
                <div className="flex gap-6 text-[10px] font-black uppercase tracking-[0.2em] text-slate-500">
                  <div className="flex items-center gap-2"><span className="w-2.5 h-2.5 bg-blue-500 rounded-full shadow-[0_0_8px_rgba(59,130,246,0.6)]" /> Label Bubble</div>
                  <div className="flex items-center gap-2"><span className="w-2.5 h-2.5 bg-amber-500 rounded-sm shadow-[0_0_8px_rgba(245,158,11,0.6)]" /> Duct Body</div>
                </div>
                {hoveredDuct && (
                  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-blue-400 font-bold text-sm">
                    {hoveredDuct.dimension} • {hoveredDuct.pressure}
                  </motion.div>
                )}
              </div>
            </div>

            {/* Sidebar - Precision Controls */}
            <div className="xl:col-span-1 space-y-6 flex flex-col h-[80vh]">
              <div className="flex-1 bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-[2rem] p-6 flex flex-col overflow-hidden">
                <h2 className="text-xl font-bold mb-6 flex justify-between items-center">
                  <span>System Inventory</span>
                  <span className="bg-slate-800 text-xs px-2 py-1 rounded-md text-slate-400 font-mono">
                    {processedData.ducts.length}
                  </span>
                </h2>

                <div className="flex-1 overflow-y-auto space-y-3 pr-2 custom-scrollbar">
                  {processedData.ducts.map((duct, idx) => (
                    <button
                      key={idx}
                      onClick={() => scrollToDuct(duct)}
                      onMouseEnter={() => setHoveredDuct(duct)}
                      onMouseLeave={() => setHoveredDuct(null)}
                      className={`w-full text-left p-4 rounded-2xl border transition-all relative overflow-hidden group ${selectedDuct?.coords.cx === duct.coords.cx
                        ? 'bg-blue-600/90 border-blue-400 shadow-lg'
                        : 'bg-slate-800/40 border-slate-800 hover:border-slate-700'
                        }`}
                    >
                      <div className="relative z-10 flex justify-between items-start">
                        <div className="space-y-1">
                          <div className="font-black text-sm tracking-tight">DUX-{duct.id}</div>
                          <div className={`text-xs font-medium ${selectedDuct?.coords.cx === duct.id ? 'text-blue-100' : 'text-slate-500'}`}>
                            {duct.dimension} • {duct.pressure}
                          </div>
                        </div>
                        <div className="bg-white/10 px-2 py-1 rounded text-[10px] font-bold">POS: {duct.coords.cx},{duct.coords.cy}</div>
                      </div>
                      <div className="absolute top-0 right-0 p-4 opacity-0 group-hover:opacity-10 transition-opacity text-4xl">📎</div>
                    </button>
                  ))}
                </div>

                {/* Selected Details Expansion */}
                <AnimatePresence mode="wait">
                  {selectedDuct && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="mt-6 pt-6 border-t border-slate-800 space-y-4 overflow-hidden"
                    >
                      <div className="space-y-1">
                        <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Selected Component</div>
                        <div className="text-2xl font-black">{selectedDuct.dimension}</div>
                      </div>
                      <p className="text-xs text-slate-400 leading-relaxed italic border-l-2 border-slate-700 pl-3">
                        &quot;{selectedDuct.description}&quot;
                      </p>
                      <button
                        onClick={() => setSelectedDuct(null)}
                        className="w-full py-3 bg-slate-800 hover:bg-slate-700 rounded-xl font-bold text-xs transition-colors"
                      >
                        Release Lock
                      </button>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              {/* Analysis Summary Badge */}
              <div className="bg-gradient-to-br from-indigo-900/40 to-blue-900/40 border border-indigo-500/20 p-6 rounded-[2rem] flex items-center justify-between">
                <div className="space-y-1">
                  <div className="text-xs font-bold text-indigo-300/60 leading-none">HIGH CAPACITY</div>
                  <div className="text-2xl font-black">{processedData.ducts.filter(d => d.pressure === "High Pressure").length} Ducts</div>
                </div>
                <div className="p-3 bg-indigo-500/20 rounded-full text-2xl">⚡</div>
              </div>
            </div>
          </div>
        )}
      </div>

      <style jsx global>{`
        .custom-scrollbar::-webkit-scrollbar { width: 6px; height: 6px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 10px; }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #334155; }
      `}</style>

      <footer className="mt-24 pb-12 text-center">
        <div className="text-[10px] font-black uppercase tracking-[0.4em] text-slate-700">
          Architecture Logic v2.4 • Midlothian DHC Unit Analysis
        </div>
      </footer>
    </main>
  );
}
