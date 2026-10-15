# Using Memory in CrewAI — PESU CIE Agentic AI Workshop

This folder contains two hands-on examples showing how **Memory** can be enabled in a CrewAI crew and how agents can use it across tasks and across runs.

An agent can be given a role, goal, backstory, and task in Python. Enabling `memory=True` lets the agent or crew store what it has learned and draw on that information later, so it does not have to start from zero every time.

## Learning objectives

By working through these examples, you will learn how to:

- Enable memory at the agent level (`memory=True` on an `Agent`) and at the crew level (`memory=True` on a `Crew`).
- Build a sequential multi-agent crew in which tasks pass context to each other with `context=[...]`.
- Configure a local OpenAI-compatible model through LM Studio, using the same `LLM` setup in both examples.
- Use an agent that checks its memory before calling a web search tool, and observe when it skips the tool.
- Run the same script several times and compare how memory changes the behavior and the output.
- Note that in CrewAI - it uses an unified memory concept and Memory can be set at the Agent level OR at the Crew level.

## Folder structure

```text
UsingMemory/
├── README.md
├── 1_memory.py
└── 2_memory.py
```

Place both Python files in the same folder. Example 2 writes its memory store to the working directory, so run it from this folder.

## Prerequisites

- Python 3.10 or later (use a version supported by the CrewAI version you install).
- `pip` and a terminal.
- **LM Studio** with a model downloaded and its local server running.
- A **Tavily API key** for Example 2, which uses the `TavilySearchTool` for live web search.
- Internet access to install Python packages and to reach the Tavily search service. The LM Studio inference calls themselves run locally.

## 1. Create and activate a virtual environment

Run these commands from the `Memory` directory.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

### Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

## 2. Install dependencies

Install the packages used by the examples:

```bash
pip install crewai crewai-tools python-dotenv openai
```

`crewai-tools` is required for `TavilySearchTool` in `2_memory.py`. If CrewAI reports that memory or the `memory` parameter is unavailable, check the CrewAI version installed in your environment and use a version that supports the memory features used in these scripts.

## 3. Configure your model

Both scripts load environment variables from a `.env` file. Create a `.env` file in the `Memory` folder, the same folder you run the scripts from.

### LM Studio (local model)

1. Open LM Studio and download a model your computer can run.
2. Load the model.
3. Start LM Studio's local server. The usual OpenAI-compatible base URL is `http://localhost:1234/v1`; use the URL shown in your LM Studio settings if it differs.
4. Create `Memory/.env` with the values below.

Example `.env`:

```dotenv
MODEL_NAME=qwen3.5-9b
OPENAI_BASE_URL=http://localhost:1234/v1
OPENAI_API_KEY=lm-studio
TAVILY_API_KEY=replace_with_your_tavily_api_key
```

Replace `MODEL_NAME` with the model identifier expected by your LM Studio server. The `OPENAI_API_KEY` value can be a placeholder for local LM Studio use; it is not a real secret in this configuration. `TAVILY_API_KEY` is only needed for `2_memory.py`, but both scripts check for the variables they use at startup.

The LLM is defined in each script in the same way, pointing at LM Studio through the OpenAI-compatible interface:

```python
llm = LLM(
    model=f"openai/{MODEL_NAME}",
    base_url=BASE_URL,
    api_key=API_KEY,
    temperature=0.2  # 1_memory.py uses 0.2; 2_memory.py uses 0.0
)
```

> **Security:** Never commit `.env` files or real API keys to Git. Commit a `.env.example` file containing placeholders if you want to document configuration. If a real key has already been pushed to a remote repository, revoke or rotate it.

## Example 1 — Publishing Crew with Memory

**Location:** `1_memory.py`

This example builds a three-agent sequential crew that writes, edits, and publishes a short fantasy novel manuscript. The agents are:

1. **Writer** — writes the complete manuscript. This agent has `memory=True`.
2. **Editor** — reviews and edits the manuscript for grammar, structure, and clarity.
3. **Publisher** — oversees publication and distribution.

Each task depends on the one before it. The editing task receives the writer's output through `context=[write_manuscript_task]`, and the publishing task receives the edited manuscript through `context=[edit_manuscript_task]`.

The writer's expected output includes a hard boundary: the novel must be no more than 1000 words and must be complete in its story.

### Run it

From the `Memory` directory:

```bash
python 1_memory.py
```

The script prints the progress of each agent and the final crew result to the terminal. Because `verbose=True` is set, you can follow each agent's reasoning as it works.

### How the memory is used

Memory is turned on for the **Writer** agent with `memory=True`. The Editor and Publisher agents do not have memory enabled. Use this example to show students how memory is configured on one agent in a crew that otherwise passes information through task context.

## Example 2 — Research Agent: Memory First, Search Second

**Location:** `2_memory.py`

This example builds a single research agent that answers user questions. Its goal and backstory instruct it to check its memory before running a live web search. It has access to `TavilySearchTool`, which returns up to 10 results.

Each run creates a new task asking the agent to answer a query in a concise five-bullet summary. The task tells the agent to answer from memory if it already has enough information, and to use the search tool only when memory is missing or incomplete.

The crew has `memory=True`, which activates the persistent vector storage that saves information from earlier runs. The agent also has `memory=True`.

The LLM for this example uses `temperature=0.0`, which keeps tool and memory selection as consistent as possible from run to run.

### Run it

The script takes a run number as a command-line argument. Run them in order, because runs 2 and 3 depend on what earlier runs stored.

```bash
python 2_memory.py 1   # Run 1: Initial search. Populates memory.
python 2_memory.py 2   # Run 2: Same topic. Should answer from memory without the search tool.
python 2_memory.py 3   # Run 3: New topic. Memory miss. Should trigger the search tool again.
```

Running the script with no argument prints the usage instructions.

Each run prints the result and how long it took. Compare the timing and the verbose output between run 1 and run 2 to see whether the search tool was used.

### Changing the queries

The queries for each run are written in the script. Commented-out alternatives are included so you can try a different topic. For example, run 1 can be changed to the James Webb Space Telescope query, and run 2 to a follow-up question about the same topic.

### How the memory is used

Memory is stored between runs, so information retrieved in run 1 is available in run 2. The instruction to check memory first is in both the agent's backstory and the task description. A memory hit should produce an answer without a search call. A memory miss, such as a new topic in run 3, should produce a new search.

This example is a good place to show students that memory does not guarantee a particular behavior. The agent's choice depends on the model, the prompt, and what memory contains. Check the verbose output rather than assuming the search tool was skipped.

## Troubleshooting

### The script cannot connect to the model

- Confirm that LM Studio is open, the model is loaded, and the local server is running.
- Check `OPENAI_BASE_URL` and `MODEL_NAME` in the `.env` file.
- Test the configured base URL and model identifier against the LM Studio server.
- Ensure you activated the intended virtual environment before installing packages and running the script.

### A required environment variable is missing

- Confirm the `.env` file is in the `Memory` folder and that you are running the script from that folder.
- Check spelling: `MODEL_NAME`, `OPENAI_BASE_URL`, `OPENAI_API_KEY`, and, for `2_memory.py`, `TAVILY_API_KEY`.
- Do not add quotation marks unless your value requires them.

### The search tool fails in Example 2

- Confirm `TAVILY_API_KEY` is set to a valid key.
- Confirm `crewai-tools` is installed.
- Check your internet connection.

### Memory does not seem to persist between runs

- Run the scripts from the same folder each time. The storage location depends on the working directory.
- Run `2_memory.py 1` before `2_memory.py 2`. Run 2 can only use what run 1 stored.
- Check the installed CrewAI version for compatibility with the memory features used in the code.

### The agent searches even when the answer seems to be in memory

Memory retrieval is not deterministic. Look at the verbose output to see what the agent did. Try a closer repeat of the same query, and remember that the instruction to check memory first is guidance for the model, not a guarantee.

## Suggested student experiments

1. In `1_memory.py`, set `memory=True` on the Editor agent as well and compare the final manuscript with the original run.
2. Run `2_memory.py 1` twice and compare the answers and timings. Note whether the second run used the search tool.
3. Run `2_memory.py 2` before `2_memory.py 1` and observe what happens when memory is empty.
4. Change the temperature in `2_memory.py` from `0.0` to `0.2` and see whether tool selection changes.
5. Ask a follow-up question in run 2 that is only partly answered by run 1. Observe whether the agent searches for the missing information.
6. Remove the sentence about checking memory first from the agent's backstory and observe how the behavior changes.

## Key takeaway

**Memory gives an agent a record of what it has seen before; instructions and tools decide what it does with that record.** These examples show that memory can reduce repeated work and that its effect is easiest to understand when you compare runs and read the verbose output.
