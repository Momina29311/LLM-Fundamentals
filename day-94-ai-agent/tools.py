import pandas as pd
from pathlib import Path

def _load_df(path: str) -> pd.DataFrame:
    return pd.read_csv(path)

def summarize_dataset(path: str) -> dict:
    df = _load_df(path)
    missing_per_col = df.isna().sum().to_dict()
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "dtypes": {str(k): str(v) for k, v in df.dtypes.items()},
        "missing_per_column": missing_per_col,
        "head": df.head(3).to_dict(orient="list"),
    }

def get_column_info(path: str, column: str) -> dict:
    df = _load_df(path)
    if column not in df.columns:
        return {"error": f"Column '{column}' not found."}
    col = df[column]
    info = {
        "column": column,
        "dtype": str(col.dtype),
        "count": int(col.count()),
        "missing": int(col.isna().sum()),
    }
    if pd.api.types.is_numeric_dtype(col):
        info["min"] = float(col.min())
        info["max"] = float(col.max())
        info["unique_count"] = int(col.nunique())
    else:
        info["unique_count"] = int(col.nunique())
        info["sample_values"] = list(col.dropna().unique()[:10])
    return info

def calculate_statistics(path: str, column: str) -> dict:
    df = _load_df(path)
    if column not in df.columns:
        return {"error": f"Column '{column}' not found."}
    col = df[column]
    if not pd.api.types.is_numeric_dtype(col):
        return {"error": f"Column '{column}' is not numeric."}
    desc = col.describe()
    return {
        "column": column,
        "count": int(desc.get("count", 0)),
        "mean": float(desc.get("mean", 0)),
        "std": float(desc.get("std", 0)),
        "min": float(desc.get("min", 0)),
        "25%": float(desc.get("25%", 0)),
        "50%": float(desc.get("50%", 0)),
        "75%": float(desc.get("75%", 0)),
        "max": float(desc.get("max", 0)),
    }

def calculate(expression: str, context: dict) -> dict:
    """
    Safe tiny calculator.
    expression: e.g. "mean > 50", "mean - 50", "mean + std"
    context: e.g. {"mean": 62.3, "std": 5.1}
    """
    allowed_names = set(context.keys())
    # simple safety: only allow names from context + basic ops
    code = expression.strip()
    # quick guard: reject dangerous keywords
    dangerous = ["__", "import", "eval", "exec", "open", "os", "sys"]
    if any(k in code for k in dangerous):
        return {"error": "Invalid expression."}
    try:
        result = eval(code, {"__builtins__": {}}, context)
        return {"expression": expression, "result": result}
    except Exception as e:
        return {"error": str(e)}