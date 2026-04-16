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
EMAIL_AUTH_CODE = os.getenv("EMAIL_AUTH_CODE") # 网易邮箱 16 位授权码

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

    对于每一篇符合条件的论文，请严格按照以下格式输出：
    ### [中文标题简译]
    - **原标题**: [Original Title]
    - **核心技术**: [简述算法创新点
