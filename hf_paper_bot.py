import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import openai

# 1. 配置参数
HF_API_URL = "https://huggingface.co/api/daily_papers"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
EMAIL_SENDER = 'zoeywang1220@163.com'    # 您的网易发件箱
EMAIL_RECEIVER = 'zoeywang1220@163.com'  # 您的接收箱
EMAIL_AUTH_CODE = os.getenv("EMAIL_AUTH_CODE") # 网易邮箱授权码

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
    
    # 提取标题和摘要进行分析
    context = "\n".join([f"- Title: {p['title']}\n  Abstract: {p['paper']['summary'][:400]}..." for p in papers])
    
    prompt = f"""
    你是一名资深的运筹优化(OR)算法工程师。请从以下论文中筛选出与以下领域相关的研究：
    1. 供应链管理、库存控制、路径规划(VRP)、生产调度(JSP)。
    2. 组合优化(Combinatorial Optimization)与深度学习/强化学习的结合。
    3. LLM/Agent 在逻辑推理、数学建模或工业流程中的应用。

    对于每一篇符合条件的论文，请严格按照以下 Markdown 格式输出：
    ### [中文标题简译]
    - **原标题**: [Original Title]
    - **核心技术**: [简述算法或模型创新点，如使用了什么强化学习架构或 Agent 模式]
    - **OR 应用场景**: [该研究可借鉴到供应链、库存或调度的哪些具体环节]

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

def send_email(content):
    if "今日无相关 OR 研究" in content:
        print("今日无相关 OR 论文，跳过发送。")
        return

    msg = MIMEText(content, 'markdown', 'utf-8')
    msg['Subject'] = Header("📅 今日 AI + OR 领域论文精选", 'utf-8')
    msg['From'] = f"AI Paper Bot <{EMAIL_SENDER}>"
    msg['To'] = EMAIL_RECEIVER

    try:
        with smtplib.SMTP_SSL("smtp.163.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_AUTH_CODE)
            server.sendmail(EMAIL_SENDER, [EMAIL_RECEIVER], msg.as_string())
        print("邮件发送成功！")
    except Exception as e:
        print(f"发送失败: {e}")

if __name__ == "__main__":
    raw_papers = get_papers()
    report = analyze_papers(raw_papers)
    send_email(report)
