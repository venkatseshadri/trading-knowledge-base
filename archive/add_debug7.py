with open('/home/trading_ceo/python-trader/orbiter/core/engine/runtime/core_engine.py', 'r') as f:
    content = f.read()

# Add debug for rules_path
old_init = '''        rules_path = session_manager.get_active_rules_file()
        logger.debug(f"[{self.__class__.__name__}.__init__] - Active rules file: {rules_path}")'''

new_init = '''        rules_path = session_manager.get_active_rules_file()
        logger.info(f"CORE_ENGINE: Active rules file: {rules_path}")
        logger.debug(f"[{self.__class__.__name__}.__init__] - Active rules file: {rules_path}")'''

content = content.replace(old_init, new_init)

with open('/home/trading_ceo/python-trader/orbiter/core/engine/runtime/core_engine.py', 'w') as f:
    f.write(content)

print('Added core_engine debug')
