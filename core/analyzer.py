import os
import json
import re
import time
from datetime import date, timedelta
import openai

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "deepseek-chat")

_OR_KEYWORDS = [
    # 经典 OR 问题
    "SUPPLY CHAIN", "INVENTORY", "VEHICLE ROUTING", "VRP", "TSP",
    "TRAVELING SALESMAN", "JOB SHOP", "JOBSHOP", "JOB-SHOP",
    "FLOW SHOP", "SCHEDULING", "PRODUCTION PLANNING",
    "OPERATIONS RESEARCH", "OPERATIONAL RESEARCH",
    "MATHEMATICAL PROGRAMMING", "LINEAR PROGRAMMING", "INTEGER PROGRAMMING",
    "MIXED INTEGER", "STOCHASTIC PROGRAMMING", "ROBUST OPTIMIZATION",
    "COMBINATORIAL OPTIMIZATION", "NETWORK FLOW", "FACILITY LOCATION",
    "WAREHOUSE", "ORDER PICKING", "RESOURCE ALLOCATION",
    "METAHEURISTIC", "GENETIC ALGORITHM", "SIMULATED ANNEALING",
    "TABU SEARCH", "ANT COLONY", "PARTICLE SWARM",
    "COLUMN GENERATION", "BRANCH AND BOUND", "BRANCH AND PRICE",
    "LAGRANGIAN RELAXATION", "BENDERS DECOMPOSITION",
    "DEMAND FORECASTING", "DELIVERY ROUTING", "LAST MILE",
    "MULTI-OBJECTIVE OPTIMIZATION", "PARETO",
    "CAPACITATED", "BIN PACKING", "KNAPSACK",
    "ROUTING PROBLEM", "CONSTRAINT PROGRAMMING", "LOCAL SEARCH",
    "BILEVEL OPTIMIZATION", "PARALLEL MACHINE", "LOGISTICS",
    "DISPATCH", "ASSIGNMENT PROBLEM", "SET COVERING", "SET PACKING",
]

_AI_KEYWORDS = [
    # 深度学习 / 强化学习
    "REINFORCEMENT LEARNING", "DEEP LEARNING", "NEURAL NETWORK",
    "TRANSFORMER", "ATTENTION MECHANISM", "GRAPH NEURAL",
    "LARGE LANGUAGE MODEL", "LLM", "FOUNDATION MODEL",
    "GENERATIVE", "DIFFUSION MODEL",
    # ML 方法
    "MACHINE LEARNING", "SUPERVISED LEARNING", "UNSUPERVISED",
    "IMITATION LEARNING", "CONTRASTIVE LEARNING",
    # AI for Optimization 专用词
    "NEURAL COMBINATORIAL", "LEARNING TO OPTIMIZE", "LEARNING-BASED",
    "POINTER NETWORK", "ATTENTION-BASED", "END-TO-END",
    "POLICY GRADIENT", "PROXIMAL POLICY", "Q-LEARNING",
    "MONTE CARLO TREE", "AUTOREGRESSIVE",
]


def filter_relevant(papers: list[dict], days: int = 30) -> list[dict]:
    """
    双维度评分过滤 + 时间过滤：
    - 时间：只保留最近 days 天内发表的论文（依赖 paper['date'] 字段）
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

        title = p.get("title", "").upper()
        summary = p.get("summary", "").upper()
        text = title + " " + summary

        or_title_hits = sum(1 for kw in _OR_KEYWORDS if kw in title)
        or_hits = sum(1 for kw in _OR_KEYWORDS if kw in text)
        ai_hits = sum(1 for kw in _AI_KEYWORDS if kw in text)

        # 规则 1：标题直接命中 OR 关键词
        if or_title_hits >= 1:
            result.append(p)
            continue
        # 规则 2：AI+OR 双维度交叉（摘要中均有命中）
        if or_hits >= 2 and ai_hits >= 1:
            result.append(p)
            continue
        # 规则 3：摘要高度 OR 相关（纯 OR 论文，无需 AI 词）
        if or_hits >= 3:
            result.append(p)

    if skipped_old:
        print(f"  [filter] skipped {skipped_old} papers older than {days} days")
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

        prompt = f"""你是AI+运筹优化(OR)领域的资深研究员。请分析以下论文，返回严格的JSON格式。

输出一个JSON对象，包含 "papers" 数组，每个元素格式：
{{
  "id": "原样复制论文ID，不得修改",
  "title_zh": "中文标题（简洁准确）",
  "contribution_zh": "核心算法创新（一句话，不超过50字）",
  "value_zh": "工业应用场景（一句话，不超过50字）",
  "keywords": ["关键词1","关键词2","关键词3"],
  "score": 与AI+OR交叉的相关性评分0-10（整数）
}}

评分标准：
- 9-10分：直接研究OR核心问题（调度、路径规划、供应链优化等）
- 7-8分：AI/ML方法明确用于解决OR经典问题
- 4-6分：间接相关（通用优化方法，可能适用于OR）
- 0-3分：与OR无关（纯CV、NLP、视频生成等）

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
