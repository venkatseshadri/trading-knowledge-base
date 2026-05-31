# SMC + CSV Logger Integration Verification Checklist

## How to Use This Checklist

Once Deepseek completes the integration, run the verification steps below in order:

1. **Code Structure Checks** (Static analysis)
2. **Database Schema Verification** (Schema check)
3. **CSV Logger Initialization** (File system check)
4. **SMC Calculation Verification** (Logic check)
5. **Data Capture Verification** (Data quality check)
6. **Performance & Storage Check** (Operational check)

---

## ✅ VERIFICATION STEP 1: Code Structure

### Check 1.1: Imports Added
```bash
# In /home/trading_ceo/python-trader/varaha/data_capture_v3_duckdb.py, verify:
grep -n "from varaha_smc_and_logger import" data_capture_v3_duckdb.py
```
**Expected Output:**
```
Line N: from varaha_smc_and_logger import compute_smc_indicators, CSVLogger, export_to_csv
```
✅ PASS: Import found
❌ FAIL: Import not found or incorrect

### Check 1.2: CSV Logger Initialized
```bash
# Verify CSVLogger initialization in main()
grep -n "csv_logger = CSVLogger" data_capture_v3_duckdb.py
```
**Expected Output:**
```
Line N: csv_logger = CSVLogger(
```
✅ PASS: CSVLogger initialization found
❌ FAIL: CSVLogger initialization not found

### Check 1.3: SMC Calculation Called
```bash
# Verify SMC computation is called in capture_once()
grep -n "smc = compute_smc_indicators" data_capture_v3_duckdb.py
```
**Expected Output:**
```
Line N: smc = compute_smc_indicators(buf)
```
✅ PASS: SMC calculation called
❌ FAIL: SMC calculation not found

### Check 1.4: CSV Export Called
```bash
# Verify export_to_csv is called
grep -n "export_to_csv" data_capture_v3_duckdb.py
```
**Expected Output:**
```
Line N: export_to_csv(csv_logger, db, timestamp, date_str, ds.index)
```
✅ PASS: CSV export found
❌ FAIL: CSV export not found

---

## ✅ VERIFICATION STEP 2: Database Schema

### Check 2.1: SMC Columns Exist in Schema
```bash
# Connect to DuckDB and check schema
python3 << 'EOF'
import duckdb
conn = duckdb.connect('/home/trading_ceo/python-trader/varaha/data/varaha_data.duckdb')
cols = conn.execute("DESCRIBE market_data").fetchall()
col_names = [c[0] for c in cols]

# Check for all SMC columns
smc_cols = ['ob_zone_high', 'ob_zone_low', 'ob_strength',
            'fvg_high', 'fvg_low', 'fvg_mitigated',
            'swing_high', 'swing_low', 'liquidity_swept',
            'structure_type', 'structure_confirmed', 'next_target', 'smc_strength']

missing = [c for c in smc_cols if c not in col_names]

if missing:
    print("❌ FAIL: Missing columns:", missing)
else:
    print("✅ PASS: All SMC columns present")
    
# Also check Pivot/Fib columns still exist
pivot_cols = ['pivot_pp', 'pivot_r1', 'pivot_r2', 'pivot_r3', 'pivot_s1', 'pivot_s2', 'pivot_s3']
fib_cols = ['fib_0', 'fib_236', 'fib_382', 'fib_50', 'fib_618', 'fib_786', 'fib_100']
or_cols = ['open_range_high', 'open_range_low']

for col_list in [pivot_cols, fib_cols, or_cols]:
    missing = [c for c in col_list if c not in col_names]
    if missing:
        print(f"❌ FAIL: Missing {col_list[0].split('_')[0]} columns:", missing)
    else:
        print(f"✅ PASS: All {col_list[0].split('_')[0]} columns present")

print(f"\nTotal columns: {len(col_names)}")
print(f"Expected: 66 (43 base + 13 SMC + 16 Pivot/Fib/OR)")
EOF
```

**Expected Output:**
```
✅ PASS: All SMC columns present
✅ PASS: All pivot columns present
✅ PASS: All fib columns present
✅ PASS: All open_range columns present
Total columns: 66
Expected: 66
```

---

## ✅ VERIFICATION STEP 3: CSV Logger Initialization

### Check 3.1: CSV Directory Created
```bash
ls -la /home/trading_ceo/data/csv/
```
**Expected Output:**
```
total N
drwxr-xr-x  2 trading_ceo trading_ceo  4096 May  5 HH:MM .
drwxr-xr-x  5 trading_ceo trading_ceo  4096 May  5 HH:MM ..
```
✅ PASS: Directory exists
❌ FAIL: Directory doesn't exist

### Check 3.2: Today's CSV Files Created
```bash
# Run a test capture
python3 /home/trading_ceo/python-trader/varaha/data_capture_v3_duckdb.py --once --no-broker

# Check for CSV files
ls -lh /home/trading_ceo/data/csv/
```
**Expected Output:**
```
2026-05-05_market.csv    (544 KB)
2026-05-05_options.csv   (9.1 MB)
```
✅ PASS: Both market and options CSV files created
❌ FAIL: Files not created

---

## ✅ VERIFICATION STEP 4: SMC Calculation Verification

### Check 4.1: SMC Values in Database
```bash
python3 << 'EOF'
import duckdb
conn = duckdb.connect('/home/trading_ceo/python-trader/varaha/data/varaha_data.duckdb')

# Get latest market data with SMC columns
latest = conn.execute("""
    SELECT timestamp, index_name, spot,
           ob_zone_high, ob_zone_low, ob_strength,
           fvg_high, fvg_low, fvg_mitigated,
           swing_high, swing_low, liquidity_swept,
           structure_type, structure_confirmed, next_target,
           smc_strength
    FROM market_data
    ORDER BY timestamp DESC LIMIT 1
""").fetchall()

if latest:
    row = latest[0]
    print(f"Timestamp: {row[0]}")
    print(f"Index: {row[1]}")
    print(f"Spot: {row[2]}")
    print(f"\nSMC Indicators:")
    print(f"  OB Zone: {row[3]} - {row[4]} (strength: {row[5]})")
    print(f"  FVG: {row[6]} - {row[7]} (mitigated: {row[8]})")
    print(f"  Liquidity: H={row[9]}, L={row[10]} (swept: {row[11]})")
    print(f"  Structure: {row[12]} (confirmed: {row[13]}, target: {row[14]})")
    print(f"  SMC Strength: {row[15]}")
    
    # Check if any SMC values are being calculated
    smc_values = [row[3], row[4], row[5], row[6], row[7], row[9], row[10], row[12], row[15]]
    has_data = any(v is not None for v in smc_values)
    
    if has_data:
        print("\n✅ PASS: SMC values are being calculated")
    else:
        print("\n❌ FAIL: SMC values are all None")
else:
    print("❌ FAIL: No data in market_data table")
EOF
```

**Expected Output:**
```
Timestamp: 2026-05-05T...
Index: NIFTY
Spot: 24120.65

SMC Indicators:
  OB Zone: 24100 - 24150 (strength: 4)
  FVG: 24120 - 24000 (mitigated: False)
  Liquidity: H=24200, L=24000 (swept: False)
  Structure: HH (confirmed: True, target: 24250)
  SMC Strength: 75

✅ PASS: SMC values are being calculated
```

### Check 4.2: SMC Calculation Logic
```bash
python3 << 'EOF'
# Verify SMC calculation logic by checking row counts
import duckdb
conn = duckdb.connect('/home/trading_ceo/python-trader/varaha/data/varaha_data.duckdb')

# Check market_data has SMC data
market_count = conn.execute("SELECT COUNT(*) FROM market_data WHERE smc_strength IS NOT NULL").fetchone()[0]
total_count = conn.execute("SELECT COUNT(*) FROM market_data").fetchone()[0]

print(f"Market data rows with SMC: {market_count} / {total_count}")

if market_count > 0:
    print("✅ PASS: SMC values are being calculated")
    # Check distribution
    stats = conn.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE ob_zone_high IS NOT NULL) as with_ob,
            COUNT(*) FILTER (WHERE fvg_high IS NOT NULL) as with_fvg,
            COUNT(*) FILTER (WHERE liquidity_swept) as swept,
            COUNT(*) FILTER (WHERE structure_confirmed) as confirmed,
            AVG(smc_strength) as avg_strength
        FROM market_data
    """).fetchone()
    
    print(f"\nSMC Distribution:")
    print(f"  With Order Block: {stats[1]}/{stats[0]}")
    print(f"  With FVG: {stats[2]}/{stats[0]}")
    print(f"  Liquidity Swept: {stats[3]}/{stats[0]}")
    print(f"  Structure Confirmed: {stats[4]}/{stats[0]}")
    print(f"  Average SMC Strength: {stats[5]:.1f}")
else:
    print("❌ FAIL: No SMC values calculated")
EOF
```

**Expected Output:**
```
Market data rows with SMC: 364 / 364
✅ PASS: SMC values are being calculated

SMC Distribution:
  With Order Block: 45/364
  With FVG: 120/364
  Liquidity Swept: 89/364
  Structure Confirmed: 328/364
  Average SMC Strength: 52.3
```

---

## ✅ VERIFICATION STEP 5: CSV Data Verification

### Check 5.1: Market CSV Data
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
        print(f"✅ PASS: Market CSV created with {len(rows)} rows")
        
        # Check headers
        headers = rows[0].keys()
        smc_headers = ['ob_zone_high', 'ob_zone_low', 'ob_strength',
                       'fvg_high', 'fvg_low', 'fvg_mitigated',
                       'swing_high', 'swing_low', 'liquidity_swept',
                       'structure_type', 'structure_confirmed', 'next_target',
                       'smc_strength']
        
        missing_headers = [h for h in smc_headers if h not in headers]
        
        if missing_headers:
            print(f"❌ FAIL: Missing headers in CSV: {missing_headers}")
        else:
            print(f"✅ PASS: All SMC headers present in CSV")
        
        # Show sample row
        sample = rows[0]
        print(f"\nSample row:")
        print(f"  Timestamp: {sample.get('timestamp')}")
        print(f"  Spot: {sample.get('spot')}")
        print(f"  SMC Strength: {sample.get('smc_strength')}")
    else:
        print("❌ FAIL: Market CSV is empty")
else:
    print(f"❌ FAIL: Market CSV not found at {csv_file}")
EOF
```

**Expected Output:**
```
✅ PASS: Market CSV created with 360 rows
✅ PASS: All SMC headers present in CSV

Sample row:
  Timestamp: 2026-05-05T09:15:00...
  Spot: 24100.5
  SMC Strength: 50.0
```

### Check 5.2: Options CSV Data
```bash
python3 << 'EOF'
import csv
import os
import gzip

csv_file = '/home/trading_ceo/data/csv/2026-05-05_options.csv'
gz_file = csv_file + '.gz'

# Check for either uncompressed or compressed
if os.path.exists(csv_file):
    print(f"Options CSV (uncompressed): {os.path.getsize(csv_file) / (1024*1024):.1f} MB")
elif os.path.exists(gz_file):
    print(f"Options CSV (compressed): {os.path.getsize(gz_file) / (1024*1024):.1f} MB")
    print("✅ PASS: Options CSV was auto-compressed (expected at EOD)")
else:
    print("❌ FAIL: Options CSV not found")

# Check options data exists in database
import duckdb
conn = duckdb.connect('/home/trading_ceo/python-trader/varaha/data/varaha_data.duckdb')
opt_count = conn.execute("SELECT COUNT(*) FROM option_snapshots").fetchone()[0]

if opt_count > 0:
    print(f"✅ PASS: {opt_count} option records in database")
else:
    print("❌ FAIL: No option records in database")
EOF
```

**Expected Output:**
```
Options CSV (uncompressed): 9.1 MB
✅ PASS: 23760 option records in database
```

---

## ✅ VERIFICATION STEP 6: Performance & Storage Check

### Check 6.1: Storage Usage
```bash
python3 << 'EOF'
from pathlib import Path

csv_dir = Path('/home/trading_ceo/data/csv')

if csv_dir.exists():
    uncompressed = sum(f.stat().st_size for f in csv_dir.glob('*.csv')) / (1024**2)
    compressed = sum(f.stat().st_size for f in csv_dir.glob('*.csv.gz')) / (1024**2)
    total = uncompressed + compressed
    
    print(f"CSV Storage Usage:")
    print(f"  Uncompressed: {uncompressed:.1f} MB")
    print(f"  Compressed: {compressed:.1f} MB")
    print(f"  Total: {total:.1f} MB")
    
    if total < 200:  # Should be much less for 1 day
        print(f"\n✅ PASS: Storage within expected range")
    else:
        print(f"\n❌ FAIL: Storage unexpectedly high")
else:
    print("❌ FAIL: CSV directory not found")
EOF
```

**Expected Output:**
```
CSV Storage Usage:
  Uncompressed: 0.5 MB
  Compressed: 9.1 MB
  Total: 9.6 MB

✅ PASS: Storage within expected range
```

### Check 6.2: Data Consistency (DuckDB vs CSV)
```bash
python3 << 'EOF'
import csv
import duckdb

# Count rows in DuckDB
conn = duckdb.connect('/home/trading_ceo/python-trader/varaha/data/varaha_data.duckdb')
db_market_count = conn.execute("SELECT COUNT(*) FROM market_data WHERE DATE(timestamp) = '2026-05-05'").fetchone()[0]
db_option_count = conn.execute("SELECT COUNT(*) FROM option_snapshots WHERE date = '2026-05-05'").fetchone()[0]

# Count rows in CSV
csv_market = 0
csv_options = 0

try:
    with open('/home/trading_ceo/data/csv/2026-05-05_market.csv', 'r') as f:
        csv_market = sum(1 for _ in f) - 1  # Exclude header
except:
    pass

try:
    with open('/home/trading_ceo/data/csv/2026-05-05_options.csv', 'r') as f:
        csv_options = sum(1 for _ in f) - 1  # Exclude header
except:
    pass

print(f"Data Consistency Check:")
print(f"  Market data: DB={db_market_count}, CSV={csv_market}")
print(f"  Option data: DB={db_option_count}, CSV={csv_options}")

if db_market_count == csv_market and db_option_count == csv_options:
    print(f"\n✅ PASS: DuckDB and CSV data counts match")
else:
    print(f"\n⚠️  WARNING: Data counts don't match (may be normal if capture ongoing)")
EOF
```

**Expected Output:**
```
Data Consistency Check:
  Market data: DB=360, CSV=360
  Option data: DB=23760, CSV=23760

✅ PASS: DuckDB and CSV data counts match
```

---

## ✅ VERIFICATION STEP 7: Final Integration Test

### Check 7.1: Full Capture Test
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
```

**Expected Output:**
```
✅ PASS: Capture completed successfully
```

### Check 7.2: Log for Errors
```bash
# Check for any errors in output
tail -50 /tmp/varaha_data_capture.log | grep -i "error\|exception\|fail"
```

**Expected Output:**
```
(No errors should be found)
```

---

## 📋 Verification Summary

Run this final check to generate a summary:

```bash
python3 << 'EOF'
import duckdb
from pathlib import Path

checks = {
    "Code: Imports": False,
    "Code: CSV Logger Init": False,
    "Code: SMC Calculation": False,
    "Code: CSV Export": False,
    "Schema: SMC Columns": False,
    "Schema: Pivot/Fib Columns": False,
    "Files: CSV Directory": False,
    "Files: Market CSV": False,
    "Files: Options CSV": False,
    "Data: SMC Values": False,
    "Data: Consistency": False,
    "Storage: Under 200MB": False,
}

# Check code
import subprocess
result = subprocess.run(["grep", "-c", "compute_smc_indicators", 
                        "/home/trading_ceo/python-trader/varaha/data_capture_v3_duckdb.py"],
                       capture_output=True)
checks["Code: SMC Calculation"] = result.returncode == 0

# Check files
csv_dir = Path('/home/trading_ceo/data/csv')
checks["Files: CSV Directory"] = csv_dir.exists()

# Check database
try:
    conn = duckdb.connect('/home/trading_ceo/python-trader/varaha/data/varaha_data.duckdb')
    cols = [c[0] for c in conn.execute("DESCRIBE market_data").fetchall()]
    checks["Schema: SMC Columns"] = 'smc_strength' in cols
    checks["Schema: Pivot/Fib Columns"] = 'pivot_pp' in cols
    
    count = conn.execute("SELECT COUNT(*) FROM market_data WHERE smc_strength IS NOT NULL").fetchone()[0]
    checks["Data: SMC Values"] = count > 0
except:
    pass

# Print results
print("\n" + "="*60)
print("INTEGRATION VERIFICATION SUMMARY")
print("="*60)

passed = sum(1 for v in checks.values() if v)
total = len(checks)

for check, result in checks.items():
    status = "✅" if result else "❌"
    print(f"{status} {check}")

print("="*60)
print(f"Result: {passed}/{total} checks passed")

if passed == total:
    print("🎉 INTEGRATION SUCCESSFUL - Ready for production!")
elif passed >= total * 0.8:
    print("⚠️  INTEGRATION MOSTLY COMPLETE - Minor issues to fix")
else:
    print("❌ INTEGRATION INCOMPLETE - Major work needed")
print("="*60)
EOF
```

---

## Next Steps

After verification completes:

1. ✅ If all checks pass → **Integration is complete, ready for live trading**
2. ⚠️ If some checks fail → **Review failing checks and debug**
3. ❌ If major checks fail → **Ask Deepseek to review integration**

---

## Quick Command to Run All Checks

```bash
# Save this as verify_integration.sh
#!/bin/bash

echo "Running SMC + Logger Integration Verification..."
echo ""

# Run all checks
python3 << 'EOF'
# [Insert all checks from above]
EOF
```

