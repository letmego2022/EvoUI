# EvoUI — AI-Driven Testing Platform for QA Teams

EvoUI is an AI-driven testing platform designed to **assist QA engineers** across the full testing lifecycle: test case authoring, API testing, and UI automation.

Its core differentiator is a **process-first memory model**: EvoUI stores and retrieves knowledge from critical workflow checkpoints (key nodes), then uses agent-based orchestration to execute and verify end-to-end scenarios more reliably.

## Dashboard Overview

The dashboard is the operational hub for daily QA collaboration. It centralizes project status, test assets, and execution entry points so teams can move from planning to validation with clear context and fewer handoffs.

<img width="1645" height="1080" alt="image" src="https://github.com/user-attachments/assets/61c03ed7-3660-455d-b85d-ed9ba8cafb42" />
<img width="1639" height="959" alt="image" src="https://github.com/user-attachments/assets/bcef5006-0538-460c-bb6d-b34191d41d74" />


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

## MemoryAgent Overview

MemoryAgent is EvoUI's core module for **workflow memory, intelligent execution, and self-healing replay**, built around a closed loop of **Planner / Executor / Critic / Report / Scenario Memory**.

### 1) Intelligent Planning (Planner)
- Uses the Router to map user intent to the target system, then combines system context and entry URL to build a structured execution plan.
- Produces a parseable JSON plan as the unified input for downstream UI actions and step orchestration.

### 2) Vision-Guided Execution (Executor)
- Interprets each step using both global objective and current instruction, then generates executable actions (click, input, select, etc.).
- Supports retries and dynamically corrects actions before/after execution using screenshots and semantic context.

### 3) Step Acceptance (Critic)
- After each step, the Critic performs visual acceptance to determine whether the step objective has been achieved.
- On failure, it returns reasons and suggestions (e.g., offset-click retry, clear-and-refill, terminate flow) to drive closed-loop correction.

### 4) Scenario Memory and Reuse
- Stores reusable assets in scenario JSON files, including `target_url`, `steps`, and `operations`.
- Supports operation-level incremental accumulation (`description/actions/assertion`) with governance metadata such as `success`, `fail`, and `last_used`.
- During execution, selects reuse strategies based on global goal, current step, and operation summaries: `reuse` / `reuse_modified` / `new` / `unsure`.

### 5) Replay and Self-Healing
- Replays actions from historical steps; when actions fail or acceptance fails, self-healing is triggered automatically.
- Self-healing re-captures screenshots, generates new actions, and re-validates; once successful, repaired `actions/assertion` are written back to scenario files to improve future replay stability.

### 6) Traceable Reporting (ReportManager)
- Captures Planner output, each visual attempt, Critic acceptance results, and token consumption during execution.
- Automatically generates HTML reports and screenshot indexes for review, audit, and issue diagnosis.

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

## Product Walkthrough (Left/Right Timeline)

> Updated to a timeline-style layout with **left image / stage node / right image**, so the flow reads like a step-by-step journey.

| Left View | Timeline Node | Right View |
|---|---|---|
| <img width="360" alt="EvoUI login page" src="https://github.com/user-attachments/assets/92ac4f5c-99d4-4018-b9fc-75ffc7f4d5ab" /> | **Phase 01: Access the Platform**<br/>Sign in and enter the unified dashboard to establish project context. | <img width="360" alt="EvoUI dashboard" src="https://github.com/user-attachments/assets/3bae5bb1-8232-4137-bb86-51d1da53826e" /> |
| <img width="360" alt="EvoUI user story management" src="https://github.com/user-attachments/assets/510f0860-ca1e-47ac-824a-9ef250817522" /> | **Phase 02: Structure Requirements**<br/>Curate and structure stories into executable testing assets. | <img width="360" alt="EvoUI test case generation" src="https://github.com/user-attachments/assets/7f7d9c8f-715f-45aa-9901-97cb1447b204" /> |
| <img width="360" alt="EvoUI API automation" src="https://github.com/user-attachments/assets/3fe2c388-cd0a-4d98-9b66-2b026486f0c5" /> | **Phase 03: Generate & Execute**<br/>Generate scripts automatically and move into agent-assisted execution. | <img width="360" alt="EvoUI AI agent workspace" src="https://github.com/user-attachments/assets/45217d70-4e61-4b77-ac77-b98277f733fd" /> |
| <img width="360" alt="EvoUI agent orchestration" src="https://github.com/user-attachments/assets/f9dc035e-d667-4a37-9dbb-bd2ea04c9e9e" /> | **Phase 04: Orchestrate & Optimize Loop**<br/>Orchestrate workflows, run UI automation, and feed reports into memory optimization. | <img width="360" alt="EvoUI UI automation robot" src="https://github.com/user-attachments/assets/c91e6534-fa42-47ba-9cd8-ac250fd85c3e" /> |

### End-to-End Timeline Summary

`Login/Dashboard → Story Curation → Case/API Generation → Agent Orchestration & Execution → UI Validation Reports → Memory Feedback Optimization`
