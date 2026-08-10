import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from load_scenario import *

from analyse_portfolio import*

def scrape_portfolio_tables(driver):
    tables = driver.find_elements(By.TAG_NAME, "table")
    table_names=[]
    dataframes = []
    for table in tables:
        title="Unknown"
        try:
            title_element = table.find_element(By.XPATH, "preceding::h4[1]")
            title = title_element.text.strip()
        except:
            pass
        rows = table.find_elements(By.TAG_NAME, "tr")
        data = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "th") + row.find_elements(By.TAG_NAME, "td")
            data.append([cell.text for cell in cells])
        data = [row for row in data if any(cell.strip() for cell in row)]
        if not data:
            continue
        max_cols = max(len(row) for row in data)
        header = [f"col_{i}" for i in range(max_cols)]
        normalized_rows = []
        for row in data:
            row = row + [""] * (max_cols - len(row))
            normalized_rows.append(row)
        df = pd.DataFrame(normalized_rows, columns=header)
        table_names.append(title)
        dataframes.append(df)
    return dataframes, table_names

def clean_value(val):
    if isinstance(val, str):
        val = val.replace("%", "").replace(",", "")
        try:
            return float(val)
        except ValueError:
            return val
    return val


def extract_metrics(dfs, names):
    results = {}

    for df, name in zip(dfs, names):
        results[name] = {}

        tables_with_extra_row = {
            "Portfolio Model",
            "Performance Summary",
            "Simulated Assets - Correlations and Returns",
            "Loss Probabilities"
        }

        if name in tables_with_extra_row:
            df = df.iloc[:-1]


        if name == "Loss Probabilities":
            for i in range(2,df.shape[0]):
                row_key = str(df.iloc[i,0]).strip()
                row_key = row_key.replace(">=", "").strip()
                results[name][row_key]={}
                results[name][row_key]["Loss Probability Excluding Cashflows | Within Time Period"] = clean_value(df.iloc[i,1])
                results[name][row_key]["Loss Probability Excluding Cashflows | End of Time Period"] = clean_value(df.iloc[i,2])
                results[name][row_key]["Loss Probability Including Cashflows | Within Time Period"] = clean_value(df.iloc[i,3])
                results[name][row_key]["Loss Probability Including Cashflows | End of Time Period"] = clean_value(df.iloc[i,4])

                


        else:
            for i in range(1, df.shape[0]):
                row_key = df.iloc[i, 0]

                if pd.isna(row_key) or str(row_key).strip() == "":
                    continue

                row_key = str(row_key).strip().replace("\n", " ")

                results[name][row_key] = {}

                for j in range(1, df.shape[1]):
                    col_key = df.iloc[0, j]

                    if pd.isna(col_key) or str(col_key).strip() == "":
                        col_key = f"col_{j}"
                    else:
                        col_key = str(col_key).strip()

                    value = clean_value(df.iloc[i, j])

                    if value == "" or str(value).strip() == "":
                        continue

                    results[name][row_key][col_key] = value

    return results



def run_portfolio_visualizer(driver, config=None, portfolio_name=None, sample=None):

    if sample is not None:
        portfolio_model_config = sample["simulation_model_configuration"]
        portfolio_asset_allocation = sample["asset_allocation"]

    else:
        if config is None or portfolio_name not in config:
            raise ValueError(f"Scenario '{portfolio_name}' not found in config")

        portfolio = get_portfolio_config(config, portfolio_name)

        portfolio_model_config = get_portfolio_model_configuration(portfolio)
        portfolio_asset_allocation = get_portfolio_asset_allocation(portfolio)

    if isinstance(portfolio_asset_allocation, list):
        portfolio_asset_allocation = dict(portfolio_asset_allocation)

    driver.get("https://www.portfoliovisualizer.com/monte-carlo-simulation")

    WebDriverWait(driver,10).until(
        EC.presence_of_element_located((By.NAME,"initialAmount"))
    )

    for key, value in portfolio_model_config.items():

        element = WebDriverWait(driver,10).until(
            EC.presence_of_element_located((By.NAME, key))
        )

        tag = element.tag_name

        if tag == "select":
            dropdown = Select(element)

            value = str(value).strip()
            options = [o.text.strip() for o in dropdown.options]

            if value not in options:
                raise ValueError(f"Invalid value '{value}' for dropdown '{key}'")

            dropdown.select_by_visible_text(value)

        else:
            element.clear()
            element.send_keys(str(value))

    for i, (asset_name, allocation) in enumerate(sorted(portfolio_asset_allocation.items()), start=1):

        if i > 50:
            raise ValueError("Portfolio Visualizer supports max 50 assets")

        if i in [11,21,31,41]:
            WebDriverWait(driver,10).until(
                EC.element_to_be_clickable((By.LINK_TEXT,"More"))
            ).click()

        name = "asset" + str(i)
        element = driver.find_element(By.NAME, name)
        dropdown = Select(element)

        asset_name = str(asset_name).strip()
        options = [o.text.strip() for o in dropdown.options]

        if asset_name not in options:
            raise ValueError(f"Invalid asset '{asset_name}'")

        dropdown.select_by_visible_text(asset_name)

        name = "allocation" + str(i) + "_1"
        element = driver.find_element(By.NAME, name)
        element.clear()
        element.send_keys(str(allocation))

    run_button = WebDriverWait(driver,10).until(
        EC.presence_of_element_located((By.ID,"submitButton"))
    )

    driver.execute_script("arguments[0].click();", run_button)

    WebDriverWait(driver,10).until(
        EC.presence_of_element_located(
            (By.XPATH, "//*[contains(text(),'Monte Carlo Simulation Results')]")
        )
    )

    dfs, names = scrape_portfolio_tables(driver)

    return dfs, names
