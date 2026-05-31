# Antariksh & Brahmand: Complete Agent & System Architecture

**Last Updated:** May 20, 2026  
**Status:** Production Ready (Monday 09:15 AM)

---

## Overview

Antariksh is a **7-agent CrewAI trading system** with Brahmand as the **autonomous data/monitoring backbone**.

```
┌─────────────────────────────────────────────────────────┐
│          ANTARIKSH TRADING DESK (CrewAI)                │
│  7 Agents + Order Hub + Risk Rules + Telegram Bridge    │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    ┌────▼─────────┐      ┌─────▼──────────┐
    │  BRAHMAND    │      │  EXTERNAL      │
    │  Autonomous  │      │  Systems       │
    │  Monitor     │      │                │
    └──────────────┘      └────────────────┘
         │                       │
    ┌────▼────────────────────────▼──┐
    │   DuckDB + Order Ledger         │
    │   (Trade State + Audit Trail)   │
    └─────────────────────────────────┘
```

---

## Part 1: ANTARIKSH Trading Desk

### **7-Agent Core Crew**

#### 1. **SCOUT Agent** — Market Regime Detector
- **Role:** Reads market conditions, identifies regime (TRENDING_BULL, TRENDING_BEAR, SIDEWAYS)
- **Input:** VIX, NIFTY spot, momentum indicators
- **Output:** Regime classification + confidence score
- **Runs:** Entry decision phase (before strategist)
- **File:** `agents/scout_agent.py`
- **Decision:** "Market is SIDEWAYS 75% confidence → proceed or reject"

---

#### 2. **RESEARCHER Agent** — Signal & Backtest Analysis
- **Role:** Researches entry signals, backtests proposed trades
- **Input:** Entry gate signals (Trend + Trendline combo), historical data
- **Output:** Win rate %, max drawdown, profit factor for trade setup
- **Runs:** Entry decision phase
- **File:** `agents/research_agent.py`
- **Decision:** "Iron Fly at 23700/23800: 65% win rate, 3:1 RR → GO"

---

#### 3. **STRATEGIST Agent** — Trade Structure Design
- **Role:** Designs Iron Butterfly setup (strike selection, wings, exits)
- **Input:** Entry signal, ATM strike, regime, backtest results
- **Output:** Legs (PE/CE strikes, quantities, SL, TP)
- **Runs:** Entry decision phase
- **File:** `agents/strategist_agent.py`
- **Decision:** "SELL 23750 PE/CE, wings @ 23650/23850, SL ₹3500, TP ₹2L"

---

#### 4. **RISK GUARD Agent** — Capital & Position Safety
- **Role:** Hard-checks all risk limits before execution
- **Input:** Proposed trade, current capital, margin, open positions
- **Output:** APPROVED or REJECTED with reason
- **Runs:** Entry validation + monitoring (runs every 5 min via kickoff)
- **File:** `risk_config.py` (deterministic rules, not LLM)
- **Rules (Hard):**
  - Max daily loss: ₹100K
  - Max position loss: ₹30K
  - Max concurrent trades: 4
  - Max shifts: 2/trade
  - Free cash floor: ₹50K
  - Margin utilization: ≤ 85%
- **Decision:** "Capital OK, margin OK, no conflicts → APPROVED"

---

#### 5. **EXECUTOR Agent** — Order Placement
- **Role:** Places orders via Order Agent hub, tracks execution
- **Input:** Approved trade structure, symbol, quantity, pricing
- **Output:** Order IDs, fill prices, execution timestamps
- **Runs:** Entry execution phase
- **File:** `agents/executioner_agent.py` + `order_agent.py`
- **Decision:** "Placed PE order @ ₹150, CE order @ ₹145 | Total credit ₹2,05,000"

---

#### 6. **SENTINEL Agent** — Real-time Position Monitor
- **Role:** Watches positions for SL/TP/margin breaches (not yet autonomous)
- **Input:** Active position, live option LTP, account state
- **Output:** Alerts, exit signals, emergency actions
- **Runs:** Continuous during market hours (via risk_monitor.py every 1 min)
- **File:** `risk_monitor.py` (new, 2026-05-20)
- **Checks:**
  - SL hit → EXIT immediately
  - TP hit → EXIT immediately
  - Margin call → reduce/close position
  - Position MORPH detected → shift legs
- **Decision:** "SL hit on PE leg @ 1:05 PM → EXIT trade | PnL: -₹28K"

---

#### 7. **AUDITOR Agent** — Trade Logging & Compliance
- **Role:** Records all trades, checks invariants, enforces audit trail
- **Input:** Entry/exit details, all actions, P&L
- **Output:** Immutable JSONL audit log
- **Runs:** Post-trade (entry) and close (exit)
- **File:** `agents/auditor_agent.py` (via trading_desk.py)
- **Invariants (Hard):**
  - All trades logged with timestamps
  - SL/TP checked before execution
  - Capital never goes negative
  - Max 4 concurrent trades
  - Re-entry max 1/session
- **Output Example:**
  ```json
  {
    "trade_id": "TRADE-20260520-001",
    "entry_time": "09:35:15",
    "entry_gate": "TREND",
    "legs": [{"symbol": "NIFTY23750PE", "action": "SELL", "qty": 65, "price": 150}],
    "status": "CLOSED",
    "close_time": "14:05:30",
    "close_reason": "SL_HIT",
    "pnl": -28000,
    "capital_after": 583000
  }
  ```

---

### **Central Order Agent (Order Hub)**

**File:** `brahmand/order_agent.py`

**Purpose:** Single point of order routing for ALL order types

**Order Types:**
- `ENTRY` — Initial trade placement
- `EXIT` — Close entire trade
- `SL` / `TP` — Stop loss / take profit orders
- `MODIFY_SL` / `MODIFY_TP` — Adjust levels
- `SHIFT_CLOSE` — Leg shifter closing old leg
- `SHIFT_OPEN` — Leg shifter opening new leg
- `MORPH` — Position manager morphing

**Dual-Write (May 20 onwards):**
1. **order_ledger.json** — `/tmp/order_ledger.json` (fast, scheduler checks this)
2. **trade_execution.duckdb** — Separate DB (audit trail, research, risk monitor reads)

**Flow:**
```
Any agent needs order
  ↓
place_order(symbol, action, qty, price, order_type, trade_id)
  ├─ Generates order_id
  ├─ PAPER mode: immediately mark FILLED
  ├─ Write to order_ledger.json
  ├─ Write to trade_execution.duckdb
  └─ Return order confirmation
```

---

### **Risk Configuration System**

**File:** `antariksh/risk_config.py`

**Purpose:** Zero-hardcoding risk limits, hot-reload capable

**All Limits Stored:**
```python
CAPITAL = 611_000  # Total account capital
FREE_CASH_FLOOR = 50_000
MAX_MARGIN_UTIL = 85%

RISK_PER_TRADE = 30_000  # Max loss per trade
RISK_PER_DAY = 100_000  # Max daily loss
MAX_CONCURRENT = 4  # Concurrent positions
MAX_SHIFTS = 2  # Shifts per trade

NIFTY_LOT = 65  # Lot size
WING_WIDTH = [50, 100, 150, 200, 250]  # Options for wing width
TSL_THRESHOLD = 25%  # Activate trailing SL at 25% of TP profit
```

**Public API:**
```python
get_config_summary()  # Display formatted config
get_current_limits()  # From broker (margin sync)
sync_with_config()    # Update from risk_config.py
```

---

### **Trading Desk Orchestration**

**File:** `antariksh/trading_desk.py`

**Phases:**
1. **PREPARATION** (pre-market)
   - Initialize registries (agents + tools)
   - Load market data
   - Verify broker connections

2. **ENTRY** (9:15-11:30 window)
   - Every 5 min: check entry signals
   - If gates pass: run 7-agent crew
   - Place orders via Order Agent

3. **MONITORING** (9:15-15:30)
   - Every 1 min: risk_monitor.py checks SL/TP/MORPH
   - Every 5 min: leg_shifter evaluates shifts
   - Every minute: pattern enricher adds indicators

4. **EXIT** (14:30-15:30)
   - Risk monitor auto-closes if SL/TP hit
   - Manual exit if needed
   - Audit log finalized

---

## Part 2: BRAHMAND Autonomous Monitor

### **Risk Monitor** (1-min Cadence)

**File:** `brahmand/risk_monitor.py`

**Cron:** `*/1 9-15 * * 1-5 python3 risk_monitor.py`

**Logic:**
```python
if not has_active_trades():
    exit()  # Nothing to do

for trade in get_active_trades():
    # Query option LTP from DuckDB
    ltp = query_latest_price(symbol, strike, expiry)
    
    # Check SL trigger
    if ltp >= trade["sl"][leg_type]:
        close_trade(trade_id, "SL_HIT")
        update_order_ledger()
        return
    
    # Check TP trigger
    if ltp <= trade["tp"][leg_type]:
        close_trade(trade_id, "TP_HIT")
        update_order_ledger()
        return
    
    # Check MORPH (position manager call)
    actions = position_manager.run(trade)
    if actions:
        execute_morph(actions)
    
    # Log audit
    log_monitor_action(trade_id, ltp, pnl)
```

**Output:**
- Updates `trade_execution.duckdb` → `active_trades` (mark CLOSED)
- Updates `order_ledger.json` → mark orders closed
- Logs to `risk_monitor_YYYYMMDD.log`

---

### **Pattern Enricher** (Continuous)

**File:** `brahmand/pattern_enricher.py`

**Cron:** `*/5 9-15 * * 1-5 python3 pattern_enricher.py --live`

**Purpose:** Detect intraday patterns (momentum, volatility shifts)

**Outputs:**
- Momentum score (5-min rolling)
- Support/resistance updates
- Volatility regime changes
- Entry trigger signals for kickoff

---

### **Margin Capture** (Every 5 min)

**File:** `brahmand/margin_capture.py`

**Cron:** `*/5 9-15 * * 1-5 python3 margin_capture.py`

**Purpose:** Fetch live broker margins, validate capital safety

**Outputs:**
- Current margin available (Shoonya + Flattrade)
- Free cash vs floor
- Warns if margin < 20% buffer

---

### **Data Health Check**

**File:** `brahmand/data_health.py`

**Cron:** `*/5 9-15 * * 1-5 python3 data_health.py --alert`

**Checks:**
- DuckDB integrity
- Option snapshot freshness (LTP age < 2 min)
- Quote feed continuity
- Missing OHLCV bars

---

### **Leg Shifter** (Strategy Adaptation)

**File:** `brahmand/leg_shifter.py`

**Called by:** Kickoff monitor loop, position_manager

**Purpose:** Auto-adapt trade structure based on market movement

**Shifts:**
1. **HEDGE_SHIFT** — Move hedge closer/further as stock moves
2. **SELL_SHIFT** — Roll sold leg to new ATM as stock moves

**All orders via:** Order Agent (dual-write to JSON + DuckDB)

---

### **Position Manager** (Adaptive Rules)

**File:** `brahmand/position_manager.py`

**Called by:** Risk monitor, kickoff monitor loop

**Priority Actions:**
1. P1: Theta decay ≥ 37.5% → ROLL to ATM
2. P2: Hedge > 150 pts from sold strike → TIGHTEN
3. P3: Entry signal changed → MORPH (add/remove side)
4. P4-P7: SL/TP/floor checks (but risk_monitor primary)

---

### **Scheduler (Kickoff)** (Every 5 min)

**File:** `brahmand/kickoff.py`

**Cron:** `*/5 9-15 * * 1-5 python3 kickoff.py`

**Logic:**
```python
if has_active_trade:
    # Risk monitor handles, don't run crew
    skip()
elif should_enter():
    # No trade + gates pass
    run_full_5_agent_crew()
    write_to_trade_execution.duckdb()
else:
    # Cooldown or max trades reached
    skip()
```

**Checks:**
- Simple: `if state["active_trade"]`
- Risk monitor keeps DB in sync
- No expensive DB query in scheduler

---

## Part 3: Data & State Management

### **Trade Execution DB** (NEW May 20)

**File:** `brahmand/trade_execution.duckdb`

**Schema:**
```sql
active_trades
├─ trade_id (PK)
├─ entry_time
├─ strategy
├─ entry_gate_signal
├─ legs (JSON)
├─ sl (JSON)
├─ tp (JSON)
└─ status (ACTIVE | CLOSED)

trade_history  (for research)
├─ trade_id
├─ entry_time / close_time
├─ close_reason (SL_HIT | TP_HIT | MORPH)
├─ final_pnl
└─ duration_mins

monitoring_log  (audit trail)
├─ trade_id
├─ monitored_at
├─ current_ltp
├─ current_pnl
├─ action_taken
└─ note
```

**Purpose:**
- Risk monitor reads/writes
- Scheduler checks for active trades
- Research/post-mortem queries
- Queryable audit trail

---

### **Order Ledger** (Original)

**File:** `/tmp/order_ledger.json`

**Format:**
```json
{
  "orders": {
    "ORD-20260520-0001": {
      "order_id": "ORD-20260520-0001",
      "symbol": "NIFTY23750PE",
      "action_type": "SELL",
      "quantity": 65,
      "price": 150.0,
      "status": "FILLED",
      "trade_id": "TRADE-20260520-001",
      "timestamp": "2026-05-20T09:35:15",
      "execution_time": "2026-05-20T09:35:15"
    }
  },
  "order_counter": 1
}
```

**Dual-write (Order Agent):**
1. Fast check by scheduler
2. Updated by Risk Monitor when trade closes

---

### **Market Data v4** (With EMA)

**File:** `python-trader/varaha/data/market_data_multitf.duckdb`

**New (May 20):** EMA wiring into v4 aggregator

**EMA Support:**
- Timeframes: 1min, 5min, 15min, 60min, 1D
- Periods: 5, 9, 20, 50, 100, 200
- Updated via: `update_ema(close, tf="5min")`
- Files: `brahmand/ema_aggregator.py`, `ema_backfill.py`, `ema_integration_hook.py`

---

## Part 4: Governance & Dispatch Crews

### **CEO Crew** (Daily)

**Cron:** 
- 07:55 — Governance alignment
- 16:00 — EOD review
- 10:00 (Sunday) — Weekend readiness

**Role:** Strategic review, evaluate performance vs expectations

---

### **Asset Manager (AM) Crew** (Daily 08:55)

**Role:** Query broker margins, check capital limits, report to PM

---

### **Portfolio Manager (PM) Crew** (Daily 08:55)

**Role:** Read AM data, build strategy spec for day

---

### **Trading Analyst (TA) Crew** (Daily 09:18)

**Role:** Validate trades match PM spec, report PnL

---

### **Post-Analyst (PA) Crew** (Daily 16:00)

**Role:** Generate recommendations from DuckDB data

---

## Summary Table

| Agent/System | Type | Cadence | File | Output |
|---|---|---|---|---|
| **Scout** | CrewAI | Entry phase | agents/scout_agent.py | Regime + confidence |
| **Researcher** | CrewAI | Entry phase | agents/research_agent.py | Win rate, drawdown |
| **Strategist** | CrewAI | Entry phase | agents/strategist_agent.py | Trade structure (legs, SL, TP) |
| **Risk Guard** | Deterministic | Entry + 1min | risk_config.py | APPROVED/REJECTED |
| **Executor** | CrewAI | Entry execution | agents/executioner_agent.py | Order IDs, fills |
| **Sentinel** | Python script | 1-min | risk_monitor.py | SL/TP checks, exit orders |
| **Auditor** | CrewAI | Post-trade | agents/auditor_agent.py | JSONL audit log |
| **Order Agent** | Hub | On-demand | order_agent.py | Dual-write (JSON + DuckDB) |
| **Risk Monitor** | Cron | 1-min | risk_monitor.py | Active trade monitoring |
| **Pattern Enricher** | Cron | 5-min | pattern_enricher.py | Intraday patterns |
| **Margin Capture** | Cron | 5-min | margin_capture.py | Live margin data |
| **Data Health** | Cron | 5-min | data_health.py | Data integrity checks |
| **Leg Shifter** | Module | On-demand | leg_shifter.py | Shift proposals/execution |
| **Position Manager** | Module | On-demand | position_manager.py | Adaptive rules (roll, tighten, morph) |
| **Kickoff Scheduler** | Cron | 5-min | kickoff.py | Entry gate decisions |

---

## Critical Invariants (Never Violated)

1. **Capital Safe:** Account equity never negative
2. **SL Always Checked:** Before every order execution
3. **Max 4 Concurrent:** Hard limit, no exceptions
4. **Risk Guard → Executor:** No order without approval
5. **Audit Trail Complete:** Every trade logged immutably
6. **Order Agent Single Point:** All orders route through here
7. **Risk Monitor Authority:** Closes positions, not scheduler

---

## Monday 09:15 AM Go-Live Checklist

- ✅ 7-agent crew builds and runs
- ✅ EMA data flowing (v4 aggregator wired)
- ✅ Order ledger JSON + DuckDB dual-write
- ✅ Risk monitor 1-min cron active
- ✅ Risk Guard limits loaded
- ✅ Broker tokens fresh (07:00 cron)
- ✅ Scheduler checks simple, fast
- ✅ Telegram bridge ready
- ✅ Audit logging initialized

---

**Architecture by:** Claude (May 8-20, 2026)  
**Status:** Production. Ready for live trading Monday.
