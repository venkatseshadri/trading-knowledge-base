import sys
with open("/home/trading_ceo/python-trader/orbiter/core/engine/rule/rule_manager.py", "r") as f:
    c = f.read()

# Add debug logging
old = """logger.info(f"COMPILE_RULES: rule_list_key={rule_list_key}, data_keys={list(data.keys())}, target_list_len={len(target_list)}")"""
new = """logger.info(f"COMPILE_RULES: rule_list_key={rule_list_key}, data_keys={list(data.keys())}, target_list_len={len(target_list)}, has_key={rule_list_key in data}")"""

c = c.replace(old, new)
with open("/home/trading_ceo/python-trader/orbiter/core/engine/rule/rule_manager.py", "w") as f:
    f.write(c)
print("Added compile rules debug")

