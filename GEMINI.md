# ghostshell — Gemini Context

@./CLAUDE.md
@./REPO-MAP.md

## Gemini-Specific Notes
- This file imports CLAUDE.md and REPO-MAP.md via Gemini's @import syntax.
- You are typically used for PLANNING and ANALYSIS, not direct code execution.
- Read the full codebase structure via REPO-MAP.md before proposing changes.
- Output structured plans with specific file paths and function names.
- Identify module boundaries, dependency edges, and natural seam lines.
- When analyzing god files (>1,500 lines): map every function to a proposed module.
- Do not modify: CLAUDE.md, AGENTS.md, GEMINI.md, REPO-MAP.md, .env files.
