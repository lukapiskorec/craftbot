---
name: roof-framing-and-sheathing
description: Use when modelling any pitched roof (gable, hip, valley, dormer), roof sheathing, or roof coverings; also when a brief names a roof pitch or covering material.
---

# Roof framing and sheathing

## Overview

Roof rules are mostly threshold rules: pitch decides which members exist, which coverings are legal and which system resists thrust. A good roof generator branches on those thresholds explicitly instead of always emitting the same part list.

## Slope as a parameter

- Rise is always written first. Two conventions coexist: framing-square form with run fixed at 12 (4/12), and ratio form keeping a leading 1 (1:3 below 45 degrees, 3:1 above). 4/12 and 1:3 are the same roof. Take one slope parameter and normalise it; silently swapping conventions inverts the roof (CMHC).
- **The 1:3 threshold switches the thrust system.** At 1:3 or steeper: ceiling joists tie the rafter feet, collar ties on rafter pairs as intermediate support. Below 1:3: vertical support at the peak instead (ridge beam on struts, or a bearing wall), after which continuous ties are unnecessary (CMHC).
- **Coverings are slope-gated**: asphalt shingles 1:3 in normal application (1:6 with low-slope application), wood shingles 1:4, shakes 1:3, sheet metal 1:4; low-slope roofs need at least a 1:50 fall and a membrane. Check the pitch-covering pair in any brief that names both (CMHC).

## Hip roof plan geometry

Unless the brief explicitly asks for different pitches on different sides, assume equal pitch all around; the rules below hold for that case.

- Equal pitch: ridge length = building length minus width, hips leave the corners at 45 degrees in plan; on a T or L plan with equally wide wings, both ridges are level and valleys run at exactly 45 degrees from the inside corners (CMHC). Widening a wing to match the main block makes all hip ends congruent, so one dormer module can repeat on every facet.
- **Choose global parameters backwards from the tightest downstream constraint.** Solve the slope from the dormer stack-up formula, then check the answer against the source's acceptable range; choose the dormer module and grid offset so doubled and trimmed rafters land on grid lines on every facet.
- Hip and valley rafters run about 50 mm deeper than the jacks they receive, because the jack's angled cheek face is taller than its nominal depth (CMHC). At hip ends the deeper hip displaces the outermost ceiling joist: double it inboard and infill with stub and tail joists at the same spacing (CMHC).
- Derived formulas, labelled as derived (the CMHC chapters contain no trigonometry): hip drop = S x t / sqrt(2) so the hip's top corners lie on both roof planes; birdsmouth height above plate HAP = depth / cos(theta) minus seat x S. Bird's mouths make profiles non-convex, so split the rafter into body plus tail (see procedural-geometry).
- **Intermediate supports shorten rafter span**: collar ties (1:3 and up), dwarf walls (below 1:3), struts at 45 degrees or more standing on bearing partitions, strongbacks under hip-end jacks (CMHC). Where geometry forbids 45 degrees (a strut chasing a member that itself rises), record the member as needing engineering instead of faking the angle.

## Assembly order is structural

Ceiling joists go in before rafters, because rafter thrust would otherwise push the walls apart. Sheathing goes on before dormers; the dormer stands on the sheathing and the cutout is simply the inside of its walls, which also means one plane (main board top) clips every dormer-to-roof contact (CMHC). Following the real build order tends to hand you one shared clipping surface instead of many pairwise fixes.

## Sheathing

- **Boards run perpendicular to the rafters (parallel to the eaves) on every facet, including hip triangles** (CMHC Fig. 98); boards running up-slope on hip facets contradict the figure and should be corrected when found in an inherited model.
- Board layout rules (generalise to any coursed material on a support grid): rows start at the eave with full boards; every end joint lands on a support; cut runs at the farthest support within stock length; odd rows start with a half board so joints stagger; the last row is ripped, and slivers under about 40 mm merge into the previous row as a carpenter would.
- Panels: face grain perpendicular to framing, joints staggered, 2 to 3 mm gaps, nailing 150 mm at edges and 300 mm in the field, unsupported edges get H-clips or blocking (CMHC).
- **Where two sheathed planes meet** (dormer into main roof): end each layer on the other's opposite face, so the two share exactly the intersection line, neither overlap nor gap. The symmetric choice (both layers ending on one offset level) overlaps by the full board thickness.
- Overhangs: lookouts at least twice the overhang; any member the lookouts land on gets doubled when they project more than 1.5 spaces into the roof (CMHC).

## Coverings and cavities

- A covering is an exposure-driven course stack with a fixed order: eave protection, starter strip, first course aligned to the starter, then courses at the allowed exposure, ridge and hip caps last, lapped away from the prevailing wind (CMHC). Exposure plus joint offset plus a doubled starter course is the whole algorithm, and it covers wall shingles and lap siding too.
- The vented cavity is geometry: at least 63 mm clear between insulation and sheathing (25 mm with baffles), and energy rules push heel depth toward 300 mm. A performance requirement shows up in the model as member depth or a batten layer (CMHC).

## Provenance

Distilled from *Canadian Wood-Frame House Construction* (CMHC), chapters 11 "Ceiling and Roof Framing" and 12 "Roof Sheathing and Coverings" (original PDF in the experiment folders), and from the Fable design rationale documents of experiments 07, 11 and 13 in the CraftBot repo (https://github.com/lukapiskorec/craftbot). Formulas marked derived are the modelling agent's, not the source's.
