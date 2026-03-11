# EvoUI — AI-Driven Testing Platform for QA Teams

EvoUI is an AI-driven testing platform designed to **assist QA engineers** across the full testing lifecycle: test case authoring, API testing, and UI automation.

Its core differentiator is a **process-first memory model**: EvoUI stores and retrieves knowledge from critical workflow checkpoints (key nodes), then uses agent-based orchestration to execute and verify end-to-end scenarios more reliably.
仪表盘页面
<img width="2492" height="1155" alt="image" src="https://github.com/user-attachments/assets/9a22b036-2684-4814-aeaf-25e5f3690b8d" />

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

## MemoryAgent 功能介绍

MemoryAgent 是 EvoUI 中负责“流程记忆 + 智能执行 + 自愈回放”的核心模块，围绕 **Planner / Executor / Critic / Report / Scenario Memory** 形成闭环。

### 1) 智能规划（Planner）
- 先通过 Router 根据用户指令匹配目标系统，再结合系统上下文与入口 URL 生成结构化执行计划。
- 输出可解析的 JSON 计划，为后续 UI 执行与步骤编排提供统一输入。

### 2) 视觉执行（Executor）
- 每一步会结合全局目标与当前步骤描述进行视觉理解，生成可执行动作（点击、输入、选择等）。
- 支持重试机制，并在执行前后结合页面截图与语义上下文动态修正动作。

### 3) 步骤验收（Critic）
- 每个步骤执行后由 Critic 进行视觉验收，判断当前步骤是否达成。
- 若验收失败，会返回失败原因与建议（如重试偏移点击、清空重填、终止流程），驱动闭环修正。

### 4) 场景记忆与复用（Scenario Memory）
- 以场景 JSON 维护 target_url、steps、operations 等可复用资产。
- 支持 operation 级别的增量沉淀（description/actions/assertion），并记录 success/fail/last_used 等统计信息。
- 在执行时可根据“全局目标 + 当前步骤 + 可用操作摘要”判断复用策略：`reuse` / `reuse_modified` / `new` / `unsure`。

### 5) 回放与自愈（Replay + Self-Healing）
- 可按历史 steps 回放动作；当动作异常或验收失败时自动进入自愈流程。
- 自愈流程会重新截图、生成新动作、再次验收；成功后会把修复后的 actions/assertion 回写到场景文件，持续提升后续回放成功率。

### 6) 可追踪报告（ReportManager）
- 执行过程会记录 Planner 输出、每次视觉尝试、Critic 验收结果与 Token 消耗。
- 自动生成 HTML 报告与截图索引，支持复盘、审计和问题定位。

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

---

## Product Walkthrough (Bilingual + Left/Right Timeline)

> Updated to a timeline-style layout with **left image / stage node / right image**, so the flow reads like a step-by-step journey.

| Left View | Timeline Node | Right View |
|---|---|---|
| <img width="360" alt="EvoUI login page" src="https://github.com/user-attachments/assets/92ac4f5c-99d4-4018-b9fc-75ffc7f4d5ab" /> | **Phase 01: Access the Platform**<br/>中文：登录并进入统一仪表盘，建立测试上下文。<br/>EN: Sign in and enter the unified dashboard to establish project context. | <img width="360" alt="EvoUI dashboard" src="https://github.com/user-attachments/assets/3bae5bb1-8232-4137-bb86-51d1da53826e" /> |
| <img width="360" alt="EvoUI user story management" src="https://github.com/user-attachments/assets/510f0860-ca1e-47ac-824a-9ef250817522" /> | **Phase 02: Structure Requirements**<br/>中文：维护 Story 结构，沉淀为可执行测试资产。<br/>EN: Curate and structure stories into executable testing assets. | <img width="360" alt="EvoUI test case generation" src="https://github.com/user-attachments/assets/7f7d9c8f-715f-45aa-9901-97cb1447b204" /> |
| <img width="360" alt="EvoUI API automation" src="https://github.com/user-attachments/assets/3fe2c388-cd0a-4d98-9b66-2b026486f0c5" /> | **Phase 03: Generate & Execute**<br/>中文：自动生成脚本，并进入 Agent 协同执行。<br/>EN: Generate scripts automatically and move into agent-assisted execution. | <img width="360" alt="EvoUI AI agent workspace" src="https://github.com/user-attachments/assets/45217d70-4e61-4b77-ac77-b98277f733fd" /> |
| <img width="360" alt="EvoUI agent orchestration" src="https://github.com/user-attachments/assets/f9dc035e-d667-4a37-9dbb-bd2ea04c9e9e" /> | **Phase 04: Orchestrate & Optimize Loop**<br/>中文：流程编排、UI 执行、报告回流，形成记忆优化闭环。<br/>EN: Orchestrate workflows, run UI automation, and feed reports into memory optimization. | <img width="360" alt="EvoUI UI automation robot" src="https://github.com/user-attachments/assets/c91e6534-fa42-47ba-9cd8-ac250fd85c3e" /> |

### End-to-End Timeline Summary

`Login/Dashboard → Story Curation → Case/API Generation → Agent Orchestration & Execution → UI Validation Reports → Memory Feedback Optimization`
