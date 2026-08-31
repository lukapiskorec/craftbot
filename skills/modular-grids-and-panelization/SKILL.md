---
name: modular-grids-and-panelization
description: Use when a brief involves prefabrication, panels, sheet materials, modular dimensioning, CLT or mass timber, or a multi-storey building assembled from factory elements.
---

# Modular grids and panelization

## Overview

In panelized construction the dimensional system is derived, not chosen: sheet and panel sizes come from somewhere concrete (a sheet catalogue, a truck, two people lifting), and everything else follows. A generator should take those source constraints as inputs and compute the grid, not hard-code spacings.

## Where the module comes from

- **Sheet size sets the module.** Local sheets 1220 x 2440 give a module of 1220 and a planning grid of 610; studs at 610, trusses at 1220, plans in multiples of 610. Swap in a 600 mm European sheet and the model rescales coherently (FRIM). Sanity check: a wall length that is not a multiple of the half-module means the grid was used wrong.
- **Soft-metric warning**: code tables say 300/400/600 but what gets built is 305/406/610, so that 1220 x 2440 sheets land on framing (CMHC). Pick spacing so the sheet divides evenly by it; sheets whose edges float mid-bay are the classic tell of a fake model.
- **Panel size is set by handling or transport, not structure.** Man-handled panels cap at about 3 m (FRIM); trailer envelopes are 13.6 x 2.45 x 3.0 m, CLT master panels about 16 x 3 m, 3D modules up to 4.15 m wide (How to CLT). A 3 m storey height falls out of a truck, not an aesthetic. Validate every element against the stock envelope, and prefer the largest panel that fits over arbitrary subdivision.
- **Tolerances are part of the system**: panels made 1 to 3 mm undersize, expansion gaps between sheets covered by beading, lapped unsealed junctions that drain (FRIM, Segal). Butting nominal sizes edge to edge models something that cannot be built. Prefer lapping and offsets over mitres and cut-to-fit.

## The tartan grid (Segal)

Alternate wide panel bands (600 or 1200 mm, from board sizes) with narrow structural bands (commonly 50 mm): every joist, mullion, sole plate and post lands on a band, so panels are never cut. The numbers reconcile at a module repeat of 650 = 600 + 50, giving the stated 3.85 m maximum bay as 6 x 650 minus 50 (a derived reconciliation, not stated in the source). Columns deeper than the band stand partly outside the grid, pushed outside the building or projecting from a partition, never longways inside the grid. Design order is plan first: partitions are laid out, then the frame follows the plan.

## Dimensional discipline as a metric

Rank a design by its count of distinct element types: optimized (one panel type), systematized (a few types), non-systematized (every panel different) (How to CLT). A generator can self-check by grouping elements by dimension signature and reporting the count; it is also the reason to reuse a parametrized constructor instead of emitting one-off boxes.

## Multi-storey panel systems

- **System selection by storey count** is a lookup, not a guess: modular 4-8, honeycomb 6-16, parting wall 4-12, CLT-core hybrid 4-16, CLT plus timber frame up to 3-5; below four storeys a light frame may beat CLT on material (How to CLT; the numbers are preliminary and Sweden-specific, carry that caveat).
- **Vertical alignment of load-bearing walls governs plan repetition**: honeycomb repeats the whole plan, parting-wall systems free the interiors as long as parting walls line up, module systems stack aligned (How to CLT). This turns "repeat the floor upward" into a justified rule and names which walls may vary.
- **Platform vs balloon sets the assembly loop**: platform iterates per storey (walls, slab on top, raise Z); balloon places full-height walls once and hangs floors between. One priority sentence settles hundreds of junctions: slab over platform walls, slab against balloon walls, and slabs meeting balloon walls need ledgers to bear on.
- **Cores are the stability backbone**, built from tall continuous panels while everything else restarts per storey; model the core first. A concrete podium under the timber absorbs the different ground-floor plan and keeps timber off wet ground (How to CLT).
- **Sizing is span in, thickness out, with a reinforcement tier**: slabs 200/220 mm under 5 m span, 240/260 mm at 5 to 7 m (light/heavy superstructure); the light-or-heavy flag reindexes every table including walls, and storey-band indexing (I-III, IV-VI, VII-VIII) thickens lower walls in defensible steps (How to CLT, same caveat).
- **Openings in panels have pier minimums** (edge pier 300 mm, pier 600 mm between large openings) and three formation methods (CNC cutout, slab support, lintel support); switch method when an opening passes 2 m instead of silently cutting an unbuildable hole (How to CLT).
- **Panelization splits land on features**, not on even divisions: a corridor opening band becomes its own strip so its pieces are the per-storey lintels; elements nested on one master panel share a width (How to CLT).

## Build-ups as layer lists

Model any wall, floor or roof build-up as an ordered list of (name, thickness) pairs around the marked structural layer, generated by offsetting along the normal (How to CLT). Segal's clothes vocabulary names the roles: vest (interior comfort), sweater (insulation), raincoat (weather), fitting loosely so the assembly breathes. A substrate layer's geometry can depend on the layer above it (spaced sheathing pitch equals shingle exposure, CMHC), so carry cross-layer parameters instead of treating layers independently.

## Provenance

Distilled from these summarized reference documents: *Construction Manual of Prefabricated Timber House* (FRIM/ITTO Technical Information Handbook No. 5, 1996), *The Segal Method* (The Architects' Journal special issue, 5 November 1986, by Jon Broome), *How to CLT: architectural guidelines for early stages* (Arkemi, Stockholm, 2nd ed. 2024), *Canadian Wood-Frame House Construction* (CMHC); and from the Fable design rationale documents of experiments 08 and 09 in the CraftBot repo (https://github.com/lukapiskorec/craftbot).
