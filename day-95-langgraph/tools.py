import pandas as pd


def load_dataset(path="train.csv"):
    return pd.read_csv(path)


def summarize_dataset(df):
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns[:10]),
        "missing_values": int(df.isnull().sum().sum()),
    }


def calculate_mean(df, column):
    if column not in df.columns:
        return f"Column '{column}' was not found."

    return float(df[column].mean())


def analyze_mean(df, column, threshold=50):
    if column not in df.columns:
        return f"Column '{column}' was not found."

    mean_value = float(df[column].mean())
    comparison = (
        "greater than"
        if mean_value > threshold
        else "not greater than"
    )

    return {
        "column": column,
        "mean": mean_value,
        "threshold": threshold,
        "comparison": comparison,
    }