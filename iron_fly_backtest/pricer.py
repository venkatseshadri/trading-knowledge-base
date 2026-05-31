"""Vectorized Black-Scholes pricer for NIFTY options.

NIFTY options are European-style. We have minute-level spot data but no
options chain. Use BS with realized-vol-as-IV-proxy.
"""
import numpy as np
from scipy.stats import norm

RISK_FREE = 0.07  # India 10y rough proxy
TRADING_MINUTES_PER_YEAR = 252 * 375  # 252 trading days × 375 min/day


def bs_price(spot, strike, t_years, vol, option_type='CE'):
    """Black-Scholes price. All inputs can be scalars or numpy arrays.

    Args:
        spot: underlying price (scalar or array)
        strike: option strike (scalar or array)
        t_years: time to expiry in years
        vol: annualized volatility (decimal, e.g. 0.15 for 15%)
        option_type: 'CE' or 'PE'

    Returns:
        Option premium per share (multiply by lot size for contract value)
    """
    spot = np.asarray(spot, dtype=float)
    strike = np.asarray(strike, dtype=float)
    t_years = np.asarray(t_years, dtype=float)
    vol = np.asarray(vol, dtype=float)

    # Avoid divide-by-zero at expiry
    t_years = np.maximum(t_years, 1e-6)
    vol = np.maximum(vol, 1e-4)

    sqrt_t = np.sqrt(t_years)
    d1 = (np.log(spot / strike) + (RISK_FREE + 0.5 * vol**2) * t_years) / (vol * sqrt_t)
    d2 = d1 - vol * sqrt_t

    if option_type == 'CE':
        price = spot * norm.cdf(d1) - strike * np.exp(-RISK_FREE * t_years) * norm.cdf(d2)
    elif option_type == 'PE':
        price = strike * np.exp(-RISK_FREE * t_years) * norm.cdf(-d2) - spot * norm.cdf(-d1)
    else:
        raise ValueError(f"option_type must be CE or PE, got {option_type}")

    return np.maximum(price, 0.0)


def realized_vol_annualized(close_prices, window=20):
    """Compute trailing N-day realized vol from daily closes, annualized.

    Returns decimal (e.g. 0.15 = 15%).
    """
    log_returns = np.log(close_prices / close_prices.shift(1))
    return log_returns.rolling(window).std() * np.sqrt(252)


def time_to_expiry_years(now_dt, expiry_dt):
    """Compute time to expiry in years using trading-minute convention.

    Indian options expire at 3:30 PM IST. We use minute-of-trading-day basis.
    """
    if now_dt >= expiry_dt:
        return 1e-6
    seconds = (expiry_dt - now_dt).total_seconds()
    minutes = seconds / 60.0
    return minutes / TRADING_MINUTES_PER_YEAR


# Quick self-test
if __name__ == '__main__':
    import pandas as pd

    # Sanity: ATM straddle on 25000 spot, 7 DTE, 15% vol
    spot = 25000
    strike = 25000
    t = 7 / 252
    vol = 0.15

    ce = bs_price(spot, strike, t, vol, 'CE')
    pe = bs_price(spot, strike, t, vol, 'PE')
    print(f"ATM 25000, 7 DTE, 15% vol:")
    print(f"  CE: ₹{ce:.2f}")
    print(f"  PE: ₹{pe:.2f}")
    print(f"  Straddle: ₹{ce+pe:.2f}")
    print(f"  Expected: ~ ₹150-180 each (typical NIFTY 7 DTE ATM)")
    print()

    # Vectorized test
    spots = np.array([24800, 24900, 25000, 25100, 25200])
    strikes = np.full_like(spots, 25000, dtype=float)
    ts = np.full_like(spots, 7/252, dtype=float)
    vols = np.full_like(spots, 0.15, dtype=float)
    ce_arr = bs_price(spots, strikes, ts, vols, 'CE')
    pe_arr = bs_price(spots, strikes, ts, vols, 'PE')
    print("Spot scan, 25000 strike, 7 DTE, 15% vol:")
    for s, c, p in zip(spots, ce_arr, pe_arr):
        print(f"  Spot {s}: CE={c:.2f}, PE={p:.2f}")
