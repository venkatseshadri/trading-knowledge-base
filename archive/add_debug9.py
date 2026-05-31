# Fix the path in strategy.json
import json

with open('/home/trading_ceo/python-trader/orbiter/strategies/mcx_trend_follower/strategy.json') as f:
    data = json.load(f)

# Fix the paths - remove 'orbiter/' prefix
if 'orbiter/' in data['files']['rules_file']:
    data['files']['rules_file'] = data['files']['rules_file'].replace('orbiter/', '')
if 'orbiter/' in data['files']['instruments_file']:
    data['files']['instruments_file'] = data['files']['instruments_file'].replace('orbiter/', '')
if 'orbiter/' in data['files']['filters_file']:
    data['files']['filters_file'] = data['files']['filters_file'].replace('orbiter/', '')

with open('/home/trading_ceo/python-trader/orbiter/strategies/mcx_trend_follower/strategy.json', 'w') as f:
    json.dump(data, f, indent=2)

print('Fixed paths in strategy.json')
print('rules_file:', data['files']['rules_file'])
