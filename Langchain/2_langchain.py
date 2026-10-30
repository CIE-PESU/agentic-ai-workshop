"""
Two-agent pipeline: Researcher (Tavily) -> Writer (Markdown report)
====================================================================

This is NOT a "crew" with automatic hand-off — langchain.agents.create_agent
builds ONE agent at a time. To chain two agents you just run them one after
another in plain Python: agent #1's final answer becomes part of agent #2's
input. That's the whole trick.

Install:
    pip install -U langchain langchain-openai langchain-google-genai langchain-tavily

Env vars needed:
    TAVILY_API_KEY
    GOOGLE_API_KEY   (only if USE_LOCAL_QWEN = False)
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch

from langchain.agents import create_agent
from langchain.agents.middleware import ModelCallLimitMiddleware

# -1. Load the Environment Variables
load_dotenv()


# -----------------------------------------------------------------
# 0. Model switch (same as before)
# -----------------------------------------------------------------
USE_LOCAL_QWEN = True

if USE_LOCAL_QWEN:
    llm = ChatOpenAI(
        model="qwen3.5-9b",
        base_url="http://localhost:1234/v1",
        api_key="lm-studio",
        temperature=0.2,
        max_completion_tokens=2048,
    )
else:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        api_key=os.environ["GEMINI_API_KEY"],
        temperature=0.2,
        max_tokens=2048,
    )

# -----------------------------------------------------------------
# 1. Tools
# -----------------------------------------------------------------
TAVILY_API_KEY=os.getenv("TAVILY_API_KEY")
tavily_search = TavilySearch(max_results=5, topic="general")

# -----------------------------------------------------------------
# 2. Agent #1: Researcher
#    - has the Tavily tool
#    - job is ONLY to gather and summarize facts, with sources
# -----------------------------------------------------------------
researcher = create_agent(
    model=llm,
    tools=[tavily_search],
    system_prompt=(
        "You are a research assistant. Use the tavily_search tool to gather "
        "current, factual information on the given topic. Search as many "
        "times as needed (different angles, not repeats). When done, write "
        "a thorough research brief in plain text: key findings, relevant "
        "statistics or examples, and a short list of the source URLs you "
        "used. Do not write the final report yet -- just the raw findings."
    ),
    # caps this agent to at most N model calls per run as has been set, 
    # so it can't loop forever
    middleware=[ModelCallLimitMiddleware(run_limit=3, exit_behavior="end")],
)

# -----------------------------------------------------------------
# 3. Agent #2: Writer
#    - no tools -- it only works with the text it's handed
#    - job is to turn the research brief into a polished Markdown report
# -----------------------------------------------------------------
writer = create_agent(
    model=llm,
    tools=[],
    system_prompt=(
        "You are a report writer. You will be given a research brief. "
        "Turn it into a well-structured Markdown report with:\n"
        "- A title (# heading)\n"
        "- A short introduction\n"
        "- 2-4 themed sections with ## headings\n"
        "- A brief conclusion\n"
        "- A 'Sources' section at the end listing the URLs you were given\n"
        "Only use the information provided to you. Output raw Markdown, "
        "nothing else (no commentary before or after)."
    ),
)


def print_trace(result, label):
    """Simple stand-in for CrewAI's verbose=True: show every message."""
    print(f"\n===== {label}: message trace =====")
    for m in result["messages"]:
        role = m.type
        text = m.content if isinstance(m.content, str) else str(m.content)
        preview = text if len(text) < 400 else text[:400] + " ...[truncated]"
        print(f"\n--- {role} ---\n{preview}")


def run_pipeline(topic: str, output_path: str = "report.md") -> str:
    # --- Step 1: research ---
    print(f"The Research Topic given is: {topic}\n")

    research_result = researcher.invoke(
        {"messages": [{"role": "user", "content": f"Research this topic: {topic}"}]},
        config={"recursion_limit": 25},
    )
    print_trace(research_result, "RESEARCHER")
    research_brief = research_result["messages"][-1].content

    # --- Step 2: write, handing the brief over as context ---
    writer_input = (
        f"Topic: {topic}\n\n"
        f"Research brief:\n{research_brief}\n\n"
        f"Write the Markdown report now."
    )
    writer_result = writer.invoke(
        {"messages": [{"role": "user", "content": writer_input}]},
        config={"recursion_limit": 10},
    )
    print_trace(writer_result, "WRITER")
    report_md = writer_result["messages"][-1].content

    # --- Step 3: save to disk ---
    Path(output_path).write_text(report_md, encoding="utf-8")
    print(f"\nReport saved to {output_path}")
    return report_md


if __name__ == "__main__":
    topic = input("What topic should I research today: ")
    print("*** Invoking the Langchain Agent Pipeline ***\n")
    output_filename = str(datetime.now()) + "_report.md"
    run_pipeline(
        topic=topic,
        output_path=output_filename,
    )