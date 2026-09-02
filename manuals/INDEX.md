# Manuals index

Timber construction manuals used as reference material for CraftBot experiments. Each manual has an extracted markdown summary in this folder, committed to the repo, and an original PDF that stays local and gitignored (`manuals/*.pdf`) because of copyright. The summary header and the entry below say where the PDF can be downloaded; save it in this folder under the exact filename listed so the experiment workflow finds it.

How an experiment run uses this folder (the full procedure is in `skills/running-craftbot-experiment/SKILL.md`):

1. Read the descriptions below and pick the manuals that touch the brief.
2. Read their tables of contents and pick the chapters; one chapter of a long handbook is often all that applies.
3. Read the extracted `.md` of the picked manuals in full. It carries the numbers, rules, build sequences and a figure index with PDF page numbers.
4. Open the original PDF at the pages the chapter list and the figure index point to. Drawn details, appendix sheets and span tables are only there.

The `.md` is a companion to the PDF, not a replacement: text extraction keeps tables and loses figures.

Adding a manual: write `<slug>_extracted.md` with the same header block as the others (original PDF filename and download link, source, scope, most useful for; then contents, quick reference, chapter notes, figure index, modelling rules), add an entry below in the same format, and put the PDF in this folder.

Links were checked on 2026-09-02. "Direct PDF" means the URL returns the file; "landing page" means one more click; "borrowable" means an Internet Archive item that needs a free account to read and cannot be downloaded.

## Summary table

| Manual | Extracted summary | Pages | Online |
|---|---|---|---|
| [Canadian Wood-Frame House Construction](#canadian-wood-frame-house-construction) | [`canadian_wood_frame_house_construction_extracted.md`](canadian_wood_frame_house_construction_extracted.md) | 335 | landing page, direct PDF one click away |
| [Advanced Framing Construction Guide](#advanced-framing-construction-guide) | [`apa_advanced_framing_extracted.md`](apa_advanced_framing_extracted.md) | 24 | landing page, email-gated download |
| [Introduction to timber frame construction (TRADA WIS 0-3)](#introduction-to-timber-frame-construction-trada-wis-0-3) | [`trada_wis_0-3_timber_frame_introduction_extracted.md`](trada_wis_0-3_timber_frame_introduction_extracted.md) | 8 | direct PDF (mirror) |
| [Timber frame construction: a useful pocket site guide](#timber-frame-construction-a-useful-pocket-site-guide) | [`merronbrook_timber_frame_pocket_guide_extracted.md`](merronbrook_timber_frame_pocket_guide_extracted.md) | 64 | direct PDF |
| [Construction Manual of Prefabricated Timber House](#construction-manual-of-prefabricated-timber-house) | [`construction_manual_extracted.md`](construction_manual_extracted.md) | 60 | direct PDF |
| [The Segal method](#the-segal-method) | [`segal_method_extracted.md`](segal_method_extracted.md) | 16 | direct PDF |
| [How to CLT](#how-to-clt) | [`how_to_clt_extracted.md`](how_to_clt_extracted.md) | 38 | direct PDF |
| [The CLT Handbook, CLT structures, facts and planning](#the-clt-handbook-clt-structures-facts-and-planning) | [`clt_handbook_2022_facts_and_planning_extracted.md`](clt_handbook_2022_facts_and_planning_extracted.md) | 188 | direct PDF |
| [The CLT Handbook, CLT structures, design and detailing](#the-clt-handbook-clt-structures-design-and-detailing) | [`clt_handbook_2022_design_and_detailing_extracted.md`](clt_handbook_2022_design_and_detailing_extracted.md) | 156 | direct PDF |
| [Canadian CLT Handbook, 2019 Edition](#canadian-clt-handbook-2019-edition) | [`canadian_clt_handbook_2019_extracted.md`](canadian_clt_handbook_2019_extracted.md) | 812 | landing page, form-gated download |
| [Binderholz Solid Timber Manual](#binderholz-solid-timber-manual) | [`binderholz_solid_timber_manual_extracted.md`](binderholz_solid_timber_manual_extracted.md) | 248 | direct PDF |
| [Building Systems by Stora Enso, 3 to 8 Storey Modular Element Buildings](#building-systems-by-stora-enso-3-to-8-storey-modular-element-buildings) | [`stora_enso_modular_element_buildings_extracted.md`](stora_enso_modular_element_buildings_extracted.md) | 96 | direct PDF |
| [Mass Timber Design Manual 2021](#mass-timber-design-manual-2021) | [`mass_timber_design_manual_2021_extracted.md`](mass_timber_design_manual_2021_extracted.md) | 98 | landing page, email-gated download |
| [Architect's Handbook of Construction Detailing](#architects-handbook-of-construction-detailing) | [`architects_handbook_construction_detailing_extracted.md`](architects_handbook_construction_detailing_extracted.md) | 457 | borrowable (Internet Archive) or purchase |
| [London Housing Design Guide (interim edition, 2010)](#london-housing-design-guide-interim-edition-2010) | [`london_housing_design_guide_2010_extracted.md`](london_housing_design_guide_2010_extracted.md) | 108 | direct PDF |
| [Woodworking, The Complete Step By Step Manual](#woodworking-the-complete-step-by-step-manual) | [`woodworking_complete_step_by_step_manual_extracted.md`](woodworking_complete_step_by_step_manual_extracted.md) | 400 | direct PDF (Internet Archive) |
| [Woodworking Wisdom and Know-How](#woodworking-wisdom-and-know-how) | [`woodworking_wisdom_and_know_how_extracted.md`](woodworking_wisdom_and_know_how_extracted.md) | 1891 | borrowable (Internet Archive) or purchase |

## Entries

### Light timber frame (platform frame, post and beam)

#### Canadian Wood-Frame House Construction

- PDF: `Canadian Wood-Frame House Construction.pdf`
- Extracted: [`canadian_wood_frame_house_construction_extracted.md`](canadian_wood_frame_house_construction_extracted.md)
- Online: https://publications.gc.ca/site/eng/9.700100/publication.html (publisher landing page with a download link to the direct PDF at https://publications.gc.ca/collections/collection_2014/schl-cmhc/NH17-3-2013-eng.pdf; the direct PDF link redirects to an interstitial page for a bare request but serves the file, application/pdf, 12.6 MB, when fetched with a Referer header from the landing page; verified 2026-09-02, HTTP 200 both pages)
- About: Published by Canada Mortgage and Housing Corporation (CMHC), Canada's national housing agency. Covers the full construction sequence for a typical one- to three-storey Canadian platform-framed house, from site work and foundations through every framing stage to interior finishes, aligned with the 2010 National Building Code. A modelling agent gets prescriptive member sizes and spacings for essentially every wood structural element (floor and roof joists, beams, studs, lintels, rafters, deck framing) from 44 appendix span tables, plus a fully labelled whole-house cutaway drawing.
- Contents:
  1. Important general information (pp. 1-10; PDF pp. 20-29)
  2. Planning, design and construction (pp. 11-23; PDF pp. 30-42) [stages of construction schedule, permits]
  3. Concrete (pp. 24-27; PDF pp. 43-46)
  4. Lumber and other wood products (pp. 28-32; PDF pp. 47-51) [grades, engineered wood, panel products]
  5. Functions of the building envelope, water air vapour and heat control (pp. 33-59; PDF pp. 52-78) [air/vapour barrier location, insulation placement and amounts]
  6. Location and excavation (pp. 60-65; PDF pp. 79-84)
  7. Footings, foundations and slabs (pp. 66-88; PDF pp. 85-107) [footing and foundation wall sizing, slabs, drainage, backfill]
  8. Framing the house (pp. 89-92; PDF pp. 108-111) [platform vs balloon framing, lateral load exposure categories]
  9. Floor framing (pp. 93-107; PDF pp. 112-126) [sill plates, beams, joists, subfloor, worked sizing examples]
  10. Wall framing (pp. 108-117; PDF pp. 127-136) [studs, lintels, braced wall panels, SIPs]
  11. Ceiling and roof framing (pp. 118-135; PDF pp. 137-154) [trusses, site-built rafters, hip and valley framing, ventilation]
  12. Roof sheathing and coverings (pp. 136-147; PDF pp. 155-166) [panel and board sheathing, eave protection, shingles, shakes, metal, tile]
  13. Wall sheathing and exterior finishes (pp. 148-163; PDF pp. 167-182) [sheathing thickness, siding types, stucco, masonry veneer, EIFS]
  14. Flashing (pp. 164-172; PDF pp. 183-191) [base, counter, valley, stepped, cap and drip flashing types]
  15. Windows, exterior doors and skylights (pp. 173-184; PDF pp. 192-203) [NAFS ratings, egress sizes, installation sequence]
  16. Exterior trim and millwork (pp. 185-188; PDF pp. 204-207) [soffit and fascia types]
  17. Stairs (pp. 189-195; PDF pp. 208-214) [rise/run, stringers, handrails, guards, ramps]
  18. Chimneys, flues and fireplaces (pp. 196-202; PDF pp. 215-221) [masonry and factory-built chimneys, fireplace proportions]
  19. Plumbing, electrical and appliances (pp. 203-214; PDF pp. 222-233) [joist/stud notching and drilling limits, wiring and plumbing framing]
  20. Space conditioning systems (pp. 215-226; PDF pp. 234-245) [forced air, hydronic, ventilation, HRV/ERV]
  21. Interior wall and ceiling finishes (pp. 227-231; PDF pp. 246-250) [gypsum board thickness and fastening]
  22. Floor coverings (pp. 232-237; PDF pp. 251-256) [subfloor and underlay by finish type]
  23. Interior doors, frames and trim (pp. 238-245; PDF pp. 257-264) [door sizes, hardware, cabinets]
  24. Coating finishes (pp. 246-249; PDF pp. 265-268) [paint, varnish, stain, lacquer]
  25. Eavestroughs and downspouts (pp. 250-251; PDF pp. 269-270)
  26. Decks, porches and balconies (pp. 252-255; PDF pp. 271-274) [post/beam/joist sizing, guard heights, ledger connection]
  27. Garages and carports (pp. 256-258; PDF pp. 275-277) [air barrier separation, CO safety, dimensions]
  28. Surface drainage, driveways and walkways (pp. 259-260; PDF pp. 278-279)
  29. Maintenance (p. 261; PDF p. 280)
  30. Appendix A, tables (pp. 262-312; PDF pp. 281-331) [44 span and reference tables: floor/roof/ceiling joists, beams, studs, lintels, sheathing thickness, nailing schedules, deck members]
  31. Appendix B, cutaway view of a wood-frame house (pp. 313-315; PDF pp. 332-335) [one whole-house section drawing, 77 labelled callouts]
- Most useful for: sizing and spacing platform-frame floor, wall, ceiling and roof members and deck framing from the appendix span tables; footing, foundation and slab dimensions; stair and guard geometry; the overall build sequence for a typical wood-frame house.

#### Advanced Framing Construction Guide

- PDF: `APA-Advanced-Framing-Construction-Guide.pdf`
- Extracted: [`apa_advanced_framing_extracted.md`](apa_advanced_framing_extracted.md)
- Online: https://www.apawood.org/guides-tools-training/technical-document-library/construction-guides/advanced-framing/ (publisher page with download button; the button posts to a gated form that requires name and email before it releases the PDF, so it is not a direct link; verified 2026-09-02, HTTP 200, text/html, page names the document "Advanced Framing Construction Guide (M400)" and shows "PDF, 24 pages")
- About: APA, The Engineered Wood Association (Tacoma, Washington), a US wood products trade association. Covers advanced framing (optimum value engineering) for wood light frame residential construction: 24 inch on center studs, two-stud and insulated three-stud corners, ladder-blocked wall intersections, single top plates and the stack framing they require, single-ply and wood structural panel box headers, and continuous panel wall sheathing for bracing and siding attachment, all against the 2012 IRC/IECC and the AWC's WFCM. A modelling agent gets exact geometry and fastening for these framing details plus a wind-pressure sheathing nailing table, but no full span tables, no foundation design and no high-wind/seismic engineered design (out of scope, referred to the IBC). The copy in this repository is Form M400A, revised September 2014; apawood.org currently distributes a later edition, Form M400 (no "A"), revised April 2016, under the same title and page count.
- Contents:
  1. Front matter (pp. 1 to 3; PDF pp. 1 to 3) [cover, sustainability sidebar, table of contents]
  2. Components of advanced framing (p. 4; PDF p. 4)
  3. Advanced framing defined (p. 5; PDF p. 5)
  4. Advantages of advanced framing (pp. 5 to 7; PDF pp. 5 to 7) [energy efficiency, structural integrity, sustainability; "cost effectiveness" is listed in the source's own contents but has no separate heading in the body]
  5. Incorporating advanced framing techniques (p. 8; PDF p. 8) [four-step adoption sequence]
  6. Floor framing (pp. 8 to 9; PDF pp. 8 to 9)
  7. Wall framing (pp. 9 to 16; PDF pp. 9 to 16) [stud spacing, corners, interior wall intersections, connection details, headers, wood structural panel box headers, openings, blocking, metal hardware]
  8. Single top plates (pp. 17 to 18; PDF pp. 17 to 18) [ceiling and roof framing, framing member layout]
  9. Wall sheathing (pp. 18 to 20; PDF pp. 18 to 20) [wind resistance and wall assemblies, wall bracing]
  10. More information (pp. 21 to 22; PDF pp. 21 to 22) [further publications, codes referenced, acknowledgements]
  11. About APA and back matter (pp. 23 to 24; PDF pp. 23 to 24)
- Most useful for: sizing and spacing platform-frame wall studs, corners, headers and top plates for 24 inch on center "advanced framed" wood walls, and getting the connection and sheathing details the geometry needs.

#### Introduction to timber frame construction (TRADA WIS 0-3)

- PDF: `TRADA WIS 0-3 Introduction to timber frame construction 2016.pdf`
- Extracted: [`trada_wis_0-3_timber_frame_introduction_extracted.md`](trada_wis_0-3_timber_frame_introduction_extracted.md)
- Online: https://turnertimber.co.uk/introduction.pdf (direct PDF, mirrored by Turner Timber, a UK timber frame company; verified 2026-09-02, HTTP 200, content-type application/pdf, content-length 668820 bytes matching the local file exactly)
- About: TRADA Wood Information Sheet WIS 0-3, prepared by Exova BM TRADA, reviewed April 2016. 8 pages. UK platform timber frame housing and low-rise buildings. Gives a modelling agent typical stud sizes and spacings, external wall and party floor layer build-ups, and pointers to the more detailed TRADA publications and Wood Information Sheets for anything it does not itself state (span tables, nailing schedules, full working drawings).
- Contents:
  1. Title page and key points (p. 1)
  2. Benefits of timber frame construction (p. 2)
  3. Related publications (p. 2; TRADA books and 20 related Wood Information Sheets)
  4. Method of construction (pp. 2 to 3; platform frame sequence, open vs closed panels, BS 5268 variation box)
  5. External walls (pp. 4 to 5; stud sizes and spacing, insulated service zone, sheathing, breather membrane, cladding options)
  6. Internal walls (p. 6)
  7. Party walls (p. 6; twin frame with cavity, plasterboard layers)
  8. Other structural elements (p. 7; floors, head binders, header joists, trussed rafter roofs, party floors)
  9. Services (p. 7)
  10. Preservative treatment (p. 7)
  11. References (pp. 7 to 8; 35 numbered references to standards, TRADA books and other WIS)
  12. About TRADA (p. 8; publisher boilerplate)
- Most useful for: orienting a modelling agent to UK platform-frame stud sizes, spacings and wall or party floor layer order before it builds a wall panel, floor platform, or party wall assembly.

#### Timber frame construction: a useful pocket site guide

- PDF: `Merronbrook - Timber Frame Pocket Guide.pdf`
- Extracted: [`merronbrook_timber_frame_pocket_guide_extracted.md`](merronbrook_timber_frame_pocket_guide_extracted.md)
- Online: https://www.merronbrook.co.uk/assets/downloads/timber-frames/timberframepocketguide-aug2016.pdf (direct PDF, hosted as a customer resource on Merronbrook Ltd's downloads page; verified 2026-09-02, HTTP 200, content-type application/pdf, content-length matches the local file byte for byte)
- About: Structural Timber Association (STA) pocket site guide for UK low rise domestic timber frame construction, version 2.0, August 2016, supported by NHBC and LABC. Covers open panel timber frame with timber floor joists and truss rafter roofs. A modelling agent gets erection tolerances, sole plate setting out and packing methods, cavity barrier and breather membrane layout, and differential movement gaps between frame and masonry cladding. It does not give stud sizes, spans or panel buildups, those are left to project specific drawings.
- Contents:
  1. Cover, sponsors and foreword (PDF pp. 1 to 3)
  2. Introduction (PDF pp. 5 to 6, scope: open panel frame, timber floor joists, truss rafter roofs)
  3. Using the guide (PDF p. 7, icon key for best practice, defect warnings, checklists)
  4. Coordination checklist (PDF pp. 8 to 9, contractor, design team and erector checklists)
  5. Build sequence, what to look for (PDF pp. 10 to 18, 106 numbered checks across 9 stages from before work starts to after external cladding)
  6. Best practice advice notes (PDF pp. 19 to 61, twelve sections listed below)
     - Substructure (PDF pp. 20 to 22, diagonal, level and edge tolerances)
     - Sole plates (PDF pp. 23 to 31, setting out tolerances, three packing methods, fixing types)
     - Frame erection (PDF pp. 32 to 36, nailing centres, plumb and alignment tolerances, breather membrane)
     - Insulation (PDF pp. 37 to 41, wall and cold roof space details, fully filled party walls)
     - Vapour control layer, VCL (PDF pp. 42 to 43, fixing and lapping specification)
     - Thermal efficiency and airtightness (PDF pp. 44 to 45, junction lapping details)
     - Dry lining (PDF p. 46, fixing centres)
     - Fire stops (PDF p. 47, required locations)
     - Cavity barriers (PDF pp. 48 to 51, required locations by UK nation, checklist)
     - Cavity barriers and fire stops at party walls (PDF p. 52)
     - Masonry cladding (PDF pp. 53 to 56, cavity width, vent spacing, wall tie spacing)
     - Installing services (PDF p. 57, notching and drilling rules)
     - Differential movement (PDF pp. 58 to 61, gap allowances by storey)
  7. Summary (PDF p. 62)
  8. Reference documents and further reading (PDF p. 63)
- Most useful for: setting UK platform frame erection tolerances, sole plate and packing geometry, cavity barrier and vent layout, and differential movement gaps between a timber frame and masonry cladding.

#### Construction Manual of Prefabricated Timber House

- PDF: `Construction Manual Of Prefabricated Timber House.pdf`
- Extracted: [`construction_manual_extracted.md`](construction_manual_extracted.md)
- Online: https://www.itto.int/files/user/pdf/publications/PD12%2087/pd-12-87%20e.pdf (direct PDF, ITTO's own file archive; verified 2026-09-02, HTTP 200, content-type application/pdf, content-length 1417358 bytes, exact byte match with the local copy)
- About: Forest Research Institute Malaysia (FRIM) handbook produced for a FRIM/ITTO project, 1996, covering a single storey, low cost, prefabricated timber-framed house for Malaysia and similar tropical climates. A modelling agent gets full member sizes and a construction sequence for platform frame walls, floor and roof trusses built as factory panels, plus 9 appendix drawing sheets with exact panel and truss geometry.
- Contents:
  1. Introduction (p. 1; PDF p. 9)
  2. Fabrication system (pp. 2 to 4; PDF pp. 10 to 12) [pre-cut system, modular panel system, large size panel system, volume element system]
  3. Design of the house (pp. 5 to 7; PDF pp. 13 to 15) [post and beam versus timber-framed, balloon versus platform frame, wall panel make-up]
  4. Basic principles (pp. 8 to 12; PDF pp. 16 to 20) [modular dimensioning, load path, load-bearing versus non-load-bearing walls, panel-making tolerances, sequence of construction]
  5. General requirements and specification of material (pp. 13 to 16; PDF pp. 21 to 24) [timber grade and treatment, Table 1 quantities and sizes for every component group]
  6. Details of construction (pp. 17 to 38; PDF pp. 25 to 46) [setting out, footings, platform, wall panels, kitchen, roof trusses, doors and windows, railings and stairs, ceiling, services, finishing]
  7. Maintenance and repair (pp. 39 to 40; PDF pp. 47 to 48) [raised platform, exterior walls, interior, roof]
  8. References (p. 41; PDF p. 49)
  9. Appendix I, detailed technical drawings (PDF pp. 50 to 59) [9 sheets: plan and sections, panel layout, panel elevations, door and window details, platform details, panel connections, truss and roof framing]
- Most useful for: sizing and sequencing a small platform frame timber house built from prefabricated wall, floor and roof panels, with exact truss and panel geometry in the appendix drawings.

#### The Segal method

- PDF: `THE SEGAL METHOD - color.pdf`
- Extracted: [`segal_method_extracted.md`](segal_method_extracted.md)
- Online: https://jonbroome.co.uk/wp-content/uploads/2021/02/AJ-Segal-Special-Issue-The-Segal-Method-05-Nov-1986-reduced.pdf (direct PDF, hosted on Jon Broome's own site, he wrote the original article; verified 2026-09-02, HTTP 200, content-type application/pdf, 24.5 MB). The landing page is https://jonbroome.co.uk/?p=1221. Printed folio numbers below are inferred from spread order and the cover's handwritten "pp 31-68", they are not legible in the scan itself.
- About: The Architects' Journal special issue on Walter Segal's self build timber frame method, 5 November 1986, written by Jon Broome, Segal's joint architect on the Lewisham self build housing schemes. Covers detached one and two storey timber post and beam houses in England. A modelling agent gets the tartan grid logic, the post and beam frame with a floor level tie beam, and the clamped panel wall, floor, and roof build ups, all as a magazine feature rather than a construction manual, so no span tables or nailing schedules.
- Contents:
  1. Cover and contents (pp. cover to 31; PDF pp. 1 to 2)
  2. Walter Segal's approach (pp. 32 to 35; PDF pp. 3 to 4)
  3. The essential method (pp. 36 to 37; PDF p. 5)
  4. 1 General arrangement (p. 38; PDF p. 6)
  5. 2 Modular grid (p. 39; PDF p. 6)
  6. 3 Layout drawings (p. 40; PDF p. 7)
  7. 4 Structural layout (p. 40; PDF p. 7)
  8. 5 Calculations (p. 41; PDF p. 7)
  9. 6 Framing drawings (p. 41; PDF p. 7)
  10. 7 Schedule of materials (p. 42; PDF p. 8)
  11. 8 Catalogue of elements (p. 42; PDF p. 8)
  12. 9 Building instructions (p. 43; PDF p. 8)
  13. 10 Foundations (pp. 43 to 44; PDF pp. 8 to 9)
  14. 11 Structural frame (pp. 44 to 47; PDF pp. 9 to 10)
  15. 12 Roof (p. 48; PDF p. 11)
  16. 13 Floors (p. 49; PDF p. 11)
  17. 14 External walls (p. 50; PDF p. 12)
  18. 15 Windows (pp. 51 to 52; PDF pp. 12 to 13)
  19. 16 Partitions (p. 53; PDF p. 13)
  20. 17 Ceilings (p. 54; PDF p. 14)
  21. 18 Stairs and other features (p. 54; PDF p. 14)
  22. 19 Services (p. 55; PDF p. 14)
  23. The future (pp. 56 to 57; PDF p. 15)
- Most useful for: tartan grid planning, a post and beam self build timber frame with a floor level tie beam, and clamped infill wall, roof and floor build ups for a Segal method house.

### Cross laminated timber and mass timber

#### How to CLT

- PDF: `Arkemi - How to CLT Handbook.pdf`
- Extracted: [`how_to_clt_extracted.md`](how_to_clt_extracted.md)
- Online: https://arkemi.se/images/downloads/Arkemi_How-to-CLT_Handbook_30.pdf (direct PDF, content-length matches the repo copy byte for byte; verified 2026-09-02, HTTP 200, content-type application/pdf)
- About: Arkemi (Stockholm) architectural guidelines for cross laminated timber, second edition 2024, aimed at architects working in early design stages on Swedish residential buildings. A modelling agent gets a structural system taxonomy (panel, honeycomb, parting wall, hybrid, 3D-module), master panel and transport size limits, and dimensioned build-up tables for walls, floors and roofs.
- Contents:
  1. Cover and table of contents (pp. i-ii; PDF pp. 1-2)
  2. Introduction (pp. 2-7; PDF pp. 3-5) [acknowledgements, foreword, three-part workflow]
  3. CLT and Swedish forestry (pp. 8-21; PDF pp. 6-12) [sustainable forestry debate, designing with reduced impact, glossary]
  4. Collaborate with CLT (pp. 22-33; PDF pp. 13-18) [6 principles for architect-engineer collaboration]
  5. Design with CLT for early stages (pp. 34-49; PDF pp. 19-26) [structural systems: panel vs 3D-module, honeycomb, parting wall, hybrid; CLT elements: wall, floor, roof, stairs]
  6. Rules of thumb (pp. 50-63; PDF pp. 27-33) [master panel and transport limits, wall/slab/roof thickness rules, dimensioned build-up library]
  7. Postface (pp. 64-71; PDF pp. 34-37) [image references, bibliography]
  8. Back cover (p. 72; PDF p. 38) [download QR code]
- Most useful for: choosing a CLT structural system and sizing walls, floor slabs, roofs and openings for a 3 to 8 storey CLT residential building at early design stage.

#### The CLT Handbook, CLT structures, facts and planning

- PDF: `The CLT Handbook 2022 - facts and planning.pdf`
- Extracted: [`clt_handbook_2022_facts_and_planning_extracted.md`](clt_handbook_2022_facts_and_planning_extracted.md)
- Online: https://www.swedishwood.com/siteassets/5-publikationer/pdfer/clt-handbook-2019-eng-m-svensk-standard-2019.pdf (direct PDF, publisher's own site; verified 2026-09-02, HTTP 200, content-type application/pdf, content-length 16803491 bytes, matches the local file byte for byte)
- About: published by Swedish Wood (Svenskt Tra, Foreningen Sveriges Skogsindustrier), Stockholm, first edition 2019, lead author Anders Gustafsson (RISE). Covers CLT product facts, Eurocode 5 based structural design, joints, floor and wall systems, fire, acoustics, moisture and site handling for multi-storey timber buildings in a Nordic/European context. A modelling agent gets panel and board dimension limits, real cross-section layups by layer count and thickness, span and load preliminary sizing charts, joint and connection layouts with fastener spacing rules, wall and floor build-up thicknesses, and transport and lifting limits. Despite the "2022" in the filename, the PDF's own imprint dates it 2019. A separate UK edition, *design and detailing*, revised by Arup for UK codes and published in 2022 by the Confederation of Timber Industries, is covered in a companion summary (`manuals/The CLT Handbook 2022 - design and detailing.pdf`).
- Contents:
  1. CLT as a construction material (pp. 8 to 23; introduction, architect's view, manufacture, board and panel dimension tables, strength/fire/moisture properties, appearance classes, typical uses)
  2. Design systems for CLT (pp. 24 to 29; panel as beam/shell, preliminary floor thickness versus span and wall load versus height charts)
  3. Design of CLT structures (pp. 30 to 71; Eurocode 5 basis, material properties, beam theory, cross-section tables for 3 and 5 layer panels, plate theory, design software, worked examples)
  4. Joints and connections (pp. 72 to 89; fastener types, panel edge joints, connections to beams, wall to wall, wall to floor, wall to foundation and roof, screw/nail plate design, fastener spacing tables)
  5. Floor structures (pp. 90 to 109; flat, cassette/hollow and composite floor types, span table, deformation and vibration checks, fire and acoustic notes, connection details, worked example)
  6. Walls (pp. 110 to 132; panel dimensions and transport limits, static design, structure stability and overturning, fire and acoustic tables, wall cross-section build-ups, detailed connections, worked examples)
  7. CLT and fire (pp. 133 to 144; charring rates, effective cross-section method, fire resistance classes, worked examples)
  8. CLT and sound (pp. 145 to 156; acoustic vocabulary and Swedish code classes, floor and wall build-up sound performance tables)
  9. CLT, heat and moisture (pp. 157 to 163; thermal mass and moisture buffering, moisture movement, thermal insulation and U-value worked example)
  10. Purchasing and assembly (pp. 164 to 175; enquiry checklist, delivery/storage/transport limits, lifting methods and self-weight guide values, frame stabilisation, weather protection systems, moisture inspection)
  11. Symbols, bibliography, non-liability, Swedish Wood publications (pp. 176 to 188; notation glossary, cited standards, publisher terms, related handbooks)
- Most useful for: sizing CLT wall and floor panels and picking real cross-section layups for early design, laying out joints and connections between CLT walls, floors, foundations and roofs, and building up wall/floor sections with realistic thicknesses and transport/lifting limits.

#### The CLT Handbook, CLT structures, design and detailing

- PDF: `The CLT Handbook 2022 - design and detailing.pdf`
- Extracted: [`clt_handbook_2022_design_and_detailing_extracted.md`](clt_handbook_2022_design_and_detailing_extracted.md)
- Online: https://www.swedishwood.com/siteassets/5-publikationer/pdfer/clt-ukedition-2022.pdf (direct PDF; verified 2026-09-02, HTTP 200, content-type application/pdf, content-length 14133683 bytes matching the local file exactly)
- About: published by Swedish Forest Industries Federation (Swedish Wood) with Arup and the Confederation of Timber Industries, UK edition 1:2022, 156 pages. Covers CLT as a material, Eurocode 5 basis of design, out-of-plane and in-plane panel design with section-property tables, connection types and design equations, floor and wall design and build-ups, fire, acoustics, thermal comfort, and procurement and site erection. A modelling agent gets panel thickness and layer-count tables, screw/nail/dowel spacing rules, drawn wall-to-wall, wall-to-floor, wall-to-foundation and wall-to-roof connection details, and the erection/moisture sequence for a CLT building.
- Contents:
  1. CLT as a construction material (pp. 8 to 23; manufacture, board and panel dimensions, properties, appearance classes)
  2. Basis of design of CLT structures (pp. 24 to 33; loads, service classes, partial factors, material properties table)
  3. Design of CLT structures (pp. 34 to 51; out-of-plane and in-plane behaviour, design tables for 3 and 5-layer panel section properties)
  4. Connections (pp. 52 to 68; joint types, wall-to-wall/floor/foundation/roof details, screw and nail spacing tables)
  5. Floors (pp. 69 to 85; CLT slab, ribbed slab, CLT-concrete composite, deflection, vibration, example build-ups)
  6. Walls (pp. 86 to 97; shear walls, lateral stability, wall build-ups, connection details, worked example)
  7. CLT and fire safety (pp. 98 to 111; charring design, effective cross-section, protected/unprotected floor and wall examples)
  8. CLT and sound (pp. 112 to 130; floor and wall constructions, junction and flanking details)
  9. CLT and thermal comfort (pp. 131 to 135; thermal mass, condensation, U-value worked example)
  10. Procurement and site works (pp. 136 to 141; tendering, moisture protection, delivery, lifting, temporary stability)
  11. Back matter (pp. 142 to 156; symbols, bibliography, non-liability and copyright, Swedish CLT mills, Swedish Wood publications list)
- Most useful for: sizing CLT wall, floor and roof panel build-ups and thicknesses, laying out CLT-to-CLT connection geometry and fastener spacing, and getting fire, acoustic and moisture/erection detailing right for a CLT building model.

#### Canadian CLT Handbook, 2019 Edition

- PDF: `Canadian CLT Handbook 2019.pdf`
- Extracted: [`canadian_clt_handbook_2019_extracted.md`](canadian_clt_handbook_2019_extracted.md)
- Online: https://web.fpinnovations.ca/download/clt-handbook-2019-full-edition/ (publisher page with a gated "download the free PDF" button, requires a short form; verified 2026-09-02, HTTP 200, content-type text/html, page title confirms "CLT Handbook 2019 Full Edition")
- About: FPInnovations (Pointe-Claire, Quebec), the current North American reference on cross laminated timber, covering both Canadian CLT Handbook volumes in one 812-page PDF. A modelling agent gets CLT panel product data and stress grades, the CSA O86 structural design method for floors/roofs/walls, a full connections catalogue with drawn details, lateral (shear wall) design rules, lifting/handling/transport geometry, and a complete worked 8-storey mass timber building with member sizes and connection counts.
- Contents:
  1. Introduction to cross-laminated timber (PDF pp. 8-54) [product definition, standards, market data, built examples]
  2. Cross-laminated timber manufacturing (PDF pp. 55-106) [dimensions, tolerances, stress grades, manufacturing process, QA]
  3. Structural design of cross-laminated timber elements (PDF pp. 107-172) [modification factors, flatwise bending/shear, walls, beams/lintels, worked examples]
  4. Lateral design of cross-laminated timber buildings (PDF pp. 173-222) [shear wall aspect ratio, brackets and hold-downs, rocking behaviour]
  5. Connections in cross-laminated timber buildings (PDF pp. 223-298) [splines, half-laps, brackets, wall-to-floor/roof/foundation details, worked examples]
  6. Duration of load and creep factors for cross-laminated timber panels (PDF pp. 299-314) [KD factor, creep, mechanically fastened CLT]
  7. Vibration performance of cross-laminated timber floors and tall wood buildings (PDF pp. 315-362) [vibration-controlled span method, TCC floors, tall-building vibration]
  8. Fire performance of cross-laminated timber assemblies (PDF pp. 363-472) [charring rate method, fire testing, exit stair shafts]
  9. Acoustic performance of cross-laminated timber assemblies (PDF pp. 473-520) [STC/ASTC, wall and floor/ceiling assembly design examples]
  10. Building enclosure design of cross-laminated timber construction (PDF pp. 521-585) [heat/air/vapour/moisture control, construction moisture]
  11. Environmental performance of cross-laminated timber (PDF pp. 586-638) [life cycle assessment, wood supply, indoor air emissions]
  12. Lifting and handling of CLT elements (PDF pp. 639-708) [slinging systems, rigging calculations, transportation envelopes]
  13. Design example (PDF pp. 709-812) [8-storey building: loads, gravity/fire/lateral design, connections, full drawing set]
- Most useful for: sizing and detailing CLT floor, roof and wall panels; drawing panel-to-panel and wall-to-floor/foundation connections; laying out CLT shear walls; sequencing lifting and erection; reproducing a complete 8-storey mass timber building as a reference example.

#### Binderholz Solid Timber Manual

- PDF: `Binderholz - Solid Timber Manual.pdf`
- Extracted: [`binderholz_solid_timber_manual_extracted.md`](binderholz_solid_timber_manual_extracted.md)
- Online: https://www.binderholz.com/fileadmin/user_upload/pdf/products/solid-timber-manual.pdf (direct PDF, publisher's own file server; verified 2026-09-02, HTTP 200, content-type application/pdf, 248 pages matching the local copy)
- About: Binderholz (Austria) and Saint-Gobain Rigips Austria's joint product catalogue for CLT BBS cross laminated timber panels combined with Rigips dry lining systems. Aimed at architects, planners and builders working on solid timber residential and commercial buildings. A modelling agent gets 139 fully dimensioned, fire and acoustically tested exterior wall, interior wall, partition wall, roof and ceiling layer build-ups, plus a few fire-stop and wall-to-ceiling connection details. It does not give CLT panel production sizes, span tables or an erection sequence.
- Contents:
  1. Introduction (pp. 1 to 20; PDF pp. 1 to 20) - manual purpose, testing institutes behind the ratings, CLT BBS and Rigips product overview, advantages of timber construction
  2. Sustainability (pp. 21 to 48; PDF pp. 21 to 48) - forestry and carbon arguments, zero-waste manufacturing, environmental product declarations behind the ecology score on every datasheet
  3. Building physics (pp. 49 to 92; PDF pp. 49 to 92) - sound insulation and flanking transmission, heat insulation and humidity regulation, fire protection (fire resistance classes, CLT burn-off rates and formulas, fire-stop and wall-to-ceiling joint details)
  4. Exterior wall (pp. 93 to 148; PDF pp. 93 to 148) - 54 tested rear-ventilated, rendered and clad exterior wall assemblies, one dimensioned datasheet each
  5. Interior and partition wall (pp. 149 to 180; PDF pp. 149 to 180) - 26 tested single-leaf interior wall and double-leaf partition wall assemblies
  6. Roof (pp. 181 to 212; PDF pp. 181 to 212) - 26 tested steep (pitched) and flat roof assemblies
  7. Ceiling (pp. 213 to 248; PDF pp. 213 to 248) - 33 tested unfinished and suspended ceiling assemblies under a CLT BBS slab
- Most useful for: sourcing exact, tested layer build-ups (thicknesses, materials, fire resistance, U-value, sound insulation) for CLT BBS walls, roofs and ceilings, plus CLT BBS material constants and a handful of fire-stop and wall-to-ceiling connection details.

#### Building Systems by Stora Enso, 3 to 8 Storey Modular Element Buildings

- PDF: `Stora Enso Design Manual - Modular Element Buildings.pdf`
- Extracted: [`stora_enso_modular_element_buildings_extracted.md`](stora_enso_modular_element_buildings_extracted.md)
- Online: https://www.storaenso.com/-/media/Documents/Download-center/Documents/Product-brochures/Wood-products/Design-Manual-A4-Modular-element-buildings20161227finalversion-40EN.pdf (direct PDF, Stora Enso's own download center; verified 2026-09-02, HTTP 200, content-type application/pdf, content-length 13894243 bytes, exact byte match with the local copy)
- About: Stora Enso Division Wood Products, Building Solutions design manual, version 4.0, published 26 December 2016. Covers Stora Enso's CLT modular building system for wood multi-storey residential buildings, 3 to 8 storeys. A modelling agent gets a catalogue of wall, floor, roof and stair build-ups, a full set of module-to-module and module-to-ground connection drawings, and the erection sequence of a stacked-module building around a central corridor.
- Contents:
  1. Introduction and disclaimer (PDF pp. 3 to 5)
  2. Anatomy of the Stora Enso modular building system (PDF pp. 6 to 9) [anatomy of a modular building, anatomy of a modular element, element systems compared to on-site and 2D-panel construction]
  3. Architectural design guidelines (PDF pp. 10 to 16) [repetition and variation of modules, building typology, wet zones and technical shafts, apartment layout, case study floor plan and sections]
  4. Building System by Stora Enso (PDF pp. 17 to 28) [structural components and size limits, manufacturing process, acoustics, fire design, deformation and cracking, HVAC routing, bracing, seismic design, erection procedure sequence]
  5. Structural design (PDF pp. 29 to 85) [5.1 structural types, pp. 30 to 50: wall, floor, roof and stair build-up catalogue with fire and acoustic ratings; 5.2 structural details, pp. 51 to 85: 17 module joint drawings, 6 foundation drawings, 3 plan-corner drawings]
  6. Transportation and instructions for on-site assembly (PDF pp. 86 to 89) [transport of modules, principles of erection, moisture control plan, protection of walls, roofs and indoor conditions on site]
  7. Sustainability (PDF pp. 90 to 93) [sourced wood, energy efficiency, life cycle design, certification schemes]
  8. Stora Enso (PDF pp. 94 to 95) [company profile]
- Most useful for: sizing and detailing a CLT panel-and-slab modular residential building, its module-to-module and module-to-ground joints, and the floor-by-floor erection sequence of stacked room and technical modules around a central corridor and stair. Does not give span tables, load calculations, fastener schedules or a numeric module transport envelope.

#### Mass Timber Design Manual 2021

- PDF: `Mass Timber Design Manual 2021.pdf`
- Extracted: [`mass_timber_design_manual_2021_extracted.md`](mass_timber_design_manual_2021_extracted.md)
- Online: https://info.thinkwood.com/download/mass-timber-design-manual (publisher landing page with an email-gated download form, redirected from the URL printed in the PDF itself, info.thinkwood.com/masstimberdesignmanual; verified 2026-09-02, HTTP 200, text/html, page visibly names "Mass Timber Design Manual" and confirms it is the free first edition)
- About: WoodWorks (Wood Products Council) and Think Wood, US trade associations for the wood products industry, published this as a free awareness and marketing compilation for architects, engineers and developers working in commercial, multifamily, and civic mass timber buildings. A modelling agent gets the five mass timber product categories at a glance, roughly 20 built case studies with occasional structural grid or panel dimensions, and a plain-language walk through the 2021 IBC's new Type IV-A/B/C tall wood construction types. It is not a design or span reference: most technical chapters summarize an external paper and link out to it rather than reproducing its tables.
- Contents:
  1. Foreword (pp. 5 to 7; PDF pp. 5 to 7) [two personal essays from WoodWorks board members, no technical content]
  2. Introduction (pp. 8 to 9; PDF pp. 8 to 9) [how to use this manual, WoodWorks Innovation Network support]
  3. Mass Timber Products (pp. 10 to 29; PDF pp. 10 to 29) [CLT, DLT, NLT, glulam product pages; insurance; 2021 IBC construction types; case studies 77 Wade, Catalyst, Model-C]
  4. Timber Design Applications (pp. 30 to 55; PDF pp. 30 to 55) [case studies Candlewood Suites, Clay Creative, Hudson Office, Diamond Foods, Karuna; grid design, fire design, acoustics, floor vibration, connections, construction management, enclosure, moisture]
  5. Solutions for Building Taller (pp. 56 to 73; PDF pp. 56 to 73) [case studies Origine, 2150 Keith Drive; Type IV-A/B/C code tables, shaft wall and fire resistance rules, Tall With Timber tower case study]
  6. Mass Timber and Sustainability (pp. 74 to 95; PDF pp. 74 to 95) [case studies Platte Fifteen, Olver Design Building, Bullitt Center; forestry Q+A, carbon accounting, green building credits, Timber City research]
  7. Conclusion (pp. 96 to 97; PDF pp. 96 to 97) [closing summary and resource folder link]
  8. Sources (p. 98; PDF p. 98) [8 numbered endnotes with URLs]
- Most useful for: quick orientation to mass timber product types and realistic structural grid dimensions (25x25 to 30x30 ft) from built case studies, and to which IBC Type IV-A/B/C construction type allows how much exposed mass timber.

### General detailing and housing planning standards

#### Architect's Handbook of Construction Detailing

- PDF: `Architects Handbook of Construction Detailing.pdf`
- Extracted: [`architects_handbook_construction_detailing_extracted.md`](architects_handbook_construction_detailing_extracted.md)
- Online: https://www.wiley.com/en-us/architect's-handbook-of-construction-detailing-2nd-edition-p-9780470381915 (publisher product page, no direct download; purchase or borrow) and https://archive.org/details/architectshandbo0000ball_a4w2 (Internet Archive item, borrowable); verified 2026-09-02, HTTP 200 on both (text/html)
- About: John Wiley and Sons (Hoboken, New Jersey), second edition 2009, David Kent Ballast, FAIA, CSI. A general US architectural detailing reference, 178 short detail sheets across concrete, masonry, metal, wood, thermal/moisture, doors and windows, and finishes, each keyed to a CSI MasterFormat six-digit number. A modelling agent gets envelope and connection geometry (member sizes, clearances, fastener spacing, tolerances) for a named condition, not span tables or a build sequence; wood coverage is limited to platform and multistory light-frame wall sections, SIP panels, glulam connections, and shop millwork, plus scattered wood-relevant sheets elsewhere (brick veneer over wood studs, wood shingle eaves, a wood door, a wood window, wood strip and parquet flooring, generic stair layout geometry).
- Contents:
  1. Concrete details (pp. 1 to 53; PDF pp. 19 to 71) [slab-on-grade and cast-in-place tolerances; slab joints; architectural and precast concrete panels; GFRC]
  2. Masonry details (pp. 55 to 141; PDF pp. 72 to 158) [CMU, brick, and composite wall expansion joints; cavity walls; brick veneer over wood and steel stud backup; anchored stone veneer]
  3. Metal details (pp. 143 to 167; PDF pp. 160 to 184) [structural steel tolerances; steel support for masonry/precast/curtain walls; open web joists; generic stair layout geometry; metal stairs and guards]
  4. Wood details (pp. 169 to 201; PDF pp. 186 to 218) [platform and multistory frame sections at foundation, floor line, and roof; structural insulated panels; glulam beam, purlin, and column connections; cabinets, countertops, shelving, flush paneling]
  5. Thermal and moisture protection details (pp. 203 to 295; PDF pp. 219 to 311) [waterproofing; weather barrier concepts; EIFS; shingle, wood shingle, and tile roofing at eaves; built-up, modified bitumen, EPDM, and TPO membrane roofing; sealants; roof drains]
  6. Door and window details (pp. 297 to 345; PDF pp. 312 to 359) [steel, aluminum, and wood doors and frames; storefront and curtain wall glazing; aluminum, steel, and wood windows; interior glazed openings]
  7. Finish details (pp. 347 to 413; PDF pp. 361 to 427) [gypsum wallboard partitions and ceilings, wood and metal framed; ceramic tile; acoustical ceilings; stone and terrazzo flooring; wood parquet, strip, laminate, and resilient flooring]
- Most useful for: platform and multistory wood wall sections at the foundation and roof, hold-down and shear-transfer detailing, SIP wall/roof junctions, glulam beam-column-purlin connections, generic stair layout geometry, and wood shingle eave, wood door, wood window, and wood strip flooring assemblies.

#### London Housing Design Guide (interim edition, 2010)

- PDF: `London Housing Design Guide 2010.pdf`
- Extracted: [`london_housing_design_guide_2010_extracted.md`](london_housing_design_guide_2010_extracted.md)
- Online: https://www.london.gov.uk/sites/default/files/interim_london_housing_design_guide.pdf (direct PDF, hosted by the Greater London Authority, current successor to the London Development Agency which published it; verified 2026-09-02, HTTP 200, content-type application/pdf, content-length 2782360 bytes matching the local file size). Backup copy on the Internet Archive Wayback Machine at https://web.archive.org/web/20120522230915/http://www.designforlondon.gov.uk/uploads/media/Interim_London_Housing_Design_Guide.pdf, verified the same date, HTTP 200, application/pdf.
- About: Published by the London Development Agency for the Mayor of London, August 2010. A planning and space standards guide for new housing in London, not a construction manual: minimum dwelling floor areas by bedroom and person count, room sizes, ceiling heights, storage, private open space, circulation and stair widths, lift rules, parking, and wheelchair accessible housing standards. A modelling agent gets plan-layout constraints for any modelled dwelling, not framing or connection details.
- Contents:
  1. Foreword and introduction (pp. 4 to 10; PDF pp. 4 to 10)
  2. Summary Table of London Housing Design Guide Standards (pp. 11 to 17; PDF pp. 11 to 17) [every numbered standard in the guide, condensed into one table with Priority 1/2 marking]
  3. 1.0 Shaping Good Places (pp. 18 to 25; PDF pp. 18 to 25) [defining places, outdoor spaces and play provision]
  4. 2.0 Housing for a Diverse City (pp. 26 to 31; PDF pp. 26 to 31) [density matrix by PTAL band, residential mix and tenure]
  5. 3.0 From Street to Front Door (pp. 32 to 43; PDF pp. 32 to 43) [entrances, shared circulation cores, lifts and stairs, car parking, cycle storage, refuse]
  6. 4.0 Dwelling Space Standards (pp. 44 to 61; PDF pp. 44 to 61) [minimum GIA table by bedroom/person/storey, room sizes, circulation, bathrooms, storage, private open space]
  7. 5.0 Home as a Place of Retreat (pp. 62 to 69; PDF pp. 62 to 69) [privacy, dual aspect, noise, floor to ceiling heights, daylight and sunlight]
  8. 6.0 Climate Change Mitigation and Adaptation (pp. 70 to 79; PDF pp. 70 to 79) [Code for Sustainable Homes level, energy hierarchy, water, materials, ecology]
  9. 7.0 Managing the Design Process (pp. 80 to 89; PDF pp. 80 to 89) [client role, design team selection, RIBA stage process, not dimensional]
  10. Appendix 1, Space Standards Study (pp. 92 to 93; PDF pp. 92 to 93) [dimensioned room by room floor plans behind the GIA table, by occupancy]
  11. Appendix 2, Furniture Schedule (pp. 94 to 97; PDF pp. 94 to 97) [dimensioned kitchen, dining, living and bedroom furniture, sizes and quantities by dwelling size]
  12. Appendix 3, Wheelchair Accessible Housing Design Standards (pp. 96 to 103 in the source's own contents page, actually PDF pp. 98 to 103) [14 point checklist of wheelchair clearance and manoeuvring dimensions]
  13. Appendix 4, Definitions (p. 104; PDF p. 104) [GIA, habitable room, Lifetime Homes and other defined terms]
  14. Appendix 5, References and credits (pp. 105 to 106; PDF pp. 105 to 106)
- Most useful for: setting plan-layout constraints on modelled buildings, minimum dwelling and room floor areas by occupancy, ceiling heights, corridor and stair geometry, door widths, storage and private open space sizes, and furniture footprints for scaling room layouts.

### Woodworking and joinery

#### Woodworking, The Complete Step By Step Manual

- PDF: `Woodworking, The Complete Step By Step Manual.pdf`
- Extracted: [`woodworking_complete_step_by_step_manual_extracted.md`](woodworking_complete_step_by_step_manual_extracted.md)
- Online: https://archive.org/download/woodworking-the-complete-step-by-step-manual/Woodworking%2C%20The%20Complete%20Step%20By%20Step%20Manual.pdf (Internet Archive, direct PDF download, content-length matches the repo copy byte for byte at 80,230,307 bytes; verified 2026-09-02, HTTP 200, content-type application/pdf). Commercial product page for the same edition (ISBN 978-1-4654-9111-4): https://www.amazon.com/Woodworking-Complete-Step-step-Manual/dp/1465491112 (verified 2026-09-02, HTTP 200, text/html).
- About: DK (Dorling Kindersley), This American Edition 2020, previously published as Woodwork (2010). A hand-tool and light-machine furniture-making course, not a construction or framing manual. A modelling agent gets a catalogue of 35 named joints with cutting proportions and ratios, a directory of about 100 wood species, and 28 furniture projects with full dimensions and cutting lists.
- Contents:
  1. Introduction (pp. 8-9; PDF pp. 8-9)
  2. Tools (pp. 12-75; PDF pp. 12-75) [hand tools: saws, planes, chisels, measuring/marking, clamps; power tools: drills, routers, power saws, sanders; stationary machines: table saws, band saws, planers, lathes, mortisers, drill presses; commercial joining systems, fixings, workshop layout]
  3. Techniques, introduction and preparing wood (pp. 78-87; PDF pp. 78-87) [selecting wood, rough sizing allowances, facing and edging, cutting to final size]
  4. Joinery (pp. 88-145; PDF pp. 88-145) [35 named joints: edge joints, tongue-and-groove, halving, housing, miter, mortise-and-tenon family, bridle, comb, dovetail family, floating tenon, commercial connectors, each with cutting proportions]
  5. Jigs, turning, veneering, finishing, restoring (pp. 146-171; PDF pp. 146-171) [jigs and templates, spindle turning, veneering and lipping, finishing options table, antique furniture restoration]
  6. Woods (pp. 174-193; PDF pp. 174-193) [wood terms glossary, softwoods directory, hardwoods directory, veneers directory]
  7. Projects (pp. 196-387; PDF pp. 196-387) [28 furniture and household projects, cutting board to chair, each with overall dimensions, key joints, and a full cutting list]
  8. Appendix (pp. 388-400; PDF pp. 388-400) [glossary, index, acknowledgments, contributors, picture credits]
- Most useful for: the geometry, ratios, and proportions of hand-cut timber joints (mortise-and-tenon, dovetail, housing, halving, miter, bridle) and for scale reference dimensions of named furniture pieces.

#### Woodworking Wisdom and Know-How

- PDF: `Woodworking Wisdom  Know-How  Everything You Need to Design, Build and Create.pdf` (note the double space before "Know-How" in the filename)
- Extracted: [`woodworking_wisdom_and_know_how_extracted.md`](woodworking_wisdom_and_know_how_extracted.md)
- Online: https://archive.org/details/woodworking-wisdom-know-how-everything-you-need-to-design-build-and-create (Internet Archive item, borrowable; verified 2026-09-02, HTTP 200, text/html, page title and description match the book). Publisher product page: https://www.hachettebookgroup.com/titles/taunton-press/woodworking-wisdom-know-how/9780762465446/?lens=black-dog-leventhal (verified 2026-09-02, HTTP 200, text/html, mentions the title and ISBN). No direct free PDF found; a scan is listed on a scraping site (dokumen.pub) which is not linked here, use the archive.org loan or buy from the publisher/retailer link instead.
- About: Black Dog and Leventhal Publishers (2014), compiled by Josh Leventhal from about 150 Fine Woodworking magazine articles (Taunton Press, used by permission). A furniture-making and workshop book, not construction or framing. A modelling agent gets wood-movement clearances and a shrinkage table with an actual calculation formula, a comparative joint-strength test (18 joint types ranked by peak load), lumber sizing conventions (rough-sawn quarters, board footage, hardwood grading), and about 45 furniture, box, and cabinet projects, several with named member dimensions (a trestle table's wedged through-tenon, a student tool-chest size range, dated Shaker antiques with full dimensions).
- Contents:
  1. Types and species of wood (PDF p.13) [cherry, maple, walnut, oak, pine, mahogany, ebony identification; plywood; reclaimed wood]
  2. Shopping for lumber (PDF p.74) [rough-sawn quarter system, board foot, NHLA hardwood grades]
  3. Grain, figure, moisture, and movement (PDF p.86) [wood grain and figure types; moisture content and shrinkage tables; wood-movement clearances for breadboard ends, doors, drawers, tabletops]
  4. Hand tools (PDF p.125) [handsaws, handplanes, scrapers, chisels, sharpening]
  5. Power tools (PDF p.210) [tablesaw, bandsaw, miter saw, routers, drill press]
  6. Other tools and accessories (PDF p.277) [measuring, clamping, glue, screws, jigs]
  7. Workshop plans and layouts (PDF p.324) [shop floor plans of all sizes, wiring, lighting]
  8. Workbenches and storage (PDF p.383) [two full workbench builds with member sizes, vises, sawhorses, shop storage]
  9. Workshop safety (PDF p.466) [first aid, dust collection]
  10. Developing designs and organizing projects (PDF p.494) [design process, mock-ups]
  11. Milling and shaping wood (PDF p.524) [milling, ripping, resawing, tapers, moldings]
  12. Joinery (PDF p.613) [18-joint strength comparison test; dadoes and rabbets; miter; mortise and tenon including through, curved-work, and pegged variants; dovetails including slope ratios and layout; biscuit, dowel, and rule joints]
  13. Bending (PDF p.760) [steam-bending time and temperature rules, free-form bending, laminated bending ply counts]
  14. Turning wood and making curves (PDF p.795) [spindle and faceplate turning, curves by hand and bandsaw]
  15. Carving (PDF p.847) [tools, surface and applied carving]
  16. Veneer, marquetry, and inlay (PDF p.875) [veneering, marquetry, stringing and banding]
  17. Finishing tools and fundamentals (PDF p.948) [finish types, application, brushes, spraying]
  18. Preparing and sanding wood (PDF p.982) [sanding technique and sequence]
  19. Coloring and dyeing (PDF p.1032) [dyes, gel stains]
  20. Finish types and recipes (PDF p.1056) [French polish, shellac, lacquer, varnish, wax, milk paint, water-based, named finish recipes with mixing ratios]
  21. Specific woods and special effects (PDF p.1124) [species-specific finishing, patina, texturing]
  22. Fixes and troubleshooting (PDF p.1168) [finishing repairs]
  23. The language of furniture construction (PDF p.1192) [illustrated furniture-parts glossary]
  24. Boxes and small items (PDF p.1201) [tool chest, blanket chest, picture frame, cutting board, chessboard, turned pen and candlesticks]
  25. Chairs and beds (PDF p.1303) [Windsor rocker, benches, Adirondack chair with named curve radii, five bed-building methods]
  26. Tables and desks (PDF p.1403) [side tables, trestle table with wedged through-tenon at an 8-degree angle, drawer table, desk]
  27. Cabinets and shelves (PDF p.1542) [cabinet backs, book rack, wall cabinet, vanity, bombe chest, console, hutch, mudroom built-in]
  28. Doors, drawers, legs, and hardware (PDF p.1634) [door types and gaps, cabriole and pad-foot legs, bracket feet, drawer fitting, drawer-pull sizing rules]
  29. 18th century designs (PDF p.1727) [corner chair, tea table, Queen Anne lowboy]
  30. Shaker designs (PDF p.1761) [door, drawer, molding, knob, and leg profiles; two dated antiques with full dimensions]
  31. Arts and Crafts designs (PDF p.1792) [Morris chair, coffee table, cabinet, leaded-glass doors]
- Most useful for: wood-movement clearances and shrinkage data for sizing solid-wood members and joints; comparative joint strength and proportions (mortise and tenon, dovetail, half-lap, bridle); lumber nominal-versus-actual sizing; and furniture and shop-fixture member dimensions where a modelling task needs a plausible chair, table, box, or workbench rather than a building structure.
