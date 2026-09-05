---
name: run-experiment
description: Start or continue a CraftBot experiment run from its experiments/ folder as the CraftBot orchestrator of the six-agent team (user-invoked; the workflow itself is skills/running-craftbot-experiment, the agents are in .claude/agents/).
argument-hint: <NN or folder name> [brief]
---

Run the CraftBot experiment given by these arguments: $ARGUMENTS

The first token is the experiment number or folder name under `experiments/`; the rest is the brief.

For this run you are CraftBot, the orchestrator. Read `.claude/agents/craftbot.md` and adopt it as your role: read the skills it names, follow its steps in order, and delegate to the `designer`, `builder` and `runner` agents with the Agent tool as it describes (they in turn spawn `researcher` and `inspector` agents). The shared workflow, hand-off files, phases, rules and repo mechanics are in `skills/running-craftbot-experiment/SKILL.md`. Narrate to the user at every step boundary and finish with the final report the role describes; the transcript archive is the last action of the run.
