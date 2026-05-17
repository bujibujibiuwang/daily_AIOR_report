import os
import json
from datetime import date, timedelta

HISTORY_FILE = "history.txt"
PAPERS_JSON = os.path.join("web", "public", "papers.json")
INDEX_FILE = os.path.join("docs", "index.md")
RETENTION_DAYS = 30


# ---------- history.txt ----------

def get_history() -> set[str]:
    if not os.path.exists(HISTORY_FILE):
        return set()
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


def save_history(paper_ids: list[str]) -> None:
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        for pid in paper_ids:
            f.write(f"{pid}\n")


# ---------- papers.json ----------

def load_papers_json() -> list[dict]:
    if not os.path.exists(PAPERS_JSON):
        return []
    with open(PAPERS_JSON, "r", encoding="utf-8") as f:
        return json.load(f).get("papers", [])


def save_papers_json(new_papers: list[dict]) -> None:
    os.makedirs(os.path.dirname(PAPERS_JSON), exist_ok=True)
    existing = load_papers_json()
    existing_ids = {p["id"] for p in existing}
    for p in new_papers:
        if p["id"] not in existing_ids:
            existing.insert(0, p)
            existing_ids.add(p["id"])

    threshold = (date.today() - timedelta(days=RETENTION_DAYS)).isoformat()
    existing = [p for p in existing if (p.get("date") or "9999") >= threshold]

    with open(PAPERS_JSON, "w", encoding="utf-8") as f:
        json.dump(
            {"updated": str(date.today()), "papers": existing},
            f,
            ensure_ascii=False,
            indent=2,
        )


# ---------- docs/index.md ----------

def save_index_md(papers: list[dict], today_str: str) -> None:
    os.makedirs("docs", exist_ok=True)
    header = "---\nlayout: default\n---\n"

    if not papers:
        block_body = "今日无新增 OR 相关研究\n"
    else:
        lines = []
        for p in sorted(papers, key=lambda x: -x.get("score", 0)):
            lines.append(f"\n### {p.get('title_zh') or p['title']}")
            lines.append(f"- **英文标题**: {p['title']}")
            source_badge = {"huggingface": "🤗 HuggingFace", "arxiv": "📄 arXiv",
                            "paperswithcode": "💻 PapersWithCode"}.get(p.get("source", ""), p.get("source", ""))
            lines.append(f"- **来源**: {source_badge}  ⭐ {p.get('score', 0)}/10")
            if p.get("authors"):
                lines.append(f"- **作者**: {', '.join(str(a) for a in p['authors'][:3])}")
            if p.get("contribution_zh"):
                lines.append(f"- **核心贡献**: {p['contribution_zh']}")
            if p.get("value_zh"):
                lines.append(f"- **实践价值**: {p['value_zh']}")
            if p.get("keywords"):
                lines.append(f"- **OR 技术关键词**: {', '.join(p['keywords'])}")
            lines.append(f"- **论文链接**: {p['link']}")
            lines.append("---")
        block_body = "\n".join(lines) + "\n"

    new_block = f"{today_str}\n\n{block_body}"

    existing = ""
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            existing = f.read()

    content = existing.replace(header, "").strip()
    blocks = []
    if content:
        if content.startswith("## 📅 "):
            content = content[len("## 📅 "):]
        for chunk in content.split("\n## 📅 "):
            chunk = chunk.strip()
            if chunk:
                blocks.append(chunk)

    blocks.insert(0, new_block.strip())
    threshold = (date.today() - timedelta(days=RETENTION_DAYS)).isoformat()
    valid_blocks = [b for b in blocks if b[:10] >= threshold]

    final = header + "\n## 📅 ".join(valid_blocks)
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(final)
