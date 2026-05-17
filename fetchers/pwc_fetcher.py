import requests

PWC_API = "https://paperswithcode.com/api/v1/papers/"

_OR_KEYWORDS = [
    "supply chain", "vehicle routing", "scheduling", "inventory",
    "logistics", "optimization", "operations research", "routing",
]


def fetch(max_results: int = 50) -> list[dict]:
    try:
        resp = requests.get(
            PWC_API,
            params={"ordering": "-published", "page_size": max_results},
            timeout=30,
        )
        if resp.status_code != 200:
            return []
        papers = []
        for p in resp.json().get("results", []):
            arxiv_id = p.get("arxiv_id") or ""
            paper_id = f"pwc_{arxiv_id}" if arxiv_id else f"pwc_{p.get('id', '')}"
            title = p.get("title") or ""
            abstract = (p.get("abstract") or "")[:1000]
            text = f"{title} {abstract}".lower()
            if not any(kw in text for kw in _OR_KEYWORDS):
                continue
            papers.append({
                "id": paper_id,
                "title": title,
                "summary": abstract,
                "authors": p.get("authors") or [],
                "link": p.get("url_abs") or f"https://paperswithcode.com/paper/{arxiv_id}",
                "source": "paperswithcode",
            })
        return papers
    except Exception:
        return []
