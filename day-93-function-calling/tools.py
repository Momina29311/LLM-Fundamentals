# tools.py

import ast
import operator
from pathlib import Path

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype


# Keep train.csv in the same folder as this file
DF_PATH = Path(__file__).parent / "train.csv"


def _load_df() -> pd.DataFrame:
    """Load the dataset from the project folder."""
    if not DF_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DF_PATH}\n"
            "Place train.csv in the same folder as tools.py."
        )

    return pd.read_csv(DF_PATH)


def summarize_dataset() -> dict:
    """Return a basic summary of the dataset."""
    df = _load_df()

    return {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names": df.columns.tolist(),
        "numeric_columns": df.select_dtypes(
            include=np.number
        ).columns.tolist(),
        "categorical_columns": df.select_dtypes(
            exclude=np.number
        ).columns.tolist(),
        "missing_values": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
    }


def get_column_info(column: str) -> dict:
    """Return detailed information about one dataset column."""
    df = _load_df()

    if column not in df.columns:
        return {
            "error": f"Column '{column}' not found.",
            "available_columns": df.columns.tolist()[:20],
        }

    col = df[column]

    info = {
        "column": column,
        "dtype": str(col.dtype),
        "non_null_count": int(col.count()),
        "null_count": int(col.isna().sum()),
        "unique_values": int(col.nunique()),
    }

    if is_numeric_dtype(col):
        info.update(
            {
                "min": float(col.min()),
                "max": float(col.max()),
                "mean": float(col.mean()),
                "std": float(col.std()),
            }
        )
    else:
        info["top_5_values"] = col.value_counts().head(5).to_dict()

    return info


def calculate_statistics(
    column: str,
    stats: list[str] | None = None,
) -> dict:
    """
    Calculate statistics for a numeric column.

    Supported statistics:
    mean, median, std, min, max, count
    """
    df = _load_df()

    if column not in df.columns:
        return {"error": f"Column '{column}' not found."}

    col = df[column]

    if not is_numeric_dtype(col):
        return {"error": f"Column '{column}' is not numeric."}

    if stats is None:
        stats = ["mean", "median", "std", "min", "max", "count"]

    supported_stats = {
        "mean": lambda: float(col.mean()),
        "median": lambda: float(col.median()),
        "std": lambda: float(col.std()),
        "min": lambda: float(col.min()),
        "max": lambda: float(col.max()),
        "count": lambda: int(col.count()),
    }

    result = {"column": column}

    for stat in stats:
        if stat not in supported_stats:
            result["warning"] = (
                f"Unsupported statistic '{stat}'. "
                f"Supported values: {list(supported_stats)}"
            )
            continue

        result[stat] = supported_stats[stat]()

    return result


def calculate(expression: str) -> dict:
    """
    Safely evaluate a basic mathematical expression.

    Examples:
        calculate("25 * 48")
        calculate("100 / 4 + 7")
        calculate("(10 + 5) ** 2")
    """

    allowed_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    def evaluate_node(node):
        # Python 3.8+ represents numbers as ast.Constant
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool):
                raise ValueError("Boolean values are not allowed.")

            if isinstance(node.value, (int, float)):
                return node.value

            raise ValueError("Only numeric values are allowed.")

        # Binary operations such as 25 * 48
        if isinstance(node, ast.BinOp):
            left_value = evaluate_node(node.left)
            right_value = evaluate_node(node.right)
            operator_type = type(node.op)

            if operator_type not in allowed_operators:
                raise ValueError("This operator is not allowed.")

            return allowed_operators[operator_type](
                left_value,
                right_value,
            )

        # Unary operations such as -10 or +5
        if isinstance(node, ast.UnaryOp):
            operand_value = evaluate_node(node.operand)
            operator_type = type(node.op)

            if operator_type not in allowed_operators:
                raise ValueError("This operator is not allowed.")

            return allowed_operators[operator_type](operand_value)

        raise ValueError(
            "Invalid expression. Use numbers and basic operators only."
        )

    try:
        expression = expression.strip()

        if not expression:
            return {"error": "Expression cannot be empty."}

        tree = ast.parse(expression, mode="eval")
        result = evaluate_node(tree.body)

        return {
            "expression": expression,
            "result": float(result),
        }

    except ZeroDivisionError:
        return {"error": "Division by zero is not allowed."}

    except SyntaxError:
        return {"error": "Invalid mathematical expression."}

    except OverflowError:
        return {"error": "The result is too large."}

    except Exception as error:
        return {"error": str(error)}