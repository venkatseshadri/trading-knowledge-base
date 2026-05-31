with open('/home/trading_ceo/python-trader/orbiter/core/engine/rule/rule_manager.py', 'r') as f:
    content = f.read()

# Add debug inside _compile_rules to see what's in data
old_compile = '''    def _compile_rules(self, rule_list_key: str, target_list: List[Dict]) -> List[Dict]:
        try:
            data = DataManager.load_json(self.rules_file_path)
            if not data: return []'''

new_compile = '''    def _compile_rules(self, rule_list_key: str, target_list: List[Dict]) -> List[Dict]:
        try:
            data = DataManager.load_json(self.rules_file_path)
            logger.info(f"COMPILE_RULES: rule_list_key={rule_list_key}, data_keys={list(data.keys())}, target_list_len={len(target_list)}")
            if not data: return []'''

content = content.replace(old_compile, new_compile)

with open('/home/trading_ceo/python-trader/orbiter/core/engine/rule/rule_manager.py', 'w') as f:
    f.write(content)

print('Added compile debug')
