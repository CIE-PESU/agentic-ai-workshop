"""
CrewAI + hand-rolled MCP client — "FAKE" MCP usage
====================================================
This script DOES speak the real MCP wire protocol (Streamable HTTP,
ClientSession, session.initialize(), session.call_tool()) — but it
hardcodes the 3 tool names and their argument schemas as Python
wrapper functions below. The agent never sees the server's own
tool list; it only sees 3 pre-written CrewAI tools.

That makes this "MCP-shaped REST" rather than true MCP: compare this
file to 1_wb_mcpserver.py, which hands the agent the tools the
server discovers on its own, with no hardcoded names anywhere.

Scope of work (matches 1_wb_api.py and 1_wb_mcpserver.py for a clean 3-way classroom comparison):
    Retrieve and summarize India's GDP per capita, 2004-2025.
Note: Took about 221 seconds to complete the Task
"""

import os
import time
import asyncio
from contextlib import AsyncExitStack
from crewai import Agent, Crew, Process, Task, LLM
from crewai.tools import tool
from dotenv import load_dotenv

# MCP SDK Client modules
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client  # FIXED: was "streamable_http_client"

load_dotenv()

# --- Config for Heavy Model (CrewAI) ---
MODEL_NAME = os.getenv("MODEL_NAME")
BASE_URL = os.getenv("OPENAI_BASE_URL")
API_KEY = os.getenv("OPENAI_API_KEY")

llm = LLM(
    model=f"openai/{MODEL_NAME}",
    base_url=BASE_URL,
    api_key=API_KEY,
    temperature=0.0,  # Low temp for deterministic tool/memory selection
)

# Public World Bank Data360 MCP Endpoint
# (You can also point this to http://localhost:8000/mcp if running npx @worldbank/data360-mcp locally)
DATA360_MCP_URL = "https://maimcpext.worldbank.org/ext/data360/mcp"


# =====================================================================
# 1. HELPER: ASYNC MCP TOOL CALLER
# =====================================================================

async def _call_mcp_tool_async(tool_name: str, arguments: dict) -> str:
    """Connects to the Data360 MCP Server and executes an MCP tool by name."""
    print("Calling the _call_mcp_tool_async Function to invoke the MCP Request with the WB360 MCP Server")
    async with AsyncExitStack() as stack:
        # Establish Streamable HTTP Transport connection
        read_stream, write_stream, _ = await stack.enter_async_context(
            streamablehttp_client(DATA360_MCP_URL)
        )
        # Create and initialize MCP session
        session = await stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )
        await session.initialize()

        # Call the requested tool on the MCP server
        result = await session.call_tool(tool_name, arguments)

        # Parse MCP TextContent response
        if result.content:
            return result.content[0].text
        return "No data returned from MCP tool."


def run_mcp_tool(tool_name: str, arguments: dict) -> str:
    """Synchronous wrapper for CrewAI tool compatibility."""
    return asyncio.run(_call_mcp_tool_async(tool_name, arguments))


# =====================================================================
# 2. CREWAI TOOLS WRAPPING THE DATA360 MCP SERVER
#    (hardcoded tool names + schemas — this is the "fake MCP" part)
# =====================================================================

@tool("MCP: Search Indicators")
def mcp_search_indicators(query: str, required_country: str = "IND") -> str:
    """
    Calls the MCP server tool 'data360_search_indicators'.
    Searches the World Bank catalog for indicators related to a topic and checks country coverage.
    """
    print(f"Calling the Tool Function mcp_search_indicators for query: {query}")
    args = {
        "query": query,
        "required_country": required_country,
    }
    return run_mcp_tool("data360_search_indicators", args)


@tool("MCP: Fetch Data")
def mcp_get_data(database_id: str, indicator_id: str, country_code: str = "IND",
                  start_year: int = 2004, end_year: int = 2025) -> str:
    """
    Calls the MCP server tool 'data360_get_data'.
    Fetches observations from Data360 with country, year, and dimension filters.
    """
    print("Calling the Tool Function mcp_get_data for the Indicators and the Country ID")
    args = {
        "database_id": database_id,
        "indicator_id": indicator_id,
        "country_code": country_code,
        "start_year": start_year,
        "end_year": end_year,
    }
    return run_mcp_tool("data360_get_data", args)


@tool("MCP: Summarize Data")
def mcp_summarize_data(database_id: str, indicator_id: str, country_code: str = "IND",
                        start_year: int = 2004, end_year: int = 2025) -> str:
    """
    Calls the MCP server tool 'data360_summarize_data'.
    Returns aggregated summary statistics and period trends directly from the MCP server.
    """
    print("Calling the Tool Function mcp_summarize_data for the Indicator and the Country ID")
    args = {
        "database_id": database_id,
        "indicator_id": indicator_id,
        "country_code": country_code,
        "start_year": start_year,
        "end_year": end_year,
    }
    return run_mcp_tool("data360_summarize_data", args)


# =====================================================================
# 3. CREWAI AGENTS
# =====================================================================

data_agent = Agent(
    role="World Bank Data360 MCP Specialist",
    goal="Use Model Context Protocol (MCP) tools to discover indicator IDs and retrieve validated time-series data.",
    backstory=(
        "You are an AI data engineer connected to the official World Bank Data360 MCP server. "
        "You use MCP protocol tools to verify country coverage and extract accurate statistical series."
    ),
    tools=[mcp_search_indicators, mcp_get_data, mcp_summarize_data],
    verbose=False,
    llm=llm,
)

analyst_agent = Agent(
    role="Senior Economic Analyst",
    goal="Analyze time series observations provided by the MCP tools and write comparative summaries.",
    backstory=(
        "You are a development economist who interprets data gathered from World Bank MCP servers "
        "to deliver structured, objective macroeconomic insights."
    ),
    verbose=False,
    llm=llm,
)


# =====================================================================
# 4. CREWAI TASKS — scope: India GDP per capita, 2004-2025
# =====================================================================

mcp_discovery_task = Task(
    description=(
        "1. Use 'MCP: Search Indicators' to find the indicator ID and database ID for "
        "'GDP per capita' for India (IND).\n"
        "2. Use 'MCP: Fetch Data' or 'MCP: Summarize Data' to retrieve historical values "
        "for India from 2004 to 2025."
    ),
    expected_output="Valid indicator ID, database ID, and the retrieved GDP per capita "
                     "time-series data for India from 2004 to 2025.",
    agent=data_agent,
)

mcp_analysis_task = Task(
    description=(
        "Review the time-series data retrieved via the MCP server. "
        "Synthesize the key trends, growth trajectory, and periodic highlights for India's "
        "GDP per capita from 2004 to 2025 into an executive summary."
    ),
    expected_output="An executive briefing summarizing India's GDP per capita trajectory "
                     "from 2004 to 2025, based strictly on the MCP data.",
    agent=analyst_agent,
)


# =====================================================================
# 5. EXECUTION
# =====================================================================

if __name__ == "__main__":
    mcp_crew = Crew(
        agents=[data_agent, analyst_agent],
        tasks=[mcp_discovery_task, mcp_analysis_task],
        process=Process.sequential,
        verbose=True,
    )

    print("--- Starting CrewAI Workflow connected to Data360 MCP Server (hand-rolled / 'fake' MCP) ---")
    start_time = time.time()
    result = mcp_crew.kickoff()
    print("\n================ FINAL MCP BRIEFING ================\n")
    print(result)
    print(f"⏱️ Total time taken: {time.time() - start_time:.2f} seconds\n")