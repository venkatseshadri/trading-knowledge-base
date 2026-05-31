import sys
with open("/home/trading_ceo/python-trader/orbiter/core/engine/rule/rule_manager.py", "r") as f:
    c = f.read()

# Add scoring weights to defaults
old = """defaults = {\"market_adx\": 0.0, \"market_ema_fast\": 0.0, \"market_ema_slow\": 0.0, \"market_rsi\": 50.0, \"market_supertrend_dir\": 0}"""
new = """defaults = {"market_adx": 0.0, "market_ema_fast": 0.0, "market_ema_slow": 0.0, "market_rsi": 50.0, "market_supertrend_dir": 0, "filter_supertrend_direction_numeric": 0, "filters_scoring_combined_score_weight_adx": 0.4, "filters_scoring_combined_score_weight_ema_slope": 0.3, "filters_scoring_combined_score_weight_supertrend": 0.3}"""

c = c.replace(old, new)
with open("/home/trading_ceo/python-trader/orbiter/core/engine/rule/rule_manager.py", "w") as f:
    f.write(c)
print("Fixed rule_manager.py defaults")

