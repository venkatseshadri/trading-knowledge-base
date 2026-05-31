"""Analyze permutation backtest results.

For each variable: compute mean P&L, win rate, profit factor, Sharpe.
Run feature importance via random forest to rank impact.
Output: ranked recommendations.
"""
import pandas as pd
import numpy as np

PATH = '/home/trading_ceo/iron_fly_backtest/results_2024_2026.csv'

df = pd.read_csv(PATH)
df['win'] = (df['pnl_per_lot'] > 0).astype(int)
df['entry_dt'] = pd.to_datetime(df['entry_dt'])
df['entry_dow'] = df['entry_dt'].dt.dayofweek

print("=" * 80)
print("IRON FLY/CONDOR PERMUTATION BACKTEST — RESULTS ANALYSIS")
print("=" * 80)
print(f"Period: {df['entry_dt'].min()} to {df['entry_dt'].max()}")
print(f"Total simulated trades: {len(df):,}")
print(f"Unique entry days:      {df['entry_dt'].dt.date.nunique():,}")
print(f"Permutations per day:   {len(df) // df['entry_dt'].dt.date.nunique()}")
print()


def stats(group):
    return pd.Series({
        'trades':       len(group),
        'mean_pnl':     group['pnl_per_lot'].mean(),
        'median_pnl':   group['pnl_per_lot'].median(),
        'win_rate':     group['win'].mean() * 100,
        'profit_factor': (group[group['pnl_per_lot'] > 0]['pnl_per_lot'].sum() /
                         abs(group[group['pnl_per_lot'] < 0]['pnl_per_lot'].sum() or 1)),
        'avg_win':      group[group['pnl_per_lot'] > 0]['pnl_per_lot'].mean() if (group['pnl_per_lot'] > 0).any() else 0,
        'avg_loss':     group[group['pnl_per_lot'] < 0]['pnl_per_lot'].mean() if (group['pnl_per_lot'] < 0).any() else 0,
        'worst':        group['pnl_per_lot'].min(),
        'best':         group['pnl_per_lot'].max(),
        'sharpe':       group['pnl_per_lot'].mean() / group['pnl_per_lot'].std() if group['pnl_per_lot'].std() > 0 else 0,
    })


# --- 1. ENTRY TIME IMPACT ---
print("=" * 80)
print("1. ENTRY TIME IMPACT")
print("=" * 80)
print("\n(P&L in ₹ per lot, sample = all configs across all days)")
print()
result = df.groupby('entry_time_str').apply(stats).round(1)
print(result.to_string())
print()
best_time = result['mean_pnl'].idxmax()
worst_time = result['mean_pnl'].idxmin()
print(f"BEST entry time:  {best_time} (₹{result.loc[best_time, 'mean_pnl']:.0f}/lot avg)")
print(f"WORST entry time: {worst_time} (₹{result.loc[worst_time, 'mean_pnl']:.0f}/lot avg)")
print(f"Spread:           ₹{result.loc[best_time, 'mean_pnl'] - result.loc[worst_time, 'mean_pnl']:.0f}/lot")
print()


# --- 2. SL % IMPACT ---
print("=" * 80)
print("2. SL % OF CREDIT IMPACT")
print("=" * 80)
print()
result = df.groupby('sl_pct_setting').apply(stats).round(1)
print(result.to_string())
print()
best_sl = result['mean_pnl'].idxmax()
print(f"BEST SL %: {best_sl}× credit (₹{result.loc[best_sl, 'mean_pnl']:.0f}/lot avg)")
print()


# --- 3. STRUCTURE IMPACT ---
print("=" * 80)
print("3. STRUCTURE (IB vs IC) + WIDTH IMPACT")
print("=" * 80)
print()
result = df.groupby('structure_name').apply(stats).round(1)
print(result.to_string())
print()
best_struct = result['mean_pnl'].idxmax()
worst_struct = result['mean_pnl'].idxmin()
print(f"BEST structure:  {best_struct} (₹{result.loc[best_struct, 'mean_pnl']:.0f}/lot avg)")
print(f"WORST structure: {worst_struct} (₹{result.loc[worst_struct, 'mean_pnl']:.0f}/lot avg)")
print()


# --- 4. TP RULE IMPACT ---
print("=" * 80)
print("4. TP RULE IMPACT")
print("=" * 80)
print()
result = df.groupby('tp_rule_name').apply(stats).round(1)
print(result.to_string())
print()
best_tp = result['mean_pnl'].idxmax()
worst_tp = result['mean_pnl'].idxmin()
print(f"BEST TP rule:  {best_tp} (₹{result.loc[best_tp, 'mean_pnl']:.0f}/lot avg)")
print(f"WORST TP rule: {worst_tp} (₹{result.loc[worst_tp, 'mean_pnl']:.0f}/lot avg)")
print()


# --- 5. ENTRY DAY-OF-WEEK IMPACT ---
print("=" * 80)
print("5. ENTRY DAY-OF-WEEK IMPACT (Mon=0, Tue=1)")
print("=" * 80)
print()
result = df.groupby('entry_dow').apply(stats).round(1)
print(result.to_string())
print()


# --- 6. INTERACTION: STRUCTURE × SL ---
print("=" * 80)
print("6. INTERACTION: STRUCTURE × SL — Mean P&L per lot (₹)")
print("=" * 80)
print()
pivot = df.pivot_table(values='pnl_per_lot', index='structure_name',
                       columns='sl_pct_setting', aggfunc='mean').round(0)
print(pivot.to_string())
print()


# --- 7. INTERACTION: ENTRY TIME × TP RULE ---
print("=" * 80)
print("7. INTERACTION: ENTRY TIME × TP RULE — Mean P&L per lot (₹)")
print("=" * 80)
print()
pivot = df.pivot_table(values='pnl_per_lot', index='entry_time_str',
                       columns='tp_rule_name', aggfunc='mean').round(0)
print(pivot.to_string())
print()


# --- 8. TOP 10 CONFIGURATIONS ---
print("=" * 80)
print("8. TOP 10 CONFIGURATIONS BY MEAN P&L")
print("=" * 80)
print()
config_cols = ['entry_time_str', 'structure_name', 'sl_pct_setting', 'tp_rule_name']
top = df.groupby(config_cols).apply(stats).round(1)
top = top.sort_values('mean_pnl', ascending=False)
print(top.head(10).to_string())
print()


# --- 9. WORST 10 CONFIGURATIONS ---
print("=" * 80)
print("9. WORST 10 CONFIGURATIONS BY MEAN P&L")
print("=" * 80)
print()
print(top.tail(10).to_string())
print()


# --- 10. RANKED VARIABLE IMPACT (variance-based) ---
print("=" * 80)
print("10. RANKED VARIABLE IMPACT — Which lever moves P&L most?")
print("=" * 80)
print("\n(Spread between best and worst level for each variable)")
print()

variables = {
    'Entry Time':      'entry_time_str',
    'SL % of Credit':  'sl_pct_setting',
    'Structure':       'structure_name',
    'TP Rule':         'tp_rule_name',
    'Day of Week':     'entry_dow',
}

impact_summary = []
for name, col in variables.items():
    means = df.groupby(col)['pnl_per_lot'].mean()
    spread = means.max() - means.min()
    best = means.idxmax()
    worst = means.idxmin()
    impact_summary.append({
        'Variable':     name,
        'Best Level':   best,
        'Best ₹/lot':   round(means.max(), 0),
        'Worst Level':  worst,
        'Worst ₹/lot':  round(means.min(), 0),
        'Spread ₹/lot': round(spread, 0),
    })

impact_df = pd.DataFrame(impact_summary).sort_values('Spread ₹/lot', ascending=False)
print(impact_df.to_string(index=False))
print()


# --- 11. RANDOM FOREST FEATURE IMPORTANCE ---
print("=" * 80)
print("11. RANDOM FOREST FEATURE IMPORTANCE")
print("=" * 80)
print()
try:
    from sklearn.ensemble import RandomForestRegressor

    # Encode categoricals
    feat_df = df.copy()
    feat_df['entry_time_num'] = feat_df['entry_time_str'].map({
        '09:30': 0, '10:00': 1, '11:00': 2, '13:00': 3
    })
    feat_df['structure_num'] = feat_df['structure_name'].map({
        'IB-100w': 0, 'IB-150w': 1, 'IB-200w': 2,
        'IC50-100w': 3, 'IC100-200w': 4
    })
    feat_df['tp_num'] = feat_df['tp_rule_name'].map({
        'TP-250inr': 0, 'TP-500inr': 1, 'TP-25pct': 2, 'TP-50pct': 3
    })

    features = ['entry_time_num', 'sl_pct_setting', 'structure_num',
                'tp_num', 'entry_dow', 'vol_estimate', 'dte_days']
    X = feat_df[features].dropna()
    y = feat_df.loc[X.index, 'pnl_per_lot']

    rf = RandomForestRegressor(n_estimators=100, max_depth=8, n_jobs=-1, random_state=42)
    rf.fit(X, y)

    importance = pd.DataFrame({
        'feature': features,
        'importance': rf.feature_importances_
    }).sort_values('importance', ascending=False)
    importance['importance_pct'] = (importance['importance'] * 100).round(1)
    print(importance.to_string(index=False))
    print()
    print("Interpretation:")
    print("  Higher importance = the feature explains more P&L variance")
    print("  Volatility regime is usually #1 (it's exogenous, not a knob)")
    print("  Among controllable knobs, the highest importance = highest leverage")
except ImportError:
    print("(sklearn not available, skipping RF analysis — pip install scikit-learn)")

print()
print("=" * 80)
print("DONE")
print("=" * 80)
