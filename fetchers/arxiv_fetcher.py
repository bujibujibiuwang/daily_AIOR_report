import requests
import xml.etree.ElementTree as ET


ARXIV_BASE = "http://export.arxiv.org/api/query"

_QUERY = (
    '(ti:"supply chain" OR ti:"vehicle routing" OR ti:"VRP" OR ti:"TSP" '
    'OR ti:"scheduling" OR ti:"logistics" OR ti:"inventory" '
    'OR ti:"operations research" OR ti:"combinatorial optimization" '
    'OR abs:"vehicle routing" OR abs:"operations research" '
    'OR abs:"combinatorial optimization" OR abs:"integer programming") '
    'AND (cat:cs.AI OR cat:math.OC OR cat:cs.LG OR cat:econ.GN)'
)


def fetch(max_results: int = 50) -> list[dict]:
    params = {
        "search_query": _QUERY,
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
            papers.append({
                "id": arxiv_id,
                "title": title,
                "summary": summary[:1000],
                "authors": authors,
                "link": f"https://arxiv.org/abs/{arxiv_id}",
                "source": "arxiv",
            })
        return papers
    except Exception:
        return []
