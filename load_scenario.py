import json
from pathlib import Path

def get_portfolio_config(config, name):
    if name not in config:
        raise ValueError(f"Portfolio '{name}' not found in config")
    return config[name]

def get_portfolio_model_configuration(portfolio):
    return portfolio["simulation_model_configuration"]

def get_portfolio_asset_allocation(portfolio):
    return portfolio["asset_allocation"]

def validate_baseline_allocation(assets):
    total = sum(assets.values())
    if total != 100:
        raise ValueError(f"Asset allocation must sum to 100 (got {total})")
    if len(assets) > 50:
        raise ValueError("Too many assets in config")

def validate_sampling_ranges(assets):
    sum_min_val = 0
    sum_max_val = 0
    for name, bounds in assets.items():
        if not isinstance(bounds, list) or len(bounds) != 2:
            raise ValueError(f"{name} must be a list [min, max]")
        min_val, max_val = bounds
        if not isinstance(min_val, (int, float)) or not isinstance(max_val, (int, float)):
            raise ValueError(f"{name}: bounds must be numeric")
        if not (0 <= min_val <= 100 and 0 <= max_val <= 100):
            raise ValueError(f"{name}: bounds must be between 0 and 100")
        if min_val > max_val:
            raise ValueError(f"{name}: invalid bounds [{min_val}, {max_val}]")
        sum_min_val += min_val
        sum_max_val += max_val
    if sum_max_val < 100 or sum_min_val > 100:
        raise ValueError(f"No valid allocation possible: sum(min)={sum_min_val}, sum(max)={sum_max_val}")
    
def load_config(path):
    with open(path) as f:
        return json.load(f)