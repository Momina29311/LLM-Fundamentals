from tools import summarize_dataset, get_column_info, calculate_statistics, calculate

# Reuse FUNCTION_MAP and run_tool_call
FUNCTION_MAP = {
    "summarize_dataset": summarize_dataset,
    "get_column_info": get_column_info,
    "calculate_statistics": calculate_statistics,
    "calculate": calculate,
}


def run_tool_call(name: str, arguments: dict) -> dict:
    func = FUNCTION_MAP[name]
    return func(**arguments)


def mock_llm_decide_tool(user_message: str):
    text = user_message.lower()

    if "summarize" in text and "dataset" in text:
        return "summarize_dataset", {}

    if "info" in text and "column" in text:
        import re
        match = re.search(r"'([^']+)'", user_message)
        col = match.group(1) if match else "label"
        return "get_column_info", {"column": col}

    if "statistics" in text or "average" in text or "mean" in text:
        import re
        match = re.search(r"'([^']+)'", user_message)
        col = match.group(1) if match else "pixel0"
        stats = ["mean", "max", "count"]
        return "calculate_statistics", {"column": col, "stats": stats}

    if any(op in text for op in ["+", "-", "*", "/", "x", "×"]):
        expr = user_message.replace("Calculate", "").replace("calculate", "")
        expr = expr.replace("What is", "").replace("what is", "")
        expr = expr.replace("×", "*").replace("x", "*")
        expr = expr.strip()
        return "calculate", {"expression": expr}

    return None, {}


def chat_with_tool_calling_mock(user_message: str) -> str:
    tool_name, args = mock_llm_decide_tool(user_message)

    if tool_name is None:
        return "I did not detect a specific data-science tool to call for this request."

    result = run_tool_call(tool_name, args)

    if tool_name == "summarize_dataset":
        return (
            f"The dataset has {result['rows']} rows and {result['columns']} columns. "
            f"Example columns: {', '.join(result['column_names'][:5])} ..."
        )

    if tool_name == "get_column_info":
        if "error" in result:
            return result["error"]
        return (
            f"Column '{result['column']}' has dtype {result['dtype']}, "
            f"{result['non_null_count']} non-null values and {result['null_count']} nulls."
        )

    if tool_name == "calculate_statistics":
        if "error" in result:
            return result["error"]
        parts = []
        for key in ["mean", "median", "std", "min", "max", "count"]:
            if key in result:
                parts.append(f"{key} = {result[key]}")
        stats_text = "; ".join(parts)
        return f"Statistics for column '{result['column']}': {stats_text}."

    if tool_name == "calculate":
        if "error" in result:
            return f"Could not evaluate expression: {result['error']}"
        return f"The result of {result['expression']} is {result['result']}."

    return f"Tool '{tool_name}' returned: {result}"


if __name__ == "__main__":
    print("Data Science Function-Calling Assistant (mock, no API)")
    print("Examples:")
    print("- Summarize the dataset.")
    print("- Give me info about the 'label' column.")
    print("- Calculate statistics (mean, max, count) for the 'pixel0' column.")
    print("- What is 25 * 48?")
    print()

    while True:
        user = input("You: ").strip()
        if user.lower() in ["exit", "quit"]:
            break
        answer = chat_with_tool_calling_mock(user)
        print("Assistant:", answer)
        print()