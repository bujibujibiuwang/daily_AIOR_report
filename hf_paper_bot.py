import os
import requests
import openai
from datetime import date, datetime, timedelta

# 1. 配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com")
HF_API_URL = "https://huggingface.co/api/daily_papers"
HISTORY_FILE = "history.txt"
INDEX_FILE = "docs/index.md"

def get_history():
    if not os.path.exists(HISTORY_FILE): return set()
    with open(HISTORY_FILE, "r") as f: return set(line.strip() for line in f)

def get_papers():
    try:
        resp = requests.get(HF_API_URL, timeout=30)
        return resp.json() if resp.status_code == 200 else []
    except: return []

def analyze_papers(papers):
    history = get_history()
    new_papers = [p for p in papers if p['paper']['id'] not in history]
    
    if not new_papers:
        return "今日无新增 OR 相关研究", []

    client = openai.OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
    
    context = ""
    for p in new_papers:
        context += f"\n标题: {p['title']}\n摘要: {p['paper'].get('summary', '')[:500]}\n链接: https://huggingface.co/papers/{p['paper']['id']}\n---\n"

    prompt = f"""
    你是一名运筹优化(OR)与人工智能交叉领域的资深审稿人。
    
    【任务】分析以下论文，筛选出属于“AI + 运筹优化”交叉领域的高质量研究。
    
    【强制筛选原则】
    只要论文标题或摘要中包含以下关键词之一，即视为【高度相关】，必须进入分析列表：
    - 关键词包括: SUPPLY CHAIN, INVENTORY, FORECAST, OPTIMIZATION, ROUTE, SCHEDULING, PRODUCTION, TSP, VRP, JSP, LOGISTICS, MATHEMATICAL PROGRAMMING, DECISION MAKING。
    
    如果论文未出现上述关键词，但其内容本质上涉及算法优化、复杂系统决策或启发式算法改进，也请纳入。
    
    【输出格式 (严格遵守)】
    ---
    ### [中文标题]
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
    
    response = client.chat.completions.create(
        model="deepseek-chat", 
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content, new_papers

def update_website(content, new_papers):
    if "今日无新增" in content or "今日无相关 OR 研究" in content:
        print(content)
        return

    os.makedirs("docs", exist_ok=True)
    header = "---\nlayout: default\n---\n"
    today_str = str(date.today())
    # 组合新块：包含日期标题和内容
    new_block = f"{today_str}\n\n{content}\n"
    
    # 1. 获取旧内容
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            full_content = f.read().replace(header, "").strip()
    else:
        full_content = ""

    # 2. 合并：新内容 + 旧内容
    combined_content = new_block + ("\n## 📅 " + full_content if full_content else "")
    
    # 3. 按日期过滤 (保留30天)
    blocks = combined_content.split("\n## 📅 ")
    valid_blocks = [blocks[0]] 
    threshold_date = date.today() - timedelta(days=30)
    
    for i in range(1, len(blocks)):
        try:
            date_str = blocks[i][:10]
            if datetime.strptime(date_str, "%Y-%m-%d").date() >= threshold_date:
                valid_blocks.append(blocks[i])
        except: continue
            
    # 4. 重新拼装
    final_content = header + "\n## 📅 ".join(valid_blocks)
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(final_content)
    
    # 5. 更新历史记录与推送
    with open(HISTORY_FILE, "a") as f:
        for p in new_papers: f.write(f"{p['paper']['id']}\n")

    os.system("git config user.name 'github-actions'")
    os.system("git config user.email 'github-actions@github.com'")
    os.system(f"git add {INDEX_FILE} {HISTORY_FILE}")
    os.system("git commit -m 'Update report and history'")
    os.system("git push")

if __name__ == "__main__":
    raw_papers = get_papers()
    report, new_papers = analyze_papers(raw_papers)
    update_website(report, new_papers)
