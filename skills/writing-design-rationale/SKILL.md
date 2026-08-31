---
name: writing-design-rationale
description: Use at the end of every experiment run, before archiving the session transcript, to record decisions, deviations, iterations, and verification honestly.
---

# Writing design rationale

## Overview

The rationale is the mechanism by which a run's knowledge survives. Session transcripts drop the model's private reasoning; only messages, tool calls and results remain. So the rationale is written at the end of the run while the reasoning is still in context, and the transcript is archived last.

## Template

Section table proven across multiple runs:

0. About this document
1. How to run / outputs: render command, the named view list, the collection tree, member and overlap counts
2. Reading the inputs: the source-to-rule-to-number mapping table, then deliberate deviations
2b. Comparison round: figure-by-figure or photo-vs-model diff table (in the reference / in the model / change or kept-with-reason)
3. Reading the reference code: what was inherited, what it constrains
4. What had to change / construction logic settled before geometry
5. Core modelling decisions, each with alternatives considered and rejected
5b. Independent structural improvements (the review that ignores the reference)
6. Detailed geometry numbers
7. Verification: what the checks prove, and a separate "Not verified" list
8. Iterations table: one row per version, the change, and what the renders or checks showed
9. Scope and known simplifications

## What must be recorded

- **Deliberate deviations** from the reference, each with its cause and the rejected alternative named. This is what lets a reviewer separate "did not notice" from "noticed and chose otherwise".
- **Considered and not changed**, with reasons, so the next iteration does not re-litigate settled questions. A floor build-up rejected because modelling it would shift every level for no structural information is one sentence that saves the next run a day.
- **Rejected geometry variants with the symptom that killed each**, including attempts abandoned on paper. This turns an iteration log into reusable knowledge instead of a changelog.
- **Not verified, separate from out of scope.** Structural adequacy, bearing, nailing and connection design are never proven by the overlap check and views; quantify residual approximations where possible (each drop and offset in millimetres). Nothing unverified is presented as verified.
- **The fidelity boundary**: what is absent, what is present only as texture, which member sizes are plausible rather than calculated.

## Style rules

- Argue structural additions by load path, not appearance.
- Give every number its datum and its source (reference clause, derivation, or assumption).
- Label your own derivations as yours, never as sourced (see working-from-reference-documents).
- The iterations table carries the two regression numbers (members, penetrating pairs) per version.

## Provenance

Template established in experiment 13 and adopted by later runs; recording principles stated independently in all ten Fable design rationale documents in the CraftBot repo (https://github.com/lukapiskorec/craftbot).
