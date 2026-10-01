#####
# CrewAI Example 2
#
# TWO AGENTS + TWO TASKS + SEQUENTIAL EXECUTION
#
# Agent 1: Researcher
#   -> Task 1: Research the topic
#
# Agent 2: Report Writer
#   -> Task 2: Convert the research into a report
#
# The output of Task 1 becomes the CONTEXT for Task 2.
#
# This demonstrates how multiple specialized agents
# can collaborate inside a CrewAI Crew.
#####

import os
import time

from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM


# --------------------------------------------------
# 1. Load configuration
# --------------------------------------------------

load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME")
BASE_URL = os.getenv("OPENAI_BASE_URL")
API_KEY = os.getenv("OPENAI_API_KEY")

print(f"Using model : {MODEL_NAME}")
print(f"Using base URL : {BASE_URL}")


# --------------------------------------------------
# 2. Connect CrewAI to the LLM
# --------------------------------------------------

llm = LLM(
    model=f"openai/{MODEL_NAME}",
    base_url=BASE_URL,
    api_key=API_KEY,
    temperature=0.2
)

print("Connected to LLM successfully.")


# ==================================================
# 3. AGENT 1 — RESEARCHER
# ==================================================

research_agent = Agent(

    role="Research Analyst",

    goal=(
        "Research the given topic and produce a clear, "
        "well-structured and factually grounded research brief "
        "that another agent can use to write a report."
    ),

    backstory=(
        "You are an experienced research analyst. "
        "Your job is to investigate a topic, identify the "
        "important concepts, organize the findings logically, "
        "and separate important facts from unnecessary detail. "
        "You do NOT write the final report."
    ),

    llm=llm,

    verbose=True,

    # We want this agent to concentrate only on its own task.
    #We do not want the agent to be able to delegate tasks to other agents as of now
    #since we are defining their bounded scope well.
    #Delegation will be set to True for Agents who function as Managerial Agents :)
    #An Irony that even the Tech world thinks that Managers only Delegate - I am a joking
    allow_delegation=False
)


# ==================================================
# 4. AGENT 2 — REPORT WRITER
# ==================================================

report_writer_agent = Agent(

    role="Technical Report Writer",

    goal=(
        "Transform the research findings provided to you "
        "into a clear, logically structured and readable "
        "Markdown report."
    ),

    backstory=(
        "You are an experienced technical writer. "
        "You specialize in converting research findings "
        "into well-organized reports for students and "
        "professional readers. "
        "You do not perform new research. "
        "You work primarily with the research provided "
        "by the Research Analyst."
    ),

    llm=llm,

    verbose=True,

    # Keep the demonstration simple:
    # this agent writes rather than delegating work.
    allow_delegation=False
)


# ==================================================
# 5. TASK 1 — RESEARCH
# ==================================================

research_task = Task(

    name="research_task",

    description=(
        "Research the following topic:\n\n"
        "{topic}\n\n"

        "Prepare a research brief for another AI agent "
        "who will later write the final report.\n\n"

        "The research brief should cover:\n"

        "1. What the topic is\n"
        "2. Important concepts and terminology\n"
        "3. Why the topic is important\n"
        "4. How it works at a high level\n"
        "5. Important examples or applications\n"
        "6. Key facts or insights\n"
        "7. Key takeaways\n\n"

        "Do NOT write the final report.\n"
        "Focus on producing useful research findings "
        "that another agent can use."
    ),

    expected_output=(
        "A structured research brief containing "
        "the important findings, concepts, explanations, "
        "examples and key takeaways about the topic. "
        "The output should be suitable as input to a "
        "separate report-writing agent."
    ),

    agent=research_agent
)


# ==================================================
# 6. TASK 2 — WRITE THE REPORT
# ==================================================

report_task = Task(

    name="report_task",

    description=(
        "Using the research findings produced by the "
        "Research Analyst, write the final report about:\n\n"
        "{topic}\n\n"

        "The report should be written for a student audience "
        "and should be clear, logically structured and easy "
        "to understand.\n\n"

        "Structure the report using these sections:\n"

        "# {topic}\n\n"

        "## What is it?\n"
        "Explain the topic clearly.\n\n"

        "## Why does it matter?\n"
        "Explain its importance and relevance.\n\n"

        "## How does it work?\n"
        "Explain the basic mechanism or process.\n\n"

        "## Practical Examples\n"
        "Give relevant examples or applications.\n\n"

        "## Key Takeaways\n"
        "Summarize the most important points.\n\n"

        "Use ONLY the research findings provided by the "
        "Research Analyst as the primary source for the report.\n\n"

        "Do not describe the research process itself. "
        "Produce the final report."
    ),

    expected_output=(
        "A polished Markdown report containing:\n"
        "- A title\n"
        "- What is it?\n"
        "- Why does it matter?\n"
        "- How does it work?\n"
        "- Practical Examples\n"
        "- Key Takeaways\n\n"
        "The report should be clear, coherent and "
        "suitable for a student to read."
    ),

    agent=report_writer_agent,

    # ------------------------------------------------
    # IMPORTANT:
    #
    # Give Task 2 the output of Task 1 as context.
    # ------------------------------------------------
    context=[research_task],

    # CrewAI writes the final task output to this file.
    output_file="final_report.md",

    # Ask CrewAI to format the output as Markdown.
    markdown=True
)


# ==================================================
# 7. CREATE THE CREW
# ==================================================

crew = Crew(

    agents=[
        research_agent,report_writer_agent
    ],

    tasks=[
        research_task,report_task
    ],

    # ------------------------------------------------
    # IMPORTANT:
    #
    # Tasks execute in the order in which they appear.
    # ------------------------------------------------
    process=Process.sequential,

    verbose=True
)


# ==================================================
# 8. GET USER INPUT
# ==================================================

topic = input(
    "\nWhat would you like the two-agent crew to investigate? "
)


# ==================================================
# 9. RUN THE CREW
# ==================================================

start_time = time.time()

start_readable = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(start_time))

print(f"\n🚀 [START] Crew execution started at: "f"{start_readable}")

print("\nRunning the two-agent crew...\n")

result = crew.kickoff(inputs={"topic": topic})


# ==================================================
# 10. DISPLAY THE RESEARCH RESULT
# ==================================================

print("\n")
print("=" * 70)
print("TASK 1 — RESEARCH RESULT")
print("=" * 70)


# ==================================================
# 11. DISPLAY THE FINAL REPORT
# ==================================================

print("\n")
print("=" * 70)
print("TASK 2 — FINAL REPORT")
print("=" * 70)
print(result.tasks_output)


# ==================================================
# 12. EXECUTION SUMMARY
# ==================================================

end_time = time.time()

end_readable = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(end_time))

elapsed_seconds = end_time - start_time

print("\n")
print("=" * 70)
print("EXECUTION SUMMARY")
print("=" * 70)

print(f"🏁 Finished at : {end_readable}")
print(f"⏱️ Total time  : {elapsed_seconds:.2f} seconds")
print(f"🤖 Model       : {MODEL_NAME}")
print("\n📄 Final report saved as: final_report.md")
print(f"\nThe Token usage for this execution is: {result.token_usage}")