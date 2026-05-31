# Revert the session_manager fix since we fixed the root cause
with open('/home/trading_ceo/python-trader/orbiter/core/engine/session/session_manager.py', 'r') as f:
    content = f.read()

old_code = '''        # Avoid double path prefix: if rel_path already starts with orbiter/, don't prepend strat_path_val
        if rel_path and rel_path.startswith('orbiter/'):
            full_strategy_path = os.path.join(self.project_root, rel_path)
        else:
            full_strategy_path = os.path.join(self.project_root, strat_path_val, rel_path)'''

new_code = '''        full_strategy_path = os.path.join(self.project_root, strat_path_val, rel_path)'''

content = content.replace(old_code, new_code)

with open('/home/trading_ceo/python-trader/orbiter/core/engine/session/session_manager.py', 'w') as f:
    f.write(content)

print('Reverted session_manager fix')
