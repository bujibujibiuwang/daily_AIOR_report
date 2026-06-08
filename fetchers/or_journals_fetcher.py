import requests
from datetime import datetime, timedelta, timezone

CROSSREF_API = "https://api.crossref.org/works"
JOURNALS = [
    "Operations Research",
    "Management Science",
]

# ...existing code...

SC_KEYWORDS = [
    "supply chain", "inventory", "inventory control", "inventory management",
    "demand forecast", "demand forecasting", "demand prediction",
    "safety stock", "replenishment", "newsvendor", "logistics",
    "lead time", "service level", "warehouse", "distribution"
]

AI_KEYWORDS = [
    "artificial intelligence", "machine learning", "deep learning",
    "neural network", "transformer", "large language model", "llm",
    "time series", "xgboost", "lightgbm", "random forest", "reinforcement learning"
]

# 用于 Crossref 粗检索（扩大召回）
QUERY_TERMS = SC_KEYWORDS + AI_KEYWORDS

def _days_ago_iso(days: int) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=days)
    return dt.strftime("%Y-%m-%d")

def _safe_get_title(item: dict) -> str:
    t = item.get("title", [])
    return t[0].strip() if t else ""

def _safe_get_abstract(item: dict) -> str:
    return (item.get("abstract") or "").strip()

def _is_sc_ai_intersection(title: str, abstract: str) -> bool:
    text = f"{title} {abstract}".lower()
    has_sc = any(k in text for k in SC_KEYWORDS)
    has_ai = any(k in text for k in AI_KEYWORDS)
    return has_sc and has_ai

def fetch(days_back: int = 30, per_journal: int = 100) -> list[dict]:
    papers: list[dict] = []
    headers = {"User-Agent": "daily_AIOR_report/1.0 (mailto:your_email@example.com)"}
    from_date = _days_ago_iso(days_back)

    for journal in JOURNALS:
        params = {
            "filter": f'from-pub-date:{from_date},container-title:{journal},type:journal-article',
            "rows": per_journal,
            "sort": "published",
            "order": "desc",
            "select": "DOI,title,URL,abstract,published-print,published-online,container-title,author",
            "query.bibliographic": " OR ".join(QUERY_TERMS),
        }

        try:
            resp = requests.get(CROSSREF_API, params=params, headers=headers, timeout=30)
            if resp.status_code != 200:
                continue

            items = resp.json().get("message", {}).get("items", [])
            for it in items:
                doi = (it.get("DOI") or "").strip()
                title = _safe_get_title(it)
                if not doi or not title:
                    continue

                abstract = _safe_get_abstract(it)
                if not _is_sc_ai_intersection(title, abstract):
                    continue

                link = it.get("URL") or (f"https://doi.org/{doi}" if doi else "")
                papers.append({
                    "id": f"crossref:{doi.lower()}",
                    "title": title,
                    "abstract": abstract,
                    "url": link,
                    "source": "OR-Journal",
                    "journal": (it.get("container-title") or [""])[0],
                    "publishedAt": "",
                })
        except Exception:
            continue

    return papers