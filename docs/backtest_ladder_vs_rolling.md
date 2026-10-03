# Continuous Ladder vs Rolling Legs — Iron Fly Management

**Companion to:**
- `/home/trading_ceo/backtest_analysis_corrected.md`
- `/home/trading_ceo/backtest_pnl_levers.md`

**Source data:** `/home/trading_ceo/backtest_results_corrected.csv` (62 trades)
**Date:** 2026-05-02

---

## What Each Approach Actually Is

### Continuous Ladder

Enter a fresh iron fly on a fixed cadence (every Monday, every 7-DTE rolldown, every fortnight), staggering across expiries so multiple flies are always live at different DTE buckets. Each fly is **passively managed** — exits only on mechanical rules (profit target, stop, expiry). You diversify across *time*, not adjustments. New legs start at fresh ATM each cycle.

### Rolling Legs

Hold fewer concurrent positions and **actively defend** them. When price tests one wing, roll the unchallenged side closer to spot to collect more credit (re-centering the breakevens), or roll the whole position out in time. The "trade" becomes a multi-cycle saga; final P&L includes all rolls.

---

## Dimension-by-Dimension Comparison

| Dimension | Continuous ladder | Rolling legs |
|---|---|---|
| **Theta capture** | Runs continuously across multiple DTE buckets — always paid, smoothed over time | Concentrated in fewer positions; adds re-credits via rolls but each roll resets DTE |
| **Capital usage** | Higher (multiple flies open at once); steady drawdown of margin | Lower base, but rolls *grow* margin as adjustments stack |
| **Loss per trade** | Bounded per fly; with stops, capped further | Unbounded in theory — a sequence of bad rolls can compound losses |
| **Regime sensitivity** | Roughly neutral; wins when average IV > realized over the cycle | **Highly asymmetric** — wins in choppy / mean-reverting tape, loses badly in trends |
| **Path dependence** | Low — each fly's outcome is independent of the others | Very high — every roll embeds a *directional bet* that the trend will reverse |
| **Operational load** | Low; calendar + exit rules can be coded once | High; needs real-time monitoring, judgment calls, regime reads |
| **Backtest fidelity** | Clean; easy to validate, hard to overfit | Notoriously hard; roll rules silently encode lookahead, win rates flatter than reality |
| **Drawdown shape** | Many small drawdowns, stochastic, recover via fresh entries | Long, slow burn on a single position; one bad sequence can dominate a year |
| **P&L distribution** | Slightly negatively skewed, fat-tailed but bounded | **Heavy left tail** — most months small wins, rare months catastrophic |
| **Compounding** | Smoother — winners and losers blend; theta and reversion are uncorrelated across expiries | Lumpy — a successful defended trade is a multi-x of one credit; a failed defense kills weeks of gains |

---

## What Your Data Tells Us

Your corrected backtest is essentially a **ladder already** — you entered multiple expiries on the same days (Oct 15, 17, 18, 23, 24, 28). The lessons:

- **Ladder of short-dated narrow flies** (36 trades, ≤150-pt wings): breakeven at +106 → ladder works structurally; just needs profit target + stop to clear costs and beat the winner/loser asymmetry.
- **Ladder of far-dated wide flies** (19 trades, 1000–2000-pt wings): bled −2,853 → ladder doesn't fix bad position selection. The fix is a DTE filter and a hard stop, *not* rolls.

### What if you'd rolled legs instead during this window?

NIFTY fell ~5% over Oct 15 → Oct 28, 2024 — a clean trending decline. The textbook defensive roll (move the call side down toward spot to collect more credit as puts get tested) would have:

1. Collected fresh credit on each roll → felt good intraday
2. Re-centered the position lower each time → kept selling into the trend
3. Built up cumulative short-delta exposure
4. Compounded the loss when the trend continued

**Rolling legs in a trending market is the classic way to turn a −1× credit loss into a −3× to −5× credit loss.** Your data window is precisely the regime where rolling underperforms ladder.

---

## Recommendation

For a **systematic, capital-efficient, backtestable** iron fly book → **continuous ladder is the right base.** It matches your existing setup, rewards mechanical discipline, and your data can be re-run with profit-target / stop-loss overlays without restructuring.

**Rolling legs is an *enhancement layer*, not a replacement** — and only worth adding if:

1. The ladder base shows positive expectancy with simple exits (i.e., Levers 1 + 2 from the prior report turn it green)
2. You add a regime filter (e.g., only roll when ADX < 20 or realized vol < implied vol)
3. You cap total rolls per position (e.g., max 1 defensive roll, then exit)

Without all three, rolling legs in a backtest will look great in choppy windows and catastrophic in trending ones — and you'll only learn which after you trade live.

---

## Concrete Next Experiments

Extends the experiment list from `backtest_pnl_levers.md`:

- **Variant 7a:** Ladder, no rolls — clean baseline (with profit target + stop loss + DTE filter from prior report)
- **Variant 7b:** Ladder + max-1-defensive-roll when tested side hits 1.5× credit MTM, with regime filter (ADX or realized-vs-implied-vol)
- **Variant 7c:** Pure rolling-legs (one position at a time, defended until stopped)

**Compare on:**
- Total P&L
- Profit factor
- **Max drawdown depth and time-to-recovery**
- **Worst-month P&L**

Rolling looks tempting on average return; it's the tail that decides whether it's actually tradeable. A strategy with higher mean P&L but a single −5× credit drawdown month is unlikely to survive in live trading even if its backtest looks clean.

---

## Bottom Line

| Question | Answer |
|---|---|
| Best base architecture? | **Continuous ladder** |
| When does ladder fail? | Bad position selection (e.g., wide-wing far-dated flies with no stop) |
| When does rolling win? | Choppy / mean-reverting markets, with strict roll caps and regime filter |
| When does rolling fail? | Trending markets — rolls amplify the loss |
| Should you mix them? | Only after the ladder base is proven profitable with simple exits |
| What's the trap? | Rolling-legs backtests overstate edge because roll rules embed lookahead |

Build the ladder right first. Add rolls only as a controlled enhancement, never as a way to rescue a losing position.
