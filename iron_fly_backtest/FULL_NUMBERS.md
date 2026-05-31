# Iron Fly/Condor Permutation Backtest — Raw Numbers

**Period:** 2024-01-01 to 2026-01-20
**Entry days:** 209 (Mon + Tue only)
**Configurations:** 640 (Day × Time × Structure × SL × TP) = 2 × 4 × 5 × 4 × 4
**Total simulated trades:** 66,880
**P&L unit:** ₹ per lot (lot size = 75)

**Pricing model:** Black-Scholes; vol = 20-day realized × 1.1 (IV proxy, no real options chain)
**Excludes:** bid-ask slippage, brokerage, IV smile/skew, IV crush events

---

## Variable Grid

| Dimension | Levels |
|---|---|
| Entry day-of-week | Mon (0), Tue (1) |
| Entry time | 09:30, 10:00, 11:00, 13:00 |
| Structure | IB-100w, IB-150w, IB-200w, IC50-100w, IC100-200w |
| SL × credit | 1.00, 1.25, 1.50, 2.00 |
| TP rule | TP-250inr (₹250/sh fixed), TP-500inr, TP-25pct (of credit), TP-50pct (of credit) |

Structure encoding: `IB-Nw` = Iron Butterfly, body at ATM, wings ±N pts. `ICA-Bw` = Iron Condor, body offset ±A pts from ATM, wings B pts further out.

---

## 1. Entry Time

| Time | Trades | Mean ₹ | Median ₹ | Win % | PF | Avg Win | Avg Loss | Worst | Best | Sharpe |
|---|---|---|---|---|---|---|---|---|---|---|
| 09:30 | 16,720 | 974 | 610 | 83.5 | 3.9 | 1,572 | -2,051 | -9,987 | 7,728 | 0.5 |
| 10:00 | 16,720 | 997 | 702 | 84.6 | 4.1 | 1,564 | -2,113 | -9,567 | 7,385 | 0.5 |
| 11:00 | 16,720 | 1,126 | 877 | 87.1 | 5.0 | 1,618 | -2,212 | -9,907 | 7,583 | 0.6 |
| 13:00 | 16,720 | 1,118 | 868 | 87.8 | 5.0 | 1,589 | -2,270 | -9,130 | 7,378 | 0.6 |

## 2. SL % of Credit

| SL × | Trades | Mean ₹ | Median ₹ | Win % | PF | Avg Win | Avg Loss | Worst | Best | Sharpe |
|---|---|---|---|---|---|---|---|---|---|---|
| 1.00 | 16,720 | 1,054 | 770 | 85.6 | 4.5 | 1,587 | -2,105 | -7,741 | 7,728 | 0.5 |
| 1.25 | 16,720 | 1,054 | 775 | 85.7 | 4.5 | 1,586 | -2,140 | -8,251 | 7,728 | 0.5 |
| 1.50 | 16,720 | 1,054 | 780 | 85.8 | 4.4 | 1,586 | -2,165 | -8,939 | 7,728 | 0.5 |
| 2.00 | 16,720 | 1,053 | 782 | 85.9 | 4.4 | 1,586 | -2,195 | -9,987 | 7,728 | 0.5 |

## 3. Structure

| Structure | Trades | Mean ₹ | Median ₹ | Win % | PF | Avg Win | Avg Loss | Worst | Best | Sharpe | Avg Credit |
|---|---|---|---|---|---|---|---|---|---|---|---|
| IB-100w     | 13,376 | 572   | 520   | 78.2 | 3.6 | 1,017 | -1,029 | -3,065 | 3,935 | 0.5 | 6,122 |
| IB-150w     | 13,376 | 1,014 | 1,015 | 83.4 | 4.0 | 1,617 | -2,024 | -5,764 | 5,677 | 0.5 | 8,279 |
| IB-200w     | 13,376 | 1,409 | 1,500 | 87.5 | 4.3 | 2,095 | -3,396 | -9,130 | 7,408 | 0.6 | 9,980 |
| IC50-100w   | 13,376 | 804   | 912   | 86.4 | 4.2 | 1,222 | -1,836 | -4,969 | 4,157 | 0.6 | 4,884 |
| IC100-200w  | 13,376 | 1,469 | 792   | 93.2 | 5.9 | 1,896 | -4,410 | -9,987 | 7,728 | 0.6 | 6,284 |

## 4. TP Rule

| TP Rule | Trades | Mean ₹ | Median ₹ | Win % | PF | Avg Win | Avg Loss | Worst | Best | Sharpe |
|---|---|---|---|---|---|---|---|---|---|---|
| TP-250inr | 16,720 | 524   | 270   | 95.6 | 5.5 | 669   | -2,623 | -9,567 | 6,214 | 0.5 |
| TP-500inr | 16,720 | 833   | 541   | 93.2 | 5.8 | 1,081 | -2,562 | -9,567 | 7,583 | 0.6 |
| TP-25pct  | 16,720 | 1,187 | 1,566 | 80.8 | 4.0 | 1,957 | -2,065 | -9,567 | 7,728 | 0.6 |
| TP-50pct  | 16,720 | 1,671 | 2,008 | 73.4 | 4.1 | 3,013 | -2,030 | -9,987 | 7,728 | 0.6 |

## 5. Entry Day of Week

| DOW | Trades | Mean ₹ | Median ₹ | Win % | PF | Avg Win | Avg Loss | Worst | Best | Sharpe |
|---|---|---|---|---|---|---|---|---|---|---|
| Mon (0) | 32,640 | 1,615 | 1,550 | 85.7 | 8.1 | 2,148 | -1,577 | -7,014 | 7,728 | 0.8 |
| Tue (1) | 34,240 | 519   | 510   | 85.8 | 2.4 | 1,051 | -2,705 | -9,987 | 5,638 | 0.3 |

---

## 6. Interaction: Structure × SL — Mean ₹/lot

| Structure \ SL× | 1.00 | 1.25 | 1.50 | 2.00 |
|---|---|---|---|---|
| IB-100w     | 572   | 572   | 572   | 572   |
| IB-150w     | 1,014 | 1,013 | 1,014 | 1,014 |
| IB-200w     | 1,399 | 1,405 | 1,416 | 1,417 |
| IC50-100w   | 804   | 802   | 804   | 807   |
| IC100-200w  | 1,482 | 1,478 | 1,464 | 1,453 |

## 7. Interaction: Entry Time × TP Rule — Mean ₹/lot

| Time \ TP | TP-250inr | TP-500inr | TP-25pct | TP-50pct |
|---|---|---|---|---|
| 09:30 | 413 | 718 | 1,125 | 1,639 |
| 10:00 | 411 | 743 | 1,183 | 1,650 |
| 11:00 | 539 | 935 | 1,248 | 1,782 |
| 13:00 | 733 | 937 | 1,190 | 1,613 |

## 8. Interaction: DOW × Structure — Mean ₹/lot

| Structure \ DOW | Mon | Tue |
|---|---|---|
| IB-100w     | 741   | 410 |
| IB-150w     | 1,440 | 608 |
| IB-200w     | 2,142 | 711 |
| IC50-100w   | 1,211 | 417 |
| IC100-200w  | 2,540 | 449 |

## 9. Interaction: DOW × TP Rule — Mean ₹/lot

| TP \ DOW | Mon | Tue |
|---|---|---|
| TP-250inr | 949   | 119   |
| TP-500inr | 1,448 | 247   |
| TP-25pct  | 1,759 | 641   |
| TP-50pct  | 2,303 | 1,069 |

## 10. Interaction: Structure × TP Rule — Mean ₹/lot

| Structure \ TP | TP-250inr | TP-500inr | TP-25pct | TP-50pct |
|---|---|---|---|---|
| IB-100w    | 339 | 408   | 656   | 884   |
| IB-150w    | 626 | 727   | 1,075 | 1,627 |
| IB-200w    | 642 | 1,083 | 1,530 | 2,381 |
| IC50-100w  | 566 | 665   | 791   | 1,196 |
| IC100-200w | 446 | 1,283 | 1,881 | 2,267 |

---

## 11. Variable Spread Ranking (best level − worst level)

| Variable | Best Level | Best ₹ | Worst Level | Worst ₹ | Spread ₹ |
|---|---|---|---|---|---|
| TP Rule        | TP-50pct    | 1,671 | TP-250inr | 524   | 1,147 |
| Day of Week    | Mon         | 1,615 | Tue       | 519   | 1,096 |
| Structure      | IC100-200w  | 1,469 | IB-100w   | 572   | 898   |
| Entry Time     | 11:00       | 1,126 | 09:30     | 974   | 152   |
| SL % of Credit | 1.25        | 1,054 | 2.00      | 1,053 | 2     |

## 12. Random Forest Feature Importance (P&L variance explained)

| Feature | Importance | % |
|---|---|---|
| vol_estimate    | 0.4225 | 42.3 |
| tp_num          | 0.1718 | 17.2 |
| structure_num   | 0.1602 | 16.0 |
| entry_dow       | 0.1500 | 15.0 |
| dte_days        | 0.0496 | 5.0  |
| entry_time_num  | 0.0457 | 4.6  |
| sl_pct_setting  | 0.0001 | 0.0  |

Model: RandomForestRegressor(n_estimators=100, max_depth=8). Target = pnl_per_lot. Features as encoded ints.

---

## 13. Vol Regime Buckets

| Vol Bucket | Trades | Mean ₹ | Median ₹ | Win % | Avg Credit |
|---|---|---|---|---|---|
| Low (<10%)        | 18,560 | 1,162 | 854 | 90.0 | 6,249 |
| Medium (10–13%)   | 25,280 | 869   | 631 | 80.0 | 6,889 |
| High (13–16%)     |  9,920 | 933   | 770 | 80.0 | 7,528 |
| Very High (>16%)  | 13,120 | 1,348 | 987 | 90.0 | 8,436 |

## 14. Exit Reason Breakdown

| Exit Reason | Trades | % of All | Mean ₹ | Win % |
|---|---|---|---|---|
| TP            | 52,018 | 77.8 | 1,557  | 100.0 |
| EOD           | 14,177 | 21.2 | -544   | 40.0  |
| SL            |    669 | 1.0  | -4,290 | 0.0   |
| EOD_DATA_END  |     16 | 0.0  | 2,149  | 100.0 |

## 15. Duration to Exit (minutes)

| Exit | Count | Mean | Std | Min | 25% | 50% | 75% | Max |
|---|---|---|---|---|---|---|---|---|
| SL  |    669 | 121   |  79 |    8 |   57 |   106 |   169 |   330 |
| TP  | 52,018 | 709   | 650 |    8 |   88 |   272 | 1,395 | 1,770 |
| EOD | 14,177 | 939   | 726 |  120 |  240 |   330 | 1,740 | 1,770 |

## 16. P&L Distribution Percentiles (all 66,880 trades)

| Pct | ₹/lot |
|---|---|
| 1%  | -5,451 |
| 5%  | -2,338 |
| 10% | -975   |
| 25% | 264    |
| 50% | 778    |
| 75% | 2,008  |
| 90% | 3,405  |
| 95% | 4,518  |
| 99% | 5,905  |

## 17. Credit Collected by Structure (₹/lot)

| Structure | Avg | Median | Min | Max |
|---|---|---|---|---|
| IB-100w     | 6,122 | 6,437  | 3,365 | 7,191  |
| IB-150w     | 8,279 | 8,893  | 3,514 | 10,563 |
| IB-200w     | 9,980 | 10,890 | 3,529 | 13,787 |
| IC50-100w   | 4,884 | 5,414  | 962   | 6,893  |
| IC100-200w  | 6,284 | 7,263  | 164   | 12,605 |

---

## 18. Top 20 Configurations by Mean P&L

| Rank | DOW | Time | Structure | SL× | TP | N | Mean ₹ | Median | Std | Win% | PF | Worst | Best | Sharpe |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Mon | 13:00 | IC100-200w | 1.50 | TP-50pct | 102 | 3,835 | 4,513 | 2,656 | 90.0 | 12.3 | -7,014 | 7,378 | 1.44 |
| 2 | Mon | 13:00 | IC100-200w | 2.00 | TP-50pct | 102 | 3,835 | 4,513 | 2,656 | 90.0 | 12.3 | -7,014 | 7,378 | 1.44 |
| 3 | Mon | 13:00 | IC100-200w | 1.00 | TP-50pct | 102 | 3,835 | 4,513 | 2,656 | 90.0 | 12.3 | -7,014 | 7,378 | 1.44 |
| 4 | Mon | 13:00 | IC100-200w | 1.25 | TP-50pct | 102 | 3,835 | 4,513 | 2,656 | 90.0 | 12.3 | -7,014 | 7,378 | 1.44 |
| 5 | Mon | 11:00 | IC100-200w | 1.50 | TP-50pct | 102 | 3,784 | 4,702 | 2,966 | 90.0 | 9.1  | -6,560 | 7,583 | 1.28 |
| 6 | Mon | 11:00 | IC100-200w | 1.25 | TP-50pct | 102 | 3,784 | 4,702 | 2,966 | 90.0 | 9.1  | -6,560 | 7,583 | 1.28 |
| 7 | Mon | 11:00 | IC100-200w | 2.00 | TP-50pct | 102 | 3,784 | 4,702 | 2,966 | 90.0 | 9.1  | -6,560 | 7,583 | 1.28 |
| 8 | Mon | 11:00 | IC100-200w | 1.00 | TP-50pct | 102 | 3,784 | 4,702 | 2,966 | 90.0 | 9.1  | -6,560 | 7,583 | 1.28 |
| 9 | Mon | 10:00 | IC100-200w | 1.50 | TP-50pct | 102 | 3,620 | 4,724 | 2,940 | 90.0 | 9.4  | -6,435 | 6,318 | 1.23 |
|10 | Mon | 10:00 | IC100-200w | 2.00 | TP-50pct | 102 | 3,620 | 4,724 | 2,940 | 90.0 | 9.4  | -6,435 | 6,318 | 1.23 |

(Full 640-row sorted table in `all_configs_full_stats.csv`.)

## 19. Bottom 10 Configurations by Mean P&L

| DOW | Time | Structure | SL× | TP | N | Mean ₹ | Win% | Worst | Best |
|---|---|---|---|---|---|---|---|---|---|
| Tue | 10:00 | IC100-200w | 2.00 | TP-250inr | 107 | 204 | 97.6 | -7,869 | 4,908 |
| Tue | 11:00 | IC100-200w | 1.25 | TP-250inr | 107 | 222 | 97.1 | -5,488 | 3,980 |
| Tue | 11:00 | IC100-200w | 1.00 | TP-250inr | 107 | 225 | 96.7 | -4,535 | 3,980 |
| Tue | 11:00 | IC100-200w | 1.50 | TP-250inr | 107 | 238 | 97.6 | -5,991 | 3,980 |
| Tue | 10:00 | IC100-200w | 1.50 | TP-250inr | 107 | 238 | 97.6 | -6,439 | 4,908 |
| Tue | 10:00 | IC100-200w | 1.00 | TP-250inr | 107 | 248 | 96.7 | -4,211 | 4,908 |
| Tue | 10:00 | IC100-200w | 1.25 | TP-250inr | 107 | 257 | 97.6 | -5,668 | 4,908 |
| Tue | 09:30 | IC100-200w | 2.00 | TP-250inr | 107 | 285 | 97.6 | -5,115 | 4,861 |
| Tue | 09:30 | IC100-200w | 1.00 | TP-250inr | 107 | 294 | 97.1 | -3,899 | 4,861 |
| Tue | 09:30 | IC100-200w | 1.25 | TP-250inr | 107 | 297 | 97.6 | -4,614 | 4,861 |

---

## Files

- `all_configs_full_stats.csv` — All 640 configurations × full stats (n, mean, median, std, win_rate, profit_factor, avg_win, avg_loss, worst, best, avg_credit, sharpe), sorted by mean P&L descending.
- `results_2024_2026.csv` — Raw per-trade output (66,880 rows): entry_dt, exit_dt, duration_min, all 4 strikes, credit, P&L, exit reason, MAE, MFE, vol_used, plus all config columns.
- `runner.py`, `simulator.py`, `pricer.py`, `analyze.py` — Source.
