with open('/home/trading_ceo/python-trader/orbiter/core/engine/rule/rule_manager.py', 'r') as f:
    content = f.read()

# Add debug inside the for loop
old_loop = '''            for s in data.get(rule_list_key, []):
                expr = s.get('expression') or self._convert_to_expression(s.get(signals_key, {}))
                rule_entry = {"name": s.get('name', 'Unnamed'), "engine": rule_engine.Rule(expr), prio_key: s.get(prio_key, 0)}'''

new_loop = '''            items = data.get(rule_list_key, [])
            logger.info(f"COMPILE_LOOP: rule_list_key={rule_list_key}, items_count={len(items)}")
            for s in items:
                logger.info(f"COMPILE_ITEM: {s.get('name', 'Unnamed')}, keys={list(s.keys())}")
                expr = s.get('expression') or self._convert_to_expression(s.get(signals_key, {}))
                rule_entry = {"name": s.get('name', 'Unnamed'), "engine": rule_engine.Rule(expr), prio_key: s.get(prio_key, 0)}'''

content = content.replace(old_loop, new_loop)

with open('/home/trading_ceo/python-trader/orbiter/core/engine/rule/rule_manager.py', 'w') as f:
    f.write(content)

print('Added loop debug')
