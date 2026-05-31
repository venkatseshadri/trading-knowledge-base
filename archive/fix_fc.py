import sys
with open("/home/trading_ceo/python-trader/orbiter/core/engine/rule/fact_calculator.py", "r") as f:
    c = f.read()

# Fix the double-prefix bug
old = """        # Add indicators as market.* facts (BOTH dot and underscore formats)
        for k, v in indicators.items():
            facts[f"market.{k}"] = v
            facts[f"market_{k}"] = v"""
            
new = """        # Add indicators as market.* facts (BOTH dot and underscore formats)
        for k, v in indicators.items():
            if k not in facts:
                facts[k] = v"""

c = c.replace(old, new)
with open("/home/trading_ceo/python-trader/orbiter/core/engine/rule/fact_calculator.py", "w") as f:
    f.write(c)
print("Fixed fact_calculator.py")
