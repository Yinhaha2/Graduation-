# analysis_viz — Figure guide

Notebook: `perf_pr_visualization.ipynb`  
Data: `../full_analysis_distilled.csv`（**最终数据集：1183 PR，672 merged，511 closed**；合并率 **56.8%** = 672/1183）  
Figures: `figures/`

Numbers below match the current distilled table. Merge-rate charts use the terminal corpus (open PRs were removed). Overall merge rate ≈ **56.8%**.

---

## 01–02 · Code churn vs merge outcome

**What it shows:** Boxplot of `changes` by outcome, plus binned PR counts with a merge-rate line.

**Phenomenon:** Smaller patches merge more easily; there is **no** “more lines ⇒ higher merge rate” pattern.

| Changes bin | Terminal PRs | Merge rate |
|-------------|--------------|------------|
| ≤100 | 490 | **61.4%** |
| 101–500 | 350 | 52.6% |
| 501–2k | 196 | 54.1% |
| 2k–10k | 107 | 56.1% |
| >10k | 40 | 52.5% |

Median `changes`: merged **141**, closed **172**. Zero-line churn (`changes=0`) is **13** PRs (all closed) and is counted in ≤100. Bins sum to 1183.

---

## 03–04 · File count vs merge outcome

**What it shows:** Boxplot of `file_count` by outcome, plus merge rate by file-count bin.

**Phenomenon:** File-count bins are relatively flat; single-file and very large multi-file PRs both sit near or above the corpus average. Median files is **4** for both merged and closed.

| Files bin | Terminal PRs | Merge rate |
|-----------|--------------|------------|
| 0 | 13 | 0.0% |
| 1 | 240 | **62.9%** |
| 2–5 | 466 | 54.7% |
| 6–20 | 287 | 55.4% |
| 21–100 | 114 | 59.6% |
| >100 | 63 | 61.9% |

The 13 zero-file PRs are the same 13 zero-churn closed PRs. Bins sum to 1183.

---

## 05–06 · PR lifespan vs merge outcome

**What it shows:** Lifespan (`lifespan_hours`) by outcome, plus merge rate by lifetime bin.

**Phenomenon:** Merged PRs are much shorter-lived; long-open PRs rarely merge (often stale / no interaction, not slow rejection).

| Lifespan | Terminal PRs | Merge rate |
|----------|--------------|------------|
| <1h | 573 | **76.6%** |
| 1–24h | 236 | 57.2% |
| 1–7d | 180 | 40.0% |
| >7d | 153 | **17.0%** |
| (lifespan missing) | 41 | 0.0% |

Median lifespan: merged **~0.08 h (~5 min)**; closed **~24.3 h (~1 day)**. Among merged, `fast_merge=true` is **78.6%**. Figure 06 uses the four non-missing bins only; the 41 PRs with missing lifespan (merge rate 0%) are in the table, not the chart.

---

## 07–08 · Comment volume vs merge outcome

**What it shows:** Comment distribution by outcome, plus merge rate by comment bin (`review_comment_count` + `pr_comment_count`).

**Phenomenon:** Zero-comment PRs are common on the merge side (fast / low-friction path). More comments do **not** mean a higher merge rate.

| Comment bin | Terminal PRs | Merge rate |
|-------------|--------------|------------|
| 0 | 547 | **71.5%** |
| 1–2 | 294 | 43.2% |
| 3–9 | 255 | 43.1% |
| ≥10 | 87 | 50.6% |

Median comments: merged **0** (391/672 = 58.2% zero); closed **2** (156/511 = 30.5% zero). Bins sum to 1183. The 0 bin is `comment_total==0`, not a `pd.cut` interval that starts after 0.

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

**Phenomenon:** Almost never labeled as introducing a new issue — **`none` on 1174 / 1183 (99.2%)**. Non-none cases are **7** one-off labels (e.g. `fabricated_benchmark`, `mutable_global_state`, `incorrect_lru_eviction`), each n=1. Treat as rare anecdotes, not a systematic failure mode.

---

## 14 · Terminal outcomes (pie)

**What it shows:** Share of merged vs closed among terminal PRs (open excluded from this pie).

**Phenomenon:** Terminal outcomes split as **merged 672 (56.8%)** vs **closed 511 (43.2%)**. Open PRs are not in this snapshot.

---

## 15 · Merge rate by agent

**What it shows:** Merge rate for agents with **n ≥ 30**, vs corpus average.

**Phenomenon:** Large spread across agents — not a uniform “AI merge rate”.

| Agent | PRs | Merge rate |
|-------|-----|------------|
| OpenAI_Codex | 629 | **71.9%** |
| Claude_Code | 34 | 61.8% |
| Cursor | 89 | 53.9% |
| Copilot | 206 | 37.9% |
| Devin | 225 | **32.4%** |

---

## 16 · Reproducibility vs outcome

**What it shows:** Stacked outcomes by `reproducibility` label.

**Phenomenon:** Materials are usually weak; “sufficient” is rare. Better material labels correlate with higher merge share, but sample for `sufficient` is tiny.

| reproducibility | Count | Share | Merged / Closed |
|-----------------|-------|-------|-----------------|
| `insufficient` | 730 | **61.7%** | 356 / 374 |
| `partial` | 235 | 19.9% | 173 / 62 |
| `unknown` | 194 | 16.4% | 127 / 67 |
| `sufficient` | 24 | **2.0%** | 16 / 8 |

Auxiliary: `body_has_repro_steps=true` only **53 (4.5%)**.

---

## 17 · Agent capability boundary (`boundary_tag`)

**What it shows:** Which capability boundary each PR illustrates, with PR count bars and merge-rate line (overall ≈ **56.8%**).

**Phenomenon:** Merge rate is highest on PRs tagged **technical stack**, lower on **process/workflow**, and lowest when the tag is **evidence / reproducibility**. These are analytic tags, not measured cognitive abilities.

| Boundary | PR count | Merge rate |
|----------|----------|------------|
| Technical stack (stack / framework depth) | **588** | **79.6%** (well above overall) |
| Process / workflow (review, scope, CI) | **562** | **35.6%** (well below overall) |
| Evidence required (benchmark / repro gap) | **32** | **12.5%** |
| Unknown | 1 | 0% |

Reading: volume is split between technical and process (588 vs 562), but merge rates diverge — stack-depth changes often merge; process friction and missing evidence mark lower-merge strata. `boundary_tag` stratifies the corpus; it does not cause merge.

---

## 18 · Formal review count vs merge outcome

**What it shows:** Merge rate by `review_count` bin (terminal PRs).

**Phenomenon:** Zero formal reviews is the majority path and sits near the average; having **at least one** review associates with a higher merge rate (selection / iteration effects, not proven causation).

| Review count | Terminal PRs | Merge rate |
|--------------|--------------|------------|
| 0 | 837 | 53.8% |
| 1 | 146 | **65.1%** |
| 2–3 | 97 | 63.9% |
| ≥4 | 103 | 63.1% |

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
