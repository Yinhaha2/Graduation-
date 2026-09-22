# Full Analysis — Agent Performance PR Corpus

> **最终数据集**：1183 PR，694 merged，489 closed。合并率 **58.7%**（694/1183）。全库统一口径：仅终态 merged / closed，不含 open。
> Built from `finaldatabase/per_pr/{pr_id}/{pr_id}_analysis.json` (plus 6 root few-shot gold labels).
> Wide table: `full_analysis_distilled.csv` (regenerate with `python generate_full_analysis.py`).

---

## 1. Outcome distribution

| Status | Count | Share |
|--------|-------|-------|
| merged | 694 | 58.7% |
| closed (not merged) | 489 | 41.3% |

- **Merge rate** (merged / n): **58.7%** (694/1183)

Note: this snapshot is **terminal-only** (`merged` vs `closed` without merge). Still-open PRs were removed and are not in the denominator.

---

## 2. Main reasons for merge vs close

Grouped from `perf_labels.outcome_reason` (LLM labels in analysis JSON, not raw review text).
This is a **string-cluster of `outcome_reason`**, not the RQ1.2 behavioral `merged_path` taxonomy (`fast_low_friction` / `reviewed_iteration` / `no_formal_review`). Do not treat the two tables as the same partition.

### 2.1 Merged — grouped reasons

| Group | Count | Share of merged |
|-------|-------|-----------------|
| small_scope_low_risk | 437 | 63.0% |
| other | 91 | 13.1% |
| after_review_iteration | 89 | 12.8% |
| without_formal_review | 77 | 11.1% |

Grouped-reason rows sum to 694/694. This is not the RQ1.2 `merged_path` table (fast_low_friction / reviewed_iteration / no_formal_review).

22 merged PRs have an empty `outcome_reason`. Their GitHub `merged_at` was restored from the status-refresh cache after an earlier pass had stored them as closed, so the closed-state reason strings were removed rather than counted as merge reasons.

**Reading (descriptive, not causal):** most merged PRs have an `outcome_reason` that clusters as **small scope / low risk**; next is **after review iteration**. The `without_formal_review` cluster here is an `outcome_reason` string group, not the RQ1.2 path `no_formal_review`.

Merged `outcome_reason` raw Top 5:

| outcome_reason | Count |
|----------------|-------|
| `merged_small_scope_low_risk` | 388 |
| `merged_after_review_fix` | 71 |
| `merged_small_scope_no_review` | 18 |
| `merged_self_merge_no_review` | 7 |
| `merged_small_scope_self_merge` | 6 |

### 2.2 Closed — grouped reasons

| Group | Count | Share of closed |
|-------|-------|-----------------|
| other | 195 | 39.9% |
| stale_or_inactivity | 130 | 26.6% |
| closed_without_meaningful_review | 125 | 25.6% |
| functional_or_correctness | 24 | 4.9% |
| missing_evidence_or_benchmark | 11 | 2.2% |
| performance_regression_or_no_gain | 3 | 0.6% |
| scope_too_large | 1 | 0.2% |

Grouped-reason rows sum to 489/489.

**Reading:** closed is dominated by **process closes** (stale / no review / author closed), not a single “perf failed” label; among PRs with review text, `functional_failure` and `correctness_edge_case` stand out more.

Closed `outcome_reason` raw Top 5:

| outcome_reason | Count |
|----------------|-------|
| `stale_no_review_engagement` | 44 |
| `stale_inactivity` | 33 |
| `closed_by_author_no_review` | 13 |
| `self_closed_no_review` | 12 |
| `closed_no_review_engagement` | 11 |

---

## 3. Outcome vs change size / comment volume

### 3.1 Code churn (`changes`)

| Changes bin | Terminal PRs | Merge rate |
|-------------|--------------|------------|
| ≤100 | 490 | 63.1% |
| 101–500 | 349 | 53.0% |
| 501–2k | 197 | 55.8% |
| 2k–10k | 98 | 61.2% |
| >10k | 49 | 61.2% |

- Median changes — merged: **143**; closed: **170**
- Zero-line churn (`changes=0`) is counted in ≤100 (13 PRs, all closed).
- Change-size bins sum to 1183/1183.
- **No “more changes ⇒ more merges” pattern:** the ≤100-line bin has the highest merge rate; the >10k bin does not exceed it.

### 3.2 Comment volume (review + PR comments)

| Comment bin | Terminal PRs | Merge rate |
|-------------|--------------|------------|
| 0 | 547 | 72.8% |
| 1–2 | 294 | 43.9% |
| 3–9 | 255 | 45.1% |
| ≥10 | 87 | 59.8% |

- Median comment total — merged: **0**; closed: **2**
- Zero-comment PRs: **547** (46.2%); this bin is `comment_total==0`, not a `pd.cut` interval that starts after 0. Comment bins sum to 1183/1183. High comment volume does not imply a higher merge rate.

---

## 4. Outcome vs PR lifespan

| Lifespan | Terminal PRs | Merge rate |
|----------|--------------|------------|
| <1h | 568 | 77.3% |
| 1–24h | 232 | 58.2% |
| 1–7d | 165 | 43.6% |
| >7d | 218 | 22.0% |

- Median lifespan — merged: **0.122 h** (~7 min)
- Median lifespan — closed: **37.6 h** (~1.6 d)
- Share with `fast_merge=true` — merged: **76.1%**; closed: 0%

**Association:** merged PRs are much shorter-lived; long-lived closed PRs often track stale / no interaction, not slow rejection after review.

---

## 5. Optimization layer and antipatterns

### 5.1 `optimization_layer` (Top 12)

| optimization_layer | Count | Share |
|--------------------|-------|-------|
| `application_service` | 193 | 16.3% |
| `build` | 163 | 13.8% |
| `frontend_ui` | 135 | 11.4% |
| `runtime_library` | 117 | 9.9% |
| `application_control_flow` | 83 | 7.0% |
| `compiler` | 45 | 3.8% |
| `infrastructure` | 33 | 2.8% |
| `runtime_vm` | 29 | 2.5% |
| `compiler_backend` | 26 | 2.2% |
| `compiler_optimization` | 15 | 1.3% |
| `compiler_codegen` | 14 | 1.2% |
| `test_infrastructure` | 12 | 1.0% |

Top 12 sum to 865; the remaining 318 PRs sit in less frequent layers and are not listed.

### 5.2 Inefficiency antipatterns (`inefficiency_antipattern` ≠ none)

**Merged top:** `repeated_io`(33), `nested_loop`(10), `unknown`(5), `lock_misuse`(2), `main_thread_blocking`(2), `memory_leak`(2)

**Closed top:** `repeated_io`(35), `nested_loop`(4), `lock_misuse`(3), `repeated_computation`(2), `redundant_computation`(2), `blocking_io`(2)

`repeated_io` leads on both sides (slightly more on closed). Most PRs are still labeled `none`.

---

## 6. How maintainers detect perf issues

Field: `perf_labels.detection_method` (multi-label).

| detection_method | PR count | Share of corpus |
|------------------|----------|-----------------|
| `unknown` | 766 | 64.8% |
| `code_reading` | 363 | 30.7% |
| `ci_auto` | 92 | 7.8% |
| `manual_testing` | 16 | 1.4% |
| `manual_test` | 8 | 0.7% |
| `benchmark` | 6 | 0.5% |
| `load_test` | 4 | 0.3% |
| `(empty)` | 4 | 0.3% |
| `profiler` | 3 | 0.3% |
| `unit_test` | 3 | 0.3% |

Counts are PR hits (multi-label); row totals can exceed corpus n. Labels beyond the top 10 account for 20 additional hits.
- **Dominant when observable:** **`code_reading`** (363 PRs with at least one hit).
- Next: **`ci_auto`** (92); `profiler` / `load_test` / `benchmark` alone are rare.
- **766** labeled `unknown`, consistent with **70.8%** (837/1183) having `review_count=0` — detection is often unobservable.

---

## 7. Can PR materials support perf-defect reproduction?

| reproducibility | Count | Share |
|-----------------|-------|-------|
| `insufficient` | 730 | 61.7% |
| `partial` | 235 | 19.9% |
| `unknown` | 194 | 16.4% |
| `sufficient` | 24 | 2.0% |

Rows sum to 1183/1183.

Auxiliary signals:
- `body_has_repro_steps=true`: **53** (4.5%)
- `body_has_benchmark_table=true`: **48**
- `material_reproducibility=sufficient`: **24**

**Material-dimension takeaway:** most PRs are **insufficient or partial**; only ~**2%** reach sufficient.

---

## 8. Regression / review-issue handling

| regression_handling | Count | Share |
|---------------------|-------|-------|
| `not_applicable` | 598 | 50.5% |
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

Rows sum to 1183/1183.

- **`not_applicable`** (50.5%): no clear regression-handling context (often direct merge or process close).
- **`reject_close`** (33.6%): reject/close dominant; mostly among closed.
- **`fix_in_pr`** (143): fixed in the same PR; `revert` only **2**.

### 8.1 Who fixes in `fix_in_pr` (heuristic text labels, not ground truth)

| Fix mode | Count | Share of fix_in_pr |
|----------|-------|--------------------|
| human_led_or_requested | 80 | 55.9% |
| ai_author_in_pr | 32 | 22.4% |
| human_ai_collaborative | 21 | 14.7% |
| unclear | 10 | 7.0% |

- Each PR has a single `meta.agent`; no structured multi-agent field — cannot systematically measure multi-agent co-fixes.
- New-issue-in-fix signal: `antipattern_in_fix` ≠ none on **7** PRs (0.6%).

---

## 9. Linked issues

- `linked_issue_count > 0`: **203** (**17.2%**)
- No linked issue: **980** (**82.8%** of corpus); merged **595/694** (85.7%); closed **385/489** (78.7%).

Most agent perf PRs are **not** clearly opened to fix a linked issue; optimizations are often agent-initiated.

---

## 10. Pass rate, focus distribution, capability boundaries

- **Merge rate for AI perf PRs: 58.7%** (694/1183).

### 10.1 Common `perf_focus` on merged

`constant_folding`(24), `compiler_optimization`(21), `benchmark_infrastructure`(11), `cache`(8), `lazy_loading`(7), `compile_time_optimization`(7), `build_performance`(6), `caching`(6)

### 10.2 Common `perf_focus` on closed

`bundle_size_reduction`(12), `cache`(9), `constant_folding`(9), `lazy_load`(7), `build_performance`(6), `caching`(6), `code_splitting`(6), `compiler_optimization`(6)

### 10.3 `boundary_tag` distribution

| boundary_tag | Count |
|--------------|-------|
| `technical_stack` | 588 |
| `process` | 562 |
| `evidence_required` | 32 |
| `unknown` | 1 |

### 10.4 Strengths vs boundaries (label-based; needs human check)

**Strengths (merged-side signals)**
- Small-scope control-flow / compiler constant-folding / build-and-cache changes merge more easily under low review friction.
- `technical_stack` dominates (588); this is an analytic tag for routine stack-layer work, not a measured agent ability.

**Boundaries (closed / higher-risk signals)**
- Process closes (stale / no review) dominate and mask true “perf rejected” rates.
- `evidence_required` boundaries (32) align with `missing_benchmark` / insufficient reproducibility.
- Large churn (>10k changes) does not merge better; `repeated_io` is slightly higher on closed.
- Without reproducible materials, review is hard to close.

---

## 11. Merge rate by agent (n≥30)

| Agent | PRs | Merge rate |
|-------|-----|------------|
| OpenAI_Codex | 629 | 73.1% |
| Claude_Code | 34 | 64.7% |
| Cursor | 89 | 55.1% |
| Copilot | 206 | 43.2% |
| Devin | 225 | 32.9% |

---

## 12. Data & method notes

- Stats use **labels and narrative fields** in analysis JSON, not a fresh GitHub event re-crawl.
- Labels such as `outcome_reason` are LLM-generated (synonym inflation); this report coarsens merge/close groups.
- Fix actor / new-issue-in-fix findings are **text heuristics** — sample-check before paper use.
- Merge rate is merged / corpus n on the terminal snapshot (open PRs are not in this dataset).
- `merged_at` / `closed_at` on the formerly-open cohort follow `summary/github_status_cache.json` (the refresh log). Where that cache showed a merge the master had missed, status is merged and the old closed-state `outcome_reason` is left empty.
