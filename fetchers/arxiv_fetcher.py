import requests
import xml.etree.ElementTree as ET
from datetime import date, timedelta


ARXIV_BASE = "http://export.arxiv.org/api/query"

_QUERY_TEMPLATE = (
    # 供应链核心问题词（标题或摘要命中）
    '(ti:"supply chain" OR ti:"demand forecast" OR ti:"demand prediction" '
    'OR ti:"inventory" OR ti:"safety stock" OR ti:"replenishment" '
    'OR ti:"inventory control" OR ti:"inventory management" '
    'OR ti:"inventory optimization" OR ti:"demand planning" '
    'OR ti:"supply chain risk" OR ti:"supply chain disruption" '
    'OR abs:"demand forecasting" OR abs:"inventory optimization" '
    'OR abs:"safety stock" OR abs:"replenishment policy" '
    'OR abs:"supply chain management" OR abs:"newsvendor") '
    # 交集：要求论文在 AI/ML 相关类别下
    'AND (cat:cs.LG OR cat:cs.AI OR cat:stat.ML OR cat:math.OC OR cat:econ.GN)'
    ' AND submittedDate:[{start} TO {end}]'
)


def fetch(max_results: int = 100) -> list[dict]:
    # 抓取最近 7 天提交的 OR 相关论文，确保每天都有新内容
    end_date = date.today()
    start_date = end_date - timedelta(days=7)
    query = _QUERY_TEMPLATE.format(
        start=start_date.strftime("%Y%m%d") + "0000",
        end=end_date.strftime("%Y%m%d") + "2359",
    )
    params = {
        "search_query": query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    try:
        resp = requests.get(ARXIV_BASE, params=params, timeout=30)
        if resp.status_code != 200:
            return []
        root = ET.fromstring(resp.text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        papers = []
        for entry in root.findall("atom:entry", ns):
            id_elem = entry.find("atom:id", ns)
            if id_elem is None:
                continue
            arxiv_id = id_elem.text.split("/abs/")[-1].strip()
            title_elem = entry.find("atom:title", ns)
            summary_elem = entry.find("atom:summary", ns)
            title = (title_elem.text or "").strip().replace("\n", " ")
            summary = (summary_elem.text or "").strip().replace("\n", " ")
            authors = [
                (a.find("atom:name", ns).text or "")
                for a in entry.findall("atom:author", ns)
                if a.find("atom:name", ns) is not None
            ]
            published_elem = entry.find("atom:published", ns)
            published = (published_elem.text or "")[:10] if published_elem is not None else ""
            papers.append({
                "id": arxiv_id,
                "title": title,
                "summary": summary[:1000],
                "authors": authors,
                "link": f"https://arxiv.org/abs/{arxiv_id}",
                "source": "arxiv",
                "date": published,
            })
        return papers
    except Exception:
        return []
