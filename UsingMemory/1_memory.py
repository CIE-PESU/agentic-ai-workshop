import os
from dotenv import load_dotenv

from crewai import Agent, Task, Crew, Process, LLM

load_dotenv()
MODEL_NAME = os.getenv("MODEL_NAME")
BASE_URL = os.getenv("OPENAI_BASE_URL")
API_KEY = os.getenv("OPENAI_API_KEY")
CREWAI_STORAGE_DIR = os.getenv("CREWAI_STORAGE_DIR")

if not MODEL_NAME or not BASE_URL or not API_KEY:
    raise ValueError("Please ensure MODEL_NAME, OPENAI_BASE_URL, and OPENAI_API_KEY are set in your .env file.")

# Connect to the LLM
llm = LLM(
    model=f"openai/{MODEL_NAME}",
    base_url=BASE_URL,
    api_key=API_KEY,
    temperature=0.2
)
print("Connected to LLM successfully.")

#Define the Agents
#Writer Agent
writer = Agent(
role='Writer',
goal='Write a short complete manuscript for a novel.',
backstory="The writer has experience in short and crsip fiction writing, specializing in " \
"fantasy novels. They craft captivating stories with deep characters.",
verbose=True,
memory=True,
llm=llm
)

#Editor Agent
editor = Agent(
role='Editor',
goal='Review and edit the manuscript to improve writing quality and clarity.',
backstory="The editor has worked with multiple bestselling authors. " \
"They focus on improving the structure, grammar, and pacing of the manuscript.",
verbose=True,
llm=llm
)

#Publisher Agent
publisher = Agent(
role='Publisher',
goal='Manage the publishing and distribution of the book.',
backstory="The publisher ensures that the manuscript is printed and " \
"distributed globally. They manage contracts and marketing.",
verbose=True,
llm=llm
)

#Now define the respective Tasks
#Writer Task
write_manuscript_task = Task(
    description='Write the complete manuscript for a novel.',
    agent=writer,
    expected_output='A short completed manuscript for the novel. ' \
    'Hard Boundary - Ensure that the' \
    'novel is not more than 1000 words and is complete in its story. ',
)

#Editor Task
edit_manuscript_task = Task(
    description='Review and edit the manuscript for grammar, structure, and clarity.',
    agent=editor,
    expected_output='An edited version of the manuscript with improvements.',
    context=[write_manuscript_task]  # Depends on the writer’s manuscript
)

#Publisher Task
publish_book_task = Task(
    description='Oversee the publication and distribution of the book.',
    agent=publisher,
    expected_output='Printed and distributed copies of the book.',
    context=[edit_manuscript_task]  # Depends on the edited manuscript
)

#Assemble your Crew now
publishing_crew = Crew(
    agents=[writer, editor, publisher],
    tasks=[write_manuscript_task, edit_manuscript_task, publish_book_task],
    process=Process.sequential,
    verbose=True
)

result = publishing_crew.kickoff()
print("\n" + "=" * 60)
print("Crew Result")
print("=" * 60)
print(result)