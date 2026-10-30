"""
Starter code: LangChain create_agent + Tavily web search tool
================================================================

What this shows
----------------
1. How to wire up an LLM two different ways:
   a) A LOCAL model served by LM Studio, called the "OpenAI way"
      (LM Studio exposes an OpenAI-compatible /v1 endpoint).
   b) Google's Gemini Flash Lite, for students who'd rather use a
      hosted model.
2. How to create a Tavily web search tool.
3. How to build and run an agent with langchain.agents.create_agent.

Install (pick what you need):
    pip install -U langchain langchain-openai langchain-google-genai langchain-tavily

Environment variables you'll need:
    TAVILY_API_KEY   -> always required (get a free key at tavily.com)
    GOOGLE_API_KEY    -> only if USE_LOCAL_QWEN = False (Gemini)

LM Studio setup (if USE_LOCAL_QWEN = True):
    - Open LM Studio, load your Qwen 3.5 9B model.
    - Start the "Local Server" (default: http://localhost:1234/v1).
    - No real API key is needed; any placeholder string works.
"""

import os
from dotenv import load_dotenv
from langchain_tavily import TavilySearch

# Hosted Gemini Flash Lite via Google's LangChain integration.
from langchain_google_genai import ChatGoogleGenerativeAI

# For Lamngchain's Agent core framework
from langchain.agents import create_agent

# -1. Load the Environment Variables
load_dotenv()

# -----------------------------------------------------------------
# 0. Flip this switch to choose which model backs the agent.
# -----------------------------------------------------------------
USE_LOCAL_QWEN = True   # True -> LM Studio / Qwen 3.5 9B
                        # False -> Gemini 2.5/3.5 Flash Lite

# -----------------------------------------------------------------
# 1. Initialize the LLM
# -----------------------------------------------------------------
if USE_LOCAL_QWEN:
    # LM Studio speaks the OpenAI Chat Completions protocol, so we
    # just point ChatOpenAI at the local server instead of OpenAI's.
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(
        model="qwen3.5-9b",              # must match the model name shown in LM Studio
        base_url="http://localhost:1234/v1",
        api_key="lm-studio",             # LM Studio ignores the value, but the field is required
        temperature=0.2,
    )
else:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",   # swap for "gemini-3.5-flash-lite" once/if available
        api_key=os.environ["GEMINI_API_KEY"],
        temperature=0.2,
    )

# -----------------------------------------------------------------
# 2. Create the Tavily search tool
# -----------------------------------------------------------------
TAVILY_API_KEY=os.getenv("TAVILY_API_KEY")
tavily_search = TavilySearch(
    max_results=5,
    topic="general",
)
# TavilySearch reads TAVILY_API_KEY from the environment automatically,
# or you can pass it explicitly: TavilySearch(tavily_api_key="...", ...)

# -----------------------------------------------------------------
# 3. Build the agent
# -----------------------------------------------------------------
agent = create_agent(
    model=llm,
    tools=[tavily_search],
    system_prompt=(
        "You are a helpful research assistant. "
        "Use the tavily_search tool whenever you need current or "
        "factual information you are not sure about."
    ),
)

# -----------------------------------------------------------------
# 4. Run it
# -----------------------------------------------------------------
if __name__ == "__main__":
    question = "What is the most popular sport in the world? Only cite from Wikipedia."
    print(f"The Question we are asking the Agent: {question}")

    result = agent.invoke({
        "messages": [{"role": "user", "content": question}]
    })

    # `result["messages"]` is the full conversation, including any tool calls.
    # The final assistant message is the last one in the list.
    final_message = result["messages"][-1]
    print(final_message.content)