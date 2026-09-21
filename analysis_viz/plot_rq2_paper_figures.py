#!/usr/bin/env python3
"""RQ2 paper figures: lifespan cliff (bar+line) and detection-method contrast.

Computed on the frozen terminal corpus (merged+closed only).
detection_method is multi-label.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SHADOW = Path(__file__).resolve().parent.parent
CSV = SHADOW / "full_analysis_distilled.csv"
PAPER = Path(
    r"C:\Users\Y2698\Desktop\研究生\毕设\Agentic_Performance_PR_Analysis__EMSE_\pics\results"
)

C_BAR = "#C5C5C5"
C_LINE = "#1F4E3A"
C_UNKNOWN = "#D4D4D4"
C_READ = "#2F6F4E"
C_MEASURE = "#3D5A80"

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
    fig.savefig(PAPER / f"{stem}.png", dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(PAPER / f"{stem}.pdf", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", stem)


def plot_lifespan() -> None:
    df = pd.read_csv(CSV)
    t = df[df["status"].isin(["merged", "closed"])].copy()
    bins = [0, 1, 24, 168, 10**9]
    labels = ["< 1 hour", "1 hour – 1 day", "1–7 days", "> 7 days"]
    t["bin"] = pd.cut(t["lifespan_hours"], bins=bins, labels=labels)
    n = []
    rate = []
    for lab in labels:
        g = t[t["bin"] == lab]
        n.append(int(len(g)))
        rate.append(100.0 * (g["status"] == "merged").mean())

    x = np.arange(len(labels))
    fig, ax1 = plt.subplots(figsize=(6.7, 3.7))
    ax1.bar(x, n, width=0.62, color=C_BAR, zorder=2, label="Terminal PRs")
    ax1.set_ylabel("Number of terminal PRs")
    ax1.set_ylim(0, max(n) * 1.22)
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels)
    ax1.spines["top"].set_visible(False)

    ax2 = ax1.twinx()
    ax2.plot(
        x,
        rate,
        color=C_LINE,
        marker="o",
        markersize=8.5,
        linewidth=2.6,
        zorder=4,
        label="Merge rate",
    )
    ax2.set_ylabel("Merge rate (%)")
    ax2.set_ylim(0, 100)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_color(C_LINE)
    ax2.tick_params(axis="y", colors=C_LINE)
    ax2.yaxis.label.set_color(C_LINE)

    for i, (ni, ri) in enumerate(zip(n, rate)):
        ax1.text(
            i,
            ni * 0.50,
            f"$n$={ni}",
            ha="center",
            va="center",
            fontsize=7.6,
            color="#555555",
        )
        ax2.annotate(
            f"{ri:.1f}%",
            (i, ri),
            textcoords="offset points",
            xytext=(0, 10),
            ha="center",
            fontsize=8.4,
            color=C_LINE,
            fontweight="medium",
        )

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, frameon=False, loc="upper right")
    fig.tight_layout()
    save(fig, "rq2_lifespan")


def plot_detection() -> None:
    df = pd.read_csv(CSV)
    n_all = len(df)
    s = df["detection_method"].fillna("").astype(str)

    def hits(*names: str) -> int:
        def one(row: str) -> bool:
            parts = {p.strip() for p in row.split("|") if p.strip()}
            return any(name in parts for name in names)

        return int(s.apply(one).sum())

    rows = [
        ("Unknown", hits("unknown"), C_UNKNOWN, "#444444"),
        ("Code reading", hits("code_reading"), C_READ, "white"),
        ("CI automation", hits("ci_auto"), C_MEASURE, "white"),
        ("Benchmark / load-test", hits("benchmark", "load_test"), C_MEASURE, "white"),
    ]

    fig, ax = plt.subplots(figsize=(6.4, 2.85))
    y = list(range(len(rows)))[::-1]
    vals = [r[1] for r in rows]
    xmax = max(vals)
    ax.barh(y, vals, color=[r[2] for r in rows], height=0.66, edgecolor="none")
    for yi, (lab, v, _c, tc) in zip(y, rows):
        pct = 100.0 * v / n_all
        label = f"{v:,}  ({pct:.1f}%)"
        if v / xmax > 0.28:
            ax.text(v * 0.98, yi, label, ha="right", va="center", color=tc, fontsize=8.3)
        else:
            ax.text(v + xmax * 0.02, yi, label, ha="left", va="center", color="#222", fontsize=8.3)

    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in rows])
    ax.set_xlabel(f"Number of PRs  (multi-label; corpus n = {n_all:,})")
    ax.set_xlim(0, xmax * 1.12)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    save(fig, "rq2_detection")


if __name__ == "__main__":
    plot_lifespan()
    plot_detection()
