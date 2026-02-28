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

---

## Product Walkthrough (中英双语)

> Below is a compact, operation-style walkthrough. Each screen includes Chinese + English captions and uses a smaller display width for easier reading.

### 1. 登录页 / Login Page
**中文**：终端（CMD）风格登录界面，贴近测试与研发人员的工作心智。  
**EN**: Terminal-style login experience designed for QA and engineering users.

<img width="560" alt="EvoUI login page" src="https://github.com/user-attachments/assets/92ac4f5c-99d4-4018-b9fc-75ffc7f4d5ab" />

### 2. 仪表盘 / Dashboard
**中文**：统一入口管理测试域（Domain）与项目，并提供 AI Agent 的核心入口。  
**EN**: Unified dashboard for test-domain/project management and quick access to AI Agents.

<img width="560" alt="EvoUI dashboard" src="https://github.com/user-attachments/assets/3bae5bb1-8232-4137-bb86-51d1da53826e" />

### 3. User Story 管理 / User Story Management
**中文**：支持手动维护多类 User Story（PAGE / FUNCTION / FLOW / API 等）。  
**EN**: Manually manage multiple User Story types (PAGE / FUNCTION / FLOW / API, etc.).

<img width="560" alt="EvoUI user story management" src="https://github.com/user-attachments/assets/510f0860-ca1e-47ac-824a-9ef250817522" />

### 4. 用例生成 / Test Case Generation
**中文**：基于 UI 页面元素，由 AI BA 提取结构化信息并生成测试用例；其他场景可直接由 AI 生成。  
**EN**: Generate test cases from structured UI analysis (AI BA extraction), with direct AI generation for other scenarios.

<img width="560" alt="EvoUI test case generation" src="https://github.com/user-attachments/assets/7f7d9c8f-715f-45aa-9901-97cb1447b204" />

### 5. 接口自动化 / API Automation
**中文**：AI 可读取 API 类 User Story 自动生成脚本，支持对话式修改与主动优化，并保留偏好记忆。  
**EN**: AI generates API test scripts from API-tagged stories, supports conversational edits and proactive optimization with preference memory.

<img width="560" alt="EvoUI API automation" src="https://github.com/user-attachments/assets/3fe2c388-cd0a-4d98-9b66-2b026486f0c5" />

### 6. AI Agent 工作台 / AI Agent Workspace
**中文**：集中管理 Agent 能力、执行入口与协同上下文。  
**EN**: Central workspace for Agent capabilities, execution entry points, and shared context.

<img width="560" alt="EvoUI AI agent workspace" src="https://github.com/user-attachments/assets/45217d70-4e61-4b77-ac77-b98277f733fd" />

### 7. Agent 流程编排 / Agent Workflow Orchestration
**中文**：可视化编排复杂任务流程，支持多阶段执行与分支控制。  
**EN**: Visually orchestrate complex, multi-stage workflows with branch control.

<img width="560" alt="EvoUI agent orchestration" src="https://github.com/user-attachments/assets/f9dc035e-d667-4a37-9dbb-bd2ea04c9e9e" />

### 8. UI 自动化机器人 / UI Automation Robot
**中文**：执行 UI 自动化任务，输出报告，并结合记忆机制持续优化执行稳定性。  
**EN**: Execute UI automation with reporting and memory-driven stability improvements.

<img width="560" alt="EvoUI UI automation robot" src="https://github.com/user-attachments/assets/c91e6534-fa42-47ba-9cd8-ac250fd85c3e" />
