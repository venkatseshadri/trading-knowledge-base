import sys
with open("/home/trading_ceo/python-trader/orbiter/core/engine/rule/rule_manager.py", "r") as f:
    c = f.read()

# Add debug after compiling rules
old = """            return sorted(compiled, key=lambda x: x[prio_key], reverse=True)"""
new = """            logger.info(f"COMPILED: key={rule_list_key}, compiled_count={len(compiled)}")
            return sorted(compiled, key=lambda x: x[prio_key], reverse=True)"""

c = c.replace(old, new)
with open("/home/trading_ceo/python-trader/orbiter/core/engine/rule/rule_manager.py", "w") as f:
    f.write(c)
print("Added compiled debug")

