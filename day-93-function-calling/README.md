# Day 93 — Function-Calling Data Science Assistant

## Idea

This project demonstrates **function calling** with a mock LLM:  
instead of answering everything itself, the LLM decides which Python tool to call, passes arguments, and uses the result to generate a final answer.

This is the key pattern behind tool-using LLMs and AI agents.

## Tools

The assistant has access to these data-science tools:

- `summarize_dataset()` – basic summary of the dataset (rows, columns, types).
- `get_column_info(column)` – info about a specific column (dtype, nulls, stats).
- `calculate_statistics(column, stats)` – compute mean, median, std, min, max, count.
- `calculate(expression)` – safe evaluation of math expressions like `"25 * 48"`.

## Project structure

```text
day-93-function-calling/
│
├── notebook.ipynb        # Main demo: mock LLM + tool calling
├── tools.py              # Tool implementations (dataset + calculator)
├── train.csv             # Kaggle dataset (MNIST-like, 42k rows, 785 columns)
├── README.md
└── screenshots/          # Screenshots of demo runs
```

## How it works (flow)

For each user question:

1. **Mock LLM** inspects the question and selects a tool + arguments.  
2. The selected **Python function** is called from `FUNCTION_MAP`.  
3. The **tool result** (dict) is returned.  
4. The assistant formats a **human-readable answer**.

Example:

- User: “Calculate the mean, maximum, and count for the 'pixel0' column.”  
- Mock LLM → `calculate_statistics(column="pixel0", stats=["mean","max","count"])`  
- Python → computes stats from `train.csv`  
- Assistant → “Statistics for column 'pixel0': mean = 0.0; max = 0.0; count = 42000.”

## Example queries

Run these in `notebook.ipynb`:

```python
demo_questions = [
    "Summarize the dataset.",
    "What information is available in the 'label' column?",
    "Calculate the mean, maximum, and count for the 'pixel0' column.",
    "What is 25 multiplied by 48?",
]
```

Expected outputs:

- Dataset summary with rows/columns and example column names.  
- Info about the `label` column (dtype, non-null, nulls).  
- Statistics for `pixel0` (mean, max, count).  
- Math result: `25 * 48 = 1200`.

Error-handling examples:

```python
error_demo_questions = [
    "Give me info about the 'age' column.",
    "Calculate mean and std for the 'nonexistent_column' column.",
    "What is 25 * ?",
]
```

These show graceful error messages when:
- The column doesn’t exist.  
- The expression is invalid.

## Running the demo

1. Ensure `train.csv` is in the same folder as `tools.py` and `notebook.ipynb`.  
2. Open `notebook.ipynb` in VS Code or Jupyter.  
3. Run all cells from top to bottom.  
4. Execute the `demo_questions` and `error_demo_questions` cells to see the full flow.

## What I learned

- How function/tool calling lets LLMs delegate work to code instead of doing everything themselves.  
- How to design simple tool schemas (function name + arguments).  
- How to route user questions to the right tool with basic rules.  
- How to handle tool errors gracefully and explain them to the user.  
- How this pattern leads directly into **AI agents** (Day 94): reasoning + tools + multiple steps + memory.

## Next steps

- Replace the mock LLM with a real LLM API that supports tool calling.  
- Add more data-science tools (e.g., correlation, simple plots, clustering).  
- Turn this into a small Streamlit app for interactive use.