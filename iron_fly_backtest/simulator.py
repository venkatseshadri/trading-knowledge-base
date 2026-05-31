"""Iron Fly / Iron Condor day-by-day simulator.

For a given entry day, time, structure config and exit rules,
simulates intraday MTM minute-by-minute using BS-priced legs.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pricer import bs_price, time_to_expiry_years


# NIFTY conventions
STRIKE_GRID = 50  # NIFTY strikes are at 50-point intervals
LOT_SIZE = 75     # NIFTY lot size (post Nov 2024 reduction)
EXPIRY_HOUR = 15  # 3:30 PM IST
EXPIRY_MINUTE = 30
EOD_EXIT_HOUR = 15  # exit by 3:00 PM to avoid pin risk
EOD_EXIT_MINUTE = 0


def round_to_strike(price):
    """Round to nearest 50-pt strike."""
    return int(round(price / STRIKE_GRID) * STRIKE_GRID)


def build_iron_fly(spot_at_entry, body_offset_pts, hedge_distance_pts):
    """Build an Iron Fly or Iron Condor.

    Args:
        spot_at_entry: spot price at trade entry
        body_offset_pts: how far body strikes are from ATM (0 = Iron Fly,
                         50 = Iron Condor with 100pt body width, etc.)
        hedge_distance_pts: distance from body to wings

    Returns dict with:
        sell_ce_strike, sell_pe_strike (the body)
        buy_ce_strike, buy_pe_strike  (the wings)
    """
    atm = round_to_strike(spot_at_entry)

    if body_offset_pts == 0:
        # Iron Fly — body legs on same strike
        sell_ce_strike = atm
        sell_pe_strike = atm
    else:
        # Iron Condor — body legs offset
        sell_ce_strike = atm + body_offset_pts
        sell_pe_strike = atm - body_offset_pts

    buy_ce_strike = sell_ce_strike + hedge_distance_pts
    buy_pe_strike = sell_pe_strike - hedge_distance_pts

    return {
        'sell_ce_strike': sell_ce_strike,
        'sell_pe_strike': sell_pe_strike,
        'buy_ce_strike': buy_ce_strike,
        'buy_pe_strike': buy_pe_strike,
        'atm': atm,
    }


def get_expiry_datetime(entry_dt, weekly_expiry_dow=1):
    """Get the next NIFTY weekly expiry datetime.

    NIFTY weekly expiry was Thursday until Sep 2024, then Tuesday.
    For simplicity here, use Tuesday (dow=1) since covers most of test period.

    Returns datetime of expiry at 3:30 PM IST.
    """
    days_ahead = (weekly_expiry_dow - entry_dt.weekday()) % 7
    if days_ahead == 0 and entry_dt.hour >= EXPIRY_HOUR:
        days_ahead = 7  # already expired today
    expiry_date = entry_dt.date() + timedelta(days=days_ahead)
    return datetime.combine(expiry_date, datetime.min.time()).replace(
        hour=EXPIRY_HOUR, minute=EXPIRY_MINUTE
    )


def price_position(spot, position, current_dt, expiry_dt, vol):
    """Price all 4 legs of an Iron Fly/Condor.

    Returns: dict with leg prices and net position value.
    Position value = entry_credit - current_value (positive = profit).
    """
    t = time_to_expiry_years(current_dt, expiry_dt)

    sell_ce = bs_price(spot, position['sell_ce_strike'], t, vol, 'CE')
    sell_pe = bs_price(spot, position['sell_pe_strike'], t, vol, 'PE')
    buy_ce = bs_price(spot, position['buy_ce_strike'], t, vol, 'CE')
    buy_pe = bs_price(spot, position['buy_pe_strike'], t, vol, 'PE')

    # Net cost to close right now (we'd buy back shorts, sell longs)
    net_cost_to_close = sell_ce + sell_pe - buy_ce - buy_pe

    return {
        'sell_ce': float(sell_ce),
        'sell_pe': float(sell_pe),
        'buy_ce': float(buy_ce),
        'buy_pe': float(buy_pe),
        'net_close_cost': float(net_cost_to_close),
    }


def simulate_day(day_minute_data, entry_time_str, structure_config,
                 sl_pct_of_credit, tp_rule, expiry_dt, vol):
    """Simulate one Iron Fly/Condor trade on one day.

    Args:
        day_minute_data: DataFrame with minute bars for entry_dt's day onward
                         (index=datetime, cols=open/high/low/close)
        entry_time_str: e.g. '09:30' — when to enter on entry day
        structure_config: {'body_offset_pts': 0|50|100, 'hedge_distance_pts': 100|150|...}
        sl_pct_of_credit: e.g. 1.0 for 100%, 1.5 for 150%
        tp_rule: dict like {'type': 'fixed', 'value': 250} or {'type': 'pct_credit', 'value': 0.5}
        expiry_dt: datetime of expiry
        vol: annualized vol estimate (decimal)

    Returns dict with trade outcome.
    """
    # Find entry minute
    entry_date = day_minute_data.index[0].date()
    entry_dt = pd.Timestamp(entry_date) + pd.Timedelta(hours=int(entry_time_str.split(':')[0]),
                                                        minutes=int(entry_time_str.split(':')[1]))

    # Filter to entry minute onward
    trade_data = day_minute_data[day_minute_data.index >= entry_dt].copy()
    if len(trade_data) == 0:
        return None

    spot_at_entry = float(trade_data.iloc[0]['open'])

    # Build position
    position = build_iron_fly(
        spot_at_entry,
        structure_config['body_offset_pts'],
        structure_config['hedge_distance_pts']
    )

    # Compute entry credit
    entry_prices = price_position(spot_at_entry, position, entry_dt, expiry_dt, vol)
    entry_credit = entry_prices['net_close_cost']  # what we received

    # Compute SL and TP thresholds (in P&L per share)
    sl_loss = sl_pct_of_credit * entry_credit  # max loss = X% of credit
    if tp_rule['type'] == 'fixed':
        # tp_rule['value'] is in rupees per share
        tp_profit = tp_rule['value']
    elif tp_rule['type'] == 'pct_credit':
        tp_profit = tp_rule['value'] * entry_credit
    else:
        tp_profit = entry_credit  # default: 100% of credit (max profit)

    # EOD exit time (3:00 PM on expiry day, or expiry time if same day)
    eod_exit_dt = pd.Timestamp(expiry_dt.date()) + pd.Timedelta(
        hours=EOD_EXIT_HOUR, minutes=EOD_EXIT_MINUTE
    )

    # Walk through minute by minute
    mae = 0  # max adverse excursion (worst loss seen)
    mfe = 0  # max favorable excursion (best profit seen)
    exit_reason = None
    exit_dt = None
    exit_pnl = None

    # Vectorize: price all legs across all minutes at once
    spots = trade_data['close'].values
    minutes = trade_data.index
    ts = np.array([time_to_expiry_years(m, expiry_dt) for m in minutes])

    sell_ce_prices = bs_price(spots, position['sell_ce_strike'], ts, vol, 'CE')
    sell_pe_prices = bs_price(spots, position['sell_pe_strike'], ts, vol, 'PE')
    buy_ce_prices = bs_price(spots, position['buy_ce_strike'], ts, vol, 'CE')
    buy_pe_prices = bs_price(spots, position['buy_pe_strike'], ts, vol, 'PE')

    # P&L per share at each minute = entry_credit - current_close_cost
    current_close_costs = sell_ce_prices + sell_pe_prices - buy_ce_prices - buy_pe_prices
    pnl_per_share = entry_credit - current_close_costs

    # Find first exit trigger
    for i in range(len(minutes)):
        m = minutes[i]
        pnl = pnl_per_share[i]

        if pnl > mfe:
            mfe = pnl
        if pnl < mae:
            mae = pnl

        # SL check (loss exceeds threshold)
        if pnl <= -sl_loss:
            exit_reason = 'SL'
            exit_dt = m
            exit_pnl = pnl
            break

        # TP check
        if pnl >= tp_profit:
            exit_reason = 'TP'
            exit_dt = m
            exit_pnl = pnl
            break

        # EOD check
        if m >= eod_exit_dt:
            exit_reason = 'EOD'
            exit_dt = m
            exit_pnl = pnl
            break
    else:
        # Loop finished without exit — use last bar
        exit_reason = 'EOD_DATA_END'
        exit_dt = minutes[-1]
        exit_pnl = pnl_per_share[-1]

    # Net P&L per lot
    pnl_per_lot = exit_pnl * LOT_SIZE
    credit_per_lot = entry_credit * LOT_SIZE

    return {
        'entry_dt': entry_dt,
        'exit_dt': exit_dt,
        'duration_min': (exit_dt - entry_dt).total_seconds() / 60,
        'spot_entry': spot_at_entry,
        'spot_exit': float(trade_data.loc[exit_dt, 'close']) if exit_dt in trade_data.index else float(trade_data['close'].iloc[-1]),
        'sell_ce_strike': position['sell_ce_strike'],
        'sell_pe_strike': position['sell_pe_strike'],
        'buy_ce_strike': position['buy_ce_strike'],
        'buy_pe_strike': position['buy_pe_strike'],
        'credit_per_share': float(entry_credit),
        'credit_per_lot': float(credit_per_lot),
        'pnl_per_share': float(exit_pnl),
        'pnl_per_lot': float(pnl_per_lot),
        'exit_reason': exit_reason,
        'mae_per_share': float(mae),
        'mfe_per_share': float(mfe),
        'vol_used': float(vol),
        'sl_pct': sl_pct_of_credit,
        'tp_type': tp_rule['type'],
        'tp_value': tp_rule['value'],
    }


# Self-test
if __name__ == '__main__':
    print("Loading minute data (sample only)...")
    df = pd.read_csv('/home/trading_ceo/nifty_minute_2015_2026.csv')
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date').sort_index()

    # Take a recent Monday
    recent_data = df['2024-10-21':'2024-10-22']
    print(f"Sample data: {len(recent_data)} minutes")
    print(f"First: {recent_data.index[0]}, Last: {recent_data.index[-1]}")

    expiry = get_expiry_datetime(recent_data.index[0])
    print(f"Expiry: {expiry}")

    structure = {'body_offset_pts': 0, 'hedge_distance_pts': 200}
    tp_rule = {'type': 'pct_credit', 'value': 0.5}

    result = simulate_day(
        day_minute_data=recent_data,
        entry_time_str='09:30',
        structure_config=structure,
        sl_pct_of_credit=1.5,
        tp_rule=tp_rule,
        expiry_dt=expiry,
        vol=0.13,
    )
    print()
    print("Trade result:")
    for k, v in result.items():
        print(f"  {k}: {v}")
