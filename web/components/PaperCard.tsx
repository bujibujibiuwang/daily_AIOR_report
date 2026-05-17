"use client";

import { useState } from "react";
import type { Paper } from "@/app/page";

const SOURCE_STYLE: Record<string, string> = {
  huggingface: "bg-yellow-100 text-yellow-800",
  arxiv: "bg-red-100 text-red-700",
  paperswithcode: "bg-green-100 text-green-800",
};

const SOURCE_LABEL: Record<string, string> = {
  huggingface: "🤗 HF",
  arxiv: "📄 arXiv",
  paperswithcode: "💻 PWC",
};

function ScoreDots({ score }: { score: number }) {
  return (
    <span className="flex gap-0.5 items-center">
      {[...Array(10)].map((_, i) => (
        <span
          key={i}
          className={`inline-block w-1.5 h-1.5 rounded-full ${
            i < score ? "bg-blue-500" : "bg-gray-200"
          }`}
        />
      ))}
      <span className="ml-1 text-xs text-gray-500 font-medium">{score}/10</span>
    </span>
  );
}

export default function PaperCard({ paper }: { paper: Paper }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 hover:shadow-md transition-all duration-200 hover:border-blue-100">
      {/* Top row */}
      <div className="flex items-start gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2 mb-1.5">
            <span
              className={`text-xs px-2 py-0.5 rounded-full font-semibold ${
                SOURCE_STYLE[paper.source] ?? "bg-gray-100 text-gray-700"
              }`}
            >
              {SOURCE_LABEL[paper.source] ?? paper.source}
            </span>
            <ScoreDots score={paper.score} />
          </div>

          {/* Chinese title */}
          <h3 className="font-bold text-gray-900 text-base leading-snug">
            {paper.title_zh || paper.title}
          </h3>
          {/* English title */}
          {paper.title_zh && (
            <p className="text-gray-400 text-xs mt-0.5 truncate" title={paper.title}>
              {paper.title}
            </p>
          )}
        </div>

        <a
          href={paper.link}
          target="_blank"
          rel="noopener noreferrer"
          className="shrink-0 bg-blue-50 hover:bg-blue-600 hover:text-white text-blue-600 text-sm px-3 py-1.5 rounded-xl font-medium transition-colors"
        >
          阅读 →
        </a>
      </div>

      {/* Contribution highlight */}
      {paper.contribution_zh && (
        <div className="mt-3 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-3">
          <p className="text-sm text-blue-900">
            <span className="font-semibold">💡 核心贡献：</span>
            {paper.contribution_zh}
          </p>
        </div>
      )}

      {/* Expand toggle */}
      <button
        onClick={() => setExpanded((v) => !v)}
        className="text-xs text-gray-400 hover:text-blue-500 mt-2.5 transition-colors"
      >
        {expanded ? "▲ 收起" : "▼ 展开详情"}
      </button>

      {/* Expanded details */}
      {expanded && (
        <div className="mt-3 space-y-2.5 text-sm text-gray-600 border-t pt-3">
          {paper.value_zh && (
            <p>
              <span className="font-semibold text-gray-700">💼 实践价值：</span>
              {paper.value_zh}
            </p>
          )}
          {paper.keywords && paper.keywords.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {paper.keywords.map((k) => (
                <span
                  key={k}
                  className="bg-gray-100 hover:bg-blue-100 text-gray-600 px-2 py-0.5 rounded-lg text-xs cursor-default transition-colors"
                >
                  {k}
                </span>
              ))}
            </div>
          )}
          {paper.authors && paper.authors.length > 0 && (
            <p className="text-gray-400 text-xs">
              👤 {paper.authors.slice(0, 4).join(", ")}
              {paper.authors.length > 4 ? ` 等 ${paper.authors.length} 人` : ""}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
