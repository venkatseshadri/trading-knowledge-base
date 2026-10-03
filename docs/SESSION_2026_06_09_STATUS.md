# Session Status — 2026-06-09

## Result: Zero trades

## What's working

| System | Status |
|--------|--------|
| PENGUIN (data capture) | ✅ 7/7 services active, enriched data flowing (spot, atm_strike, VIX, ADX all populated) |
| UNICORN (LLM entry gate) | ✅ Adversarial debate running, producing go/no-go signals |
| BRAHMAND kickoff | ✅ Cron executing every 5 min, chain reaches all agents |
| Porcupine (regression harness) | ✅ 9/9 milestones, autobuilder running |

## What's broken

CrewAI agent output parsing after UNICORN gates:

```
15:36: NOT_UP=True NOT_DOWN=True      ← UNICORN says go
15:36: Regime: None (VIX=?) → None   ← Regime agent output NOT parsed
15:37: Crew raw output: None          ← Strategy agent output lost
15:37: PROVENANCE VIOLATION → NONE    ← CLAMPED
15:37: Execution: no trade → SKIP
```

The regime agent *produces* correct output (VIX 15.56, ADX 57.02, "enter" — visible in CrewAI task output), but `e2e_chain.py` cannot extract it. Same for Strategy agent.

Cascading failure chain:
1. Regime output unparsed → `regime=None`
2. Strategy receives `regime=None` → `strategy_type=None`
3. Provenance CLAMPED → Execution aborts

## Fixes applied today

1. `antariksh/config/sqlite_schema.py:37` — busy_timeout 5000→30000ms
2. `antariksh/consumers/instrument_consumer.py:283-322` — split consumer transaction (market_data commit before option_prices) to release lock for enricher
3. Deployed `PENGUIN_ENRICHER_LOCK_FIX_APPLIED.md` (was coded but not restarted) — `BEGIN IMMEDIATE` + 5-retry backoff in `instrument_enricher.py`

## Next action

Investigate why CrewAI `tasks_output` is `None` for Regime and Strategy agents despite the agents producing valid output visible in the logs. Possible causes: JSON parse failure, task output extraction bug, or CrewAI version incompatibility.

---

## RESOLVED (2026-06-09, later) — it was a JSON parse/extraction bug, not `tasks_output=None`

**Root cause (proven):** `e2e_chain` extracted agent output with
`parse_json_output(str(result.tasks_output[i]))`. But CrewAI's `TaskOutput.__str__`
returns `str(json_dict)` / `str(pydantic)` when the agent emits **structured** output —
a single-quoted **Python repr** like `{'regime': 'enter', 'vix': 15.56}`. `json.loads`
rejects single quotes, so **every** structured agent output parsed to `{}` →
`regime=None` → `strategy_type=NONE` → provenance CLAMP → SKIP. The agents were
correct all along (that's why their output was visible via the step callbacks); the
extraction threw it away.

**Fix** (`brahmand@4e4456e`):
- `parsing.py`: new `extract_task_output()` reads `.json_dict` / `.pydantic` **directly**
  (no stringify); `parse_json_output` is now string-aware (braces inside string values)
  and tolerates single-quoted python-repr dicts. Regression test `tests/test_output_parsing.py` (11/11).
- `e2e_chain.py`: all 3 extraction sites use `extract_task_output`; loud diagnostic if a
  crew ever truly returns no `tasks_output` (logs `type`+`repr`).

**Verification:** unit-proven against a real `crewai.TaskOutput(json_dict=...)` —
old path → `{}`, new path → the correct dict. Final confirmation is the next live
kickoff (Mon); the added diagnostic makes any residual conclusive.

**Flagged, NOT auto-fixed:**
- `regime_check.py` / `strategy_check.py` carry the same `json.loads(str(result))` bug
  but are **dead code** (unimported) — left as-is.
- `risk_agent_crew.evaluate_trade` returns `{"result": str(result)}` (a string) while
  `position_manager.run_bridge` expects a **list** (`if isinstance(llm_actions, list)`),
  so the LLM risk agent's morph/shift/TSL actions are **silently discarded** and the
  deterministic SL/TP path always runs. This is a **risk-path behavioral** issue —
  needs Board sign-off before changing (it would activate LLM-driven risk actions live).

**Note:** the earlier `_deterministic_fallback` fixes (#3 session_phase/SuperTrend, #4
VIX-null) are on the **LLM-down** path — they did NOT address this; this parse bug was
the actual zero-trades blocker on the **primary** path.
