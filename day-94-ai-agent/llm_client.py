import json


def llm_choose_action(history, dataset_path):
    """
    Simple rule-based 'agent' that mimics an AI agent loop.
    It looks at the last user message and decides which tool to call next.
    """
    # Get the last user message
    last_user = None
    for m in reversed(history):
        if m["role"] == "user":
            last_user = m["content"]
            break

    if last_user is None:
        return {
            "action": "finish",
            "answer": "No user question found.",
        }

    text = last_user.lower()

    # If we already have tool results in history, use them to finish
    tool_results = [m for m in history if m["role"] == "tool"]

    # Rule 1: If question asks to summarize dataset and no summary yet
    # Avoid triggering this when the question is mainly about pixel0 stats
    if (
        ("summarize" in text or "summary" in text or "dataset" in text)
        and "pixel0" not in text
        and not any("summarize_dataset" in str(r) for r in tool_results)
    ):
        return {
            "action": "tool",
            "tool": "summarize_dataset",
            "args": {"path": dataset_path},
        }

    # Rule 2: If question mentions a column and wants info
    if "pixel0" in text and ("info" in text or "column" in text) and not any(
        "get_column_info" in str(r) for r in tool_results
    ):
        return {
            "action": "tool",
            "tool": "get_column_info",
            "args": {"path": dataset_path, "column": "pixel0"},
        }

    # Rule 3: If question mentions mean/average/statistics for a column
    if "pixel0" in text and ("mean" in text or "average" in text or "statistics" in text):
        # If we don't have stats yet, call calculate_statistics
        if not any("calculate_statistics" in str(r) for r in tool_results):
            return {
                "action": "tool",
                "tool": "calculate_statistics",
                "args": {"path": dataset_path, "column": "pixel0"},
            }
        else:
            # We already have stats, now finish with an answer
            stats_result = None
            for r in tool_results:
                try:
                    data = json.loads(r["content"])
                except Exception:
                    continue
                if data.get("tool") == "calculate_statistics":
                    stats_result = data.get("result")
                    break

            if stats_result and "mean" in stats_result:
                mean_val = stats_result["mean"]
                if "greater than 50" in text or "> 50" in text:
                    ans = (
                        f"The 'pixel0' column has an average value of {mean_val}, "
                        f"which is {'greater' if mean_val > 50 else 'not greater'} than 50."
                    )
                elif "greater than 0" in text or "> 0" in text:
                    ans = (
                        f"The 'pixel0' column has an average value of {mean_val}, "
                        f"which is {'greater' if mean_val > 0 else 'not greater'} than 0."
                    )
                else:
                    ans = f"The 'pixel0' column has an average value of {mean_val}."
                return {
                    "action": "finish",
                    "answer": ans,
                }

    # Rule 4: Generic fallback for pixel0 + greater than X
    if "pixel0" in text and ("greater than" in text or ">" in text):
        # If no stats yet, get them
        if not any("calculate_statistics" in str(r) for r in tool_results):
            return {
                "action": "tool",
                "tool": "calculate_statistics",
                "args": {"path": dataset_path, "column": "pixel0"},
            }
        else:
            # Use existing stats to answer
            stats_result = None
            for r in tool_results:
                try:
                    data = json.loads(r["content"])
                except Exception:
                    continue
                if data.get("tool") == "calculate_statistics":
                    stats_result = data.get("result")
                    break

            if stats_result and "mean" in stats_result:
                mean_val = stats_result["mean"]
                if "greater than 50" in text or "> 50" in text:
                    ans = (
                        f"The 'pixel0' column has an average value of {mean_val}, "
                        f"which is {'greater' if mean_val > 50 else 'not greater'} than 50."
                    )
                elif "greater than 0" in text or "> 0" in text:
                    ans = (
                        f"The 'pixel0' column has an average value of {mean_val}, "
                        f"which is {'greater' if mean_val > 0 else 'not greater'} than 0."
                    )
                else:
                    ans = f"The 'pixel0' column has an average value of {mean_val}."
                return {
                    "action": "finish",
                    "answer": ans,
                }

    # Default: finish with a simple explanation
    return {
        "action": "finish",
        "answer": (
            "This is a simple rule-based demo agent. "
            "It can handle questions about summarizing the dataset and analyzing the 'pixel0' column. "
            "For a full AI agent, connect a real LLM here."
        ),
    }