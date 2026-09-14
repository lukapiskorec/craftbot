# Cost review, experiment 16, Fable run

Written by CraftBot after the close-out, 2026-09-14, off the record of the run. Findings only, nothing changed. The question: was the six-agent team as cheap as it could have been, and did the changes made after the experiment 15 audit (tiers, a fresh Builder per version, parallel Inspectors on subsets, the pair threshold, changed views only, lean reads, measurement) pay off?

## 1. What the run cost

Context at return and tool calls, from the task notifications. "Sonnet" marks the mechanical tier.

| Agent | Spawn | Context at return | Calls | Note |
|---|---|---|---|---|
| Designer | concept stage | 179k | 46 | spawned one Researcher |
| Researcher (Sonnet) | one question set, 8 questions | about 240k | 78 | 17 manuals opened at index level, 6 read, 11 snippets |
| Runner (Sonnet) | standing, 8 messages | 15k to 29k | 1 to 2 per message | |
| Builder | v01 | 234k | 58 | no Inspectors (32 pairs, over the threshold) |
| Designer, fresh | eight v01 questions | 81k | 10 | |
| Builder | v02 | 207k | 51 | two Inspectors, sizes not reported |
| Builder | v03, first attempt | unknown | unknown | usage-limit cut-off after patching the script |
| Builder | v03, restart | 162k | 54 | three Inspectors, sizes not reported |
| Designer, resumed | phase 2 round | 229k (from 179k) | 61 (from 46) | comparison Inspector (Sonnet) 89k, 25 calls |
| Builder | v04 | 256k | 59 | Inspectors (Sonnet) 98k / 23 and 109k / 27 |
| Designer, fresh | three v04 count questions | 38k | 8 | |
| CraftBot | the session | not measured | about 45 | reads: concept, notes files, requirements, comparison table |

Eighteen spawns in all: 1 Designer resumed once plus 2 fresh, 5 Builders (one cut off), 1 Researcher, 7 Inspectors, 1 Runner. Wall clock about three hours of agent time. One usage-limit cut-off.

The bill is context times calls, not context at return. With context growing roughly linearly over an agent's calls, the cache-read volume is about half the final context times the calls. On that estimate:

| Tier | Agents | Estimated cache reads |
|---|---|---|
| Fable | four Builders | about 24M tokens (13.6M + 10.6M + 8.7M + 15.1M, halved) |
| Fable | Designer, three spawns | about 8M (concept 4.1M, phase 2 resume 3.1M, the two fresh ones 0.6M) |
| Fable | CraftBot | under 3M |
| Sonnet | Researcher | about 9.4M |
| Sonnet | seven Inspectors | about 8M (three measured at 1.1M to 1.5M each, four estimated alike) |
| Sonnet | Runner | about 0.2M |

So roughly 35M on Fable and 18M on Sonnet, and the four Builders are about half of the whole run.

## 2. Against the experiment 15 baseline

| | Experiment 15 | Experiment 16 |
|---|---|---|
| Builder | one, 270k over 73 calls across three forced restarts | four fresh, 162k to 256k, 51 to 59 calls each |
| Designer | 230k over 48 calls plus four resumes for two-line questions | 179k, one resume for phase 2 (to 229k), two fresh at 81k and 38k for questions |
| Inspectors | 100 to 150k each, all 49 views, on Fable | 89k to 109k each, 10 to 20 views, on Sonnet |
| Researcher | about 150k on Fable | about 240k on Sonnet |
| Runner | 31k over 15 calls | 29k over about 12 calls |
| Cut-offs | four, each a cold cache and a 60 to 80k re-read | one; the patch was on disk, the restart diffed it and continued |

Which post-15 changes paid off:

- Tiers: eight of eighteen spawns ran on Sonnet, about a third of the cache reads. Paid off, and the Sonnet Inspectors caught the one defect the checks could not see (the apex stubs).
- Fresh Builder per version: the one cut-off cost about one cold start, not a chain of restarts, because `version_notes.md` and the patched script were the memory. Paid off.
- Pair threshold: v01 at 32 pairs got no Inspector. Paid off, small.
- Fresh Designer for questions: 81k and 38k against a resume of a 180k to 230k agent. Paid off.
- Lean reads: the Builder never opened `sources.md`, the Runner stayed under 30k. Paid off.
- Parallel Inspectors on subsets: partly. Subsets were 10 to 20 views, and each Inspector still ended near 100k. The saving against one Inspector on 40 views is real, but see finding 3.
- Changed views only: v03 rendered with `--only`, then the full set anyway because it converged, as the rule says. The rule is right for the record and costs little (render time 67 s); the cost is in who reads the views, not in rendering them.

## 3. Where the tokens could still go down

Ordered by estimated saving.

1. **A regression Inspector on an unchanged family.** v04's box Inspector read 18 views (109k, 27 calls) to confirm the box had not changed, while the script asserted the box unchanged and the checks were clean. v03's box Inspector did the same on 9 views. Rule to add: no Inspector on a family the version did not touch when the checks are clean; the Inspector on the changed family gets the orbits and the changed-family views only. Saving about 100k per version, about 250k here.

2. **The Builders' call count.** Each Builder spent 51 to 59 calls and ended at 160k to 260k, two to three times the 80k cold start the cost rules assume. From the notes, the calls go to reading the 640 to 824 line script (10 to 13k tokens per read, read more than once after edits), render logs, diagnostic renders (v02 hid collections to isolate the stubs), Blender probes on the `.blend` (v02, v03 and v04 all probed vertex spans by hand), and re-rendering close-ups the Inspectors could not read. Three measures, each worth a few tens of k per version: read only the function bodies to change (a grep and a line range) instead of the whole file; a probe script in `tools/` that prints an object's bounds and vertex span by name, so a probe is one call and not a written Blender snippet; the stub check below, so the diagnostic renders are not needed. Together perhaps 50 to 80k per Builder, 200 to 300k over the run, and fewer chances to hit a usage limit mid-version.

3. **An Inspector verifying a Builder-checked line.** R-21 (splice positions) is a `builder` check in `requirements.md`, and the v03 Builder confirmed it with a probe on the `.blend`. It still rendered eight close-up views (27 to 34, two of them at a zoom the Inspector could not read) and spawned a third Inspector for them. Rule: an Inspector never verifies a `script` or `builder` line; it gets `inspector` lines only. Saving about 60 to 80k and a few Builder calls in v03.

4. **The Researcher's question set.** 240k and 78 calls is the largest single mechanical spend and 60 percent more than the experiment 15 Researcher. Eight questions, three of which (thin sections, tall studs, clerestory) the Designer could predict as "not covered" because the brief demands what no manual has. Rules: at most five questions per Researcher; the Designer marks the ones it expects to be departures so the Researcher stops at the index level for them; one PDF page per figure, cropped once. Saving perhaps 80 to 100k.

5. **Resuming the concept Designer for phase 2.** The resume added 50k of context over 15 calls, but every one of those calls carried about 200k, about 3M cache reads. A fresh Designer reading `concept.md`, `design_notes.md`, `version_notes.md` and `inspection_v03.md` would have started near 60k; the photo rule set it needs is in `concept.md`, and the comparison Inspector reads the photos itself. The workflow says resume for phase 2; this run says a fresh one would have been three to four times cheaper for the same output. Saving about 2M cache reads.

6. **The Runner's confirmation round-trip.** Before the run close-out the Runner asked CraftBot to confirm that the rationale and callouts were final (one extra message, 28k, no work). Its role can say that CraftBot's `run` message is that confirmation. Saving one round-trip.

7. **Inspector part files.** The v02 box Inspector and the v04 ring Inspector returned their tables inline instead of writing `inspection_vXX_<part>.md`, and the Builder wrote the file for them. A few k each, and the Builder's context grows by the table. The spawn prompt should say the part file is a required hand-off, as the v04 notes suggest.

Not a saving, checked and rejected: spawning the v02 Builder in parallel with the Designer that answered the v01 questions. The splice answer landed mid-version and needed v03, but v03 was needed anyway for the apex stubs the v02 Inspectors found, so the parallel spawn cost nothing and saved six minutes.

## 4. Tool gaps that cost tokens

- **A stub check.** The 22 apex webs passed the overlap check (a stub overlaps nothing) and the contact check (it touches its chord) for two versions, and were found by an Inspector, then pinned by the Builder with two diagnostic renders and a probe. A check that flags any member whose vertex span is under a fraction of its intended length is a script-side assertion (the v03 script has one over `WEB_ENDS`); a generic version would need the intended endpoints, which `bar` and `member` know when they build the piece. Recording the intended length as a custom property at build time and checking it in `check_contacts.py` would make it free.
- **A named probe.** Every Builder wrote a Blender snippet to list an object's bounds. One script (`probe.py name_glob`) would replace those calls.
- **Close-up framing.** Two Inspectors could not read views at the set's zoom (v02: joints, corner, leaf; v03: splices), each costing a re-render and a second look. The v03 notes give the rule (the frame is about 2.1 times the focus radius; a 120 mm member needs a radius under 1.2 m to read); `views_template.py` should carry it.

## 5. Numbers to carry as the next baseline

Per version, this run: one Builder at 160 to 260k over 50 to 60 calls, two Inspectors at about 100k over 25 calls, a Runner call at 20 to 30k over 2 calls. Per run: one Designer at 180k plus a phase-2 round, one Researcher at 240k, fresh Designers at 40 to 80k per question set. A fix on this list that lands should show up as a Builder under 150k or an Inspector under 60k in the next run's section 8.
