# Full Analysis — Agent Performance PR Corpus

> **最终数据集**：1183 PR，672 merged，511 closed。合并率 **56.8%**（672/1183）。全库统一口径：仅终态 merged / closed，不含 open。
> Built from `finaldatabase/per_pr/{pr_id}/{pr_id}_analysis.json` (plus 6 root few-shot gold labels).
> Wide table: `full_analysis_distilled.csv` (regenerate with `python generate_full_analysis.py`).

---

## 1. Outcome distribution

| Status | Count | Share |
|--------|-------|-------|
| merged | 672 | 56.8% |
| closed (not merged) | 511 | 43.2% |

- **Merge rate** (merged / n): **56.8%** (672/1183)

Note: this snapshot is **terminal-only** (`merged` vs `closed` without merge). Still-open PRs were removed and are not in the denominator.

---

## 2. Main reasons for merge vs close

Grouped from `perf_labels.outcome_reason` (LLM labels in analysis JSON, not raw review text).

### 2.1 Merged — grouped reasons

| Group | Count | Share of merged |
|-------|-------|-----------------|
| small_scope_low_risk | 437 | 65.0% |
| after_review_iteration | 89 | 13.2% |
| without_formal_review | 77 | 11.5% |
| other | 69 | 10.3% |

**Reading (descriptive, not causal):** most merged PRs are labeled **small scope / low risk** (`small_scope_low_risk`); next is **merged after review iteration** (`after_review_iteration`); ~10% lack formal-review signals (`without_formal_review`).

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
| other | 203 | 39.7% |
| stale_or_inactivity | 142 | 27.8% |
| closed_without_meaningful_review | 127 | 24.9% |
| functional_or_correctness | 24 | 4.7% |
| missing_evidence_or_benchmark | 11 | 2.2% |
| performance_regression_or_no_gain | 3 | 0.6% |
| scope_too_large | 1 | 0.2% |

**Reading:** closed is dominated by **process closes** (stale / no review / author closed), not a single “perf failed” label; among PRs with review text, `functional_failure` and `correctness_edge_case` stand out more.

Closed `outcome_reason` raw Top 5:

| outcome_reason | Count |
|----------------|-------|
| `stale_no_review_engagement` | 50 |
| `stale_inactivity` | 33 |
| `closed_by_author_no_review` | 13 |
| `closed_no_review_engagement` | 12 |
| `self_closed_no_review` | 12 |

---

## 3. Outcome vs change size / comment volume

### 3.1 Code churn (`changes`)

| Changes bin | Terminal PRs | Merge rate |
|-------------|--------------|------------|
| ≤100 | 477 | 63.1% |
| 101–500 | 350 | 52.6% |
| 501–2k | 196 | 54.1% |
| 2k–10k | 107 | 56.1% |
| >10k | 40 | 52.5% |

- Median changes — merged: **141**; closed: **172**
- **No “more changes ⇒ more merges” pattern:** ≤100-line bin has the highest merge rate (~63%); >10k is ~52%.

### 3.2 Comment volume (review + PR comments)

| Comment bin | Terminal PRs | Merge rate |
|-------------|--------------|------------|
| 0 | 161 | 47.8% |
| 1–2 | 202 | 35.1% |
| 3–9 | 197 | 47.7% |
| ≥10 | 76 | 51.3% |

- Median comment total — merged: **0**; closed: **2**
- Zero-comment PRs have higher merge rates (fast merge / no review path); high comment volume does not imply higher merge rate.

---

## 4. Outcome vs PR lifespan

| Lifespan | Terminal PRs | Merge rate |
|----------|--------------|------------|
| <1h | 573 | 76.6% |
| 1–24h | 236 | 57.2% |
| 1–7d | 180 | 40.0% |
| >7d | 153 | 17.0% |

- Median lifespan — merged: **0.079 h** (~5 min)
- Median lifespan — closed: **24.3 h** (~1.0 d)
- Share with `fast_merge=true` — merged: **78.6%**; closed: 0%

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

### 5.2 Inefficiency antipatterns (`inefficiency_antipattern` ≠ none)

**Merged top:** `repeated_io`(32), `nested_loop`(9), `unknown`(4), `lock_misuse`(2), `main_thread_blocking`(2), `memory_leak`(2)

**Closed top:** `repeated_io`(36), `nested_loop`(5), `lock_misuse`(3), `repeated_computation`(2), `redundant_computation`(2), `blocking_io`(2)

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

- **Dominant when observable:** **`code_reading`** (~363 PRs with at least one hit).
- Next: **`ci_auto`** (~92); `profiler` / `load_test` / `benchmark` alone are rare.
- ~**766** labeled `unknown`, consistent with ~**71%** lacking formal review — detection is often unobservable.

---

## 7. Can PR materials support perf-defect reproduction?

| reproducibility | Count | Share |
|-----------------|-------|-------|
| `insufficient` | 730 | 61.7% |
| `partial` | 235 | 19.9% |
| `unknown` | 194 | 16.4% |
| `sufficient` | 24 | 2.0% |

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
- No linked issue: **980** (**82.8%**)

Most agent perf PRs are **not** clearly opened to fix a linked issue; optimizations are often agent-initiated.

---

## 10. Pass rate, focus distribution, capability boundaries

- **Merge rate for AI perf PRs: ~56.8%** (672/1183).

### 10.1 Common `perf_focus` on merged

`constant_folding`(23), `compiler_optimization`(21), `benchmark_infrastructure`(11), `cache`(8), `lazy_loading`(7), `compile_time_optimization`(7), `caching`(6), `compiler_codegen`(6)

### 10.2 Common `perf_focus` on closed

`bundle_size_reduction`(12), `constant_folding`(10), `cache`(9), `build_performance`(7), `lazy_load`(7), `caching`(6), `code_splitting`(6), `compiler_optimization`(6)

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
- `technical_stack` dominates (588), i.e. problems in a routine stack layer agents can often handle.

**Boundaries (closed / higher-risk signals)**
- Process closes (stale / no review) dominate and mask true “perf rejected” rates.
- `evidence_required` boundaries (32) align with `missing_benchmark` / insufficient reproducibility.
- Large churn (>10k changes) does not merge better; `repeated_io` is slightly higher on closed.
- Without reproducible materials, review is hard to close.

---

## 11. Merge rate by agent (n≥30)

| Agent | PRs | Merge rate |
|-------|-----|------------|
| OpenAI_Codex | 629 | 71.9% |
| Claude_Code | 34 | 61.8% |
| Cursor | 89 | 53.9% |
| Copilot | 206 | 37.9% |
| Devin | 225 | 32.4% |

---

## 12. Data & method notes

- Stats use **labels and narrative fields** in analysis JSON, not a fresh GitHub event re-crawl.
- Labels such as `outcome_reason` are LLM-generated (synonym inflation); this report coarsens merge/close groups.
- Fix actor / new-issue-in-fix findings are **text heuristics** — sample-check before paper use.
- Merge rate is merged / corpus n on the terminal snapshot (open PRs are not in this dataset).
