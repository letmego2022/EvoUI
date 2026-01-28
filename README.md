# EvoUI – Self-Evolving Intelligent UI Automation

**EvoUI** is an advanced UI automation framework designed to combine AI-driven action memory, visual fallback execution, and intelligent step verification. The system continuously learns from previous actions, reuses existing operation memories, and adapts to dynamic web UI changes.  

---

## Features

### 1. AI-Powered Operation Memory
- Reuse previous UI actions for new steps with high confidence.
- Supports parameterized reuse (`reuse_modified`) for inputs like text fields.
- Avoids blindly repeating actions; considers element coordinates, action type, and context.
- Maintains statistics for each operation (success/failure, last used).

### 2. Multi-Step Action Verification
- Each automation step can contain multiple actions (type, click, select, etc.).
- EvoUI verifies the success of **every action** before marking the step as complete.
- Detects incomplete steps (e.g., typed input but save button not clicked).

### 3. Visual Feedback & Fallback Execution
- Integrates SoM (Semantic Overlay Marking) to accurately locate UI elements.
- Marks attempted clicks visually for debugging.
- Automatically triggers visual fallback if memory-based actions fail.
- Supports dynamic corrections when target elements are partially off-screen or hidden.

### 4. State Transition & Input Consistency Checks
- Checks status changes for toggles, add/remove buttons, and other state-flipping elements.
- Verifies typed content matches intended input, including secure fields.

### 5. Self-Evolving & Governance
- Tracks each operation's success/failure history.
- Supports AI-driven operation selection based on global goals and step context.
- Improves automation reliability by learning which actions are reusable or need adjustment.

---

## System Architecture

```

User Scenario / Test Case
│
▼
Step-by-Step Instructions
│
▼
┌─────────────────────────┐
│  EvoUI Operation Memory │
│  - Reuse previous steps │
│  - Parameter adjustment │
└───────────┬─────────────┘
│
▼
Action Execution Engine
┌─────────────────────────┐
│ - Click / Type / Scroll │
│ - Hover / Swipe / Keys │
└───────────┬─────────────┘
│
▼
Verification & Visual Fallback
┌─────────────────────────┐
│ - Screenshot & SoM      │
│ - Step validation       │
│ - Fallback execution    │
└─────────────────────────┘

````

---

## Installation

```bash
# Clone the repository
git clone https://github.com/your_org/EvoUI.git
cd EvoUI

# Install dependencies
pip install -r requirements.txt
````

**Requirements:**

* Python 3.9+
* Playwright (Chromium)
* Additional Python packages as listed in `requirements.txt`

---

## Usage

```python
from evo_ui import EvoUIOperator

# Initialize operator
operator = EvoUIOperator(target_url="https://example.com")

# Define scenario steps
steps = [
    "Enter project name in the input box",
    "Click the save button to create project"
]

# Execute scenario
for step_idx, step_desc in enumerate(steps):
    # EvoUI selects or reuses operations automatically
    step_success = operator.execute_step(step_desc, global_goal="Create a new project")
    if not step_success:
        print(f"Step {step_idx+1} failed, fallback triggered.")
```

---

## Key Advantages

* **Intelligent Reuse:** Minimize duplicated work with operation memory and parameter adaptation.
* **Robustness:** Visual fallback ensures automation succeeds even when memory-based execution fails.
* **Traceable:** Each step and action is logged with success/failure, coordinates, and timestamps.
* **Self-Evolving:** System improves over time, learning which actions are reliable for future scenarios.

---

## License

~~ MIT License – see `LICENSE` file for details. ~~

---

## Contact

For questions or contributions, please reach out to `your_email@example.com`.


