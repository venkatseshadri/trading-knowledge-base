with open('/home/trading_ceo/python-trader/orbiter/core/engine/rule/rule_manager.py', 'r') as f:
    content = f.read()

# Add debug after rule_schema is set
old_init = '''        self.rule_schema = self.schema_manager.get_key('rule_schema')'''
new_init = '''        self.rule_schema = self.schema_manager.get_key('rule_schema')
        logger.info(f"RULE_SCHEMA: {self.rule_schema}")'''

content = content.replace(old_init, new_init)

# Add debug before loading scoring rules
old_load = '''    def _load_and_compile_scoring_rules(self) -> List[Dict]:
        return self._compile_rules(self.rule_schema.get('scoring_rules_key', 'scoring_rules'), self.scoring_rules)'''

new_load = '''    def _load_and_compile_scoring_rules(self) -> List[Dict]:
        logger.info(f"LOAD_SCORING: scoring_rules_key={self.rule_schema.get('scoring_rules_key', 'scoring_rules')}, scoring_rules={len(self.scoring_rules)}")
        return self._compile_rules(self.rule_schema.get('scoring_rules_key', 'scoring_rules'), self.scoring_rules)'''

content = content.replace(old_load, new_load)

with open('/home/trading_ceo/python-trader/orbiter/core/engine/rule/rule_manager.py', 'w') as f:
    f.write(content)

print('Added schema debug')
