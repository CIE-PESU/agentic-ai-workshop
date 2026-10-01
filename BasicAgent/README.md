# PESU CIE - Agentic AI Workshop H2 2026

## Session: Week 1 and 2 - Basic Agents

Welcome to the **PESU CIE Agentic AI Workshop**.

In these first two sessions, we will build our understanding of **LLMs, CrewAI, Agents, Tasks, and Crews** by running simple CrewAI programs locally.

You can follow **one of two approaches**:

- **Option 1: LM Studio** — run an LLM locally on your laptop.
- **Option 2: Gemini API** — use Google's Gemini API if you cannot install or run LM Studio on your laptop.

---

# 1. Getting a Gemini API Key

This option is for students who **cannot install or run LM Studio** on their laptops.

### Step 1: Open Google AI Studio

Go to:

https://aistudio.google.com/

### Step 2: Create an API Key

Create a **New API Key**.

### Step 3: Copy the API Key

Copy the generated API key and keep it available for the workshop.

You will place the key in the `.env` file used by the CrewAI examples.

> **Important:** Do not share your API key with anyone and do not commit your `.env` file to GitHub.

---

# 2. Using LM Studio

If your laptop can run a local LLM, you can use **LM Studio**.

### Step 1: Install LM Studio

Install and configure LM Studio on your laptop.

### Step 2: Download a Model

Pull/download:

**Qwen 3.5 9B**

or select a **smaller model** depending on your laptop's:

- RAM
- CPU
- GPU
- Available disk space
- Overall processing capability

The goal is to have a model that runs comfortably on your machine.

---

# 3. Python Version

Please use:

**Python 3.10 to 3.12**

Python 3.13 may also work, but if you encounter compatibility issues, use Python 3.12.

You can check your Python version with:

```bash
python --version
```

or:

```bash
python3 --version
```

---

# 4. Code Provided in This Folder

You will find the following Python scripts in this folder.

| File | Description |
|---|---|
| `basicagent.py` | Basic CrewAI Agent for LM Studio users |
| `v2_basicagent.py` | More complex CrewAI Agent for LM Studio users |
| `v1_multiagent.py` | Multi-Agent CrewAI example for LM Studio users |
| `crewai-gemini.py` | Basic CrewAI Agent for Gemini users |
| `DOTENV.SAMPLE` | Environment configuration template for API keys and future usage |

## About the Gemini configuration

The following programs can also be configured by students to work with the Gemini API:

- `v2_basicagent.py`
- `v1_multiagent.py`

You can configure these examples for Gemini based on the LLM you choose.

The current workshop configuration uses:

```text
gemini/gemini-3.5-flash-lite
```

> **Note:** Model availability and model names can change. If the configured Gemini model is unavailable in your account, check the current models available through Google AI Studio and adjust the configuration accordingly.

---

# 5. Setting Up the Environment

It is recommended that you create a Python virtual environment for the workshop.

## Create a virtual environment

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

---

# 6. Installing CrewAI

First, upgrade `pip`:

```bash
python -m pip install -U pip
```

Then install CrewAI:

```bash
pip install crewai
```

You can verify the installation with:

```bash
python -c "import crewai; print('CrewAI installed successfully')"
```

## Alternative: Using `uv`

Students who are comfortable with `uv` can alternatively use `uv` for Python environment and package management.

If you face installation or environment-related issues, please reach out to the TAs.

### TAs

- **Ashwin Venkatesh**
- **Kishan Kabadi**

Please contact them via **WhatsApp / Call** for installation-related assistance.

---

# 7. Environment Configuration

A file named:

```text
.env.example
```

is provided as a template.

Create your own `.env` file based on this template.

For example:

```bash
cp .env.example .env
```

Then edit `.env` with the configuration appropriate for your setup.

## Important

**Never commit your `.env` file to GitHub.**

Your `.env` file may contain an API key or other private configuration.

The repository should contain:

```text
.env.example
```

but **not your actual `.env` file**.

---

# 8. What We Are Learning

During Weeks 1 and 2, focus on understanding the basic building blocks of CrewAI.

You should become familiar with:

```text
Agent
  │
  ├── Role
  ├── Goal
  ├── Backstory
  ├── LLM
  └── Verbose
       │
       ▼
Task
  │
  ├── Description
  ├── Expected Output
  └── Agent
       │
       ▼
Crew
  │
  ├── Agents
  ├── Tasks
  └── Process
```

The objective is not just to make the code run.

You should understand **what each of these components does and why it exists**.

---

# 9. To Do Before the Next Class

Please complete the following before the next session.

### 1. Get CrewAI installed and running

Make sure that you can successfully install CrewAI and run at least one of the examples.

### 2. Test the code

Run all the relevant code examples with your own questions/topics.

Try changing the input and observe how the Agent responds.

### 3. Understand the Verbose Output

Pay attention to the output produced when:

```python
verbose=True
```

is used.

Observe what CrewAI tells you about:

- Agent execution
- Task execution
- Crew execution
- LLM calls
- Agent responses

Do not simply ignore the verbose output.

It is useful for understanding what is happening inside the CrewAI workflow.

### 4. If you are using LM Studio

Keep an eye on the **LM Studio LLM logs** while your CrewAI program is running.

Observe:

- When the model receives a request
- The prompt being processed
- The model's response
- Processing/inference information

### 5. If you are using Gemini

Keep an eye on **Gemini API rate limits** while experimenting.

Avoid repeatedly running large prompts unnecessarily, particularly while testing or debugging your code.

---

# 10. Recommended Learning Approach

Do not be afraid to modify the examples.

Try changing:

- The Agent's role
- The Agent's goal
- The Agent's backstory
- The Task description
- The expected output
- The topic/question given to the Crew

Then run the program again and observe what changes.

The goal of these first sessions is to move from:

> **"I can run a CrewAI program."**

to:

> **"I understand how an Agent, Task, and Crew work together."**

---

## Workshop Progression

We will progressively move from:

```text
Basic Agent
     ↓
More Complex Agent
     ↓
Multiple Agents
     ↓
Multiple Tasks
     ↓
Sequential Execution
     ↓
Tools
     ↓
Memory
     ↓
More Complex Agentic Workflows
```

Have fun experimenting, breaking things, and understanding **why** they break.
