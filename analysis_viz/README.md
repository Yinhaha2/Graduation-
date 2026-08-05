# analysis_viz — Figure guide

Notebook: `perf_pr_visualization.ipynb`  
Data: `../full_analysis_distilled.csv` (**1219** PRs; terminal merge rate **56.9%** on 1180 merged+closed)  
Figures: `figures/`

Numbers below match the current distilled table. Merge-rate charts for size/lifespan/comments/reviews use **terminal PRs only**; the boundary-tag chart uses **all PRs** for the rate line (open counts as not merged), with overall ≈ **57%**.

---

## 01–02 · Code churn vs merge outcome

**What it shows:** Boxplot of `changes` by outcome, plus binned PR counts with a merge-rate line.

**Phenomenon:** Smaller patches merge more easily; there is **no** “more lines ⇒ higher merge rate” pattern.

| Changes bin | Terminal PRs | Merge rate |
|-------------|--------------|------------|
| ≤100 | 476 | **63.2%** |
| 101–500 | 349 | 52.4% |
| 501–2k | 195 | 54.4% |
| 2k–10k | 107 | 56.1% |
| >10k | 40 | 52.5% |

Median `changes`: merged **141**, closed **172**.

---

## 03–04 · File count vs merge outcome

**What it shows:** Boxplot of `file_count` by outcome, plus merge rate by file-count bin.

**Phenomenon:** File-count bins are relatively flat; single-file and very large multi-file PRs both sit near or above the corpus average. Median files is **4** for both merged and closed.

| Files bin | Terminal PRs | Merge rate |
|-----------|--------------|------------|
| 1 | 240 | **62.9%** |
| 2–5 | 464 | 54.7% |
| 6–20 | 286 | 55.6% |
| 21–100 | 114 | 59.6% |
| >100 | 63 | 61.9% |

---

## 05–06 · PR lifespan vs merge outcome

**What it shows:** Lifespan (`lifespan_hours`) by outcome, plus merge rate by lifetime bin.

**Phenomenon:** Merged PRs are much shorter-lived; long-open PRs rarely merge (often stale / no interaction, not slow rejection).

| Lifespan | Terminal PRs | Merge rate |
|----------|--------------|------------|
| <1h | 573 | **76.6%** |
| 1–24h | 236 | 57.2% |
| 1–7d | 180 | 40.0% |
| >7d | 150 | **16.7%** |

Median lifespan: merged **~0.08 h (~5 min)**; closed **~23.6 h (~1 day)**. Among merged, `fast_merge=true` is **78.7%**.

---

## 07–08 · Comment volume vs merge outcome

**What it shows:** Comment distribution by outcome, plus merge rate by comment bin (`review_comment_count` + `pr_comment_count`).

**Phenomenon:** Zero-comment PRs are common on the merge side (fast / low-friction path). More comments do **not** mean a higher merge rate.

| Comment bin | Terminal PRs | Merge rate |
|-------------|--------------|------------|
| 0 | 161 | 47.8% |
| 1–2 | 202 | **35.1%** (lowest) |
| 3–9 | 197 | 47.7% |
| ≥10 | 75 | 50.7% |

Median comments: merged **0** (58% zero); closed **2** (30% zero).

---

## 09 · Inefficiency antipatterns

**What it shows:** Counts of non-`none` / non-`unknown` `inefficiency_antipattern` labels (multi-label exploded).

**Phenomenon:** Most PRs have no antipattern label. When present, **`repeated_io`** dominates on both sides (merged **32**, closed **36**); next is `nested_loop` (merged 9, closed 5). Antipattern tags do not cleanly separate merge vs close.

---

## 10 · Detection methods

**What it shows:** How maintainers detect perf issues (`detection_method`, multi-label; chart excludes `unknown`).

**Phenomenon:** When observable, detection is mostly **static code reading**, not profiling/benchmarks.

| Method | PR hits | Share of corpus |
|--------|---------|-----------------|
| `unknown` (often omitted from bar) | 786 | **64.5%** |
| `code_reading` | 378 | 31.0% |
| `ci_auto` | 93 | 7.6% |
| `manual_testing` / `manual_test` | 18+8 | ~2% |
| `benchmark` / `load_test` / `profiler` | ≤6 each | rare |

Large `unknown` share aligns with ~71% lacking formal review — detection is often unobservable.

---

## 11 · Optimization layer

**What it shows:** Where the optimization sits (`optimization_layer`).

**Phenomenon:** Work concentrates in application / build / UI / library layers, not deep compiler/VM work.

Top layers: `application_service` **201 (16.5%)**, `build` **165 (13.5%)**, `frontend_ui` **137 (11.2%)**, `runtime_library` **122 (10.0%)**, `application_control_flow` **87 (7.1%)**. Compiler-related layers are each under ~4%.

---

## 12 · Regression handling

**What it shows:** How regression / review issues are handled (`regression_handling`).

**Phenomenon:** Most PRs have no clear regression-handling story; when they do, reject/close dominates over in-PR fix.

| Label | Count | Share |
|-------|-------|-------|
| `not_applicable` | 626 | **51.4%** |
| `reject_close` | 397 | 32.6% |
| `fix_in_pr` | 148 | 12.1% |
| `revert` | 2 | 0.2% |

---

## 13 · Antipattern in fix

**What it shows:** Whether the fix itself introduces a new antipattern (`antipattern_in_fix`).

**Phenomenon:** Almost never labeled as introducing a new issue — **`none` on 1211 / 1219 (99.3%)**. Non-none cases are **8** one-off labels (e.g. `fabricated_benchmark`, `mutable_global_state`, `incorrect_lru_eviction`), each n=1. Treat as rare anecdotes, not a systematic failure mode.

---

## 14 · Terminal outcomes (pie)

**What it shows:** Share of merged vs closed among terminal PRs (open excluded from this pie).

**Phenomenon:** Corpus is roughly a coin-flip on terminal outcomes: **merged 671 (55.0% of all; 56.9% of terminal)**, **closed 509 (41.8%)**, **open 39 (3.2%)**.

---

## 15 · Merge rate by agent

**What it shows:** Merge rate for agents with **n ≥ 30**, vs corpus average.

**Phenomenon:** Large spread across agents — not a uniform “AI merge rate”.

| Agent | PRs | Merge rate |
|-------|-----|------------|
| OpenAI_Codex | 639 | **70.7%** |
| Claude_Code | 38 | 55.3% |
| Cursor | 95 | 50.5% |
| Copilot | 222 | 34.7% |
| Devin | 225 | **32.4%** |

---

## 16 · Reproducibility vs outcome

**What it shows:** Stacked outcomes by `reproducibility` label.

**Phenomenon:** Materials are usually weak; “sufficient” is rare. Better material labels correlate with higher merge share, but sample for `sufficient` is tiny.

| reproducibility | Count | Share | Merged / Closed / Open |
|-----------------|-------|-------|-------------------------|
| `insufficient` | 754 | **61.9%** | 356 / 373 / 25 |
| `partial` | 240 | 19.7% | 172 / 61 / 7 |
| `unknown` | 200 | 16.4% | 127 / 67 / 6 |
| `sufficient` | 25 | **2.1%** | 16 / 8 / 1 |

Auxiliary: `body_has_repro_steps=true` only **55 (4.5%)**.

---

## 17 · Agent capability boundary (`boundary_tag`)

**What it shows:** Which capability boundary each PR illustrates, with PR count bars and merge-rate line (overall ≈ **57%**).

**Phenomenon:** Agents look strong on **technical stack** work, weak on **process/workflow** and especially on **evidence / reproducibility** demands.

| Boundary | PR count | Merge rate (all PRs) |
|----------|----------|----------------------|
| Technical stack (stack / framework depth) | **608** | **~77%** (well above overall) |
| Process / workflow (review, scope, CI) | **575** | **~35%** (well below overall) |
| Evidence required (benchmark / repro gap) | **35** | **~11%** |
| Unknown | 1 | 0% |

Reading: volume is split between technical and process (~608 vs ~575), but success diverges sharply — stack-depth changes often merge; process friction and missing evidence mark clear capability boundaries.

---

## 18 · Formal review count vs merge outcome

**What it shows:** Merge rate by `review_count` bin (terminal PRs).

**Phenomenon:** Zero formal reviews is the majority path and sits near the average; having **at least one** review associates with a higher merge rate (selection / iteration effects, not proven causation).

| Review count | Terminal PRs | Merge rate |
|--------------|--------------|------------|
| 0 | 835 | 53.9% |
| 1 | 146 | **65.1%** |
| 2–3 | 97 | 63.9% |
| ≥4 | 102 | 62.7% |

---

## Regenerate

```bash
python generate_full_analysis.py
# then Run All in perf_pr_visualization.ipynb
```
