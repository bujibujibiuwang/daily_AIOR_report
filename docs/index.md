---
layout: default
---

## 📅 2026-05-13

好的，作为一名运筹优化与人工智能交叉领域的资深审稿人，我已根据您提供的筛选原则，对上述论文列表进行了严格分析。

经过筛选，以下论文符合“AI + 运筹优化”交叉领域的研究范畴，并具有较高的研究价值。

---

### [动态技能生命周期管理用于智能体强化学习]
- **英文标题**: Dynamic Skill Lifecycle Management for Agentic Reinforcement Learning
- **作者**: 未列出
- **核心贡献**: 提出了一种动态技能生命周期管理框架，通过强化学习优化技能的选择、获取和淘汰，解决了在有限模型容量下，技能库随任务变化而动态演化的决策优化问题。
- **实践价值**: 适用于需要持续学习和适应新任务的复杂AI Agent系统（如机器人操作、自动化工作流），通过优化技能集（可视为一种资源）的调度，提升长周期任务性能。
- **OR 技术关键词**: 强化学习, 调度, 资源分配, 决策优化
- **论文链接**: https://huggingface.co/papers/2605.10923

---

### [GridProbe: 面向长视频视觉语言模型的自适应测试时计算的后验探测]
- **英文标题**: GridProbe: Posterior-Probing for Adaptive Test-Time Compute in Long-Video VLMs
- **作者**: 未列出
- **核心贡献**: 提出GridProbe方法，将视频帧选择问题建模为一个在线优化问题，通过后验概率自适应地决定需要处理哪些帧，以最小化计算成本同时保证推理准确率。
- **实践价值**: 显著降低长视频分析（如监控、视频摘要）中的计算开销，通过在计算精度与资源消耗之间进行动态权衡，实现高效的“在环”决策。
- **OR 技术关键词**: 在线优化, 自适应调度, 计算资源分配
- **论文链接**: https://huggingface.co/papers/2605.10762

---

### [PaperFit: 基于视觉反馈的科学文档排版优化]
- **英文标题**: PaperFit: Vision-in-the-Loop Typesetting Optimization for Scientific Documents
- **作者**: 未列出
- **核心贡献**: 首创性地将排版问题形式化为一个视觉反馈驱动的优化问题，利用视觉语言模型（VLM）评估排版质量，并迭代优化布局参数，实现了从规则驱动到AI优化驱动的转变。
- **实践价值**: 自动化处理LaTeX文档中的浮动体位置、方程溢出、孤行等排版问题，显著减少作者手动调参的编译-检查循环，可直接应用于学术出版和文档自动化系统。
- **OR 技术关键词**: 数学规划, 优化, 启发式算法, 视觉反馈
- **论文链接**: https://huggingface.co/papers/2605.10341

---

### [LLiMba: 单GPU上处理撒丁语——使一个3B语言模型适应一种濒危罗曼语]
- **英文标题**: LLiMba: Sardinian on a Single GPU -- Adapting a 3B Language Model to a Vanishing Romance Language
- **作者**: 未列出
- **核心贡献**: 在严格的资源约束（单GPU）下，通过优化数据流程（预训练+微调）和模型选择，实现了高性能低资源语言模型的高效开发。这本质上是一个资源约束下的优化案例。
- **实践价值**: 为资源匮乏语言的数字化提供经济高效的解决方案，其“资源-性能”权衡优化的思路可推广至其他低资源NLP任务。
- **OR 技术关键词**: 资源约束优化, 生产调度, 数据优化
- **论文链接**: https://huggingface.co/papers/2605.09015

---

### [SplatWeaver: 学习分配高斯原语用于可泛化新视角合成]
- **英文标题**: SplatWeaver: Learning to Allocate Gaussian Primitives for Generalizable Novel View Synthesis
- **作者**: 未列出
- **核心贡献**: 提出一种学习驱动的高斯原语分配优化方法，打破了传统固定数量分配的局限，根据场景复杂度动态分配计算资源（高斯原语数量），实现了计算资源与视觉质量的最优平衡。
- **实践价值**: 用于3D场景重建与渲染，能有效减少平滑区域的计算浪费，同时保证复杂细节的精度，对VR/AR、自动驾驶仿真等领域的实时渲染有重要意义。
- **OR 技术关键词**: 资源分配, 优化, 调度
- **论文链接**: https://huggingface.co/papers/2605.07287

---

### [TMAS: 通过多智能体协同扩展测试时计算]
- **英文标题**: TMAS: Scaling Test-Time Compute via Multi-Agent Synergy
- **作者**: 未列出
- **核心贡献**: 提出一种多智能体协同推理框架，将推理过程建模为多个推理轨迹的协同优化与调度问题，通过智能体间的信息交换和任务分配，提升复杂推理任务的性能。
- **实践价值**: 提升大模型在数学、代码生成等复杂推理任务上的准确率和鲁棒性，其协同调度机制可视为一种新型的分布式计算资源调度方法。
- **OR 技术关键词**: 协同优化, 调度, 多智能体系统
- **论文链接**: https://huggingface.co/papers/2605.10344

---

### [SimWorld Studio: 使用进化编码代理为具身智能体学习自动生成环境]
- **英文标题**: SimWorld Studio: Automatic Environment Generation with Evolving Coding Agent for Embodied Agent Learning
- **作者**: 未列出
- **核心贡献**: 提出一种基于进化算法的环境自动生成框架，通过优化编码代理生成的3D环境代码，为具身智能体提供多样化、高难度的训练场景，解决了训练环境匮乏与单调的问题。
- **实践价值**: 自动生成针对性的机器人训练环境（如抓取、导航），大幅降低人工设计环境的成本，加速强化学习在机器人领域的应用。
- **OR 技术关键词**: 进化算法, 组合优化, 搜索, 生产调度（环境生成）
- **论文链接**: https://huggingface.co/papers/2605.09423

---

### [Dynamic Skill Lifecycle Management for Agentic Reinforcement Learning]
- **英文标题**: Dynamic Skill Lifecycle Management for Agentic Reinforcement Learning
- **作者**: 未列出
- **核心贡献**: 提出动态技能生命周期管理框架，将技能库的维护视为一个随时间变化的组合优化问题，通过强化学习学习技能的最优创建、调用和淘汰策略。
- **实践价值**: 适用于长期运行、任务不断变化的AI Agent，能够有效管理其“技能”这一核心资源，避免臃肿和失效，提升系统的可持续性。
- **OR 技术关键词**: 强化学习, 组合优化, 动态规划, 决策
- **论文链接**: https://huggingface.co/papers/2605.10923
