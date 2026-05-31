with open('/home/trading_ceo/python-trader/orbiter/core/engine/rule/rule_manager.py', 'r') as f:
    content = f.read()

# Add debug to see full path
old_compile = '''    def _compile_rules(self, rule_list_key: str, target_list: List[Dict]) -> List[Dict]:
        try:
            data = DataManager.load_json(self.rules_file_path)
            logger.info(f"COMPILE_RULES: file={self.rules_file_path}, key={rule_list_key}, data_keys={list(data.keys())}, target_len={len(target_list)}")'''

new_compile = '''    def _compile_rules(self, rule_list_key: str, target_list: List[Dict]) -> List[Dict]:
        try:
            import os
            full_path = os.path.abspath(self.rules_file_path) if not os.path.isabs(self.rules_file_path) else self.rules_file_path
            data = DataManager.load_json(self.rules_file_path)
            logger.info(f"COMPILE_RULES: file={full_path}, key={rule_list_key}, data_keys={list(data.keys())}, target_len={len(target_list)}")'''

content = content.replace(old_compile, new_compile)

with open('/home/trading_ceo/python-trader/orbiter/core/engine/rule/rule_manager.py', 'w') as f:
    f.write(content)

print('Added absolute path debug')
