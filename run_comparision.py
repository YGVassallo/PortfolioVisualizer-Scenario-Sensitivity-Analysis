from pathlib import Path 
from selenium import webdriver

import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from load_scenario import*
from generate_samples import*
from run_portfolio_visualizer import *
from analyse_portfolio import *


def flatten_portfolio_config(portfolio, columns):
    config={}
    for option, value in portfolio["simulation_model_configuration"].items():
        key=f"Simulation Model Configuration | {option.strip()}"
        config[key]=value
        columns[key]=option.strip()
    return config

def clean_value(val):
    if isinstance(val, str):
        val = val.strip()

        if val == "":
            return None

        if "%" in val:
            val = val.replace("%", "")
  
        if "$" in val:
            val = val.replace("$", "").replace(",", "")

        try:
            return float(val)
        except:
            return val

    return val


def flatten_metrics(results, columns):
    metrics = {}

    for table, table_data in results.items():

        if table == "Portfolio Model":
            for name, values in table_data.items():
                if "Allocation" in values:
                    value = values["Allocation"]
                    val = clean_value(value)

                    name = str(name).strip()
                    key = f"{table} | Allocation | {name}"

                    metrics[key] = val
                    columns[key] = f"Allocation | {name}"

        elif table == "Performance Summary":
            for name, values in table_data.items():
                for percentile, value in values.items():
                    val = clean_value(value)

                    key = f"{table} | {name} | {percentile}"

                    metrics[key] = val
                    columns[key] = f"{name} | {percentile}"

        elif table == "Simulated Assets - Correlations and Returns":
            for name, values in table_data.items():
                for asset, value in values.items():
                    val = clean_value(value)

                    key = f"{table} | {name} | {asset}"

                    metrics[key] = val
                    columns[key] = f"{name} | {asset}"

        elif table == "Expected Annual Return":
            for percentile, values in table_data.items():
                for year, value in values.items():
                    val = clean_value(value)

                    key = f"{table} | {percentile} | {year}"

                    metrics[key] = val
                    columns[key] = f"{percentile} | {year}"

        elif table == "Annual Return Probabilities":
            for percentage, values in table_data.items():
                for year, value in values.items():
                    val = clean_value(value)

                    key = f"{table} | {percentage} | {year}"

                    metrics[key] = val
                    columns[key] = f"{percentage} | {year}"

        elif table == "Loss Probabilities":
            for percentage, values in table_data.items():
                for column in values.keys():
                    value = values[column]

                    if value == "" or str(value).strip() == "":
                        value = None

                    val = clean_value(value)

                    key = f"{table} | {percentage} | {column}"

                    metrics[key] = val
                    columns[key] = f"{percentage} | {column}"

    return metrics

base_path=(Path(__file__).resolve().parent)
output_folder = base_path / "Outputs"
output_folder.mkdir(parents=True, exist_ok=True)

config_path=base_path/"config.json"

config=load_config(config_path)
config_baseline=get_portfolio_config(config, "baseline")
validate_baseline_allocation(get_portfolio_asset_allocation(config_baseline))




config_scenario=get_portfolio_config(config, "scenario")
validate_sampling_ranges(get_portfolio_asset_allocation(config_scenario))

sampling_config=config["sampling_config"]
num_samples=sampling_config["num_samples"]
max_attempts=sampling_config["max_attempts"]


driver=webdriver.Chrome()

driver.get("https://www.portfoliovisualizer.com/monte-carlo-simulation")

run_portfolio_visualizer(driver, config, "Baseline", config_baseline)
baseline_df, names=scrape_portfolio_tables(driver)

baseline_resulst=extract_metrics(baseline_df,names)

baseline_flat={}
baseline_flat["Scenario"]="baseline"
columns={}
baseline_config_flat=flatten_portfolio_config(config_baseline,columns)
baseline_flat.update(baseline_config_flat)
baseline_output_flat=flatten_metrics(baseline_resulst, columns)
baseline_flat.update(baseline_output_flat)


all_rows=[]
all_rows.append(baseline_flat)


for i in range(num_samples):
    sample=create_sample(config)
    dfs, names=run_portfolio_visualizer(driver, sample=sample)
    results=extract_metrics(dfs, names)
    flat_result={}
    flat_result["Scenario"]=f"Sample {i}"
    flat_result.update(flatten_portfolio_config(sample, columns))
    flat_result.update(flatten_metrics(results,columns))
    all_rows.append(flat_result)
    


df = pd.DataFrame(all_rows)

df.rename(columns=columns, inplace=True)

cols = df.columns.tolist()
cols.insert(0, cols.pop(cols.index("Scenario")))
df = df[cols]

df.to_excel(output_folder / "results.xlsx", index=False)
analyse_scenarios(df)

analyse_output(df, output_folder)
