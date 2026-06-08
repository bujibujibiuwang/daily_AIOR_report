# daily_AIOR_report

每日自动抓取多源论文，由 LLM 精选"AI + 运筹优化（OR）"交叉领域前沿研究，生成结构化中文报告，推送到网站 + 邮件。

🌐 **Next.js 网站 (Vercel)**: [daily-aior-report.vercel.app](https://daily-aior-report.vercel.app)

📄 **GitHub Pages 报告**: [bujibujibiuwang.github.io/daily_AIOR_report](https://bujibujibiuwang.github.io/daily_AIOR_report/)

> ⚠️ GitHub Pages 偶尔因部署失败而无法显示，建议两个地址均尝试访问，Vercel 版本更稳定。

---

## 🏗️ 整体架构

```
GitHub Actions (每天 09:00 北京时间)
        │
        ▼
    main.py  ←── 主入口
        │
        ├─ 1. 多源抓取
        │   ├── fetchers/hf_fetcher.py      → HuggingFace Daily Papers
        │   ├── fetchers/arxiv_fetcher.py   → arXiv (cs.AI + math.OC)
        │   └── fetchers/or_journals_fetcher.py     → OR期刊(Crossref: OR/MS)
        │
        ├─ 2. 去重 + 历史过滤
        │   └── core/storage.py → 读取 history.txt，过滤已处理论文
        │
        ├─ 3. 关键词预过滤
        │   └── core/analyzer.py → 仅保留命中 OR 关键词的论文
        │
        ├─ 4. LLM 分析 (DeepSeek)
        │   └── core/analyzer.py → 批量调用，返回中文标题/贡献/评分(0-10)
        │
        ├─ 5. 持久化存储
        │   ├── web/public/papers.json  ← Next.js 网站数据源
        │   ├── docs/index.md           ← GitHub Pages (Jekyll)
        │   └── history.txt             ← 已处理论文 ID 记录
        │
        ├─ 6. 邮件推送
        │   └── core/notifier.py → 163 SMTP_SSL 465 发送日报
        │
        └─ 7. Git 推送
            └── git push → 触发 Vercel / GitHub Pages 重新部署
```

---

## 🌐 前端（Next.js）运行机制

```
web/public/papers.json  (Python 每日更新)
        │
        ▼
web/app/page.tsx  (服务端读取 JSON，传给客户端)
        │
        ├── SearchWrapper.tsx  → 搜索框 + 来源筛选 + 按日期分组展示
        ├── PaperCard.tsx      → 每篇论文卡片（评分条、折叠详情）
        └── ChatBot.tsx        → 浮动聊天窗口
                │
                ▼
        web/app/api/chat/route.ts  (Next.js API Route)
                │
                ├── 关键词检索 papers.json，找出相关论文
                └── 把相关论文作为上下文，调用 DeepSeek 回答问题
```

---

## 🔄 一次完整运行的数据流

```
HF + arXiv + OR-Journal
    → 去重(~100篇)
    → 历史过滤(只留今日新论文)
    → 关键词过滤(只留Supply Chain + AI相关)
    → LLM打分(0-10，过滤<3分)
    → 写入 papers.json / index.md / history.txt
    → 发邮件
    → git push → Vercel 自动部署 → 网站更新
```

---

## 📁 目录结构

```
daily_AIOR_report/
├── main.py                     # 主入口（多源流水线）
├── hf_paper_bot.py             # 旧版备用（仅 HuggingFace）
├── history.txt                 # 已处理论文 ID 记录
├── requirements.txt            # Python 依赖
├── fetchers/
│   ├── hf_fetcher.py           # HuggingFace 抓取
│   ├── arxiv_fetcher.py        # arXiv 抓取
│   └── pwc_fetcher.py          # PapersWithCode 抓取
├── core/
│   ├── analyzer.py             # 关键词过滤 + LLM 分析评分
│   ├── storage.py              # papers.json / index.md 读写
│   └── notifier.py             # 邮件推送
├── docs/
│   └── index.md                # GitHub Pages 报告页
├── web/                        # Next.js 前端
│   ├── app/
│   │   ├── page.tsx            # 主页
│   │   ├── layout.tsx          # 全局布局
│   │   └── api/chat/route.ts   # RAG 聊天 API
│   ├── components/
│   │   ├── PaperCard.tsx       # 论文卡片
│   │   ├── SearchWrapper.tsx   # 搜索 + 过滤
│   │   └── ChatBot.tsx         # 浮动聊天机器人
│   └── public/
│       └── papers.json         # 论文数据（每日自动更新）
├── tests/
│   └── test_index_merge.py     # 单元测试
├── _config.yml                 # Jekyll 配置
└── .github/workflows/
    └── daily_report.yml        # GitHub Actions 定时任务
```

---

## ⚙️ 环境变量（GitHub Secrets）

| Secret 名称 | 必填 | 说明 |
|-------------|------|------|
| `OPENAI_API_KEY` | ✅ | DeepSeek / OpenAI API Key |
| `OPENAI_BASE_URL` | 可选 | 默认 `https://api.deepseek.com` |
| `OPENAI_MODEL` | 可选 | 默认 `deepseek-chat` |
| `ENABLE_EMAIL` | 可选 | 设为 `1` 开启邮件推送 |
| `SMTP_HOST` | 邮件必填 | `smtp.163.com` |
| `SMTP_PORT` | 邮件必填 | `465` |
| `SMTP_USER` | 邮件必填 | 你的 163 邮箱地址 |
| `SMTP_PASSWORD` | 邮件必填 | 163 邮箱**授权码**（非登录密码）|
| `SMTP_TLS` | 可选 | `0`（163 推荐 SSL） |
| `EMAIL_FROM` | 可选 | 发件人，默认同 `SMTP_USER` |
| `EMAIL_TO` | 邮件必填 | 收件人，多个用逗号分隔 |
| `OR_KEYWORDS` | 可选 | 自定义 OR 关键词，逗号分隔 |
| `STRICT_OR_FILTER` | 可选 | `1`=严格只过滤OR（默认），`0`=放宽 |

---

## �� 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export OPENAI_API_KEY=你的Key
export OPENAI_BASE_URL=https://api.deepseek.com

# 运行主流水线
python main.py

# 运行测试
python -m pytest
```

### 本地启动 Next.js 网站

```bash
cd web
npm install
npm run dev
# 访问 http://localhost:3000
```

---

## 🌍 部署到 Vercel（Next.js 网站）

1. 在 [vercel.com](https://vercel.com) 导入此仓库
2. **Root Directory** 设置为 `web`
3. Framework 选 `Next.js`
4. 添加环境变量：`OPENAI_API_KEY`、`OPENAI_BASE_URL`（可选）
5. 每次 GitHub Actions 推送 `papers.json` 后，Vercel 自动重新部署
