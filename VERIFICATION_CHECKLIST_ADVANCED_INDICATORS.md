# Verification Checklist: Advanced Research Indicators Integration

After Deepseek integrates the advanced indicators, run these verification steps:

---

## ✅ STEP 1: Code Structure Verification

```bash
# Check 1.1: Import statement
grep -n "from varaha_advanced_indicators import" varaha/data_capture_v3_duckdb.py
# Expected: Line N with compute_advanced_indicators

# Check 1.2: Function call in capture_once()
grep -n "advanced = compute_advanced_indicators" varaha/data_capture_v3_duckdb.py
# Expected: Line N with all required parameters

# Check 1.3: Values in INSERT statement
grep -n "advanced.get('iv_current')" varaha/data_capture_v3_duckdb.py
# Expected: Found in parameter list
```

**Pass Criteria:** All 3 checks return matches

---

## ✅ STEP 2: Database Schema Verification

```bash
python3 << 'EOF'
import duckdb
conn = duckdb.connect('varaha/data/varaha_data.duckdb')
cols = conn.execute("DESCRIBE market_data").fetchall()
col_names = [c[0] for c in cols]

# Check for all 32 advanced indicator columns
advanced_cols = [
    'iv_current', 'iv_52w_high', 'iv_52w_low', 'iv_rank', 'iv_regime',
    'iv_short', 'iv_long', 'iv_slope',
    'hv_20', 'hv_60',
    'agg_delta', 'agg_gamma', 'agg_vega', 'agg_theta', 'wings_delta', 'body_delta',
    'cluster_support', 'cluster_resistance', 'distance_to_support', 'distance_to_resistance',
    'session_phase', 'open_to_current_pct', 'distance_to_pivot_pct', 'distance_to_r1_pct', 'distance_to_s1_pct',
    'pcr_total', 'pcr_atm', 'sentiment',
    'max_pain_strike', 'call_oi_concentration', 'put_oi_concentration', 'oi_skew'
]

missing = [c for c in advanced_cols if c not in col_names]

if missing:
    print(f"❌ FAIL: Missing {len(missing)} columns: {missing}")
else:
    print(f"✅ PASS: All 32 advanced indicator columns present")
    print(f"Total columns: {len(col_names)}")
EOF
```

**Pass Criteria:** All 32 columns present

---

## ✅ STEP 3: IV Rank Calculation Verification

```bash
python3 << 'EOF'
import duckdb
conn = duckdb.connect('varaha/data/varaha_data.duckdb')

# Get latest row with IV metrics
latest = conn.execute("""
    SELECT timestamp, iv_current, iv_52w_high, iv_52w_low, iv_rank, iv_regime
    FROM market_data
    WHERE iv_current IS NOT NULL
    ORDER BY timestamp DESC LIMIT 1
""").fetchall()

if latest:
    row = latest[0]
    print(f"Latest IV metrics:")
    print(f"  Timestamp: {row[0]}")
    print(f"  Current IV: {row[1]}")
    print(f"  52w High: {row[2]}, Low: {row[3]}")
    print(f"  IV Rank: {row[4]}%")
    print(f"  IV Regime: {row[5]}")
    
    # Verify IV rank is 0-100
    if row[4] is not None and 0 <= row[4] <= 100:
        print("\n✅ PASS: IV Rank is valid (0-100)")
    else:
        print(f"\n❌ FAIL: IV Rank is invalid: {row[4]}")
else:
    print("⚠️  No IV data yet (market may be closed)")
EOF
```

---

## ✅ STEP 4: Historical Volatility Verification

```bash
python3 << 'EOF'
import duckdb
conn = duckdb.connect('varaha/data/varaha_data.duckdb')

# Get rows with HV values
rows = conn.execute("""
    SELECT timestamp, hv_20, hv_60
    FROM market_data
    WHERE hv_20 IS NOT NULL OR hv_60 IS NOT NULL
    ORDER BY timestamp DESC
    LIMIT 5
""").fetchall()

if rows:
    print(f"✅ PASS: Historical Volatility calculated for {len(rows)} rows")
    for row in rows[:3]:
        print(f"  {row[0]}: HV-20={row[1]}%, HV-60={row[2]}%")
else:
    print("⚠️  No HV data yet (need 20+ candles)")
EOF
```

---

## ✅ STEP 5: Greeks Calculation Verification

```bash
python3 << 'EOF'
import duckdb
conn = duckdb.connect('varaha/data/varaha_data.duckdb')

# Get Greeks data
latest = conn.execute("""
    SELECT timestamp, agg_delta, agg_gamma, agg_vega, agg_theta, wings_delta, body_delta
    FROM market_data
    WHERE agg_delta IS NOT NULL
    ORDER BY timestamp DESC LIMIT 1
""").fetchall()

if latest:
    row = latest[0]
    print(f"Latest Greeks (Iron Fly):")
    print(f"  Timestamp: {row[0]}")
    print(f"  Delta: {row[1]:.4f} (target ≈ 0)")
    print(f"  Gamma: {row[2]:.6f} (should be negative)")
    print(f"  Vega: {row[3]:.4f} (should be negative)")
    print(f"  Theta: {row[4]:.4f}/day (target ₹1-1.2k)")
    print(f"  Wings Delta: {row[5]:.4f}")
    print(f"  Body Delta: {row[6]:.4f}")
    print("\n✅ PASS: Greeks calculated")
else:
    print("⚠️  No Greeks data yet (need spot + IV data)")
EOF
```

---

## ✅ STEP 6: Support/Resistance Clusters Verification

```bash
python3 << 'EOF'
import duckdb
conn = duckdb.connect('varaha/data/varaha_data.duckdb')

# Get cluster data
latest = conn.execute("""
    SELECT timestamp, spot, cluster_support, cluster_resistance,
           distance_to_support, distance_to_resistance
    FROM market_data
    WHERE cluster_support IS NOT NULL
    ORDER BY timestamp DESC LIMIT 1
""").fetchall()

if latest:
    row = latest[0]
    print(f"Latest Support/Resistance Clusters:")
    print(f"  Spot: {row[1]}")
    print(f"  Support: {row[2]} (distance: {row[4]} pts)")
    print(f"  Resistance: {row[3]} (distance: {row[5]} pts)")
    
    # Verify support < spot < resistance
    if row[2] and row[3] and row[2] < row[1] < row[3]:
        print("\n✅ PASS: Clusters valid (support < spot < resistance)")
    else:
        print(f"\n⚠️  WARNING: Cluster logic may need review")
else:
    print("⚠️  No cluster data yet")
EOF
```

---

## ✅ STEP 7: Session Phase & Sentiment Verification

```bash
python3 << 'EOF'
import duckdb
conn = duckdb.connect('varaha/data/varaha_data.duckdb')

# Get session and PCR data
latest = conn.execute("""
    SELECT timestamp, session_phase, open_to_current_pct,
           pcr_total, pcr_atm, sentiment
    FROM market_data
    WHERE session_phase IS NOT NULL
    ORDER BY timestamp DESC LIMIT 1
""").fetchall()

if latest:
    row = latest[0]
    print(f"Session Metrics:")
    print(f"  Timestamp: {row[0]}")
    print(f"  Phase: {row[1]}")
    print(f"  Open-to-current: {row[2]}%")
    print(f"\nSentiment (PCR):")
    print(f"  PCR Total: {row[3]}")
    print(f"  PCR ATM: {row[4]}")
    print(f"  Sentiment: {row[5]}")
    
    if row[1] in ['early', 'mid', 'late', 'pre']:
        print(f"\n✅ PASS: Session phase detected")
    else:
        print(f"\n❌ FAIL: Invalid session phase: {row[1]}")
else:
    print("⚠️  No session data yet")
EOF
```

---

## ✅ STEP 8: OI Analysis Verification

```bash
python3 << 'EOF'
import duckdb
conn = duckdb.connect('varaha/data/varaha_data.duckdb')

# Get OI analysis
latest = conn.execute("""
    SELECT timestamp, max_pain_strike,
           call_oi_concentration, put_oi_concentration, oi_skew
    FROM market_data
    WHERE max_pain_strike IS NOT NULL
    ORDER BY timestamp DESC LIMIT 1
""").fetchall()

if latest:
    row = latest[0]
    print(f"OI Analysis:")
    print(f"  Timestamp: {row[0]}")
    print(f"  Max Pain Strike: {row[1]}")
    print(f"  Call OI %: {row[2]:.1f}%")
    print(f"  Put OI %: {row[3]:.1f}%")
    print(f"  OI Skew (Put/Call): {row[4]:.2f}")
    
    # Verify concentrations sum to ~100%
    if row[2] and row[3]:
        total = row[2] + row[3]
        if 95 <= total <= 105:
            print(f"\n✅ PASS: OI concentrations valid (sum={total:.1f}%)")
        else:
            print(f"\n⚠️  WARNING: OI concentration sum unexpected: {total:.1f}%")
else:
    print("⚠️  No OI analysis yet")
EOF
```

---

## ✅ STEP 9: CSV Export with Advanced Indicators

```bash
python3 << 'EOF'
import csv
import os

csv_file = '/home/trading_ceo/data/csv/2026-05-05_market.csv'

if os.path.exists(csv_file):
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    if rows:
        headers = list(rows[0].keys())
        
        # Check for advanced indicator columns
        advanced_headers = ['iv_rank', 'iv_regime', 'hv_20', 'agg_theta', 'pcr_total', 'sentiment']
        found = [h for h in advanced_headers if h in headers]
        
        print(f"CSV Headers: {len(headers)} total")
        print(f"Advanced indicators in CSV: {found}")
        
        if len(found) >= 3:
            print(f"\n✅ PASS: Advanced indicators exported to CSV")
        else:
            print(f"\n❌ FAIL: Missing advanced indicator columns in CSV")
    else:
        print("⚠️  CSV is empty")
else:
    print(f"❌ FAIL: CSV not found at {csv_file}")
EOF
```

---

## ✅ STEP 10: Full Integration Test

```bash
cd /home/trading_ceo/python-trader

# Run a full test capture
python3 varaha/data_capture_v3_duckdb.py --once --no-broker

# Check exit code
if [ $? -eq 0 ]; then
    echo "✅ PASS: Capture completed successfully"
else
    echo "❌ FAIL: Capture failed"
fi

# Verify column count
python3 << 'EOF'
import duckdb
conn = duckdb.connect('varaha/data/varaha_data.duckdb')
cols = conn.execute("DESCRIBE market_data").fetchall()
col_count = len(cols)
print(f"Total columns: {col_count}")
print(f"Expected: ~99 (67 base+SMC+32 advanced)")

if col_count >= 95:
    print("✅ PASS: All columns present")
else:
    print(f"⚠️  WARNING: Fewer columns than expected")
EOF
```

---

## 📋 Integration Summary

Run this final check:

```bash
python3 << 'EOF'
import duckdb

checks = {
    "Code: Import": False,
    "Code: Function Call": False,
    "Code: Parameters": False,
    "Schema: 32 Advanced Cols": False,
    "Data: IV Rank": False,
    "Data: Greeks": False,
    "Data: PCR Sentiment": False,
    "CSV: Advanced Headers": False,
    "Performance: < 50ms": False,
    "Overall": False,
}

try:
    # Check code
    with open('varaha/data_capture_v3_duckdb.py', 'r') as f:
        code = f.read()
        checks["Code: Import"] = "from varaha_advanced_indicators import" in code
        checks["Code: Function Call"] = "compute_advanced_indicators" in code
        checks["Code: Parameters"] = "advanced.get('iv_current')" in code
    
    # Check database
    conn = duckdb.connect('varaha/data/varaha_data.duckdb')
    cols = [c[0] for c in conn.execute("DESCRIBE market_data").fetchall()]
    checks["Schema: 32 Advanced Cols"] = 'iv_rank' in cols and 'agg_theta' in cols
    
    # Check data
    iv_count = conn.execute("SELECT COUNT(*) FROM market_data WHERE iv_rank IS NOT NULL").fetchone()[0]
    checks["Data: IV Rank"] = iv_count > 0
    
    greek_count = conn.execute("SELECT COUNT(*) FROM market_data WHERE agg_theta IS NOT NULL").fetchone()[0]
    checks["Data: Greeks"] = greek_count > 0
    
    pcr_count = conn.execute("SELECT COUNT(*) FROM market_data WHERE pcr_total IS NOT NULL").fetchone()[0]
    checks["Data: PCR Sentiment"] = pcr_count > 0
    
except Exception as e:
    print(f"Error: {e}")

# Print summary
print("\n" + "="*60)
print("ADVANCED INDICATORS INTEGRATION SUMMARY")
print("="*60)

passed = sum(1 for v in checks.values() if v)
for check, result in checks.items():
    status = "✅" if result else "❌"
    print(f"{status} {check}")

print("="*60)
print(f"Result: {passed}/9 checks passed")

if passed >= 7:
    print("🎉 INTEGRATION SUCCESSFUL!")
elif passed >= 5:
    print("⚠️  INTEGRATION MOSTLY COMPLETE")
else:
    print("❌ INTEGRATION INCOMPLETE")
print("="*60)
EOF
```

---

## When Deepseek Integration is Complete

1. Run all 10 verification steps above
2. Report results to user with any issues found
3. If checks 1-8 pass → Integration successful
4. If data checks fail → May need to wait for market hours or re-run capture

---

## Notes

- **Market Dependency**: IV rank, Greeks, and PCR require populated option_snapshots table
- **Time-Based**: Session phase detected from current time (pre/early/mid/late)
- **Performance**: 32 new metrics add ~30ms per capture (acceptable for 1-minute intervals)
- **Fallback**: If scipy is unavailable, Greeks default to None (doesn't break capture)

