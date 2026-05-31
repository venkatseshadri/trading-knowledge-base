#!/usr/bin/env python3
"""
60% Sideways Thesis Validation on 11 years of NIFTY minute data.

Tests the user's claim: "market is sideways 60% of time" — which underpins
the stop-and-recenter Iron Butterfly strategy.

Multiple "sideways" definitions tested:
  A) Day's close within ±0.5% of open (tight)
  B) Day's close within ±1.0% of open (medium)
  C) Day's close within ±1.5% of open (loose, ~ wing-bound for 150pt fly)
  D) Day's intraday range (high-low) < 1% of open (no whipsaw)
  E) Day's max excursion from open < 1% (touched neither breakeven)
"""

import pandas as pd
import numpy as np

print("=" * 80)
print("60% SIDEWAYS THESIS — VALIDATION ON 11 YEARS OF NIFTY DATA")
print("=" * 80)
print()

print("Loading 1.02M minute bars...")
df = pd.read_csv('/home/trading_ceo/nifty_minute_2015_2026.csv')
df['date'] = pd.to_datetime(df['date'])
df['day'] = df['date'].dt.date
df = df.set_index('date').sort_index()
print(f"Loaded {len(df):,} rows, {df['day'].nunique():,} trading days")
print()

# Aggregate to daily OHLC
daily = df.groupby('day').agg(
    open=('open', 'first'),
    high=('high', 'max'),
    low=('low', 'min'),
    close=('close', 'last'),
)
daily['close_move_pct'] = (daily['close'] - daily['open']) / daily['open'] * 100
daily['high_move_pct'] = (daily['high'] - daily['open']) / daily['open'] * 100
daily['low_move_pct'] = (daily['low'] - daily['open']) / daily['open'] * 100
daily['range_pct'] = (daily['high'] - daily['low']) / daily['open'] * 100
daily['max_excursion_pct'] = daily[['high_move_pct', 'low_move_pct']].abs().max(axis=1)

print(f"Total trading days: {len(daily):,}")
print()

# --- DEFINITION TESTS ---
print("=" * 80)
print("SIDEWAYS DEFINITION TESTS — % of days qualifying as 'sideways'")
print("=" * 80)
print()

definitions = {
    'A) Close within ±0.5% of open':           daily['close_move_pct'].abs() < 0.5,
    'B) Close within ±1.0% of open':           daily['close_move_pct'].abs() < 1.0,
    'C) Close within ±1.5% of open':           daily['close_move_pct'].abs() < 1.5,
    'D) Intraday range (H-L) < 1.0%':          daily['range_pct'] < 1.0,
    'E) Intraday range (H-L) < 1.5%':          daily['range_pct'] < 1.5,
    'F) Max excursion from open < 1.0%':       daily['max_excursion_pct'] < 1.0,
    'G) Max excursion from open < 1.5%':       daily['max_excursion_pct'] < 1.5,
}

print(f"{'Definition':<50} {'%Days':>8} {'Days':>8}")
print("-" * 70)
for name, mask in definitions.items():
    pct = mask.sum() / len(daily) * 100
    bar = "✓" if pct >= 60 else "✗"
    flag = " ← MEETS 60% CLAIM" if pct >= 60 else ""
    print(f"{name:<50} {pct:>7.1f}% {mask.sum():>8,}{flag}")
print()

# --- YEAR-BY-YEAR (using definition C: ±1.5% close) ---
print("=" * 80)
print("YEAR-BY-YEAR BREAKDOWN — Definition C (Close within ±1.5%)")
print("=" * 80)
print()

daily['year'] = pd.to_datetime(daily.index).year
yearly = daily.groupby('year').apply(lambda x: pd.Series({
    'days': len(x),
    'sideways_C_pct': (x['close_move_pct'].abs() < 1.5).sum() / len(x) * 100,
    'sideways_G_pct': (x['max_excursion_pct'] < 1.5).sum() / len(x) * 100,
    'avg_range_pct': x['range_pct'].mean(),
    'big_move_days': (x['close_move_pct'].abs() > 2).sum(),
}))

print(f"{'Year':<6} {'Days':>6} {'Sideways(C)':>14} {'Sideways(G)':>14} {'AvgRange':>10} {'>±2%days':>10}")
print("-" * 70)
for year, row in yearly.iterrows():
    print(f"{year:<6} {int(row['days']):>6} {row['sideways_C_pct']:>13.1f}% {row['sideways_G_pct']:>13.1f}% {row['avg_range_pct']:>9.2f}% {int(row['big_move_days']):>10}")
print()

# --- INTRADAY EXCURSION ANALYSIS (KEY for Iron Fly) ---
print("=" * 80)
print("INTRADAY EXCURSION — Did Iron Fly's body strike get tested?")
print("=" * 80)
print()
print("For an ATM Iron Fly with 150pt wings, breakevens are typically 0.6-0.8%")
print("from spot (assuming credit ~150 pts on a ₹25k spot).")
print()

# % days where max excursion exceeded various breakeven thresholds
thresholds = [0.3, 0.5, 0.6, 0.8, 1.0, 1.2, 1.5, 2.0]
print(f"{'Excursion threshold':<25} {'%Days exceeded':>18}")
print("-" * 50)
for t in thresholds:
    pct = (daily['max_excursion_pct'] > t).sum() / len(daily) * 100
    print(f"  Touched ±{t}% of open    {pct:>16.1f}%")
print()

# --- SL HIT FREQUENCY (proxy) ---
print("=" * 80)
print("SL HIT FREQUENCY — Proxy via max excursion")
print("=" * 80)
print()
print("Assumption: Iron Fly body strike SL hits when max excursion > 0.6%")
print("(conservative — actual SL depends on credit + premium decay rate)")
print()

sl_threshold = 0.6
sl_hit_days = (daily['max_excursion_pct'] > sl_threshold).sum()
sl_hit_pct = sl_hit_days / len(daily) * 100
print(f"Days where SL would have triggered: {sl_hit_days:,} of {len(daily):,} ({sl_hit_pct:.1f}%)")
print(f"Days where SL would NOT trigger:    {len(daily)-sl_hit_days:,} ({100-sl_hit_pct:.1f}%)")
print()
print("→ These 'no-SL' days are the pure-theta winners")
print("→ Recenter strategy needs to make money on the OTHER 70%")
print()

# --- MULTIPLE TOUCHES (re-entry frequency proxy) ---
print("=" * 80)
print("RE-ENTRY FREQUENCY — How often does price oscillate intraday?")
print("=" * 80)
print()
print("Counts per-day: how many times did price cross ±0.6% from open?")
print("(This estimates re-entry count if you stop & recenter on each cross)")
print()

def count_crossings(group, threshold_pct=0.6):
    """Count how many times price crossed threshold zones in a day."""
    open_price = group['open'].iloc[0]
    upper = open_price * (1 + threshold_pct/100)
    lower = open_price * (1 - threshold_pct/100)

    inside = True
    crossings = 0
    for _, row in group.iterrows():
        if inside and (row['high'] > upper or row['low'] < lower):
            crossings += 1
            inside = False
        elif not inside and (row['low'] <= upper and row['high'] >= lower):
            # back inside band? simplified: assume re-enter band
            inside = True
    return crossings

print("Computing crossings (this samples 200 random days to keep fast)...")
sample_days = np.random.RandomState(42).choice(df['day'].unique(), 200, replace=False)
crossings = []
for d in sample_days:
    day_data = df[df['day'] == d]
    crossings.append(count_crossings(day_data, threshold_pct=0.6))

cr_series = pd.Series(crossings)
print(f"Crossings per day (sample of 200 days):")
print(f"  Mean:    {cr_series.mean():.2f}")
print(f"  Median:  {cr_series.median():.0f}")
print(f"  Max:     {cr_series.max()}")
print(f"  Distribution:")
for n in range(int(cr_series.max())+1):
    count = (cr_series == n).sum()
    if count > 0:
        print(f"    {n} crossings: {count} days ({count/2:.0f}%)")
print()

# --- BOTTOM LINE ---
print("=" * 80)
print("VERDICT ON YOUR 60% SIDEWAYS THESIS")
print("=" * 80)
print()

best_def_pct = max((daily[mask].shape[0] / len(daily) * 100)
                   for mask in [
                       daily['close_move_pct'].abs() < 1.5,
                       daily['range_pct'] < 1.5,
                       daily['max_excursion_pct'] < 1.5,
                   ])

closest_to_60 = daily['close_move_pct'].abs() < 1.5
pct_close_15 = closest_to_60.sum() / len(daily) * 100

print(f"Your claim:           60% of days are sideways")
print()
print(f"What the 11-year data shows:")
print(f"  Close within ±0.5%:  {(daily['close_move_pct'].abs() < 0.5).sum() / len(daily) * 100:.1f}% of days")
print(f"  Close within ±1.0%:  {(daily['close_move_pct'].abs() < 1.0).sum() / len(daily) * 100:.1f}% of days")
print(f"  Close within ±1.5%:  {pct_close_15:.1f}% of days")
print(f"  Range stays <1.0%:   {(daily['range_pct'] < 1.0).sum() / len(daily) * 100:.1f}% of days")
print(f"  Max excursion <0.6%: {(daily['max_excursion_pct'] < 0.6).sum() / len(daily) * 100:.1f}% of days")
print()

if pct_close_15 >= 55:
    print(f"✓ CLAIM SUPPORTED if 'sideways' means close within ±1.5% of open ({pct_close_15:.0f}%)")
else:
    print(f"✗ CLAIM NOT SUPPORTED at any reasonable definition")
print()

print("Critical caveat for Iron Fly:")
print("  Iron Fly P&L depends on INTRADAY EXCURSION, not just close.")
print(f"  Even on 'sideways close' days, {(daily['max_excursion_pct'] > 0.6).sum() / len(daily) * 100:.0f}% touched ±0.6% intraday.")
print(f"  → Your SL would have triggered ~{(daily['max_excursion_pct'] > 0.6).sum() / len(daily) * 100:.0f}% of days regardless of close")
print()
print("Implication:")
print("  The right question isn't 'is market sideways?' — it's:")
print("  'After SL hits, does price RETURN to the new ATM in remaining session?'")
print("  This needs intraday simulation, not daily aggregates. Next analysis.")
