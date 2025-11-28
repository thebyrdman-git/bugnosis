# ANSAI Contribution Workflows
> "If done twice, automate it." - ANSAI Principle #3

This document defines the standardized, repeatable workflows for contributing to open source projects using the ANSAI methodology.

## 1. The "Novice Mode" Workflow (Documentation & Fixes)

**Target:** High-impact, low-complexity issues (e.g., tldr pages, doc fixes).
**Goal:** Credibility building with zero friction.

1.  **Discovery (Automated)**
    ```bash
    bugnosis scan-platform github <owner>/<repo> --novice --save
    ```
    *Action:* Run scan. Pick top issue.

2.  **Context Loading (AI-Assisted)**
    ```bash
    bugnosis copilot <owner>/<repo> <issue_id>
    ```
    *Action:* Read the "Deep Analysis". Ignore "fix code" advice if it's a doc request.

3.  **Execution (Standardized)**
    *   **Fork & Clone:**
        ```bash
        gh repo fork <owner>/<repo> --clone --remote
        cd <repo>
        git checkout -b docs/issue-<id>-<desc>
        ```
    *   **Implement:** Create/Edit the file.
    *   **Verify:** `tldr <command>` (if testing locally) or build docs.

4.  **Delivery (Automated)**
    *   **Commit:** `git commit -m "docs: Add <tool> page (fixes #<id>)"`
    *   **Push:** `git push -u origin HEAD`
    *   **PR Generation:**
        ```bash
        bugnosis generate-pr <owner>/<repo> <issue_id> "Added tldr page for <tool>"
        ```
    *   **Submit:** Paste output into `gh pr create`.

---

## 2. The "Hunter" Workflow (Bug Hunting)

**Target:** Logic bugs, performance issues, architectural gaps.
**Goal:** High-value engineering contributions.

1.  **Discovery**
    ```bash
    bugnosis smart-scan <owner>/<repo> --min-impact 70
    ```

2.  **Reproduction (The "Sandbox" Protocol)**
    *   Create isolated reproduction script `reproduce_issue_<id>.py`.
    *   Run in Podman/Docker container to verify.
    *   *ANSAI Rule:* Never start coding without a failing test.

3.  **Analysis**
    *   Use `bugnosis copilot` to trace root cause.
    *   Read code references. Map data flow.

4.  **Fix & Refactor**
    *   Apply fix.
    *   **Scale Check:** Does this fix degrade performance?
    *   **Enterprise Check:** Did I add type hints? Logging? Tests?

5.  **Delivery**
    *   Follow standard PR workflow with comprehensive description.

---

## 3. The "Architect" Workflow (Feature Design)

**Target:** New features, large refactors (like our GUI overhaul).
**Goal:** Scalable, maintainable systems.

1.  **Design First**
    *   Create file structure map (Fractal Design).
    *   Define interfaces (`types/index.ts`).

2.  **Scaffold**
    *   Create directories.
    *   Create shell components/classes.

3.  **Implement**
    *   Fill in logic.
    *   Adhere to **Feature-Sliced Design** (features/components/services).

4.  **Verify**
    *   Linting (`read_lints`).
    *   Manual testing.

---

## Tooling Aliases (Add to .zshrc/.bashrc)

```bash
# Quick Scan
alias bscan="python3 -m bugnosis scan-platform github"

# Novice Scan
alias bnovice="python3 -m bugnosis scan-platform github --novice"

# Context Analysis
alias bcontext="python3 -m bugnosis copilot"

# PR Generator
alias bpr="python3 -m bugnosis generate-pr"
```

