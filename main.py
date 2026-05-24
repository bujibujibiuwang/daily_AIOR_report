"""
AI+OR Daily Report Pipeline
Multi-source fetch → LLM analysis → papers.json + index.md + email
"""
import os
from datetime import date

from fetchers import hf_fetcher, arxiv_fetcher, pwc_fetcher
from core import storage, notifier
from core.analyzer import filter_relevant, analyze_batch


def build_email_body(papers: list[dict], today_str: str) -> str:
    if not papers:
        return f"AI+OR 每日报告 {today_str}\n\n今日无新增 OR 相关研究。"
    lines = [f"AI+OR 每日精选报告 {today_str}", "=" * 50]
    for p in papers:
        lines += [
            "",
            f"📄 {p.get('title_zh') or p['title']}",
            f"   {p['title']}",
            f"📌 核心贡献: {p.get('contribution_zh', '')}",
            f"💼 实践价值: {p.get('value_zh', '')}",
            f"🏷️  关键词: {', '.join(p.get('keywords', []))}",
            f"⭐ 相关性: {p.get('score', 0)}/10  |  来源: {p.get('source', '')}",
            f"🔗 {p['link']}",
            "-" * 40,
        ]
    return "\n".join(lines)


def main() -> None:
    today = date.today()
    today_str = str(today)
    print(f"=== AI+OR Daily Report {today_str} ===")

    # 1. Multi-source fetch
    print("Fetching: HuggingFace...")
    raw = hf_fetcher.fetch()
    print(f"  HF: {len(raw)} papers")

    print("Fetching: arXiv...")
    arxiv = arxiv_fetcher.fetch()
    print(f"  arXiv: {len(arxiv)} papers")

    print("Fetching: PapersWithCode...")
    pwc = pwc_fetcher.fetch()
    print(f"  PWC: {len(pwc)} papers")

    # 2. Deduplicate
    seen: set[str] = set()
    all_papers: list[dict] = []
    for p in raw + arxiv + pwc:
        if p["id"] not in seen:
            seen.add(p["id"])
            all_papers.append(p)
    print(f"Total unique: {len(all_papers)}")

    # 3. Filter history
    history = storage.get_history()
    new_papers = [p for p in all_papers if p["id"] not in history]
    print(f"New (not in history): {len(new_papers)}")

    # 4. Keyword pre-filter
    relevant = filter_relevant(new_papers)
    print(f"OR-relevant: {len(relevant)}")

    # 5. LLM analysis
    if relevant:
        print("Analyzing with LLM...")
        analysis = analyze_batch(relevant)
        analysis_map = {r["id"]: r for r in analysis if "id" in r}
    else:
        analysis_map = {}

    # 6. Enrich & score threshold
    enriched: list[dict] = []
    for p in relevant:
        a = analysis_map.get(p["id"], {})
        score = a.get("score", 0)
        if score < 6:
            continue
        enriched.append({
            **p,
            "date": today_str,
            "title_zh": a.get("title_zh", p["title"]),
            "contribution_zh": a.get("contribution_zh", ""),
            "value_zh": a.get("value_zh", ""),
            "keywords": a.get("keywords", []),
            "score": score,
        })

    print(f"High-quality OR papers: {len(enriched)}")

    # 7. Persist
    storage.save_papers_json(enriched)
    storage.save_index_md(enriched, today_str)
    storage.save_history([p["id"] for p in relevant])  # mark ALL relevant as seen

    # 8. Email
    email_body = build_email_body(enriched, today_str)
    notifier.send_email_notification(email_body, today)

    # 9. Git push
    os.system("git config user.name 'github-actions'")
    os.system("git config user.email 'github-actions@github.com'")
    os.system(f"git add docs/index.md history.txt web/public/papers.json")
    os.system(f"git commit -m 'Daily update {today_str}: {len(enriched)} OR papers'")
    os.system("git push")

    print("Done! ✅")


if __name__ == "__main__":
    main()
