# Instructor Guide

## Part 1 — Failure Mode Drills

Run:
```bash
pytest -q tests/test_part1_fault_injection.py
```

Have learners map each fault to:
- detection point
- recovery policy
- escalation condition
- business risk

Then add a seventh mode such as `STALE_DATA` or `SCHEMA_DRIFT`.

## Part 2 — Graceful Degradation

Run:
```bash
pytest -q tests/test_part2_graceful_degradation.py -vv
```

Discuss:
- retry budgets
- partial success
- safe fallback
- escalation
- why more retries can reduce reliability

## Part 3 — Persistence Deep-Dive

Run:
```bash
pytest -q tests/test_part3_persistence.py -vv
```

The key lesson is checkpoint timing: persist state BEFORE the risky operation, not only after it.

The Cosmos adapter uses:
- database: `agent_reliability_lab`
- container: `agent_state`
- partition key: `/partitionKey`

## Part 4 — Observability & Scoring

Run:
```bash
pytest -q tests/test_part4_observability.py -vv
```

Ask learners to add:
- latency_ms
- model/deployment
- tool_name
- retry_count
- fault_mode
- checkpoint_id
- correlation_id

Then create a one-page diagnostic.

## Final diagnostic

Ask:
1. Which fault was most dangerous?
2. Which was easiest to detect?
3. Where can a plausible but wrong answer occur?
4. Which state must survive restart?
5. Which signals should reach Application Insights?
6. What minimum score would you accept for production?
