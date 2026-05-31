import re

# 1. Add TRACE to core_engine.py for scoring
with open('/home/trading_ceo/python-trader/orbiter/core/engine/runtime/core_engine.py', 'r') as f:
    content = f.read()

# Add scoring trace
old_score = '''            # 🔥 Scoring for visibility
            score = 0.0
            if tech_facts:
                score = self.rule_manager.evaluate_score(source=self, context=self.constants.get('fact_contexts', 'instrument_context'), **{**extra_facts, 'raw_data_for_filter': raw_data_for_filter})'''

new_score = '''            # 🔥 Scoring for visibility
            score = 0.0
            logger.trace(f"SCORING: symbol={symbol_name}, tech_facts_keys={list(tech_facts.keys())[:10]}")
            if tech_facts:
                score = self.rule_manager.evaluate_score(source=self, context=self.constants.get('fact_contexts', 'instrument_context'), **{**extra_facts, 'raw_data_for_filter': raw_data_for_filter})
                logger.trace(f"SCORED: symbol={symbol_name}, score={score}")'''

content = content.replace(old_score, new_score)

with open('/home/trading_ceo/python-trader/orbiter/core/engine/runtime/core_engine.py', 'w') as f:
    f.write(content)

print('Added scoring TRACE to core_engine.py')
