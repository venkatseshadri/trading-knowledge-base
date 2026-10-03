# SENSEX Option Symbol Format — deepseek

## Finding

SENSEX option symbols in Shoonya BFO exchange use a **fundamentally different format** from NIFTY.

### NIFTY format (current code, works)
```
NIFTY05MAY26C24050
```
Pattern: `{prefix}{DD}{MMM}{YY}{C/P}{strike}`
- 2-digit day, 3-char month, 2-digit year, type letter, strike

### SENSEX format (actual Shoonya requirement)
```
SENSEX2650777100CE
```
Pattern: `SENSEX26{M}{DD}{strike5digits}{CE/PE}`
- `SENSEX26` = prefix + year (26=2026)
- `5` = single-digit month (5=May, NOT 05)
- `07` = 2-digit day
- `77100` = 5-digit strike (zero-padded to 5 digits)
- `CE` or `PE` = full 2-char option type

### Code location
`data_capture_v3_duckdb.py:280`:
```python
tsym = f"{prefix}{expiry[:2]}{expiry[3:6].upper()}{expiry[-2:]}{opt_type[0]}{strike}"
```

This single formula generates wrong symbols for SENSEX.

### Verified working
Tested 6 SENSEX ATM/OTM option quotes — all return valid LTP and OI:
```
SENSEX2650777100CE → ltp=373.30, oi=365,700
SENSEX2650777100PE → ltp=599.55, oi=254,860
SENSEX2650777000CE → ltp=417.85, oi=933,620
```

### Fix needed
`get_option_quote()` must branch on index name to use different format strings:

```python
if self.index == 'SENSEX':
    # SENSEX format: SENSEX26{M}{DD}{STRIKE5DIGITS}{CE/PE}
    m = str(int(expiry[3:5]))  # month without leading zero
    d = expiry[:2]             # day
    y = expiry[-2:]            # year
    tsym = f"{prefix}{y}{m}{d}{strike:05d}{opt_type}"
else:
    # NIFTY format: NIFTY{DD}{MMM}{YY}{C/P}{STRIKE}
    tsym = f"{prefix}{expiry[:2]}{expiry[3:6].upper()}{expiry[-2:]}{opt_type[0]}{strike}"
```

### Additional note
BFO SENSEX search returns 0 weekly contracts (`weekly='W1'`). Only monthly expiries found (26-MAY-2026, not 07-MAY-2026). The expiry handling logic may also need adjustment for SENSEX weekly vs monthly.
