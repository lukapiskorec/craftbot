---
name: reading-visual-references
description: Use when the reference material for an experiment is photographs, drawings, or floor plans rather than (or alongside) a dimensioned manual, and dimensions or topology must be read off images.
---

# Reading visual references

## Overview

Images answer different questions than documents do, and different images answer different questions than each other. The recurring failure is asking an image for something it cannot say (a plan for pane counts, a photo for absolute dimensions) and building confidently on the guess.

## Assign each image a role before measuring

- **Plans and drawings give extents and modules**: overall rectangle, module sizes, drainage direction, grid.
- **Photographs give topology, counts, orientation and proportion**: bay counts, panel splits, whether a volume is solid or open, which way a frame's legs spread, member slenderness, cladding direction.
- Interior photos are data too: one interior shot can reveal that a light well is in fact an open shaft.
- A photo settles orientation that a drawing leaves ambiguous, but cross-check the reading against statics before accepting it.

Never mix roles. Asking a plan how many panes a window has wastes a round.

## Getting dimensions out of an unscaled image

- **Calibrate off a known object**: a person (about 1.75 m), a door, a standard timber section, a scale bar. Record the calibration constant (1.75 m over 255 px gives about 145 px/m) so later comparison passes reuse the same scale.
- **Derive repeat spacings by counting** members across a calibrated span, not by measuring one bay.
- **Read pitch off the member line directly** and round to a plausible construction angle (51 degrees measured, 50 used).

## When there is no manual at all

Fix dimensions in this order, and say which is which in the rationale:

1. Topology and counts from the images (bay count, truss type, brace positions).
2. Absolute dimensions from the building program (a two-car carport gives a 6 m span).
3. Member sections from named standard practice, chosen as a consistent family, not one at a time ("standard Scandinavian/N-American sections" gives 50 x 150 studs at 600 centres).

## Two-pass reading

Read full-frame first and build the whole model from what the images agree on at that scale. Only then crop and upscale the details the model is weakest at (eave, gable, apex). The close read is productive second because by then you know which details matter and where the model is guessing. A stronger variant compresses the first pass into a short numbered rule set (found object, deck level, wall geometry, roof geometry, openings) and traces every later decision to one of those rules, which keeps a photo-driven model from drifting into free invention.

## The comparison round

After the model stands, re-measure it against the reference at the same calibration and tabulate the deltas. Give every difference one of three verdicts: within a stated tolerance (about 0.1 m works at building scale), fix, or out of scope for the modelling vocabulary. The "kept" rows carry reasons (an eave detail is worth keeping unfaithful when matching it would raise the whole roof and the detail is hidden anyway). This is what separates "did not notice" from "noticed and chose otherwise".

## Material substitution

When the reference building uses materials outside the experiment's palette, substitute honestly and write it down. Match the massing and bay rhythm, let member depth follow from span, and state where the two disagree rather than drawing an impossible section. A timber ring beam standing in for a steel edge will read visibly heavier than the original, and the rationale says so; corrugated metal can become open-jointed vertical boards that keep the same visual grain.

## Provenance

Distilled from the Fable design rationale documents of experiments 01, 02, 03, 06 and 07 in the CraftBot repo (https://github.com/lukapiskorec/craftbot).
