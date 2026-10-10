# PESU CIE --- Agentic AI Workshop: Using Tools with CrewAI

This workshop explores how tools extend AI agents beyond the
capabilities of a language model alone. You will compare web-search
tools, website scraping, and YouTube video retrieval while building
small CrewAI workflows.

> **Workshop environment:** The instructor tested the examples with
> Python **3.12.10** and CrewAI **1.15.21**. As of **10 October 2026**,
> CrewAI **1.15.27** is available. Tool APIs, optional dependencies, and
> provider integrations can change between releases. If your output or
> setup differs from the instructor's, check your installed versions and
> the complete error message before changing the code.

------------------------------------------------------------------------

## 1. Using Tools for AI Agents

An LLM can understand and generate language, reason over the information
provided to it, and produce structured responses. By itself, however, it
does not automatically have access to live websites, private files,
databases, external services, or the ability to execute arbitrary
operations in the world.

A **tool** is a callable capability that an agent can use to perform a
specific operation---for example, search the web, read a file, query a
database, or retrieve content from a website.

In CrewAI, tools can be attached to an agent. The agent can then decide
when a tool is useful, call it with suitable inputs, inspect the
returned result, and use that result in its work. Tool use depends on
the agent's instructions, the task, the LLM's tool-calling behavior, and
the tool's implementation.

### Why are tools necessary?

Tools can extend an agent beyond the information and capabilities
available in its LLM alone:

-   **Access current information:** search for recent announcements,
    research, and news.
-   **Retrieve source material:** fetch text from websites, documents,
    and other sources.
-   **Interact with systems:** query databases or call APIs when
    properly configured and authorized.
-   **Perform specialized operations:** use cloud services,
    machine-learning models, or domain-specific utilities.
-   **Ground answers in evidence:** give an agent source material to
    analyze instead of relying only on its learned knowledge.

Tools do not make every answer correct. Search results may be stale or
incomplete, websites may block scraping, APIs may fail, and an agent may
misinterpret returned content. Validate important findings against their
original sources.

### Examples of tool categories

  -----------------------------------------------------------------------
  Category                Example capability      Typical use
  ----------------------- ----------------------- -----------------------
  File tools              Read or write local     Read a brief, inspect a
                          files                   CSV, or save a report

  Search tools            Search the web or a     Find recent news,
                          search index            research, and relevant
                                                  pages

  Website scraping tools  Extract readable        Read an article after
                          content from a URL      finding it in search

  Database tools          Query a database or     Answer questions about
                          retrieve records        authorized business
                                                  data

  Cloud and API tools     Call cloud services or  Retrieve information or
                          external APIs           trigger an approved
                                                  operation

  Machine-learning tools  Invoke a model or ML    Classify, embed,
                          service                 summarize, or analyze
                                                  data
  -----------------------------------------------------------------------

The exact tools available depend on the installed packages, optional
dependencies, API access, and configuration.

------------------------------------------------------------------------

## 2. Focus: CrewAI Tools

CrewAI provides reusable tools that can be attached to agents. For
example:

-   `SerperDevTool` --- search the web using the Serper service.
-   `ScrapeWebsiteTool` --- retrieve and extract content from a website.
-   `TavilySearchTool` --- search the web using Tavily.
-   `ExaSearchTool` --- search using Exa's search service.
-   `YoutubeVideoSearchTool` --- retrieve/search video content using the
    tool's supported YouTube workflow. This tool is marked
    **experimental**; its behavior and dependencies may change between
    versions.

### Search versus scraping

**Search tools** help discover relevant pages. They typically return
search results such as titles, URLs, snippets, or extracted information,
depending on the provider and configuration.

**Scraping tools** fetch a particular website and attempt to extract its
content. Scraping is not the same as searching: a scraper generally
needs a URL to visit.

A common research workflow is:

1.  Search for relevant and recent pages.
2.  Select promising URLs.
3.  Scrape or retrieve the pages where appropriate.
4.  Ask the research agent to assess relevance, date, evidence, and
    credibility.
5.  Pass the research findings to a report-writing agent.

A search result's date or snippet is not proof that the page itself
contains recent information. Check publication dates and source pages
directly.

### The tools used in this workshop

  --------------------------------------------------------------------------
  Tool                       Role in the exercise    API key or setup
  -------------------------- ----------------------- -----------------------
  `SerperDevTool`            Discover relevant web   Serper API key,
                             pages and news          commonly
                                                     `SERPER_API_KEY`

  `ScrapeWebsiteTool`        Retrieve content from a Usually no separate
                             selected website        search-provider API
                                                     key; access to a site
                                                     can still be restricted

  `TavilySearchTool`         Search for relevant web Tavily API key,
                             content                 commonly
                                                     `TAVILY_API_KEY`; may
                                                     require the
                                                     `tavily-python` package

  `ExaSearchTool`            Search using Exa        Exa API key, commonly
                                                     `EXA_API_KEY`; check
                                                     whether your installed
                                                     CrewAI Tools version
                                                     requires the `exa-py`
                                                     extra

  `YoutubeVideoSearchTool`   Retrieve content        Experimental
                             associated with a       integration;
                             YouTube video           dependencies and
                                                     configuration can vary
                                                     by version
  --------------------------------------------------------------------------

**Important dependency note:** `crewai[tools]` installs CrewAI with its
declared tools extra, but it does not necessarily install every optional
integration used by every tool. The optional dependencies declared by
the version you install are authoritative. If an integration raises
`ModuleNotFoundError` or an import error, inspect the error and install
the specific missing package rather than assuming all integrations are
included.

------------------------------------------------------------------------

## 3. Installation and environment setup

### 3.1 Create a virtual environment

Use a separate virtual environment for the workshop so that dependencies
do not interfere with other Python projects.

**macOS / Linux**

``` bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

**Windows PowerShell**

``` powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Check your Python version:

``` bash
python --version
```

For this workshop, prefer **Python 3.12.x** or **3.13.x**. CrewAI's
supported Python range and compatibility with individual integrations
can change, so consult the release metadata and documentation for your
installed version.

### 3.2 Install CrewAI with tools

``` bash
python -m pip install "crewai[tools]"
```

This installs CrewAI and the dependencies declared for its tools extra.
It does not guarantee that every optional third-party integration is
installed.

For the Tavily exercise, install the additional SDK if it is missing:

``` bash
python -m pip install tavily-python
```

For Exa, some CrewAI Tools releases expose `exa-py` as an optional
integration dependency. If your installation reports that `exa` or
`exa_py` is missing, install:

``` bash
python -m pip install exa-py
```

For `SerperDevTool` and `ScrapeWebsiteTool`, no additional provider SDK
is normally required beyond the compatible CrewAI Tools installation.
`SerperDevTool` still requires a valid Serper API key. If your version
reports a missing dependency, follow the error message and the
documentation for that exact release.

For the experimental YouTube tool, do not assume its dependencies are
stable across versions. Follow the requirements for the installed
release. An alternative is to fetch a video's transcript separately with
`youtube-transcript-api`, then provide that transcript to an agent as
input.

### 3.3 Check installed versions and dependencies

``` bash
python -m pip show crewai crewai-tools
crewai --version
python -m pip check
```

`python --version` reports the Python interpreter version.
`crewai --version` reports the installed CrewAI CLI version when the
command is available; it does **not** tell you the version of every
integration package.

If a tool fails, capture the complete traceback and inspect the
environment:

``` bash
python -m pip show tavily-python exa-py youtube-transcript-api
```

Use the same activated virtual environment to install packages and run
the script.

### 3.4 Configure your `.env` file

Create a `.env` file in the project directory. Add only the keys for
services you actually use.

``` dotenv
# LLM provider — choose the keys needed by your setup
GEMINI_API_KEY=replace_with_your_gemini_key

# Web-search providers
SERPER_API_KEY=replace_with_your_serper_key
TAVILY_API_KEY=replace_with_your_tavily_key
EXA_API_KEY=replace_with_your_exa_key
```

If using LM Studio, configure the local model and base URL in the Python
code or environment variables according to the example provided by your
instructor. A local LM Studio setup may not need a paid LLM API key.

**Security:** Never commit `.env` to GitHub or share API keys in
screenshots. Add `.env` to `.gitignore`:

``` gitignore
.env
.venv/
__pycache__/
```

Some tools or integrations may use different environment-variable names
in different releases. Check the documentation and source code for the
version installed in your environment.

------------------------------------------------------------------------

## 4. LLM options: LM Studio or Gemini

The three exercises can use either:

-   **LM Studio:** run a compatible local model on your computer and
    configure CrewAI to use the local OpenAI-compatible endpoint.
    Performance depends on your computer and the model selected.
-   **Gemini API:** configure CrewAI's LLM integration with your Gemini
    API key. The free tier has usage limits and model availability can
    change; check the current terms and quotas.

Use the LLM configuration supplied with the corresponding code file. Do
not assume that a tool's own provider configuration is automatically
inherited from the LLM configured on an agent.

------------------------------------------------------------------------

## 5. Exercise 1 --- `1_topic_generator.py`

### Objective

Build a two-agent research workflow that identifies important AI and
Agentic AI news from the **seven days preceding the run date**, then
writes a Markdown report.

### What the code does

1.  **Selects an LLM:** use a local model through LM Studio or the
    Gemini API, depending on your setup.
2.  **Initializes `SerperDevTool`:** the research agent can search the
    web through Serper.
3.  **Initializes `ScrapeWebsiteTool`:** the agent can retrieve content
    from relevant websites when given appropriate URLs.
4.  **Creates a Research Agent:** its goal is to find relevant AI and
    Agentic AI news from the last seven days.
5.  **Defines a Research Task:** its instructions and guardrails should
    require recent sources, relevant evidence, publication dates, source
    URLs, and clear handling of uncertain dates.
6.  **Creates a Report Writer Agent and Task:** the report writer uses
    the research task's output as context and writes a structured
    Markdown report to the output file specified in the code.

### What to inspect

-   Observe how the search and scrape objects are initialized.
    Experiment with supported parameters and read their documentation.
-   Follow the verbose agent logs to understand when the search tool is
    called, what it returns, and whether scraping follows.
-   Check whether results actually fall within the seven-day window.
-   Open the original websites and verify their publication dates. A
    search result appearing today does not necessarily mean the
    underlying article was published today.
-   Inspect the generated Markdown report for source URLs, useful
    summaries, duplicate stories, unsupported claims, and clear
    separation between facts and interpretation.
-   If scraping fails, check whether the website blocks automated
    requests or requires JavaScript or authentication.

### Student challenge

Change the research instructions to prioritize one topic, such as AI
agents in education, open-source LLMs, or enterprise agentic workflows.
Compare the results and explain which changes came from the task
instructions versus the tools.

------------------------------------------------------------------------

## 6. Exercise 2 --- `2_topic_generator.py`

### Objective

Compare **Tavily and Exa as alternative search tools** by using them
independently to research AI and Agentic AI news from the last seven
days.

### What the code does

1.  Configures an LLM using LM Studio or Gemini.
2.  Initializes `TavilySearchTool` and `ExaSearchTool`.
3.  Creates a Research Agent and a Research Task with instructions and
    guardrails for recent, relevant, evidence-based news.
4.  Creates a Report Writer Agent and Task that use the research
    findings as context and save a Markdown report.
5.  Runs controlled experiments so that you can inspect the results
    produced by each search tool.

### Important: compare the tools independently

Do not assume that attaching both tools to one agent guarantees a fair
comparison. The agent may choose one tool, use both in a different
order, or combine their outputs.

For a meaningful comparison:

1.  Run a Tavily-only search using the same research question.
2.  Run an Exa-only search using the same research question.
3.  Keep the LLM, task instructions, date window, and other settings as
    consistent as possible.
4.  Compare the returned URLs and source content before comparing the
    final reports.

If your code attaches both tools to the same agent, inspect the verbose
logs to determine which tools were actually invoked.

### What to inspect

-   Observe how `TavilySearchTool` and `ExaSearchTool` are initialized
    and experiment with their supported parameters.
-   Read the verbose logs and trace the execution path.
-   Check whether each tool returns genuinely recent news from the
    seven-day window.
-   Verify the publication date and claims on the original source
    websites.
-   Compare relevance, source diversity, duplication, result
    completeness, useful snippets, date accuracy, and the effort needed
    to verify claims.
-   Compare all three search tools across Exercises 1 and 2: Serper,
    Tavily, and Exa.
-   Record cases where a tool returns a relevant-looking result that is
    too old, lacks a clear date, or links to a page that does not
    support the summary.

### Suggested comparison table

  -----------------------------------------------------------------------
  Criterion         Serper            Tavily            Exa
  ----------------- ----------------- ----------------- -----------------
  Relevant results  Record            Record            Record
                    observations      observations      observations

  Results within    Verify source     Verify source     Verify source
  date window       dates             dates             dates

  Diversity of      Record            Record            Record
  sources           observations      observations      observations

  Useful result     Record            Record            Record
  content           observations      observations      observations

  Duplicate or      Record            Record            Record
  irrelevant        observations      observations      observations
  results                                               

  Ease of verifying Record            Record            Record
  evidence          observations      observations      observations
  -----------------------------------------------------------------------

There is no guaranteed winner for every query. The purpose is to compare
the tools empirically under the same conditions.

------------------------------------------------------------------------

## 7. Exercise 3 --- `3_youtube_summarizer.py`

### Objective

Use `YoutubeVideoSearchTool` to retrieve content associated with a short
YouTube video, summarize it with a research agent, and produce a
Markdown report using a second agent.

### Choose a suitable video

-   Choose a video approximately **5--10 minutes** long.
-   Ensure the video is accessible to your environment.
-   Prefer a video with captions or a transcript.
-   Record the video URL so that you can compare the output with the
    original material.

### What the code does

1.  Configures the LLM using LM Studio or Gemini.
2.  Initializes a `YoutubeVideoSearchTool` object using the
    configuration supported by the installed version.
3.  Creates a simple Video Researcher Agent and Task to retrieve and
    summarize the video content.
4.  Passes the research task's output to a Report Writer Agent through
    task context.
5.  Writes a Markdown report using the output file configured in the
    code.

### What to inspect

-   Observe what the tool actually retrieves. Does it provide transcript
    passages, selected excerpts, metadata, or another representation?
-   Check the verbose logs to see whether the tool was invoked and what
    information was returned.
-   Compare the summary with the original video. Check whether the key
    concepts, examples, and conclusions are represented accurately.
-   Inspect the Markdown report and determine whether it follows the
    task instructions and expected-output requirements.
-   Modify the agent's role, goal, backstory, task description,
    guardrails, and expected output. Run the same video again and
    compare the results.

### Experimental-tool warning

`YoutubeVideoSearchTool` is identified as experimental in the relevant
CrewAI documentation/version. Its behavior, initialization, dependency
requirements, and compatibility may change. An example that works in the
instructor's environment may fail in another environment even when both
users run the same top-level installation command.

If the tool fails, capture the complete traceback and inspect your
CrewAI and CrewAI Tools versions. As an alternative, you can retrieve a
transcript directly with `youtube-transcript-api` and pass the resulting
text into the Research Agent. This alternative is a different
data-retrieval approach: it does not demonstrate the agent invoking a
YouTube tool.

------------------------------------------------------------------------

## 8. Standard instructions for all students

1.  **Use a virtual environment.** Create and activate the workshop
    environment before installing dependencies or running code.
2.  **Use a `.env` file.** Store API keys for the search providers you
    use---Serper, Tavily, and Exa---and for your chosen LLM provider. Do
    not commit secrets to Git.
3.  **Check versions before debugging.** The instructor's tested setup
    is Python 3.12.10 and CrewAI 1.15.21. As of 10 October 2026, CrewAI
    1.15.27 is available. A newer version is not automatically better
    for reproducing a classroom example; the instructor's and student's
    dependency sets may differ.
4.  **Do not rely only on `crewai --version`.** Check both `crewai` and
    `crewai-tools` with `python -m pip show crewai crewai-tools`.
5.  **Prefer Python 3.12.x or 3.13.x for this workshop.** Check the
    supported Python range for the exact CrewAI release and its
    integrations. Other Python versions may work, but compatibility
    should be verified.
6.  **Remember that tool integrations can have optional dependencies.**
    `pip install "crewai[tools]"` installs the dependencies declared for
    that extra; it does not guarantee every third-party integration is
    installed in every release. Tavily may require `tavily-python`; Exa
    may require `exa-py`, depending on the installed version. Follow the
    actual import error and package documentation.
7.  **Do not assume the instructor and student environments are
    identical.** Unpinned installs can resolve different versions at
    different times. Record working versions and use a tested
    requirements file when distributing workshop code.
8.  **Read the full traceback.** Distinguish missing packages, invalid
    API keys, rate limits, network errors, provider errors, tool
    initialization failures, and model errors before changing the code.
9.  **Verify recent claims at their sources.** A prompt asking for news
    from the last seven days is an instruction, not a guarantee. Confirm
    source dates and evidence yourself.
10. **Protect API keys and respect websites.** Follow provider quotas,
    website terms, access controls, and applicable scraping policies.

### Useful troubleshooting commands

``` bash
python --version
crewai --version
python -m pip show crewai crewai-tools
python -m pip check
python -m pip freeze
```

To check a particular integration:

``` bash
python -m pip show tavily-python exa-py youtube-transcript-api
```

If the instructor's code fails in your environment, share the **complete
traceback**, the output of the version commands above, and which script
you were running. Never include API keys in your report.

------------------------------------------------------------------------
## 9. Some Tips and Tricks to avoid running into LM Studio Issues as seen

-   Some students experienced slow responses on Local LM Studio Setups and this could be because of the Model
Sizing and memory consumption.
-   Students are suggested to use a smaller model like Gemma 4 E2B or Gemma 4 E4B or Bonsai 8B.
-   In LM Studio set an initial Context Length of 4K to start with.
-   In the Code that we write, when you define the LLM object add these parameters: max_tokens=512, temperature=0.2, timeout=180, max_retries=2, max_iter=2 or 3.
-   The Instructor given code is using longer Task and Agent Prompts, which can be shortened to avoid Longer or Costlier Input Token Costs.  Instructor will bear this in mind :smile: and advises Students to also try shorter prompts.
-   With Gemini, it is advised to have more than One API Key for Students to use.

------------------------------------------------------------------------
## 10. Final learning outcomes

By completing these exercises, you should be able to:

-   Explain how tools extend an agent's capabilities beyond the LLM
    alone.
-   Distinguish search from website scraping and direct transcript
    retrieval.
-   Configure CrewAI agents with appropriate tools and instructions.
-   Trace tool calls using verbose output.
-   Compare alternative search providers under controlled conditions.
-   Evaluate source recency, relevance, and evidence rather than
    trusting generated reports blindly.
-   Diagnose common dependency and version-compatibility problems.
-   Produce a research report using a sequential, multi-agent CrewAI
    workflow.

**Remember:** the purpose of the workshop is not simply to make the code
run. It is to understand how the agent uses tools, evaluate the quality
of the retrieved evidence, and improve the workflow through deliberate
experimentation.
