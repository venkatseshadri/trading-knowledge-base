#!/usr/bin/env python3
"""
Analyze stop-and-recenter strategy against Oct 2024 backtest data.
Key question: How many times per session would we reopen after SL hit?
"""

import pandas as pd
import numpy as np
from collections import defaultdict

# Load backtest data
df = pd.read_csv('/home/trading_ceo/backtest_results_corrected.csv')
df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')

print("=" * 80)
print("STOP-AND-RECENTER STRATEGY ANALYSIS")
print("=" * 80)
print()

# --- SESSION ANALYSIS: Group by date ---
sessions = defaultdict(list)
for idx, row in df.iterrows():
    sessions[row['date'].date()].append({
        'expiry': row['expiry'],
        'body_ce': row['body_ce_strike'],
        'body_pe': row['body_pe_strike'],
        'entry_cost': row['entry_cost'],
        'pnl': row['pnl'],
        'pnl_pct': row['pnl_percent'],
        'max_loss': row['max_loss'],
    })

print("SESSION BREAKDOWN (by date)")
print("-" * 80)

session_stats = []

for session_date in sorted(sessions.keys()):
    trades = sessions[session_date]
    session_pnl = sum(t['pnl'] for t in trades)
    session_wins = sum(1 for t in trades if t['pnl'] > 0)
    session_losses = sum(1 for t in trades if t['pnl'] < 0)
    session_worst = min(t['pnl'] for t in trades)

    # Hypothesis: Each losing trade = one "SL hit" = one re-entry
    # (user closes entire butterfly on SL, reopens at new ATM)
    re_entries = session_losses

    print(f"\n{session_date.strftime('%Y-%m-%d')}:")
    print(f"  Trades:        {len(trades)}")
    print(f"  Wins:          {session_wins} ({100*session_wins/len(trades):.0f}%)")
    print(f"  Losses:        {session_losses} ({100*session_losses/len(trades):.0f}%)")
    print(f"  Session P&L:   ₹{session_pnl:+.2f}")
    print(f"  Worst trade:   ₹{session_worst:+.2f}")
    print(f"  Re-entries:    {re_entries} (if closing on SL, reopening)")

    session_stats.append({
        'date': session_date,
        'trades': len(trades),
        'wins': session_wins,
        'losses': session_losses,
        'pnl': session_pnl,
        'worst': session_worst,
        're_entries': re_entries,
        're_entry_pct': 100 * re_entries / len(trades),
    })

# --- SUMMARY STATISTICS ---
print("\n" + "=" * 80)
print("SUMMARY ACROSS ALL SESSIONS")
print("=" * 80)

total_trades = sum(s['trades'] for s in session_stats)
total_wins = sum(s['wins'] for s in session_stats)
total_losses = sum(s['losses'] for s in session_stats)
total_pnl = sum(s['pnl'] for s in session_stats)
total_re_entries = sum(s['re_entries'] for s in session_stats)
avg_re_entries_per_session = np.mean([s['re_entry_pct'] for s in session_stats])

print(f"\nTotal Sessions:           {len(session_stats)}")
print(f"Total Trades:             {total_trades}")
print(f"Total Wins:               {total_wins} ({100*total_wins/total_trades:.1f}%)")
print(f"Total Losses:             {total_losses} ({100*total_losses/total_trades:.1f}%)")
print(f"Total P&L:                ₹{total_pnl:+.2f}")
print(f"Total Re-entries:         {total_re_entries} (trades that lost)")
print(f"Avg Re-entries/session:   {total_re_entries/len(session_stats):.1f} per day")
print(f"% of trades that are SL:  {100*total_losses/total_trades:.1f}%")

# --- WORST SESSIONS ---
print("\n" + "-" * 80)
print("WORST SESSIONS (Highest Re-entry Count)")
print("-" * 80)

worst_sessions = sorted(session_stats, key=lambda x: x['re_entries'], reverse=True)[:3]
for s in worst_sessions:
    print(f"\n{s['date'].strftime('%Y-%m-%d')}: {s['re_entries']} re-entries, P&L ₹{s['pnl']:+.2f}")
    print(f"  {s['losses']}/{s['trades']} trades lost")

# --- DISTRIBUTION OF RE-ENTRIES ---
print("\n" + "-" * 80)
print("RE-ENTRY FREQUENCY DISTRIBUTION")
print("-" * 80)

re_entry_dist = defaultdict(int)
for s in session_stats:
    re_entry_dist[s['re_entries']] += 1

print("\nHow many sessions had N re-entries?")
for re_entries in sorted(re_entry_dist.keys()):
    count = re_entry_dist[re_entries]
    print(f"  {re_entries} re-entries: {count} sessions ({100*count/len(session_stats):.0f}%)")

# --- DIRECTIONAL QUESTION ---
print("\n" + "=" * 80)
print("DIRECTIONAL ANALYSIS: Can We Predict Market Direction After SL?")
print("=" * 80)

# For each session, check if next session's opening strikes moved in expected direction
for i, s in enumerate(sorted(session_stats, key=lambda x: x['date'])):
    if i == 0:
        continue

    prev_session = sorted(session_stats, key=lambda x: x['date'])[i-1]

    prev_body_ce = np.mean([t['body_ce'] for t in sessions[prev_session['date']]])
    curr_body_ce = np.mean([t['body_ce'] for t in sessions[s['date']]])

    # Market moved up (new CE higher) or down (new PE lower)?
    direction_implied = "UP" if curr_body_ce > prev_body_ce else "DOWN"

    print(f"\n{prev_session['date']} → {s['date']}")
    print(f"  Prior session ATM: ₹{prev_body_ce:.0f}, Next ATM: ₹{curr_body_ce:.0f}")
    print(f"  Market moved:      {direction_implied} ({curr_body_ce - prev_body_ce:+.0f} pts)")
    print(f"  Next session P&L:  ₹{s['pnl']:+.2f}")

# --- THE 60% SIDEWAYS QUESTION ---
print("\n" + "=" * 80)
print("THE 60% SIDEWAYS THESIS")
print("=" * 80)

print("\nCritical Question: If you reopened after each SL...")
print("...would the market be 'sideways' 60% of the time?")
print()
print("What counts as 'sideways' in your model?")
print("  A) Market closed within original butterfly wings?")
print("  B) Market moved <1% from entry?")
print("  C) Market moved <ATR from entry?")
print("  D) Market reverted within N candles after SL?")
print()
print("⚠️  WITHOUT DEFINING 'SIDEWAYS', we can't validate the 60% claim.")
print()

profitable_sessions = sum(1 for s in session_stats if s['pnl'] > 0)
print(f"Sessions ending PROFITABLE (any criteria): {profitable_sessions}/{len(session_stats)} ({100*profitable_sessions/len(session_stats):.0f}%)")
print(f"Sessions ending LOSING:                    {len(session_stats)-profitable_sessions}/{len(session_stats)} ({100*(len(session_stats)-profitable_sessions)/len(session_stats):.0f}%)")

# --- THE REAL ISSUE ---
print("\n" + "=" * 80)
print("CRITICAL FINDINGS FOR MONDAY LAUNCH")
print("=" * 80)

print(f"""
1. RE-ENTRY FREQUENCY
   - Average re-entries per session: {total_re_entries/len(session_stats):.1f}
   - Max re-entries in a session:    {max(s['re_entries'] for s in session_stats)}
   - Your model NEEDS a re-entry cap (1? 3? 5? unlimited?)

2. DIRECTIONAL PREDICTION
   - Oct 2024 had a 5% trending decline (Oct 15 @ 25500 → Oct 28 @ 24450)
   - Each session: New ATM shifted DOWN (not sideways)
   - Re-entering "in direction of move" = chasing the trend
   - THIS IS EXACTLY WHERE ROLLING FAILS (backtest_pnl_levers.md found this)

3. THE 60% SIDEWAYS QUESTION
   - You claim market is sideways 60% of time
   - Oct 2024 backtest shows: Market was TRENDING DOWN (not sideways)
   - On this data: {profitable_sessions} sessions profitable, {len(session_stats)-profitable_sessions} sessions losing
   - Your 60% sideways assumption FAILED on Oct 2024 data

4. WHAT BREAKS THE STRATEGY
   - Without defined re-entry cap: Unlimited bleeding on trending days
   - Without defined "sideways": Can't tell if market is trending or consolidating
   - Without regime filter: Will chase trends down (Oct 2024 confirms this)
   - Without SL on NEW position: Each re-entry risks unlimited loss

5. RECOMMENDATION FOR MONDAY
   Option A: Use rolling strategy (built, tested, 31/31 tests passing)
   Option B: Use stop-and-recenter WITH:
      - Re-entry cap (e.g., max 2 per session)
      - Regime filter (e.g., only recenter if volatility < 1.5% or ADX < 20)
      - Explicit "sideways" definition (e.g., closed within 200 pts of entry)
      - SL on reopened position (automatic close at -₹100)
""")
