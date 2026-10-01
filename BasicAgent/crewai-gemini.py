# crewai_gemini_agent.py
#Before running this code ensure you have a Virtual Env set and you have run this below 
# pip install crewai command
#pip install crewai

import os
import time
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM


# --------------------------------------------------
# 1. Load configuration
# --------------------------------------------------
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY was not found in .env")

MODEL_NAME = "gemini/gemini-2.5-flash-lite"
print(f"Using model: {MODEL_NAME}")


# --------------------------------------------------
# 2. Connect CrewAI to Gemini
# --------------------------------------------------

llm = LLM(
    model=MODEL_NAME,
    api_key=API_KEY,
    temperature=0.2
)

print("CrewAI connected to Gemini.")


# --------------------------------------------------
# 3. Define the Agent
# --------------------------------------------------

research_agent = Agent(

    role="Research Analyst", #What Role does this Agent Play

    #What are we trying to achieve with this Agent goes into the Goal
    goal=(
        "Research a given topic and produce a clear, "
        "accurate and concise explanation."
    ),

    #We give it a persona, a backstory for it to understand the Goal better 
    #and use this persona when actually understanding and executing the Task
    backstory=(
        "You are a careful research analyst who specializes "
        "in explaining technology and business topics. "
        "You simplify complex ideas without losing technical accuracy."
    ),
    
    #We give it the LLM Object that it needs to perform its Tasks    
    llm=llm,
    #We enable Verbosity to understand the flow of this Agent.
    #In non-test environments, Turn this off by setting it to False
    verbose=True
)


# --------------------------------------------------
# 4. Define the Task
# --------------------------------------------------

research_task = Task(

    #The Task description should be crisp and clear. 
    description=(
        "Research the topic: {topic}\n\n"

        "Provide a beginner-friendly explanation.\n\n"

        "Cover:\n"
        "1. What the topic is\n"
        "2. Why it is important\n"
        "3. One practical example\n"
        "4. Three key takeaways\n\n"

        "Keep the explanation concise."
    ),

    #We define the Output that we need it to emit
    #As of now we shall start with Textual outputs and then move on to Structured outputs
    expected_output=(
        "A concise research brief containing:\n"
        "- What is it?\n"
        "- Why does it matter?\n"
        "- Practical Example\n"
        "- Key Takeaways"
    ),

    #The Agent and the Task are Linked here.  
    agent=research_agent
)


# --------------------------------------------------
# 5. Create the Crew
# --------------------------------------------------

#We create a simple Crew of Agents but this dude is going SOLO
#We attach the Agent and the Task Object and note the [] notation for us to be able to 
#add more than one Agent and Task to the Crew.  Very much possible
#We set the Verbosity to True but in non-Test environments set it to False. 
crew = Crew(
    agents=[research_agent],
    tasks=[research_task],
    verbose=True
)


# --------------------------------------------------
# 6. Get user input
# --------------------------------------------------
#We are accepting an input here.
#Note that we would want you to give a fairly descriptive inputs and not just one word
#Note that LLMs and Agents are NOT to be treated like Google Search - Right?
topic = input(
    "\nWhat would you like the research agent to investigate? "
)


# --------------------------------------------------
# 7. Run the Crew
# --------------------------------------------------

print("\nRunning the agent...\n")
#We kickoff the Crew.  This is a Synchronous Execution which means we wait for it to run and finish
start_time = time.time()
start_readable = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))
print(f"\n🚀 [START] Crew execution started at: {start_readable}")

result = crew.kickoff(
    inputs={
        "topic": topic #We are giving it the topic that we asked as user input
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
