import sys
with open("/home/trading_ceo/python-trader/orbiter/core/engine/rule/rule_manager.py", "r") as f:
    c = f.read()

# Add debug at start of _load_and_compile_scoring_rules
old = """def _load_and_compile_scoring_rules(self) -> List[Dict]:
        logger.info(f"LOAD_SCORING: scoring_rules_key={self.rule_schema.get(\"scoring_rules_key\", \"scoring_rules\")}, scoring_rules={len(self.scoring_rules)}")"""

new = """def _load_and_compile_scoring_rules(self) -> List[Dict]:
        logger.info(f"LOAD_SCORING: rules_file={self.rules_file_path}, key={self.rule_schema.get(\"scoring_rules_key\", \"scoring_rules\")}, existing={len(self.scoring_rules)}")"""

c = c.replace(old, new)
with open("/home/trading_ceo/python-trader/orbiter/core/engine/rule/rule_manager.py", "w") as f:
    f.write(c)
print("Added file path debug")

