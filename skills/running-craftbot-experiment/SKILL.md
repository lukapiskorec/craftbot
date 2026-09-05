---
name: running-craftbot-experiment
description: Use when asked to run, start, redo, continue or resume a CraftBot experiment in this repository (an experiments/NN_Name/ folder with input/ and optionally references/), whether invoked as /run-experiment or in plain words. The workflow of the six-agent team (CraftBot, Designer, Researcher, Builder, Inspector, Runner), its hand-off files, phases, rules and the repo mechanics. Specific to the CraftBot repo layout, its tools/, skills/, .claude/agents/ and web viewer; not a general-purpose skill.
---

# Running a CraftBot experiment

## Overview

One run turns a brief plus reference materials into versioned Blender Python scripts, renders, a design rationale with callouts, models in the web viewer and an archived transcript. Since experiment 15 the run is done by a team of six agents defined in `.claude/agents/`; the session that receives `/run-experiment` acts as CraftBot, the orchestrator, and spawns the others. The user reads the narration while it runs and a full report at the end. This skill is the shared workflow; each agent's own procedure is in its agent file, and the modelling knowledge lives in the other skills and in `tools/`.

Experiments 01 to 14 were single-agent runs of the same workflow; their outputs have the same shape minus the hand-off files.

## Roles and hand-off files

| Agent | Owns | Reports to | Spawned by | May spawn |
|---|---|---|---|---|
| CraftBot | brief, scope, phases, rationale, report | the user | `/run-experiment` (the session itself) or `claude --agent craftbot` | Designer, Builder, Runner |
| Designer | spatial and construction concept, requirements, design decisions, comparison round, structural review | CraftBot | CraftBot | Researcher, Inspector |
| Researcher | manual selection and extraction, figure snippets, online search on approval | Designer | Designer | none |
| Builder | scripts, views, the render and check loop, version numbering, version notes | CraftBot (progress), Designer (design questions) | CraftBot | Inspector |
| Inspector | visual verification of one version, photo fidelity, comparison table | Builder or Designer | Builder or Designer | none |
| Runner | close-out of every version and of the run | CraftBot | CraftBot (standing, background) | none |

Every hand-off is a file in `experiments/NN_*/Fable/`, so any agent can be restarted from disk and no agent depends on another agent's chat:

| File | Written by | Read by |
|---|---|---|
| `brief.md` | CraftBot | everyone |
| `concept.md` (spatial concept, construction concept, photo rule set) | Designer | Researcher, Builder, Inspector |
| `sources.md` and snippets in `references/` with `captions.md` | Researcher | Designer, Builder |
| `requirements.md` (id, text, source, check method; ticked by the Builder) | Designer | Builder, Inspector, Runner |
| `design_notes.md` (decisions and rejected alternatives, dated by version) | Designer | CraftBot |
| `version_notes.md` (per version: change, counts, families, findings, remaining) | Builder | CraftBot |
| `inspection_vXX.md` | Inspector | Builder, Designer |
| `closeout_vXX.md`, `closeout_run.md` | Runner (via `tools/closeout.py`) | Builder, CraftBot |
| `experiment_NN_fable_vXX.py`, `views_fable.py` | Builder | Runner |
| `experiment_NN_fable_design_rationale.md`, `experiment_NN_fable_callouts.json` | CraftBot | Runner, viewer |
| `input/experiment_NN_prompts_fable.txt` | CraftBot (verbatim appends) | everyone |
| `experiment_NN_fable_conversation.jsonl` | Runner, last action of the run | nobody during the run |

## What the user provides

| Item | Where | Notes |
|---|---|---|
| Experiment folder | `experiments/NN_Name/` | NN = two digits; a bare number in the invocation resolves by globbing `experiments/NN_*` |
| Materials | `input/` | photos, drawings, an inherited script when the brief extends an earlier model |
| Manuals | `manuals/` (repo root, shared) | 17 timber construction manuals as extracted `.md` summaries plus the original PDFs (gitignored, downloadable); `manuals/INDEX.md` is the catalogue |
| Extra references | `references/` (optional) | annotated screenshots, comparison images; the Researcher adds its snippets here |
| The brief | the invocation message | what to build, constraints, iteration limit; may name a manual or a chapter, which is then mandatory |

The user places no code and no prompt files. If the brief is missing, CraftBot derives it from the folder name and the materials, states it, and proceeds; the user can interrupt. When the brief and a material disagree, the brief wins; the conflict is recorded as a deliberate deviation.

## Phases

1. **Set-up (CraftBot).** Prompt file, `brief.md` (the brief as understood, posted to the user), Designer spawned, Runner spawned in the background.
2. **Concept (Designer, Researcher).** `concept.md`, research through one or more Researchers, `requirements.md` and the photo rule set. CraftBot checks the concept against the brief and posts the source-to-rule-to-number table and the deviations before any geometry exists.
3. **Build to the brief (Builder, Inspectors, Runner).** The version loop: write, render, overlap and contact checks, family triage, an Inspector per version, patch. After every rendered version the Builder reports to CraftBot, CraftBot sends the Runner, the Runner's `closeout_vXX.md` is read before the next version. Stops at 0 pairs, 0 floating, nothing open in the inspection, every requirement of the phase ticked or waived. Default limit 10 versions per phase unless the brief says otherwise; at the limit, what remains open is reported.
4. **Comparison and structural review (Designer with an Inspector).** Against the reference (rationale 3b): the last model versus the photos, drawings or figures, as a table (in the reference, in the model, change or kept with reason). Independent of the reference (rationale 6b): load path to ground for every element, lateral stability per direction, bearing, continuity, sizes. Both feed `requirements.md`; the Builder runs the phase-2 versions under the same loop.
5. **User review rounds.** A user message with changes is a new phase: CraftBot appends it verbatim to the prompt file, splits it into scope (its own decision, recorded in `brief.md`), design (Designer) and requirement lines (Designer writes, Builder implements); the round is recorded as rationale section 3c. Push back in one line where a request is a mistake, then do it as asked.
6. **Close-out (CraftBot, Runner).** Rationale compiled from the notes files, callouts written and checked, the Runner's run check, the final report, the transcript archived last.

## Rules

- **Spawning tree** is flat under CraftBot: CraftBot spawns Designer, Builder and Runner; the Designer spawns Researchers and Inspectors; the Builder spawns Inspectors. Researchers and Inspectors are disposable, one per question set or version; their files are the record. The Runner is one standing background agent, continued with messages.
- **Disagreements.** When the Builder cannot meet a requirement, the Designer rewrites the requirement or the concept. When that changes scope, CraftBot decides and records the decision in `brief.md`. The Builder never narrows scope on its own.
- **Research depth.** The Researcher works from the manuals first, in the order index descriptions, chapter lists, extracted `.md`, PDF pages. An online search needs the Designer's approval per request; anything external is labelled in `references/captions.md` and in `sources.md`.
- **Independence.** No agent opens another agent's run folder for the same experiment (`ChatGPT 5.1/` or any other run folder). Common ground is `tools/`, `skills/`, `manuals/`, `input/` and `references/`.
- **Narrate visibly.** Transcripts drop private reasoning. Decisions, rejected alternatives and key numbers go into the notes files and into CraftBot's messages; the rationale is compiled from them.
- **Settle questions from the materials** and state an assumption rather than blocking; questions that change scope go up the tree.
- **Shared code.** The one sanctioned edit to `tools/` during a run is an `OVERRIDES` entry for the experiment in `tools/layers.py`. Promotions of helpers into `tools/` are proposals in `version_notes.md`, done after the run.
- **No commits.** The user commits; CraftBot lists the files.
- **Load skills by their descriptions.** Each agent file lists the skills it reads at startup; the conditional ones (roof-framing-and-sheathing, non-orthogonal-geometry, modular-grids-and-panelization, extending-previous-models) are read when the brief or the concept matches their description.

## Mechanics: manuals (Researcher)

Read `manuals/INDEX.md` in full. It has one entry per manual: title, extracted `.md` filename, download link, a short description and a table of contents. Narrow down in this order, and stop at the level that settles the question: descriptions, then chapter lists, then the extracted `.md` in full (200 to 900 lines, with a figure index giving PDF page numbers), then the original PDF pages with the Read tool (`pages` ranges of at most 20), including every page the figure index points to. A PDF lives in `manuals/<filename>.pdf`; if missing, download it from the index link into `manuals/` under that exact filename (`curl -L -o`). If the link is a landing page or a borrow-only item, work from the `.md` and record that the PDF was not consulted. Never copy a manual into `input/`. Adding a new manual (summary plus index entry) is a separate task, not part of a run. Defaults where the source is silent: 1220 x 2440 sheets, metric member sizes from the timber-framing skill, labelled as a derivation.

## Mechanics: building (Builder)

- Start the script from `tools/experiment_template.py` and the views from `tools/views_template.py`; read `tools/API.md` for the kits.
- Blender executable: `CRAFTBOT_BLENDER` if set, else the first existing path in `KNOWN_BLENDERS` of `tools/export_all_models.py` (4.3 first). Run it from the Bash tool; a Python subprocess must capture with `encoding="utf-8", errors="replace"`.
- Run every command from the repo root with an absolute output prefix; Blender resolves relative paths against its own cwd.
- Windows shell: write Python files and patch scripts with the Write tool and run them from a file; a Bash heredoc containing an apostrophe breaks on this machine.
- Render each version with:

```
"<blender>" --background --python tools/render_views.py -- "experiments/<exp>/Fable/experiment_NN_fable_vXX.py" "<abs repo>/experiments/<exp>/Fable/experiment_NN_fable_vXX_blender" --views "experiments/<exp>/Fable/views_fable.py" --lib "experiments/<exp>/input" [--only 01,05]
```

  This writes `experiment_NN_fable_vXX_blender_view_01.png` and following, saves a `.blend` (gitignored), writes `..._blender_pairs.txt` with every penetrating pair, and prints `OVERLAP CHECK: <n> members, <k> penetrating pairs (> 1 mm)`, the pair families (one row per cause, `tools/triage.py`) and `CONTACT CHECK: <n> members, <f> floating` (members touching nothing, `tools/check_contacts.py`).
- Each rendered version is a new file; never overwrite a version that has renders. Add a view for every new feature in the version that adds it.
- Mandatory views: the four orbits, a frame-only view, a from-below view, an interior view or section per storey; a camera matched to the reference photo when the model is meant to resemble one; a close-up for every joint that needs judgement. Hide lists use bare collection names.

## Mechanics: close-out (Runner, CraftBot)

- Per version: `python tools/closeout.py version NN vXX` exports the version (`tools/export_all_models.py`), bakes and audits the layers (`tools/layers.py`; anything in `other` needs an `OVERRIDES` entry keyed by the experiment id), rebuilds `viewer/models/index.json`, checks the view set, confirms the renders and screenshots the viewer, writing `Fable/closeout_vXX.md`.
- Per run, after the rationale and callouts are final: `python tools/closeout.py run NN --session-id <id>` checks the rationale sections, the hand-off files, the prompt file, the callouts (`tools/callouts.py --check`), the API card (`tools/api_card.py --check`), rebuilds the index and copies the transcript as the last step, writing `Fable/closeout_run.md`. The session id is the folder name in the scratchpad path (`.../<repo-slug>/<session-id>/scratchpad`); the copy ends just before that command, so it contains the report. `/export` gives the user a markdown copy.
- Callouts need the exported models: `python tools/callouts.py --names NN` lists the element name patterns; the schema is in the header of `tools/callouts.py`; at most 15 callouts, labels at most 80 characters, quotes verbatim inside the named section.
- The three `--only` filters match differently (exporter: substring of the script path; layers: substring of the model path; callouts: substring of the experiment id); the experiment folder name works for all three.
- Viewer check by hand, if needed: `python -m http.server -d viewer 8123`, then a headless Chrome screenshot of `http://127.0.0.1:8123/?model=models/<exp>/fable_vXX.json&anim=none` (`--headless=new`, never `--disable-gpu`). A wrong `model` value opens a random showcase model without an error; a red banner is a JavaScript error.

## Final report (CraftBot)

A single message a reader who saw nothing else can follow: the brief as understood (the paragraph from `brief.md`, the same as rationale section 1); the sources used and what each fixed; the versions table (version, change, members, pairs, floating); the final counts; what was verified and what was not (structural adequacy, connections, nailing are never proven by the checks); every file created or changed, by path, including viewer models and index; the commit the user may want to make; anything left open; and that the transcript copy was the last action.

## Outputs of a complete run

```
experiments/<exp>/input/experiment_NN_prompts_fable.txt
experiments/<exp>/Fable/brief.md, concept.md, sources.md, requirements.md, design_notes.md, version_notes.md
experiments/<exp>/Fable/inspection_vXX.md, closeout_vXX.md, closeout_run.md
experiments/<exp>/Fable/experiment_NN_fable_vXX.py                  one per version
experiments/<exp>/Fable/experiment_NN_fable_vXX_blender_view_YY.png  gitignored renders
experiments/<exp>/Fable/views_fable.py
experiments/<exp>/Fable/experiment_NN_fable_design_rationale.md
experiments/<exp>/Fable/experiment_NN_fable_callouts.json
experiments/<exp>/Fable/experiment_NN_fable_conversation.jsonl
experiments/<exp>/references/manual_*.png, captions.md                 Researcher snippets
viewer/models/<exp>/fable_vXX.json, fable_rationale.md, fable_callouts.json, index.json updated
tools/layers.py                                                      only if an OVERRIDES entry was needed
manuals/<name>.pdf                                                   only if downloaded during the run; gitignored
```

## Common mistakes

| Mistake | Consequence | Rule |
|---|---|---|
| Reading only the extracted `.md` of a manual | plans and panel schedules in the appendix sheets missed | read the PDF pages too |
| Picking a manual from memory instead of `manuals/INDEX.md` | the chapter that answers the brief sits in a manual you did not think of | index descriptions, then contents, then `.md`, then PDF |
| Reading a whole handbook PDF | hundreds of pages of fire and acoustics for two chapters of framing | select chapters from the index contents and the `.md` figure index |
| Copying a manual into `input/` | a second copy drifts from `manuals/`, and the PDF gets committed | read from `manuals/`; download missing PDFs there |
| Inverted half-space normal in a clip | member silently missing, overlap check clean | frame-only views for every version; the Inspector reports absence |
| A tread, board or stud that touches nothing | passes the overlap check, fails as a building | the contact check lists it; fix the bearing, not the report |
| Two pieces with the same object name | one overwrites the other without error | name with all loop indices |
| Rendering a fix over an existing version file | the iterations table no longer matches the renders | new version per render batch |
| Trusting the checks alone | absent or void geometry never reported | an Inspector on every version |
| A hide list with slash paths (`Existing/Shed_Walls`) | hides nothing, the frame-only view shows the cladding | bare collection names; Blender collection names are global |
| Authoring callouts before the export | `--names` and `--check` find no models | export first, callouts after |
| Rationale after the archive | transcript lacks the reasoning the rationale needs | rationale first, transcript last |
| Exporting only the final version | viewer iteration slider shows one step | `closeout.py version` for every version |
| A requirement quietly dropped by the Builder | the model narrows the brief without a record | Designer rewrites, CraftBot decides scope, `brief.md` records it |

## Provenance

Assembled from the Fable prompt files of experiments 01-14 (`input/experiment_NN_prompts_fable.txt`), their design rationale documents, and the project notes that accumulated across those runs. The manuals step was added on 2026-09-02 when the reference PDFs moved into `manuals/`. The six-agent team, the hand-off files, the contact check, the triage table and the close-out script were added on 2026-09-06 after the experiment 14 context audit (455 k tokens of context, 68 percent of it screenshots, manuals and code that a single agent read and then needed only in compressed form).
