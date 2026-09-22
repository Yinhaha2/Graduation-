# analysis_viz — Figure guide

Notebook: `perf_pr_visualization.ipynb`  
Data: `../full_analysis_distilled.csv`（**最终数据集：1183 PR，694 merged，489 closed**；合并率 **58.7%** = 694/1183）  
Figures: `figures/`

Numbers below match the current distilled table. Merge-rate charts use the terminal corpus (open PRs were removed). Overall merge rate ≈ **58.7%**.

---

## 01–02 · Code churn vs merge outcome

**What it shows:** Boxplot of `changes` by outcome, plus binned PR counts with a merge-rate line.

**Phenomenon:** Smaller patches merge more easily; there is **no** “more lines ⇒ higher merge rate” pattern.

| Changes bin | Terminal PRs | Merge rate |
|-------------|--------------|------------|
| ≤100 | 490 | **63.1%** |
| 101–500 | 349 | 53.0% |
| 501–2k | 197 | 55.8% |
| 2k–10k | 98 | 61.2% |
| >10k | 49 | 61.2% |

Median `changes`: merged **143**, closed **170**. Zero-line churn (`changes=0`) is **13** PRs (all closed) and is counted in ≤100. Bins sum to 1183.

---

## 03–04 · File count vs merge outcome

**What it shows:** Boxplot of `file_count` by outcome, plus merge rate by file-count bin.

**Phenomenon:** File-count bins are relatively flat; single-file and very large multi-file PRs both sit near or above the corpus average. Median files is **4** for both merged and closed.

| Files bin | Terminal PRs | Merge rate |
|-----------|--------------|------------|
| 0 | 13 | 0.0% |
| 1 | 240 | **65.4%** |
| 2–5 | 464 | 56.0% |
| 6–20 | 287 | 56.4% |
| 21–100 | 115 | 63.5% |
| >100 | 64 | 65.6% |

The 13 zero-file PRs are the same 13 zero-churn closed PRs. Bins sum to 1183.

---

## 05–06 · PR lifespan vs merge outcome

**What it shows:** Lifespan (`lifespan_hours`) by outcome, plus merge rate by lifetime bin.

**Phenomenon:** Merged PRs are much shorter-lived; long-open PRs rarely merge (often stale / no interaction, not slow rejection).

| Lifespan | Terminal PRs | Merge rate |
|----------|--------------|------------|
| <1h | 568 | **77.3%** |
| 1–24h | 232 | 58.2% |
| 1–7d | 165 | 43.6% |
| >7d | 218 | **22.0%** |

Median lifespan: merged **~0.12 h (~7 min)**; closed **~37.6 h (~1.6 day)**. Among merged, `fast_merge=true` is **76.1%** (528/694). Lifespan is filled for all 1183 PRs; bins sum to 1183.

---

## 07–08 · Comment volume vs merge outcome

**What it shows:** Comment distribution by outcome, plus merge rate by comment bin (`review_comment_count` + `pr_comment_count`).

**Phenomenon:** Zero-comment PRs are common on the merge side (fast / low-friction path). More comments do **not** mean a higher merge rate.

| Comment bin | Terminal PRs | Merge rate |
|-------------|--------------|------------|
| 0 | 547 | **72.8%** |
| 1–2 | 294 | 43.9% |
| 3–9 | 255 | 45.1% |
| ≥10 | 87 | 59.8% |

Median comments: merged **0** (398/694 = 57.3% zero); closed **2** (149/489 = 30.5% zero). Bins sum to 1183. The 0 bin is `comment_total==0`, not a `pd.cut` interval that starts after 0.

---

## 09 · Inefficiency antipatterns

**What it shows:** Counts of non-`none` / non-`unknown` `inefficiency_antipattern` labels (multi-label exploded).

**Phenomenon:** Most PRs have no antipattern label. When present, **`repeated_io`** dominates on both sides (merged **33**, closed **35**); next is `nested_loop` (merged 10, closed 4). Antipattern tags do not cleanly separate merge vs close.

---

## 10 · Detection methods

**What it shows:** How maintainers detect perf issues (`detection_method`, multi-label; chart excludes `unknown`).

**Phenomenon:** When observable, detection is mostly **static code reading**, not profiling/benchmarks.

| Method | PR hits | Share of corpus |
|--------|---------|-----------------|
| `unknown` (often omitted from bar) | 766 | **64.8%** |
| `code_reading` | 363 | 30.7% |
| `ci_auto` | 92 | 7.8% |
| `manual_testing` / `manual_test` | 16+8 | ~2% |
| `benchmark` / `load_test` / `profiler` | ≤6 each | rare |

Large `unknown` share aligns with **70.8%** (`837/1183`) having `review_count=0` — detection is often unobservable. Detection is multi-label, so method rows can sum past 1183.

---

## 11 · Optimization layer

**What it shows:** Where the optimization sits (`optimization_layer`).

**Phenomenon:** Work concentrates in application / build / UI / library layers, not deep compiler/VM work.

Top layers: `application_service` **193 (16.3%)**, `build` **163 (13.8%)**, `frontend_ui` **135 (11.4%)**, `runtime_library` **117 (9.9%)**, `application_control_flow` **83 (7.0%)**. Compiler-related layers are each under ~4%.

---

## 12 · Regression handling

**What it shows:** How regression / review issues are handled (`regression_handling`).

**Phenomenon:** Most PRs have no clear regression-handling story; when they do, reject/close dominates over in-PR fix.

| Label | Count | Share |
|-------|-------|-------|
| `not_applicable` | 598 | **50.5%** |
| `reject_close` | 398 | 33.6% |
| `fix_in_pr` | 143 | 12.1% |
| `ignore` | 18 | 1.5% |
| `unknown` | 17 | 1.4% |
| `revert` | 2 | 0.2% |
| `fix_followup` | 2 | 0.2% |
| `close_no_merge` | 1 | 0.1% |
| `abandon` | 1 | 0.1% |
| `recreated_in_new_pr` | 1 | 0.1% |
| `closed_no_merge` | 1 | 0.1% |
| `draft_converted_no_fix` | 1 | 0.1% |

Rows sum to 1183/1183. Rare labels (`abandon` / `recreated_in_new_pr` / `closed_no_merge` / `draft_converted_no_fix`) are kept so the table is exhaustive.

---

## 13 · Antipattern in fix

**What it shows:** Whether the fix itself introduces a new antipattern (`antipattern_in_fix`).

**Phenomenon:** Almost never labeled as introducing a new issue — **`none` on 1174 / 1183 (99.2%)**. Labeled non-none cases are **7** one-off labels (e.g. `fabricated_benchmark`, `mutable_global_state`, `incorrect_lru_eviction`), each n=1, and **2** rows have the field empty. Treat the labeled cases as rare anecdotes, not a systematic failure mode.

---

## 14 · Terminal outcomes (pie)

**What it shows:** Share of merged vs closed among terminal PRs (open excluded from this pie).

**Phenomenon:** Terminal outcomes split as **merged 694 (58.7%)** vs **closed 489 (41.3%)**. Open PRs are not in this snapshot.

---

## 15 · Merge rate by agent

**What it shows:** Merge rate for agents with **n ≥ 30**, vs corpus average.

**Phenomenon:** Large spread across agents — not a uniform “AI merge rate”.

| Agent | PRs | Merge rate |
|-------|-----|------------|
| OpenAI_Codex | 629 | **73.1%** |
| Claude_Code | 34 | 64.7% |
| Cursor | 89 | 55.1% |
| Copilot | 206 | 43.2% |
| Devin | 225 | **32.9%** |

---

## 16 · Reproducibility vs outcome

**What it shows:** Stacked outcomes by `reproducibility` label.

**Phenomenon:** Materials are usually weak; “sufficient” is rare. Better material labels correlate with higher merge share, but sample for `sufficient` is tiny.

| reproducibility | Count | Share | Merged / Closed |
|-----------------|-------|-------|-----------------|
| `insufficient` | 730 | **61.7%** | 372 / 358 |
| `partial` | 235 | 19.9% | 176 / 59 |
| `unknown` | 194 | 16.4% | 130 / 64 |
| `sufficient` | 24 | **2.0%** | 16 / 8 |

Auxiliary: `body_has_repro_steps=true` only **53 (4.5%)**.

---

## 17 · Agent capability boundary (`boundary_tag`)

**What it shows:** Which capability boundary each PR illustrates, with PR count bars and merge-rate line (overall ≈ **58.7%**).

**Phenomenon:** Merge rate is highest on PRs tagged **technical stack**, lower on **process/workflow**, and lowest when the tag is **evidence / reproducibility**. These are analytic tags, not measured cognitive abilities.

| Boundary | PR count | Merge rate |
|----------|----------|------------|
| Technical stack (stack / framework depth) | **588** | **80.4%** (well above overall) |
| Process / workflow (review, scope, CI) | **562** | **38.1%** (well below overall) |
| Evidence required (benchmark / repro gap) | **32** | **21.9%** |
| Unknown | 1 | 0% |

Reading: volume is split between technical and process (588 vs 562), but merge rates diverge — stack-depth changes often merge; process friction and missing evidence mark lower-merge strata. `boundary_tag` stratifies the corpus; it does not cause merge.

---

## 18 · Formal review count vs merge outcome

**What it shows:** Merge rate by `review_count` bin (terminal PRs).

**Phenomenon:** Zero formal reviews is the majority path and sits near the average; having **at least one** review associates with a higher merge rate (selection / iteration effects, not proven causation).

| Review count | Terminal PRs | Merge rate |
|--------------|--------------|------------|
| 0 | 837 | 55.0% |
| 1 | 147 | **66.0%** |
| 2–3 | 95 | 68.4% |
| ≥4 | 104 | 69.2% |

---

## Regenerate

```bash
python generate_full_analysis.py
python generate_rq_analysis.py
python analysis_viz/run_corpus_figures.py
python analysis_viz/plot_rq1_paper_figures.py
python analysis_viz/plot_rq2_paper_figures.py
python analysis_viz/plot_rq3_paper_figures.py
python analysis_viz/redraw_paper_figures.py
```
