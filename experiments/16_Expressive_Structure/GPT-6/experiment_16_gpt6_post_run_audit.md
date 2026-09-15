# Experiment 16 GPT-6: post-run efficiency audit and tooling proposals

Written 2026-09-15, after the experiment was concluded. This is a separate retrospective requested by the user, not another design phase. It is not appended to the experiment prompt history or archived conversation, and it does not change the model, requirements, rationale, viewer, skills or tools. All recommendations below are proposals for later review.

## 1. Conclusion

The revised team workflow worked in several important respects: different Builders owned v01 and v02; research and inspection used the cheaper model; one focused Designer resolved the base datum; file handoffs preserved completed work through interruptions; and no third version was created without a defect to fix. The separate full-foot bearing assertion was particularly valuable: it found a real geometric support deficit despite zero overlaps and zero floating members.

There is still substantial avoidable processing. The largest opportunities are the orchestrator's repeated wait/status turns, oversized batched reads that were truncated and then reread, repeated full inspections of a local correction, and close-out compatibility work that required extensive model reasoning. The correct skills were generally selected, but loading was not uniformly correct or demonstrably complete. The Runner missed its prescribed workflow sections, and the Researcher's claimed PDF consultation is not supported by its tool record.

No reliable percentage saving against Experiment 15 can be claimed. That baseline describes a larger, three-building run with different models, views, interruptions and reporting metrics. This audit establishes a measured baseline for this GPT-6 run instead.

## 2. Evidence and accounting method

Reviewed:

- The frozen [experiment conversation](experiment_16_gpt6_conversation.jsonl), its agent spawns, progress messages and tool outputs. This snapshot excludes the present audit and ends before the final user-facing completion response.
- Nine child-session JSONL logs in `C:/Users/lukap/.codex/sessions/2026/09/14/` and `2026/09/15/`, selected by their parent-thread IDs, not by unrelated session contents. These contain their completed work and final returns.
- The run's concept, sources, requirements, version notes, inspections, close-out reports, scripts and rationale.
- `.claude/agents/`, `.codex/agents/`, the relevant `skills/` instructions, the existing `tools/` implementations and the two change commits discussed below.

For each thread, the token table uses the last available `event_msg` / `token_count` / `info.total_token_usage` record. Cumulative records are not summed within a thread. The child counters were monotonic across continuations; their first counters start with their own initial requests rather than inheriting the parent's accumulated usage. Threads are then summed once each. This avoids counting cached input again as an additional category or adding reasoning output on top of the output field that contains it.

These are logged token-processing counters, not a dollar invoice. Cached tokens are still input tokens; they are not equivalent in cost to uncached input. No pricing or savings in dollars is estimated. Peak request input is the maximum reported `last_token_usage.input_tokens`, not the total size of a transcript or a guaranteed measure of unique knowledge in context.

Tool requests below count top-level `function_call` and `custom_tool_call` records. An `exec` can contain several nested operations, loops or batched reads, so these are not counts of every shell process or underlying tool invocation.

### Measured usage

| Agent | Logged model | Input tokens | Cached input | Output tokens | Peak request input | Top-level tool requests |
|---|---|---:|---:|---:|---:|---:|
| CraftBot/root, archived snapshot | gpt-6-astra | 9,283,605 | 8,996,864 | 25,934 | 113,969 | 124 |
| Concept + phase-2 Designer | gpt-6-astra | 3,149,783 | 2,975,872 | 23,722 | 114,143 | 36 |
| Focused base-detail Designer | gpt-6-astra | 201,741 | 164,480 | 1,698 | 34,037 | 6 |
| Builder v01 | gpt-6-astra | 3,020,716 | 2,866,688 | 20,581 | 95,906 | 40 |
| Builder v02 | gpt-6-astra | 2,218,248 | 2,054,528 | 7,921 | 91,999 | 29 |
| Researcher | gpt-5.6-luna | 992,599 | 918,784 | 8,549 | 73,235 | 17 |
| Inspector v01 | gpt-5.6-luna | 394,620 | 333,312 | 4,659 | 70,352 | 9 |
| Inspector v02 | gpt-5.6-luna | 291,143 | 235,648 | 4,149 | 64,451 | 9 |
| Comparison Inspector | gpt-5.6-luna | 875,288 | 810,752 | 6,813 | 90,396 | 16 |
| Standing Runner | gpt-5.6-luna | 3,019,974 | 2,835,456 | 14,902 | 77,340 | 52 |
| **Sum of these snapshots** | | **23,447,717** | **22,192,384** | **118,928** | not additive | **338** |

The sum is 23,566,645 input-plus-output tokens. Uncached input is 1,255,333 tokens; 94.65% of input is reported cached. Child agents account for 14,164,112 input tokens. Root alone accounts for 39.59% of the combined input processing. The final root completion response and any events after the frozen archive are not included, so this is a bounded accounting snapshot rather than a claim of a complete billing total.

The original rationale said token totals were unavailable because they were not exposed in agent returns. That statement described the information available to the orchestration at handoff, but it is not a limitation of the retained local logs. This retrospective supplies the missing measurements without rewriting the concluded rationale. Turn-context records also identify the exact judgement model as `gpt-6-astra`; the run-time documents reported only the GPT-6 family.

### Session identifiers for reproducibility

Root archive thread: `01a0a09e-9832-7061-978f-70842387639f`.

| Agent | Local session ID |
|---|---|
| Designer | `01a0a0a1-3d33-7b70-b400-3345a8e01298` |
| Base Designer | `01a0a0ab-e575-7572-89e5-3be6ddebc88b` |
| Builder v01 | `01a0a0aa-1e9a-7450-905d-ffc26066d3d2` |
| Builder v02 | `01a0a1b1-f679-7b52-908b-6caec220c425` |
| Researcher | `01a0a0a3-8136-72c0-b8da-c2fb1dcca738` |
| Inspector v01 | `01a0a1ac-9830-7091-a4f6-23b7355da535` |
| Inspector v02 | `01a0a1b5-22bc-71a0-9cfc-f7ff479d1e77` |
| Comparison Inspector | `01a0a355-1360-7312-8fac-1e7581657678` |
| Runner | `01a0a0a1-a6b5-7641-ac8c-c81ed4bb7b58` |

The comparison Inspector's file is under September 15; the other child files are under September 14. Filenames are `rollout-<local-start-time>-<session-id>.jsonl`. Ordinal references below identify individual records in these logs. Child logs were inspected in place and are not newly copied into the concluded archive.

## 3. Effect of changes introduced after Experiment 15

Commit `39f99de` introduced the cost rules, structural-logic skill, explicit reading table, model tiers, fresh Builders, focused Designer questions, inspection subsets, pair threshold and opt-in variations. Commit `ddfba1b` added the Codex entry-point adapter and six custom-agent profiles. Both predate this run. The Cycles pipeline and rendering fixes were also present, but this run used the standard diagnostic render workflow; there is no evidence that those presentation changes reduced this run's token usage.

| Change | What happened in Experiment 16 | Assessment |
|---|---|---|
| Cheaper mechanical tier | Researcher, three Inspectors and Runner all logged `gpt-5.6-luna`; judgement agents logged `gpt-6-astra` | Applied correctly. Monetary benefit cannot be calculated from this audit alone. |
| Fresh Builder per version | Separate v01 and v02 agents; interrupted work resumed within its own version | Applied correctly. Resuming an interrupted v02 handoff was not reuse across versions. |
| Focused fresh Designer for small questions | Base-datum question resolved in six top-level requests, peak input 34,037 | Useful isolation. It was still given more files/history than its narrow question required. |
| File handoffs | Saved scripts, render outputs and Inspector report survived usage-limit interruptions | Effective. On the second continuation, the completed v02 inspection and 8/8 close-out were recognized instead of rerendered. |
| Structural-logic always loaded by main Designer/Builders | Present in their read calls; load paths and independent review were recorded | Valuable. Full-foot checking went beyond generic collision/contact tests. Read truncation weakens blanket claims of complete loading. |
| No Inspector above 20 pairs | Initial 86 clashes were corrected before the first rendered/inspected version | No expensive inspection was performed on the bad assembly. It also avoided a rendered diagnostic iteration, a pragmatic deviation from the literal render-first loop. |
| View subsets and changed-view policy | One room Inspector per version; both read all 19 views; comparison read 17 model views plus 11 references | Role separation worked, but view scope remained broad. v02 was a phase-ending version, so its full render set followed the current rule. Narrower inspection would require an explicit policy distinction. |
| Default one variation | One building was designed | Correct. Multi-variation machinery was unnecessary but appeared in some full-workflow reads. |
| Ten-line returns / lean handoffs | Final returns were generally short; body reports and repeated reads were much longer | Partly successful. Short final messages did not prevent growth in the agents' contexts or duplicated documentation. |
| Cost measurement at returns | Agents reported totals unavailable | Not implemented operationally. No automatic usage metadata arrived in return notifications; the workflow assumed a reporting mechanism this harness did not provide. Local JSONL counters fill the gap after the fact. |
| Codex adapters reuse canonical roles | Custom agents loaded canonical role definitions | Basic role dispatch worked. The wrapper chain was confused with the actual workflow by Runner; transcript, shell and validator compatibility remained unresolved infrastructure work. |

The Experiment-15 commit cites a Builder context around 270k and Designer around 230k. Here peak logged request input stayed around 96k for the Builders and 114k for the main Designer. That is encouraging evidence of smaller working contexts, but the prior figures use a different reporting basis and a larger problem. It does not establish a controlled percentage improvement.

## 4. Did agents load the correct skills?

Expected reads come from the role files and their explicitly named conditional skills. A filename in a request proves that a read was requested; it does not prove that the entire returned text reached the agent. Several output batches were clipped by the outer `functions.exec` limit even though the inner shell calls allowed more output.

| Agent | Evidence from its own tool calls | Verdict |
|---|---|---|
| Root | Read the Codex wrapper, canonical entry point, CraftBot role, workflow and writing-design-rationale; revisited workflow chunks after truncation | Appropriate orchestrator selection. It later read more source-table/report content than its strict summary-only role prescribed. |
| Main Designer | Requested workflow, reading-visual-references, structural-logic, working-from-reference-documents, timber-framing, roof-framing-and-sheathing and non-orthogonal-geometry | Correct selection. Initial batch at ordinal 27 returned 20,521 tokens into a 10k outer budget. Four skills were reread successfully at ordinal 44; a second full workflow read at 55 also truncated. Do not claim perfectly verified full loading of every intended section. |
| Builder v01 | Requested procedural-geometry, structural-logic, verifying-models, the three timber/roof/non-orthogonal conditionals, API/README and workflow Rules/Mechanics | Correct selection and initial workflow section targeting. Ordinal 30 batch contained 26,729 tokens and truncated; ordinal 50 reread the three conditional skills and API without truncation. The larger first packet unnecessarily mixed instructions and handoffs. |
| Builder v02 | Requested the same relevant skills, plus both entry-point wrappers and a full workflow; reread several skills and later the Rules section | Correct subject coverage, inefficient loading. Read/output ordinals 37/50, 54/58 and 60/64 were truncated: 18,943, 15,183 and 13,129 original tokens respectively. The final packet needed for a local bevel was nearly as large as v01's working context. |
| Focused base Designer | Read its role plus full concept, requirements, design notes, agent and brief; no direct `skills/` read in its six-request session | Incomplete evidence for the conditionals named by its spawn. The role's small-question exception also says to read only a narrow handoff set, creating ambiguity with the parent's demand for all startup skills. Define the intended small-question instruction packet explicitly in a future revision. |
| Researcher | Requested working-from-reference-documents, workflow, reading-visual-references and manual index | Correct names, poor delivery discipline. One 26,272-token batch truncated; later searches do not establish complete loading of the prescribed manual workflow/index or full selected manual summaries. Its actual source consultation has a separate gap below. |
| v01 and v02 room Inspectors | Each loaded verifying-models in untruncated output; used textual photo rules rather than actual source-image comparison | Correct. reading-visual-references was not necessary for the assigned textual-rule pass and was not silently added. |
| Comparison Inspector | Loaded verifying-models and explicitly assigned reading-visual-references in untruncated output | Correct. It received 28 image payloads: 17 model views, five photos and six manual snippets. |
| Runner | Read its role, `.agents/skills/run-experiment/SKILL.md` and `.claude/skills/run-experiment/SKILL.md`; searched the latter for close-out sections | Incorrect destination. Its full record contains no read of `skills/running-craftbot-experiment/SKILL.md`, which is where its prescribed Mechanics/Outputs sections actually reside. It used scripts and parent messages to complete the work. |

`unslop` was not available in the session's skill catalog; its conditional omission is not a defect. Not loading extending-previous-models was correct: this was a new independent design, not an extension of another run. A 500 mm repetitive frame grid alone did not require adding modular-grids-and-panelization to the requested skill set. The timber, faceted roof and non-orthogonal conditionals were appropriate.

### Source-consultation discrepancy

The Researcher's `sources.md`, section 2, states that exact local PDF pages were consulted. Its complete tool record instead shows `rg`/`Get-Content` searches over extracted summaries and shared `references/captions.md`, plus a listing of PDF filenames. There is no PDF page read, raster extraction, image-view call or delivered image payload. Its selected manual summaries were searched and partly sliced, not read completely as its role prescribed.

Therefore the PDF-consultation claim is unsupported by that agent's record. The main Designer did receive 16 images, comprising the five input photographs and 11 shared snippets; Builders and the later comparison Inspector also received figure images. Those later visual checks support some figure-based decisions but do not retroactively establish the Researcher's claimed primary-source consultation. Nor does the existence of an earlier caption prove that this agent read its source page.

This is a provenance and verification finding, not a recommendation to remove source review for speed. A future pass should load the exact required pages/crops with an explicit consultation record, and distinguish text-summary reuse from actual PDF inspection. The Designer's corrections to stale dimensions and stud-table/attachment wording also show why those boundaries matter. This audit records the discrepancy without altering the concluded sources file.

## 5. Where further token efficiency is available

### A. Reduce orchestrator resumptions and duplicate status work

The archived root contains 45 sleep requests, four agent waits, six agent listings, 19 messages, 11 follow-up tasks and five spawns, against 34 `exec` requests. That is 90 coordination/wait requests out of 124. Many turns reported that an unchanged inspection was still running. Root processed 9.28 million input tokens despite not creating the geometry or reading render images.

Frequent user updates were required by the active host instructions, so simply waiting silently for many minutes would not have complied. Future optimization should address the mechanism: event-driven completions, milestone notifications from agents, and a compact orchestration context that does not reprocess long prior tool output for each wait. Reducing redundant reminders and listings is available within the existing communication constraint. A precise savings estimate would require a controlled replay; most repeated input was cached.

### B. Budget the outer read packet, not only each inner command

The truncation examples above are direct evidence, not guesses about verbosity. Parallel reads reduced shell latency but combined more content than the outer output budget could return. Agents then reread entire skills, sometimes clipping the replacement batch again. Some instructions were potentially omitted while their read cost was still incurred.

Candidate future rule: keep a bounded packet of required sections under the outer budget, make returned-file/section completion explicit, and fetch only the missing tail if truncation occurs. Role-specific workflow sections should replace full workflow reads. Entry-point adapters are for starting the orchestrator; reading both again in every Builder is not useful construction context. Do not replace mandatory instruction reading with summaries unless the instruction itself allows that.

### C. Distinguish complete render coverage from inspection delta

The two room Inspectors each received 19 image payloads. v02 only changed the lowest 90 mm of column chords, yet repeated a full 19-view inspection. The comparison Inspector received another 17 model images and 11 reference images, growing to 90,396 input tokens in its final request. In total, the three Inspectors received 66 image payloads and processed 1,561,051 input tokens.

Possible later policy: retain a full phase-ending render set, but give a delta Inspector the base/underside views, mandatory shared context views and prior findings; reserve the actual-photo comparison for matched exterior/interior and roof-profile images. Any family without new evidence can retain the previous inspection with an explicit unchanged-geometry record. This is a policy proposal, not a claim that the current final-version full-render rule was violated. Do not reduce the two-channel check to an assertion that unchanged names prove unchanged geometry.

For this one-room building, additional parallel Inspectors would duplicate startup and shared views. It is not automatically a token saving. Parallel subsets are more attractive when there are genuinely separable storeys or variations.

### D. Keep new Builders fresh, but make their packets smaller

The fresh-v02 decision was correct. Nevertheless, v02 processed 2.22 million input tokens for a local bevel and bearing assertion, reaching 91,999 tokens in one request. Its instruction rereads, six shared manual figures and full inspection coordination account for work beyond the small code change.

The four judgement-agent spawns omitted `fork_turns`, selecting the runtime's default history inheritance; mechanical agents used `fork_turns="none"`. Explicit file-based fresh starts are worth reviewing, especially for the base-detail Designer. However, first-request input was only about 20.6k for judgement children versus 15.7–16.2k for mechanical children. The logs do not support blaming the entire later context size on copied parent history; required instructions, file reads, images and ongoing messages made it grow. Do not promise a specific saving from changing the fork flag alone.

### E. Put meaningful bearing assertions before the first render

v01's clean overlap/contact result was followed by discovery of a maximum 0.753 mm unsupported foot edge. v02 fixed it and proved the new test failed on the inherited geometry before passing the correction. This is good verification, but placing that footprint assertion in the initial preflight could have avoided a second geometry/render/inspection/export cycle for this particular defect.

Do not remove the assertion or weaken tolerance to save a version. The next run should use an explicit support-area contract where full bearing is a requirement. Constant-value assertions and material tags alone are much weaker evidence than assertions over the generated mesh.

### F. Make close-out a bounded operation and validate with the real validator

The Runner used 52 top-level tool requests and 3.02 million input tokens. It dealt with wrong initial run paths, WindowsApps Python stubs, Blender 4.3 export timeouts, Chrome sandbox/GPU failure, ground layer mapping, a restrictive view regex, Codex transcript discovery and rationale-heading punctuation. A mechanical task became a substantial debugging session.

The preflight eventually reported rationale sections present, but its improvised regex attempts did not reproduce the actual `closeout.py` contract requiring `## N.`. Final close-out failed that step, copied a transcript anyway, then was rerun after a punctuation-only patch. Thus the final successful archive was last, but the workflow did not prevent an earlier premature archive on a failing run.

Future proposals: one tested runtime preflight, direct reusable validation functions, a no-archive validation mode, archive only after all required checks pass, and a precise transcript path/session manifest. Read only structured model counts rather than the first line of a minified model JSON, which here returned a large model payload. Shell quoting and tool-argument errors also caused retries; a reviewed file-based launcher would reduce those repeated model decisions.

Role ownership deserves clarification. Runner's canonical role prohibits editing documents and tools; root nevertheless assigned it the layer repair, and it ultimately changed rationale punctuation too. These were targeted and useful changes, but blur the intended mechanical role. A future contract should either allow specified repair operations explicitly or route them consistently to the owning role. The initial Runner failure report followed its role by naming owners; root's later request expanded that responsibility.

### G. Keep one authoritative long explanation

Concept, sources, requirements, design notes, version notes, part inspections, merged inspections and rationale repeat much of the same geometry and caveats. The Designer's final request reached 114k input. Root also wrote and repeatedly patched a large rationale while later phases were still pending, despite the workflow calling for phase-end compilation.

Keep the necessary file handoffs, but consider stable requirement IDs, concise change records, short merged findings and references to one authoritative dimensional table. Compile the final narrative once per completed phase. An Inspector's long evidence report can remain on disk; parents should load the summary and only the disputed row. This retains auditability while reducing repeated transmission.

## 6. Experiment-developed code worth considering for tools/

No new standalone reusable tool was added during this run. The persistent shared change was the three-line experiment-16 sleeper classification in `tools/layers.py`; that is configuration, not a new tool. Reusable candidates are embedded in v01/v02 or exist as the Runner's ad hoc launcher commands. None is promoted by this audit.

| Candidate and existing location | Value demonstrated here | Proposed fit within tools/ | Constraints before acceptance |
|---|---|---|---|
| **Full-foot bearing check**, [v02 script](experiment_16_gpt6_v02.py), lines 279–302 | Found support deficit invisible to zero-pair/zero-floating checks; verified all 56 seats after correction | Highest-priority candidate: `tools/check_bearing.py`, a sibling to `check_contacts.py`, with a small explicit supported-member/support contract; optionally integrated into preflight | Current implementation selects named first chord segments and horizontal rectangular foot faces, checks axis-aligned support extents/top levels, and projects the footprint to the lower layer. It is not a general rotated/concave/sloping bearing-area test. Generalize selection/datums carefully; retain distinct precision and required-seat tolerances; test partial seats, gaps and rotated supports. |
| **Mitred polyline chord with local fitted seat**, `cut_polyline()` at v02 lines 60–79 | Produces separate straight slats at complementary bisectors; local bevel preserves stock/profile while narrowing the horizontal foot to its support width | A small helper in `tools/framing.py` using existing `geometry2d.strip/clip` and plane helpers; a pure seat-profile calculation could belong in `geometry2d.py` | Do not promote the current hard-coded globals or first/last-segment assumptions. Make section, end plane and seat width explicit. Check vertical, both sloping directions, sharp/reversing turns, convexity and stock containment. The seat check should be independent of the geometry generator. |
| **Planar-facet slat roof cover and matching chord bevel**, v02 lines 130–176 | Covers an additive faceted roof with straight stock, complementary seams and matched chord-top faces | Conditional candidate: build on `planes.frame_prism`, `ruled.surface_quad` and existing board/panel helpers; expose only the genuinely missing planar slat-tiling operation | Existing `framing.boards`, `geometry2d.columns` and ruled/sheathing tools already cover much of this. First compare their APIs. Do not create another general roof engine. The present code assumes planar additive facets, fixed stations and particular end extensions; it is not a doubly curved roof solution. |
| **Empty room/entrance bounds assertion**, `bounds_enter()` at v02 lines 269–274 | Checks all modeled members against protected clear volumes, catching unintended intrusions/obstructed entry | Small optional helper in the verification toolkit or a companion to `check_contacts.py` | Current test uses world axis-aligned bounding boxes and can conservatively reject nonintersecting rotated/concave geometry. Name it as a bounds test, or add a documented narrow phase. Do not call it exact solid clearance. |
| **Codex transcript adapter / runtime launcher**, Runner commands at ordinals 450 and 472 | Allowed final close-out to use the actual root Codex rollout while retaining existing close-out checks; bundled Python removed the PATH-stub dependency | Add explicit transcript-source/provider handling to `tools/closeout.py`; reuse runtime discovery from `export_all_models.py` rather than duplicating it | The ad hoc command monkeypatches `glob.glob` and hard-codes a user path/session. Keep the capability, not that technique. Validate root ID, select a unique source, keep audit turns outside the run snapshot, fail before archive on validation errors, and document that one root transcript is not the full subagent log tree. |

The full-foot check is the strongest promotion candidate. The chord-seat helper is a useful second candidate. Roof tiling should be considered only after checking overlap with existing kits. The two small wrappers `box()`/`profile()`, timber colour/tag helpers, sine profiles, exact frame/mat layouts and `views_gpt6.py` are experiment-specific configuration; they do not justify new tools by themselves. `strip_between()` is largely a convenience wrapper over existing primitives.

No visualization-generation script, PDF-processing utility or other new persistent tool was found in this run. The Researcher reused existing reference assets; the late shell adapter was not saved as a standalone script. A future usage-report utility would also be valuable, but it was not developed during the experiment and should not be presented as an existing tool ready for promotion.

## 7. Proposed review order — no implementation yet

1. Make skill delivery complete and bounded; correct the wrapper/workflow routing and source-consultation evidence contract.
2. Expose per-agent usage from actual runtime counters and make orchestration waits consume less repeated context.
3. Establish a tested close-out preflight/archive boundary and resolve mechanical-role ownership.
4. Review the full-bearing checker and narrowly parameterized chord-seat helper for promotion when there is a second consumer.
5. Separate final render completeness from delta inspection, and reduce duplicated handoff prose.

These are collected findings, not approved changes. No skill, agent profile, tool, experiment geometry, viewer file, concluded prompt, rationale or archived conversation was modified for this audit. Only this document is added.
