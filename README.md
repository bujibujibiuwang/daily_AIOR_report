# daily_AIOR_report

每日抓取 Hugging Face Daily Papers，并由 LLM 生成“AI + 运筹优化（OR）”交叉领域精选报告，输出到 `docs/index.md`（适合 GitHub Pages）。

## 功能概览
- 自动拉取 Hugging Face Daily Papers
- 过滤历史论文（避免重复）
- 调用 LLM 生成结构化中文报告
- 按日期归档到 `docs/index.md`，默认保留最近 30 天

## 环境变量
- `OPENAI_API_KEY`：必填
- `OPENAI_BASE_URL`：可选，默认 `https://api.deepseek.com`
- `OPENAI_MODEL`：可选，默认 `deepseek-chat`
- `OR_KEYWORDS`：可选，逗号分隔的 OR 关键词列表（覆盖默认值）
- `AI_KEYWORDS`：可选，逗号分隔的 AI 关键词列表（覆盖默认值）
- `STRICT_OR_FILTER`：可选，默认 `1`（仅命中 OR 关键词才进入分析）；设为 `0` 时放宽为 OR 或 AI 命中
- `ENABLE_EMAIL`：可选，设为 `1` 开启邮件推送
- `SMTP_HOST`：SMTP 服务地址
- `SMTP_PORT`：SMTP 端口（默认 587）
- `SMTP_USER`：SMTP 用户名（可选）
- `SMTP_PASSWORD`：SMTP 密码（可选）
- `SMTP_TLS`：是否使用 STARTTLS（默认 `1`，设为 `0` 使用 SSL）
- `EMAIL_FROM`：发件人地址（可选，默认 `SMTP_USER`）
- `EMAIL_TO`：收件人列表，逗号分隔

## 本地运行
1. 安装依赖
2. 设置环境变量
3. 运行脚本

可直接运行：`python hf_paper_bot.py`

## 目录结构
- `hf_paper_bot.py`：主脚本
- `history.txt`：已处理论文 id
- `docs/index.md`：输出的报告页面