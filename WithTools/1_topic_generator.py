# In this code we will explore how to use Tools with CrewAI Agents.
# Before we access the Tools, Run this command to install the required libraries
# pip install 'crewai[tools]'

# This code will use 1 Tool - To bring to us 3 Latest Topics that are happening
# in the world of AI and Agentic AI this week.

import os
import time

from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

load_dotenv()

#Load the environment variables from the .env file
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")
BASE_URL = os.getenv("OPENAI_BASE_URL")
API_KEY = os.getenv("OPENAI_API_KEY")

print(f"Using model : {MODEL_NAME}")
print(f"Using base URL : {BASE_URL}")

# Create the Search Tool using Serper
search_tool = SerperDevTool(max_usage_count=5, n_results=5)
scrape_tool = ScrapeWebsiteTool()

# For those using Gemini as the LLM use this code snippet below
# and remember - No base_url parameter to be given
# and you will not use the Local LLM part and you can safely delete the Local LLM definition below
GEMINI_MODEL_NAME = "gemini/gemini-3.5-flash-lite"
llm = LLM(
    model=GEMINI_MODEL_NAME,
    api_key=API_KEY,
    temperature=0.2
)

# Connect to the Local LLM
# Note:If you are using the Gemini LLM, You can safely delete the Local LLM definition below
llm = LLM(
    model=f"openai/{MODEL_NAME}",
    base_url=BASE_URL,
    api_key=API_KEY,
    temperature=0.2
)
print("Connected to LLM successfully.")

# Research Agent
research_agent = Agent(
    role = "AI News Researcher",
    goal = ("Research the latest topics and news trends from the world " \
    "of AI and Agentic AI in the last 7 days. You will use the SerperDevTool and ScrapeWebsiteTool"
    " to find "
    "the latest news and topics. You will provide a " \
    "summary of the findings."
    "You will not be looking for news or topics older than 7 days."),
    backstory = ("You are an AI News Researcher, your job is to research the latest " \
    "topics and news trends from the world of AI and Agentic AI this week or the last 7 days. "),
    llm = llm,
    verbose=True,
    allow_delegation=False,
    tools = [search_tool, scrape_tool],
)

#The Report writer Agent definition
report_writer_agent = Agent(
    role="Technical Report Writer",
    goal=(
        "Transform the research findings provided to you "
        "into a clear, logically structured and readable "
        "Markdown report."
    ),
    backstory=(
        "You are an experienced technical writer. "
        "You specialize in converting research findings and latest news"
        "into well-organized reports for students and "
        "professional readers. "
        "You do not perform new research. "
        "You work primarily with the research provided "
        "by the AI News Researcher."
    ),
    llm=llm,
    verbose=True,
    allow_delegation=False
)

#Create the Research task
research_task = Task(
        name="Research Latest AI Topics",
        description=(
        "Research the latest topics and news trends from the world "
        "of AI and Agentic AI ONLY from the Last 7 Days. Use the SerperDevTool to find "
        "the latest news and topics. "
        "You will look for Latest News as on THIS week or the Last 7 Days and " \
        "will actively discard any news or topics on AI and Agentic AI that are older."
        "You will provide a summary of the findings clearly indicating:" \
        "1. What is the News or Trend or Headline about the topic." \
        "2. What is the significance of this news or trend." \
        "3. What are the key points or takeaways from this news or trend." \
        "4. Provide a link to the source of the news or trend."
        "5. Provide the Date of the News or Trend Publication."
        "Do not focus on WRITING the final report but focus on providing a " \
        "summary of the findings. "
        

    ),
    agent=research_agent,
    expected_output=(
        "A Crisp Summary of the Top 3 Latest Topics, News and Trends:" \
        "Prepare a Brief for the next agent to write a report."
        "You will capture the Headlines, Significance, Key Points and Source "
        "Links for each of the 3 topics."
    )
)

#Create the Report Writing task
report_task = Task(
    name="Write Report",
    description=(
        "Transform the research findings provided to you "
        "into a clear, logically structured and readable "
        "Markdown report."
    ),
    agent=report_writer_agent,
    context=[research_task],
    expected_output=(
        "A well-structured Markdown report based on the research findings."
        "Capture the following clearly in the report:"
        "1. Introduction to the topic and its significance."
        "2. Detailed explanation of the topic and its implications."
        "3. Key takeaways and insights from the research."
        "4. Conclusion summarizing the findings and their relevance."
        "5. Include any relevant references or sources used in the research."
        "6. Mention the Date of the News or Trend Publication for each topic."
    ),
    output_file="AI_Trends_Report.md",
    markdown=True
)

crew = Crew(
    agents = [research_agent, report_writer_agent],
    tasks = [research_task, report_task],
    process = Process.sequential,
    verbose=True
)

start_time = time.time()
start_readable = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(start_time))
print(f"\n🚀 [START] Crew execution started at: "f"{start_readable}")

print("\nRunning the two-agent crew...\n")

result = crew.kickoff()
print("\n")
print("=" * 60)
print("RESEARCH RESULT")
print("=" * 60)
print(result)

# EXECUTION SUMMARY
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
print("\n📄 Final report saved as: AI_Trends_Report.md")
print(f"\nThe Token usage for this execution is: {result.token_usage}")