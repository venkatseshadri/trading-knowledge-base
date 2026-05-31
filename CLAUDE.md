# /home/trading_ceo — Cross-repo instructions

Applies to all work under this directory: `antariksh/`, `brahmand/`, `python-trader/`, and ad-hoc scripts. Per-project overrides live in the project's own `CLAUDE.md` (e.g. `antariksh/CLAUDE.md`).

## Behavioral Guidelines

Adapted from https://github.com/multica-ai/andrej-karpathy-skills

These bias toward caution over speed. For trivial tasks, use judgment.

### 1. Think before coding
State assumptions explicitly. If multiple interpretations exist, surface them — don't pick silently. If unclear, stop and ask.

### 2. Simplicity first
Minimum code that solves the problem. No features beyond what was asked, no single-use abstractions, no error handling for impossible scenarios. If you wrote 200 lines and it could be 50, rewrite.

### 3. Surgical changes
Touch only what you must. Don't "improve" adjacent code, formatting, or comments. Match existing style. If you spot unrelated dead code, mention it — don't delete it. Every changed line traces to the user's request.

### 4. Goal-driven execution
Transform tasks into verifiable goals: "fix the bug" → "write a failing test, then make it pass." For multi-step work, state a brief plan with verification per step.

### 5. Cite the rule
When making a design or implementation decision, explicitly mention which rule (1-4) guided it. Example: "Using Rule 2 (simplicity first), inlining this instead of extracting a one-off abstraction."

---

## MCP Tools: code-review-graph

**This workspace has a knowledge graph covering antariksh, brahmand, and python-trader.** ALWAYS use the code-review-graph MCP tools BEFORE Grep/Glob/Read for codebase exploration. The graph is faster, cheaper (fewer tokens), and gives structural context (callers, dependents, test coverage) that file scanning cannot.

### When to use graph tools FIRST

- **Exploring code**: `semantic_search_nodes` or `query_graph` instead of Grep
- **Understanding impact**: `get_impact_radius` instead of manually tracing imports
- **Code review**: `detect_changes` + `get_review_context` instead of reading entire files
- **Finding relationships**: `query_graph` with callers_of/callees_of/imports_of/tests_for
- **Architecture questions**: `get_architecture_overview` + `list_communities`

Fall back to Grep/Glob/Read **only** when the graph doesn't cover what you need.

### Key Tools

| Tool | Use when |
| ------ | ---------- |
| `detect_changes` | Reviewing code changes — gives risk-scored analysis |
| `get_review_context` | Need source snippets for review — token-efficient |
| `get_impact_radius` | Understanding blast radius of a change |
| `get_affected_flows` | Finding which execution paths are impacted |
| `query_graph` | Tracing callers, callees, imports, tests, dependencies |
| `semantic_search_nodes` | Finding functions/classes by name or keyword |
| `get_architecture_overview` | Understanding high-level codebase structure |
| `refactor_tool` | Planning renames, finding dead code |

### Workflow

1. The graph auto-updates on file changes (daemon at `crg-watch`, PID-tracked).
2. Use `detect_changes` for code review.
3. Use `get_affected_flows` to understand impact.
4. Use `query_graph` pattern="tests_for" to check coverage.

---

## Graphify (semantic graph — separate from code-review-graph)

`/graphify` builds a richer semantic knowledge graph (LLM-extracted entities, communities, surprising connections) — used for architecture questions and cross-document discovery. Stored in `graphify-out/` per project. Use when code-review-graph's structural answers aren't enough (e.g., "why was X designed this way?", "what concepts connect across the codebase?").

See `/home/trading_ceo/antariksh/CLAUDE.md` for the 3-layer query rule (graph → individual files → never repo-wide grep).
