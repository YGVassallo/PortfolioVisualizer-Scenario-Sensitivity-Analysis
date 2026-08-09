import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def analyse_scenarios(df):
    columns = [
        col for col in df.columns
        if col.startswith("Simulation Model Configuration")
        or col.startswith("Allocation |")
    ]
    return df[columns]

def perfSummary(df, percentiles, column:str):
    keys=["Scenario"]
    for percentile in percentiles:
        key = f"{column} | {percentile}"
        if key in df.columns:
            keys.append(key)
    perf_summary_df=df[keys]
    return perf_summary_df

def make_safe_filename(title):
    return (
        title.replace("(", "")
             .replace(")", "")
             .replace(" ", "_")
             .replace("/", "")
             .replace("%", "")
             .replace("|", "")
             .replace(",", "")
    )

def plotPerfSummary(perf_summary_df, percentiles, title:str, folder):
    plt.figure(figsize=(14,8))
    for i in range(len(perf_summary_df)):
        scenario = perf_summary_df.iloc[i, 0]
        values = perf_summary_df.iloc[i, 1:].values
        if scenario.lower() == "baseline":
            plt.plot(percentiles, values, linewidth=3, label="Baseline")
        else:
            plt.plot(percentiles, values, alpha=0.3, label=scenario)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=10)
    safe_title=make_safe_filename(title)
    plt.title(safe_title)
    plt.tight_layout()
    plt.savefig(folder / f"{safe_title}.png")
    plt.show()

def expectedAnnualReturn(df, years, percentile):
    keys = ["Scenario"]
    for year in years:
        key = f"{percentile} | {year}"
        if key in df.columns:
            keys.append(key)
    expected_annual_return=df[keys]
    return expected_annual_return

def plotExpectedAnnualReturn(expected_annual_return, years, title: str, folder):
    plt.figure(figsize=(14,8))
    values_len = expected_annual_return.shape[1] - 1  # ohne "Scenario"
    x = years[:values_len]
    for i in range(len(expected_annual_return)):
        scenario = expected_annual_return.iloc[i, 0]
        values = expected_annual_return.iloc[i, 1:].values
        if scenario.lower() == "baseline":
            plt.plot(x, values, linewidth=3, label="Baseline")
        else:
            plt.plot(x, values, alpha=0.3, label=scenario)
    plt.xlabel("Time Horizon (Years)")
    plt.ylabel("Expected Annual Return (%)")
    plt.xticks(fontsize=10, rotation=30)
    plt.yticks(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=10)
    safe_title=make_safe_filename(title)
    plt.title(safe_title)
    plt.tight_layout()
    plt.savefig(folder / f"{safe_title}.png")
    plt.show()

def annualReturnProbabilities(df, probabilities, year):
    keys = ["Scenario"]
    for probability in probabilities:
        key = f"{probability} | {year}"
        if key in df.columns:
            keys.append(key)
    annual_return_probabilities=df[keys]
    return annual_return_probabilities    

def plotAnnualReturnProbabilities(annual_return_probabilities, probabilities, title: str, folder):
    plt.figure(figsize=(14,8))
    for i in range(len(annual_return_probabilities)):
        scenario = annual_return_probabilities.iloc[i, 0]
        values = annual_return_probabilities.iloc[i, 1:].values
        if scenario == "baseline":
            plt.plot(probabilities, values, linewidth=3, label="Baseline")
        else:
            plt.plot(probabilities, values, alpha=0.3, label=scenario)
    plt.xlabel("Return Threshold (%)")
    plt.ylabel("Probability")
    plt.xticks(fontsize=10, rotation=30)
    plt.yticks(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=10)
    safe_title=make_safe_filename(title)
    plt.title(safe_title)
    plt.tight_layout()
    plt.savefig(folder / f"{safe_title}.png")
    plt.show()

def lossProb(df, percentages, cashflows:bool, timePeriod:bool):
    key=" | Loss Probability "
    if cashflows:
        key=key+"Including Cashflows | "
    else:
        key=key+"Excluding Cashflows | "
    if timePeriod:
        key=key+"Within Time Period"
    else:
        key=key+"End of Time Period"
    keys=["Scenario"]
    for percentage in percentages:
        temp=percentage+key
        #print(df[temp])
        if temp in df.columns:
            keys.append(temp)
    loss_prob_df=df[keys]
    #print(len(loss_prob_df))
    return loss_prob_df

def plotLossProb(loss_prob, percentages, title:str, folder):
    plt.figure(figsize=(14,8))
    for i in range(len(loss_prob)):
        scenario = loss_prob.iloc[i, 0]
        values = loss_prob.iloc[i, 1:].values
        if scenario == "baseline":
            plt.plot(percentages, values, linewidth=3,label="Baseline")
        else:
            plt.plot(percentages, values, alpha=0.3, label=scenario)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=10)
    plt.xlabel("Loss Threshold (%)")
    plt.ylabel("Probability")
    plt.xticks(fontsize=10, rotation=30)
    plt.yticks(fontsize=10)
    safe_title=make_safe_filename(title)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(folder / f"{safe_title}.png")
    plt.show()

def plot_sensitivity(df, output_col, folder):
    df_inputs = analyse_scenarios(df)
    input_cols = df_inputs.columns
    input_cols = [col for col in input_cols if col != "Scenario"]
    n = len(input_cols)
    cols = 4
    rows = math.ceil(n / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 4 * rows))
    axes = np.array(axes).reshape(-1)
    for i, input_col in enumerate(input_cols):
        ax = axes[i]
        x = df[input_col]
        y = df[output_col]
        ax.scatter(x, y)
        ax.set_title(input_col.replace("Allocation | ", ""), fontsize=10)
        ax.set_xlabel("Input", fontsize=8)
        ax.set_ylabel("Output", fontsize=8)
        ax.tick_params(axis='both', labelsize=8)
        ax.grid(True, alpha=0.3)
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j]) 
    title="Sensitivity"
    safe_title=make_safe_filename(title)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(folder / f"{safe_title}.png")
    plt.show()

def plot_local_sensitivity(df, output_col, folder):
    df_inputs = analyse_scenarios(df)
    input_cols = df_inputs.columns
    input_cols = [col for col in input_cols if col != "Scenario"]
    n = len(input_cols)
    cols = 4
    rows = math.ceil(n / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 4 * rows))
    axes = np.array(axes).reshape(-1)
    for i, input_col in enumerate(input_cols):
        ax = axes[i]
        x = df[input_col]
        y = df[output_col]
        sorted_idx = np.argsort(x)
        x_sorted = x.iloc[sorted_idx].to_numpy()
        y_sorted = y.iloc[sorted_idx].to_numpy()
        dx = np.diff(x_sorted).astype(float)
        dy = np.diff(y_sorted).astype(float)
        dx[dx == 0] = np.nan
        sensitivity = dy / dx
        ax.plot(x_sorted[1:], sensitivity)
        ax.set_title(input_col.replace("Allocation | ", ""), fontsize=10)
        ax.set_xlabel("Input", fontsize=8)
        ax.set_ylabel("Sensitivity", fontsize=8)
        ax.tick_params(axis='both', labelsize=8)
        ax.grid(True, alpha=0.3)
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])
    title="Local Sensitivity"
    safe_title=make_safe_filename(title)
    plt.title(safe_title)
    plt.tight_layout()
    plt.savefig(folder / f"{safe_title}.png")
    plt.show()

def compute_sensitivity_scores(df, output_col):
    df_inputs = analyse_scenarios(df)
    input_cols = df_inputs.columns
    input_cols = [col for col in input_cols if col != "Scenario"]
    scores = {}
    for input_col in input_cols:
        x = df[input_col].astype(str).str.replace("%", "")
        x = pd.to_numeric(x, errors="coerce")
        y = df[output_col].astype(str).str.replace("%", "")
        y = pd.to_numeric(y, errors="coerce")
        mask = (~x.isna()) & (~y.isna())
        x = x[mask]
        y = y[mask]
        if len(x) < 2:
            continue
        if x.nunique() < 2:
            score = 0
            clean_name = input_col.replace("Allocation | ", "")
            scores[clean_name] = score
            continue
        sorted_idx = np.argsort(x)
        x_sorted = x.iloc[sorted_idx]
        y_sorted = y.iloc[sorted_idx]
        dx = np.diff(x_sorted).astype(float)
        dy = np.diff(y_sorted).astype(float)
        dx[dx == 0] = np.nan
        sensitivity = dy / dx
        if len(sensitivity) == 0 or np.all(np.isnan(sensitivity)):
            score = 0
        else:
            score = np.nanmean(np.abs(sensitivity))
        if np.isnan(score):
            score = 0
        clean_name = input_col.replace("Allocation | ", "")
        scores[clean_name] = score
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_scores

def plot_sensitivity_ranking(scores, folder, title):
    names = [x[0] for x in scores]
    values = [x[1] for x in scores]

    names = [n.replace("Simulation Model Configuration | ", "") for n in names]
    names = [n.replace("Allocation | ", "") for n in names]

    plt.figure(figsize=(10, 6))
    plt.barh(names, values)
    plt.gca().invert_yaxis()

    plt.yticks(fontsize=8)
    plt.xticks(fontsize=8)

    safe_title=make_safe_filename(title)
    safe_title="Sensitivity Ranking"+safe_title
    plt.title(safe_title)
    plt.tight_layout()
    plt.savefig(folder / f"{safe_title}.png")
    plt.show()
    
def find_interesting(scores):
    values = [s[1] for s in scores]

    if len(values) == 0:
        return []

    mean = np.mean(values)
    std = np.std(values)

    threshold = mean + 0.5 * std

    interesting = [s for s in scores if s[1] >= threshold]

    if len(interesting) == 0:
        interesting = scores[:3]

    return interesting

def plot_interesting_sensitivity(df, output_col, interesting, folder, title):
    interesting_names = [x[0] for x in interesting]

    input_cols = []
    for name in interesting_names:
        col_name = f"Allocation | {name}"
        if col_name in df.columns:
            input_cols.append(col_name)

    input_cols = list(set(input_cols))
    n = len(input_cols)

    if n == 0:
        return

    cols = 2
    rows = math.ceil(n / cols)

    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 4 * rows))

    axes = np.array(axes).reshape(-1)

    for i, input_col in enumerate(input_cols):
        ax = axes[i]

        x = df[input_col].astype(str).str.replace("%", "")
        x = pd.to_numeric(x, errors="coerce")

        y = df[output_col].astype(str).str.replace("%", "")
        y = pd.to_numeric(y, errors="coerce")

        mask = (~x.isna()) & (~y.isna())
        x = x[mask]
        y = y[mask]

        if len(x) < 2 or x.nunique() < 2:
            continue

        df_temp = pd.DataFrame({"x": x, "y": y})
        df_grouped = df_temp.groupby("x").mean().reset_index()

        x = df_grouped["x"]
        y = df_grouped["y"]

        ax.plot(x, y, marker="o")

        if len(x) >= 2:
            try:
                z = np.polyfit(x, y, 1)
                p = np.poly1d(z)
                ax.plot(x, p(x), color="red")
            except:
                pass

        ax.set_title(input_col.replace("Allocation | ", ""), fontsize=10)
        ax.set_xlabel("Input", fontsize=8)
        ax.set_ylabel("Output", fontsize=8)
        ax.tick_params(axis='both', labelsize=8)
        ax.grid(True, alpha=0.3)

    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    safe_title = make_safe_filename(title)

    plt.suptitle(title, fontsize=14)
    plt.tight_layout()

    plt.savefig(folder / f"{safe_title}.png")
    plt.show()

def analyse_output(df, folder):

    percentiles = ["10th Percentile", "25th Percentile", "50th Percentile", "75th Percentile", "90th Percentile"]

    # --- 1. Portfolio End Balance (wichtigster Output) ---
    end_balance_nominal = perfSummary(df, percentiles, "Portfolio End Balance (nominal)")
    plotPerfSummary(end_balance_nominal, percentiles, "Portfolio End Balance (nominal)", folder)

    output_col = "Portfolio End Balance (nominal) | 50th Percentile"

    scores = compute_sensitivity_scores(df, output_col)
    plot_sensitivity_ranking(scores, folder, output_col)

    interesting = find_interesting(scores)
    plot_interesting_sensitivity(df, output_col, interesting, folder, output_col)

    # --- 2. Expected Annual Return ---
    years = ["1 Year", "3 Years", "5 Years", "10 Years", "15 Years", "20 Years", "25 Years", "30 Years", "40 Years", "50 Years"]
    expected_annual_return_50 = expectedAnnualReturn(df, years, "50th Percentile")
    plotExpectedAnnualReturn(expected_annual_return_50, years, "Expected Annual Return 50th Percentile", folder)

    output_col = "50th Percentile | 10 Years"

    scores = compute_sensitivity_scores(df, output_col)
    plot_sensitivity_ranking(scores, folder, output_col)

    interesting = find_interesting(scores)
    plot_interesting_sensitivity(df, output_col, interesting, folder, output_col)

    # --- 3. Loss Probability (Risiko) ---
    percentages = [
        "2.50%", "5.00%", "7.50%", "10.00%", "12.50%",
        "15.00%", "17.50%", "20.00%", "22.50%", "25.00%",
        "27.50%", "30.00%", "32.50%", "35.00%", "37.50%", "40.00%"
    ]

    loss_prob = lossProb(df, percentages, False, True)
    plotLossProb(loss_prob, percentages, "Loss Probability (Excluding Cashflows, Within Period)", folder)

    output_col = "10.00% | Loss Probability Excluding Cashflows | Within Time Period"

    if output_col in df.columns:
        scores = compute_sensitivity_scores(df, output_col)
        plot_sensitivity_ranking(scores, folder, output_col)

        interesting = find_interesting(scores)
        plot_interesting_sensitivity(df, output_col, interesting, folder, output_col)

'''
def analyse_portfolio(df):
    print(df.head())
    print(df.columns)
'''