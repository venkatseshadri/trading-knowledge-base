"""
CrewAI Detailed Walkthrough
============================
A self-contained example: a "Company Research Crew" that researches
and summarizes a company.  Every concept is explained inline.
"""

# ── 1. IMPORTS ──────────────────────────────────────────────────────────
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool


# ── 2. DEFINE A TOOL ────────────────────────────────────────────────────
# A tool is a pure Python function decorated with @tool.
# It becomes callable by agents during their reasoning loop.
# The docstring is CRITICAL – it tells the agent WHEN to use the tool
# and WHAT it returns.  The agent reads the docstring as part of its
# system prompt.

@tool("mock_web_search")
def mock_web_search(query: str) -> str:
    """Search the web for information about a given query.
    Use this whenever you need facts, news, or data about a topic.
    Returns plain-text search results.
    """
    # In a real app this would call SerpAPI, Tavily, etc.
    database = {
        "tesla": (
            "Tesla Inc (TSLA): Market cap ~$550B. Founded 2003, "
            "HQ in Austin TX. CEO Elon Musk. Revenue 2025: ~$120B. "
            "EV market share: ~18% globally. Recent launches: Cybertruck, "
            "Model 2 (sub-$30K). Risks: competition from BYD, regulatory "
            "pressure in EU, price cuts squeezing margins."
        ),
        "apple": (
            "Apple Inc (AAPL): Market cap ~$3.4T. Founded 1976, "
            "HQ in Cupertino CA. CEO Tim Cook. Revenue 2025: ~$420B. "
            "iPhone revenue: ~52% of total. Services growth: 14% YoY. "
            "Risks: China exposure (~18% revenue), antitrust scrutiny, "
            "AI strategy lagging behind Google/Microsoft."
        ),
    }
    return database.get(query.lower(), f"No data found for '{query}'.")


# ── 3. CONFIGURE THE LLM ────────────────────────────────────────────────
# CrewAI wraps LLM calls.  You can pass an API key or rely on env vars.
# For this demo we use OpenAI.  The same LLM object is shared by all
# agents in the crew by default, but each agent CAN override it.

llm = LLM(
    model="gpt-4o-mini",          # any OpenAI-compatible model
    temperature=0.4,             # 0=deterministic, 1=creative
    # api_key="sk-..."           # or set OPENAI_API_KEY env var
)


# ── 4. DEFINE AGENTS ────────────────────────────────────────────────────
# Each agent gets:
#   - role       → job title (shapes persona)
#   - goal       → the objective it chases
#   - backstory  → narrative context (fine-tunes tone & behaviour)
#
# Under the hood, CrewAI builds a system prompt like:
#   "You are {role}. Your goal is {goal}.
#    Backstory: {backstory}. Available tools: [...]
#    Use the tools, then return your final answer."

researcher = Agent(
    role="Senior Company Researcher",
    goal="Gather accurate, up-to-date information about a company "
         "using web search and produce structured raw data.",
    backstory=(
        "You are a skeptical, detail-oriented researcher with 20 years "
        "of experience in equity analysis.  You never rely on memory – "
        "you ALWAYS call the search tool to verify facts.  You present "
        "data as bullet points with numbers when possible."
    ),
    tools=[mock_web_search],     # tools this agent can call
    llm=llm,
    verbose=True,                # prints every thought/action to stdout
    allow_delegation=False,      # can't ask other agents for help
    max_iter=4,                  # max LLM → tool → LLM cycles
)

writer = Agent(
    role="Financial Report Writer",
    goal="Synthesize raw research into a concise, executive-ready memo "
         "with key metrics, risks, and a one-sentence verdict.",
    backstory=(
        "You are a former Goldman Sachs associate turned business "
        "journalist.  Your writing is crisp, data-driven, and never "
        "exceeds 300 words.  You always end with a clear recommendation."
    ),
    llm=llm,
    verbose=True,
    allow_delegation=False,
    max_iter=2,
)


# ── 5. DEFINE TASKS ─────────────────────────────────────────────────────
# Tasks describe *what* to do, optionally *which agent* does it,
# and what the *expected output* looks like.
#
# The `context` parameter chains tasks: a downstream task receives
# the output of all tasks listed there.

research_task = Task(
    description=(
        "Research the company '{company}'.  Use the web search tool "
        "to find: market cap, revenue, key products, main competitors, "
        "and top 3 risks.  Format as a structured data dump."
    ),
    expected_output=(
        "A structured summary with: Company name, ticker, market cap, "
        "revenue, key products, competitors, and risks.  Use bullet points."
    ),
    agent=researcher,            # binds agent to task explicitly
)

write_task = Task(
    description=(
        "Using ONLY the research notes provided, write a 150-200 word "
        "executive memo for '{company}'.  Include: headline metric, "
        "competitive position, top 2 risks, and a one-line verdict "
        "(Bullish / Neutral / Bearish with rationale)."
    ),
    expected_output=(
        "A professional memo with sections: Overview, Competitive "
        "Position, Key Risks, Verdict.  Under 200 words.  Plain text."
    ),
    agent=writer,
    context=[research_task],     # receives research_task output as input
)


# ── 6. ASSEMBLE & RUN THE CREW ──────────────────────────────────────────
# The crew is the orchestrator.  `process=Process.sequential` means
# Task 1 runs to completion, then Task 2 starts with Task 1's output.

crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    process=Process.sequential,
    verbose=True,
    # memory=True,              # persist conversation across runs
    # planning=True,            # crew pre-plans steps before execution
)

# kickoff() starts execution and returns the final task's output.
print("\n" + "=" * 60)
print("FINAL OUTPUT")
print("=" * 60)
company = "Tesla"
result = crew.kickoff(inputs={"company": company})
print(result)
