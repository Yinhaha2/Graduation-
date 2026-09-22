#!/usr/bin/env python3
"""RQ3 paper figures: reviewed-failure Pareto bars and a two-panel auxiliary.

Numbers come from analysis_viz/rq_analysis_metrics.json on the frozen terminal corpus.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

SHADOW = Path(__file__).resolve().parent.parent
METRICS = SHADOW / "analysis_viz" / "rq_analysis_metrics.json"
PAPER = Path(
    r"C:\Users\Y2698\Desktop\研究生\毕设\Agentic_Performance_PR_Analysis__EMSE_\pics\results"
)
RQFIGURE = PAPER / "RQFigure"

C_TOP = "#8C2F28"
C_REST = "#8A8A8A"
C_TECH = "#2F6F4E"
C_PROC = "#C47B3A"
C_EVID = "#8C2F28"
C_HUMAN = "#3D5A80"
C_AI = "#2F6F4E"
C_COLLAB = "#D4A574"
C_UNCLEAR = "#C8C8C8"

FAIL_LABEL = {
    "functional_or_correctness": "Functional / correctness",
    "design_or_approach": "Design / approach veto",
    "other_or_mixed": "Mixed / other",
    "missing_evidence": "Missing evidence",
    "ci_or_tests": "CI / test failure",
    "silent_or_unexplained": "Silence with signal",
    "scope": "Overscope",
}
FIX_LABEL = {
    "human_led_or_requested": ("Human-led", C_HUMAN),
    "ai_author_in_pr": ("AI author", C_AI),
    "human_ai_collaborative": ("Collaboration", C_COLLAB),
    "unclear": ("Unclear", C_UNCLEAR),
}

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 9.5,
        "axes.linewidth": 0.6,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)


def save(fig: plt.Figure, stem: str) -> None:
    PAPER.mkdir(parents=True, exist_ok=True)
    RQFIGURE.mkdir(parents=True, exist_ok=True)
    fig.savefig(PAPER / f"{stem}.png", dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(PAPER / f"{stem}.pdf", bbox_inches="tight", facecolor="white")
    fig.savefig(RQFIGURE / f"{stem}.pdf", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", stem, "-> RQFigure")


def load_metrics() -> dict:
    if not METRICS.exists():
        raise SystemExit(f"Missing {METRICS}; run python generate_rq_analysis.py first.")
    return json.loads(METRICS.read_text(encoding="utf-8"))


def plot_failure() -> None:
    m = load_metrics()
    reviewed_n = int(m.get("reviewed_closed_n") or 0)
    fail = m.get("failure_type") or {}
    rows = sorted(
        ((FAIL_LABEL.get(k, k), int(v), 100.0 * int(v) / reviewed_n if reviewed_n else 0.0) for k, v in fail.items()),
        key=lambda r: -r[1],
    )
    labs = [r[0] for r in rows]
    pcts = [r[2] for r in rows]
    ns = [r[1] for r in rows]
    colors = [C_TOP if i < 2 else C_REST for i in range(len(rows))]

    fig, ax = plt.subplots(figsize=(6.6, 3.85))
    y = np.arange(len(rows))[::-1]
    ax.barh(y, pcts, color=colors, height=0.68, edgecolor="none")
    for yi, p, n in zip(y, pcts, ns):
        ax.text(p + 0.7, yi, f"{p:.1f}%  (n={n})", ha="left", va="center", fontsize=8.2, color="#222")
    ax.set_yticks(y)
    ax.set_yticklabels(labs)
    ax.set_xlim(0, 50)
    ax.set_xticks([0, 10, 20, 30, 40, 50])
    ax.set_xticklabels(["0%", "10%", "20%", "30%", "40%", "50%"])
    ax.set_xlabel("Share of reviewed failures")
    ax.set_title(rf"Reviewed failures  ($n = {reviewed_n}$)", loc="center", fontsize=11, pad=8, color="#222")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    save(fig, "rq3_failure")


def plot_aux() -> None:
    m = load_metrics()
    bound = m.get("boundary_terminal_merge") or {}
    fig = plt.figure(figsize=(6.8, 4.85))
    gs = fig.add_gridspec(2, 1, height_ratios=[2.2, 1.15], hspace=0.62)

    ax = fig.add_subplot(gs[0])
    spec = [
        ("technical_stack", "Technical stack", C_TECH),
        ("process", "Process", C_PROC),
        ("evidence_required", "Evidence required", C_EVID),
    ]
    names = []
    rates = []
    colors = []
    for key, lab, col in spec:
        rec = bound.get(key) or {}
        n = int(rec.get("n") or 0)
        rate = 100.0 * float(rec.get("merge_rate") or 0.0)
        names.append(f"{lab}\n$n$={n}")
        rates.append(rate)
        colors.append(col)
    x = np.arange(len(names))
    ax.bar(x, rates, color=colors, width=0.62, edgecolor="none")
    for i, r in enumerate(rates):
        ax.text(i, r + 2.0, f"{r:.1f}%", ha="center", va="bottom", fontsize=8.8, fontweight="medium", color="#222")
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.set_ylim(0, 96)
    ax.set_ylabel("Terminal merge rate (%)")
    ax.set_title("Capability boundary", loc="left", fontsize=10.5, pad=6, color="#222")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax2 = fig.add_subplot(gs[1])
    modes = m.get("fix_modes") or {}
    total = sum(int(v) for v in modes.values()) or 1
    segs = []
    for key, (lab, col) in FIX_LABEL.items():
        n = int(modes.get(key) or 0)
        share = 100.0 * n / total
        segs.append((share, col, f"{lab} ({share:.1f}%)"))
    left = 0.0
    for pct, col, lab in segs:
        ax2.barh([0], [pct], left=left, height=0.45, color=col, edgecolor="white", linewidth=0.6, label=lab)
        left += pct
    ax2.set_xlim(0, 100)
    ax2.set_ylim(-0.7, 0.55)
    ax2.set_yticks([])
    ax2.set_xticks([0, 25, 50, 75, 100])
    ax2.set_xticklabels(["0%", "25%", "50%", "75%", "100%"])
    ax2.set_xlabel(f"Share of in-PR repairs  (n = {sum(int(v) for v in modes.values())})")
    ax2.set_title("Who repaired in the same PR", loc="left", fontsize=10.5, pad=2, color="#222")
    ax2.spines["top"].set_visible(False)
    ax2.spines["left"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.legend(
        frameon=False,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.55),
        ncol=2,
        fontsize=8.0,
        handlelength=1.2,
        columnspacing=1.4,
    )
    save(fig, "rq3_aux")


if __name__ == "__main__":
    plot_failure()
    plot_aux()
