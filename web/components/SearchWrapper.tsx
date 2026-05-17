"use client";

import { useState, useMemo } from "react";
import PaperCard from "./PaperCard";
import type { Paper } from "@/app/page";

const SOURCE_OPTIONS = [
  { value: "all", label: "全部来源" },
  { value: "huggingface", label: "🤗 HuggingFace" },
  { value: "arxiv", label: "📄 arXiv" },
  { value: "paperswithcode", label: "💻 PapersWithCode" },
];

export default function SearchWrapper({ papers }: { papers: Paper[] }) {
  const [query, setQuery] = useState("");
  const [source, setSource] = useState("all");

  const filtered = useMemo(() => {
    return papers.filter((p) => {
      const text =
        `${p.title} ${p.title_zh ?? ""} ${(p.keywords ?? []).join(" ")} ${p.contribution_zh ?? ""}`.toLowerCase();
      const matchQuery = !query || text.includes(query.toLowerCase());
      const matchSource = source === "all" || p.source === source;
      return matchQuery && matchSource;
    });
  }, [papers, query, source]);

  const grouped = useMemo(() => {
    const g: Record<string, Paper[]> = {};
    for (const p of filtered) {
      const d = p.date || "unknown";
      if (!g[d]) g[d] = [];
      g[d].push(p);
    }
    return g;
  }, [filtered]);

  const sortedDates = Object.keys(grouped).sort().reverse();

  return (
    <div>
      {/* Search + Filter Bar */}
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="relative flex-1">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">🔍</span>
          <input
            type="text"
            placeholder="搜索论文标题、关键词、贡献..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2.5 border border-gray-200 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400 bg-white"
          />
        </div>
        <select
          value={source}
          onChange={(e) => setSource(e.target.value)}
          className="border border-gray-200 rounded-xl px-4 py-2.5 bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400 cursor-pointer"
        >
          {SOURCE_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
      </div>

      {/* Results */}
      {sortedDates.length === 0 ? (
        <div className="text-center text-gray-400 py-20 text-lg">
          暂无匹配论文 🤷
        </div>
      ) : (
        sortedDates.map((d) => (
          <div key={d} className="mb-10">
            <div className="flex items-center gap-3 mb-4">
              <h2 className="text-lg font-bold text-gray-700">📅 {d}</h2>
              <span className="bg-blue-100 text-blue-700 text-xs font-semibold px-2.5 py-0.5 rounded-full">
                {grouped[d].length} 篇
              </span>
              <div className="flex-1 h-px bg-gray-200" />
            </div>
            <div className="grid gap-4">
              {grouped[d]
                .sort((a, b) => b.score - a.score)
                .map((p) => (
                  <PaperCard key={p.id} paper={p} />
                ))}
            </div>
          </div>
        ))
      )}
    </div>
  );
}
