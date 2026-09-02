---
name: running-craftbot-experiment
description: Use when asked to run, start, redo, continue or resume a CraftBot experiment in this repository (an experiments/NN_Name_Blender_Python/ folder with input/ and optionally references/), whether invoked as /run-experiment or in plain words. Specific to the CraftBot repo layout, its tools/, skills/ and web viewer; not a general-purpose skill.
---

# Running a CraftBot experiment

## Overview

One run turns a brief plus reference materials into versioned Blender Python scripts, renders, a design rationale with callouts, models in the web viewer and an archived transcript. The agent works on its own from start to finish; the user reads the narration while it runs and a full report at the end. This skill is the repo-specific workflow; the general modelling knowledge lives in the other skills and the code in `tools/`.

## What the user provides

| Item | Where | Notes |
|---|---|---|
| Experiment folder | `experiments/NN_Name_Blender_Python/` | NN = two digits; a bare number in the invocation resolves by globbing `experiments/NN_*` |
| Materials | `input/` | photos, drawings, an inherited script when the brief extends an earlier model |
| Manuals | `manuals/` (repo root, shared by all experiments) | 17 timber construction manuals as extracted `.md` summaries plus the original PDFs (gitignored, downloadable); `manuals/INDEX.md` is the catalogue. Runs before 2026-09-02 kept their manual in `input/`; a `original_pdf_provenance.txt` there says which one. |
| Extra references | `references/` (optional) | annotated screenshots, comparison images |
| The brief | the invocation message | what to build, constraints, iteration limit; may name a manual or a chapter, which is then mandatory |

The user places no code and no prompt files; the agent writes the prompt file itself (step 0). If the brief is missing, derive it from the folder name and the materials, state it in the first message, and proceed; the user can interrupt. When the brief and a material disagree (a photo of a different roof type than the brief names), the brief wins; record the conflict as a deliberate deviation and use the material only for what still applies (joints, member proportions, bracing idiom).

## Rules for the whole run

- **Independence.** Never open another agent's scripts for the same experiment (`ChatGPT 5.1/` or any other run folder). Common ground is `tools/`, `skills/`, `manuals/`, `input/` and `references/` only.
- **Narrate visibly.** Transcripts drop the model's private reasoning. Write decisions, rejected alternatives and key numbers into messages as you go; they become the rationale.
- **Settle questions from the materials.** Consult the manuals and images before asking; state an assumption and continue rather than blocking.
- **Manuals stay in `manuals/`.** Read them there; never copy a PDF or an extracted `.md` into `input/`. A PDF downloaded during a run lands in `manuals/` under the filename the index gives and is gitignored. Adding a new manual (summary plus index entry) is a separate task, not part of a run.
- **Run every command from the repo root.** Blender resolves relative paths against its own cwd, so the output prefix is always absolute.
- **Blender executable.** `CRAFTBOT_BLENDER` if set, else the first existing path in `KNOWN_BLENDERS` of `tools/export_all_models.py` (4.3 first); write that path into the render command. Run it from the Bash tool; if you wrap it in a Python subprocess instead, capture with `encoding="utf-8", errors="replace"` or cp1252 decoding crashes.
- **Windows shell.** Write Python files and patch scripts with the Write tool and run them from a file: Bash heredocs containing an apostrophe break on this machine.
- **Shared code.** The one sanctioned edit to `tools/` during a run is an `OVERRIDES` entry for this experiment in `tools/layers.py` (step 6). Promote a helper into `tools/` only after the run, as a separate proposal.
- **No commits.** The user commits; list the files for them instead.
- **Load the other skills by their descriptions** before the step that needs them: working-from-reference-documents, reading-visual-references, procedural-geometry, non-orthogonal-geometry, timber-framing, roof-framing-and-sheathing, modular-grids-and-panelization, extending-previous-models, verifying-models, writing-design-rationale.

## Steps

### 0. Set up

1. Write `input/experiment_NN_prompts_fable.txt` with the invocation message verbatim; append later instructions as they arrive.
2. Create `Fable/`. If it already exists with versions, this is a continuation: read the highest `experiment_NN_fable_vXX.py`, the rationale if present, and resume the numbering.
3. Read `tools/README.md`; the kits there are the starting point for all geometry.

### 1. Select the manuals

Read `manuals/INDEX.md` in full. It has one entry per manual: title, extracted `.md` filename, download link, a short description and a table of contents. Narrow down in this order, and stop at the level that settles the question:

1. Descriptions: pick every manual whose description touches the brief (building type, structural system, region, level of detail). A brief that names a manual or chapter makes that one mandatory.
2. Table of contents: within the picked manuals, pick the chapters; most manuals contribute one or two chapters, and an 800-page handbook is never read whole.
3. Extracted `.md`: read the chosen manuals' summaries in full (they are 200 to 900 lines); they carry the numbers, rules, build sequences and a figure index with PDF page numbers.
4. Original PDF: open the pages of the chosen chapters with the Read tool (`pages` ranges of at most 20), plus every page the figure index points to. Drawn details, appendix sheets and span tables live only there.

For the PDF, check `manuals/<filename>.pdf` first; if it is missing, download it from the link in the index entry into `manuals/` under that exact filename (`curl -L -o`). If the link is a landing page or a borrow-only item and no download is possible, work from the extracted `.md` and record in the rationale that the PDF was not consulted. Post the selection in the first message: manual, chapters, why, and whether the PDF was available.

### 2. Read the inputs

Read every file in `input/` and `references/` (every image, any drawing or script), then the selected manual chapters as above: the extracted `.md` first, then the PDF pages (the appendix sheets carry plans and panel dimensions that the extracted `.md` loses). Post the source-to-rule-to-number table (manual, figure or clause, the rule it gives, the number used) and the list of deliberate deviations before writing geometry. This table is rationale section 2. Defaults where the source is silent: 1220 x 2440 sheets, metric member sizes from the timber-framing skill, labelled as your derivation.

### 3. Set up the run files

| File | Purpose |
|---|---|
| `Fable/experiment_NN_fable_v01.py` | the model script; start from `tools/experiment_template.py` (one parameter block, derived levels as functions, members in named collections by structural role, element count printed at the end) |
| `Fable/views_fable.py` | copy of `tools/views_template.py`, edited: the four orbits, a frame-only view and a from-below view are mandatory; elevations, top, section cuts, a camera matched to the reference photo (when the model is meant to resemble one) and joint close-ups as the model needs them. Number once, keep stable across versions, append only. |

The old per-experiment `render_fable.py` files are the pre-tools renderer; only their `VIEWS` lists are worth copying.

Render each version with:

```
"<blender>" --background --python tools/render_views.py -- "experiments/<exp>/Fable/experiment_NN_fable_vXX.py" "<abs repo>/experiments/<exp>/Fable/experiment_NN_fable_vXX_blender" --views "experiments/<exp>/Fable/views_fable.py" --lib "experiments/<exp>/input" [--only 01,05]
```

This writes `experiment_NN_fable_vXX_blender_view_01.png` and following, saves a `.blend` (gitignored) and prints `OVERLAP CHECK: <n> members, <k> penetrating pairs (> 1 mm)`.

### 4. Iterate (phase 1: build to the brief)

Loop: write the script, render, open every view PNG with the Read tool, read the overlap line, fix, repeat. Each rendered version is a new file; never overwrite a version that has renders. Add a view for every new feature in the version that adds it. Per version, post one message: what changed, what the renders showed, member count and penetrating pairs. Stop when the brief is met, the renders show no missing or misplaced geometry, and the check reports 0 pairs at 1 mm. Default limit 10 versions per phase unless the brief says otherwise; if the limit is reached, say what remains open.

### 5. Iterate (phase 2: comparison and structural review)

Runs automatically once phase 1 converges; post a phase-boundary message first. Two reviews, then more versions under the same loop and limit:

- **Against the reference** (rationale section 2b). Compare the last model with the photos, drawings or figures in `input/` and `references/`: plan layout, connection details, element dimensions and positions. Table: in the reference, in the model, change or kept with reason. When the reference shows a different building, state the mismatch in one line and limit the table to what transfers; when nothing transfers, skip it.
- **Independent of the reference** (rationale section 5b). Review the model as a structure: load path to ground for every element, bearing, bracing, continuity, member sizes. List improvements with the reason for each.

### 6. Close out, in this order

1. Write `Fable/experiment_NN_fable_design_rationale.md` following writing-design-rationale; section 0 of `experiments/13_Hip_Roof_Sheathing_Blender_Python/Fable/experiment_13_fable_design_rationale.md` is the template, with 2b and 5b added for the phase-2 tables. One document only.
2. Export every version to the viewer: `python tools/export_all_models.py --only NN_` (Blender runs each `Fable/experiment_NN_fable_vXX.py`; the rationale is copied and `index.json` rebuilt).
3. `python tools/layers.py --audit --only NN`. If any name family lands in `other`, add an `OVERRIDES` entry keyed `"NN"` in `tools/layers.py` and run `python tools/layers.py --bake --only NN`.
4. Callouts, which need the exported models: `python tools/callouts.py --names NN` lists the element name patterns; write `Fable/experiment_NN_fable_callouts.json` (schema in the header of `tools/callouts.py`: each callout names element patterns and a numbered rationale section; the verbatim quote is optional but makes the tag jump to the passage); `python tools/callouts.py --check --only NN`; then `python tools/export_all_models.py --index-only` to copy the callouts next to the models.
5. Viewer check: start `python -m http.server -d viewer 8123` in the background, then

   ```
   timeout 60 "C:/Program Files/Google/Chrome/Application/chrome.exe" --headless=new --hide-scrollbars --window-size=1600,1000 --screenshot="<scratchpad>/viewer_NN.png" --virtual-time-budget=6000 "http://127.0.0.1:8123/?model=models/<exp>/fable_vXX.json&anim=none"
   ```

   and Read the PNG, then stop the server. The `model` parameter is the model file path as listed in `viewer/models/index.json`; a wrong value opens a random showcase model without any error. A red banner is a JavaScript error. Never `--disable-gpu` (its software renderer hangs).
6. Post the final report (below).
7. Archive the transcript as the very last action: the session id is the folder name in the scratchpad path (`.../<repo-slug>/<session-id>/scratchpad`, repo slug `C--Users-lukap-Documents-GitHub-craftbot`); copy `~/.claude/projects/<repo-slug>/<session-id>.jsonl` to `Fable/experiment_NN_fable_conversation.jsonl`. The copy ends just before this command, so it contains the report. Remind the user that `/export` gives a markdown copy.

The three `--only` filters match differently (exporter: substring of the script path; layers: substring of the model path; callouts: substring of the experiment id); `NN_` and `NN` as written work for all three.

## Final report

A single message a reader who saw nothing else can follow: the brief as understood; the sources used and what each fixed; the versions table (version, change, members, pairs); the final counts; what was verified and what was not (structural adequacy, connections, nailing are never proven by the check); every file created or changed, by path, including viewer models and index; the commit the user may want to make; anything left open; and that the transcript copy follows as the last step.

## Outputs of a complete run

```
experiments/<exp>/input/experiment_NN_prompts_fable.txt
experiments/<exp>/Fable/experiment_NN_fable_vXX.py                  one per version
experiments/<exp>/Fable/experiment_NN_fable_vXX_blender_view_YY.png  gitignored renders
experiments/<exp>/Fable/views_fable.py
experiments/<exp>/Fable/experiment_NN_fable_design_rationale.md
experiments/<exp>/Fable/experiment_NN_fable_callouts.json
experiments/<exp>/Fable/experiment_NN_fable_conversation.jsonl
viewer/models/<exp>/fable_vXX.json, fable_rationale.md, fable_callouts.json, index.json updated
tools/layers.py                                                      only if an OVERRIDES entry was needed
manuals/<name>.pdf                                                   only if downloaded during the run; gitignored, nothing to commit
```

## Common mistakes

| Mistake | Consequence | Rule |
|---|---|---|
| Reading only the extracted `.md` of a manual | plans and panel schedules in the appendix sheets missed | read the PDF pages too |
| Picking a manual from memory instead of `manuals/INDEX.md` | the chapter that answers the brief sits in a manual you did not think of | index descriptions, then contents, then `.md`, then PDF |
| Reading a whole handbook PDF | hundreds of pages of fire and acoustics for two chapters of framing | select chapters from the index contents and the `.md` figure index |
| Copying a manual into `input/` | a second copy drifts from `manuals/`, and the PDF gets committed | read from `manuals/`; download missing PDFs there |
| Inverted half-space normal in a clip | member silently missing, overlap check clean | frame-only views for every version |
| Two pieces with the same object name | one overwrites the other without error | name with all loop indices |
| Rendering a fix over an existing version file | the iterations table no longer matches the renders | new version per render batch |
| Trusting the check alone | absent or void geometry never reported | look at every view |
| Authoring callouts before the export | `--names` and `--check` find no models | export first, callouts after |
| Rationale after the archive | transcript lacks the reasoning the rationale needs | rationale first, transcript last |
| Exporting only the final version | viewer iteration slider shows one step | `--only NN_` exports every version |

## Provenance

Assembled from the Fable prompt files of experiments 01-13 (`input/experiment_NN_prompts_fable.txt`), their design rationale documents, and the project notes that accumulated across those runs. The manuals step was added on 2026-09-02 when the reference PDFs moved out of the experiment folders into `manuals/`.
