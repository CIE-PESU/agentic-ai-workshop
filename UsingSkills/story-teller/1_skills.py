import os
from pathlib import Path
import time
from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task, LLM
from crewai.skills import activate_skill, discover_skills

load_dotenv()
MODEL_NAME = os.getenv("MODEL_NAME")
BASE_URL = os.getenv("OPENAI_BASE_URL")
API_KEY = os.getenv("OPENAI_API_KEY")

if not MODEL_NAME:
    raise ValueError("MODEL_NAME environment variable is not set. Please set it in the .env file.")
if not BASE_URL:
    raise ValueError("OPENAI_BASE_URL environment variable is not set. Please set it in the .env file.")
if not API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it in the .env file.")

BASE_DIR = Path(__file__).resolve().parent
SKILLS_DIR = BASE_DIR / "skills"

print(f"Using model : {MODEL_NAME}")
print(f"Using base URL : {BASE_URL}")

#Check if Skills folder exists and raise an error if it does not
if not SKILLS_DIR.exists():
    raise FileNotFoundError(f"CrewAI skills directory not found at: "f"{SKILLS_DIR}")

#If Skills Exist, then use the discover_skills function to find or discover all the skills available
discovered = discover_skills(SKILLS_DIR)

#If we are unable to discover or find any skills, then raise an error
if not discovered:
    raise RuntimeError(
        f"No CrewAI skills discovered under: " 
        f"{SKILLS_DIR}\nExpected structures such as:\n skills/agentic-ai-storyteller/SKILL.md\n")

#Print the details of the Discovered Skills and then Activate them
print("\nDiscovered CrewAI skills:")
for skill in discovered:
    print(f"  - {skill}")
    activated = [
        activate_skill(skill) #This call will activate any Skill that has been discovered or found
        for skill in discovered
    ]
print(f"\nActivated {len(activated)} CrewAI skill(s).\n")

# Connect to the LLM
llm = LLM(
    model=f"openai/{MODEL_NAME}",
    base_url=BASE_URL,
    api_key=API_KEY,
    temperature=0.2
)
print("Connected to LLM successfully.")

#We will define an output file to store the generated story
output_file = "Agentic-AI-Story.md"

#Define our Storyteller Agent with a role, goal and backstory.  
storyteller_agent = Agent(
    role="Futuristic Speculative Fiction Author",
    goal="Write gripping, short-form science fiction or futuristic stories " \
    "featuring autonomous Agentic AI systems.",
    backstory=(
        "You are an award-winning speculative fiction writer who specializes in techno-thrillers. "
        "You understand complex computer architectures, agentic loops, and multi-step reasoning. "
        "Your writing style is sharp, atmospheric, and highly engaging. You strictly follow safety "
        "guardrails for student audiences and pride yourself on masterful, unexpected plot twists."
    ),
    verbose=True,
    allow_delegation=False,
    llm=llm,
    #skills=activated, #One way of loading all the skills
    skills=["./skills"] #Another Easier way to Load the skills.
    # tools=[TavilySearchResults()] # We will use this in the later phases
)

#Define the Storytelling Task with a description, expected output and the agent.
storytelling_task = Task(
    description=(
        "Craft a compelling short story based on the theme given to you by the user: {ai_context}\n"
        "The story must use the activated skills to understand and create the narrative:\n"
        "1. Create a unique title for the story based on the Theme provided by the user"
        "2. Weave the story based on the Theme provided by the user\n"
        "3. Create something that is interesting but not too deeply complex.\n"
        "4. Add elements of Humor but ensure that the Theme is well covered with examples.\n"
    ),
    expected_output=(
        "A complete fictional short story with a unique title. "
        "Strictly under 500 words. "
        "Contains absolutely NO profanity, vulgarity or explicit language. "
        "Includes only the title and the story text, with zero introductory or explanatory text."
        "It sticks to the provided theme and is suitable for a classroom setting."
    ),
    agent=storyteller_agent,
)

crew = Crew(
    agents=[storyteller_agent],
    tasks=[storytelling_task],
    verbose=True
)

#Collect the AI Context on which we will ask the Agent to Write a Story
ai_context = input(
    "\nGive me an AI topic on which to write a Story (ex: AI in Healthcare, " \
    "Transportation, Entertainment etc). Be Clear and Specific: "
)

print("\nRunning the agent...\n")
#We kickoff the Crew.  This is a Synchronous Execution which means we wait for it to run and finish
start_time = time.time()
start_readable = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))
print(f"\n🚀 [START] Crew execution started at: {start_readable}")

result = crew.kickoff(
    inputs={
        "ai_context": ai_context #We are giving it the AI topic that we asked as user input
    }
)

#Display the Results
print("\n")
print("=" * 60)
print("STORY RESULT")
print("=" * 60)
print(result)
# Capture and print the end time
end_time = time.time()
end_readable = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time))
print(f"🏁 [END] Story Writing Crew execution finished at: {end_readable}")

# Calculate total elapsed duration
elapsed_seconds = end_time - start_time
print(f"⏱️ [TOTAL TIME TAKEN]: {elapsed_seconds:.2f} seconds for Model: {MODEL_NAME}\n")