# Full Analysis — Agent Performance PR Corpus

> Built from `finaldatabase/per_pr/{pr_id}/{pr_id}_analysis.json` (plus 6 root few-shot gold labels); **1219** PRs aligned with the master table.
> Wide table: `full_analysis_distilled.csv` (regenerate with `python3 generate_full_analysis.py`).

---

## 1. Outcome distribution

| Status | Count | Share |
|--------|-------|-------|
| merged | 671 | 55.0% |
| closed (terminal, not merged) | 509 | 41.8% |
| open | 39 | 3.2% |

- **Overall merge rate** (incl. open): 55.0% (671/1219)
- **Terminal merge rate** (merged + closed only, n=1180): **56.9%**

Note: `closed` means closed without merge on GitHub (not “approved”); `open` is still open at snapshot time.

---

## 2. Main reasons for merge vs close

Grouped from `perf_labels.outcome_reason` (LLM labels in analysis JSON, not raw review text).

### 2.1 Merged — grouped reasons

| Group | Count | Share of merged |
|-------|-------|-----------------|
| small_scope_low_risk | 437 | 65.1% |
| after_review_iteration | 88 | 13.1% |
| without_formal_review | 77 | 11.5% |
| other | 69 | 10.3% |

**Reading (descriptive, not causal):** most merged PRs are labeled **small scope / low risk** (`small_scope_low_risk`); next is **merged after review iteration** (`after_review_iteration`); ~10% lack formal-review signals (`without_formal_review`).

Merged `outcome_reason` raw Top 5:

| outcome_reason | Count |
|----------------|-------|
| `merged_small_scope_low_risk` | 388 |
| `merged_after_review_fix` | 70 |
| `merged_small_scope_no_review` | 18 |
| `merged_self_merge_no_review` | 7 |
| `merged_small_scope_self_merge` | 6 |

### 2.2 Closed — grouped reasons

| Group | Count | Share of closed |
|-------|-------|-----------------|
| other | 203 | 39.9% |
| stale_or_inactivity | 140 | 27.5% |
| closed_without_meaningful_review | 127 | 25.0% |
| functional_or_correctness | 24 | 4.7% |
| missing_evidence_or_benchmark | 11 | 2.2% |
| performance_regression_or_no_gain | 3 | 0.6% |
| scope_too_large | 1 | 0.2% |

**Reading:** closed is dominated by **process closes** (stale / no review / author closed), not a single “perf failed” label; among PRs with review text, `functional_failure` and `correctness_edge_case` stand out more.

Closed `outcome_reason` raw Top 5:

| outcome_reason | Count |
|----------------|-------|
| `stale_no_review_engagement` | 49 |
| `stale_inactivity` | 32 |
| `closed_by_author_no_review` | 13 |
| `closed_no_review_engagement` | 12 |
| `self_closed_no_review` | 12 |

---

## 3. Outcome vs change size / comment volume

### 3.1 Code churn (`changes`)

| Changes bin | Terminal PRs | Merge rate |
|-------------|--------------|------------|
| ≤100 | 476 | 63.2% |
| 101–500 | 349 | 52.4% |
| 501–2k | 195 | 54.4% |
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
| ≥10 | 75 | 50.7% |

- Median comment total — merged: **0**; closed: **2**
- Zero-comment PRs have higher merge rates (fast merge / no review path); high comment volume does not imply higher merge rate.

---

## 4. Outcome vs PR lifespan

| Lifespan | Terminal PRs | Merge rate |
|----------|--------------|------------|
| <1h | 573 | 76.6% |
| 1–24h | 236 | 57.2% |
| 1–7d | 180 | 40.0% |
| >7d | 150 | 16.7% |

- Median lifespan — merged: **0.077 h** (~5 min)
- Median lifespan — closed: **23.6 h** (~1.0 d)
- Share with `fast_merge=true` — merged: **78.7%**; closed: 0%

**Association:** merged PRs are much shorter-lived; long-lived closed PRs often track stale / no interaction, not slow rejection after review.

---

## 5. Optimization layer and antipatterns

### 5.1 `optimization_layer` (Top 12)

| optimization_layer | Count | Share |
|--------------------|-------|-------|
| `application_service` | 201 | 16.5% |
| `build` | 165 | 13.5% |
| `frontend_ui` | 137 | 11.2% |
| `runtime_library` | 122 | 10.0% |
| `application_control_flow` | 87 | 7.1% |
| `compiler` | 45 | 3.7% |
| `infrastructure` | 35 | 2.9% |
| `runtime_vm` | 29 | 2.4% |
| `compiler_backend` | 26 | 2.1% |
| `compiler_optimization` | 15 | 1.2% |
| `compiler_codegen` | 14 | 1.1% |
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
| `unknown` | 786 | 64.5% |
| `code_reading` | 378 | 31.0% |
| `ci_auto` | 93 | 7.6% |
| `manual_testing` | 18 | 1.5% |
| `manual_test` | 8 | 0.7% |
| `benchmark` | 6 | 0.5% |
| `load_test` | 5 | 0.4% |
| `(empty)` | 4 | 0.3% |
| `profiler` | 3 | 0.2% |
| `unit_test` | 3 | 0.2% |

- **Dominant when observable:** **`code_reading`** (~378 PRs with at least one hit).
- Next: **`ci_auto`** (~93); `profiler` / `load_test` / `benchmark` alone are rare.
- ~**786** labeled `unknown`, consistent with ~**71%** lacking formal review — detection is often unobservable.

---

## 7. Can PR materials support perf-defect reproduction?

| reproducibility | Count | Share |
|-----------------|-------|-------|
| `insufficient` | 754 | 61.9% |
| `partial` | 240 | 19.7% |
| `unknown` | 200 | 16.4% |
| `sufficient` | 25 | 2.1% |

Auxiliary signals:
- `body_has_repro_steps=true`: **55** (4.5%)
- `body_has_benchmark_table=true`: **51**
- `material_reproducibility=sufficient`: **25**

**Material-dimension takeaway:** most PRs are **insufficient or partial**; only ~**2%** reach sufficient.

---

## 8. Regression / review-issue handling

| regression_handling | Count | Share |
|---------------------|-------|-------|
| `not_applicable` | 626 | 51.4% |
| `reject_close` | 397 | 32.6% |
| `fix_in_pr` | 148 | 12.1% |
| `unknown` | 20 | 1.6% |
| `ignore` | 18 | 1.5% |
| `revert` | 2 | 0.2% |
| `fix_followup` | 2 | 0.2% |
| `close_no_merge` | 1 | 0.1% |
| `fix_pending` | 1 | 0.1% |
| `abandon` | 1 | 0.1% |
| `recreated_in_new_pr` | 1 | 0.1% |
| `closed_no_merge` | 1 | 0.1% |
| `draft_converted_no_fix` | 1 | 0.1% |

- **`not_applicable`** (51.4%): no clear regression-handling context (often direct merge or process close).
- **`reject_close`** (32.6%): reject/close dominant; mostly among closed.
- **`fix_in_pr`** (148): fixed in the same PR; `revert` only **2**.

### 8.1 Who fixes in `fix_in_pr` (heuristic text labels, not ground truth)

| Fix mode | Count | Share of fix_in_pr |
|----------|-------|--------------------|
| human_led_or_requested | 82 | 55.4% |
| ai_author_in_pr | 33 | 22.3% |
| human_ai_collaborative | 22 | 14.9% |
| unclear | 11 | 7.4% |

- Each PR has a single `meta.agent`; no structured multi-agent field — cannot systematically measure multi-agent co-fixes.
- New-issue-in-fix signal: `antipattern_in_fix` ≠ none on **8** PRs (0.7%).

---

## 9. Linked issues

- `linked_issue_count > 0`: **215** (**17.6%**)
- No linked issue: **1004** (**82.4%**)

Most agent perf PRs are **not** clearly opened to fix a linked issue; optimizations are often agent-initiated.

---

## 10. Pass rate, focus distribution, capability boundaries

- **Terminal merge rate for AI perf PRs: ~56.9%** (671/1180).

### 10.1 Common `perf_focus` on merged

`constant_folding`(23), `compiler_optimization`(21), `benchmark_infrastructure`(11), `cache`(8), `lazy_loading`(7), `compile_time_optimization`(7), `caching`(6), `compiler_codegen`(6)

### 10.2 Common `perf_focus` on closed

`bundle_size_reduction`(12), `constant_folding`(10), `cache`(9), `build_performance`(7), `caching`(6), `lazy_load`(6), `code_splitting`(6), `compiler_optimization`(6)

### 10.3 `boundary_tag` distribution

| boundary_tag | Count |
|--------------|-------|
| `technical_stack` | 608 |
| `process` | 575 |
| `evidence_required` | 35 |
| `unknown` | 1 |

### 10.4 Strengths vs boundaries (label-based; needs human check)

**Strengths (merged-side signals)**
- Small-scope control-flow / compiler constant-folding / build-and-cache changes merge more easily under low review friction.
- `technical_stack` dominates (608), i.e. problems in a routine stack layer agents can often handle.

**Boundaries (closed / higher-risk signals)**
- Process closes (stale / no review) dominate and mask true “perf rejected” rates.
- `evidence_required` boundaries (35) align with `missing_benchmark` / insufficient reproducibility.
- Large churn (>10k changes) does not merge better; `repeated_io` is slightly higher on closed.
- Without reproducible materials, review is hard to close.

---

## 11. Merge rate by agent (n≥30)

| Agent | PRs | Merge rate |
|-------|-----|------------|
| OpenAI_Codex | 639 | 70.7% |
| Claude_Code | 38 | 55.3% |
| Cursor | 95 | 50.5% |
| Copilot | 222 | 34.7% |
| Devin | 225 | 32.4% |

---

## 12. Data & method notes

- Stats use **labels and narrative fields** in analysis JSON, not a fresh GitHub event re-crawl.
- Labels such as `outcome_reason` are LLM-generated (synonym inflation); this report coarsens merge/close groups.
- Fix actor / new-issue-in-fix findings are **text heuristics** — sample-check before paper use.
- Open PRs should usually be excluded or reported separately when computing pass rates.
