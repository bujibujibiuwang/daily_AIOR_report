import time
import requests
import xml.etree.ElementTree as ET
from datetime import date, timedelta

ARXIV_BASE = "https://export.arxiv.org/api/query"

_QUERY_TEMPLATE = (
    '(ti:"supply chain" OR ti:"demand forecast" OR ti:"demand prediction" '
    'OR ti:"inventory" OR ti:"safety stock" OR ti:"replenishment" '
    'OR ti:"inventory control" OR ti:"inventory management" '
    'OR ti:"inventory optimization" OR ti:"demand planning" '
    'OR ti:"supply chain risk" OR ti:"supply chain disruption" '
    'OR abs:"demand forecasting" OR abs:"inventory optimization" '
    'OR abs:"safety stock" OR abs:"replenishment policy" '
    'OR abs:"supply chain management" OR abs:"newsvendor" OR abs:"logistics") '
    'AND (cat:cs.LG OR cat:cs.AI OR cat:stat.ML OR cat:math.OC OR cat:econ.GN) '
    'AND submittedDate:[{start} TO {end}]'
)

_MAX_RETRIES = 5
_BACKOFF_SECONDS = [3, 6, 12, 24, 48]


def _build_query(days_back: int = 7) -> str:
    end_date = date.today()
    start_date = end_date - timedelta(days=days_back)
    # arXiv date format: YYYYMMDDHHMMSS (14 digits)
    start = start_date.strftime("%Y%m%d") + "000000"
    end = end_date.strftime("%Y%m%d") + "235959"
    return _QUERY_TEMPLATE.format(start=start, end=end)


def _request_with_retry(params: dict) -> str:
    headers = {
        "User-Agent": "daily_AIOR_report/1.0 (mailto:your_email@example.com)"
    }

    last_err = None
    for i in range(_MAX_RETRIES):
        try:
            resp = requests.get(ARXIV_BASE, params=params, headers=headers, timeout=30)

            if resp.status_code == 200:
                return resp.text

            # rate limit / transient errors
            if resp.status_code in (429, 500, 502, 503, 504):
                retry_after = resp.headers.get("Retry-After")
                wait = int(retry_after) if retry_after and retry_after.isdigit() else _BACKOFF_SECONDS[min(i, len(_BACKOFF_SECONDS) - 1)]
                print(f"[arXiv] HTTP {resp.status_code}, retry in {wait}s (attempt {i+1}/{_MAX_RETRIES})")
                time.sleep(wait)
                continue

            print(f"[arXiv] HTTP {resp.status_code}, no retry")
            return ""

        except requests.RequestException as e:
            last_err = e
            wait = _BACKOFF_SECONDS[min(i, len(_BACKOFF_SECONDS) - 1)]
            print(f"[arXiv] request error: {e}, retry in {wait}s (attempt {i+1}/{_MAX_RETRIES})")
            time.sleep(wait)

    if last_err:
        print(f"[arXiv] failed after retries: {last_err}")
    return ""


def fetch(max_results: int = 100, days_back: int = 7) -> list[dict]:
    query = _build_query(days_back=days_back)
    params = {
        "search_query": query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }

    xml_text = _request_with_retry(params)
    if not xml_text:
        return []

    try:
        root = ET.fromstring(xml_text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        papers = []

        for entry in root.findall("atom:entry", ns):
            id_elem = entry.find("atom:id", ns)
            if id_elem is None or not id_elem.text:
                continue

            arxiv_id = id_elem.text.split("/abs/")[-1].strip()

            title_elem = entry.find("atom:title", ns)
            summary_elem = entry.find("atom:summary", ns)
            published_elem = entry.find("atom:published", ns)

            title = ((title_elem.text or "") if title_elem is not None else "").strip().replace("\n", " ")
            summary = ((summary_elem.text or "") if summary_elem is not None else "").strip().replace("\n", " ")
            published = (published_elem.text or "")[:10] if published_elem is not None else ""

            authors = []
            for a in entry.findall("atom:author", ns):
                name_elem = a.find("atom:name", ns)
                if name_elem is not None and name_elem.text:
                    authors.append(name_elem.text.strip())

            papers.append(
                {
                    "id": arxiv_id,
                    "title": title,
                    "summary": summary[:2000],
                    "authors": authors,
                    "link": f"https://arxiv.org/abs/{arxiv_id}",
                    "source": "arxiv",
                    "date": published,
                }
            )

        return papers

    except ET.ParseError as e:
        print(f"[arXiv] XML parse error: {e}")
        return []