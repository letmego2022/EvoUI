# EvoUI —— 面向测试团队的 AI 驱动测试平台

EvoUI 是一个专为**测试人员/QA 团队**打造的 AI 驱动测试平台，覆盖测试生命周期中的关键环节：**测试用例编写、接口测试、UI 自动化**。

EvoUI 的核心优势是“**流程优先的记忆机制**”：围绕关键流程节点（Key Nodes）进行记忆存储与读取，并通过 Agent 流程编排实现稳定、可恢复、可追踪的端到端测试执行。

---

## EvoUI 解决什么问题

传统自动化常见痛点：
- 页面结构变化导致脚本易碎；
- 接口依赖链复杂，编排成本高；
- 业务流程长且分支多，失败后难以恢复；
- 自动化结果缺乏过程可解释性。

EvoUI 通过以下方式提升稳定性与效率：
- **流程记忆**（不仅是单元素定位）
- **上下文感知复用**（按场景调用历史成功动作）
- **Agent 编排**（规划-执行-纠偏-验证）
- **节点级验证**（关键节点可追溯）

---

## 核心能力

### 1）AI 辅助测试用例编写
- 根据需求或业务场景生成并优化测试用例。
- 通过模板与参数化步骤提升用例标准化程度。
- 将关键流程节点沉淀为可复用的测试记忆资产。

### 2）接口测试（API Testing）
- 支持接口参数、断言与依赖调用的编排。
- 支持多接口链路验证，适配真实业务流程。
- 复用历史成功执行记忆，提升回归稳定性。

### 3）UI 自动化
- 覆盖 click/input/select/scroll/keyboard 等常见交互动作。
- 在 DOM 不稳定或元素识别不确定时，启用 SoM 类语义视觉辅助。
- 记忆驱动执行失败时，自动切换视觉兜底执行。

### 4）关键节点流程记忆：存储与读取
- 围绕**关键流程节点**持久化成功动作路径。
- 按上下文、目标与置信度检索最优记忆。
- 支持参数化复用（`reuse_modified`），适配相似场景。
- 记录动作级成功/失败/最近使用，支持治理与迭代。

### 5）Agent 流程编排
- 多 Agent / 多工具协同完成规划、执行与验证。
- 根据当前状态动态决策下一步动作。
- 可处理弹窗、中断、隐藏元素、异常跳转等分支场景。

### 6）验证与质量闸门
- 每一步中的每个动作都可验证后再判定完成。
- 校验状态翻转与输入一致性，避免“执行了但不正确”。
- 生成可追溯执行报告，便于审计与定位问题。

---

## EvoUI 工作方式（高层流程）

```text
业务需求 / 测试场景
        │
        ▼
AI 辅助测试设计（用例 + API + UI）
        │
        ▼
流程节点记忆层
- 关键节点存储
- 场景化检索
- 参数化复用
        │
        ▼
Agent 编排引擎
- 规划
- 执行
- 纠偏恢复
        │
        ▼
执行层（API + UI）
- 优先记忆驱动
- 必要时视觉兜底
        │
        ▼
验证与报告
- 步骤/节点校验
- 结果可追溯
```

---

## 典型应用场景

- 核心业务流程回归测试
- 跨页面、跨系统的端到端流程验证
- API + UI 混合链路的一体化测试
- 新成员快速接入（复用团队沉淀的流程记忆）

---

## 平台定位

EvoUI 不只是一个脚本执行器，而是一个面向测试团队的 **AI 协作平台（QA Co-pilot）**：
- 前置提升用例设计效率，
- 中段保障执行稳定性，
- 后置提供可解释、可追溯的结果。

帮助团队在保证质量的前提下，更快地交付自动化能力。

---

## 产品界面速览（中英双语 + 左右时间线）

> 可以。下面改成“左图 / 阶段节点 / 右图”的时间线排布，阅读时会更像流程推进。

| 左侧视图 | 时间线节点 | 右侧视图 |
|---|---|---|
| <img width="360" alt="EvoUI 登录页" src="https://github.com/user-attachments/assets/92ac4f5c-99d4-4018-b9fc-75ffc7f4d5ab" /> | **Phase 01：进入平台**<br/>中文：登录后进入统一仪表盘，快速查看项目进度、测试资产与执行入口，建立完整测试上下文。<br/>EN: Sign in and land on the dashboard to establish project context. | <img width="360" alt="EvoUI 仪表盘" src="https://github.com/user-attachments/assets/3bae5bb1-8232-4137-bb86-51d1da53826e" /> |
| <img width="360" alt="EvoUI User Story 管理" src="https://github.com/user-attachments/assets/510f0860-ca1e-47ac-824a-9ef250817522" /> | **Phase 02：沉淀需求**<br/>中文：维护 Story 结构，沉淀为可执行测试资产。<br/>EN: Curate stories and structure requirements into executable assets. | <img width="360" alt="EvoUI 用例生成" src="https://github.com/user-attachments/assets/7f7d9c8f-715f-45aa-9901-97cb1447b204" /> |
| <img width="360" alt="EvoUI 接口自动化" src="https://github.com/user-attachments/assets/3fe2c388-cd0a-4d98-9b66-2b026486f0c5" /> | **Phase 03：生成与执行**<br/>中文：自动生成脚本，并进入 Agent 协同执行。<br/>EN: Generate scripts and move into agent-driven execution. | <img width="360" alt="EvoUI AI Agent" src="https://github.com/user-attachments/assets/45217d70-4e61-4b77-ac77-b98277f733fd" /> |
| <img width="360" alt="EvoUI Agent 流程编排" src="https://github.com/user-attachments/assets/f9dc035e-d667-4a37-9dbb-bd2ea04c9e9e" /> | **Phase 04：编排优化闭环**<br/>中文：流程编排、UI 执行、报告回流，形成记忆优化闭环。<br/>EN: Orchestrate flows, execute UI tasks, and feed reports back into memory optimization. | <img width="360" alt="EvoUI UI 自动化机器人" src="https://github.com/user-attachments/assets/c91e6534-fa42-47ba-9cd8-ac250fd85c3e" /> |

### 一图看完整链路（Timeline Summary）

`登录/仪表盘 → Story 管理 → 用例/API 生成 → Agent 编排执行 → UI 报告验证 → 记忆回流优化`
