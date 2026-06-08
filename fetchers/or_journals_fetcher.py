import re
import requests
from datetime import datetime, timedelta, timezone

CROSSREF_API = "https://api.crossref.org/works"
JOURNALS = [
    "Operations Research",
    "Management Science",
]

# ── 供应链场景词（标题必须命中至少 1 个）────────────────────────────────────
SC_TITLE_KEYWORDS = [
    # 需求预测
    "demand forecast", "demand forecasting", "demand prediction",
    "demand planning", "demand estimation", "demand sensing",
    "retail forecast", "sales forecast", "sales prediction",
    # 库存管理
    "inventory", "inventory control", "inventory management",
    "inventory optimization", "inventory policy", "inventory replenishment",
    "safety stock", "stock-out", "stockout", "reorder point",
    "order quantity", "lot sizing", "newsvendor", "base-stock",
    "multi-echelon inventory", "perishable inventory",
    # 补货与订单
    "replenishment", "order fulfillment", "order management",
    "procurement", "sourcing", "supplier selection",
    # 供应链整体
    "supply chain", "supply chain management", "supply chain optimization",
    "supply chain risk", "supply chain disruption", "supply chain resilience",
    "supply chain network", "supply chain planning", "supply chain forecasting",
    "bullwhip effect", "vendor managed inventory",
    # 物流仓储
    "logistics", "warehouse", "warehousing", "distribution center",
    "last-mile", "fulfillment center", "cross-docking",
    "cold chain", "reverse logistics", "omnichannel",
    # 生产计划
    "production planning", "capacity planning", "lead time",
    "service level", "fill rate",
]

# ── 摘要辅助匹配（标题未命中时辅助加分）────────────────────────────────────
SC_ABSTRACT_KEYWORDS = [
    "supply chain", "inventory", "demand forecast",
    "replenishment", "safety stock", "logistics",
]

# ── AI 方法词（全文命中至少 1 个）──────────────────────────────────────────
AI_STRICT_KEYWORDS = [
    # 大语言模型
    "large language model", "llm", "gpt", "chatgpt", "gpt-4",
    "bert", "t5", "foundation model", "generative ai", "prompt",
    # 深度学习架构
    "transformer", "attention mechanism", "self-attention",
    "neural network", "deep learning", "deep neural",
    "lstm", "gru", "recurrent neural", "convolutional neural",
    "graph neural network", "gnn",
    # 机器学习方法
    "machine learning", "reinforcement learning", "deep reinforcement",
    "xgboost", "lightgbm", "gradient boosting", "random forest",
    "transfer learning", "federated learning",
    # 时间序列/预测专项
    "time series", "probabilistic forecast", "quantile regression",
    "conformal prediction", "bayesian deep", "temporal fusion",
    # 通用 AI
    "artificial intelligence",
]

# ── 噪声词（无明确AI方法时直接排除）────────────────────────────────────────
NOISE_KEYWORDS = [
    "branch-and-cut", "branch-price-and-cut", "primal-dual",
    "mixed-integer programming", "integer programming",
    "stochastic programming", "robust optimization",
    "vehicle routing", "queueing", "markov decision",
    "dynamic programming", "linear programming",
]

QUERY_TERMS = SC_TITLE_KEYWORDS[:10]  # Crossref 粗检索只取核心词避免参数过长


def _days_ago_iso(days: int) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=days)
    return dt.strftime("%Y-%m-%d")


def _safe_get_title(item: dict) -> str:
    t = item.get("title", [])
    return t[0].strip() if t else ""


def _safe_get_abstract(item: dict) -> str:
    raw = (item.get("abstract") or "").strip()
    return re.sub(r"<[^>]+>", " ", raw).strip()


def _contains_any(text: str, keywords: list) -> bool:
    return any(k in text for k in keywords)


def _is_sc_ai_intersection(title: str, abstract: str) -> bool:
    t = (title or "").lower()
    a = (abstract or "").lower()
    full = f"{t} {a}"

    # 供应链词：标题命中 OR（标题+摘要）都命中
    has_sc = (
        _contains_any(t, SC_TITLE_KEYWORDS)
        or (_contains_any(t, SC_ABSTRACT_KEYWORDS) and _contains_any(a, SC_ABSTRACT_KEYWORDS))
    )

    # AI 词：全文命中
    has_ai = _contains_any(full, AI_STRICT_KEYWORDS)

    # 噪声词：无 AI 时剔除
    is_noise = _contains_any(full, NOISE_KEYWORDS) and not has_ai

    return has_sc and has_ai and not is_noise


def fetch(days_back: int = 30, per_journal: int = 100, debug: bool = False) -> list[dict]:
    papers: list[dict] = []
    headers = {"User-Agent": "daily_AIOR_report/1.0 (mailto:your_real_email@example.com)"}
    from_date = _days_ago_iso(days_back)

    for journal in JOURNALS:
        params = {
            # 先按期刊+时间抓，再本地做 SC+AI 过滤
            "filter": f'from-pub-date:{from_date},container-title:{journal},type:journal-article',
            "rows": per_journal,
            "sort": "published",
            "order": "desc",
            "select": "DOI,title,URL,abstract,published-print,published-online,container-title,author",
        }

        try:
            resp = requests.get(CROSSREF_API, params=params, headers=headers, timeout=30)
            if resp.status_code != 200:
                if debug:
                    print(f"[OR-Journal] {journal} HTTP {resp.status_code}")
                continue

            items = resp.json().get("message", {}).get("items", [])
            if debug:
                print(f"[OR-Journal] {journal} raw items: {len(items)}")

            kept = 0
            for it in items:
                doi = (it.get("DOI") or "").strip()
                title = _safe_get_title(it)
                if not doi or not title:
                    continue

                abstract = _safe_get_abstract(it)
                if not _is_sc_ai_intersection(title, abstract):
                    continue

                link = it.get("URL") or f"https://doi.org/{doi}"
                papers.append({
                    "id": f"crossref:{doi.lower()}",
                    "title": title,
                    "abstract": abstract,
                    "url": link,
                    "source": "OR-Journal",
                    "journal": (it.get("container-title") or [""])[0],
                    "publishedAt": "",
                })
                kept += 1

            if debug:
                print(f"[OR-Journal] {journal} kept after SC+AI: {kept}")

        except Exception as e:
            if debug:
                print(f"[OR-Journal] {journal} error: {e}")
            continue

    return papers