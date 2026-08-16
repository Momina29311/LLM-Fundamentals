# 🚀 Day 95 — LangGraph Multi-Step Workflow

Part of my **#100DaysOfDataScience** journey.

On Day 95, I explored **LangGraph** and learned how LLM/AI workflows can be represented as structured graphs with nodes, state, and conditional routing.

---

## 🎯 Objective

Build a simple data-science-focused workflow using LangGraph that can:

- Analyze a user's query
- Determine what type of operation is required
- Select the appropriate tool
- Execute the selected operation
- Generate a final answer

---

## 🧠 What I Learned

### What is LangGraph?

LangGraph is a framework for building **stateful, multi-step AI workflows** using graph-based execution.

Instead of treating an AI application as a single prompt → response pipeline, LangGraph allows us to define:

- **Nodes** → individual steps in the workflow
- **Edges** → transitions between steps
- **State** → information passed throughout the workflow
- **Conditional routing** → choosing different paths based on the input

---

## 🔄 Workflow

The workflow built in this project follows:

```text
User Query
     ↓
Analyze Query
     ↓
Select Tool
     ↓
 ┌───────────────┬───────────────┬───────────────┬───────────────┐
 ↓               ↓               ↓               ↓
Comparison      Mean           Summary         Unknown
 ↓               ↓               ↓               ↓
Execute         Execute        Execute         Execute
Comparison      Mean           Summary         Unknown
 └───────────────┴───────────────┴───────────────┴───────────────┘
                         ↓
                  Generate Answer
                         ↓
                       End