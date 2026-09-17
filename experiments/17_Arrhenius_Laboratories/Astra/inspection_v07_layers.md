# v07 layer review - accepted

Independent Designer fallback review under the Coordinator's recorded one-reviewer exception. No v07 geometry code read. Directly inspected Workbench10/49/50/58 and the actual export report fixture_layers_v07.txt.

WB49 shows the repeated real concrete Beam/Column/corbel system and core structural walls, without the fine facade/window/skylight members, curved metal stair rims or new facade hardware. Its transverse hierarchy is legible and there is no invented continuous longitudinal EdgeBeam. WB10 uses the legacy visibility set;49 is the authoritative actual-taxonomy isolation.

WB50 shows the fine facade frames, inclined glazing framing, rooflight grid, guards and curved stair rims separately from primary concrete. The former erroneously classified entrance concrete rectangle is absent. The new brackets are small at the full-building scale; isolated58 verifies their discrete array and55–57 supply joint detail. Numeric membership, not pixel size, establishes all180 pieces in fixtures.

The exported30,156-element JSON SHA256 is2a074a8867df408bdd16b5c3a24f0d7d5177bbb9f7a2a1e126a8ce07c2cf26b3. Eleven taxonomy checks pass:5,414 timber-frame pieces,395 steel-frame pieces including180 new bracket pieces,178 skylight frames and1,152 StairRim pieces are fixtures; four concrete RooflightSeatBeams remain frame; EntranceApproachSlab is floors; no element is other. All180 exact bracket names and Facade/SteelFrames collections are explicitly checked. Fixture classification does not deny the structural role of the metal rims or attachment hardware.

WB54 was directly inspected and confirms the same correct fixtures isolation, without the entrance concrete slab or primary frame. Complete image identity and independent recomputed export hash pass in inspection_v07_identity.md. No layer correction is requested from the completed evidence.
