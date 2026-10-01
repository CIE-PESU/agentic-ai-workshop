#####
# This code is the first basic agent using CrewAI.
# Created to demonstrate the basic functionality of what an AI Agent can do.
# This uses CrewAI as we at PESU CIE - Agentic AI workshop are using this framework to start with
# The instructions to run this in your local environment is below.
# This code assumes that you are using LMStudio with Qwen 3.5 9b.
# If you use any other model, say Bonsai 8B or Mistral or Gemma4 E2B etc, add that in the env file.
# Students are expected to run this as-is OR do their own tweaks and get it to work on their systems.
#####
#python -m venv .venv
#source .venv/bin/activate
#python -m pip install -U pip
#pip install crewai

import os
import time
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM


# --------------------------------------------------
# 1. Load configuration
# --------------------------------------------------

load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME")
BASE_URL = os.getenv("OPENAI_BASE_URL")
API_KEY = os.getenv("OPENAI_API_KEY")
print(f"Using model: {MODEL_NAME}")
print(f"Using base URL: {BASE_URL}")


# --------------------------------------------------
# 2. Connect CrewAI to local Qwen model
# --------------------------------------------------

llm = LLM(
    model=f"openai/{MODEL_NAME}",
    base_url=BASE_URL,
    api_key=API_KEY,
    temperature=0.2
)

print("Connected to LLM successfully.")

# --------------------------------------------------
# 3. Define the Agent
# --------------------------------------------------
# Define the Agent's Role, Its Goal (what must it achieve) and 
# a Backstory (to give it context and personality)
research_agent = Agent(

    role="Research Analyst",

    goal=(
        "Research a given topic and produce a clear, "
        "accurate and concise explanation."
    ),

    backstory=(
        "You are a careful research analyst who specializes "
        "in explaining technology and business topics. "
        "You simplify complex ideas without losing technical accuracy."
    ),

    llm=llm,

    verbose=True
)


# --------------------------------------------------
# 4. Define the Task
# --------------------------------------------------
# This Task definition is the heart of the activity that we will ask the Agent to perform.
# We give it a description of what we want it to achieve.
# We define the expected output that we want to receive from the Agent.
# Finally, we assign the Agent that will perform the Task.
research_task = Task(

    description=(
        "Research the topic: {topic}\n\n"

        "Provide a beginner-friendly but technically accurate "
        "research brief.\n\n"

        "Cover:\n"
        "1. What the topic is\n"
        "2. Why it is important\n"
        "3. How it works at a high level\n"
        "4. One practical example\n"
        "5. Three key takeaways\n\n"

        "Do not make the explanation unnecessarily long."
    ),

    expected_output=(
        "A concise research brief containing:\n"
        "- What is it?\n"
        "- Why does it matter?\n"
        "- How does it work?\n"
        "- Practical Example\n"
        "- Key Takeaways"
    ),

    agent=research_agent
)


# --------------------------------------------------
# 5. Create the Crew
# --------------------------------------------------

# We then create the Crew of Agents (in this case just one Agent)
# We assign the Task (in this case just one Task)
# We are intentionally setting verbose=True so that we can see the inner workings 
# of the Crew as it executes the Task.
crew = Crew(
    agents=[research_agent],
    tasks=[research_task],
    verbose=True
)


# --------------------------------------------------
# 6. Get user input
# --------------------------------------------------

topic = input(
    "\nWhat would you like the research agent to investigate? "
)


# --------------------------------------------------
# 7. Run the Crew
# --------------------------------------------------
# Now we ask the Crew of Agents to Run and perform the Task that we have defined.
start_time = time.time()
start_readable = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))
print(f"\n🚀 [START] Crew execution started at: {start_readable}")

result = crew.kickoff(
    inputs={
        "topic": topic
    }
)


# --------------------------------------------------
# 8. Display result
# --------------------------------------------------

print("\n")
print("=" * 60)
print("RESEARCH RESULT")
print("=" * 60)
print(result)

# Capture and print the end time
end_time = time.time()
end_readable = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time))
print(f"🏁 [END] Crew execution finished at: {end_readable}")

# Calculate total elapsed duration
elapsed_seconds = end_time - start_time
print(f"⏱️ [TOTAL TIME TAKEN]: {elapsed_seconds:.2f} seconds for Model: {MODEL_NAME}\n")
print(result.tasks_output)
