# Agent Reliability Lab — Azure OpenAI + Agents + Cosmos DB + pytest

A four-part, VS Code-ready Python lab for learning reliability engineering for AI agents.

## What you build

1. **Failure Mode Drills** — a six-mode fault injection harness driven by pytest.
2. **Graceful Degradation** — partial-success paths, fallback chain, retry budgets and escalation triggers.
3. **Persistence Deep-Dive** — Cosmos DB checkpointing, two memory tiers and tested recovery.
4. **Observability & Scoring** — structured logs, Application Insights-compatible telemetry hooks and a reliability score.

The lab runs in two modes:

- **MOCK mode**: no Azure resources required. Uses simulated LLM/tool data and local JSON persistence.
- **AZURE mode**: uses Azure OpenAI for the agent decision step and Azure Cosmos DB for persistence.

## Six fault modes

| Mode | Injected failure | Expected behavior |
|---|---|---|
| `LLM_TIMEOUT` | model call timeout | bounded retry, then fallback/escalation |
| `LLM_RATE_LIMIT` | model returns 429 | bounded retry |
| `TOOL_TIMEOUT` | downstream tool timeout | partial result/fallback or escalation |
| `TOOL_BAD_DATA` | plausible but invalid data | validate before use |
| `PERSISTENCE_FAILURE` | checkpoint write failure | preserve safety and escalate |
| `CASCADE_FAILURE` | dependency failure propagates | contain blast radius |

## Prerequisites

- [uv](https://docs.astral.sh/uv/) — manages both the Python toolchain and the dependencies
- VS Code + Python extension
- Optional Azure subscription with Azure OpenAI/Microsoft Foundry and Cosmos DB for NoSQL

You do **not** need a system Python 3.12. uv downloads the interpreter itself, so the
machine's `python3` is never used. (On many macOS machines it is far too old for this lab.)

## Install uv

macOS/Linux:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Homebrew:
```bash
brew install uv
```

Windows PowerShell:
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Restart the shell, then confirm:
```bash
uv --version
```

## Set up the lab

Same three commands on macOS, Linux and Windows:

```bash
uv venv --python 3.12
uv pip install -r requirements.txt
cp .env.example .env
```

`uv venv --python 3.12` pins the interpreter and downloads Python 3.12 if it is not already
present. On Windows PowerShell, use `copy .env.example .env` for the last line.

Then set the mode in `.env`.

For the offline lab (no Azure resources needed — this is the default):
```env
LAB_MODE=mock
```

For Azure:
```env
LAB_MODE=azure
AZURE_OPENAI_ENDPOINT=https://YOUR-RESOURCE.openai.azure.com/
AZURE_OPENAI_API_KEY=YOUR_KEY
AZURE_OPENAI_DEPLOYMENT=YOUR_DEPLOYMENT
AZURE_OPENAI_API_VERSION=2024-10-21
COSMOS_ENDPOINT=https://YOUR-ACCOUNT.documents.azure.com:443/
COSMOS_KEY=YOUR_KEY
COSMOS_DATABASE=agent_reliability_lab
COSMOS_CONTAINER=agent_state
```

## Run

Prefix every command with `uv run`. There is no activation step — `uv run` selects the `.venv`
and installs the lab's own package into it first, so `import reliability_lab` resolves from the
`src/` layout.

```bash
uv run python -m reliability_lab.demo
uv run pytest -q
```

Part-by-part:
```bash
uv run pytest -q tests/test_part1_fault_injection.py
uv run pytest -q tests/test_part2_graceful_degradation.py
uv run pytest -q tests/test_part3_persistence.py
uv run pytest -q tests/test_part4_observability.py
```

Azure integration (needs `LAB_MODE=azure` and the Azure values in `.env`):
```bash
uv run python -m reliability_lab.azure_demo
```

### Troubleshooting

`ModuleNotFoundError: No module named 'reliability_lab'` means the command was run as bare
`python ...` instead of `uv run python ...`. Either add the `uv run` prefix, or install the
package once with `uv pip install -e .`.

## What actually uses Azure

Two things vary independently: the **reasoning step** (mock string or a real model call) and
**persistence** (local JSON file or Cosmos DB). They are not tied together, and most of the lab
does not use Azure at all.

| Part / entry point | Reasoning step | Checkpoints | Changes with `LAB_MODE`? |
|---|---|---|---|
| **Part 1** — fault injection | not used | not used | No |
| **Part 2** — graceful degradation | Mock (forced) | Local JSON | No |
| **Part 3** — persistence | not used | Local JSON (forced) | No |
| **Part 4** — observability & scoring | Mock (forced) | Local JSON | No |
| `demo.py` | **Follows `LAB_MODE`** | Local JSON (always) | Reasoning step only |
| `azure_demo.py` | Azure OpenAI (forced) | **Cosmos DB** | Requires `azure` |

Three consequences worth knowing before you start:

- **All four parts run identically in both modes.** Every test hardcodes the mock reasoning step
  and the local store, so `uv run pytest` behaves the same whether `LAB_MODE` is `mock` or `azure`
  — and a passing suite says nothing about whether your Azure credentials are correct. Use the
  preflight checks in the Azure Setup Guide for that.
- **`demo.py` in azure mode is a hybrid.** It calls Azure OpenAI for the answer but still writes
  checkpoints to `local_state/checkpoints.json`. Do not go looking for those rows in Cosmos.
- **`azure_demo.py` is the only thing that writes to Cosmos DB.**

## VS Code

```bash
code .
```

Select the interpreter created by `uv venv` — `.venv/bin/python` on macOS/Linux,
`.venv\Scripts\python.exe` on Windows. The Testing panel then discovers pytest automatically.

## Teaching flow

### Part 1 — Failure Mode Drills
Build and run the six fault injectors. Ask learners to identify detection, recovery, escalation and business risk.

### Part 2 — Graceful Degradation
Add retry budgets, fallbacks, partial-success responses and escalation rules.

### Part 3 — Persistence Deep-Dive
Checkpoint before risky operations, simulate restart, recover state, then switch the adapter from local JSON to Cosmos DB.

### Part 4 — Observability & Scoring
Emit structured events, add latency/fault/correlation fields, and calculate a reliability score.

## Final challenge

Make the agent:
1. accept invalid tool data,
2. retry forever,
3. checkpoint only after a risky operation,
4. log only free-form strings.

Then ask which failures become invisible, unrecoverable or capable of producing an incorrect business outcome.
