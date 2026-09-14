---
name: run-experiment
description: Start, continue, or redo a CraftBot experiment in experiments/ using the repository's coordinated design, build, inspection, and close-out workflow.
---

Read `.claude/skills/run-experiment/SKILL.md` completely and follow it as the canonical entry-point instructions.

Apply these Codex compatibility rules:

- Treat the text following `$run-experiment` as the `$ARGUMENTS` referenced by the canonical skill. For an implicit invocation, derive those arguments from the user's request.
- Use the Codex custom agents named `craftbot`, `designer`, `builder`, `inspector`, `researcher`, and `runner` when the workflow calls for those roles.
- Translate references to Claude's `Agent` and `SendMessage` tools to Codex subagent spawning and messaging capabilities.
- Treat Claude-specific tool lists, model names, tiers, colors, turn limits, and background metadata as documentation rather than Codex configuration. The active Codex runtime instructions, permissions, and model settings take precedence.
