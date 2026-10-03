# Phase 1 & Phase 2 Audit Report
**Date:** 2026-05-09  
**Scope:** Specification compliance audit (01-01-PLAN.md vs. actual implementation)  
**Status:** PARTIAL COMPLIANCE with CRITICAL GAPS

---

## Executive Summary

| Phase | Spec Target | Actual | Gap | Severity |
|-------|------------|--------|-----|----------|
| **Phase 1** | 4 modules + config + cron | 1/4 modules + config | 3 missing modules + cron | 🔴 CRITICAL |
| **Phase 2** | 6 TODO items | 4/6 complete | Executor wiring, Sentinel MTM, real-time loop, Telegram | 🟡 HIGH |

**Verdict:** Phase 1 & 2 scaffolding is 70% complete but **lacks critical automation** (cron scheduler) and **has architectural debt** (inline classes not extracted). Phase 2 is 67% architecturally complete but 0% integrated.

---

## PHASE 1 Audit (01-01-PLAN.md Spec)

### Must-Have Truths (from spec)
| Truth | Required | Actual | Status |
|-------|----------|--------|--------|
| "System can fetch real VIX <20 gate data every market open" | ✅ | `MarketDataBridge.get_current_vix()` exists but NOT extracted to `vix_engine.py` | ⚠️ INLINE |
| "System knows current NIFTY spot and ATM strike" | ✅ | `MarketDataBridge.get_nifty_spot()` inline; ATM strike logic missing | ⚠️ PARTIAL |
| "System skips trading on scheduled high-impact event days" | ✅ | `is_event_day()` STUBBED (returns False); NO event calendar loaded | ❌ BROKEN |
| "System respects 10:30–11:30 entry window and 14:30 hard exit" | ✅ | Hardcoded in `Phase1Config` but not enforced in gate logic | ⚠️ PARTIAL |

### Required Artifacts (from spec)

#### 1. `antariksh/vix_engine.py` ❌ MISSING
**Spec requires:**
- `get_vix()` → float
- `is_vix_safe()` → bool (check if VIX < threshold)
- `check_vix_gate()` → bool

**Actual:** All logic is INLINE in `phase1_mvs.py` under `GateChecker` class
- `GateChecker.check_layer1_regime()` contains VIX logic
- No separate module; cannot import `from vix_engine import get_vix()`
- No hardcoded event calendar

**Impact:** 
- ❌ Cannot unit-test VIX logic independently
- ❌ Cannot swap VIX source (yfinance ↔ broker) without editing phase1_mvs.py
- ❌ No reusability for Phase 2 agents

---

#### 2. `antariksh/event_calendar.py` ❌ MISSING
**Spec requires:**
- `is_event_day(date) → bool`
- `get_event_name(date) → str`
- Hardcoded 2026 RBI/budget/election dates

**Actual:** 
```python
# phase1_mvs.py
@staticmethod
def is_event_day() -> bool:
    # TODO: Load from config/event_calendar.json
    logger.debug("is_event_day() deferred to config load")
    return False  # ← ALWAYS FALSE
```

**Impact:**
- ❌ **CRITICAL:** System will trade on RBI/budget/election days
- ❌ No event calendar file exists (`config/event_calendar.json` not created)
- ❌ 2026 dates not recorded anywhere
- ❌ Test: `is_event_day()` on RBI day (e.g., 2026-04-10) would incorrectly permit trading

---

#### 3. `antariksh/market_data_bridge.py` ❌ MISSING
**Spec requires:** Separate module with:
- `get_current_vix() → float`
- `get_nifty_spot() → float`
- `is_event_day() → bool` (delegating to event_calendar.py)
- `get_entry_window() → tuple`

**Actual:** All logic INLINE in `phase1_mvs.py` under `MarketDataBridge` class

**Impact:**
- ❌ Cannot reuse bridge in Phase 2 agents
- ❌ No separation of concerns (market data vs. gate logic)

---

#### 4. `config/antariksh_rules.yaml` ✅ EXISTS & COMPLETE

**Status:** Fully populated with all L3 parameters
- VIX threshold: 20.0 ✅
- SL: ₹3,500 ✅
- TP: ₹1,000 ✅
- Wings: ±300 pts ✅
- Entry window: 10:30–11:30 ✅
- Hard exit: 14:30 ✅
- Free cash floor: ₹11,000 ✅
- Kill switches: Defined ✅
- Sanity checks: 19 checks across 5 tiers ✅

**Quality:** High. Matches STRATEGY_DESIGN_QUESTIONS.md decisions. Includes all constitutional constraints.

---

### Key Links from Spec

| From | To | Via | Required Pattern | Actual |
|------|----|----|-------------------|--------|
| `phase1_mvs.py` | `vix_engine.get_vix()` | import + hourly call | `from.*vix_engine import` | ❌ NOT IMPORTED |
| `vix_engine.py` | `antariksh_rules.yaml` | load VIX_THRESHOLD | `yaml.load.*vix_threshold` | ❌ NO vix_engine.py |
| `phase1_mvs.py` | `event_calendar.is_event_day()` | skip logic | `is_event_day()\|skip` | ❌ STUBBED |

---

### Phase 1 Week 1 TODO Checklist (from spec)

#### Week 1: Real Data Integration
- [x] `MarketDataBridge.get_current_vix()` — exists inline, works
- [ ] ~~Extract to `vix_engine.py`~~ — NOT DONE
- [x] `MarketDataBridge.get_nifty_spot()` — exists inline, works
- [x] `MarketDataBridge.is_event_day()` — **STUBBED**, returns False always
- [ ] Create `config/event_calendar.json` with hardcoded 2026 dates — **NOT CREATED**
- [ ] Verify data updates at 9:30 AM IST (cron + systemd timer) — **NOT CONFIGURED**

#### Week 1: Telegram Integration
- [x] `TelegramBridge.send_message()` — exists inline
- [x] Hook to `/tmp/antariksh_telegram.txt` — works
- [ ] Integration test with picoclaw — not documented

#### Week 1: Scheduler (Cron) ❌ CRITICAL MISSING
- [ ] `scheduler/run_phase1_9am.sh` — **DOES NOT EXIST**
- [ ] `scheduler/run_phase1_2pm.sh` — **DOES NOT EXIST**
- [ ] Cron entries for 9:30 AM / 2:35 PM — **NOT CONFIGURED**

**Current cron config** (`/etc/cron.d/antariksh_exec_reports`):
```
*/15 * * * * health check (no entry/exit invocation)
0 12 * * 1-5 daily report (6:00 PM IST = 12:30 UTC)
0 14 * * 0 weekly report
0 15 * * 1 monthly report
```

❌ **NO entry gate at 9:30 AM**  
❌ **NO exit gate at 2:35 PM**

---

## PHASE 2 Audit (DeepSeek Report + CREW_SPEC.md)

### Delivered (Phase 2 Completion)

#### 1. Crew Architecture ✅ COMPLETE (555 lines)
- **File:** `/home/trading_ceo/antariksh/crew_structure.py`
- **Agents:** 7 (Orchestrator, Scanner, Strategist, Executor, Sentinel, Risk Guard, Auditor)
- **Tasks:** 6 (scan → plan → check_risk → execute → monitor → log)
- **Process:** Hierarchical with Orchestrator as manager_agent
- **State:** Shared `market_state` dict for inter-agent communication

**Quality:** High. Matches HITL handoff spec. CrewAI 1.14.4 compatible.

---

#### 2. Test Harness ✅ COMPLETE (264 lines)
- **File:** `/home/trading_ceo/antariksh/crew_test.py`
- **Tests:** 4 mock dry-run tests
  - test_1_mock_dryrun: VIX gate PASS → plan generated
  - test_2_task_dependencies: agent hierarchy verified
  - test_3_risk_guard_halt: capital breach → HALT
  - test_4_gate_skip_high_vix: VIX > 20 → skip

**Quality:** Coverage for gate logic, risk guard, and re-entry. No live integration tests yet.

---

#### 3. Specification Document ✅ COMPLETE (199 lines)
- **File:** `/home/trading_ceo/antariksh/CREW_SPEC.md`
- **Content:** Role specs, task descriptions, integration points, threat model
- **Quality:** Good. Matches actual code.

---

#### 4. Three Engine Implementations ✅ COMPLETE

##### AuditorEngine (Phase 1 Log Integration)
- Reads `logs/cfo_audit_YYYY-MM-DD.jsonl`
- Calculates MTD P&L from historical JSONL
- Seeds `market_state['mtd_pnl']` at session start
- **Status:** Integrated into `initialize_session()`

##### RiskGuardEngine (Hard Deterministic Rules)
- 5 checks: daily SL, portfolio SL, 30-day DD, free cash floor, burn rate
- Returns `{passed, checks, violations, recommendations, halt}`
- Updates `market_state['halt']` for Executor
- **Status:** Integrated. No LLM in critical path.

##### ReEntryTracker (1 Re-entry Per Session)
- `can_re_enter()` checks halt status + attempts remaining
- `mark_re_entry()` increments counter
- Blocks re-entry if `market_state['halt']` is True
- **Status:** Integrated.

##### initialize_session() Bootstrap
- Calls AuditorEngine.calculate_mtd_from_logs()
- Seeds market_state with MTD context
- Resets halt, risk_ok, re-entries
- **Status:** Implemented.

---

### TODO (Phase 2 Incomplete)

#### 1. Executor.place_order() ❌ STUBBED
**Current:** Logs "would place order for X"
**Spec requires:** Wire to actual Flattrade API
**Blocker:** None (integrated but not activated)
**Effort:** 2 hours (copy pattern from broker_manager.py)

#### 2. Sentinel MTM Calculation ❌ MISSING REAL-TIME
**Current:** Stub returns mock P&L
**Spec requires:** Real Black-Scholes integration with backtester.py
**Blocker:** None (infrastructure exists)
**Effort:** 3 hours (integrate Black-Scholes, call every 2 sec)

#### 3. Scanner Real-Time Loop ❌ MISSING
**Current:** Single fetch per session
**Spec requires:** Poll market data every 60s
**Blocker:** None (MarketDataBridge.get_current_vix() exists)
**Effort:** 1 hour (add asyncio loop, retry logic)

#### 4. Telegram Bridge Integration ❌ NOT WIRED
**Current:** Phase 2 crew has no Telegram calls
**Spec requires:** Bidirectional HITL (send updates, receive confirmations)
**Blocker:** None (telegram_bridge.py exists from Phase 1)
**Effort:** 2 hours (add agent task, wire to existing module)

#### 5. LLM Cost Optimization ❌ NOT PRIORITIZED
**Current:** All agents use DeepSeek
**Spec requires:** Strategist/Guard use Claude Opus (critical), Scanner/Auditor use DeepSeek
**Blocker:** None (config already supports tiered assignment)
**Effort:** 0.5 hours (update crew_structure.py LLM assignments)

---

## Critical Gap Analysis

### 🔴 CRITICAL (blocks Monday live run)

#### 1. No Cron Scheduler for Entry/Exit
- **What:** `phase1_mvs.py` has no invocation schedule
- **Impact:** System won't run at 9:30 AM / 2:35 PM without manual trigger
- **Fix:** Add 2 lines to `/etc/cron.d/antariksh_exec_reports`:
  ```cron
  30 09 * * 1-5 root /home/trading_ceo/antariksh/run_entry.sh
  35 14 * * 1-5 root /home/trading_ceo/antariksh/run_exit.sh
  ```
- **Time:** 30 min

#### 2. Event Calendar Always Returns False
- **What:** `is_event_day()` stub prevents RBI/budget/election filtering
- **Impact:** System will trade on critical event days (high slippage, gapped opens)
- **Fix:** Create `config/event_calendar.json` + populate `event_calendar.py` with 2026 dates
- **Time:** 1 hour

#### 3. Phase 1 Architecture Debt: Inline Classes Not Extracted
- **What:** `vix_engine`, `market_data_bridge`, `event_calendar` are inline in `phase1_mvs.py`
- **Impact:** 
  - Cannot unit-test gate logic independently
  - Cannot reuse in Phase 2 agents (crew expects modular imports)
  - Harder to maintain and debug
  - Specification EXPLICITLY requires separate modules
- **Fix:** Extract 3 classes to separate files
- **Time:** 2 hours

---

### 🟡 HIGH (blocks Phase 2 integration)

#### 4. Executor.place_order() Not Wired to Real Broker
- **What:** Executor agent has stub that logs instead of placing orders
- **Impact:** Phase 2 crew will not execute real trades; only dry-run
- **Fix:** Wire to Flattrade API via broker_manager.py
- **Time:** 2 hours

#### 5. Sentinel Real-Time MTM Missing
- **What:** Sentinel agent has no real Black-Scholes P&L tracking
- **Impact:** Risk Guard cannot react to live position changes; only end-of-session audit
- **Fix:** Integrate backtester.py Black-Scholes, call every 2s during trading window
- **Time:** 3 hours

#### 6. Scanner Real-Time Loop Missing
- **What:** Scanner makes one VIX fetch per session, not continuous polling
- **Impact:** Gate checks stale data; cannot detect intraday VIX spike (e.g., 18 → 22 at 10:45 AM)
- **Fix:** Add asyncio loop, poll every 60s, update market_state
- **Time:** 1 hour

#### 7. Telegram Bridge Not Wired to Phase 2 Crew
- **What:** crew_structure.py has no Telegram agent task
- **Impact:** No two-message protocol; user gets no updates from crew
- **Fix:** Add TelegramBridge task, hook to existing telegram_bridge.py
- **Time:** 2 hours

---

### 🟢 MEDIUM (operational/optimization)

#### 8. LLM Cost Not Optimized
- **What:** All agents use DeepSeek; no tier-based fallback
- **Impact:** Cost higher than necessary; redundant expensive calls
- **Fix:** Update `crew_structure.py` LLM assignments per antariksh_rules.yaml
- **Time:** 0.5 hours

#### 9. No Phase 1 Summary Document
- **What:** DEEPSEEK_REPORT.md is external; no `01-01-SUMMARY.md` in project
- **Impact:** Phase 1 completion record not in git; harder to audit
- **Fix:** Create `01-01-SUMMARY.md` from DEEPSEEK_REPORT.md
- **Time:** 0.5 hours

---

## Specification Compliance Matrix

### Phase 1 (01-01-PLAN.md)

| Requirement | Required | Actual | Compliance % |
|---|---|---|---|
| Must-have truths (4/4) | 4 | 2 (VIX+window only; event calendar broken, NIFTY strike missing) | 50% |
| Artifact: vix_engine.py | ✅ | ❌ inline | 0% |
| Artifact: event_calendar.py | ✅ | ❌ inline + broken | 0% |
| Artifact: market_data_bridge.py | ✅ | ❌ inline | 0% |
| Artifact: antariksh_rules.yaml | ✅ | ✅ | 100% |
| Cron scheduler (9:30 AM) | ✅ | ❌ | 0% |
| Cron scheduler (2:35 PM) | ✅ | ❌ | 0% |
| **Phase 1 Total Compliance** | — | — | **38%** |

### Phase 2 (DEEPSEEK_REPORT.md)

| Item | Required | Actual | Status |
|---|---|---|---|
| Crew structure (7 agents, 6 tasks) | ✅ | ✅ | 100% |
| Test harness (4 tests) | ✅ | ✅ | 100% |
| AuditorEngine | ✅ | ✅ | 100% |
| RiskGuardEngine | ✅ | ✅ | 100% |
| ReEntryTracker | ✅ | ✅ | 100% |
| initialize_session() | ✅ | ✅ | 100% |
| Executor API wiring | ✅ | ⚠️ stub only | 25% |
| Sentinel MTM integration | ✅ | ❌ | 0% |
| Scanner real-time loop | ✅ | ❌ | 0% |
| Telegram bridge wiring | ✅ | ❌ | 0% |
| LLM cost optimization | ✅ | ❌ | 0% |
| **Phase 2 Total Compliance** | — | — | **64%** |

---

## Recommendations

### Priority 1: Unblock Monday Live Run (Due 2026-05-13)

1. **Add cron scheduler** (30 min)
   ```bash
   # Create run_entry.sh and run_exit.sh wrappers
   # Add to /etc/cron.d/antariksh_exec_reports
   ```

2. **Implement event_calendar.py** (1 hour)
   ```python
   # Extract from phase1_mvs.py, hardcode 2026 dates
   # Create config/event_calendar.json
   ```

3. **Extract market_data_bridge.py, vix_engine.py** (2 hours)
   - Move GateChecker logic to vix_engine.py
   - Move MarketDataBridge class to market_data_bridge.py
   - Update phase1_mvs.py imports

**Subtotal: 3.5 hours**

### Priority 2: Phase 2 Integration Readiness (Due 2026-05-15)

4. **Wire Executor.place_order() to Flattrade** (2 hours)
5. **Integrate Sentinel MTM with backtester.py** (3 hours)
6. **Add Scanner real-time polling loop** (1 hour)
7. **Wire Telegram bridge task to crew** (2 hours)

**Subtotal: 8 hours**

### Priority 3: Quality & Documentation (Due 2026-05-20)

8. **Optimize LLM tier assignments** (0.5 hours)
9. **Create 01-01-SUMMARY.md** (0.5 hours)
10. **Unit test extracted modules** (2 hours)

**Subtotal: 3 hours**

---

## Files Needing Creation / Modification

### NEW Files to Create
- `antariksh/vix_engine.py` (80+ lines)
- `antariksh/event_calendar.py` (100+ lines)
- `antariksh/market_data_bridge.py` (80+ lines)
- `config/event_calendar.json` (2026 RBI/budget/election dates)
- `antariksh/scheduler/run_entry.sh`
- `antariksh/scheduler/run_exit.sh`
- `01-01-SUMMARY.md` (documentation)

### Files to Modify
- `phase1_mvs.py` (remove inline classes, add imports)
- `/etc/cron.d/antariksh_exec_reports` (add 2 cron lines)
- `crew_structure.py` (wire Telegram, optimize LLM tiers)

---

## Appendix: Detailed Specs vs. Actuals

### Spec Quote 1: Artifact Requirements
> **From 01-01-PLAN.md:**
> ```yaml
> artifacts:
>   - path: "antariksh/vix_engine.py"
>     provides: "VIX polling + gate logic (VIX < 20)"
>     exports: ["get_vix", "is_vix_safe"]
> ```

**Actual:** No `vix_engine.py`. Logic is inline in `GateChecker` class in `phase1_mvs.py`.

---

### Spec Quote 2: Module Wiring
> **From 01-01-PLAN.md:**
> ```yaml
> key_links:
>   - from: "phase1_mvs.py"
>     to: "vix_engine.get_vix()"
>     via: "import + hourly call"
>     pattern: "from.*vix_engine import|get_vix()"
> ```

**Actual:** `phase1_mvs.py` has no `from vix_engine import`. VIX logic is inline.

---

### Spec Quote 3: Configuration
> **From 01-01-PLAN.md:**
> ```yaml
> config/antariksh_rules.yaml:
>   provides: "L3 parameters (VIX=20, SL=3500, TP=1000, wings=300)"
>   contains: ["layer_1_regime_gate", "vix_threshold", "entry_window"]
> ```

**Actual:** ✅ COMPLETE. File has all required fields with correct values.

---

### Spec Quote 4: Scheduler
> **From PHASE1_README.md:**
> ```bash
> # Install cron job (to be done in Week 1)
> crontab -e
> # Add:
> # 30 09 * * 1-5 /home/trading_ceo/antariksh/scheduler/run_phase1_9am.sh
> # 35 14 * * 1-5 /home/trading_ceo/antariksh/scheduler/run_phase1_2pm.sh
> ```

**Actual:** ❌ MISSING. No scheduler directory, no shell wrappers, no cron entries.

---

## Sign-Off

**Audit conducted by:** Claude (interim CEO)  
**Date:** 2026-05-09  
**Severity of gaps:** CRITICAL (3.5 hours to unblock Monday, 8 hours to production)  
**Recommendation:** Implement Priority 1 items by 2026-05-13 (Monday EOD)
