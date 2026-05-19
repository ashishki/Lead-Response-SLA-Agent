# Codex Orchestrator Prompt

This repository uses the project-local orchestrator at:

`docs/prompts/ORCHESTRATOR.md`

There is no Claude Code runtime for this project. Do not paste an orchestrator
prompt into Claude, and do not invoke Codex through `codex exec` from inside an
active Codex session.

The active Codex session should read `docs/CODEX_PROMPT.md`, `docs/tasks.md`,
and `docs/IMPLEMENTATION_CONTRACT.md`, then perform the next task directly in
the current workspace.
