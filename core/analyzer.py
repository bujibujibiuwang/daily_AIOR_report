import os
import json
import re
import openai

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "deepseek-chat")

_OR_KEYWORDS = [
    "SUPPLY CHAIN", "INVENTORY", "FORECAST", "OPTIMIZATION", "ROUTE",
    "SCHEDULING", "PRODUCTION", "TSP", "VRP", "JSP", "LOGISTICS",
    "MATHEMATICAL PROGRAMMING", "DECISION MAKING", "ASSIGNMENT", "PLANNING",
    "OPERATIONS RESEARCH", "NETWORK FLOW", "INTEGER PROGRAMMING",
    "COMBINATORIAL", "HEURISTIC", "METAHEURISTIC", "DISPATCH",
]


def filter_relevant(papers: list[dict]) -> list[dict]:
    result = []
    for p in papers:
        text = f"{p.get('title', '')} {p.get('summary', '')}".upper()
        if any(kw in text for kw in _OR_KEYWORDS):
            result.append(p)
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
  "id": "原样复制论文ID",
  "title_zh": "中文标题（简洁准确）",
  "contribution_zh": "核心算法创新（一句话，不超过50字）",
  "value_zh": "工业应用场景（一句话，不超过50字）",
  "keywords": ["关键词1","关键词2","关键词3"],
  "score": 与AI+OR交叉的相关性评分0-10（整数）
}}

评分标准：10=直接研究OR核心问题；7-9=AI方法用于OR场景；4-6=间接相关；0-3=基本无关。
如果完全无关请将score设为0。只输出JSON，不要有其他内容。

论文列表：
{context}"""

        try:
            resp = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = resp.choices[0].message.content.strip()
            # Extract JSON object
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                data = json.loads(match.group())
                results.extend(data.get("papers", []))
        except Exception as e:
            print(f"  [analyzer] batch error: {e}")

    return results
