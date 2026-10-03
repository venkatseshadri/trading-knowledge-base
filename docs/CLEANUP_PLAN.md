# Full Disk Cleanup Plan

*Drive: 96G total, 61G used, 36G free — Run date: 2026-05-06*

---

## 1. /root (24G total)

### 🔴 /root/.cache — 12G

| Path | Size | Safe? | Note |
|---|---|---|---|
| `/root/.cache/pip` | **6.7G** | ✅ Delete | `pip cache purge` |
| `/root/.cache/go-build` | 1.6G | ✅ Delete | `go clean -cache` |
| `/root/.cache/kagglehub` | 1.2G | ✅ Delete | Downloaded datasets |
| `/root/.cache/puppeteer` | 630M | ⚠️ Keep? | Browser for auth scripts |
| `/root/.cache/ms-playwright` | 622M | ✅ Delete | Alternative to puppeteer |
| `/root/.cache/huggingface` | 605M | ✅ Delete | ML model cache |
| `/root/.cache/node-gyp` | 140M | ⚠️ Keep? | Node build cache |
| `/root/.cache/opencode` | 98M | ⚠️ Keep | Active tool cache |

### 🔴 /root/.ollama — 5.6G

| Path | Size | Note |
|---|---|---|
| `/root/.ollama/models` | 5.6G | LLM models — **delete if not using ollama** |

### 🟡 /root/.npm — 1.5G

Delete with `npm cache clean --force` (1.5G). Rebuilds on next install.

### 🟡 /root/.local — 2.0G

| Path | Size | Note |
|---|---|---|
| `/root/.local/share/opencode` | 1.2G | OpenCode session data |
| `/root/.local/share/claude` | 950M | Claude session data |

### 🟡 /root/.nvm — 1.2G

Node version manager. Multiple Node versions cached.

---

## 2. /tmp (6.2G) — ALL SAFE TO DELETE

| Path | Size | Note |
|---|---|---|
| `/tmp/pip-unpack-1x2l97h2` | **2.7G** | Stale pip temp |
| `nifty_combined_2024.csv` | 677M | Old NSE data |
| `NSE FUTURE AND OPTIONS DATASET 2024.zip` | 179M | Already extracted |
| `*.csv` (~15 files) | ~1.5G | Old NSE FNO datasets |
| `google-chrome-stable_current_amd64.deb` | 122M | Old installer |
| `org.chromium.*` | 160M | Chromium temp |
| `varaha_*_copy.duckdb` | 22M | Test DB copies |

---

## 3. /var (2.7G)

| Path | Size | Action |
|---|---|---|
| `/var/lib/snapd` | 2.0G | Snap packages — `snap list` to check |
| `/var/log/journal` | 128M | `journalctl --vacuum-size=50M` |

---

## 4. /home/trading_ceo (11G)

| Path | Size | Action |
|---|---|---|
| `orbiter_n2.log` | **275M** | Delete |
| `/tmp/varaha_data_capture.log` | 43M | Truncate (`> file`) |
| `/tmp/varaha_data_capture_sensex.log` | 46M | Truncate |
| Symbol file duplicates | 17M | Delete ShoonyaApi-py/ copies |
| Analysis docs (~17 files) | ~200K | Delete old May 5 reports |
| `nifty_data/` | 4.8G | **KEEP** (OHLCV data) |
| `data/csv/` | 1.5G | **KEEP** (CSV exports) |
| DuckDB files | 14M | **KEEP** (live DBs) |

---

## Summary

| Category | Reclaimable |
|---|---|
| /root/.cache (pip + go + kaggle + huggingface + playwright) | ~11G |
| /root/.ollama/models | 5.6G |
| /tmp (pip temp + old CSVs + test DBs) | ~5.5G |
| /root/.npm cache | 1.5G |
| /var snap packages (audit first) | ~1G |
| /home cleanup | ~350M |
| /var/log journals | ~80M |
| **Total reclaimable** | **~25G** |

**After cleanup: 61G → ~36G used, ~61G free (63% free)**

---

## Commands

```bash
# pip cache
pip cache purge

# go cache
go clean -cache -modcache

# npm cache
npm cache clean --force

# ollama models (if not needed)
rm -rf /root/.ollama/models

# /tmp cleanup
rm -rf /tmp/pip-unpack-*
rm -f /tmp/nifty_combined_2024.csv /tmp/NSE_*.csv /tmp/NSE_*.CSV /tmp/NSE_*.zip
rm -f /tmp/google-chrome-stable_current_amd64.deb
rm -rf /tmp/org.chromium.*
rm -f /tmp/varaha_*_copy.duckdb /tmp/varaha_test_v4*.duckdb

# journals
journalctl --vacuum-size=50M

# orbiter log
rm /home/trading_ceo/orbiter_n2.log

# truncate capture logs
> /tmp/varaha_data_capture.log
> /tmp/varaha_data_capture_sensex.log

# symbol file duplicates in ~/
rm /home/trading_ceo/BFO_symbols.txt /home/trading_ceo/MCX_symbols.txt

# ShoonyaApi-py duplicates
rm /home/trading_ceo/python-trader/ShoonyaApi-py/*_symbols.txt

# old analysis docs (May 5 debug reports)
rm /home/trading_ceo/VERIFICATION_CHECKLIST_SMC_LOGGER.md
rm /home/trading_ceo/VERIFICATION_CHECKLIST_ADVANCED_INDICATORS.md
rm /home/trading_ceo/INTEGRATION_GUIDE_ADVANCED_INDICATORS.md
rm /home/trading_ceo/INTEGRATION_GUIDE_SMC_LOGGER.md
rm /home/trading_ceo/INTEGRATION_COMPLETE.md
rm /home/trading_ceo/DEEPSEEK_REPORT_CRITICAL_ANALYSIS.md
rm /home/trading_ceo/CRITICAL_ISSUES_AND_SOLUTIONS.md
rm /home/trading_ceo/FINAL_STATUS_REPORT.md
rm /home/trading_ceo/RESEARCH_INDICATORS_SUMMARY.md
rm /home/trading_ceo/YDAY_ANALYSIS_REPORT_20260504_deepseek.md
rm /home/trading_ceo/latest_changes_deepseek.md
rm /home/trading_ceo/IV_IMPLEMENTATION_COMPLETE.md
rm /home/trading_ceo/IV_ISSUE_INVESTIGATION.md
rm /home/trading_ceo/SENSEX_CAPTURE_TROUBLESHOOTING.md
```

⚠️ **Verify before deleting ollama models** — only if you don't run local LLMs.
