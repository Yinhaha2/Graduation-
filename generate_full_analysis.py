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
OUT_MD = ROOT / "analysis_viz" / "FullAnalysis.md"
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


# Inclusive left edges so 0-line / 0-comment PRs are not dropped by pd.cut.
CHANGES_BINS = [-0.1, 100, 500, 2000, 10000, 10**9]
CHANGES_LABELS = ["≤100", "101–500", "501–2k", "2k–10k", ">10k"]
COMMENT_BINS = [-0.1, 0.5, 2.5, 9.5, 10**9]
COMMENT_LABELS = ["0", "1–2", "3–9", "≥10"]
FILE_BINS = [-0.1, 0.5, 1.5, 5.5, 20.5, 100.5, 10**9]
FILE_LABELS = ["0", "1", "2–5", "6–20", "21–100", ">100"]
LIFESPAN_BINS = [-0.1, 1, 24, 168, 10**9]
LIFESPAN_LABELS = ["<1h", "1–24h", "1–7d", ">7d"]


def assign_bin(series: pd.Series, bins: list, labels: list) -> pd.Series:
    return pd.cut(series, bins=bins, labels=labels, include_lowest=True)


def top_counter(series: pd.Series, n: int = 10) -> str:
    c = series.value_counts().head(n)
    lines = []
    for k, v in c.items():
        lines.append(f"| `{k}` | {v} | {pct(v, len(series))} |")
    return "\n".join(lines)


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

    terminal = terminal.copy()
    terminal["changes_bin"] = assign_bin(terminal["changes"], CHANGES_BINS, CHANGES_LABELS)
    merge_by_bin = terminal.groupby("changes_bin", observed=True)["status"].apply(
        lambda s: (s == "merged").mean()
    )

    terminal["comment_bin"] = assign_bin(terminal["comment_total"], COMMENT_BINS, COMMENT_LABELS)
    merge_by_comment = terminal.groupby("comment_bin", observed=True)["status"].apply(
        lambda s: (s == "merged").mean()
    )

    terminal["lifespan_bin"] = assign_bin(terminal["lifespan_hours"], LIFESPAN_BINS, LIFESPAN_LABELS)
    merge_by_life = terminal.groupby("lifespan_bin", observed=True)["status"].apply(
        lambda s: (s == "merged").mean()
    )
    life_missing = int(terminal["lifespan_hours"].isna().sum())
    life_missing_merged = int(
        ((terminal["lifespan_hours"].isna()) & (terminal["status"] == "merged")).sum()
    )

    det = Counter()
    for methods in df["detection_method"].fillna(""):
        if not methods:
            det["(empty)"] += 1
            continue
        for m in methods.split("|"):
            det[m] += 1

    reg = df["regression_handling"].fillna("(empty)").value_counts()
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
            if not ap or ap in {"none", "unknown"}:
                continue
            if row["status"] == "merged":
                anti_merged[ap] += 1
            elif row["status"] == "closed":
                anti_closed[ap] += 1

    outcome_rows = [
        f"| merged | {len(merged)} | {pct(len(merged), n)} |",
        f"| closed (not merged) | {len(closed)} | {pct(len(closed), n)} |",
    ]
    if len(open_):
        outcome_rows.append(f"| open | {len(open_)} | {pct(len(open_), n)} |")
        rate_lines = [
            f"- **Overall merge rate** (incl. open): {pct(len(merged), n)} ({len(merged)}/{n})",
            f"- **Terminal merge rate** (merged + closed only, n={len(terminal)}): **{pct(len(merged), len(terminal))}**",
            "",
            "Note: `closed` means closed without merge on GitHub (not “approved”); `open` is still open at snapshot time.",
        ]
    else:
        rate_lines = [
            f"- **Merge rate** (merged / n): **{pct(len(merged), n)}** ({len(merged)}/{n})",
            "",
            "Note: this snapshot is **terminal-only** (`merged` vs `closed` without merge). Still-open PRs were removed and are not in the denominator.",
        ]

    lines = [
        "# Full Analysis — Agent Performance PR Corpus",
        "",
        f"> **最终数据集**：{n} PR，{len(merged)} merged，{len(closed)} closed。合并率 **{pct(len(merged), n)}**（{len(merged)}/{n}）。全库统一口径：仅终态 merged / closed，不含 open。",
        "> Built from `finaldatabase/per_pr/{pr_id}/{pr_id}_analysis.json`.",
        f"> Wide table: `full_analysis_distilled.csv` (regenerate with `python generate_full_analysis.py`).",
        "",
        "---",
        "",
        "## 1. Outcome distribution",
        "",
        "| Status | Count | Share |",
        "|--------|-------|-------|",
        *outcome_rows,
        "",
        *rate_lines,
        "",
        "---",
        "",
        "## 2. Merge path and close motivation",
        "",
        "Same partition as `RQ_Analysis.md`: `merged_path` on merged PRs, `close_motivation` on closed PRs.",
        "",
        "### 2.1 `merged_path`",
        "",
        "| merged_path | Count | Share of merged |",
        "|-------------|-------|-----------------|",
    ]
    path_counts = merged["merged_path"].value_counts()
    for k, v in path_counts.items():
        lines.append(f"| `{k}` | {int(v)} | {pct(int(v), len(merged))} |")
    lines.append("")
    lines.append(f"Rows sum to {int(path_counts.sum())}/{len(merged)}.")
    blank = merged[merged["outcome_reason"].fillna("").astype(str).str.strip().eq("")]
    if len(blank):
        bits = ", ".join(f"`{k}` {int(v)}" for k, v in blank["merged_path"].value_counts().items())
        lines.append("")
        lines.append(
            f"{len(blank)} merged PRs have an empty `outcome_reason` "
            "(status restored to merged from the refresh cache). "
            f"They are already inside the path table: {bits}."
        )

    mot_counts = closed["close_motivation"].value_counts()
    lines += [
        "",
        "### 2.2 `close_motivation`",
        "",
        "Status `closed` is not merged. The rows below split that status; they are not a second corpus.",
        "",
        "| close_motivation | Count | Share of closed |",
        "|------------------|-------|-----------------|",
    ]
    for k, v in mot_counts.items():
        lines.append(f"| `{k}` | {int(v)} | {pct(int(v), len(closed))} |")
    lines.append("")
    lines.append(f"Rows sum to {int(mot_counts.sum())}/{len(closed)}.")

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
        f"- Zero-line churn (`changes=0`) is counted in ≤100 ({int((terminal['changes']==0).sum())} PRs, all closed).",
        f"- Change-size bins sum to {int(terminal['changes_bin'].notna().sum())}/{len(terminal)}.",
        "- **No “more changes ⇒ more merges” pattern:** the ≤100-line bin has the highest merge rate; the >10k bin does not exceed it.",
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
        f"- Zero-comment PRs: **{int((terminal['comment_total'].fillna(0)==0).sum())}** "
        f"({pct(int((terminal['comment_total'].fillna(0)==0).sum()), len(terminal))}); "
        "this bin is `comment_total==0`, not a `pd.cut` interval that starts after 0. "
        f"Comment bins sum to {int(terminal['comment_bin'].notna().sum())}/{len(terminal)}. "
        "High comment volume does not imply a higher merge rate.",
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
    if life_missing:
        miss_rate = life_missing_merged / life_missing if life_missing else 0
        lines.append(f"| (lifespan missing) | {life_missing} | {100*miss_rate:.1f}% |")

    lines += [
        "",
        f"- Median lifespan — merged: **{merged['lifespan_hours'].median():.3f} h** (~{merged['lifespan_hours'].median()*60:.0f} min)",
        f"- Median lifespan — closed: **{closed['lifespan_hours'].median():.1f} h** (~{closed['lifespan_hours'].median()/24:.1f} d)",
        f"- Share with `fast_merge=true` — merged: **{merged['fast_merge'].mean()*100:.1f}%**; closed: 0%",
        "",
        (
            lambda lc, ls, lr: (
                f"**Association:** merged PRs are much shorter-lived. Among closed PRs with lifespan >7d ({lc}), "
                f"`silent_abandonment` is {ls} and `real_rejection` is {lr}. "
                "Long lifespan is not the same as slow rejection after review, and it is not only abandonment."
            )
        )(
            int((closed["lifespan_hours"] > 168).sum()),
            int(((closed["lifespan_hours"] > 168) & (closed["close_motivation"] == "silent_abandonment")).sum()),
            int(((closed["lifespan_hours"] > 168) & (closed["close_motivation"] == "real_rejection")).sum()),
        ),
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
        f"Top 12 sum to {int(opt_layer.sum())}; the remaining {n - int(opt_layer.sum())} PRs sit in less frequent layers and are not listed.",
        "",
        "### 5.2 Inefficiency antipatterns (`inefficiency_antipattern` ≠ none / unknown)",
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

    extra_det = int(sum(det.values()) - sum(v for _, v in det.most_common(10)))
    no_review_share = (df["review_count"].fillna(0) == 0).mean() if "review_count" in df.columns else 0
    lines += [
        "",
        "Counts are PR hits (multi-label); row totals can exceed corpus n."
        + (f" Labels beyond the top 10 account for {extra_det} additional hits." if extra_det else ""),
        f"- **Dominant when observable:** **`code_reading`** ({det.get('code_reading', 0)} PRs with at least one hit).",
        f"- Next: **`ci_auto`** ({det.get('ci_auto', 0)}); `profiler` / `load_test` / `benchmark` alone are rare.",
        f"- **{det.get('unknown', 0)}** labeled `unknown`, consistent with **{100*no_review_share:.1f}%** ({int((df['review_count'].fillna(0)==0).sum())}/{n}) having `review_count=0` — detection is often unobservable.",
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
    lines.append("")
    lines.append(f"Rows sum to {int(repro.sum())}/{n}.")

    lines += [
        "",
        "Auxiliary signals:",
        f"- `body_has_repro_steps=true`: **{int(df['body_has_repro_steps'].sum())}** ({pct(int(df['body_has_repro_steps'].sum()), n)})",
        f"- `body_has_benchmark_table=true`: **{int(df['body_has_benchmark_table'].sum())}**",
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
        f"Rows sum to {int(reg.sum())}/{n}. `reject_close` is this field's label, not `close_motivation=real_rejection`.",
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
        f"- No linked issue: **{n - linked}** (**{pct(n - linked, n)}** of corpus); "
        f"merged **{int((~merged['has_linked_issue'].fillna(False)).sum())}/{len(merged)}** "
        f"({pct(int((~merged['has_linked_issue'].fillna(False)).sum()), len(merged))}); "
        f"closed **{int((~closed['has_linked_issue'].fillna(False)).sum())}/{len(closed)}** "
        f"({pct(int((~closed['has_linked_issue'].fillna(False)).sum()), len(closed))}).",
        "",
        "Most agent perf PRs are **not** clearly opened to fix a linked issue; optimizations are often agent-initiated.",
        "",
        "---",
        "",
        "## 10. Merge rate, focus distribution, capability boundaries",
        "",
        f"- **Merge rate for AI perf PRs: {100*len(merged)/n:.1f}%** ({len(merged)}/{n}).",
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
        (
            f"- In the lists above, `constant_folding` is {pf_m.get('constant_folding', 0)} merged / "
            f"{pf_c.get('constant_folding', 0)} closed, and `compiler_optimization` is "
            f"{pf_m.get('compiler_optimization', 0)} / {pf_c.get('compiler_optimization', 0)}. "
            f"`cache` is {pf_m.get('cache', 0)} / {pf_c.get('cache', 0)}, "
            f"`caching` is {pf_m.get('caching', 0)} / {pf_c.get('caching', 0)}, and "
            f"`build_performance` is {pf_m.get('build_performance', 0)} / {pf_c.get('build_performance', 0)}: "
            "those three do not have a higher merged count. "
            f"`technical_stack` is a separate analytic tag; its median `changes` is "
            f"{df.loc[df['boundary_tag']=='technical_stack', 'changes'].median():.0f}, "
            f"and `process` is {df.loc[df['boundary_tag']=='process', 'changes'].median():.0f}."
        ),
        f"- `technical_stack` ({int((df['boundary_tag']=='technical_stack').sum())}) is an analytic tag for routine stack-layer work, not a measured agent ability.",
        "",
        "**Boundaries (closed / higher-risk signals)**",
        f"- Among closed, `silent_abandonment` is {int((closed['close_motivation']=='silent_abandonment').sum())} and `real_rejection` is {int((closed['close_motivation']=='real_rejection').sum())} (same split as §2.2).",
        "- Large churn (>10k changes) does not merge better; `repeated_io` is slightly higher on closed.",
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
        "- `merged_path` / `close_motivation` are the same partition as `RQ_Analysis.md`. `outcome_reason` strings are not a second grouping.",
        "- Fix actor / new-issue-in-fix findings are **text heuristics** — sample-check before paper use.",
        "- Merge rate is merged / corpus n on the terminal snapshot (open PRs are not in this dataset).",
        "- `merged_at` / `closed_at` on the formerly-open cohort follow `summary/github_status_cache.json` (the refresh log). Where that cache showed a merge the master had missed, status is merged and the old closed-state `outcome_reason` is left empty.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    records = load_all_analyses()
    if not records:
        raise SystemExit("No analysis JSON files found.")

    from generate_rq_analysis import (
        classify_close_motivation,
        classify_merged_path,
        enrich_row,
    )

    df = pd.DataFrame([enrich_row(d, flatten_record(d)) for d in records])
    merged_mask = df["status"].eq("merged")
    closed_mask = df["status"].eq("closed")
    df["merged_path"] = pd.NA
    df["close_motivation"] = pd.NA
    df.loc[merged_mask, "merged_path"] = df.loc[merged_mask].apply(classify_merged_path, axis=1)
    df.loc[closed_mask, "close_motivation"] = df.loc[closed_mask].apply(
        classify_close_motivation, axis=1
    )
    drop_cols = [
        c
        for c in (
            "rejection_signals",
            "concern_detail",
            "changes_requested_n",
            "review_states_json",
            "collaboration_trajectory",
        )
        if c in df.columns
    ]
    df.drop(columns=drop_cols).to_csv(OUT_CSV, index=False, encoding="utf-8")

    md = build_markdown(df, records)
    OUT_MD.write_text(md, encoding="utf-8")

    print(f"Wrote {OUT_CSV} ({len(df)} rows)")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
