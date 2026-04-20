import os
import requests
import openai
from datetime import date, datetime, timedelta

# 1. 配置项
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com")
HF_API_URL = "https://huggingface.co/api/daily_papers"
HISTORY_FILE = "history.txt"
INDEX_FILE = "docs/index.md"

def get_history():
    if not os.path.exists(HISTORY_FILE): return set()
    with open(HISTORY_FILE, "r") as f: return set(line.strip() for line in f)

def save_history(paper_ids):
    with open(HISTORY_FILE, "a") as f:
        for pid in paper_ids: f.write(f"{pid}\n")

def get_papers():
    try:
        resp = requests.get(HF_API_URL, timeout=30)
        return resp.json() if resp.status_code == 200 else []
    except: return []

def analyze_papers(papers):
    history = get_history()
    new_papers = [p for p in papers if p['paper']['id'] not in history]
    if not new_papers: return "今日无新增 OR 相关研究", []

    client = openai.OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
    context = "\n".join([f"Title: {p['title']}\nSummary: {p['paper'].get('summary', '')[:500]}\nID: {p['paper']['id']}\n" for p in new_papers])
    
    prompt = f"""
    你是一名运筹优化(OR)与人工智能交叉领域的资深审稿人。请分析以下论文，筛选出属于 AI+OR 交叉方向的研究。
    筛选标准：组合优化(TSP/VRP/JSP/库存)、数学规划加速、供应链决策、RL/GNN 在工业决策中的应用。
    输出格式(必须严格遵守)：
    ---
    ### [中文标题]
    - **作者**: [列出主要作者]
    - **核心贡献**: [一句话算法创新点]
    - **实践价值**: [工业应用场景]
    - **OR 技术关键词**: [如: 强化学习, VRP, 鲁棒优化]
    - **论文链接**: [https://huggingface.co/papers/{p['paper']['id']}]
    
    若无符合条件的论文，直接回复：今日无相关 OR 研究
    
    待分析论文:
    {context}
    """
    
    resp = client.chat.completions.create(model="deepseek-chat", messages=[{"role": "user", "content": prompt}])
    return resp.choices[0].message.content, new_papers

def update_website(content, new_papers):
    if "今日无相关 OR 研究" in content or "今日无新增" in content:
        print(content)
        return

    os.makedirs("docs", exist_ok=True)
    # 获取旧内容
    old_content = ""
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "r", encoding="utf-8") as f: old_content = f.read()

    # 构造新内容块
    new_block = f"\n---\n## 📅 {date.today()}\n\n{content}\n"
    
    # 简单的合并：保持头部，追加新内容到最前
    header = "---\nlayout: default\n---\n"
    body = old_content.replace(header, "").strip()
    
    # 拼接：Header + 新内容 + 旧内容
    final_content = header + new_block + "\n" + body
    
    with open(INDEX_FILE, "w", encoding="utf-8") as f: f.write(final_content)
    
    # 更新历史记录
    save_history([p['paper']['id'] for p in new_papers])

    # 提交推送
    os.system("git config user.name 'github-actions'")
    os.system("git config user.email 'github-actions@github.com'")
    os.system(f"git add {INDEX_FILE} {HISTORY_FILE}")
    os.system("git commit -m 'Update report'")
    os.system("git push")

if __name__ == "__main__":
    raw_papers = get_papers()
    report, new_papers = analyze_papers(raw_papers)
    update_website(report, new_papers)
