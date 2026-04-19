import os
import requests
import openai
from datetime import date

# 1. 配置参数 (从 GitHub Secrets 获取)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com")
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
    你是一名运筹优化(OR)与人工智能交叉领域的资深审稿人。
    
    【任务】
    从以下论文列表中筛选出“核心研究内容”确实属于 AI+OR 交叉方向的论文。
    
    【判别标准 (以下三者满足其一方可入选)】
    1. 组合优化问题 (如 TSP, VRP, JSP, 库存控制, 设施选址) 结合了强化学习、图神经网络(GNN)或启发式算法。
    2. 数学规划算法 (如分支定界、割平面法) 被 AI 方法加速或替代。
    3. LLM 在工业供应链场景的决策逻辑、逻辑推理或数学建模中的具体落地。
    
    【严格排除】
    - 纯粹的 NLP 任务（如纯文本分类、情感分析）。
    - 纯粹的 LLM 训练技术（如模型对齐、长上下文窗口、纯 Agent 记忆优化等与运筹优化无直接关联的内容）。
    
    【输出格式】
    请严格按照以下格式，仅输出筛选后的论文，如果无相关论文则输出“今日无匹配研究”：
    
    ### [中文标题]
    - **作者**: [列出主要作者或团队]
    - **核心贡献**: [用一句话概括：算法上有什么创新？解决了什么难题？]
    - **实践价值**: [如果是工业界，它能解决什么具体问题？如：降低配送成本、提升库存预测精度等]
    - **OR 技术关键词**: [如：深度强化学习, 分支定界, VRP, 鲁棒优化]
    - **论文链接**: [https://huggingface.co/papers/{p['paper']['id']}]

    ---
    待分析论文列表:
    {context}
    """
    
    # 修改这里
    response = client.chat.completions.create(
        model="deepseek-chat",  # 改为服务商支持的模型名称
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
