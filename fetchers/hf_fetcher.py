import requests


HF_API_URL = "https://huggingface.co/api/daily_papers"

# 供应链 + AI 相关的粗筛关键词（全大写匹配）
_SC_FILTER = [
    "SUPPLY CHAIN", "DEMAND FORECAST", "DEMAND PREDICTION", "DEMAND PLANNING",
    "INVENTORY", "SAFETY STOCK", "REPLENISHMENT", "NEWSVENDOR",
    "STOCK-OUT", "STOCKOUT", "REORDER", "ORDER QUANTITY",
    "PROCUREMENT", "SOURCING", "SUPPLIER",
    "WAREHOUSE", "DISTRIBUTION CENTER", "ORDER FULFILLMENT",
    "BULLWHIP", "LEAD TIME", "SERVICE LEVEL",
    "SALES FORECAST", "RETAIL FORECAST", "RETAIL DEMAND",
]


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
            title = base.get("title") or p.get("title") or ""
            summary = base.get("summary") or p.get("summary") or ""
            # 只保留与供应链相关的论文，降低后续 LLM 调用成本
            combined = (title + " " + summary).upper()
            if not any(kw in combined for kw in _SC_FILTER):
                continue
            papers.append({
                "id": paper_id,
                "title": title,
                "summary": summary[:1000],
                "authors": [a.get("name", a) if isinstance(a, dict) else a
                            for a in (base.get("authors") or [])],
                "link": f"https://huggingface.co/papers/{paper_id}",
                "source": "huggingface",
                "date": (base.get("publishedAt") or p.get("publishedAt") or "")[:10],
            })
        return papers
    except Exception:
        return []
