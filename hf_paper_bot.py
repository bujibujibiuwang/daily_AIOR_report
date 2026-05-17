import os
import requests
import openai
import smtplib
from email.message import EmailMessage
from datetime import date, datetime, timedelta

# 1. 配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "deepseek-chat")
HF_API_URL = "https://huggingface.co/api/daily_papers"
HISTORY_FILE = "history.txt"
INDEX_FILE = "docs/index.md"
HISTORY_RETENTION_DAYS = 30

NO_NEW_MARKER = "今日无新增 OR 相关研究"
DEFAULT_OR_KEYWORDS = [
    "SUPPLY CHAIN",
    "INVENTORY",
    "FORECAST",
    "OPTIMIZATION",
    "ROUTE",
    "SCHEDULING",
    "PRODUCTION",
    "TSP",
    "VRP",
    "JSP",
    "LOGISTICS",
    "MATHEMATICAL PROGRAMMING",
    "DECISION MAKING",
    "ASSIGNMENT",
    "PLANNING",
    "OPERATIONS RESEARCH",
    "NETWORK FLOW",
]
DEFAULT_AI_KEYWORDS = [
    "MACHINE LEARNING",
    "DEEP LEARNING",
    "REINFORCEMENT LEARNING",
    "LLM",
    "LARGE LANGUAGE MODEL",
    "NEURAL",
    "AI",
]

def get_history():
    if not os.path.exists(HISTORY_FILE):
        return set()
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def get_papers():
    try:
        resp = requests.get(HF_API_URL, timeout=30)
        return resp.json() if resp.status_code == 200 else []
    except Exception:
        return []


def normalize_paper(paper):
    base = paper.get("paper", {}) if isinstance(paper, dict) else {}
    paper_id = base.get("id") or paper.get("id")
    title = base.get("title") or paper.get("title") or ""
    summary = base.get("summary") or paper.get("summary") or ""
    authors = base.get("authors") or paper.get("authors") or []
    link = f"https://huggingface.co/papers/{paper_id}" if paper_id else ""
    return {
        "id": paper_id,
        "title": title,
        "summary": summary,
        "authors": authors,
        "link": link,
    }


def build_prompt(context):
    return f"""
你是一名运筹优化(OR)与人工智能交叉领域的资深审稿人。

【任务】分析以下论文，筛选出属于“AI + 运筹优化”交叉领域的高质量研究。

【强制筛选原则】
只要论文标题或摘要中包含以下关键词之一，即视为【高度相关】，必须进入分析列表：
- 关键词包括: SUPPLY CHAIN, INVENTORY, FORECAST, OPTIMIZATION, ROUTE, SCHEDULING, PRODUCTION, TSP, VRP, JSP, LOGISTICS, MATHEMATICAL PROGRAMMING, DECISION MAKING。

如果论文未出现上述关键词，但其内容本质上涉及算法优化、复杂系统决策或启发式算法改进，也请纳入。

【输出格式 (严格遵守)】
---
### [中文标题]
- **英文标题**: [填写原论文英文标题]
- **作者**: [列出主要作者]
- **核心贡献**: [一句话算法创新点]
- **实践价值**: [工业应用场景]
- **OR 技术关键词**: [如: 强化学习, VRP, 鲁棒优化]
- **论文链接**: [直接抄写上面提供的链接]
---

(如果不属于以上任何范畴，请跳过，不要输出任何内容)

待分析论文列表:
{context}
"""


def parse_keywords(raw_value, fallback):
    if not raw_value:
        return fallback
    keywords = [kw.strip() for kw in raw_value.split(",") if kw.strip()]
    return keywords if keywords else fallback


def keyword_hits(text, keywords):
    if not text:
        return []
    upper_text = text.upper()
    return [kw for kw in keywords if kw in upper_text]


def filter_relevant_papers(papers):
    or_keywords = parse_keywords(os.getenv("OR_KEYWORDS"), DEFAULT_OR_KEYWORDS)
    ai_keywords = parse_keywords(os.getenv("AI_KEYWORDS"), DEFAULT_AI_KEYWORDS)
    strict_mode = os.getenv("STRICT_OR_FILTER", "1") == "1"

    filtered = []
    for paper in papers:
        text = f"{paper['title']} {paper['summary']}"
        or_hits = keyword_hits(text, or_keywords)
        ai_hits = keyword_hits(text, ai_keywords)
        if strict_mode:
            if or_hits:
                filtered.append(paper)
        else:
            if or_hits or ai_hits:
                filtered.append(paper)
    return filtered

def analyze_papers(papers):
    history = get_history()
    normalized = [normalize_paper(p) for p in papers]
    new_papers = [p for p in normalized if p["id"] and p["id"] not in history]

    if not new_papers:
        return NO_NEW_MARKER, []

    filtered_papers = filter_relevant_papers(new_papers)
    if not filtered_papers:
        return NO_NEW_MARKER, []

    if not OPENAI_API_KEY:
        raise RuntimeError("缺少 OPENAI_API_KEY，无法生成报告")

    client = openai.OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)

    context = ""
    for p in filtered_papers:
        summary = (p["summary"] or "")[:500]
        context += (
            f"\n标题: {p['title']}\n"
            f"摘要: {summary}\n"
            f"链接: {p['link']}\n---\n"
        )

    prompt = build_prompt(context)

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip(), filtered_papers


def merge_index_content(existing_content, new_block, today):
    header = "---\nlayout: default\n---\n"
    content = existing_content.replace(header, "").strip()
    blocks = []
    if content:
        if content.startswith("## 📅 "):
            content = content[len("## 📅 "):]
        chunks = content.split("\n## 📅 ")
        for chunk in chunks:
            chunk = chunk.strip()
            if chunk:
                blocks.append(chunk)
    blocks.insert(0, new_block.strip())
    threshold_date = today - timedelta(days=HISTORY_RETENTION_DAYS)
    valid_blocks = []

    for block in blocks:
        date_str = block[:10]
        try:
            block_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            continue
        if block_date >= threshold_date:
            valid_blocks.append(block)

    combined = "\n## 📅 ".join(valid_blocks)
    return f"{header}\n## 📅 {combined}" if combined else header


def build_email_message(subject, content, sender, recipients):
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = ", ".join(recipients)
    message.set_content(content)
    return message


def send_email_notification(content, today):
    if os.getenv("ENABLE_EMAIL", "0") != "1":
        return

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("EMAIL_FROM") or smtp_user
    recipients = [addr.strip() for addr in os.getenv("EMAIL_TO", "").split(",") if addr.strip()]
    if not smtp_host or not sender or not recipients:
        raise RuntimeError("缺少 SMTP_HOST / EMAIL_FROM / EMAIL_TO 配置")

    subject = f"AI+OR 每日报告 {today}"
    message = build_email_message(subject, content, sender, recipients)

    use_tls = os.getenv("SMTP_TLS", "1") == "1"
    if use_tls:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)
            server.send_message(message)
    else:
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)
            server.send_message(message)

def update_website(content, new_papers):
    if NO_NEW_MARKER in content:
        print(content)
        content = NO_NEW_MARKER

    os.makedirs("docs", exist_ok=True)
    today = date.today()
    today_str = str(today)

    new_block = f"{today_str}\n\n{content}\n"

    existing = ""
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            existing = f.read()

    final_content = merge_index_content(existing, new_block, today)
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(final_content)

    send_email_notification(content, today)

    # 5. 更新历史记录与推送
    if new_papers:
        with open(HISTORY_FILE, "a", encoding="utf-8") as f:
            for p in new_papers:
                f.write(f"{p['id']}\n")

    os.system("git config user.name 'github-actions'")
    os.system("git config user.email 'github-actions@github.com'")
    os.system(f"git add {INDEX_FILE} {HISTORY_FILE}")
    os.system("git commit -m 'Update report and history'")
    os.system("git push")

if __name__ == "__main__":
    raw_papers = get_papers()
    report, new_papers = analyze_papers(raw_papers)
    update_website(report, new_papers)
