---
name: structural-logic
description: Use for every building regardless of material, when settling the bearing stack before geometry, when checking that every element has a load path to ground and a bearing at every seat, when checking lateral stability per direction, when sizing concrete, steel or masonry members without an engineer, and when running the independent structural review. The Designer and the Builder load it always; timber-framing is loaded on top of it only when timber is one of the materials.
---

# Structural logic

## Overview

A building is a set of load paths, not a set of shapes. For every element, name what load it carries and into which element it delivers it, and place it accordingly. This skill holds the part of that habit that does not depend on the material; the material skills (timber-framing, and any later one) add their own joinery, catalogues and idioms on top.

## Before placing geometry

- **Settle the bearing stack first.** Decide what sits on what from the ground to the roof surface (footing, wall or column, beam, slab or deck, roof build-up) before any coordinate. Write out candidate stacks and reject on geometric grounds; once the stack is fixed, every height is a 1D offset.
- **Model the building's own system, not the idiom of its material.** Before adding an element, name the load path it serves in this building; if there is none, it is idiom. A glass wall carries nothing, so the roof beam above it needs a post or a wall at each end and the lateral load needs a shear element somewhere else.
- **The ground is an element.** On a slope, decide for every wall whether it retains, stands on a plinth, or sits on grade, and for every footing where its underside is relative to the finished ground at that wall face. A terrain surface is modelled where the relation of the building to the ground is part of the brief.

## Load path to ground

- Every element family has a chain to the ground that can be written as a sentence: "roof slab on transverse beams at 4 m, on posts on the glazed side and in pockets of the closed wall, posts on the floor slab over the girder line, girders on cap plates on columns on pads 1.2 m below grade." If a family cannot be written into such a sentence, it is floating even when the contact check passes.
- **Bearing at every seat.** A beam bears on a plate, a pocket or a wall for a stated length; a slab bears on the full wall thickness or on a ledger; a column stands on a base plate on a pad; a stair flight bears at both ends. The contact check only proves that surfaces touch; the bearing length and what carries the reaction are the Designer's argument.
- **Continuity.** A member that spans over a support continues through it or is spliced over it; a member that stops at an opening bears on a header, which bears on trimmers or posts. Level changes, cores and openings are the places where the chain breaks; walk each one.
- **Retaining and foundation walls.** A wall with earth on one side is a retaining wall whether it is called that or not. It needs a base (a strip footing under a braced wall, an L-base under a free-standing one), a stated retained height, and a stated top restraint (a slab, or none). Stepped footings on a slope step in short vertical risers with level runs; the riser is the width of the footing.

## Lateral stability, per direction

- Each horizontal direction needs a named shear element and a named diaphragm that brings the load to it. Walls that are all glass brace nothing; the shear elements are then concrete boxes, cores, sheathed panels, braced bays or moment frames, and they must reach the diaphragm they serve. A core that stops below the roof braces the floor it stands on and nothing above it.
- A diaphragm spans between its shear elements like a deep beam: a 60 m roof with a box at each end and nothing between is a 60 m span. State the span and what limits it.
- A frame is a moment frame only if its joints are drawn as such; a beam seated in a pocket or on a cap plate is pinned. Do not write "portal" for a pinned frame.
- Sloped ground adds sliding and overturning to retaining walls and to any box cut into the slope; the base proportions (heel, toe, key) are the answer and are labelled as practice unless a manual gives them.

## Sizing without an engineer

- Declare a catalogue per material up front and name the tradition: concrete slab and wall thicknesses, steel section family and depths, a footing pair (strip and pad). A small consistent family beats per-member invention, and re-sizing becomes a one-line change.
- Rules of thumb, labelled as practice, never as sourced: one-way concrete slab depth about span/20 simply supported and span/28 continuous; steel floor and roof beams about span/18 to span/20 deep; plate girders about span/15 to span/18; a concrete wall retaining up to 2.3 m with its top braced needs 250 to 300 mm (CMHC Table 5 gives the table); a strip footing at least 100 mm wider than the wall each side and at least as thick as its projection; a pad under a column at least as thick as its projection from the base plate. Timber sizes come from the timber-framing skill.
- Where a manual gives a table, the table replaces the rule of thumb and the row is cited. Where the brief names a load that a manual does not cover (a 12 m clear span, a 2.75 m free-standing retaining wall), say that the member is outside the manuals and record it in the deviation ledger.
- Always close with the honest line: sections are plausible for the span, not calculated.

## The independent structural review

Once per run, with the reference set aside, ask only whether the model works as a building. Read the built script or the notes, not the concept, so the review is about what stands. Checklist:

1. Vertical load path continuous to ground for every element family, written as sentences.
2. Lateral stability per direction: shear elements named, diaphragms named, spans stated, and every shear element reaching the diaphragm it serves.
3. Bearing at every seat with a length, and continuity at every discontinuity (openings, cores, level changes, cantilevers).
4. Foundations: undersides relative to grade, stepped on slopes, retaining walls with bases and top restraint.
5. Sizes plausible for their spans by the catalogue and the rules above; anything outside the manuals named.
6. Details that fail by gravity, sliding, moisture or racking (posts on slabs get plinths; hollow undercrofts get access; roofs drain somewhere).

Record what was added, and what was considered and rejected with reasons, so the next round does not re-propose it. The findings become requirement lines with the load-path argument as their source; this pass finds the defects no reference image contains.

## Provenance

Extracted from the material-neutral parts of `skills/timber-framing/SKILL.md` (bearing stack, lateral per direction, the review checklist), from the structural review of the experiment 15 Fable run (a concrete, steel and glass house on a slope: the cores that stopped under the roof, the pinned frames written as portals, the retaining walls outside the manual tables), and from *Canadian Wood-Frame House Construction* (CMHC) and the *Architect's Handbook of Construction Detailing* (AHCD) as cited in that run's `sources.md`. The span-to-depth ratios are common practice and carry no manual clause.
