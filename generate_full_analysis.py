#!/usr/bin/env python3
"""Aggregate perf PR analysis JSON into FullAnalysis.md and a distilled CSV."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
PER_PR = ROOT / "finaldatabase" / "per_pr"
OUT_MD = ROOT / "FullAnalysis.md"
OUT_CSV = ROOT / "full_analysis_distilled.csv"

FEWSHOT_ROOT_ONLY = [
    3228424652,
    3074351366,
    3194284966,
    3145702280,
    3125029980,
    3022909076,
]


def load_all_analyses() -> list[dict]:
    records: list[dict] = []
    seen: set[int] = set()

    for pr_dir in PER_PR.iterdir():
        if not pr_dir.is_dir():
            continue
        path = pr_dir / f"{pr_dir.name}_analysis.json"
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            records.append(data)
            seen.add(int(data["pr_id"]))

    for pr_id in FEWSHOT_ROOT_ONLY:
        if pr_id in seen:
            continue
        path = ROOT / f"{pr_id}_analysis.json"
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            records.append(data)
            seen.add(pr_id)

    records.sort(key=lambda d: d["pr_id"])
    return records


def flatten_record(d: dict) -> dict:
    meta = d.get("meta") or {}
    pl = d.get("perf_labels") or {}
    qm = d.get("quantitative_metrics") or {}
    cs = qm.get("change_scale") or {}
    col = qm.get("collaboration") or {}
    tl = qm.get("timeline") or {}
    es = qm.get("evidence_signals") or {}
    sa = d.get("structured_analysis") or {}
    moc = sa.get("merge_outcome_context") or {}
    rd = sa.get("review_details") or {}
    cb = sa.get("capability_boundary") or {}
    mp = sa.get("maintainer_practices") or {}
    dc = d.get("data_coverage") or {}

    def join_list(val):
        if not val:
            return ""
        if isinstance(val, list):
            return "|".join(str(x) for x in val)
        return str(val)

    return {
        "pr_id": d.get("pr_id"),
        "title": meta.get("title"),
        "html_url": meta.get("html_url"),
        "repo": meta.get("repo"),
        "agent": meta.get("agent"),
        "status": meta.get("status"),
        "topic_id": meta.get("topic_id"),
        "topic_name": meta.get("topic_name"),
        "aidev_task_type": meta.get("aidev_task_type"),
        "outcome": moc.get("outcome"),
        "outcome_reason": pl.get("outcome_reason"),
        "optimization_layer": pl.get("optimization_layer"),
        "perf_focus": join_list(pl.get("perf_focus")),
        "inefficiency_antipattern": join_list(pl.get("inefficiency_antipattern")),
        "evidence_type": join_list(pl.get("evidence_type")),
        "detection_method": join_list(pl.get("detection_method")),
        "reproducibility": pl.get("reproducibility"),
        "material_reproducibility": mp.get("material_reproducibility"),
        "regression_handling": pl.get("regression_handling"),
        "boundary_tag": pl.get("boundary_tag"),
        "boundary_type": cb.get("boundary_type"),
        "topic_difficulty": pl.get("topic_difficulty"),
        "blocking": pl.get("blocking"),
        "confidence": pl.get("confidence"),
        "primary_concern": rd.get("primary_concern"),
        "review_comment_bucket": rd.get("review_comment_bucket"),
        "review_dimensions": join_list(pl.get("review_dimensions")),
        "performance_evidence_in_review": rd.get("performance_evidence_in_review"),
        "antipattern_addressed": rd.get("antipattern_addressed"),
        "antipattern_in_fix": rd.get("antipattern_in_fix"),
        "changes": cs.get("changes"),
        "file_count": cs.get("file_count"),
        "commit_count": cs.get("commit_count"),
        "additions": cs.get("additions"),
        "deletions": cs.get("deletions"),
        "review_count": col.get("review_count"),
        "review_comment_count": col.get("review_comment_count"),
        "pr_comment_count": col.get("pr_comment_count"),
        "comment_total": (col.get("review_comment_count") or 0) + (col.get("pr_comment_count") or 0),
        "linked_issue_count": col.get("linked_issue_count") or 0,
        "has_linked_issue": (col.get("linked_issue_count") or 0) > 0,
        "lifespan_hours": tl.get("lifespan_hours"),
        "fast_merge": moc.get("lifecycle", {}).get("fast_merge"),
        "has_revert": tl.get("has_revert"),
        "body_has_repro_steps": es.get("body_has_repro_steps"),
        "body_has_benchmark_table": es.get("body_has_benchmark_table"),
        "body_has_numeric_perf_claim": es.get("body_has_numeric_perf_claim"),
        "has_formal_review": dc.get("has_formal_review"),
        "has_review_or_comment_text": dc.get("has_review_or_comment_text"),
        "evidence_gap": mp.get("evidence_gap"),
        "regression_detail": mp.get("regression_detail"),
        "reproducibility_notes": mp.get("reproducibility_notes"),
        "performance_claim": rd.get("performance_claim"),
        "notes": pl.get("notes"),
    }


def pct(n: int, total: int) -> str:
    return f"{100 * n / total:.1f}%" if total else "0.0%"


def top_counter(series: pd.Series, n: int = 10) -> str:
    c = series.value_counts().head(n)
    lines = []
    for k, v in c.items():
        lines.append(f"| `{k}` | {v} | {pct(v, len(series))} |")
    return "\n".join(lines)


def classify_merge_reason(reason: str) -> str:
    r = (reason or "").lower()
    if "small_scope" in r or "low_risk" in r:
        return "small_scope_low_risk"
    if "after_review" in r or "maintainer_fix" in r or "iterative" in r:
        return "after_review_iteration"
    if "no_review" in r or "self_merge" in r or "self_approved" in r:
        return "without_formal_review"
    return "other"


def classify_close_reason(reason: str) -> str:
    r = (reason or "").lower()
    if "stale" in r or "inactiv" in r:
        return "stale_or_inactivity"
    if "no_review" in r or "self_closed" in r or "author_closed" in r:
        return "closed_without_meaningful_review"
    if "functional" in r or "correctness" in r or "bug" in r or "test_failure" in r:
        return "functional_or_correctness"
    if "benchmark" in r or "evidence" in r or "missing" in r:
        return "missing_evidence_or_benchmark"
    if "scope" in r:
        return "scope_too_large"
    if "regression" in r or "performance" in r and "fail" in r:
        return "performance_regression_or_no_gain"
    return "other"


def classify_fix_mode(detail: str, trajectory: str) -> str:
    text = f"{detail} {trajectory}".lower()
    if re.search(r"requested changes|changes_requested|review requested|maintainer requested", text):
        if re.search(r"author|agent|commit|push", text):
            return "human_ai_collaborative"
    if re.search(r"maintainer|human reviewer|reviewer", text) and re.search(
        r"fix|commit|push|address", text
    ):
        return "human_led_or_requested"
    if re.search(r"author|agent|copilot|cursor|devin|claude", text) and re.search(
        r"commit|push|fix", text
    ):
        return "ai_author_in_pr"
    return "unclear"


def build_markdown(df: pd.DataFrame, records: list[dict]) -> str:
    n = len(df)
    merged = df[df["status"] == "merged"]
    closed = df[df["status"] == "closed"]
    open_ = df[df["status"] == "open"]
    terminal = df[df["status"].isin(["merged", "closed"])]

    merged_groups = merged["merge_reason_group"].value_counts()
    closed_groups = closed["close_reason_group"].value_counts()

    # bins
    bins = [0, 100, 500, 2000, 10000, 10**9]
    labels = ["≤100", "101–500", "501–2k", "2k–10k", ">10k"]
    terminal = terminal.copy()
    terminal["changes_bin"] = pd.cut(terminal["changes"], bins=bins, labels=labels)
    merge_by_bin = terminal.groupby("changes_bin", observed=True)["status"].apply(
        lambda s: (s == "merged").mean()
    )

    comment_bins = [0, 1, 3, 10, 10**9]
    comment_labels = ["0", "1–2", "3–9", "≥10"]
    terminal["comment_bin"] = pd.cut(terminal["comment_total"], bins=comment_bins, labels=comment_labels)
    merge_by_comment = terminal.groupby("comment_bin", observed=True)["status"].apply(
        lambda s: (s == "merged").mean()
    )

    lifespan_bins = [0, 1, 24, 168, 10**9]
    lifespan_labels = ["<1h", "1–24h", "1–7d", ">7d"]
    terminal["lifespan_bin"] = pd.cut(terminal["lifespan_hours"], bins=lifespan_bins, labels=lifespan_labels)
    merge_by_life = terminal.groupby("lifespan_bin", observed=True)["status"].apply(
        lambda s: (s == "merged").mean()
    )

    det = Counter()
    for methods in df["detection_method"].fillna(""):
        if not methods:
            det["(empty)"] += 1
            continue
        for m in methods.split("|"):
            det[m] += 1

    reg = df["regression_handling"].value_counts()
    repro = df["reproducibility"].value_counts()

    fix_modes = Counter()
    new_issue = 0
    for d in records:
        if d["perf_labels"].get("regression_handling") != "fix_in_pr":
            continue
        mp = d["structured_analysis"]["maintainer_practices"]
        traj = " ".join(d.get("evidence", {}).get("collaboration_trajectory") or [])
        fix_modes[classify_fix_mode(mp.get("regression_detail") or "", traj)] += 1

    anti_fix = df[
        df["antipattern_in_fix"].notna()
        & ~df["antipattern_in_fix"].astype(str).str.lower().isin(["none", "null", "nan"])
    ]

    linked = int(df["has_linked_issue"].sum())

    agent_merge = (
        df.groupby("agent", as_index=False)
        .agg(n=("pr_id", "count"), merge_rate=("status", lambda s: (s == "merged").mean()))
        .query("n >= 30")
        .sort_values("merge_rate", ascending=False)
    )

    opt_layer = df["optimization_layer"].value_counts().head(12)
    anti_merged = Counter()
    anti_closed = Counter()
    for _, row in df.iterrows():
        for ap in (row["inefficiency_antipattern"] or "").split("|"):
            if not ap or ap == "none":
                continue
            if row["status"] == "merged":
                anti_merged[ap] += 1
            elif row["status"] == "closed":
                anti_closed[ap] += 1

    lines = [
        "# Full Analysis — Agent Performance PR Corpus",
        "",
        f"> Built from `finaldatabase/per_pr/{{pr_id}}/{{pr_id}}_analysis.json` (plus 6 root few-shot gold labels); **{n}** PRs aligned with the master table.",
        f"> Wide table: `full_analysis_distilled.csv` (regenerate with `python3 generate_full_analysis.py`).",
        "",
        "---",
        "",
        "## 1. Outcome distribution",
        "",
        "| Status | Count | Share |",
        "|--------|-------|-------|",
        f"| merged | {len(merged)} | {pct(len(merged), n)} |",
        f"| closed (terminal, not merged) | {len(closed)} | {pct(len(closed), n)} |",
        f"| open | {len(open_)} | {pct(len(open_), n)} |",
        "",
        f"- **Overall merge rate** (incl. open): {pct(len(merged), n)} ({len(merged)}/{n})",
        f"- **Terminal merge rate** (merged + closed only, n={len(terminal)}): **{pct(len(merged), len(terminal))}**",
        "",
        "Note: `closed` means closed without merge on GitHub (not “approved”); `open` is still open at snapshot time.",
        "",
        "---",
        "",
        "## 2. Main reasons for merge vs close",
        "",
        "Grouped from `perf_labels.outcome_reason` (LLM labels in analysis JSON, not raw review text).",
        "",
        "### 2.1 Merged — grouped reasons",
        "",
        "| Group | Count | Share of merged |",
        "|-------|-------|-----------------|",
    ]
    for k, v in merged_groups.items():
        lines.append(f"| {k} | {v} | {pct(v, len(merged))} |")

    lines += [
        "",
        "**Reading (descriptive, not causal):** most merged PRs are labeled **small scope / low risk** (`small_scope_low_risk`); next is **merged after review iteration** (`after_review_iteration`); ~10% lack formal-review signals (`without_formal_review`).",
        "",
        "Merged `outcome_reason` raw Top 5:",
        "",
        "| outcome_reason | Count |",
        "|----------------|-------|",
    ]
    for k, v in merged["outcome_reason"].value_counts().head(5).items():
        lines.append(f"| `{k}` | {v} |")

    lines += [
        "",
        "### 2.2 Closed — grouped reasons",
        "",
        "| Group | Count | Share of closed |",
        "|-------|-------|-----------------|",
    ]
    for k, v in closed_groups.items():
        lines.append(f"| {k} | {v} | {pct(v, len(closed))} |")

    lines += [
        "",
        "**Reading:** closed is dominated by **process closes** (stale / no review / author closed), not a single “perf failed” label; among PRs with review text, `functional_failure` and `correctness_edge_case` stand out more.",
        "",
        "Closed `outcome_reason` raw Top 5:",
        "",
        "| outcome_reason | Count |",
        "|----------------|-------|",
    ]
    for k, v in closed["outcome_reason"].value_counts().head(5).items():
        lines.append(f"| `{k}` | {v} |")

    lines += [
        "",
        "---",
        "",
        "## 3. Outcome vs change size / comment volume",
        "",
        "### 3.1 Code churn (`changes`)",
        "",
        "| Changes bin | Terminal PRs | Merge rate |",
        "|-------------|--------------|------------|",
    ]
    for idx, rate in merge_by_bin.items():
        cnt = int((terminal["changes_bin"] == idx).sum())
        lines.append(f"| {idx} | {cnt} | {100*rate:.1f}% |")

    lines += [
        "",
        f"- Median changes — merged: **{merged['changes'].median():.0f}**; closed: **{closed['changes'].median():.0f}**",
        "- **No “more changes ⇒ more merges” pattern:** ≤100-line bin has the highest merge rate (~63%); >10k is ~52%.",
        "",
        "### 3.2 Comment volume (review + PR comments)",
        "",
        "| Comment bin | Terminal PRs | Merge rate |",
        "|-------------|--------------|------------|",
    ]
    for idx, rate in merge_by_comment.items():
        cnt = int((terminal["comment_bin"] == idx).sum())
        lines.append(f"| {idx} | {cnt} | {100*rate:.1f}% |")

    lines += [
        "",
        f"- Median comment total — merged: **{merged['comment_total'].median():.0f}**; closed: **{closed['comment_total'].median():.0f}**",
        "- Zero-comment PRs have higher merge rates (fast merge / no review path); high comment volume does not imply higher merge rate.",
        "",
        "---",
        "",
        "## 4. Outcome vs PR lifespan",
        "",
        "| Lifespan | Terminal PRs | Merge rate |",
        "|----------|--------------|------------|",
    ]
    for idx, rate in merge_by_life.items():
        cnt = int((terminal["lifespan_bin"] == idx).sum())
        lines.append(f"| {idx} | {cnt} | {100*rate:.1f}% |")

    lines += [
        "",
        f"- Median lifespan — merged: **{merged['lifespan_hours'].median():.3f} h** (~{merged['lifespan_hours'].median()*60:.0f} min)",
        f"- Median lifespan — closed: **{closed['lifespan_hours'].median():.1f} h** (~{closed['lifespan_hours'].median()/24:.1f} d)",
        f"- Share with `fast_merge=true` — merged: **{merged['fast_merge'].mean()*100:.1f}%**; closed: 0%",
        "",
        "**Association:** merged PRs are much shorter-lived; long-lived closed PRs often track stale / no interaction, not slow rejection after review.",
        "",
        "---",
        "",
        "## 5. Optimization layer and antipatterns",
        "",
        "### 5.1 `optimization_layer` (Top 12)",
        "",
        "| optimization_layer | Count | Share |",
        "|--------------------|-------|-------|",
    ]
    for k, v in opt_layer.items():
        lines.append(f"| `{k}` | {v} | {pct(v, n)} |")

    lines += [
        "",
        "### 5.2 Inefficiency antipatterns (`inefficiency_antipattern` ≠ none)",
        "",
        "**Merged top:** " + ", ".join(f"`{k}`({v})" for k, v in anti_merged.most_common(6)),
        "",
        "**Closed top:** " + ", ".join(f"`{k}`({v})" for k, v in anti_closed.most_common(6)),
        "",
        "`repeated_io` leads on both sides (slightly more on closed). Most PRs are still labeled `none`.",
        "",
        "---",
        "",
        "## 6. How maintainers detect perf issues",
        "",
        "Field: `perf_labels.detection_method` (multi-label).",
        "",
        "| detection_method | PR count | Share of corpus |",
        "|------------------|----------|-----------------|",
    ]
    for k, v in det.most_common(10):
        lines.append(f"| `{k}` | {v} | {pct(v, n)} |")

    lines += [
        "",
        "- **Dominant when observable:** **`code_reading`** (~378 PRs with at least one hit).",
        "- Next: **`ci_auto`** (~93); `profiler` / `load_test` / `benchmark` alone are rare.",
        "- ~**786** labeled `unknown`, consistent with ~**71%** lacking formal review — detection is often unobservable.",
        "",
        "---",
        "",
        "## 7. Can PR materials support perf-defect reproduction?",
        "",
        "| reproducibility | Count | Share |",
        "|-----------------|-------|-------|",
    ]
    for k, v in repro.items():
        lines.append(f"| `{k}` | {v} | {pct(v, n)} |")

    lines += [
        "",
        "Auxiliary signals:",
        f"- `body_has_repro_steps=true`: **{int(df['body_has_repro_steps'].sum())}** ({pct(int(df['body_has_repro_steps'].sum()), n)})",
        f"- `body_has_benchmark_table=true`: **{int(df['body_has_benchmark_table'].sum())}**",
        f"- `material_reproducibility=sufficient`: **{int((df['material_reproducibility']=='sufficient').sum())}**",
        "",
        "**Material-dimension takeaway:** most PRs are **insufficient or partial**; only ~**2%** reach sufficient.",
        "",
        "---",
        "",
        "## 8. Regression / review-issue handling",
        "",
        "| regression_handling | Count | Share |",
        "|---------------------|-------|-------|",
    ]
    for k, v in reg.items():
        lines.append(f"| `{k}` | {v} | {pct(v, n)} |")

    fix_total = int((df["regression_handling"] == "fix_in_pr").sum())
    lines += [
        "",
        f"- **`not_applicable`** ({pct(int((df['regression_handling']=='not_applicable').sum()), n)}): no clear regression-handling context (often direct merge or process close).",
        f"- **`reject_close`** ({pct(int((df['regression_handling']=='reject_close').sum()), n)}): reject/close dominant; mostly among closed.",
        f"- **`fix_in_pr`** ({fix_total}): fixed in the same PR; `revert` only **{int((df['regression_handling']=='revert').sum())}**.",
        "",
        "### 8.1 Who fixes in `fix_in_pr` (heuristic text labels, not ground truth)",
        "",
        "| Fix mode | Count | Share of fix_in_pr |",
        "|----------|-------|--------------------|",
    ]
    for k, v in fix_modes.most_common():
        lines.append(f"| {k} | {v} | {pct(v, fix_total)} |")

    lines += [
        "",
        "- Each PR has a single `meta.agent`; no structured multi-agent field — cannot systematically measure multi-agent co-fixes.",
        f"- New-issue-in-fix signal: `antipattern_in_fix` ≠ none on **{len(anti_fix)}** PRs ({pct(len(anti_fix), n)}).",
        "",
        "---",
        "",
        "## 9. Linked issues",
        "",
        f"- `linked_issue_count > 0`: **{linked}** (**{pct(linked, n)}**)",
        f"- No linked issue: **{n - linked}** (**{pct(n - linked, n)}**)",
        "",
        "Most agent perf PRs are **not** clearly opened to fix a linked issue; optimizations are often agent-initiated.",
        "",
        "---",
        "",
        "## 10. Pass rate, focus distribution, capability boundaries",
        "",
        f"- **Terminal merge rate for AI perf PRs: ~{100*len(merged)/len(terminal):.1f}%** ({len(merged)}/{len(terminal)}).",
        "",
        "### 10.1 Common `perf_focus` on merged",
        "",
    ]
    pf_m = Counter()
    for _, row in merged.iterrows():
        for f in (row["perf_focus"] or "").split("|"):
            if f:
                pf_m[f] += 1
    lines.append(", ".join(f"`{k}`({v})" for k, v in pf_m.most_common(8)))

    lines += [
        "",
        "### 10.2 Common `perf_focus` on closed",
        "",
    ]
    pf_c = Counter()
    for _, row in closed.iterrows():
        for f in (row["perf_focus"] or "").split("|"):
            if f:
                pf_c[f] += 1
    lines.append(", ".join(f"`{k}`({v})" for k, v in pf_c.most_common(8)))

    lines += [
        "",
        "### 10.3 `boundary_tag` distribution",
        "",
        "| boundary_tag | Count |",
        "|--------------|-------|",
    ]
    for k, v in df["boundary_tag"].value_counts().items():
        lines.append(f"| `{k}` | {v} |")

    lines += [
        "",
        "### 10.4 Strengths vs boundaries (label-based; needs human check)",
        "",
        "**Strengths (merged-side signals)**",
        "- Small-scope control-flow / compiler constant-folding / build-and-cache changes merge more easily under low review friction.",
        "- `technical_stack` dominates (608), i.e. problems in a routine stack layer agents can often handle.",
        "",
        "**Boundaries (closed / higher-risk signals)**",
        "- Process closes (stale / no review) dominate and mask true “perf rejected” rates.",
        "- `evidence_required` boundaries (35) align with `missing_benchmark` / insufficient reproducibility.",
        "- Large churn (>10k changes) does not merge better; `repeated_io` is slightly higher on closed.",
        "- Without reproducible materials, review is hard to close.",
        "",
        "---",
        "",
        "## 11. Merge rate by agent (n≥30)",
        "",
        "| Agent | PRs | Merge rate |",
        "|-------|-----|------------|",
    ]
    for _, row in agent_merge.iterrows():
        lines.append(f"| {row['agent']} | {int(row['n'])} | {100*row['merge_rate']:.1f}% |")

    lines += [
        "",
        "---",
        "",
        "## 12. Data & method notes",
        "",
        "- Stats use **labels and narrative fields** in analysis JSON, not a fresh GitHub event re-crawl.",
        "- Labels such as `outcome_reason` are LLM-generated (synonym inflation); this report coarsens merge/close groups.",
        "- Fix actor / new-issue-in-fix findings are **text heuristics** — sample-check before paper use.",
        "- Open PRs should usually be excluded or reported separately when computing pass rates.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    records = load_all_analyses()
    if not records:
        raise SystemExit("No analysis JSON files found.")

    df = pd.DataFrame([flatten_record(d) for d in records])
    df["merge_reason_group"] = df["outcome_reason"].map(classify_merge_reason)
    df["close_reason_group"] = df["outcome_reason"].map(classify_close_reason)
    df.to_csv(OUT_CSV, index=False, encoding="utf-8")

    md = build_markdown(df, records)
    OUT_MD.write_text(md, encoding="utf-8")

    print(f"Wrote {OUT_CSV} ({len(df)} rows)")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
