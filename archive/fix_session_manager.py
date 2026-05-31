with open('/home/trading_ceo/python-trader/orbiter/core/engine/session/session_manager.py', 'r') as f:
    content = f.read()

# Fix the path joining to avoid double orbiter/
old_code = '''        strat_base = self.schema_manager.get_key('project_manifest_schema', 'structure_key') or 'structure'
        strat_path_val = self.schema_manager.get_key(strat_base, 'strategies') or structure.get('strategies')
        if strat_path_val is None:
            strat_path_val = 'orbiter/strategies'

        full_strategy_path = os.path.join(self.project_root, strat_path_val, rel_path)'''

new_code = '''        strat_base = self.schema_manager.get_key('project_manifest_schema', 'structure_key') or 'structure'
        strat_path_val = self.schema_manager.get_key(strat_base, 'strategies') or structure.get('strategies')
        if strat_path_val is None:
            strat_path_val = 'orbiter/strategies'

        # Avoid double path prefix: if rel_path already starts with orbiter/, don't prepend strat_path_val
        if rel_path and rel_path.startswith('orbiter/'):
            full_strategy_path = os.path.join(self.project_root, rel_path)
        else:
            full_strategy_path = os.path.join(self.project_root, strat_path_val, rel_path)'''

content = content.replace(old_code, new_code)

with open('/home/trading_ceo/python-trader/orbiter/core/engine/session/session_manager.py', 'w') as f:
    f.write(content)

print('Fixed session_manager path joining')
