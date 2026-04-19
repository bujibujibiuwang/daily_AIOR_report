import os
import requests
import openai
from datetime import date

# 1. 配置参数 (从 GitHub Secrets 获取)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
HF_API_URL = "https://huggingface.co/api/daily_papers"

def get_papers():
    try:
        resp = requests.get(HF_API_URL, timeout=30)
        return resp.json() if resp.status_code == 200 else []
    except Exception as e:
        print(f"抓取 HF 失败: {e}")
        return []

def analyze_papers(papers):
    if not papers: return "今日 Hugging Face 无更新。"
    
    client = openai.OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
    context = "\n".join([f"- Title: {p['title']}\n  Abstract: {p['paper']['summary'][:400]}..." for p in papers])
    
    prompt = f"""
    你是一名资深的运筹优化(OR)算法工程师。请从以下论文中筛选出与以下领域相关的研究：
    1. 供应链管理、库存控制、路径规划(VRP)、生产调度(JSP)。
    2. 组合优化与深度学习/强化学习的结合。
    3. LLM/Agent 在逻辑推理、数学建模或工业流程中的应用。

    对于每一篇符合条件的论文，请严格按照以下格式输出：
    ### [中文标题简译]
    - **原标题**: {p['paper']['title'] if 'p' in locals() else 'N/A'}
    - **核心技术**: [简述算法创新点]
    - **OR 应用场景**: [该研究可借鉴的具体环节]

    如果今日所有论文都与 OR 领域无关，请只回复一行字：“今日无相关 OR 研究”。

    待分析论文：
    {context}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini", 
        messages=[{"role": "system", "content": "你是一个专业的学术助理，擅长运筹优化和AI交叉领域。"},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def update_website(content):
    if "今日无相关 OR 研究" in content:
        print("今日无相关论文，跳过更新。")
        return

    # 写入文件
    file_path = "docs/index.md"
    # 如果文件不存在，先创建
    os.makedirs("docs", exist_ok=True)
    
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"\n---\n## {date.today()}\n\n{content}\n")

    # 执行 Git 操作自动推送到 GitHub
    os.system("git config user.name 'github-actions'")
    os.system("git config user.email 'github-actions@github.com'")
    os.system("git add docs/index.md")
    os.system("git commit -m 'Update daily OR paper report'")
    os.system("git push")
    print("网站更新推送成功！")

if __name__ == "__main__":
    raw_papers = get_papers()
    report = analyze_papers(raw_papers)
    update_website(report)
