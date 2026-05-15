---
layout: default
---

## 📅 2026-05-15

好的，作为一名运筹优化与人工智能交叉领域的资深审稿人，我已根据您提供的筛选原则，对上述论文列表进行了分析。

以下是为您筛选出的【高度相关】或【本质上涉及】“AI + 运筹优化”交叉领域的研究论文。

---

### FlowCompile: 一种用于结构化LLM工作流的优化编译器
- **英文标题**: FlowCompile: An Optimizing Compiler for Structured LLM Workflows
- **作者**: 未提供
- **核心贡献**: 将结构化LLM工作流的配置（模型选择、推理预算等）优化问题，形式化为一个**路由问题**，并提出一种成本感知的优化编译器来解决该组合优化难题。
- **实践价值**: 优化由多个LLM子代理构成的复杂业务流程，在保证任务质量的同时最小化延迟和计算成本。
- **OR 技术关键词**: 路由问题, 组合优化, 调度
- **论文链接**: https://huggingface.co/papers/2605.13647

---

### F-GRPO: 分解式分组相对策略优化，用于统一的候选生成与排序
- **英文标题**: F-GRPO: Factorized Group-Relative Policy Optimization for Unified Candidate Generation and Ranking
- **作者**: 未提供
- **核心贡献**: 将LLM生成与排序的任务建模为一个组合优化问题，并提出一种分解式的策略梯度方法（F-GRPO），以在巨大的组合输出空间中高效搜索。
- **实践价值**: 优化推荐系统、信息检索等需要对候选集进行生成、排序的流水线，提升整体效用。
- **OR 技术关键词**: 组合优化, 策略优化, 排序
- **论文链接**: https://huggingface.co/papers/2605.12995

---

### 从有限交互中通过文本-表格建模预测AI Agent的决策
- **英文标题**: Predicting Decisions of AI Agents from Limited Interaction through Text-Tabular Modeling
- **作者**: 未提供
- **核心贡献**: 提出一个用于预测未知AI Agent（如谈判机器人）下一决策的框架，将问题转化为基于少量交互历史的序列决策预测。
- **实践价值**: 可用于供应链谈判、采购协商等场景，帮助我方Agent预测对手行为，优化自身决策。
- **OR 技术关键词**: 决策制定, 预测, 博弈论
- **论文链接**: https://huggingface.co/papers/2605.12411

---

### 学习的探索：通过探索感知策略优化来扩展Agent推理
- **英文标题**: Learning to Explore: Scaling Agentic Reasoning via Exploration-Aware Policy Optimization
- **作者**: 未提供
- **核心贡献**: 提出一种探索感知的强化学习框架，使LLM Agent能自适应地在不确定性高时进行探索，高效地收集环境反馈以优化决策。核心是解决探索-利用困境。
- **实践价值**: 提升AI Agent在复杂、未知环境（如自动任务规划、机器人控制）中的决策质量和鲁棒性。
- **OR 技术关键词**: 强化学习, 探索-利用困境, 决策制定
- **论文链接**: https://huggingface.co/papers/2605.08978

---

### 从行动指导中学习Agent策略
- **英文标题**: Learning Agentic Policy from Action Guidance
- **作者**: 未提供
- **核心贡献**: 提出一种从人类的日常交互数据（行动指导）中学习Agent策略的方法，避免了从零开始的复杂探索，提高了强化学习的样本效率。
- **实践价值**: 用于训练需要复杂决策的AI Agent，如自动化生产调度、物流规划等，通过模仿人类专家的行动轨迹加速学习。
- **OR 技术关键词**: 强化学习, 策略学习, 模仿学习
- **论文链接**: https://huggingface.co/papers/2605.12004

---

### HAGE：通过RL驱动的加权图演化来驾驭Agent记忆
- **英文标题**: HAGE: Harnessing Agentic Memory via RL-Driven Weighted Graph Evolution
- **作者**: 未提供
- **核心贡献**: 将LLM Agent的记忆检索重新定义为在加权关系图上的顺序、查询条件遍历，并使用强化学习动态优化图的权重和检索路径，实现更高效的记忆访问。
- **实践价值**: 提升需要长期记忆和复杂推理的Agent性能，例如在供应链管理中进行历史数据追溯和决策分析。
- **OR 技术关键词**: 强化学习, 图优化, 路径规划
- **论文链接**: https://huggingface.co/papers/2605.09942

---

### 在线策略蒸馏中的外推悬崖问题（关于近确定性结构化输出）
- **英文标题**: The Extrapolation Cliff in On-Policy Distillation of Near-Deterministic Structured Outputs
- **作者**: 未提供
- **核心贡献**: 对在线策略蒸馏中的奖励外推行为进行理论分析，推导出一个封闭形式的“安全阈值”，用于防止模型在结构化输出任务（如调度、路径规划）上性能崩溃。
- **实践价值**: 为训练任务关键型决策模型（如生产排程、VRP求解器）提供稳定训练的理论指导。
- **OR 技术关键词**: 策略优化, 调度, 鲁棒性分析
- **论文链接**: https://huggingface.co/papers/2605.08737

---

### 对在线策略蒸馏的KL散度分析：使用控制变量基线
- **英文标题**: KL for a KL: On-Policy Distillation with Control Variate Baseline
- **作者**: 未提供
- **核心贡献**: 将在线策略蒸馏（OPD）形式化为策略梯度强化学习，并引入**控制变量**技术来稳定训练，解决了单样本蒙特卡洛估计方差高的问题。
- **实践价值**: 稳定地训练基于LLM的决策模型，为后续应用于调度、路由等任务提供更可靠的训练范式。
- **OR 技术关键词**: 强化学习, 策略梯度, 方差缩减
- **论文链接**: https://huggingface.co/papers/2605.07865

---
