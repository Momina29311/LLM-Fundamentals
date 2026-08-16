from typing import TypedDict, Any

from langgraph.graph import StateGraph, START, END

from tools import (
    load_dataset,
    summarize_dataset,
    calculate_mean,
    analyze_mean,
)


class AnalysisState(TypedDict, total=False):
    question: str
    intent: str
    selected_tool: str
    column: str
    threshold: float
    result: Any
    final_answer: str


def analyze_query(state: AnalysisState) -> AnalysisState:
    """
    Analyze the user's question and identify the requested operation.
    """
    question = state["question"].lower()

    if "summarize" in question or "summary" in question:
        intent = "summary"

    elif "greater than" in question or "more than" in question:
        intent = "comparison"

    elif "mean" in question or "average" in question:
        intent = "mean"

    else:
        intent = "unknown"

    return {
        "intent": intent,
        "column": "pixel0",
    }


def select_tool(state: AnalysisState) -> AnalysisState:
    """
    Select the analysis tool based on the detected intent.
    """
    intent = state["intent"]

    if intent == "summary":
        selected_tool = "summarize_dataset"

    elif intent == "mean":
        selected_tool = "calculate_mean"

    elif intent == "comparison":
        selected_tool = "analyze_mean"

    else:
        selected_tool = "unknown"

    return {
        "selected_tool": selected_tool,
    }


def route_tool(state: AnalysisState) -> str:
    """
    Decide which execution route should run next.
    """
    selected_tool = state["selected_tool"]

    if selected_tool == "summarize_dataset":
        return "summary"

    elif selected_tool == "calculate_mean":
        return "mean"

    elif selected_tool == "analyze_mean":
        return "comparison"

    return "unknown"


def execute_summary(state: AnalysisState) -> AnalysisState:
    """
    Execute the dataset-summary tool.
    """
    df = load_dataset()

    return {
        "result": summarize_dataset(df),
    }


def execute_mean(state: AnalysisState) -> AnalysisState:
    """
    Execute the mean-calculation tool.
    """
    df = load_dataset()

    return {
        "result": calculate_mean(
            df,
            state["column"],
        ),
    }


def execute_comparison(state: AnalysisState) -> AnalysisState:
    """
    Execute the mean-comparison tool.
    """
    df = load_dataset()

    return {
        "result": analyze_mean(
            df,
            state["column"],
            state.get("threshold", 50),
        ),
    }


def execute_unknown(state: AnalysisState) -> AnalysisState:
    """
    Handle unsupported questions.
    """
    return {
        "result": "I could not understand the requested analysis.",
    }


def generate_answer(state: AnalysisState) -> AnalysisState:
    """
    Convert the tool result into a readable final answer.
    """
    selected_tool = state["selected_tool"]
    result = state["result"]

    if selected_tool == "summarize_dataset":
        answer = (
            f"The dataset contains {result['rows']} rows and "
            f"{result['columns']} columns. It has "
            f"{result['missing_values']} missing values."
        )

    elif selected_tool == "calculate_mean":
        answer = (
            f"The mean of {state['column']} is "
            f"{result:.2f}."
        )

    elif selected_tool == "analyze_mean":
        answer = (
            f"The mean of {result['column']} is "
            f"{result['mean']:.2f}. Therefore, it is "
            f"{result['comparison']} {result['threshold']}."
        )

    else:
        answer = str(result)

    return {
        "final_answer": answer,
    }


# Create the graph
workflow = StateGraph(AnalysisState)

# Register nodes
workflow.add_node("analyze_query", analyze_query)
workflow.add_node("select_tool", select_tool)
workflow.add_node("execute_summary", execute_summary)
workflow.add_node("execute_mean", execute_mean)
workflow.add_node("execute_comparison", execute_comparison)
workflow.add_node("execute_unknown", execute_unknown)
workflow.add_node("generate_answer", generate_answer)

# Normal edges
workflow.add_edge(START, "analyze_query")
workflow.add_edge("analyze_query", "select_tool")

# Conditional routing
workflow.add_conditional_edges(
    "select_tool",
    route_tool,
    {
        "summary": "execute_summary",
        "mean": "execute_mean",
        "comparison": "execute_comparison",
        "unknown": "execute_unknown",
    },
)

# All execution routes lead to the answer node
workflow.add_edge("execute_summary", "generate_answer")
workflow.add_edge("execute_mean", "generate_answer")
workflow.add_edge("execute_comparison", "generate_answer")
workflow.add_edge("execute_unknown", "generate_answer")

workflow.add_edge("generate_answer", END)

# Compile the graph
graph = workflow.compile()


if __name__ == "__main__":
    questions = [
        "Summarize the dataset.",
        "What is the mean of pixel0?",
        "Analyze pixel0 and tell me whether its mean is greater than 50.",
    ]

    # Run the three demonstration questions
    for question in questions:
        result = graph.invoke(
            {
                "question": question,
                "threshold": 50,
            }
        )

        print(f"\nQuestion: {question}")
        print(f"Answer: {result['final_answer']}")

    # Display state updates for one question
    print("\n--- LangGraph State Updates ---")

    for update in graph.stream(
        {
            "question": "What is the mean of pixel0?",
            "threshold": 50,
        },
        stream_mode="updates",
    ):
        print(update)

    # Display the Mermaid graph
    print("\n--- Mermaid Graph ---")
print(graph.get_graph().draw_mermaid())

try:
    graph.get_graph().draw_mermaid_png(
        output_file_path="workflow.png"
    )
    print("\nDiagram saved as workflow.png")

except Exception as error:
    print("\nCould not create PNG diagram.")
    print("Reason:", error)