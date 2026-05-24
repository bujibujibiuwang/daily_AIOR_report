import requests


HF_API_URL = "https://huggingface.co/api/daily_papers"


def fetch() -> list[dict]:
    try:
        resp = requests.get(HF_API_URL, timeout=30)
        if resp.status_code != 200:
            return []
        papers = []
        for p in resp.json():
            base = p.get("paper", {})
            paper_id = base.get("id") or p.get("id")
            if not paper_id:
                continue
            papers.append({
                "id": paper_id,
                "title": base.get("title") or p.get("title") or "",
                "summary": (base.get("summary") or p.get("summary") or "")[:1000],
                "authors": [a.get("name", a) if isinstance(a, dict) else a
                            for a in (base.get("authors") or [])],
                "link": f"https://huggingface.co/papers/{paper_id}",
                "source": "huggingface",
                "date": (base.get("publishedAt") or p.get("publishedAt") or "")[:10],
            })
        return papers
    except Exception:
        return []
