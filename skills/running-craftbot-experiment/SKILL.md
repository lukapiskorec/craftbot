---
name: running-craftbot-experiment
description: Use when asked to run, start, redo, continue or resume a CraftBot experiment in this repository (an experiments/NN_Name/ folder with input/ and optionally references/), whether invoked as /run-experiment or in plain words. The workflow of the six-agent team (CraftBot, Designer, Researcher, Builder, Inspector, Runner), its hand-off files, phases, rules, cost rules, the multi-variation variant and the repo mechanics. Specific to the CraftBot repo layout, its tools/, skills/, .claude/agents/ and web viewer; not a general-purpose skill.
---

# Running a CraftBot experiment

## Overview

One run turns a brief plus reference materials into versioned Blender Python scripts, renders, a design rationale with callouts, models in the web viewer and an archived transcript. Since experiment 15 the run is done by a team of six agents defined in `.claude/agents/`; the session that receives `/run-experiment` acts as CraftBot, the orchestrator, and spawns the others. The user reads the narration while it runs and a full report at the end. This skill is the shared workflow; each agent's own procedure is in its agent file, and the modelling knowledge lives in the other skills and in `tools/`.

A run belongs to one model, and everything it writes lives in a run folder named after that model (`<Agent>`, see "Run folder and agent name" below). Nothing in the workflow assumes Fable; Fable is one agent among others.

The default run designs one building. A run designs several variations of the building only when the brief explicitly asks for it; that variant, a shared stage followed by one team per variation, is in "Multi-variation runs" below.

Experiments 01 to 14 were single-agent runs of the same workflow; their outputs have the same shape minus the hand-off files.

## Run folder and agent name

Every subfolder of `experiments/NN_*/` except `input/` and `references/` is a run folder, one per model that has run the experiment. The tools (`tools/export_all_models.py`, `closeout.py`, `callouts.py`) discover run folders this way; nothing is registered anywhere else.

`<Agent>` is the folder name, `<slug>` the file slug used in every file name of the run: the folder name lower-cased with everything but letters and digits removed.

| The harness reports | `<Agent>` (folder) | `<slug>` |
|---|---|---|
| Fable 5.1, `claude-fable-5-1` (any Fable version) | `Fable` | `fable` |
| Opus 5.1, `claude-opus-5-1` | `Opus 5.1` | `opus51` |
| Opus 5, `claude-opus-5` | `Opus 5` | `opus5` |
| Sonnet 5, `claude-sonnet-5` | `Sonnet 5` | `sonnet5` |
| GPT-5.1 in ChatGPT | `ChatGPT 5.1` | `chatgpt51` |
| anything else | product name and version as reported, no vendor prefix (`Astra`, `Gemini 3 Pro`) | letters and digits of it |

Fable keeps its bare name because eleven experiments already use `Fable/`; every other model carries its version so that two generations of the same product get separate runs.

How CraftBot finds the name, before creating any file: in Claude Code the system prompt's environment section reads "You are powered by the model named X. The exact model ID is Y." Another harness states it in its own way or prints it with its model command (`/model` in Claude Code). If neither is available, CraftBot asks the user once and waits; a guessed folder name is the one mistake this section exists to prevent. The run is named after the model that runs CraftBot; the judgement agents inherit that model and never rename the folder.

The record is `<Agent>/agent.md`, written by CraftBot when it creates the folder and read by every agent it spawns:

```
# Agent

- agent: Opus 5.1
- slug: opus51
- model: Opus 5.1
- model id: claude-opus-5-1
- mechanical model: Sonnet 5
- harness: Claude Code
- started: 2026-09-08
```

If `<Agent>/` already exists for the detected model, the run is a continuation and `agent.md` is appended with a `- continued: <date>` line, not rewritten. A run folder of a different model in the same experiment is another agent's run: never opened, never written (the independence rule).

File names carry the slug: `experiment_NN_<slug>_vXX.py`, `views_<slug>.py`, `experiment_NN_<slug>_design_rationale.md`, `experiment_NN_<slug>_callouts.json`, `experiment_NN_<slug>_conversation.jsonl`, `input/experiment_NN_prompts_<slug>.txt`. In the viewer the run's models are `viewer/models/<exp>/<slug>_vXX.json` with `<slug>_rationale.md` and `<slug>_callouts.json` beside them, and the index lists the run under the folder name.

## Models per tier

Each agent file carries a `tier:` line. The judgement tier (CraftBot, Designer, Builder) runs on the model that runs CraftBot and names the run. The mechanical tier (Inspector, Researcher, Runner) does bounded work against a checklist (look at PNGs, extract cited rules, run a script) and runs on the cheapest model of the same family that reads images and follows a procedure. The tier is the general statement; the model per harness is this table, one row per harness, added when a harness is first used:

| Harness | Judgement tier | Mechanical tier | How it is set |
|---|---|---|---|
| Claude Code | the model that runs CraftBot (`model: inherit`) | Sonnet (`model: sonnet` in the three mechanical agent files) | agent frontmatter |
| any other | the model that runs CraftBot | the harness's cheaper model of the same family, if it has one, else the same model | the harness's own agent configuration; record the choice in `agent.md` |

The mechanical model goes into `agent.md` and into rationale section 0, because a Sonnet Inspector or Researcher changes what the verification and the sourcing mean. The run folder is still named after the judgement model only.

## Roles and hand-off files

| Agent | Tier | Owns | Reports to | Spawned by | May spawn |
|---|---|---|---|---|---|
| CraftBot | judgement | brief, scope, phases, rationale, report | the user | `/run-experiment` (the session itself) or `claude --agent craftbot` | Designer, Builder, Runner |
| Designer | judgement | spatial and construction concept, requirements, design decisions, comparison round, structural review | CraftBot | CraftBot (the concept-stage one is resumed for phase 2 and review rounds; a fresh one answers small questions) | Researcher, Inspector |
| Researcher | mechanical | manual selection and extraction, figure snippets, online search on approval | Designer | Designer | none |
| Builder | judgement | one version per spawn: script, views, the render and check loop, version numbering, the version's notes entry | CraftBot (progress), Designer (design questions, through the notes and CraftBot) | CraftBot, fresh for every version | Inspector |
| Inspector | mechanical | visual verification of one part of one version (a variation, a storey, or the comparison round), photo fidelity, comparison table | Builder or Designer | Builder (several per version, in parallel) or Designer | none |
| Runner | mechanical | close-out of every version and of the run | CraftBot | CraftBot (standing, background) | none |

Every hand-off is a file in `experiments/NN_*/<Agent>/`, so any agent can be restarted from disk and no agent depends on another agent's chat:

| File | Written by | Read by |
|---|---|---|
| `agent.md` (agent, slug, model, model id, mechanical model, harness, date) | CraftBot, first file of the run | everyone |
| `brief.md` | CraftBot | everyone |
| `concept.md` (spatial concept, construction concept, photo rule set; the single carrier of numbers for the Builder) | Designer | Researcher (cited sections), Builder, Inspector (rule set) |
| `sources.md` (verdict table first, then the rule table) and snippets in `references/` with `captions.md` | Researcher | Designer (the verdict table, then rows it cites); CraftBot (the verdict table) |
| `requirements.md` (id, text, source, check method; ticked by the Builder) | Designer | Builder, Inspector (assigned lines), Runner |
| `design_notes.md` (decisions and rejected alternatives, dated by version) | Designer | CraftBot |
| `version_notes.md` (per version: change, counts, families, views rendered, findings, remaining, open questions) | Builder | the next Builder, CraftBot |
| `inspection_vXX_<part>.md`, merged into `inspection_vXX.md` | Inspectors, merged by the Builder | Builder (the summaries), Designer |
| `closeout_vXX.md`, `closeout_run.md` | Runner (via `tools/closeout.py`) | Builder, CraftBot |
| `experiment_NN_<slug>_vXX.py`, `views_<slug>.py` | Builder | the next Builder, Runner |
| `experiment_NN_<slug>_design_rationale.md`, `experiment_NN_<slug>_callouts.json` | CraftBot | Runner, viewer |
| `input/experiment_NN_prompts_<slug>.txt` | CraftBot (verbatim appends) | everyone |
| `experiment_NN_<slug>_conversation.jsonl` | Runner, last action of the run | nobody during the run |
| `concept_shared.md`, `common_<slug>.py` (multi-variation runs only) | shared-stage Designer, first Builder | every team |

## What each agent reads

Each agent file lists its skills as always or conditional. A conditional skill is loaded only when the spawner names it in the spawn message: CraftBot knows the materials from the brief and the geometry from the concept, the Designer knows what its Researcher and Inspector are for. An agent loads exactly what its file lists as always plus what the message names, and reads only the files in its row.

| Agent | Always | Conditional, named by the spawner | Reads | Never reads |
|---|---|---|---|---|
| CraftBot | running-craftbot-experiment, writing-design-rationale, unslop | extending-previous-models (brief continues an earlier experiment) | brief.md (writes), agent.md, concept files (scope check), requirements.md (counts), the Researcher's verdict table, design_notes.md, version_notes.md, inspection summaries, closeout files | renders, scripts, manuals, sources.md rows |
| Designer | running-craftbot-experiment (roles, rules), reading-visual-references, structural-logic, working-from-reference-documents, unslop | timber-framing (timber in the materials), roof-framing-and-sheathing, non-orthogonal-geometry, modular-grids-and-panelization, extending-previous-models | brief.md, agent.md, input/, references/, the verdict table and the sources.md rows it cites, version_notes.md open items, inspection files when answering | scripts, other run folders |
| Researcher | working-from-reference-documents, running-craftbot-experiment (mechanics: manuals), manuals/INDEX.md | reading-visual-references (sources are drawings) | the Designer's question list, the concept sections it cites, manual .md files, the exact PDF pages the figure index names | the rest of concept.md, renders |
| Builder | running-craftbot-experiment (rules, mechanics: building), procedural-geometry, structural-logic, verifying-models, tools/API.md, unslop | timber-framing, roof-framing-and-sheathing, non-orthogonal-geometry, modular-grids-and-panelization, extending-previous-models | agent.md, brief.md, concept.md, requirements.md, the last version_notes.md entry, the previous script and views file, the previous inspection summary, the previous closeout, the snippets the concept names | sources.md, manuals, input images |
| Inspector | verifying-models | reading-visual-references (comparison round) | the PNGs of its subset, views_<slug>.py, its assigned requirement lines, the photo rule set and reference images (matched view or comparison round only), its previous findings list | scripts, sources.md, design_notes.md, PNGs outside its subset |
| Runner | running-craftbot-experiment (mechanics: close-out, outputs), the header of tools/closeout.py | none | agent.md, its own closeout files | everything else |

## What the user provides

| Item | Where | Notes |
|---|---|---|
| Experiment folder | `experiments/NN_Name/` | NN = two digits; a bare number in the invocation resolves by globbing `experiments/NN_*` |
| Materials | `input/` | photos, drawings, an inherited script when the brief extends an earlier model |
| Manuals | `manuals/` (repo root, shared) | 17 timber construction manuals as extracted `.md` summaries plus the original PDFs (gitignored, downloadable); `manuals/INDEX.md` is the catalogue |
| Extra references | `references/` (optional) | annotated screenshots, comparison images; the Researcher adds its snippets here |
| The brief | the invocation message | what to build, constraints, iteration limit; may name a manual or a chapter, which is then mandatory; asks for several variations explicitly when it wants them |

The user places no code and no prompt files. If the brief is missing, CraftBot derives it from the folder name and the materials, states it, and proceeds; the user can interrupt. When the brief and a material disagree, the brief wins; the conflict is recorded as a deliberate deviation.

## Phases

1. **Set-up (CraftBot).** Agent detected and `<Agent>/agent.md` written (the folder created if missing, the agent, the mechanical model and the folder posted to the user), prompt file, `brief.md` (the brief as understood, posted to the user, saying whether the run is single-variation or multi-variation), Designer spawned with its conditional skills, Runner spawned in the background with the run folder name.
2. **Concept (Designer, Researcher).** `concept.md`, research through one or more Researchers (each returns a verdict table; the Designer works from it), `requirements.md` and the photo rule set. CraftBot checks the concept against the brief and posts the source-to-rule-to-number table and the deviations before any geometry exists.
3. **Build to the brief (Builders, Inspectors, Runner).** The version loop, one fresh Builder per version: write, render, overlap and contact checks, family triage, Inspectors in parallel (one per variation or storey), the notes entry, return. A version over the pair threshold (20 penetrating pairs) renders the four orbits only and gets no Inspector; intermediate versions under it render the orbits plus the changed views; the first inspected and the last version of a phase render the full set. After every version the Builder reports to CraftBot, CraftBot sends the Runner, and the next Builder reads `closeout_vXX.md` and the notes entry. Stops at 0 pairs, 0 floating, nothing open in the inspection, every requirement of the phase ticked or waived. Default limit 10 versions per phase unless the brief says otherwise; at the limit, what remains open is reported.
4. **Comparison and structural review (Designer with an Inspector).** Against the reference (rationale 3b): the last model versus the photos, drawings or figures, as a table (in the reference, in the model, change or kept with reason). Independent of the reference (rationale 6b): the checklist of the structural-logic skill on what was built. Both feed `requirements.md`; the Builders run the phase-2 versions under the same loop. The concept-stage Designer is resumed for this; small questions during the build go to a fresh Designer (CraftBot step 6b).
5. **User review rounds.** A user message with changes is a new phase: CraftBot appends it verbatim to the prompt file, splits it into scope (its own decision, recorded in `brief.md`), design (Designer) and requirement lines (Designer writes, Builder implements); the round is recorded as rationale section 3c. Push back in one line where a request is a mistake, then do it as asked.
6. **Close-out (CraftBot, Runner).** Rationale compiled from the notes files, callouts written and checked, the Runner's run check, the final report, the transcript archived last.

## Rules

- **Spawning tree** is flat under CraftBot: CraftBot spawns Designer, Builder and Runner; the Designer spawns Researchers and Inspectors; the Builder spawns Inspectors. Researchers and Inspectors are disposable, one per question set or version part; their files are the record. The Runner is one standing background agent, continued with messages. The Builder is fresh per version; the Designer is resumed only for the concept, the phase-2 round and review rounds.
- **The spawner names the conditional skills.** Every spawn message lists the conditional skills the agent loads (the reading table above); the agent loads nothing conditional on its own.
- **Disagreements.** When the Builder cannot meet a requirement, it records the conflict and its nearest alternative in `version_notes.md` and its return; the Designer rewrites the requirement or the concept. When that changes scope, CraftBot decides and records the decision in `brief.md`. The Builder never narrows scope on its own.
- **Research depth.** The Researcher works from the manuals first, in the order index descriptions, chapter lists, extracted `.md`, exact PDF pages. An online search needs the Designer's approval per request; anything external is labelled in `references/captions.md` and in `sources.md`.
- **Independence.** No agent opens another agent's run folder for the same experiment (`ChatGPT 5.1/`, `Fable/` or any run folder that is not this run's `<Agent>/`). Common ground is `tools/`, `skills/`, `manuals/`, `input/` and `references/`; in a multi-variation run also the orchestrator folder's `concept_shared.md`, `sources.md` and `common_<slug>.py`, read-only for the teams.
- **Narrate visibly.** Transcripts drop private reasoning. Decisions, rejected alternatives and key numbers go into the notes files and into CraftBot's messages; the rationale is compiled from them.
- **Settle questions from the materials** and state an assumption rather than blocking; questions that change scope go up the tree.
- **Shared code.** The one sanctioned edit to `tools/` during a run is an `OVERRIDES` entry for the experiment in `tools/layers.py`. Promotions of helpers into `tools/` are proposals in `version_notes.md`, done after the run.
- **No commits.** The user commits; CraftBot lists the files.
- **Load skills by their descriptions.** Each agent file lists the skills it reads at startup; the conditional ones (timber-framing, roof-framing-and-sheathing, non-orthogonal-geometry, modular-grids-and-panelization, extending-previous-models) are named by the spawner when the brief or the concept matches their description.

## Cost rules

The token bill of a run is context length times tool calls, per agent, and the rules below follow from that. The baseline is the experiment 15 Fable run (three houses plus terrain in one model, 1296 members, 49 views): the Builder ended at 270k tokens of context after 73 tool calls across three forced restarts, the Designer at 230k after 48 calls plus four resumes for two-line questions, each Inspector at an estimated 100 to 150k after reading all 49 views, the Runner at 31k; every agent ran on the judgement model; four usage-limit cut-offs, each relaunch a cold cache and a 60 to 80k re-read.

1. Mechanical agents run on the mechanical model (the tier table).
2. A fresh Builder per version. A cold start costs about 80k tokens (agent file, skills, API card, hand-off files, the previous script); carrying the previous version's context across the next version's 30 calls costs about 2.4M in cache reads.
3. Resume an agent only when the task needs its context. A two-line question to a resumed 225k-token Designer costs five times a fresh 40k one.
4. Inspectors read subsets in parallel. Image-loads scale with the images already in context; three Inspectors on 17 views each cost under half of one on 49.
5. No Inspector above the pair threshold (20 pairs): orbits only, fix the families, inspect the next version.
6. Changed views only for intermediate versions (`--only`), the full set for the first inspected and the last version of a phase.
7. Lean reads: the Builder never opens `sources.md`; the Researcher returns a verdict table and the Designer opens rows only when a line does not settle it; the Builder reads two sections of this skill, not the file; the Builder patches with Edit instead of rewriting; render logs stay as check lines and the family table; Inspectors return ten lines and leave the tables on disk.
8. Measure: every task notification gives the returning agent's context size and tool calls. CraftBot relays them and puts the totals in rationale section 8, so the next audit has a baseline.

## Multi-variation runs

Only when the brief explicitly asks for several variations of the building. Everything above holds; this section adds a shared stage and one team per variation, so that the Builders hold one house each and the Inspectors read one house each, and the teams run at the same time.

- **Shared stage.** CraftBot writes `brief.md` with the number of variations and what must differ (a section strategy, a structural system, a plan type; the brief says which, else CraftBot decides and records it). One Designer, the shared-stage one, writes `<Agent>/concept_shared.md`: site and terrain with numbers, the plan parti, the materials, the member catalogue, the list of variation strategies, and what every variation shares verbatim. It runs the one research round; `<Agent>/sources.md` serves every team. CraftBot checks the shared concept against the brief and posts it.
- **Teams.** For each variation V, a run folder `<Agent> <V>/` (`Fable A`, `Fable B`, slug `fablea`, `fableb`) with its own `agent.md` (the shared fields plus `- variation: A` and `- team of: Fable`), spawned by CraftBot as one Designer per variation (reads `concept_shared.md` and the verdict table, writes the variation's `concept.md` and `requirements.md`, spawns a Researcher only for a question the shared `sources.md` leaves open) and then fresh Builders per version as in phase 3, each spawning its Inspectors per storey. Version numbering, notes, inspections and close-outs are per team; A can be at v05 while B is at v03. Teams never open each other's folders.
- **CraftBot's concept check.** Each variation `concept.md` against `concept_shared.md` and `brief.md`: the shared numbers identical (terrain, parti, materials, catalogue), the strategy the one assigned, and distinct from the other variations by the brief's criterion. A mismatch goes back to that team's Designer in one message.
- **Shared code.** The terrain and the shared parti are `<Agent>/common_<slug>.py`, written by the first Builder that needs it and read-only afterwards; a change to it is a CraftBot decision, done by one Builder and rendered by every team's next version. The template adds the orchestrator folder to `sys.path` when the run folder name has a variation suffix.
- **Close-out.** `closeout.py version NN vXX --agent "<Agent> <V>"` per team version. One rationale in `<Agent>/` with one section 6 and one iterations table per variation; one callouts file per variation folder (`<Agent> <V>/experiment_NN_<slugv>_callouts.json`, matched against that team's models; its quotes cite the shared rationale, which the exporter copies beside each team's models). `closeout.py run NN --agent "<Agent>"` on the orchestrator folder checks the shared files there, the team files and the callouts file in every variation folder, the prompt file and the transcript. The viewer lists the teams as separate runs of the experiment.
- **What is lost.** No single model holds every variation side by side; the viewer shows them as separate runs. If the brief wants the side-by-side, say so and the run falls back to one team with all variations in one model, which costs what the experiment 15 baseline cost.

## Mechanics: manuals (Researcher)

Read `manuals/INDEX.md` in full. It has one entry per manual: title, extracted `.md` filename, download link, a short description and a table of contents. Narrow down in this order, and stop at the level that settles the question: descriptions, then chapter lists, then the extracted `.md` in full (200 to 900 lines, with a figure index giving PDF page numbers), then the original PDF pages with the Read tool, only the exact pages the figure index or the chapter list names for the question. A PDF lives in `manuals/<filename>.pdf`; if missing, download it from the index link into `manuals/` under that exact filename (`curl -L -o`). If the link is a landing page or a borrow-only item, work from the `.md` and record that the PDF was not consulted. Never copy a manual into `input/`. Adding a new manual (summary plus index entry) is a separate task, not part of a run. Defaults where the source is silent: 1220 x 2440 sheets, metric member sizes from the timber-framing or structural-logic skill, labelled as a derivation.

## Mechanics: building (Builder)

- Start the script from `tools/experiment_template.py` (v01) or the previous version's file (later versions, patched with Edit) and the views from `tools/views_template.py`; read `tools/API.md` for the kits.
- Blender executable: `CRAFTBOT_BLENDER` if set, else the first existing path in `KNOWN_BLENDERS` of `tools/export_all_models.py` (4.3 first). Run it from the Bash tool; a Python subprocess must capture with `encoding="utf-8", errors="replace"`.
- Run every command from the repo root with an absolute output prefix; Blender resolves relative paths against its own cwd.
- Windows shell: write Python files and patch scripts with the Write and Edit tools and run them from a file; a Bash heredoc containing an apostrophe breaks on this machine.
- Render each version with:

```
"<blender>" --background --python tools/render_views.py -- "experiments/<exp>/<Agent>/experiment_NN_<slug>_vXX.py" "<abs repo>/experiments/<exp>/<Agent>/experiment_NN_<slug>_vXX_blender" --views "experiments/<exp>/<Agent>/views_<slug>.py" --lib "experiments/<exp>/input" [--only 01,05]
```

  Quote the paths; a run folder name may contain a space (`Opus 5.1`, `Fable A`). This writes `experiment_NN_<slug>_vXX_blender_view_01.png` and following, saves a `.blend` (gitignored), writes `..._blender_pairs.txt` with every penetrating pair, and prints `OVERLAP CHECK: <n> members, <k> penetrating pairs (> 1 mm)`, the pair families (one row per cause, `tools/triage.py`) and `CONTACT CHECK: <n> members, <f> floating` (members touching nothing, `tools/check_contacts.py`).
- Which views to render: the full set for v01, for the first version under the pair threshold and for the last version of a phase; the four orbits only for a version over the threshold; otherwise `--only` the four orbits plus the views that show the changed families. The notes entry names the views rendered.
- Pair threshold: 20 penetrating pairs. Over it, no Inspector.
- Each rendered version is a new file; never overwrite a version that has renders. Add a view for every new feature in the version that adds it.
- Mandatory views: the four orbits, a frame-only view, a from-below view, an interior view or section per storey; a camera matched to the reference photo when the model is meant to resemble one; a close-up for every joint that needs judgement. Hide lists use bare collection names.
- Inspectors: one per variation when the model holds several, else one per storey, spawned together. Each gets its own views plus the shared ones (the four orbits, the top view, its long section), its requirement lines, and the shared-view checklist: the building sits on its site or strip where the concept puts it; the spacing between variations or storeys is the concept's; the envelope is closed where it should be; nothing stands outside the site. Each returns ten lines; the Builder merges them into `inspection_vXX.md`.

## Mechanics: close-out (Runner, CraftBot)

- Both close-out commands take `--agent "<Agent>"`, the run folder name. Without it the script uses the experiment's only run folder and refuses when there are several, so the Runner always passes it.
- Per version: `python tools/closeout.py version NN vXX --agent "<Agent>"` exports the version (`tools/export_all_models.py`), bakes and audits the layers (`tools/layers.py`; anything in `other` needs an `OVERRIDES` entry keyed by the experiment id), rebuilds `viewer/models/index.json`, checks the view set, confirms the renders and screenshots the viewer, writing `<Agent>/closeout_vXX.md`. In a multi-variation run the agent is the variation folder (`--agent "Fable A"`).
- Per run, after the rationale and callouts are final: `python tools/closeout.py run NN --session-id <id> --agent "<Agent>"` checks the rationale sections, the hand-off files (`agent.md` included; the shared files and every variation folder's team files in a multi-variation run), the prompt file, the callouts (`tools/callouts.py --check`), the API card (`tools/api_card.py --check`), rebuilds the index and copies the transcript as the last step, writing `<Agent>/closeout_run.md`. The session id is the folder name in the scratchpad path (`.../<repo-slug>/<session-id>/scratchpad`); the copy ends just before that command, so it contains the report. `/export` gives the user a markdown copy.
- Callouts need the exported models: `python tools/callouts.py --names NN` lists the element name patterns per run folder (read the rows of this run); the schema is in the header of `tools/callouts.py`; at most 15 callouts, labels at most 80 characters, quotes verbatim inside the named section.
- The three `--only` filters match differently (exporter: substring of the script path; layers: substring of the model path; callouts: substring of the experiment id); the experiment folder name works for all three.
- Viewer check by hand, if needed: `python -m http.server -d viewer 8123`, then a headless Chrome screenshot of `http://127.0.0.1:8123/?model=models/<exp>/<slug>_vXX.json&anim=none` (`--headless=new`, never `--disable-gpu`). A wrong `model` value opens a random showcase model without an error; a red banner is a JavaScript error.

## Final report (CraftBot)

A single message a reader who saw nothing else can follow: the brief as understood (the paragraph from `brief.md`, the same as rationale section 1); the sources used and what each fixed; the versions table (version, change, members, pairs, floating); the final counts; what was verified and what was not (structural adequacy, connections, nailing are never proven by the checks); every file created or changed, by path, including viewer models and index; the cost totals per agent; the commit the user may want to make; anything left open; and that the transcript copy was the last action.

## Outputs of a complete run

```
experiments/<exp>/input/experiment_NN_prompts_<slug>.txt
experiments/<exp>/<Agent>/agent.md                                     agent, slug, model id, mechanical model, harness, date
experiments/<exp>/<Agent>/brief.md, concept.md, sources.md, requirements.md, design_notes.md, version_notes.md
experiments/<exp>/<Agent>/inspection_vXX_<part>.md, inspection_vXX.md, closeout_vXX.md, closeout_run.md
experiments/<exp>/<Agent>/experiment_NN_<slug>_vXX.py                  one per version
experiments/<exp>/<Agent>/experiment_NN_<slug>_vXX_blender_view_YY.png  gitignored renders
experiments/<exp>/<Agent>/views_<slug>.py
experiments/<exp>/<Agent>/experiment_NN_<slug>_design_rationale.md
experiments/<exp>/<Agent>/experiment_NN_<slug>_callouts.json
experiments/<exp>/<Agent>/experiment_NN_<slug>_conversation.jsonl
experiments/<exp>/references/manual_*.png, captions.md                  Researcher snippets
viewer/models/<exp>/<slug>_vXX.json, <slug>_rationale.md, <slug>_callouts.json, index.json updated
tools/layers.py                                                      only if an OVERRIDES entry was needed
manuals/<name>.pdf                                                   only if downloaded during the run; gitignored

multi-variation runs, in addition:
experiments/<exp>/<Agent>/concept_shared.md, common_<slug>.py            shared stage (the orchestrator folder has no versions)
experiments/<exp>/<Agent> <V>/agent.md, concept.md, requirements.md, design_notes.md, version_notes.md, inspections, closeouts
experiments/<exp>/<Agent> <V>/experiment_NN_<slugv>_vXX.py, views_<slugv>.py, experiment_NN_<slugv>_callouts.json
viewer/models/<exp>/<slugv>_vXX.json, <slugv>_rationale.md (a copy of the shared one), <slugv>_callouts.json
```

## Common mistakes

| Mistake | Consequence | Rule |
|---|---|---|
| Reading only the extracted `.md` of a manual | plans and panel schedules in the appendix sheets missed | read the exact PDF pages the figure index names |
| Picking a manual from memory instead of `manuals/INDEX.md` | the chapter that answers the brief sits in a manual you did not think of | index descriptions, then contents, then `.md`, then PDF pages |
| Reading a whole handbook PDF, or a page range around a figure | hundreds of pages of fire and acoustics for two chapters of framing | select chapters from the index contents and exact pages from the `.md` figure index |
| Copying a manual into `input/` | a second copy drifts from `manuals/`, and the PDF gets committed | read from `manuals/`; download missing PDFs there |
| Inverted half-space normal in a clip | member silently missing, overlap check clean | frame-only views for every version; the Inspector reports absence |
| A tread, board or stud that touches nothing | passes the overlap check, fails as a building | the contact check lists it; fix the bearing, not the report |
| Two pieces with the same object name | one overwrites the other without error | name with all loop indices |
| Rendering a fix over an existing version file | the iterations table no longer matches the renders | new version per render batch |
| Trusting the checks alone | absent or void geometry never reported | Inspectors on every version under the pair threshold |
| Spawning an Inspector on a version with hundreds of pairs | a full render set and an Inspector spent on geometry that will move | over the threshold: orbits only, fix the families first |
| One Inspector reading every view | its context carries every earlier image on every call | one Inspector per variation or storey, in parallel, subsets only |
| Resuming a fat agent for a two-line question | the whole context is resent for a small answer | a fresh Designer with the file paths and the question |
| Resuming the Builder across versions | the previous version's script and log ride along on every call | a fresh Builder per version; `version_notes.md` is its memory |
| A hide list with slash paths (`Existing/Shed_Walls`) | hides nothing, the frame-only view shows the cladding | bare collection names; Blender collection names are global |
| Authoring callouts before the export | `--names` and `--check` find no models | export first, callouts after |
| Rationale after the archive | transcript lacks the reasoning the rationale needs | rationale first, transcript last |
| Exporting only the final version | viewer iteration slider shows one step | `closeout.py version` for every version |
| A requirement quietly dropped by the Builder | the model narrows the brief without a record | Designer rewrites, CraftBot decides scope, `brief.md` records it |
| Writing into `Fable/` without checking the model | an Opus or Sonnet run lands in the Fable folder and the viewer lists it as a Fable run | detect the model first, `agent.md` is the first file, folder named after the agent |
| Three variations in one model because the brief said "variations" | the Builder holds three houses and every Inspector reads every view | the multi-variation section: shared stage, then one team per variation |

## Provenance

Assembled from the Fable prompt files of experiments 01-14 (`input/experiment_NN_prompts_fable.txt`), their design rationale documents, and the project notes that accumulated across those runs. The manuals step was added on 2026-09-02 when the reference PDFs moved into `manuals/`. The six-agent team, the hand-off files, the contact check, the triage table and the close-out script were added on 2026-09-06 after the experiment 14 context audit (455 k tokens of context, 68 percent of it screenshots, manuals and code that a single agent read and then needed only in compressed form). The run folder named after the detected model, `agent.md` and the `--agent` flag of the close-out script were added on 2026-09-08 so that the same workflow serves any model, not only Fable. The tiers, the fresh Builder per version, the parallel Inspectors, the pair threshold, the reading table, the cost rules, the structural-logic skill and the multi-variation variant were added on 2026-09-10 after the experiment 15 cost audit (four usage-limit cut-offs in one run; the numbers in "Cost rules").
