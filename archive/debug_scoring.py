import sys
with open("/home/trading_ceo/python-trader/orbiter/core/engine/rule/rule_manager.py", "r") as f:
    c = f.read()

# Add debug logging before scoring evaluation
old = """                        try:
                            result = self._score_evaluators[expr_str].evaluate(facts)"""

new = """                        # DEBUG: log facts being used for scoring
                        logger.info(f"SCORE_DEBUG: facts_adx={facts.get(\\"market_adx\\",\\"MISSING\\")} ema_f={facts.get(\\"market_ema_fast\\",\\"MISSING\\")} ema_s={facts.get(\\"market_ema_slow\\",\\"MISSING\\")} st={facts.get(\\"market_supertrend_dir\\",\\"MISSING\\")}")
                        try:
                            result = self._score_evaluators[expr_str].evaluate(facts)"""

c = c.replace(old, new)
with open("/home/trading_ceo/python-trader/orbiter/core/engine/rule/rule_manager.py", "w") as f:
    f.write(c)
print("Added debug logging")

