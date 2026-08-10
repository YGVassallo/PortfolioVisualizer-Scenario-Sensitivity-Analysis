import random
from load_scenario import load_config



def sample_simulation_config(config):
    sim_config = config["scenario"]["simulation_model_configuration"]
    sampled_config = {}
    for key, value in sim_config.items():
        if isinstance(value, list):
            if len(value) == 2 and all(isinstance(v, (int, float)) for v in value):
                min_val, max_val = value
                if isinstance(min_val, int) and isinstance(max_val, int):
                    sampled_value = random.randint(min_val, max_val)
                else:
                    sampled_value = random.uniform(min_val, max_val)
            else:
                sampled_value = random.choice(value)
        else:
            sampled_value = value
        sampled_config[key] = sampled_value
    return sampled_config

def sample_allocation_config(config):
    sim_allocation = config["scenario"]["asset_allocation"]
    max_attempts = config["sampling_config"]["max_attempts"]

    assets = list(sim_allocation.items())

    for _ in range(max_attempts):
        random.shuffle(assets)
        sampled_allocation = {}
        remaining = 100

        for i in range(len(assets) - 1):
            name, bounds = assets[i]
            min_val, max_val = bounds

            max_possible = min(max_val, remaining)

            if min_val > max_possible:
                break 

            value = random.randint(min_val, max_possible)

            sampled_allocation[name] = value
            remaining -= value

        else:
            last_name, last_bounds = assets[-1]
            min_val, max_val = last_bounds

            if min_val <= remaining <= max_val:
                sampled_allocation[last_name] = remaining
                return sampled_allocation

    raise ValueError("Could not generate valid allocation")

def create_sample(config):
    sim_config=sample_simulation_config(config)
    allocation=sample_allocation_config(config)

    sample={
        "simulation_model_configuration": sim_config,
        "asset_allocation": allocation
    }
    return sample