---
name: working-from-reference-documents
description: Use when an experiment is grounded in a construction manual, design guide, or standard (typically a summarized md document with a source PDF behind it) and the model must stay traceable to it.
---

# Working from reference documents

## Overview

Fidelity to a reference is an auditable property, not a feeling. Every number in the model should trace back to a clause in the source, and every departure should be written down with its reason. Successful runs converge on the same two-phase shape: build from the extracted rules first, then diff the finished-looking model against the source's figures and photographs.

## The mapping table comes first

Before any geometry, write a table with one row per rule taken from the reference:

| Source (section / figure / page) | Rule taken | Value and code symbol in the model |

Every constant in the script traces forward to a rule; every clause with no row is visibly unimplemented. Where the source gives a range (say, exterior walls 140-200 mm), the row records which end was picked and why. This turns "did we follow the reference" into a table read instead of a judgement call.

## Rules for taking numbers

- **A dimension is meaningless without its datum.** Establish which face or centreline a number is measured to before building on it, and cross-check headline dimensions against a second sheet. A footprint read as the platform edge can turn out to be the wall line on a larger platform, and the misread propagates into posts, trusses and the whole plan.
- **Distinguish primitive values from derived ones.** Member sizes, spacings and angles copy over; counts, rises and spans must be recomputed once your overall dimensions differ (keep the source's stair going, but recompute the riser count and height for your own floor level, and check the result still fits the space available).
- **Pick parameters at stated thresholds, not mid-range.** A threshold carries a justification the source itself supplies: the widest board still in the two-nail class is a defensible width; a round number from the middle of a range is not.
- **Trust drawings and schedules over body text** when the source contradicts itself. Manuals carry internal contradictions (a floor board 30 mm in one chapter and 22 mm in the table and drawings); the drawings and quantity schedules are usually the reliable layer.

## When the reference and the brief disagree

The brief overrides the reference, once, explicitly, in writing. If the brief says raised on stilts and the manual's kitchen wing sits on a ground slab, the wing goes, and the refusal is recorded with its reason. Leave a legible stub (a blind wall) where the omitted part would attach. Silent omission reads as an error; a recorded override reads as a decision.

## When the reference runs out

- **A silent reference still owes you a detail.** Diagrammatic sources draw arrangement, not connection. A handbook that draws slabs meeting a core without drawing the bearing still needs ledgers under the slab edges in the model. Gaps in a reference mark the places that demand inference, not the places that need no geometry.
- **Extend the source's own rules by analogy, snap to real material sizes, and label the extension as yours.** A rule stated for main-roof hips ("about 50 mm deeper") can be applied to dormer valleys the source never sizes; if the arithmetic gives a size that is not a dressed lumber size, take the next real one. Record the extension as an application of the rule, never as directly sourced.
- **Do not adopt a feature whose detail the source does not draw.** A layout whose members would stand over nothing, needing a cantilever detail the source never shows, produces geometry that looks right and is structurally nonsense. Prefer the version you can detail.
- **When geometry forbids the textbook detail, use the reference's own listed alternative** before inventing one, and verify the alternative's own limits (where collar ties are impossible around dormers, the source's struts may work, but a strut chasing a rising member can never make its minimum angle; flag such members as needing engineering instead of faking it).

## The two-phase workflow

1. **Phase 1: build from the tables.** Extract sizes, spacings and grid rules; get a complete, numerically clean model standing. Layout and proportion only become legible once there is something to diff against.
2. **Phase 2: diff against the source's images.** Re-read the figures and photographs one by one against your renders, as a table: in the figure | in the model | change made (or "kept", with reason). This pass finds what the first reading skipped: struts, strongbacks, doubled end joists and nailing strips can all arrive after the model already scores zero overlaps, and a cover photograph can drive changes the text never implied.

**The summary loses the figures.** Text extraction preserves tables well and assembly relationships badly; whatever was drawn rather than tabulated is missing from the summarized md document. A model built through several versions from the summary alone can need substantive rework once the original PDF spreads are opened. Standing order: before declaring done, go back to the original document's figures.

## The deviation ledger

Keep three running lists, and repeat them in the rationale's scope section:

1. Deviations from the source, each with its cause (brief override, geometric conflict, tooling limit) and the rejected alternative named.
2. Considered and not changed, with reasons. This stops the next iteration from re-litigating settled questions.
3. Not verified: what the source specifies that the model never checked.

## Summarizing a new reference

When producing a new summarized md document from a PDF, use this structure: a scope note naming what is and is not included (so nobody hallucinates absent span tables), a flat quick-reference table of parameter/value pairs, the prose with figure labels transcribed, a figure index, and a closing step-by-step summary for procedural modelling. A summary that ends in an ordered build sequence and begins with a parameter table can be used without rereading the prose.

## Provenance

Distilled from the Fable design rationale documents of experiments 04, 08, 09, 11 and 13 in the CraftBot repo (https://github.com/lukapiskorec/craftbot), and from these summarized reference documents: *Construction Manual of Prefabricated Timber House* (FRIM/ITTO Technical Information Handbook No. 5, 1996), *The Segal Method* (The Architects' Journal special issue, 5 November 1986, by Jon Broome), *How to CLT: architectural guidelines for early stages* (Arkemi, Stockholm, 2nd ed. 2024), and *Canadian Wood-Frame House Construction* (CMHC), chapters 11 and 12.
