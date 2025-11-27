# Developer Guide: The Hero Engine

Welcome to the engineering side of Bugnosis.

If you are reading this, you are likely interested in the **architecture**, **algorithms**, and **system design** that powers this tool.

## 🏗 Architecture Overview

Bugnosis is designed as a **Federated Impact Engine**. It is not a monolithic scraper. It is a modular system composed of:

1.  **The Core (CLI/Python):**
    *   `ImpactEngine`: The 0-100 scoring algorithm.
    *   `AIEngine`: The reasoning layer (Diagnosis, PR Gen).
    *   `FederatedSearch`: Parallel execution across platform adapters.
    *   `PluginSystem`: Extensible architecture for new capabilities.

2.  **The Interface (Tauri/Rust/React):**
    *   **Rust Backend:** Handles system tray, OS notifications, and process management.
    *   **React Frontend:** The "Antivirus" dashboard.
    *   **IPC:** Asynchronous communication between the GUI and Core.

3.  **The Data Layer (SQLite):**
    *   Local-first.
    *   Zero-latency queries for "Offline Mode".
    *   Sync-capable (future).

## 🧩 The Plugin System

We believe in **Micro-Kernels**. The core of Bugnosis should be small. Everything else is a plugin.

### Creating a Plugin

Plugins live in `~/.bugnosis/plugins/`. They can extend:
*   **Scanners:** Add Jira, Redmine, or specialized security scanners.
*   **Analyzers:** Custom impact logic (e.g., "Crypto Impact" or "Medical Device Impact").
*   **Reporters:** Export to Slack, Discord, or enterprise dashboards.

```python
from bugnosis.plugins import PluginBase

class MyCustomScanner(PluginBase):
    @property
    def name(self): return "security-audit"
    
    @property
    def version(self): return "1.0.0"
    
    def register(self, context):
        # Register a new scanning capability
        context['scanner'].register_rule('cve-check', self.check_cve)

    def check_cve(self, bug):
        # Custom logic...
        return impact_score
```

## 🧠 Hard Problems We Are Solving

This is not just "hitting an API". We are solving:

1.  **Graph-Based Impact Scoring:**
    *   *Challenge:* How do you know if a bug in `lib-core` is important?
    *   *Solution:* We are building a dependency graph crawler to calculate transitive impact. A bug in a library used by 10k projects gets a higher score.

2.  **Federated Context Resolution:**
    *   *Challenge:* User types "auth bug".
    *   *Solution:* We use LLMs to semantic-match against a vector index of open source projects, resolving "auth" to `keycloak`, `auth0`, `passport.js`, etc., across GitHub and GitLab simultaneously.

3.  **Automated Context Extraction:**
    *   *Challenge:* LLMs hallucinate fixes if they don't see the code.
    *   *Solution:* We are building a smart-context fetcher that pulls *only* relevant files (using ctags/LSP) to fit within the context window for accurate PR generation.

## 🛠 Tech Stack

*   **Language:** Python 3.10+ (Core), Rust (System), TypeScript (UI)
*   **AI:** Groq (Llama 3 70B) for speed/cost, OpenAI fallback.
*   **Build:** Poetry (Python), Cargo (Rust), Vite (Frontend).

## 🤝 How to Contribute

We treat this repo like a production engineering project.

1.  **RFC Process:** For big changes, write a short proposal in Discussions.
2.  **Tests:** Pytest is mandatory.
3.  **Types:** Mypy strict mode is our goal.

---

**"We don't just write code. We engineer impact."**
