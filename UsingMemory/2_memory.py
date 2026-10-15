import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import TavilySearchTool
load_dotenv()

current_filename = Path(__file__).name
MODEL_NAME = os.getenv("MODEL_NAME")
BASE_URL = os.getenv("OPENAI_BASE_URL")
API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not MODEL_NAME or not BASE_URL or not API_KEY or not TAVILY_API_KEY:
    raise ValueError("Ensure MODEL_NAME, OPENAI_BASE_URL, OPENAI_API_KEY, and TAVILY_API_KEY are set in .env")

# 1. Initialize LLM & Tool
llm = LLM(
    model=f"openai/{MODEL_NAME}",
    base_url=BASE_URL,
    api_key=API_KEY,
    temperature=0.0 # Low temp for deterministic tool/memory selection
)

search_tool = TavilySearchTool(max_results=10)

# 2. Define Researcher Agent with Memory and Search Tool
researcher_agent = Agent(
    role="Tech & Science Researcher",
    goal="Answer user queries accurately by first consulting memory, and using live " \
    "web search only when necessary.",
    backstory=(
        "You are an efficient research assistant. You ALWAYS check your memory "
        "first for existing information "
        "before performing a live web search."
    ),
    tools=[search_tool],
    memory=True, # Agent-level memory enabled
    verbose=True,
    llm=llm
)

def run_experiment_step(run_number: int, user_query: str):
    print("\n" + "=" * 70)
    print(f"🧪 RUN #{run_number}: '{user_query}'")
    print("=" * 70)

    research_task = Task(
        description=(
            f"Address this user prompt: '{user_query}'.\n"
            "If you already have enough information in your memory from past runs, "
            "answer directly WITHOUT using the search tool.\n"
            "If the information is missing or incomplete in memory, use the web search tool."
        ),
        expected_output="A concise 5-bullet summary answering the user query.",
        agent=researcher_agent
    )

    # Crew-level memory manages the persistent storage engine
    research_crew = Crew(
        agents=[researcher_agent],
        tasks=[research_task],
        process=Process.sequential,
        memory=True, # Activates LanceDB / Vector Storage
        verbose=True
    )

    start_time = time.time()
    result = research_crew.kickoff()
    
    print(f"\n⏱️ Run #{run_number} Completed in {time.time() - start_time:.2f}s")
    print("\nRESULT:")
    print(result)

# =====================================================================
# INTERACTIVE DEMO CONTROL
# =====================================================================
if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print(f"  python {current_filename} 1  --> Run 1: Initial Search (Populates Memory)")
        print(f"  python {current_filename} 2  --> Run 2: Ask Same Topic (Reads Memory, No Tool)")
        print(f"  python {current_filename} 3  --> Run 3: Ask New Topic (Triggers Tool)")
        sys.exit(0)

    step = sys.argv[1]

    if step == "1":
        # Run 1: First time searching for James Webb Telescope
        run_experiment_step(
            run_number=1, 
            #user_query="Search and summarize 5 recent discoveries made by the " \
            #"James Webb Space Telescope in the year 2026."
            user_query="The legend of the singer and performer - kishore kumar and his " \
            "contributions to the world of Indian Cinema and Music."
        )
    elif step == "2":
        # Run 2: Same topic -> Should pull from LanceDB memory without executing Tavily
        run_experiment_step(
            run_number=2, 
            #user_query="From among those information about James Webb Space Telescope we found "
            #"showcase 2 such discoveries"
            user_query="Would you have information on how many times did Kishore kumar win the filmfare award?"
        )
    elif step == "3":
        # Run 3: New topic -> Memory miss -> Should execute Tavily again
        run_experiment_step(
            run_number=3, 
            user_query="What are the recent major breakthroughs in Quantum Computing?"
        )