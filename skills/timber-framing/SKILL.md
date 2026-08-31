---
name: timber-framing
description: Use when modelling any framed timber structure (stud walls, floors, post-and-beam frames, trusses), when choosing member sizes without a manual, or when reviewing whether a model works as a structure.
---

# Timber framing

## Overview

A frame is a set of load paths, not a set of shapes. The habit that makes generated frames plausible: for every member, name what load it carries and into which member it delivers it, and place it accordingly.

## Before placing geometry

- **Settle the bearing stack first.** Decide what sits on what from ground to roof surface (post, plate, tie, principal, purlin, common) before any coordinate. Write out candidate stacks and reject on geometric grounds; once the stack is fixed, every height is a 1D offset.
- **Model the building's own structural system, not the default idiom.** A system braced by shear panels and a diaphragm gets no diagonal wall bracing just because stud walls usually have it; before adding a member, name which load path it serves in this building. If none, it is idiom, not structure. Pick the framing system per zone from what actually carries load there, not from the label: a building can honestly mix balloon-framed solid end walls with platform-framed volumes on the roof when its glazed sides leave no studs to continue upward.

## Rules of the frame

- **Vertical alignment.** Trusses, studs and joists stay in the same vertical planes; spacings are integer multiples sharing one origin, so load runs roof to stud to joist to ground with no transfer members (FRIM). Preserve the module through openings by putting king studs on grid lines with jacks inside them.
- **Load-bearing walls and partitions differ physically, not just by name.** Partitions are thinner and deliberately shorter, stopping about 25 mm below the structure above so nothing bears on them (FRIM).
- **Opening grammar.** Walls: king studs, jack studs carrying a header sized to its load, cripples, sill; filter regular studs out of the opening zone before framing it, so no stud lands inside a header. Floors and roofs: built-up trimmers under the loads (ply count follows load), headers across the cut, interrupted members become tail members bearing on the headers. Opening size follows what passes through it, not what the grid offers.
- **Blocking is routine, not an afterthought.** Wherever a repeated member crosses a support or a sheet edge lands mid-air: solid blocking (rollover restraint, nailing edge). Derive it from placed members, so it always fits real bays.
- **Lateral stability is a per-direction check.** Each horizontal direction needs a named shear element; when the envelope cannot brace (glass walls), sheathe an interior wall that already exists, with the deck as diaphragm. The Segal pattern: rigid frames one way, braced bays plus the floor as a horizontal plate the other. Knee braces sit in the 45 to 60 degree range.
- **Wide glazed bays**: a ring beam at one level doing three jobs (spanning posts, collecting joists, carrying loads above) replaces a top plate that has no capacity over glass; land concentrated loads near posts.
- **Equal-depth beams and joists with side bearers** keep soffits flush so every wall panel is one height; doubled interior beams even out beam loads (Segal).

## Joinery in a box-and-prism vocabulary

- **Arris bearing**: a sloped member's underside passes through the top arris of its support; reads as a bird's mouth.
- **End-face inset**: shorten a square-cut member along its axis by (|e1.n| w/2 + |e2.n| d/2) / |axis.n| so no corner of the end face crosses the bearing plane. Generic, no per-member tuning.
- **Halving joint as three boxes**: full section, half-width middle segment kept entirely on its own side of the crossing plane, full section; lap length d (1 + cos phi) / sin phi plus a margin, centred where the centrelines cross.
- **Model the carpenter's fix, not the geometric fudge.** A hip standing proud gets dropped (the real seat-cut fix, computed from the adjacent facets), not thinned; thinning hides the condition instead of modelling it.
- **Connections in light panelized systems are typed hardware with spacing rules** (nail plates, angle plates, skew nails, tighter spacing at panel edges), covered by beading; there are no carved joints in such systems, and modelling mortices there is wrong for the system (FRIM). Segal-type systems are dry-jointed throughout: bolt size follows from joint load, and the bolt size dictates minimum spacing and edge distances.

## Sizing without an engineer

- Declare a standard section catalogue up front and name the tradition (50 x 150 studs at 600 centres, 50 x 200 floor joists, 50 x 250 roof joists, 18 mm ply). A small consistent family beats per-member invention, and re-sizing becomes a one-line change.
- Calibrated anchors from CMHC worked examples: ceiling joists at 4.3 m span, 400 mm centres, SPF No.2 give 38 x 140; rafters at 1:3 slope and 4.7 m span give 38 x 184 at 300 centres or 38 x 235 at 600. Doubling the spacing costs one or two depth increments.
- Model actual dressed sizes (38 x 89 is a nominal 2x4), or everything comes out about 12 percent oversized.
- A member receiving angled members sizes to the projected face of the cut, not the nominal depth of what arrives (hips about 50 mm deeper than the jacks they receive, CMHC).
- Always close with the honest line: sections are plausible for the span, not calculated.

## The independent structural review

Once per run, review the model with the reference set aside, asking only whether it works as a building. Checklist: vertical load path continuous to ground; lateral stability in both directions; load transfer at discontinuities (openings, cores, level changes); gravity, sliding, moisture and racking at details (purlins laid on a steep slope get cleats; posts standing on slabs get plinths). Record what was added, and what was considered and rejected with reasons, so the next round does not re-propose it. This pass finds the defects no reference image contains.

## Provenance

Distilled from the Fable design rationale documents of experiments 01, 02, 03, 04, 06, 08 and 13 in the CraftBot repo (https://github.com/lukapiskorec/craftbot), and from *Construction Manual of Prefabricated Timber House* (FRIM/ITTO Technical Information Handbook No. 5, 1996), *The Segal Method* (The Architects' Journal special issue, 5 November 1986, by Jon Broome), and *Canadian Wood-Frame House Construction* (CMHC).
