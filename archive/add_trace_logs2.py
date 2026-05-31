# Add TRACE to rule_manager.py evaluate_score to see facts
with open('/home/trading_ceo/python-trader/orbiter/core/engine/rule/rule_manager.py', 'r') as f:
    content = f.read()

# Add facts tracing at start of evaluate_score
old_eval = '''    def evaluate_score(self, source: Any, context: str = "global", **extra_facts) -> float:
        logger.info(f"SCORE_EVAL: evaluate_score called with context={context}, extra_facts_keys={list(extra_facts.keys())[:10]}")
        facts = self._get_common_facts(source)'''

new_eval = '''    def evaluate_score(self, source: Any, context: str = "global", **extra_facts) -> float:
        logger.info(f"SCORE_EVAL: context={context}, extra_facts_keys={list(extra_facts.keys())[:10]}, scoring_rules_len={len(self.scoring_rules)}")
        logger.trace(f"FACTS_IN: extra_facts={ {k: str(v)[:50] for k,v in extra_facts.items()} }")
        facts = self._get_common_facts(source)
        logger.trace(f"FACTS_COMMON: common_facts_keys={list(facts.keys())[:10]}")'''

content = content.replace(old_eval, new_eval)

# Add more trace after facts are merged
old_merge = '''                defaults = {'market_adx': 0.0, 'market_ema_fast': 0.0, 'market_ema_slow': 0.0, 'market_rsi': 50.0, 'market_supertrend_dir': 0}
                facts.update(defaults)'''

new_merge = '''                defaults = {'market_adx': 0.0, 'market_ema_fast': 0.0, 'market_ema_slow': 0.0, 'market_rsi': 50.0, 'market_supertrend_dir': 0}
                facts.update(defaults)
                logger.trace(f"FACTS_AFTER_MERGE: facts_keys={list(facts.keys())}")'''

content = content.replace(old_merge, new_merge)

with open('/home/trading_ceo/python-trader/orbiter/core/engine/rule/rule_manager.py', 'w') as f:
    f.write(content)

print('Added FACTS TRACE to rule_manager.py')
