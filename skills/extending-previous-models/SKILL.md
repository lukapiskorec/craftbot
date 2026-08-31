---
name: extending-previous-models
description: Use when an experiment continues, layers onto, remodels, or compares against a previous experiment's model or script (inherited geometry, sheathing over an existing frame, deconstruction of an earlier building).
---

# Extending previous models

## Overview

An inherited model is a found object: it comes in verbatim, gets changed only through explicit, auditable moves, and is expected to need fixing where the new work touches it.

## Taking over a model

- **Bring the old script in unchanged and list every change as old / change / why.** Ad hoc edits make it impossible to tell what stayed found and what was deliberately changed.
- **Audit the interface before generating anything.** The brief may say "add sheathing", but if the inherited frame makes a clean result impossible (hips standing proud of the board plane), correcting the frame is in scope; "no geometric inconsistencies" is the real requirement. List each conflict with its measured excess.
- **Override single members by re-creating them by name.** If the element-creation helper replaces an existing object of the same name, a short override pass after the inherited script runs can rebuild exactly the wrong members (and their dependents, under the same names) without forking a thousand-line script.
- **Derive inherited dimensions with the source's own functions, never by hand.** Re-deriving a dimension by hand and forgetting one term produces a design built on the wrong number. Replicate the original computation in a helper both scripts share; export helpers, not magic numbers.
- **Collection and object names are global.** Merging two scripts collides namespaces silently; prefix the new work.

## Using what earlier runs learned

- **Read prior runs' failure notes and design around them.** A note that an earlier run struggled with corner studs on twisted walls justifies designing a single corner post from the start. A known-hard junction is cheap intelligence: convert it into a design constraint before writing geometry rather than rediscovering it through overlap failures.
- **The reference adjudicates against the prior run.** When continuing another agent's model, do not inherit its choices by default; check them against the reference and name the figure that settles it (board direction on hip facets is a real example: the earlier run ran boards up-slope, the source's figure says parallel to the eaves).
- **Carry the geometry toolkit forward and extend it**; name the inherited kit and the additions separately, and promote helpers that a second building has needed into a shared library.
- **Keep parallel agent runs independent.** When two agents attempt the same brief for comparison, do not read the other agent's scripts; only the shared library and template are common ground.

## Provenance

Distilled from the Fable design rationale documents of experiments 03, 06, 07 and 13 in the CraftBot repo (https://github.com/lukapiskorec/craftbot).
