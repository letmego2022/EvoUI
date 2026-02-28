# EvoUI — AI-Driven Testing Platform for QA Teams

EvoUI is an AI-driven testing platform designed to **assist QA engineers** across the full testing lifecycle: test case authoring, API testing, and UI automation.

Its core differentiator is a **process-first memory model**: EvoUI stores and retrieves knowledge from critical workflow checkpoints (key nodes), then uses agent-based orchestration to execute and verify end-to-end scenarios more reliably.

---

## What EvoUI Solves

Traditional automation often breaks when UI structure changes, APIs evolve, or business flows become complex. EvoUI improves resilience by combining:

- **Workflow memory** (not just single-step selectors)
- **Context-aware reuse** of validated actions
- **Agent orchestration** for multi-stage execution and recovery
- **Step-level and node-level verification** for trustworthy outcomes

---

## Core Capabilities

### 1) AI-Assisted Test Case Authoring
- Generate and refine test cases from requirements and business scenarios.
- Standardize cases with reusable templates and parameterized steps.
- Capture critical process checkpoints as reusable test memory.

### 2) API Testing
- Support endpoint-level validation with parameter and assertion orchestration.
- Enable chaining across dependent API calls as part of a full workflow.
- Reuse memory from previous successful executions to improve stability.

### 3) UI Automation
- Execute interaction steps such as click, input, select, scroll, and keyboard events.
- Apply visual assistance (SoM-style semantic overlays) when DOM-based actions are uncertain.
- Auto-fallback from memory-driven action to visual-driven action when needed.

### 4) Process Memory: Store & Retrieve by Key Nodes
- Persist successful operational paths around **critical workflow nodes**.
- Retrieve the most relevant memory based on context, intent, and confidence.
- Support parameterized reuse (`reuse_modified`) for similar but not identical tasks.
- Track operation-level outcomes (success/failure/last used) for governance.

### 5) Agent Workflow Orchestration
- Coordinate multiple agents/tools across planning, execution, and validation.
- Dynamically select next actions based on current state and global goal.
- Handle exception branches (e.g., popup, hidden element, unexpected redirect).

### 6) Verification and Quality Gates
- Validate each action within a step before marking the step complete.
- Add consistency checks for state transitions and input correctness.
- Generate traceable execution reports for audit and debugging.

---

## How EvoUI Works (High-Level)

```text
Business Requirement / QA Scenario
        │
        ▼
AI-Assisted Test Design (Case + API + UI)
        │
        ▼
Workflow Node Memory Layer
- Store key-node actions
- Retrieve best-fit memory
- Parameterized reuse
        │
        ▼
Agent Orchestration Engine
- Plan
- Execute
- Recover
        │
        ▼
Execution Layer (API + UI)
- Memory-driven first
- Visual fallback when needed
        │
        ▼
Verification & Report
- Step/node validation
- Result traceability
```

---

## Typical Use Cases

- Regression testing of core business processes
- Cross-page end-to-end workflows with conditional branches
- Hybrid API + UI validation in one orchestrated run
- Rapid onboarding for QA members with reusable process memory

---

## Positioning

EvoUI is not just a script runner. It is a **QA co-pilot platform** that combines:
- AI-assisted design,
- memory-centric execution,
- and agent-based orchestration,

to help testing teams deliver faster, more stable, and more maintainable automation.


截图：
登录页面：模仿cmd 风格偏向于测试人员（偏向于开发）
<img width="1358" height="919" alt="image" src="https://github.com/user-attachments/assets/92ac4f5c-99d4-4018-b9fc-75ffc7f4d5ab" />
仪表盘：测试方面：测试项目管理 ：测试domain（会包含多个项目）管理  AI方面：agent入口
<img width="2478" height="1175" alt="image" src="https://github.com/user-attachments/assets/3bae5bb1-8232-4137-bb86-51d1da53826e" />
项目内 userstory管理：目前是手动添加 类型有 PAGE FUNCTION  FLOW API  等
<img width="2118" height="1077" alt="image" src="https://github.com/user-attachments/assets/510f0860-ca1e-47ac-824a-9ef250817522" />
用例生成：目前是UI的页面元素，采用AI BA分析提取结构化数据后用用例生成器生成   其他的暂时使用纯AI进行生成
<img width="2059" height="1057" alt="image" src="https://github.com/user-attachments/assets/7f7d9c8f-715f-45aa-9901-97cb1447b204" />
接口自动化测试：AI读取项目内API标签的userstory生成用例，支持对话方式修改脚本 以及 AI 主动修改脚本，会保留偏向性记忆
<img width="2101" height="1083" alt="image" src="https://github.com/user-attachments/assets/3fe2c388-cd0a-4d98-9b66-2b026486f0c5" />
AI agent
<img width="2079" height="1059" alt="image" src="https://github.com/user-attachments/assets/45217d70-4e61-4b77-ac77-b98277f733fd" />
agent流程编排
<img width="2096" height="954" alt="image" src="https://github.com/user-attachments/assets/f9dc035e-d667-4a37-9dbb-bd2ea04c9e9e" />
UI 自动化执行机器人，包含报告，记忆处理等等
<img width="2165" height="1072" alt="image" src="https://github.com/user-attachments/assets/c91e6534-fa42-47ba-9cd8-ac250fd85c3e" />




