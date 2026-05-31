with open('/home/trading_ceo/python-trader/orbiter/core/engine/rule/rule_manager.py', 'r') as f:
    content = f.read()

# Add debugging at the start of evaluate_score
old_start = '''    def evaluate_score(self, source: Any, context: str = "global", **extra_facts) -> float:
        facts = self._get_common_facts(source)'''

new_start = '''    def evaluate_score(self, source: Any, context: str = "global", **extra_facts) -> float:
        logger.info(f"SCORE_EVAL: evaluate_score called with context={context}, extra_facts_keys={list(extra_facts.keys())[:10]}")
        facts = self._get_common_facts(source)'''

content = content.replace(old_start, new_start)

# Add debugging at the end before return
old_return = '''        return max_score'''

new_return = '''        logger.info(f"SCORE_RESULT: max_score={max_score}, scoring_rules_count={len(self.scoring_rules)}")
        return max_score'''

content = content.replace(old_return, new_return)

with open('/home/trading_ceo/python-trader/orbiter/core/engine/rule/rule_manager.py', 'w') as f:
    f.write(content)

print('Added more debug')
