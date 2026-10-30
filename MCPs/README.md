# PESU CIE - Agentic AI Workshop

# CrewAI × World Bank Data360 — REST vs MCP (Three-Way Comparison)

A classroom demo that retrieves **India's GDP per capita (2004–2025)** three different ways, using the same two-agent CrewAI crew each time. The only thing that changes across the three scripts is *how* data gets fetched — making it easy to compare plain REST, hand-rolled MCP, and true MCP side-by-side.

---

## The Teaching Progression

| Script | Approach | What it teaches |
|---|---|---|
| `1_wb_api.py` | Plain REST via `wbgapi` | How a developer normally wraps a REST API into CrewAI tools — hardcoded function names and schemas, no MCP |
| `1_wb_mcpfixed.py` | Hand-rolled MCP client | Uses the real MCP wire protocol (Streamable HTTP, `ClientSession`) but still hardcodes the 3 tool names and argument schemas — "MCP-shaped REST" |
| `1_wb_mcpserver.py` | True MCP via `MCPServerAdapter` | Lets CrewAI call `list_tools()` on the server; tool names, descriptions, and schemas are discovered at runtime — no hardcoding anywhere |

Run them in order: each script does the same job, but with progressively less code that *you* have to write.

---

## What each script does

All three scripts follow the same two-agent CrewAI pattern:

1. **Data Agent** — finds the right indicator ID and fetches the GDP per capita time series for India.
2. **Analyst Agent** — receives the raw data and writes an executive summary of the trends.

The data source in every case is the **World Bank Data360** platform:
- REST endpoint: `https://data360api.worldbank.org`
- MCP endpoint: `https://maimcpext.worldbank.org/ext/data360/mcp`

---

## Requirements

### Python packages

```bash
# Core (all three scripts)
pip install crewai python-dotenv

# 1_wb_api.py only
pip install wbgapi

# 1_wb_mcpfixed.py only
pip install mcp

# 1_wb_mcpserver.py only
pip install "crewai-tools[mcp]"
```

Or install everything at once:

```bash
pip install crewai "crewai-tools[mcp]" wbgapi mcp python-dotenv
```

### .env file

Create a `.env` file in the project root:

```env
# The model name as your LLM endpoint expects it (e.g. "qwen3.5-9b" for LM Studio,
# or "gpt-4o-mini" for OpenAI)
MODEL_NAME=qwen3.5-9b

# Your LLM base URL — point this at LM Studio, Ollama, OpenAI, etc.
OPENAI_BASE_URL=http://localhost:1234/v1

# API key — use any placeholder string if your local server ignores it
OPENAI_API_KEY=lm-studio
```

> **Note:** No World Bank API key is needed. The Data360 REST and MCP endpoints are public.

---

## Model requirements

All three scripts require a model that supports **function / tool calling** (the LLM must be able to decide which tool to invoke and with what arguments).

- **Local (recommended for class):** Qwen 3.5 9B served via LM Studio — supports tool calling and runs fully offline.
- **Hosted:** Any Gemini Flash model works, but you may hit **rate limits**. If that happens, add `max_iter=3` or `max_iter=5` to the Agent definition to reduce the number of model calls per run.

---

## LM Studio setup (local model)

1. Download and open [LM Studio](https://lmstudio.ai/).
2. Load the **Qwen 3.5 9B** model.
3. Go to the **Local Server** tab and start the server (default: `http://localhost:1234/v1`).
4. Set `OPENAI_BASE_URL=http://localhost:1234/v1` and `MODEL_NAME=qwen3.5-9b` in your `.env`.

---

## Running the scripts

```bash
# Step 1 — plain REST (no MCP at all)
python 1_wb_api.py

# Step 2 — real MCP wire protocol, but hardcoded tools
python 1_wb_mcpfixed.py

# Step 3 — true MCP with runtime tool discovery
python 1_wb_mcpserver.py
```

Each script prints the full CrewAI message trace and ends with a formatted executive briefing.

**Approximate run times** (Qwen 3.5 9B, local):

| Script | Time |
|---|---|
| `1_wb_api.py` | ~204 s |
| `1_wb_mcpfixed.py` | ~221 s |
| `1_wb_mcpserver.py` | ~296 s |

The MCP server script is slower because it performs the tool-discovery handshake before the crew starts.

---

## Key concept: what makes `1_wb_mcpserver.py` different

The table below shows the single most important difference between the three approaches:

| | Who defines the tool names? | Who defines the argument schemas? |
|---|---|---|
| `1_wb_api.py` | The developer (hardcoded) | The developer (hardcoded) |
| `1_wb_mcpfixed.py` | The developer (hardcoded) | The developer (hardcoded) |
| `1_wb_mcpserver.py` | **The MCP server** (discovered at runtime) | **The MCP server** (discovered at runtime) |

In `1_wb_mcpserver.py`, if the World Bank adds a new tool to their MCP server tomorrow, the agent will find it and use it — with zero code changes on your side.

---

## Project structure

```
.
├── .env                    # Your LLM credentials (never commit this)
├── 1_wb_api.py             # Plain REST via wbgapi
├── 1_wb_mcpfixed.py        # Hand-rolled MCP client (hardcoded tools)
├── 1_wb_mcpserver.py       # True MCP with MCPServerAdapter
└── README.md
```

---

## Further reading

- [CrewAI MCP documentation](https://docs.crewai.com/v1.15.27/en/mcp/overview)
- [World Bank Data360 API](https://data360api.worldbank.org)
- [wbgapi Python client](https://pypi.org/project/wbgapi/)
- [MCP specification](https://modelcontextprotocol.io)