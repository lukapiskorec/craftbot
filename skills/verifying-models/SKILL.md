---
name: verifying-models
description: Use when setting up or running the render-inspect-revise loop for a generated model, when an overlap check reports pairs, or when a model looks right but has not been verified.
---

# Verifying models

## Overview

Two verification channels catch disjoint defect classes, and neither substitutes for the other. The numeric overlap check sees penetrations that renders hide; renders see absence that the check is structurally blind to. In one full run, every collision was found by the check and none by the renders, while the one missing-geometry defect survived three iterations until a render view exposed it.

## The numeric channel

- **If a collision check script exists in the repo's tools, use it to verify model intersections; otherwise, check element intersections directly by examining the model file.** The proven form: a separating-axis test over every member pair (face normals plus edge cross products as candidate axes, AABB broad phase), run after every render, at 1 mm tolerance. Touching faces report zero, so legitimate contact (bearing, laps, decks on joists) is not noise. Cheap even at thousands of members.
- **Log two numbers per version: member count and penetrating-pair count.** The pair is the regression metric. A count rising after a feature addition is the expected signal, not a surprise; new element families reopen collisions against every family already present, so budget a fix version after a multi-family addition.
- **Assert buildability constraints on derived values** inside the script (a derived position stays inside its support, a brace clears its rafter), so a later parameter change fails loudly instead of producing a plausible wrong model.
- **A custom check's predicate needs its own debugging pass.** A protrusion test can flag true positives of the literal test that are wrong answers to the question being asked; tighten the predicate against false positives before trusting its zero.

## What the check cannot see

The overlap check is blind to three failure classes: geometry that is absent, geometry that leaves an unintended void, and surfaces that fail to cover what they should. A sign-inverted clipping plane does not make a wrong member, it makes no member, and the check stays clean. Bearing and continuity are never verified by the check either; walk each element's load down to ground by hand once per run (this is how an unsupported deck strip gets found).

## The visual channel

- **Fixed, numbered views, stable across versions**, so view 03 of v01 and v04 are directly comparable.
- The standing set: at least one camera matched to the reference image angle; orthographic elevations and top; frame-only views with sheathing, cladding or repeated members hidden; per-layer plans with the layer above hidden; a from-below view; close-ups of the joints that need judgement.
- **Add a view with every new feature** in the same version that adds the feature; new geometry no view shows is unverified geometry.
- **Close-ups catch what a clean check passes.** A model can score zero overlaps with a truss heel bearing on a cantilever instead of its binder; only the frame-only heel close-up shows it.
- **Section cuts via the camera near-clip plane**: a view carries a cut plane and the renderer sets clip start to it. No boolean cuts, no per-storey collections. Constraint: the clip plane is perpendicular to the view direction, so true sections need camera elevation 0 or plus-minus 90 degrees; a tilted camera tilts the plane and shows facade instead of interior.
- **Render settings serve legibility**: Workbench, object colour per collection, cavity shading, black outlines so coplanar members and sheets stay distinguishable. Fit the camera to the artifact under inspection (a per-view bounding-box fit beats a shared bounding-sphere fit that leaves the model small in the frame).
- **Collections are hiding switches.** Group by structural role in assembly order (foundation, posts, frames, roof framing, sheathing, facade per wall per layer); the diagnostic views are produced by hiding branches, and per-collection colour doubles as the legend.

## Failure signature table

| Symptom | Likely cause |
|---|---|
| Division by zero in an inset formula | Member axis perpendicular to the passed normal |
| Uniform overlaps of exactly half a depth | Placed by centre line instead of bearing surface |
| Overlaps on one side of a symmetric model only | Flipped local axis on mirrored members |
| Members missing or reduced to stubs, check clean | Inverted half-space clip normal |
| Surfaces render dark | Inverted winding, not lighting |
| Hiding a collection does nothing | Bare-name collection reuse across parents |
| Members or courses silently absent, no error | Object name collision overwrote them |
| Wedge gaps at square-cut ends in elevation | Expected contact-on-one-edge joints, not floating members; do not chase |

## Closing a run honestly

State what was verified (no interpenetration, resemblance to reference) and, separately, what was not: structural adequacy, bearing sizes, connection design, nailing. The gap between a clean check and a buildable structure gets written down every time; see writing-design-rationale.

## Provenance

Distilled from all ten Fable design rationale documents (experiments 01-04, 06-09, 11, 13) in the CraftBot repo (https://github.com/lukapiskorec/craftbot); the two-channel principle is stated independently in at least seven of them. The reference implementation of the check is tools/check_overlaps.py in that repo.
