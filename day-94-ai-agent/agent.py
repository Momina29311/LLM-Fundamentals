import json
from tools import summarize_dataset, get_column_info, calculate_statistics, calculate
from llm_client import llm_choose_action

TOOLS_MAP = {
    "summarize_dataset": summarize_dataset,
    "get_column_info": get_column_info,
    "calculate_statistics": calculate_statistics,
    "calculate": calculate,
}

def run_agent(user_question: str, dataset_path: str, max_turns: int = 6) -> str:
    history = [
        {
            "role": "user",
            "content": (
                f"Dataset path: {dataset_path}\n"
                f"User question: {user_question}"
            ),
        }
    ]

    for turn in range(max_turns):
        decision = llm_choose_action(history, dataset_path)

        if decision["action"] == "finish":
            return decision["answer"]

        tool_name = decision["tool"]
        args = decision["args"]

        if tool_name not in TOOLS_MAP:
            history.append({
                "role": "tool",
                "content": json.dumps({"error": f"Unknown tool: {tool_name}"}),
            })
            continue

        try:
            result = TOOLS_MAP[tool_name](**args)
        except Exception as e:
            result = {"error": str(e)}

        history.append({
            "role": "tool",
            "content": json.dumps({
                "tool": tool_name,
                "args": args,
                "result": result,
            }),
        })

    return "I couldn't complete the task within the step limit. Try a simpler question or increase max_turns."