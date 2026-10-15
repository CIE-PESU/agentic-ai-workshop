import os
from pathlib import Path
import time
from dotenv import load_dotenv
from crewai import Agent, Crew, Task, LLM

load_dotenv()
MODEL_NAME = os.getenv("MODEL_NAME")
BASE_URL = os.getenv("OPENAI_BASE_URL")
API_KEY = os.getenv("OPENAI_API_KEY")

if not MODEL_NAME or not BASE_URL or not API_KEY:
    raise ValueError("Please ensure MODEL_NAME, OPENAI_BASE_URL, and OPENAI_API_KEY are set in your .env file.")

BASE_DIR = Path(__file__).resolve().parent
print(f"BASE Directory is {BASE_DIR}")
SKILLS_DIR = BASE_DIR / "skills"
print(f"SKILLS Directory is {SKILLS_DIR}")

if not SKILLS_DIR.exists():
    raise FileNotFoundError(f"CrewAI skills directory not found at: {SKILLS_DIR}")

print(f"Using model : {MODEL_NAME}")
print(f"Using base URL : {BASE_URL}")

# Connect to the LLM
llm = LLM(
    model=f"openai/{MODEL_NAME}",
    base_url=BASE_URL,
    api_key=API_KEY,
    temperature=0.2
)
print("Connected to LLM successfully.")

output_file = "Napkin-Pitch.md"

# Define Napkin Pitch Agent
napkin_pitch_agent = Agent(
    role="Napkin Pitch Generator Agent",
    goal="Distill student ideas into structured 4-quadrant Napkin Pitches using loaded skills.",
    backstory=(
        "You are an expert startup mentor who takes raw, unstructured project ideas from students "
        "and organizes them into clean, concise Napkin Pitches. You rigorously adhere to skill "
        "instructions regarding structure, word counts, and avoiding hallucinations."
    ),
    verbose=True,
    allow_delegation=False,
    llm=llm,
    skills=["./skills"]  # Automatically loads skills from directory
)

# Define Napkin Pitch Task
napkin_pitch_task = Task(
    description=(
        "Analyze the following student concept input: '{raw_student_input}'.\n"
        "Follow the active 'napkin-pitch-architect' skill guidelines precisely to structure, "
        "categorize, and output the final Napkin Pitch template."
    ),
    expected_output=(
        "A Markdown file containing the exact Napkin Pitch template specified in the napkin-pitch-architect skill, "
        "with no additional conversational filler."
    ),
    agent=napkin_pitch_agent,
    output_file=output_file,
    markdown=True,
)

crew = Crew(
    agents=[napkin_pitch_agent],
    tasks=[napkin_pitch_task],
    verbose=True
)

# Collect Single Input from Student
print("\n--- Welcome to the Napkin Pitch Generator ---")
raw_idea = input("Describe your project idea (include any details on users, execution, or uniqueness if you have them): ")

print("\nRunning the agent...\n")
start_time = time.time()
start_readable = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))
print(f"🚀 [START] Crew execution started at: {start_readable}")

result = crew.kickoff(
    inputs={
        "raw_student_input": raw_idea
    }
)

print("\n" + "=" * 60)
print("PITCH RESULT")
print("=" * 60)
print(result)

end_time = time.time()
end_readable = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time))
print(f"🏁 [END] Execution finished at: {end_readable}")
print(f"⏱️ [TOTAL TIME TAKEN]: {end_time - start_time:.2f} seconds\n")