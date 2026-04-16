import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import openai

# 1. 配置参数 (从环境变量读取)
HF_API_URL = "https://huggingface.co/api/daily_papers"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS") # Google 应用专用密码

def get_papers():
    resp = requests.get(HF_API_URL)
    return resp.json() if resp.status_code == 200 else []

def analyze_papers(papers):
    if not papers: return "今日 Hugging Face 无更新。"
    
    client = openai.OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
    
    # 构建精简的待分析文本
    context = "\n".join([f"- Title: {p['title']}\n  Abstract: {p['paper']['summary'][:300]}..." for p in papers])
    
    prompt = f"""
    你是一名运筹优化(OR)与供应链专家。请从以下论文中筛选出与：
    1. 供应链、库存控制、路径优化(VRP)、排产调度(JSP)
    2. 强化学习(RL)在决策中的应用
    3. LLM Agent 解决数学推理或工业流程
    相关的研究。

    请为每篇相关论文输出：
    ### [中文标题] 
    - **原标题**: [Original Title]
    - **核心突破**: [简要说明算法或模型改进]
    - **OR启发**: [对库存控制、仿真或建模的具体价值]
    
    如果没有相关论文，只需回复“今日无相关研究”。

    待处理论文：
    {context}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini", # 建议使用 mini 版本降低成本
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def send_email(content):
    if "今日无相关研究" in content:
        print("无相关研究，取消邮件发送。")
        return

    msg = MIMEText(content, 'markdown', 'utf-8')
    msg['Subject'] = Header("📅 今日 AI + OR 论文速递", 'utf-8')
    msg['From'] = f"AI Bot <{GMAIL_USER}>"
    msg['To'] = GMAIL_USER

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_PASS)
        server.sendmail(GMAIL_USER, [GMAIL_USER], msg.as_string())

if __name__ == "__main__":
    papers = get_papers()
    report = analyze_papers(papers)
    send_email(report)
