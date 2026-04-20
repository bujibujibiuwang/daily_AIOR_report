import os
import requests
import openai
from datetime import date

# 1. 配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com") # 默认设为 DeepSeek
HF_API_URL = "https://huggingface.co/api/daily_papers"
HISTORY_FILE = "history.txt"

def get_history():
    if not os.path.exists(HISTORY_FILE):
        return set()
    with open(HISTORY_FILE, "r") as f:
        return set(line.strip() for line in f)

def save_history(paper_ids):
    with open(HISTORY_FILE, "a") as f:
        for pid in paper_ids:
            f.write(f"{pid}\n")

def get_papers():
    try:
        resp = requests.get(HF_API_URL, timeout=30)
        return resp.json() if resp.status_code == 200 else []
    except Exception:
        return []

def analyze_papers(papers):
    history = get_history()
    new_papers = [p for p in papers if p['paper']['id'] not in history]
    
    if not new_papers:
        return "今日无新增 OR 相关研究", []

    client = openai.OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
    
    # 构建上下文
    context = ""
    for p in new_papers:
        context += f"\nTitle: {p['title']}\nSummary: {p['paper'].get('summary', '')[:500]}\nID: {p['paper']['id']}\n"

    prompt = f"""
    你是一名运筹优化(OR)与人工智能交叉领域的资深审稿人。请分析以下论文，筛选出真正属于 AI+OR 交叉方向的研究。
    【筛选标准】组合优化(TSP/VRP/JSP/库存)、数学规划加速、供应链决策、RL/GNN 在工业决策中的应用。
    【输出格式】
    ---
    ### [中文标题]
    - **作者**: [列出主要作者]
    - **核心贡献**: [算法创新点及解决的难题]
    - **实践价值**: [工业应用场景]
    - **OR 技术关键词**: [如: 深度强化学习, VRP, 鲁棒优化]
    - **论文链接**: [https://huggingface.co/papers/此处填写对应ID]
    
    如果今日没有符合标准的论文，请直接回复：今日无相关 OR 研究
    
    待分析论文列表:
    {context}
    """
    
    response = client.chat.completions.create(
        model="deepseek-chat", 
        messages=[{"role": "system", "content": "你是一个专业的学术助理，擅长运筹优化和AI交叉领域。"},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content, new_papers

def update_website(content, new_papers):
    if "今日无相关 OR 研究" in content or "今日无新增" in content:
        print(content)
        return

    # 写入 docs/index.md
    file_path = "docs/index.md"
    os.makedirs("docs", exist_ok=True)
    
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"\n---\n## 📅 {date.today()}\n\n{content}\n")

    # 更新历史记录
    save_history([p['paper']['id'] for p in new_papers])

    # 自动提交并推送
    os.system("git config user.name 'github-actions'")
    os.system("git config user.email 'github-actions@github.com'")
    os.system(f"git add {file_path} {HISTORY_FILE}")
    os.system("git commit -m 'Update daily report and history'")
    os.system("git push")
    print("网站更新推送成功！")

if __name__ == "__main__":
    raw_papers = get_papers()
    report, new_papers = analyze_papers(raw_papers)
    update_website(report, new_papers)
