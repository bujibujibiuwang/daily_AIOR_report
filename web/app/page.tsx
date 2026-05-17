import { readFileSync } from "fs";
import { join } from "path";
import SearchWrapper from "@/components/SearchWrapper";
import ChatBot from "@/components/ChatBot";

export interface Paper {
  id: string;
  title: string;
  title_zh?: string;
  summary?: string;
  authors?: string[];
  link: string;
  source: string;
  date: string;
  score: number;
  contribution_zh?: string;
  value_zh?: string;
  keywords?: string[];
}

function loadPapers(): { papers: Paper[]; updated: string } {
  try {
    const raw = readFileSync(join(process.cwd(), "public", "papers.json"), "utf-8");
    const data = JSON.parse(raw);
    return {
      papers: (data.papers || []).filter((p: Paper) => p.score >= 3),
      updated: data.updated || "",
    };
  } catch {
    return { papers: [], updated: "" };
  }
}

export default function Home() {
  const { papers, updated } = loadPapers();

  return (
    <>
      {/* Stats bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-6 bg-white rounded-xl shadow-sm border border-gray-100 px-5 py-3">
        <div className="flex gap-6 text-sm text-gray-500">
          <span>🗓️ 最后更新: <strong className="text-gray-800">{updated || "—"}</strong></span>
          <span>📚 精选论文: <strong className="text-gray-800">{papers.length}</strong> 篇</span>
          <span>
            🤗{" "}
            <strong className="text-gray-800">
              {papers.filter((p) => p.source === "huggingface").length}
            </strong>{" "}
            · 📄{" "}
            <strong className="text-gray-800">
              {papers.filter((p) => p.source === "arxiv").length}
            </strong>{" "}
            · 💻{" "}
            <strong className="text-gray-800">
              {papers.filter((p) => p.source === "paperswithcode").length}
            </strong>
          </span>
        </div>
      </div>

      <SearchWrapper papers={papers} />
      <ChatBot />
    </>
  );
}
