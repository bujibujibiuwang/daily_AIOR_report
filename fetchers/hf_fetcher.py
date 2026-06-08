import requests

HF_API_URL = "https://huggingface.co/api/daily_papers"

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

# ── 噪声词（无明确 AI 方法时直接排除）──────────────────────────────────────
NOISE_KEYWORDS = [
    "branch-and-cut", "branch-price-and-cut", "primal-dual",
    "mixed-integer programming", "integer programming",
    "stochastic programming", "robust optimization",
    "vehicle routing", "queueing", "markov decision",
    "dynamic programming", "linear programming",
]


def _contains_any(text: str, keywords: list) -> bool:
    return any(k in text for k in keywords)


def _is_sc_ai_intersection(title: str, abstract: str) -> bool:
    t = (title or "").lower()
    a = (abstract or "").lower()
    full = f"{t} {a}"

    has_sc = _contains_any(t, SC_TITLE_KEYWORDS)
    has_ai = _contains_any(full, AI_STRICT_KEYWORDS)
    is_noise = _contains_any(full, NOISE_KEYWORDS) and not has_ai

    return has_sc and has_ai and not is_noise


def fetch() -> list[dict]:
    try:
        resp = requests.get(HF_API_URL, timeout=30)
        if resp.status_code != 200:
            print(f"[HF] HTTP {resp.status_code}")
            return []

        papers = []
        raw = resp.json()
        print(f"[HF] raw papers: {len(raw)}")

        for p in raw:
            base = p.get("paper", {})
            paper_id = base.get("id") or p.get("id")
            if not paper_id:
                continue

            title = base.get("title") or p.get("title") or ""
            summary = base.get("summary") or p.get("summary") or ""

            if not _is_sc_ai_intersection(title, summary):
                continue

            papers.append({
                "id": paper_id,
                "title": title,
                "summary": summary[:1000],
                "authors": [
                    a.get("name", a) if isinstance(a, dict) else a
                    for a in (base.get("authors") or [])
                ],
                "link": f"https://huggingface.co/papers/{paper_id}",
                "source": "huggingface",
                "date": (base.get("publishedAt") or p.get("publishedAt") or "")[:10],
            })

        print(f"[HF] kept after SC+AI filter: {len(papers)}")
        return papers

    except Exception as e:
        print(f"[HF] error: {e}")
        return []