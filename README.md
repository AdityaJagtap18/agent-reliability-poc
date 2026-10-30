# Agent Reliability POC

> A Forward Deployed Engineering (FDE) proof of concept. This repository contains both the **pre-transformation** (before) and **post-transformation** (after) states of the solution, so the impact of the work can be seen side by side.

---

## 1. Overview

| Item | Details |
|------|---------|
| **POC Name** | Agent Reliability POC |
| **Scenario / Customer** | Illustrative customer-support agent that looks up a customer record and answers a status question |
| **Owner** | Adiraj |
| **Status** | Completed |
| **Program** | FDE Program – Assignment 6 |

**One-line summary:** Shows how to make an AI agent reliable by injecting six failure modes and proving, with pytest, that it retries within a budget, degrades gracefully, recovers from checkpoints and emits structured telemetry.

---

## 2. Problem Statement

AI agents call models and tools that time out, get rate-limited, return plausible-but-wrong data, or lose state mid-run. Without explicit reliability engineering, these failures become silent, unrecoverable, or produce an incorrect business outcome.

- Model calls can time out or return HTTP 429.
- Downstream tools can time out or return bad data that looks valid.
- A failed checkpoint write or a cascading dependency failure can leave the run in an unknown state.
- Free-form logs make failures invisible and hard to score.

---

## 3. Pre-Transformation (Before)

The starting point is the reliability harness and agent scaffold: fault injection, the agent, persistence adapters, telemetry and scoring, together with the pytest drills for each part.

| Aspect | Current State |
|--------|---------------|
| Process | Agent runs a request, calls the model and a customer tool, and checkpoints state |
| Model / Tooling | Mock reasoning step (default) or Azure OpenAI; local JSON or Azure Cosmos DB for state |
| Cost | Not measured. Mock mode has no Azure cost |
| Latency / Performance | Not measured |
| Accuracy / Quality | Not scored in this snapshot |
| Pain points | Failure handling, retry budgets and observability are the focus areas the drills are built to exercise |

**Location in repo:** [Pre-Transformation/](Pre-Transformation/)

---

## 4. Post-Transformation (After)

The completed solution, run end to end in mock mode. The agent processes a request, checkpoints before and after the risky step, and returns a successful result (see `local_state/checkpoints.json`, which records a `COMPLETED` / `SUCCESS` run for `CUST-1001`).

| Aspect | New State |
|--------|-----------|
| Process | Checkpoint first, then call the model and tool with bounded retries, then fall back or escalate |
| Model / Tooling | Python owns reliability policy; Azure OpenAI is used only for the final answer in `azure` mode |
| Cost | Not measured. Mock mode has no Azure cost |
| Latency / Performance | Not measured |
| Accuracy / Quality | Reliability score out of 100 (recovery, safety, persistence, observability, 25 each) |
| Benefits | Failures are detected, contained, recoverable and visible |

**Location in repo:** [Post-Transformation/](Post-Transformation/)

---

## 5. Before vs. After

| Metric | Pre-Transformation | Post-Transformation | Change |
|--------|--------------------|---------------------|--------|
| Source code (`src/`) | Reliability harness and agent | Same files | No difference |
| Test suite (`tests/`) | Four-part pytest drills | Same files | No difference |
| Instructor guide / `pyproject.toml` | Present | Identical | No difference |
| Recorded run output | None | `local_state/checkpoints.json` (1 successful run) | Run evidence added |
| `.env.example`, `.gitignore`, VS Code settings | Present | Not included | Setup scaffolding only in Pre |

No latency, cost or accuracy figures were captured for either state, so none are claimed here. A file-by-file comparison of the two folders shows the `src/` and `tests/` contents are identical.

---

## 6. Approach

1. **Discover** – Identify the failure modes an agent must survive.
2. **Baseline** – Start from the harness and agent scaffold.
3. **Evaluate** – Check each fault mode against its expected behavior.
4. **Build** – Implement fault injection, retry budgets, fallbacks, escalation, checkpointing and telemetry.
5. **Measure** – Run the pytest suite and compute the reliability score.
6. **Hand off** – Document setup, modes and the instructor guide.

### Six Fault Modes

| Mode | Injected failure | Expected behavior |
|---|---|---|
| `LLM_TIMEOUT` | Model call timeout | Bounded retry, then fallback or escalation |
| `LLM_RATE_LIMIT` | Model returns 429 | Bounded retry |
| `TOOL_TIMEOUT` | Downstream tool timeout | Partial result, fallback or escalation |
| `TOOL_BAD_DATA` | Plausible but invalid data | Validate before use |
| `PERSISTENCE_FAILURE` | Checkpoint write failure | Preserve safety and escalate |
| `CASCADE_FAILURE` | Dependency failure propagates | Contain the blast radius |

### Evaluation Criteria

The reliability score weights four dimensions equally.

| Criterion | Weight | Why |
|---|---|---|
| Recovery | 25% | Retries must be bounded; excess retries lower the score |
| Safety | 25% | An escalated run must actually escalate |
| Persistence | 25% | A run with no checkpoint cannot be recovered |
| Observability | 25% | A run with no structured events cannot be diagnosed |

---

## 7. Repository Structure

```
Assigmnet6/
├── README.md
├── Pre-Transformation/      # "Before" state
│   ├── src/reliability_lab/ # agent, faults, persistence, telemetry, scoring, tools
│   ├── tests/               # one test file per part (1-4)
│   ├── .env.example
│   ├── INSTRUCTOR_GUIDE.md
│   └── pyproject.toml
└── Post-Transformation/     # "After" state
    ├── src/reliability_lab/
    ├── tests/
    ├── local_state/         # checkpoints written by a run
    ├── INSTRUCTOR_GUIDE.md
    └── pyproject.toml
```

Each folder also holds its own README with the full walkthrough, plus the Azure setup and result interpretation guides (.docx).

---

## 8. Getting Started

### Prerequisites

- [uv](https://docs.astral.sh/uv/), which installs Python 3.12 and the dependencies
- VS Code with the Python extension (optional)
- Optional: an Azure subscription with Azure OpenAI and Cosmos DB for NoSQL

### Setup

```powershell
cd Post-Transformation
uv venv --python 3.12
uv pip install -r requirements.txt
copy ..\Pre-Transformation\.env.example .env
```

The default is `LAB_MODE=mock`, which needs no Azure resources. For Azure, set `LAB_MODE=azure` and fill in the `AZURE_OPENAI_*` and `COSMOS_*` values in `.env`.

### Run

```powershell
uv run python -m reliability_lab.demo
uv run pytest -q
```

Run one part at a time with `uv run pytest -q tests/test_part1_fault_injection.py` (and `part2` to `part4`). The Azure integration run is `uv run python -m reliability_lab.azure_demo`.

> Note: the Python package name `reliability_lab` is an internal module name and is kept so the imports and commands above keep working.

---

## 9. Results & Learnings

- **Key result:** A mock-mode run completes with status `SUCCESS` and a persisted checkpoint; the pytest suite exercises all six fault modes.
- **What worked:** Checkpointing before the risky operation, bounded retries, and structured events that feed a reliability score.
- **What didn't:** Nothing is measured against real Azure traffic. The tests hardcode the mock reasoning step and the local store, so a passing suite says nothing about whether Azure credentials are correct.
- **Recommendations:** Checkpoint before, not only after, a risky step. Cap retries, since unlimited retries reduce reliability. Validate tool data before using it.

> Caveats: Customer data is simulated and no cost or latency was measured. Only `azure_demo.py` writes to Cosmos DB; `demo.py` in `azure` mode still checkpoints to local JSON.

---

## 10. Next Steps

- [ ] Add a seventh fault mode such as `STALE_DATA` or `SCHEMA_DRIFT`.
- [ ] Capture latency and cost baselines in both modes.
- [ ] Run the Azure integration against a real Cosmos DB account and compare with local JSON.

---

## 11. Contact

Adiraj · adiraj2503@gmail.com
