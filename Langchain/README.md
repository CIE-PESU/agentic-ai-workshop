# CIE - Agentic AI Workshop - LangChain Agent Examples

Two starter scripts that show how to build LangChain agents with a Tavily web search tool, backed by either a local Qwen model (via LM Studio) or Google's Gemini Flash Lite.

---

## Files

| File | What it does |
|---|---|
| `1_langchain.py` | Single agent that answers a question using Tavily search |
| `2_langchain.py` | Two-agent pipeline: a Researcher gathers facts, a Writer turns them into a Markdown report |

---

## Requirements

### Python packages

```bash
pip install -U langchain langchain-openai langchain-google-genai langchain-tavily python-dotenv
```

### API keys

Create a `.env` file in the project root with the following:

```env
# Required — get a free key at https://tavily.com
TAVILY_API_KEY=your_tavily_api_key_here

# Only needed if USE_LOCAL_QWEN = False (i.e. you want to use Gemini)
GEMINI_API_KEY=your_google_api_key_here
```

> **Note:** If you are using the local Qwen model via LM Studio, `GEMINI_API_KEY` is not needed.

---

## Choosing a model

Both scripts have a flag at the top:

```python
USE_LOCAL_QWEN = True   # True  -> local Qwen 3.5 9B via LM Studio
                        # False -> Gemini 2.5 Flash Lite (requires GEMINI_API_KEY)
```

Set it to `True` or `False` depending on which model you want to use.

---

## LM Studio setup (local model)

If `USE_LOCAL_QWEN = True`:

1. Download and open [LM Studio](https://lmstudio.ai/).
2. Load the **Qwen 3.5 9B** model.
3. Go to the **Local Server** tab and start the server (default address: `http://localhost:1234/v1`).
4. No real API key is needed — the scripts use `"lm-studio"` as a placeholder.

---

## Running the scripts

### Script 1 — Single agent

```bash
python 1_langchain.py
```

The agent will answer a hard-coded question using Tavily search and print the result.

### Script 2 — Two-agent pipeline

```bash
python 2_langchain.py
```

You will be prompted to enter a research topic. The pipeline will:
1. Run the **Researcher** agent to gather facts with Tavily.
2. Pass the findings to the **Writer** agent to produce a Markdown report.
3. Save the report to a timestamped `.md` file in the current directory.

---

## Project structure

```
.
├── .env                  # Your API keys (never commit this)
├── 1_langchain.py        # Single-agent example
├── 2_langchain.py        # Two-agent pipeline example
└── README.md
```

---

## Tips

- Keep your `.env` file out of version control — add it to `.gitignore`.
- The Researcher agent in `2_langchain.py` is capped at **3 model calls** per run (`ModelCallLimitMiddleware`) to prevent infinite loops.
- You can change `max_results` on `TavilySearch` to control how many web results the agent sees per search.