
import os
import time
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
from crewai_tools import YoutubeVideoSearchTool

# --------------------------------------------------
# 1. Load Gemini API key
# --------------------------------------------------
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is missing. Add it to your .env file."
    )

# Some Google-provider integrations expect GOOGLE_API_KEY.
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY

# --------------------------------------------------
# 2. Configure Gemini Flash-Lite
# --------------------------------------------------
gemini_llm = LLM(
    model="gemini/gemini-3.5-flash-lite",
    api_key=GEMINI_API_KEY,
)

# --------------------------------------------------
# 3. Configure YouTube retrieval and embeddings
# --------------------------------------------------
youtube_config = {
    "llm": {
        "provider": "google",
        "config": {
            "model": "gemini-3.5-flash-lite",
            "api_key": GEMINI_API_KEY,
        },
    },
    "embedder": {
        "provider": "google",
        "config": {
            "model": "models/gemini-embedding-001",
            "task_type": "retrieval_document",
            "api_key": GEMINI_API_KEY,
        },
    },
}

YOUTUBE_URL = "https://www.youtube.com/watch?v=Stc0beAxavY"

youtube_search_tool = YoutubeVideoSearchTool(
    youtube_video_url=YOUTUBE_URL,
    config=youtube_config,
)

# --------------------------------------------------
# 4. Agent 1: Video Researcher
# --------------------------------------------------
video_analyst = Agent(
    role="Video Content Analyst",
    goal=(
        "Extract accurate, relevant insights from the video "
        "about Clayton Christensen's Jobs-To-Be-Done framework."
    ),
    backstory=(
        "You are an entrepreneurship researcher who explains "
        "customer jobs, functional and emotional needs, and "
        "the circumstances that cause customers to seek solutions."
    ),
    llm=gemini_llm,
    tools=[youtube_search_tool],
    verbose=True,
)

analyze_task = Task(
    description=(
        "Research the provided YouTube video and identify the key "
        "ideas Clayton Christensen teaches about the Jobs-To-Be-Done "
        "framework and its application in business.\n\n"
        "Focus on:\n"
        "1. What a customer job means.\n"
        "2. Why customers 'hire' products or services.\n"
        "3. The circumstances and motivations behind customer choices.\n"
        "4. Examples or stories actually supported by the video.\n"
        "5. Lessons for young innovators and entrepreneurs.\n\n"
        "Use the YouTube search tool to retrieve relevant video content. "
        "Distinguish statements supported by retrieved content from "
        "interpretations. Do not invent quotations or video examples."
    ),
    expected_output=(
        "A structured research summary with key concepts, supporting "
        "video evidence, business implications, and lessons for students."
    ),
    agent=video_analyst,
)

# --------------------------------------------------
# 5. Agent 2: Student Report Writer
# --------------------------------------------------
report_agent = Agent(
    role="Entrepreneurship Report Writer",
    goal=(
        "Convert the research findings into a clear and useful "
        "learning report for undergraduate students."
    ),
    backstory=(
        "You teach entrepreneurship concepts through simple language, "
        "familiar examples, and practical applications."
    ),
    llm=gemini_llm,
    verbose=True,
)

report_task = Task(
    description=(
        "Using the research findings from the previous task, prepare "
        "a student-friendly report on Jobs-To-Be-Done (JTBD).\n\n"
        "Include:\n"
        "1. A simple definition of JTBD.\n"
        "2. The main insights from the video.\n"
        "3. Examples that help students understand customer jobs.\n"
        "4. How JTBD helps entrepreneurs discover customer needs.\n"
        "5. How JTBD connects to the Value Proposition Canvas.\n"
        "6. Three questions students can ask while researching "
        "their own customer segments.\n\n"
        "Clearly label any illustrative examples you create yourself. "
        "Do not present them as examples from the video unless "
        "supported by the research findings."
    ),
    expected_output=(
        "A well-structured Markdown report for undergraduate "
        "entrepreneurship students, with headings, concise explanations, "
        "illustrative examples, and practical takeaways."
    ),
    agent=report_agent,
    context=[analyze_task],
    output_file="JTBD_Insights_Report.md",
)

# --------------------------------------------------
# 6. Create the sequential Crew
# --------------------------------------------------
crew = Crew(
    agents=[video_analyst, report_agent],
    tasks=[analyze_task, report_task],
    verbose=True,
)

# --------------------------------------------------
# 7. Execute and report timing
# --------------------------------------------------
start_time = time.time()

print("\n" + "=" * 60)
print("Starting JTBD Research with Gemini Flash-Lite")
print("=" * 60)

try:
    result = crew.kickoff()

    print("\n" + "=" * 60)
    print("JTBD RESEARCH RESULT")
    print("=" * 60)
    print(result)

    print("\nReport saved as JTBD_Insights_Report.md")

    if hasattr(result, "token_usage"):
        print("\nToken usage:")
        print(result.token_usage)

except Exception as exc:
    print(f"\nExecution failed: {type(exc).__name__}: {exc}")
    raise

finally:
    elapsed = time.time() - start_time
    print(f"\nTotal execution time: {elapsed:.2f} seconds")
