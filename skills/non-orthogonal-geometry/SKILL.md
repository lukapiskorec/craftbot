---
name: non-orthogonal-geometry
description: Use when a brief involves sloped, tilted, twisted, or warped surfaces built from straight timber stock, such as pitched members meeting at angles, hips and valleys, hypar walls or roofs, or deconstructivist forms.
---

# Non-orthogonal geometry

## Overview

Leaving the orthogonal grid does not mean leaving straight stock. Almost every rule here is a consequence of one idea: build warped and angled things from straight convex pieces cut by planes, so the geometry stays buildable and the overlap check stays valid.

## Warped surfaces

- **First question for any non-planar surface: is it ruled?** A wall whose bottom and top edges are skew straight lines is a hyperbolic paraboloid, and a hypar is built entirely from straight members. Implement it as a bilinear patch between two straight segments: rulings carry studs and rafters, cross rulings carry boards.
- **Long members on a twisting surface fail.** A board 7 to 10 m long along a twisting ruling accumulates several millimetres of edge error; cut to short stock with joints on support centre lines and staggered rows. Board width varies linearly between rulings, so each board is a trapezoid.
- **Fit framing per bay, not across bays.** A member's fitting error grows with the number of bays it spans on a non-flat surface; per-bay trimmers succeed where a header fitted across three bays collides with its studs.
- **Straight continuous members (plates, rails, purlins) on a twisted surface**: either segmented blocking that follows the twist, or a continuous member narrower than the studs with stated clearance for the rotation. Document it as a simplification.
- **Report the out-of-plane residual per member and read it as design information.** A planar door in a twisted bay needing 19 mm of play is a buildability fact, not just an error metric; the residual report flags where a real builder needs tolerance, packers or a laminated member.
- **Standing a tilted object on a warped surface**: each leg is cut by two planes, the surface plane evaluated at the leg's own position and the underside plane of the frame above. No bent members, no meshed surfaces, convexity preserved.

## Cutting rules that only bite off-grid

- **Slab-exact clipping.** Clipping a member's mid-plane lets the slab poke through by half the thickness times the sine of the angle. Shift every cut plane by the worst-case thickness term so the whole slab satisfies the half-space; cuts become slightly conservative bevels, which is what a carpenter cuts anyway.
- **A cut plane must contain the target edge line.** Perpendicular-to-the-ruling is not flush-with-the-trimmer on a warped surface, because the parametric directions are not orthogonal. Derive the cut plane from the geometry being butted against, never from a local parametric direction.
- **Boolean subtraction must take the exact complement.** Computing the kept piece with an unshifted plane while the hole uses the shifted one manufactures overlaps between sibling pieces of one board.
- **Clip the profile separately on both member faces.** An oblique plane meets the near and far face at different positions; independent clipping gives true compound cheek cuts instead of square worst-case ends.

## Members meeting sloped surfaces

- **Bevel the member to the reference plane instead of moving the plane.** A flat-topped beam tangent at its centreline pushes its corners above the plane; raising the plane to clear them leaves everything bearing on an edge. Bearing face contact is the goal.
- **Rotate secondary members to the slope** so the layer above gets one continuous bearing plane; the layer offset is depth divided by cos(pitch).
- **Size against the governing edge, not the centre line.** A strongback under a sloping soffit placed by centre line runs into the members above; take the extreme edge, and re-derive the governing line from plan geometry rather than reusing a similar-looking number from elsewhere in the model.
- **Drop the shared hip or valley member below the surface** so its top corners lie under both adjoining planes, the same move as dropping the hip in roof carpentry.
- **Angled member node spacing comes from the footprint, not the eye.** The width of an angled member divided by the sine of its angle is the length it occupies on the face it meets; a 45 mm diagonal at 32 degrees needs 85 mm at the node.

## Provenance

Distilled from the Fable design rationale documents of experiments 02, 06, 07, 11 and 13 in the CraftBot repo (https://github.com/lukapiskorec/craftbot). Experiment 07 (Gehry Residence) is the deepest single source, with measured error figures for most of these rules.
