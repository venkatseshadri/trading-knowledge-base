"""Permutation runner — backtest Iron Fly/Condor across the variable grid.

Permutations tested (initial cut):
  - Entry day:    Mon, Tue (per user's iron_fly_entry_calendar memory)
  - Entry time:   09:30, 10:00, 11:00, 13:00 (4 buckets)
  - Structure:    IB-100w, IB-150w, IB-200w, IC50-100w, IC100-200w (5)
  - SL %:         100%, 125%, 150%, 200% of credit (4)
  - TP rule:      ₹250/sh, ₹500/sh, 25%cred, 50%cred (4)

Total: 2 × 4 × 5 × 4 × 4 = 640 configurations × ~400 entry days = ~256k sims
"""
import numpy as np
import pandas as pd
from datetime import timedelta
from simulator import simulate_day, get_expiry_datetime
from pricer import realized_vol_annualized
import time
import sys


# Configuration grid
ENTRY_TIMES = ['09:30', '10:00', '11:00', '13:00']

STRUCTURES = [
    {'name': 'IB-100w',      'body_offset_pts': 0,   'hedge_distance_pts': 100},
    {'name': 'IB-150w',      'body_offset_pts': 0,   'hedge_distance_pts': 150},
    {'name': 'IB-200w',      'body_offset_pts': 0,   'hedge_distance_pts': 200},
    {'name': 'IC50-100w',    'body_offset_pts': 50,  'hedge_distance_pts': 100},
    {'name': 'IC100-200w',   'body_offset_pts': 100, 'hedge_distance_pts': 200},
]

SL_LEVELS = [1.0, 1.25, 1.5, 2.0]

TP_RULES = [
    {'name': 'TP-250inr',  'type': 'fixed',      'value': 250/75},   # ₹250/lot = ₹3.33/share
    {'name': 'TP-500inr',  'type': 'fixed',      'value': 500/75},
    {'name': 'TP-25pct',   'type': 'pct_credit', 'value': 0.25},
    {'name': 'TP-50pct',   'type': 'pct_credit', 'value': 0.50},
]

# Days of week we'll enter on (per user memory: NIFTY = Fri/Mon/Tue → Tue expiry)
# 0=Mon, 1=Tue, 4=Fri
ENTRY_DAYS_OF_WEEK = [0, 1]  # Start with Mon, Tue


def load_data(start_date='2022-01-01', end_date='2026-01-23'):
    """Load minute data and compute daily realized vol.

    Loads 60 trading days of buffer before start_date so realized vol
    is available from day 1 of the test window.
    """
    buffer_start = (pd.Timestamp(start_date) - pd.Timedelta(days=90)).strftime('%Y-%m-%d')
    print(f"Loading minute data {buffer_start} to {end_date} (with vol buffer)...")
    df = pd.read_csv('/home/trading_ceo/nifty_minute_2015_2026.csv')
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date').sort_index()
    df = df.loc[buffer_start:end_date]
    print(f"Loaded {len(df):,} minute bars")

    # Daily closes for vol computation
    daily_close = df['close'].groupby(df.index.date).last()
    daily_close.index = pd.to_datetime(daily_close.index)
    rv = realized_vol_annualized(daily_close, window=20)
    # Trim back to the actual test window
    df = df.loc[start_date:end_date]
    print(f"Computed 20-day realized vol for {len(rv):,} days")
    print(f"  Vol range: {rv.dropna().min():.3f} to {rv.dropna().max():.3f}")
    print(f"  Mean vol:  {rv.dropna().mean():.3f}")

    # Bump by 1.1× as IV proxy (IV typically richer than RV)
    iv_proxy = rv * 1.1
    return df, iv_proxy


def get_entry_days(df_index, days_of_week):
    """Get list of unique trading days matching the entry days-of-week filter."""
    days = pd.Series(df_index.date).unique()
    days = pd.to_datetime(days)
    return [d for d in days if d.weekday() in days_of_week]


def run_grid(start_date='2022-01-01', end_date='2026-01-23',
             max_days=None, output_csv='/home/trading_ceo/iron_fly_backtest/results.csv'):
    """Run the full permutation grid."""
    df, iv_proxy = load_data(start_date, end_date)

    entry_days = get_entry_days(df.index, ENTRY_DAYS_OF_WEEK)
    if max_days:
        entry_days = entry_days[:max_days]
    print(f"\nWill simulate {len(entry_days)} entry days")

    perm_count = (len(ENTRY_TIMES) * len(STRUCTURES) *
                  len(SL_LEVELS) * len(TP_RULES))
    total_sims = len(entry_days) * perm_count
    print(f"Permutations per day: {perm_count}")
    print(f"Total simulations:    {total_sims:,}")

    results = []
    t_start = time.time()

    for di, entry_day in enumerate(entry_days):
        # Get vol estimate for this day (use prior day's RV)
        prior_dates = iv_proxy.index[iv_proxy.index < entry_day]
        if len(prior_dates) == 0:
            continue
        vol = iv_proxy.loc[prior_dates[-1]]
        if pd.isna(vol):
            continue

        # Get expiry (next Tuesday)
        # entry_day might be Mon (0) or Tue (1); for Tue entry, it's same-day expiry
        entry_dt = pd.Timestamp(entry_day) + pd.Timedelta(hours=9, minutes=15)
        expiry_dt = get_expiry_datetime(entry_dt)

        # Get minute data from entry_day through expiry_day
        end_dt = pd.Timestamp(expiry_dt.date()) + pd.Timedelta(hours=15, minutes=30)
        day_data = df.loc[entry_dt:end_dt]
        if len(day_data) < 100:  # need at least some bars
            continue

        for entry_time in ENTRY_TIMES:
            for structure in STRUCTURES:
                for sl_pct in SL_LEVELS:
                    for tp_rule in TP_RULES:
                        try:
                            res = simulate_day(
                                day_minute_data=day_data,
                                entry_time_str=entry_time,
                                structure_config=structure,
                                sl_pct_of_credit=sl_pct,
                                tp_rule=tp_rule,
                                expiry_dt=expiry_dt,
                                vol=vol,
                            )
                            if res is None:
                                continue
                            res['entry_day_dow'] = entry_day.weekday()
                            res['entry_time_str'] = entry_time
                            res['structure_name'] = structure['name']
                            res['body_offset_pts'] = structure['body_offset_pts']
                            res['hedge_distance_pts'] = structure['hedge_distance_pts']
                            res['sl_pct_setting'] = sl_pct
                            res['tp_rule_name'] = tp_rule['name']
                            res['vol_estimate'] = vol
                            res['dte_days'] = (expiry_dt - entry_dt).days
                            results.append(res)
                        except Exception as e:
                            pass  # skip pricing failures silently

        # Progress
        if (di + 1) % 25 == 0 or di == len(entry_days) - 1:
            elapsed = time.time() - t_start
            rate = (di + 1) / elapsed
            eta = (len(entry_days) - di - 1) / rate
            print(f"  Day {di+1}/{len(entry_days)} ({entry_day.date()}) "
                  f"| {len(results):,} trades | {elapsed:.0f}s elapsed | ETA {eta:.0f}s")

    # Save results
    res_df = pd.DataFrame(results)
    res_df.to_csv(output_csv, index=False)
    print(f"\nSaved {len(res_df):,} trades to {output_csv}")
    return res_df


if __name__ == '__main__':
    # Smaller test first: 2024-2025 only, max 30 days
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        run_grid(start_date='2024-10-01', end_date='2024-12-31', max_days=10,
                 output_csv='/home/trading_ceo/iron_fly_backtest/results_smoke.csv')
    elif len(sys.argv) > 1 and sys.argv[1] == 'full':
        run_grid(start_date='2022-01-01', end_date='2026-01-23',
                 output_csv='/home/trading_ceo/iron_fly_backtest/results.csv')
    else:
        # Default: 2024-2025 (manageable size, recent data)
        run_grid(start_date='2024-01-01', end_date='2026-01-23',
                 output_csv='/home/trading_ceo/iron_fly_backtest/results_2024_2026.csv')
