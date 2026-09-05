---
name: writing-design-rationale
description: Use at the end of every experiment run, before archiving the session transcript, to record decisions, deviations, iterations, and verification honestly.
---

# Writing design rationale

## Overview

The rationale is the mechanism by which a run's knowledge survives. Session transcripts drop the model's private reasoning; only messages, tool calls and results remain. So the rationale is written at the end of the run while the reasoning is still in context, and the transcript is archived last.

## Template

Section table proven across multiple runs (numbering from experiment 14 on;
experiments 13 and earlier lack section 1 and number the rest one lower):

0. About this document
1. Brief as understood: the task in one paragraph as the run read it, written before any source is opened and kept verbatim from the first message of the run; what is built, what is preserved, what is dropped and why. A reader who sees nothing else should be able to judge the model against it.
2. How to run / outputs: render command, the named view list, the collection tree, member and overlap counts
3. Reading the inputs: the source-to-rule-to-number mapping table, then deliberate deviations
3b. Comparison round: figure-by-figure or photo-vs-model diff table (in the reference / in the model / change or kept-with-reason)
3c. User review round (when the user sends changes after a phase): request, change, where; what was pushed back on and how it was resolved
4. Reading the reference code: what was inherited, what it constrains
5. What had to change / construction logic settled before geometry
6. Core modelling decisions, each with alternatives considered and rejected
6b. Independent structural improvements (the review that ignores the reference)
7. Detailed geometry numbers
8. Verification: what the checks prove, and a separate "Not verified" list
9. Iterations table: one row per version, the change, and what the renders or checks showed
10. Scope and known simplifications

## What must be recorded

- **The brief as understood** (section 1), including the reading of any ambiguity in the invocation and every material the brief overrides. When a later phase changes the brief, append to the paragraph rather than rewriting it, so the history of readings stays visible.
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

Template established in experiment 13 and adopted by later runs; section 1 (brief as understood) and 3c (user review round) added in experiment 14 at the user's request; recording principles stated independently in all ten Fable design rationale documents in the CraftBot repo (https://github.com/lukapiskorec/craftbot).
