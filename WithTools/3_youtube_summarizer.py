# This code uses the YoutubeVideoSearchTool to read a given Youtube Video
# and create a Analysis report based on that Video
# Note that this code has NOT been tried with the Gemini API yet 
# and could mean some changes for the same. 
# We will try it with the local LLM in our Class and then tune it for Gemini later on

import os
import time
from crewai import Agent, Task, Crew, LLM
from crewai_tools import YoutubeVideoSearchTool

# Add this dummy key to satisfy Pydantic's initial validation check
# 1. Force the global OpenAI SDK to redirect to LM Studio
os.environ["OPENAI_API_KEY"] = "lm-studio"               # Overrides the dummy key error
os.environ["OPENAI_BASE_URL"] = "http://localhost:1234/v1" # Forces ChromaDB to route locally


# 1. Define your Local LLM configuration for the Agent (via LM Studio)
local_llm = LLM(
    model="openai/qwen3.5-9b", # Match your exact loaded LLM name
    base_url="http://localhost:1234/v1",
    api_key="lm-studio" # Dummy key to fulfill validation
)

# 2. Map Nomic Embeddings from LM Studio using the OpenAI compatibility layer
lm_studio_embed_config = {
    "embedder": {
        "provider": "openai", 
        "config": {
            "model": "text-embedding-nomic-embed-text-v1.5", # Matches your exact model
            #"api_base": "http://localhost:1234/v1",         # Redirects queries locally
            #"api_key": "lm-studio"                          # Dummy key
        }
    }
}

# 3. Instantiate the Tool using the custom local embed config
youtube_search_tool = YoutubeVideoSearchTool(
    youtube_video_url="https://www.youtube.com/watch?v=Stc0beAxavY",
    config=lm_studio_embed_config,
)

# 4. Create your Agent and Task
video_analyst = Agent(
    role="Video Content Analyst",
    goal="Extract key insights from video transcripts entirely offline.",
    backstory="You are an expert researcher prioritizing local data execution.",
    llm=local_llm,
    tools=[youtube_search_tool],
    verbose=True
)

analyze_task = Task(
    # Clarify the specific topics the agent should search the video for
    description="Search inside the provided YouTube video for the key aspects of what Clayton Chritensen is " \
    "teaching about the Jobs-To-Be-Done Framework and its application in businesses."
    "Focus on extracting actionable insights and lessons for young innovators from his teachings of JTBD Framework.",
    expected_output="A bulleted list of the Key Topics, Insights, Lessons and Takeaways from the Video",
    agent=video_analyst
)

report_agent = Agent(
    role="Report Writer",
    goal="Compile a comprehensive report based on the insights extracted from the video.",
    backstory="You are a skilled writer who can synthesize information into clear, concise reports.",
    llm=local_llm,
    verbose=True
)

report_task = Task(
    description="Compile a comprehensive report for UG Students learning about" \
    "Entrepreneurship and specifically on Customer Jobs and JTBD to craft out their " \
    "Project's Value Proposition based on the insights extracted from the video.",
    expected_output="A well-structured report that is UG Student friendly that summarizes the key points "
    "and takeaways from the video. Add student friendly examples and illustrations to make this report" \
    "engaging and easy to comprehend for my UG Students.",
    agent=report_agent,
    context=[analyze_task],
    output_file="JTBD_Insights_Report.md",
    markdown=True,
)

crew = Crew(
    agents=[video_analyst, report_agent],
    tasks=[analyze_task, report_task],
)

start_time = time.time()
start_readable = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(start_time))
print(f"\n🚀 [START] Crew execution started at: "f"{start_readable}")

print("\nRunning the JTBD Video Researcher and Report Writer Agents...\n")

result = crew.kickoff()
print("\n")
print("=" * 60)
print("JTBD RESEARCH RESULT from Clayton Christensen's Video")
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
print(f"\nThe Token usage for this execution is: {result.token_usage}")