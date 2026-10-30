# pip install wbgapi is required to use the world bank 360 API
# this is a wrapper around the direct v2 API that we can also use from https://data360api.worldbank.org
"""
CrewAI + wbgapi — plain REST usage (NOT MCP)
==============================================
This script talks to the World Bank's REST API through the wbgapi
Python client. There is no MCP protocol here at all: the two tools
below are ordinary, hardcoded Python functions the developer wrote
in advance — exactly the pattern a developer would use with any
REST API, with or without an AI agent in the loop.

Scope of work (matches 1_wb_mcpfixed.py and 1_wb_mcpserver.py for a
clean 3-way classroom comparison):
    Retrieve and summarize India's GDP per capita, 2004-2025.

Note: Took about 204 seconds to complete the Task
"""

import os
import time
from dotenv import load_dotenv
import wbgapi as wb
from crewai import Agent, Crew, Process, Task, LLM
from crewai.tools import tool

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

# =====================================================================
# 1. CREWAI TOOLS USING WBGAPI (hardcoded by the developer — plain REST)
# =====================================================================

@tool("Search World Bank Indicators")
def search_wb_indicators(query: str) -> str:
    """
    Search the World Bank indicator catalog using wbgapi keyword search.
    Returns matching indicator IDs and human-readable titles.
    """
    print(f"Calling the API - wb.series.list for the query: {query}")
    try:
        matches = wb.series.list(q=query)
        results = []
        for i, item in enumerate(matches):
            if i >= 5:  # Limit to top 5 results for context efficiency
                break
            results.append({
                "indicator_id": item["id"],
                "value": item["value"],
            })
        return str(results) if results else f"No indicators found for '{query}'."
    except Exception as e:
        return f"Error searching indicators: {str(e)}"


@tool("Fetch Macroeconomic Time Series")
def fetch_wb_dataframe(country_codes: str, indicator_id: str,
                        start_year: int = 2004, end_year: int = 2025) -> str:
    """
    Fetch time series data using wbgapi into a Pandas DataFrame.
    - country_codes: Comma-separated ISO codes (e.g. 'IND' or 'IND,KOR')
    - indicator_id: World Bank indicator ID (e.g. 'NY.GDP.PCAP.KD' for Constant GDP per capita)
    """
    print("Calling the API - wb.data.DataFrame for the country codes and indicators specified")
    try:
        countries = [c.strip().upper() for c in country_codes.split(",")]
        time_range = range(start_year, end_year + 1)

        df = wb.data.DataFrame(
            series=indicator_id,
            economy=countries,
            time=time_range,
            numericTimeKeys=True,
        )

        if df.empty:
            return f"No observations found for {indicator_id} in {countries}."

        return df.to_string()
    except Exception as e:
        return f"wbgapi Error: {str(e)}"


# =====================================================================
# 2. CREWAI AGENTS — same 2-agent shape as 1_wb_mcp.py and
#    3_wb360_mcpserver.py, so the only variable across all 3 demos
#    is HOW the data gets fetched, not the crew structure.
# =====================================================================

data_engineer = Agent(
    role="World Bank Data Specialist",
    goal="Discover the correct indicator and retrieve India's GDP per capita time series using wbgapi.",
    backstory=(
        "You are an expert quantitative data engineer specializing in international development "
        "databases. You query the World Bank API via wbgapi, verify ISO country codes, and extract "
        "clean data arrays."
    ),
    tools=[search_wb_indicators, fetch_wb_dataframe],
    verbose=False,
    llm=llm,
)

analyst_agent = Agent(
    role="Senior Economic Analyst",
    goal="Analyze the retrieved time-series data and write a comparative summary.",
    backstory=(
        "You are a development economist who interprets data gathered from the World Bank API "
        "to deliver structured, objective macroeconomic insights."
    ),
    verbose=False,
    llm=llm,
)


# =====================================================================
# 3. CREWAI TASKS — scope: India GDP per capita, 2004-2025
# =====================================================================

data_task = Task(
    description=(
        "1. Use 'Search World Bank Indicators' to confirm the indicator ID for Constant GDP per "
        "Capita (or use 'NY.GDP.PCAP.KD').\n"
        "2. Use 'Fetch Macroeconomic Time Series' to retrieve data for India ('IND') from 2004 to 2025.\n"
        "3. Output the retrieved time-series values for India."
    ),
    expected_output="Valid indicator ID and the retrieved GDP per capita time-series data for "
                     "India from 2004 to 2025.",
    agent=data_engineer,
)

analysis_task = Task(
    description=(
        "Review the time-series data retrieved in the previous step. "
        "Synthesize the key trends, growth trajectory, and periodic highlights for India's "
        "GDP per capita from 2004 to 2025 into an executive summary."
    ),
    expected_output="An executive briefing summarizing India's GDP per capita trajectory "
                     "from 2004 to 2025, based strictly on the retrieved data.",
    agent=analyst_agent,
)


# =====================================================================
# 4. CREW EXECUTION
# =====================================================================

if __name__ == "__main__":
    growth_crew = Crew(
        agents=[data_engineer, analyst_agent],
        tasks=[data_task, analysis_task],
        process=Process.sequential,
        verbose=True,
    )

    print("--- Starting World Bank GDP per Capita Crew (plain REST via wbgapi) ---")
    start_time = time.time()
    result = growth_crew.kickoff()
    print("\n================ FINAL BRIEFING ================\n")
    print(result)
    print(f"⏱️ Total time taken: {time.time() - start_time:.2f} seconds\n")