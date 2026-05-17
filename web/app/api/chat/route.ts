import { NextRequest, NextResponse } from "next/server";
import { readFileSync } from "fs";
import { join } from "path";
import OpenAI from "openai";

interface Paper {
  id: string;
  title: string;
  title_zh?: string;
  summary?: string;
  link: string;
  source: string;
  date: string;
  score: number;
  contribution_zh?: string;
  value_zh?: string;
  keywords?: string[];
}

function loadPapers(): Paper[] {
  try {
    const raw = readFileSync(join(process.cwd(), "public", "papers.json"), "utf-8");
    return JSON.parse(raw).papers ?? [];
  } catch {
    return [];
  }
}

function searchPapers(papers: Paper[], question: string): Paper[] {
  const words = question
    .toLowerCase()
    .split(/[\s，,。？?！!]+/)
    .filter((w) => w.length > 1);

  const scored = papers.map((p) => {
    const text = [
      p.title,
      p.title_zh ?? "",
      ...(p.keywords ?? []),
      p.contribution_zh ?? "",
      p.value_zh ?? "",
      p.summary ?? "",
    ]
      .join(" ")
      .toLowerCase();

    const hits = words.filter((w) => text.includes(w)).length;
    return { paper: p, hits };
  });

  return scored
    .filter((s) => s.hits > 0)
    .sort((a, b) => b.hits - a.hits || b.paper.score - a.paper.score)
    .slice(0, 6)
    .map((s) => s.paper);
}

export async function POST(req: NextRequest) {
  try {
    const { question } = await req.json();
    if (!question?.trim()) {
      return NextResponse.json({ error: "Missing question" }, { status: 400 });
    }

    const papers = loadPapers();
    const relevant = searchPapers(papers, question);

    const context =
      relevant.length > 0
        ? relevant
            .map(
              (p, i) =>
                `[${i + 1}] 【${p.title_zh ?? p.title}】\n` +
                `    英文标题: ${p.title}\n` +
                `    核心贡献: ${p.contribution_zh ?? "—"}\n` +
                `    实践价值: ${p.value_zh ?? "—"}\n` +
                `    关键词: ${(p.keywords ?? []).join(", ")}\n` +
                `    链接: ${p.link}`
            )
            .join("\n\n")
        : "暂无匹配论文";

    const client = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
      baseURL: process.env.OPENAI_BASE_URL ?? "https://api.deepseek.com",
    });

    const completion = await client.chat.completions.create({
      model: process.env.OPENAI_MODEL ?? "deepseek-chat",
      messages: [
        {
          role: "system",
          content:
            "你是一个专业的AI+运筹优化(OR)领域研究助手。请基于提供的论文库，用简洁清晰的中文回答用户问题。" +
            "回答时请引用具体论文编号，并给出实用建议。如果论文库中没有相关内容，请如实说明并给出研究方向建议。",
        },
        {
          role: "user",
          content: `用户问题: ${question}\n\n相关论文 (共${relevant.length}篇):\n${context}`,
        },
      ],
    });

    return NextResponse.json({
      answer: completion.choices[0].message.content,
      sources: relevant,
    });
  } catch (err) {
    console.error("[chat API]", err);
    return NextResponse.json(
      { answer: "抱歉，发生了错误，请稍后重试。", sources: [] },
      { status: 500 }
    );
  }
}
