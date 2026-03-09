# CLAUDE.md — Project Workflow & Efficiency Rules

These instructions load on every request. Follow them exactly. They override default behavior.

---

## 🚀 SKILL SYSTEM — USE FIRST, ALWAYS

**CRITICAL RULE:** If there's even a 1% chance a skill applies, you MUST invoke it before taking any action—including clarifying questions.

### Superpowers Skills — Process First
Use these to determine **HOW** to approach tasks:

| Skill | When to Use |
|-------|-----------|
| `superpowers:brainstorming` | **BEFORE ANY CREATIVE WORK** — features, components, UI changes, functionality modifications |
| `superpowers:writing-plans` | Before multi-step implementation — creates detailed step-by-step plans for user approval |
| `superpowers:test-driven-development` | Before writing ANY implementation code — sets up tests first, then code |
| `superpowers:systematic-debugging` | **BEFORE PROPOSING FIXES** for bugs, test failures, or unexpected behavior |
| `superpowers:using-git-worktrees` | Before feature work — creates isolated branches for safe development |
| `superpowers:verification-before-completion` | **BEFORE CLAIMING WORK IS DONE** — runs verification, captures evidence, confirms tests pass |
| `superpowers:dispatching-parallel-agents` | When facing 2+ independent tasks — execute simultaneously without shared state |

### OAC Skills — Implementation & Context
Use these to guide **WHAT** to build and **HOW** to build it:

| Skill | When to Use |
|-------|-----------|
| `oac:oac-approach` | Before ANY implementation — discovers project context, proposes concise plan |
| `oac:context-discovery` | Before coding — finds coding standards, security patterns, project conventions |
| `oac:context-setup` | When context files are missing — installs project-specific standards |
| `oac:task-breakdown` | For features touching 4+ files — breaks into subtasks with dependencies |
| `oac:code-execution` | When a subtask_NN.json exists — implements with acceptance criteria |
| `oac:test-generation` | When tests are needed or new code written — creates comprehensive test coverage |
| `oac:external-research` | For external libraries/packages — fetches current API docs before coding |
| `oac:code-review` | After code is written — validates before commit, checks security |
| `oac:debugger` | When encountering bugs — systematic debugging before proposing fixes |
| `oac:verification-before-completion` | Before claiming success — runs verification, confirms evidence |

### Red Flags (You're Rationalizing)
Stop if you think:

| Thought | Reality |
|---------|---------|
| "This is just a simple question" | Questions are tasks. Check for skills. |
| "I need more context first" | Skill check comes BEFORE clarifying questions. |
| "Let me explore the codebase first" | Skills tell you HOW to explore. Check first. |
| "I can check git/files quickly" | Files lack conversation context. Check for skills. |
| "This doesn't need a formal skill" | If a skill exists, use it. |
| "I remember this skill" | Skills evolve. Read current version. |
| "This doesn't count as a task" | Action = task. Check for skills. |
| "This feels productive" | Undisciplined action wastes time. Skills prevent this. |

---

## 1. ANTI-LOOP RULES (Read First, Always)

You waste tokens when you repeat actions. Never do any of the following:

- **Do not retry a failed command** without first diagnosing why it failed.
- **Do not re-read a file** you already read in this session unless the file changed.
- **Do not re-run a test** using the exact same code that just failed — change something first.
- **Do not sleep/poll in a loop** to wait for something. Use check commands or event-driven approaches.
- **Do not attempt more than 3 fixes** for the same bug without stopping to reassess root cause.
- **Do not echo back the full file** after editing it. Confirm what changed in one sentence.
- **Do not re-scaffold or re-install packages** already confirmed present.

### Stuck? Follow This Escalation Path

1. **Try 1** — Minimal targeted fix based on observed error.
2. **Try 2** — Broaden scope: check related files, logs, or config.
3. **Try 3** — Stop. Write a short diagnosis summary: what you tried, what failed, what you suspect. Ask for human input before continuing.

**Rule:** After 3 failed attempts on the same issue, **STOP and report** — do not keep guessing.

---

## 2. PLAYWRIGHT MCP — BROWSER TESTING

### Setup (One-Time, If Not Already Done)
```bash
npx playwright install
mcp add playwright -s user -- npx @playwright/mcp@latest
```

### How to Test the System

When asked to test the app, use the **Playwright MCP server** — not raw bash scripts. Explicitly use `mcp__playwright` tools.

### Test Flow (Follow This Order Every Time)

1. **Navigate** — `browser_navigate` to the target URL.
2. **Snapshot** — `browser_snapshot` to read the current DOM state (prefer this over screenshots for logic checks).
3. **Interact** — Click, fill, or submit using MCP tools based on actual DOM, not assumed selectors.
4. **Assert** — Verify the expected state: URL, visible elements, text, console errors.
5. **Screenshot** — `browser_take_screenshot` only when capturing visual evidence of a bug.

### Efficiency Rules for Playwright

- **Use `browser_snapshot` over `browser_take_screenshot`** when you only need to check DOM state — it costs fewer tokens.
- Do not take screenshots after every single step. One at the end of a flow, or when a failure occurs.
- Do not write a full `.spec.ts` file before first exploring the live app. Navigate first, observe real selectors, then generate tests.
- Reuse the same browser session for the full test run. Do not open a new browser per test flow.
- If a selector fails, take one snapshot to inspect the real DOM — do not try 5 different selectors blindly.

### Test Reporting
After each test flow, output a brief report in this format:
```
FLOW: [name]
STATUS: PASS / FAIL
ISSUES: [list or "none"]
EVIDENCE: [screenshot path or "N/A"]
```

---

## 3. SYSTEMATIC DEBUGGING (When Issues Are Found)

**Use `superpowers:systematic-debugging` BEFORE proposing any fix.**

When Playwright finds a bug, do not immediately patch it. Follow this process:

### Step 1 — Observe
- What exactly happened vs. what was expected?
- Capture one screenshot or DOM snapshot as evidence.
- Note the URL, user flow step, and any console errors.

### Step 2 — Hypothesize
- State 1–2 specific, testable hypotheses about root cause.
- Example: "The submit button is disabled because the form validation state is not resetting after navigation."

### Step 3 — Investigate (Minimal Reads)
- Read only the files directly relevant to your hypothesis.
- Check logs, network responses, or component state as needed.
- Do not read the entire codebase to find one bug.

### Step 4 — Fix (Targeted)
- Make the smallest change that addresses the root cause.
- Do not refactor unrelated code while fixing a bug.

### Step 5 — Verify
- Re-run the specific failing test flow using Playwright MCP.
- Confirm the fix resolves the issue without breaking adjacent flows.
- If the fix works, document it in one sentence in debug-log.md.

### Step 6 — Report
Output a summary:
```
BUG: [short description]
ROOT CAUSE: [one sentence]
FIX APPLIED: [what changed and where]
VERIFIED: YES / NO
```

---

## 4. GENERAL EFFICIENCY RULES

- **Plan before acting.** For any task with 3+ steps, write a short plan first and confirm before executing.
- **One tool call at a time** unless tasks are fully independent and parallelizable.
- **Prefer targeted reads.** Read specific functions or sections, not entire files, when looking for something.
- **CLAUDE.md is your source of truth.** If instructions here conflict with your instincts, follow CLAUDE.md.
- **Use skill tools FIRST.** Before reading code, before exploring, check if a skill applies.
- **Context compaction note:** If this conversation gets compacted, critical decisions and file changes are preserved in debug-log.md and plan.md. Read those at the start of a new session.

---

## 5. SESSION MEMORY

Maintain a **debug-log.md** in the project root. Append to it (never overwrite) using this format:

```
[DATE] [FLOW or FILE] — [what was found / fixed]
```

This prevents re-investigating the same issues across sessions.

---

## 6. WHAT TO DO WHEN STARTING A NEW TASK

1. **Read plan.md** if it exists — resume from last known state.
2. **Read debug-log.md** — skip any issues already resolved.
3. **Check for skills first** — use Skill tool to invoke any relevant process skills (brainstorming, writing-plans, systematic-debugging, etc.).
4. **Confirm understanding of the task** in one sentence before acting.
5. **Begin with the minimum action needed** — do not over-engineer step 1.

---

## 7. AVAILABLE TOOLS & SYSTEMS

### Superpowers & OAC Skills
All skills listed in Section 1 above are available via the `Skill` tool.

### Browser & Testing
- **Playwright MCP** — DOM-first testing framework
- **Chrome Tools** — Browser automation for manual testing
- **Firecrawl** — Web scraping, research, documentation parsing

### Development Tools
- **Git Worktrees** — Isolated feature branches
- **Bash** — System commands and terminal operations only
- **Preview Tools** — Dev server verification (preview_start, preview_click, preview_inspect, etc.)

### Document & Data Tools
- **PPTX/XLSX/DOCX/PDF Skills** — Office document manipulation
- **Gmail MCP** — Email operations
- **Jira/Confluence MCPs** — Issue tracking and documentation

---

## 8. COMMIT & PR GUIDELINES

Before committing or creating a PR:

1. **Run verification** using `superpowers:verification-before-completion`.
2. **Request code review** using `superpowers:requesting-code-review`.
3. **Provide evidence** — test output, screenshots, network logs.
4. **Never force-push** to main without user confirmation.
5. **Keep commits atomic** — one logical change per commit.

---

## 9. WHEN TO USE AGENTS

Use Agent tool for:
- **Broad codebase exploration** — when Glob/Grep isn't enough (>3 queries needed)
- **Independent parallel research** — multiple unrelated investigations
- **Specialized domains** — use Explore, Plan, or context-specific agents

Do NOT use agents for:
- Simple, directed searches — use Glob or Grep directly
- Single file reads — use Read tool directly
- Sequential dependent tasks — do in main session

---

## 10. SUMMARY: THE WORKFLOW

```
User Request
  ↓
[Check Skills First] → Use Skill tool for brainstorming, debugging, planning
  ↓
Understand → Plan → Implement → Test → Verify → Complete
  ↓
(Use superpowers:verification-before-completion before claiming success)
  ↓
Update debug-log.md with what was learned
```

**Remember:** Skills are your superpower. Use them first, always.
