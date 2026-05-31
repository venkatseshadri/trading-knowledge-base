import sys
with open("/home/trading_ceo/python-trader/orbiter/core/engine/rule/rule_manager.py", "r") as f:
    c = f.read()

# Add debug to see if scoring rules match
old = """        for score_rule in self.scoring_rules:
            try:
                if score_rule[engine].matches(facts):"""

new = """        logger.info(f"SCORING: rules_count={len(self.scoring_rules)}, facts_keys={list(facts.keys())[:10]}")
        for score_rule in self.scoring_rules:
            try:
                matched = score_rule[engine].matches(facts)
                logger.info(f"SCORING: rule={score_rule.get(\\"name\\",\\"?\\")} matched={matched}")
                if matched:"""

c = c.replace(old, new)
with open("/home/trading_ceo/python-trader/orbiter/core/engine/rule/rule_manager.py", "w") as f:
    f.write(c)
print("Added scoring debug")

