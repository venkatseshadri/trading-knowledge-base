with open('/home/trading_ceo/python-trader/orbiter/core/engine/session/session_manager.py', 'r') as f:
    content = f.read()

old_func = '''    def get_active_rules_file(self) -> str:
        f_key = self.schema_manager.get_key('strategy_schema', 'files_key')
        r_key = self.schema_manager.get_key('strategy_schema', 'rules_file_key')
        return self.strategy_bundle.get(f_key, {}).get(r_key)'''

new_func = '''    def get_active_rules_file(self) -> str:
        f_key = self.schema_manager.get_key('strategy_schema', 'files_key')
        r_key = self.schema_manager.get_key('strategy_schema', 'rules_file_key')
        result = self.strategy_bundle.get(f_key, {}).get(r_key)
        import logging
        logger = logging.getLogger('ORBITER')
        logger.info("RULES_FILE: f_key=%s, r_key=%s, result=%s", f_key, r_key, result)
        return result'''

content = content.replace(old_func, new_func)

with open('/home/trading_ceo/python-trader/orbiter/core/engine/session/session_manager.py', 'w') as f:
    f.write(content)

print('Added rules_file debug')
