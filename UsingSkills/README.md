# Using Skills — PESU CIE Agentic AI Workshop

This folder contains two hands-on examples showing how **Agent Skills** can guide a CrewAI agent to perform a task consistently.

An agent can be given a role, goal, and task in Python. A **Skill** adds reusable instructions and a workflow for doing that task well.

## Learning objectives

By working through these examples, you will learn how to:

- Understand the difference between an agent's Python configuration and a reusable `SKILL.md`.
- Organize skills in a folder that CrewAI can discover or load.
- Use a storytelling skill to guide creative output.
- Use a pitch-architect skill to turn a rough startup idea into a structured Napkin Pitch.
- Configure a local OpenAI-compatible model through LM Studio, or use the Gemini API for the pitch-generator example.

## Folder structure

```text
UsingSkills/
├── README.md
├── story-teller/
│   ├── 1_skills.py
│   └── skills/
│       └── agentic-ai-storyteller/
│           └── SKILL.md
└── pitch-creator/
    ├── 2_skills.py
    ├── 3_skill_validation.py
    ├── 3_gemini_skill_validation.py
    ├── preflight_with_jev.py
    ├── Napkin-Pitch.md
    └── skills/
        └── napkin-pitch-architect/
            └── SKILL.md
```

Some files may be added or renamed as the workshop evolves. The `SKILL.md` files are the reusable instruction sets used by the examples.

## Prerequisites

- Python 3.10 or later (use a version supported by the CrewAI version you install).
- `pip` and a terminal.
- An LLM option:
  - **Local option:** LM Studio with a model downloaded and its local server running.
  - **Gemini option:** a Gemini API key for the Gemini pitch-generator script.
- Internet access to install Python packages. The local LM Studio inference calls themselves can run locally.

## 1. Create and activate a virtual environment

Run these commands from the `UsingSkills` directory.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

### Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

## 2. Install dependencies

Install the packages used by the examples:

```bash
pip install crewai python-dotenv openai google-genai
```

The `preflight_with_jev.py` helper is an optional TypeSafe/Jev example and requires the relevant TypeSafe Python SDK and API access. It is separate from the main scripts described below.

If CrewAI reports that `discover_skills`, `activate_skill`, or the `skills` agent parameter is unavailable, check the CrewAI version installed in your environment and use a version that supports the Skills API used by this repository.

## 3. Configure your model

The scripts load environment variables from a `.env` file in the **current working directory**. Create a separate `.env` file inside each example folder you plan to run.

### Option A — LM Studio (local model)

1. Open LM Studio and download a model your computer can run.
2. Load the model.
3. Start LM Studio's local server. The usual OpenAI-compatible base URL is `http://localhost:1234/v1`; use the URL shown in your LM Studio settings if it differs.
4. Create `story-teller/.env` or `pitch-creator/.env`, depending on the example you want to run.

Example `.env` for LM Studio:

```dotenv
MODEL_NAME=qwen3.5-9b
OPENAI_BASE_URL=http://localhost:1234/v1
OPENAI_API_KEY=lm-studio
```

Replace `MODEL_NAME` with the model identifier expected by your LM Studio server. The `OPENAI_API_KEY` value can be a placeholder for local LM Studio use; it is not a real secret in this configuration.

### Option B — Gemini API (pitch creator only)

The `3_gemini_skill_validation.py` script uses Gemini for both its pre-flight input check and the main pitch-generation agent. Create `pitch-creator/.env`:

```dotenv
GEMINI_API_KEY=replace_with_your_gemini_api_key
```

Get an API key through Google AI Studio. Keep the real key private.

> **Security:** Never commit `.env` files or real API keys to Git. Commit a `.env.example` file containing placeholders if you want to document configuration. If a real key has already been pushed to a remote repository, revoke or rotate it.

## Example 1 — Story Teller

**Location:** `story-teller/`

The agent writes a short, classroom-appropriate science-fiction story about a topic you enter. Its skill, `agentic-ai-storyteller`, directs the agent to:

- Center the story on Agentic AI systems that plan, use tools, and perform multi-step work.
- Include an unexpected plot twist.
- Keep the story under 500 words.
- Output only a title and story, without an introduction or explanation.
- Avoid profanity and inappropriate content.

### Run it

From the `UsingSkills` directory:

```bash
cd story-teller
python 1_skills.py
```

Enter a specific AI-related theme when prompted, such as `Agentic AI helping coordinate emergency response`.

The script prints the story and writes the generated result to `Agentic-AI-Story.md` in the current working directory.

### How the Skill is used

The script calls `discover_skills()` to find skills in the local `skills` directory and `activate_skill()` to activate the discovered skills. It then passes the skills directory to the agent using `skills=["./skills"]`.

This example includes both discovery/activation and directory-based skill loading to demonstrate the API. If you modify it for a production project, prefer one clearly understood loading approach and verify it against the CrewAI version you use.

## Example 2 — Napkin Pitch Creator

**Location:** `pitch-creator/`

The agent takes a student's rough project idea and creates a four-quadrant Napkin Pitch. The `napkin-pitch-architect` skill guides it to:

1. **The Big Idea** — explain the concept.
2. **Needs/Benefits** — distinguish what is known from what is still a guess.
3. **Execution** — describe how it could work and identify confirmed versus target partners.
4. **Business Rationale** — describe uniqueness and the sustainability plan.

The skill emphasizes a key entrepreneurship lesson: **do not invent missing information**. Unknown details should remain clearly marked for the student to fill in, and assumptions should not be presented as validated facts. The skill also specifies a limit of fewer than 250 words.

### A. Basic version — local model

This version loads the `napkin-pitch-architect` skill and sends the student's idea to the configured OpenAI-compatible model.

```bash
cd pitch-creator
python 2_skills.py
```

Enter a project idea when prompted. The result is printed in the terminal and written to `Napkin-Pitch.md`.

### B. Validation version — local model

This version first asks a local model through LM Studio to check whether the input is inappropriate, empty/gibberish, or a meta-prompt. If accepted, it runs the pitch-generation task.

```bash
cd pitch-creator
python 3_skill_validation.py
```

The pre-flight check is a model-based filter, not a guaranteed security boundary. Review its behavior before using it with real users. In the current code, a connection error causes the check to be skipped and execution to continue.

### C. Validation version — Gemini API

This version uses Gemini for the input check and for the main pitch-generation agent. It requires `GEMINI_API_KEY` in `pitch-creator/.env`.

```bash
cd pitch-creator
python 3_gemini_skill_validation.py
```

The model names are specified in the script. Check that the configured Gemini model identifiers are available to your account and supported by your installed CrewAI and Google GenAI SDK versions.

### Optional helper — TypeSafe/Jev pre-flight check

`preflight_with_jev.py` defines a separate function that evaluates input for profanity, very short/gibberish text, and meta-prompts using TypeSafe/Jev. It is a helper module; the main scripts above do not call it. To use it, configure `TYPESAFE_API_KEY`, install the appropriate TypeSafe SDK, and explicitly integrate `run_jev_preflight()` into the desired script.

## Troubleshooting

### The script cannot connect to the model

- Confirm that LM Studio is open, the model is loaded, and the local server is running.
- Check `OPENAI_BASE_URL` and `MODEL_NAME` in the `.env` file.
- Test the configured base URL and model identifier against the LM Studio server.
- Ensure you activated the intended virtual environment before installing packages and running the script.

### A required environment variable is missing

- Confirm the `.env` file is in the example folder you are running from.
- Check spelling: `MODEL_NAME`, `OPENAI_BASE_URL`, `OPENAI_API_KEY`, and, for the Gemini version, `GEMINI_API_KEY`.
- Do not add quotation marks unless your value requires them.

### CrewAI cannot find a skill

- Run the command from the example's own directory, as shown above. The code uses the relative path `./skills`.
- Confirm the file exists at `skills/<skill-folder>/SKILL.md`.
- Check the installed CrewAI version for compatibility with the Skills API used in the code.

### The output file appears in an unexpected folder

The scripts use relative output filenames. Run the script from its example directory so that `Agentic-AI-Story.md` or `Napkin-Pitch.md` is saved where expected.

### The generated output does not follow the Skill exactly

A Skill guides the model; it is not a deterministic guarantee. Try a clearer input, inspect the `SKILL.md` instructions, and verify the result against the required structure and word limit.

## Suggested student experiments

1. Give the Story Teller the same theme twice and compare the stories.
2. Change one rule in `agentic-ai-storyteller/SKILL.md` and observe the difference.
3. Give the Pitch Creator a vague project idea, then provide a richer version with target users, problem, solution, partners, and possible revenue.
4. Compare the generated pitch with `Napkin-Pitch.md` and identify which details are facts, assumptions, or missing.
5. Temporarily remove a requirement from the skill, rerun the agent, and observe whether the output changes.
6. Compare local-model and Gemini outputs using the same student idea.

## Key takeaway

**A Tool gives an agent a capability; a Skill gives it reusable instructions for how to approach a task.** These examples demonstrate how a carefully designed `SKILL.md` can improve consistency, output structure, and adherence to task-specific guardrails.
