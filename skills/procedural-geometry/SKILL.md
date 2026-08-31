---
name: procedural-geometry
description: Use when writing or revising Blender Python that generates construction geometry, before placing members by hand-typed coordinates.
---

# Procedural geometry

## Overview

The model hangs off a small set of derived expressions, not a table of constants. Everything below serves two goals: a parameter change propagates instead of breaking hand-entered numbers, and the geometry stays checkable by a numeric overlap test. If a collision check script exists in the repo's tools, use it to verify model intersections; otherwise, check element intersections directly by examining the model file.

## Single source of truth

- **Derive every level and position from parametric functions.** One roof-plane function fixes purlin centres, ridge levels and strut targets; changing pitch regenerates a consistent frame. Never type a number twice.
- **One shared surface function for every member that meets that surface.** Write the roof plane once as a function of position and derive trays, bevels, ceiling, post tops and cladding from it; coplanarity becomes structural instead of something to re-check.
- **One parametrized constructor per member family.** All wall bays from one wall function, every sloped roof element from one profile-extrusion helper; a family fix becomes a one-function fix.
- **Generate a derived feature list once and pass it everywhere.** Calling a seeded feature generator twice yields two different sets and cuts cladding where the wall behind is solid. A seed does not guarantee agreement; a single call does.
- **Address openings by slot index, not metric position** on gridded walls, so an opening always occupies whole panels and the structural bands inside a hole become mullions by construction.
- **Derive secondary members (blocking, noggins, rims) from the list of members actually placed**, never from the nominal grid, so they fit real bays including doubled members and skip openings.

## Cutting and joining

- **Build long and clip with half-spaces; never type endpoints.** Each facet carries a fixed plane list; one call produces a common, a jack or a cripple rafter depending only on where the member line sits. The rejected alternative, solving endpoints analytically per case, multiplies formulas.
- **Split members at discontinuities instead of branching on a straddle predicate.** A piece crossing the ridge is split plumb into two parallelograms; boundary predicates on float comparisons fail exactly at the members sitting on the boundary, which are usually the important ones.
- **Keep every solid convex.** The separating-axis check is exact only on convex solids. A bird's mouth splits the rafter into body plus tail sharing a face; a wall with a hole becomes pier, sill and lintel pieces, which also matches how the panel is fabricated. Choose the decomposition to keep the checker valid rather than relaxing the check.
- **Corners resolve by one stated rule**: long members run full length, cross members run between them, applied at every scale. In layered walls the caller states each layer's extents; corners are never resolved by magic inside the function, because the correct answer depends on neighbours the function cannot see.
- **Work in the assembly's own coordinate frame.** Roof covering expressed in (distance up slope, height normal to roof) turns trigonometry into offsets and removes drift.
- **Compute outline vertices as plane intersections, evaluated at two offset levels** (underside and top), so a shared edge between facets is the same edge for both and adjacent pieces share one end face exactly. Correctness comes from the construction, not from a tolerance check afterwards.
- **Prism profiles cannot slope across their own thickness.** A wall running along X cannot express a roof-cut top in its profile plane; it gets a flat top plus a separate wedge, one wedge per wall segment so the wedge never runs into a crossing element.

## Dimension chains and counts

- **Close the dimension chain.** Tune one genuinely free parameter so a run of repeated elements lands exactly: a stair going chosen so treads plus landings fill the core, an overhang trimmed so the roof is a whole number of trays.
- **int(round(length / module)) silently drops a partial module.** Derive counts with an explicit ceiling and a stated remainder policy, or adjust a free dimension until the division comes out whole.

## Conventions that prevent whole bug classes

- **Axes**: one convention (X along the building, Y across the span, Z up, slab top at z = 0), kept identical across experiments so numbers stay comparable and helpers move between scripts without rework.
- **Depth axis always points up** in the member helper, enforced in code. A one-sided error pattern (overlaps on one slope of a symmetric roof only) is the diagnostic signature of a missing orientation convention.
- **Normalize winding inside the prism helper**, so no caller needs to know the handedness of its axis mapping. Unexpectedly dark surfaces are a normals bug, not a lighting problem.
- **Qualify object and collection names with their parent.** Bare-name lookup can merge four walls' cladding into one collection, and a name collision can silently overwrite geometry. Uniqueness is a construction rule, not a hope.
- **Carry the toolkit forward.** Start from the previous experiment's helpers (box, prism, clip, strip, spacing), name the inherited kit and the delta separately, and promote a helper into a shared library once a second building has needed it.

## Provenance

Distilled from the Fable design rationale documents of experiments 01, 02, 03, 04, 06, 08, 09, 11 and 13 in the CraftBot repo (https://github.com/lukapiskorec/craftbot).
