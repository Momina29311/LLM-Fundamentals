# Day 94 — Data Science AI Agent

This project implements a simple AI agent for data science tasks.  
It demonstrates the core agent loop: **decide → act → observe → decide again → final answer**.

## Concepts

- **AI Agent**: A controller that can:
  - Choose which tool to call.
  - Observe tool results.
  - Decide the next step.
  - Stop when it has enough information to answer.

- **Agent vs Chatbot**:
  - Chatbot: User → LLM → Answer (single step).
  - Agent: User → Agent → Tool → Observe → Agent → … → Answer (multi-step, adaptive).

- **Agent Loop**:
  - Perceive/Observe: user question + conversation history + tool results.
  - Decide: choose next action (call a tool or finish).
  - Act: execute the chosen tool.
  - Observe: feed result back into context and repeat.

## Project Structure

```text
day-94-ai-agent/
├── notebook.ipynb        # Demo notebook with agent runs
├── agent.py              # Agent loop implementation
├── tools.py              # Data science tools
├── llm_client.py         # "Brain" of the agent (rule-based demo)
├── train.csv             # Dataset
├── README.md
└── screenshots/
    ├── agent-demo.png
    └── agent-workflow.png
```

## Tools

- `summarize_dataset(path)`  
  Returns rows, columns, dtypes, missingness, and head of the dataset.

- `get_column_info(path, column)`  
  Returns dtype, count, missing, min/max (if numeric), and sample values.

- `calculate_statistics(path, column)`  
  Returns count, mean, std, min, quartiles, max for a numeric column.

- `calculate(expression, context)`  
  Evaluates simple arithmetic/comparison expressions using provided numbers.

## Example Questions

- “Summarize the dataset.”
- “Analyze the pixel0 column and tell me whether its average value is greater than 50.”
- “Analyze the pixel0 column and tell me whether its average value is greater than 0.”
- “Summarize the dataset, then tell me the mean of pixel0 and whether it is greater than 50.”

## How to Run

1. Ensure you have Python 3 and required packages:
   ```bash
   pip install pandas
   ```
   (No external LLM is required for this demo; the agent uses a rule-based controller in `llm_client.py`.)

2. Open `notebook.ipynb` in Jupyter/VS Code.

3. Run the demo cells to see the agent in action.

## Agent Workflow

```text
User Question
      ↓
  AI Agent
      ↓
  Choose Tool
      ↓
  Python Tool
      ↓
   Result
      ↓
  Decide Again (or finish)