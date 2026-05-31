import re

with open('/home/trading_ceo/python-trader/orbiter/core/engine/rule/rule_manager.py', 'r') as f:
    content = f.read()

old_debug = '''                        # 🔥 DEBUG: Log facts if scoring is expected
                        if 'filter_supertrend_direction_numeric' not in facts:
                            logger.trace(f"Scoring Debug - Expression: {expr_str} | Keys: {list(facts.keys())}")'''

new_debug = '''                        # 🔥 DEBUG: Log facts if scoring is expected
                        logger.info(f"SCORE_DEBUG: facts_keys={list(facts.keys())[:20]}")
                        key_facts = {k: facts.get(k) for k in ['market_adx', 'market_ema_fast', 'market_ema_slow', 'market_supertrend_dir', 'filter_supertrend_direction_numeric', 'filter_adx_above_25'] if k in facts}
                        logger.info(f"SCORE_DEBUG_KEYS: {key_facts}")'''

content = content.replace(old_debug, new_debug)

with open('/home/trading_ceo/python-trader/orbiter/core/engine/rule/rule_manager.py', 'w') as f:
    f.write(content)

print('Added debug statements')
