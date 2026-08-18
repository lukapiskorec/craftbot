# CraftBot

CraftBot is a research project exploring whether large language models can participate meaningfully in architectural design when constrained to operate through executable CAD code. Instead of producing meshes or images, the LLM writes Python scripts that construct architectural geometry in Blender, refined through an iterative loop of code generation, execution, visual feedback, and revision.

A draft paper describing the project is in [`papers/`](papers/):

> *CraftBot: An LLM Interlocutor in a Code-First Approach to Architectural Design* (short paper, submitted to ICCC 2026)

## Repository structure

```
papers/         Draft paper PDF
experiments/    13 experiments, one folder each
tools/          Helper scripts for running experiments
outputs/        Default folder for headless renders (gitignored)
```

Each experiment folder follows the same layout:

- `input/` — everything given to the model: the prompt log (`experiment_XX_prompts_chatgpt51.txt`), reference PDFs/images, and the shared Python geometry library (`craftbot_lib.py`) with an element placement template
- `ChatGPT 5.1/` — outputs per iteration: generated Python scripts (`vXX.py`) and Blender viewport screenshots of the resulting models
- `references/` (some experiments) — additional reference and annotation images used during the iteration loop

## Experiments

All experiments were run with ChatGPT 5.1 (November 2025 – January 2026), grouped by the type of reference material used:

**Visual references** — 01 Carport (king post truss), 02 Gothic Carport (hammer beam truss), 03 VIPP Shelter, 06 Prouvé 6x6 Demountable House

**Hybrid references (images + text)** — 04 Construction Manual (prefabricated timber house), 05 Construction Manual Meta-Prompt, 07 Gehry Deconstruction, 08 The Segal Method, 09 How to CLT (ten-story building), 10 Staircase, 11–13 Hip Roof / Dormer Window / Roof Sheathing

## Headless execution

Experiment scripts can be executed without opening the Blender GUI using [`tools/run_experiment_headless.py`](tools/run_experiment_headless.py). The wrapper runs an experiment script in background Blender, frames the generated geometry with an orthographic (parallel) camera so the whole model is always visible, renders four orbit views with the Workbench engine (visually similar to solid-mode viewport screenshots), and saves the resulting `.blend` file:

```
blender --background --python tools/run_experiment_headless.py -- <experiment.py> <lib_dir> [out_dir]
```

- `<experiment.py>` — path to the experiment script to execute
- `<lib_dir>` — folder containing `craftbot_lib.py` (the experiment's `input/` folder)
- `[out_dir]` — optional output folder for `view_1..4.png` and `model.blend`; defaults to `outputs/<experiment_name>/` (gitignored)

Example (Windows):

```
"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" --background --python tools\run_experiment_headless.py -- "experiments\01_Carport_Assembly_Blender_Python\ChatGPT 5.1\experiment_01_chatgpt51_v01.py" "experiments\01_Carport_Assembly_Blender_Python\input"
```

## Notes

- Original ChatGPT conversation logs are not yet included; they may be added later.
- This README will be updated as the research progresses.

## About

The project author is Luka Piškorec, previously a lecturer at Aalto University and researcher at ETH Zürich. He is a co-founder of TEN Studio (Zürich and Belgrade) and {protocell:labs} (Helsinki), practices that work at an intersection of architecture, design, digital art and research.

The project is part of [art-ai-fact](https://www.aalto.fi/en/research-art/art-ai-fact) initiative funded by Aalto University in 2025-2026.
