"""
CrewAI + MCPServerAdapter (Streamable HTTP) — TRUE MCP usage
==============================================================
Unlike 1_wb_mcp.py (which hand-rolled the MCP client and hardcoded
3 tool names + argument schemas), this script lets CrewAI's
MCPServerAdapter do the real MCP handshake:

    1. Connect once to the remote MCP server over Streamable HTTP.
    2. Call the server's own `list_tools()` under the hood.
    3. Auto-generate CrewAI Tool objects 1:1 from whatever the server
       exposes — names, descriptions, and argument schemas all come
       FROM THE SERVER, not from us.
    4. Hand those tools to the Agent. The LLM now decides, at runtime,
       which discovered tool to call and with what arguments —
       based on the tool descriptions it receives from the server,
       not on anything we wrote in advance.

Requirements:
    pip install crewai "crewai-tools[mcp]" python-dotenv

.env should define:
    MODEL_NAME=<your model, e.g. gpt-4o-mini or a local model name> We use qwen3.5 9b locally
    OPENAI_BASE_URL=<your LLM endpoint - OpenAI, or a local server like LMStudio>
    OPENAI_API_KEY=<key, or any placeholder string if your local server ignores it>

Refer to documentation for CrewAI and MCP at: https://docs.crewai.com/v1.15.27/en/mcp/overview

Note: Took about 296 seconds to complete the Task
"""

import os
import time
from dotenv import load_dotenv

from crewai import Agent, Crew, Process, Task, LLM
from crewai_tools import MCPServerAdapter

load_dotenv()

# --- LLM Configuration -------------------------------------------------
# Works the same whether this points at an API-based LLM (OpenAI, etc.)
# or a local OpenAI-compatible server (Ollama, LM Studio, ...).
# The only hard requirement: the model must support function/tool calling.
# Qwen3.5 9b that we use locally allows function/tool calling.
# The Gemini Models used by Students allows function/tool calling but may have Rate Limits.
# If we hit Rate Limits - set the max_iter=3 or max_iter=5 in the Agent definition
MODEL_NAME = os.getenv("MODEL_NAME")
BASE_URL = os.getenv("OPENAI_BASE_URL")
API_KEY = os.getenv("OPENAI_API_KEY")

llm = LLM(
    model=f"openai/{MODEL_NAME}",
    base_url=BASE_URL,
    api_key=API_KEY,
    temperature=0.0,  # deterministic tool selection for class demos
)

# --- MCP Server Connection Parameters -----------------------------------
# Remote server -> Streamable HTTP transport (NOT stdio, since nothing
# is running locally). This is the only transport-specific config needed;
# everything else (tool names, schemas) is discovered automatically.
DATA360_MCP_URL = "https://maimcpext.worldbank.org/ext/data360/mcp"

server_params = {
    "url": DATA360_MCP_URL,
    "transport": "streamable-http",
}


def build_and_run_crew(data360_tools):
    """Builds the agents/tasks/crew using whatever tools were discovered
    from the MCP server, and runs it. Kept inside the `with` block so the
    MCP connection stays open for the full crew execution."""

    print(f"\nDiscovered {len(data360_tools)} tool(s) from the Data360 MCP server:")
    for t in data360_tools:
        print(f"  - {t.name}: {t.description[:100]}...")

    # ---------------------------------------------------------------
    # Agents — note: tools=data360_tools passes through EVERYTHING the
    # server advertised. We never name a specific tool anywhere below.
    # ---------------------------------------------------------------
    data_agent = Agent(
        role="World Bank Data360 MCP Specialist",
        goal=(
            "Use whatever tools are available from the connected Data360 MCP "
            "server to discover the correct indicator and database IDs, then "
            "retrieve validated time-series data."
        ),
        backstory=(
            "You are an AI data engineer connected live to the World Bank "
            "Data360 MCP server. You inspect the tools made available to you "
            "and decide which ones to call and in what order, based solely "
            "on their names and descriptions."
        ),
        tools=data360_tools,
        verbose=False,
        llm=llm,
    )

    analyst_agent = Agent(
        role="Senior Economic Analyst",
        goal="Analyze time series observations retrieved via MCP tools and write comparative summaries.",
        backstory=(
            "You are a development economist who interprets data gathered "
            "from World Bank MCP servers to deliver structured, objective "
            "macroeconomic insights."
        ),
        verbose=False,
        llm=llm,
    )

    # ---------------------------------------------------------------
    # Tasks — deliberately written WITHOUT naming a specific tool.
    # The agent must read the discovered tool descriptions and decide
    # for itself which ones to call, in which order, with what args.
    # ---------------------------------------------------------------
    mcp_discovery_task = Task(
        description=(
            "Using the MCP tools available to you, find the correct indicator "
            "ID and database ID for 'GDP per capita' for India (ISO code IND) from 2004 to 2025, "
            "then retrieve the historical time-series values for that indicator. "
            "Decide for yourself which of your available tools to use and in "
            "what order — do not assume any tool name in advance."
        ),
        expected_output="Valid indicator ID, database ID, and the retrieved GDP per capita time-series data " \
        "for India.",
        agent=data_agent,
    )

    mcp_analysis_task = Task(
        description=(
            "Review the time-series data retrieved via the MCP server in the "
            "previous step. Synthesize the key trends, growth trajectory, and "
            "periodic highlights for India into an executive summary."
        ),
        expected_output="An executive briefing summarizing India's GDP per capita trajectory " \
        "based strictly on the MCP data.",
        agent=analyst_agent,
    )

    mcp_crew = Crew(
        agents=[data_agent, analyst_agent],
        tasks=[mcp_discovery_task, mcp_analysis_task],
        process=Process.sequential,
        verbose=True,
    )

    print("\n--- Starting CrewAI Workflow connected to Data360 MCP Server (true MCPServerAdapter usage) ---")
    start_time = time.time()
    result = mcp_crew.kickoff()
    print("\n================ FINAL MCP BRIEFING ================\n")
    print(result)
    print(f"⏱️ Total time taken: {time.time() - start_time:.2f} seconds\n")
    return result


if __name__ == "__main__":
    # The `with` block owns the entire MCP session lifecycle: it connects
    # once, keeps the session alive for the whole crew run, and cleanly
    # closes it on exit — unlike the per-call connect/disconnect pattern
    # in the earlier hand-rolled version.
    #
    # connect_timeout is optional; raise it if the public endpoint is slow.
    with MCPServerAdapter(server_params, connect_timeout=60) as data360_tools:
        if not data360_tools:
            raise RuntimeError(
                "No tools were returned by the Data360 MCP server. "
                "Check that the URL is correct and the server is reachable."
            )
        build_and_run_crew(data360_tools)