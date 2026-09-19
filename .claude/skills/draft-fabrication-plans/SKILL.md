---
name: draft-fabrication-plans
description: Draft fabrication plans (A2 drawings, glue-up templates, cut list, stick order) for building a physical scale model of a finished CraftBot experiment model (user-invoked; the procedure itself is skills/draft-fabrication-plans, the code is the fabrication kit in tools/).
argument-hint: <NN or folder name> [run and version, scale, stock]
---

Draft the fabrication set for the experiment given by these arguments: $ARGUMENTS

The first token is the experiment number or folder name under `experiments/`; the rest names the run, the version and anything already decided (scale, stock, paper).

Read `skills/draft-fabrication-plans/SKILL.md` completely and follow it, with `tools/API_FABRICATION.md` for the code and `experiments/16_Expressive_Structure/fabrication/GPT-6/` as the worked example. This is not an experiment run: do not adopt the CraftBot orchestrator role, do not spawn the run's agents, and do not touch the run folder. Write everything to `experiments/<NN>/fabrication/<Run>/`, the subfolder named after the run folder the model comes from.
