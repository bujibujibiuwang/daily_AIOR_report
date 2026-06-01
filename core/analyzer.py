import os
import json
import re
import time
from datetime import date, timedelta
import openai

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "deepseek-chat")

_SC_KEYWORDS = [
    # 供应链核心概念
    "SUPPLY CHAIN", "SUPPLY-CHAIN",
    # 需求预测
    "DEMAND FORECAST", "DEMAND PREDICTION", "DEMAND SENSING",
    "SALES FORECAST", "SALES PREDICTION",
    "DEMAND PLANNING", "DEMAND ESTIMATION",
    # 库存管理
    "INVENTORY", "INVENTORY CONTROL", "INVENTORY MANAGEMENT",
    "INVENTORY OPTIMIZATION", "INVENTORY POLICY",
    "SAFETY STOCK", "REORDER POINT", "STOCK-OUT", "STOCKOUT",
    "REPLENISHMENT", "ORDER QUANTITY", "EOQ", "NEWSVENDOR",
    "MULTI-ECHELON", "MULTI ECHELON",
    # 供应链计划与优化
    "PROCUREMENT", "SOURCING", "SUPPLIER SELECTION",
    "PRODUCTION PLANNING", "MASTER PRODUCTION",
    "CAPACITY PLANNING", "S&OP", "SALES AND OPERATIONS",
    "WAREHOUSE", "DISTRIBUTION CENTER", "ORDER FULFILLMENT",
    "LEAD TIME", "SERVICE LEVEL",
    # 物流与配送（和供应链直接相关的）
    "LAST MILE", "DELIVERY ROUTING", "LOGISTICS NETWORK",
    "TRANSPORTATION PLANNING",
    # 风险与扰动
    "SUPPLY CHAIN DISRUPTION", "SUPPLY CHAIN RISK",
    "BULLWHIP", "DEMAND UNCERTAINTY", "SUPPLY UNCERTAINTY",
]

_AI_KEYWORDS = [
    # 深度学习
    "DEEP LEARNING", "NEURAL NETWORK", "CONVOLUTIONAL", "RECURRENT",
    "LSTM", "GRU", "TEMPORAL CONVOLUTIONAL",
    # Transformer / 序列模型
    "TRANSFORMER", "ATTENTION MECHANISM", "SELF-ATTENTION",
    "LARGE LANGUAGE MODEL", "LLM", "FOUNDATION MODEL",
    "TIME SERIES", "SEQUENCE MODEL", "TEMPORAL MODEL",
    # 生成/概率模型
    "GENERATIVE", "DIFFUSION MODEL", "NORMALIZING FLOW",
    "PROBABILISTIC FORECAST", "CONFORMAL PREDICTION",
    "QUANTILE REGRESSION", "UNCERTAINTY QUANTIFICATION",
    # 强化学习
    "REINFORCEMENT LEARNING", "POLICY GRADIENT", "Q-LEARNING",
    "PROXIMAL POLICY", "DEEP RL", "MULTI-AGENT",
    # 经典 ML
    "MACHINE LEARNING", "GRADIENT BOOSTING", "XGBOOST", "LIGHTGBM",
    "RANDOM FOREST", "SUPERVISED LEARNING", "TRANSFER LEARNING",
    "GRAPH NEURAL", "GNN",
    # AI for SC 专用
    "LEARNING-BASED", "DATA-DRIVEN", "END-TO-END",
    "AUTOREGRESSIVE", "FORECAST MODEL",
]


def filter_relevant(papers: list[dict], days: int = 90) -> list[dict]:
    """
    双维度评分过滤 + 时间过滤：
    - 时间：只保留最近 days 天内发表的论文（依赖 paper['date'] 字段）
      注意：HF 的 publishedAt 是 arXiv 原始发布日期，可能数月前，
      因此窗口放宽为 90 天，避免误杀 HF 精选的经典新论文。
    - OR 维度：命中 OR 关键词的数量
    - AI 维度：命中 AI/ML 关键词的数量
    保留策略：
      1. 标题命中 OR 关键词 → 直接保留（核心 OR 论文）
      2. OR 分 >= 2 且 AI 分 >= 1 → 保留（AI+OR 交叉）
      3. 仅 OR 分 >= 3 → 保留（纯 OR 但高度相关）
    """
    cutoff = date.today() - timedelta(days=days)
    result = []
    skipped_old = 0
    no_date = 0

    for p in papers:
        # 时间过滤
        raw_date = p.get("date", "")
        if raw_date:
            try:
                paper_date = date.fromisoformat(str(raw_date)[:10])
                if paper_date < cutoff:
                    skipped_old += 1
                    continue
            except ValueError:
                pass  # 日期格式异常则不过滤
        else:
            no_date += 1

        title = p.get("title", "").upper()
        summary = p.get("summary", "").upper()
        text = title + " " + summary

        sc_title_hits = sum(1 for kw in _SC_KEYWORDS if kw in title)
        sc_hits = sum(1 for kw in _SC_KEYWORDS if kw in text)
        ai_hits = sum(1 for kw in _AI_KEYWORDS if kw in text)

        # 规则 1：标题直接命中供应链关键词 + 任意 AI 词 → 直接保留
        if sc_title_hits >= 1 and ai_hits >= 1:
            result.append(p)
            continue
        # 规则 2：标题命中供应链关键词（即使暂无 AI 词，也保留待 LLM 判断）
        if sc_title_hits >= 1:
            result.append(p)
            continue
        # 规则 3：摘要中供应链 + AI 双维度交叉
        if sc_hits >= 2 and ai_hits >= 1:
            result.append(p)
            continue

    if skipped_old:
        print(f"  [filter] skipped {skipped_old} papers older than {days} days")
    if no_date:
        print(f"  [filter] {no_date} papers had no date (kept)")
    print(f"  [filter] {len(result)} / {len(papers)} papers passed SC+AI keyword filter")
    return result


def analyze_batch(papers: list[dict]) -> list[dict]:
    """LLM analysis: returns enriched paper dicts with Chinese metadata and score."""
    if not papers or not OPENAI_API_KEY:
        return []

    client = openai.OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
    results = []

    BATCH = 8
    for i in range(0, len(papers), BATCH):
        batch = papers[i : i + BATCH]
        context = ""
        for p in batch:
            context += (
                f"\nID: {p['id']}\n"
                f"标题: {p['title']}\n"
                f"摘要: {p.get('summary', '')[:400]}\n---\n"
            )

        prompt = f"""你是供应链 AI 领域的资深研究员，专注于将机器学习/深度学习技术应用于供应链管理问题。请分析以下论文，返回严格的JSON格式。

输出一个JSON对象，包含 "papers" 数组，每个元素格式：
{{
  "id": "原样复制论文ID，不得修改",
  "title_zh": "中文标题（简洁准确）",
  "contribution_zh": "核心算法创新（一句话，不超过50字）",
  "value_zh": "供应链应用场景（一句话，不超过50字）",
  "keywords": ["关键词1","关键词2","关键词3"],
  "score": 与AI+供应链交叉的相关性评分0-10（整数）
}}

评分标准（聚焦 AI × 供应链）：
- 9-10分：AI/ML 方法直接用于供应链核心问题
          例：需求预测、库存控制/优化、安全库存计算、补货策略、
              供应链风险预测、采购优化、S&OP 计划
- 7-8分：时间序列/概率预测方法，明确在零售/供应链场景验证
          或强化学习用于库存/补货决策
- 4-6分：通用时间序列预测方法（未明确供应链场景），
          或供应链问题但未使用 AI 技术
- 0-3分：与供应链无关（纯路径规划、调度、CV、NLP、视频生成等）

只输出JSON，不要有其他内容。每篇论文的id必须与输入完全一致。

论文列表：
{context}"""

        try:
            # 最多重试 3 次，间隔 10/20/30 秒
            last_err = None
            for attempt in range(3):
                try:
                    resp = client.chat.completions.create(
                        model=OPENAI_MODEL,
                        messages=[{"role": "user", "content": prompt}],
                        timeout=60,
                    )
                    break
                except Exception as e:
                    last_err = e
                    wait = (attempt + 1) * 10
                    print(f"  [analyzer] attempt {attempt+1} failed: {e}, retrying in {wait}s...")
                    time.sleep(wait)
            else:
                raise last_err

            raw = resp.choices[0].message.content.strip()
            # Extract JSON object
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                data = json.loads(match.group())
                batch_results = data.get("papers", [])
                # 验证 id 匹配，打印不匹配的情况便于调试
                batch_ids = {p["id"] for p in batch}
                for r in batch_results:
                    if r.get("id") not in batch_ids:
                        print(f"  [analyzer] WARNING: LLM returned unknown id: {r.get('id')!r}")
                results.extend(batch_results)
            else:
                print(f"  [analyzer] WARNING: no JSON found in response: {raw[:200]}")
        except Exception as e:
            print(f"  [analyzer] batch error (all retries failed): {e}")
            # 兜底：将本批论文以默认分数 6 加入结果，确保不丢失
            for p in batch:
                results.append({
                    "id": p["id"],
                    "title_zh": p["title"],
                    "contribution_zh": "",
                    "value_zh": "",
                    "keywords": [],
                    "score": 6,
                })
            print(f"  [analyzer] fallback: added {len(batch)} papers with default score=6")

    return results
