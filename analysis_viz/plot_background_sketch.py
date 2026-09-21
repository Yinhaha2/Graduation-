#!/usr/bin/env python3
"""Wireframe sketch of the Background diverging-paths figure. Not camera-ready."""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch, Rectangle

PAPER = Path(
    r"C:\Users\Y2698\Desktop\研究生\毕设\Agentic_Performance_PR_Analysis__EMSE_\pics\results"
)

plt.rcParams.update({"font.family": "DejaVu Sans", "pdf.fonttype": 42, "ps.fonttype": 42})


def box(ax, x, y, w, h, fc="#fff", ec="#333", lw=1.1, r=0.08):
    p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.012,rounding_size={r}",
                       facecolor=fc, edgecolor=ec, linewidth=lw)
    ax.add_patch(p)
    return p


def main() -> None:
    fig, ax = plt.subplots(figsize=(12.4, 6.2))
    ax.set_xlim(0, 12.4)
    ax.set_ylim(0, 6.2)
    ax.axis("off")
    fig.patch.set_facecolor("#fafafa")

    ax.text(6.2, 5.95, "SKETCH  ·  redraw in Figma / draw.io / PowerPoint",
            ha="center", va="top", fontsize=11, color="#222")
    ax.text(6.2, 5.68, "Same AI-generated performance PR  →  three review mechanisms  →  three endings",
            ha="center", va="top", fontsize=9, color="#666")

    # start
    box(ax, 0.28, 1.85, 2.35, 2.55, fc="#fff", ec="#333", lw=1.4)
    ax.add_patch(Circle((1.45, 3.85), 0.28, facecolor="#e8eef4", edgecolor="#3D5A80", lw=1.3))
    ax.text(1.45, 3.85, "bot", ha="center", va="center", fontsize=8, color="#3D5A80")
    ax.text(1.45, 3.42, "Agent", ha="center", fontsize=8.5, color="#3D5A80")
    box(ax, 0.52, 2.15, 1.88, 1.05, fc="#f6f6f6", ec="#666", lw=0.9, r=0.05)
    ax.text(1.46, 2.95, "Performance PR", ha="center", fontsize=8.5, fontweight="bold")
    ax.text(1.46, 2.68, "+  speed-up", ha="center", fontsize=8, color="#2F6F4E", family="monospace")
    ax.text(1.46, 2.46, "-  old hot path", ha="center", fontsize=8, color="#A33B32", family="monospace")
    ax.text(1.46, 2.05, "AI-generated\nPerformance PR", ha="center", va="top", fontsize=8, color="#333")

    # fork
    ax.plot([2.63, 3.15, 3.15, 3.55], [3.12, 3.12, 4.55, 4.55], color="#555", lw=1.3)
    ax.plot([3.15, 3.55], [3.12, 3.12], color="#555", lw=1.3)
    ax.plot([3.15, 3.15, 3.55], [3.12, 1.70, 1.70], color="#555", lw=1.3)

    paths = [
        dict(y=3.88, title="PATH 1  ·  Fast merge", title_c="#2F6F4E",
             chip="Codex  ·  AGI-Alpha-Agent-v0 #1377",
             bubble="“Small scope, looks safe.”",
             sub="empty review  ·  no chart  ·  ~7 s",
             bubble_ls="--", out="MERGED", out_fc="#2F6F4E", out_sub="✓  no measurement"),
        dict(y=2.45, title="PATH 2  ·  Evidence gap", title_c="#8C2F28",
             chip="Cursor  ·  vercel/turborepo #10623",
             bubble="“Where is the benchmark?\nReal benchmarking required.”",
             sub="GitHub review frame  ·  stopwatch",
             bubble_ls="-", out="CLOSED", out_fc="#8C2F28", out_sub="✕  missing evidence"),
        dict(y=1.02, title="PATH 3  ·  Design veto", title_c="#8C2F28",
             chip="Claude Code  ·  zenml-io/zenml #3375",
             bubble="“Wrong abstraction.\nUse materializers, not pickle.”",
             sub="GitHub review frame  ·  architecture",
             bubble_ls="-", out="CLOSED", out_fc="#8C2F28", out_sub="✕  design / approach"),
    ]

    for p in paths:
        y = p["y"]
        box(ax, 3.55, y, 5.55, 1.28, fc="#fff", ec="#ddd", lw=1.0)
        ax.text(3.72, y + 1.08, p["title"], fontsize=9.5, fontweight="bold", color=p["title_c"])
        ax.text(3.72, y + 0.86, p["chip"], fontsize=8, color="#666")
        ax.add_patch(Circle((4.05, y + 0.42), 0.18, facecolor="#e8eef4", edgecolor="#3D5A80", lw=1.1))
        ax.text(4.05, y + 0.42, "M", ha="center", va="center", fontsize=8, color="#3D5A80")
        b = FancyBboxPatch((4.38, y + 0.14), 3.15, 0.55, boxstyle="round,pad=0.02,rounding_size=0.08",
                           facecolor="#fff", edgecolor="#aaa", linewidth=1.0, linestyle=p["bubble_ls"])
        ax.add_patch(b)
        ax.text(5.95, y + 0.42, p["bubble"], ha="center", va="center", fontsize=8, color="#222")
        ax.text(5.95, y + 0.08, p["sub"], ha="center", fontsize=7.2, color="#999")
        ax.add_patch(FancyArrowPatch((9.15, y + 0.52), (9.55, y + 0.52),
                                     arrowstyle="-|>", mutation_scale=10, lw=1.2, color=p["out_fc"]))
        box(ax, 9.62, y + 0.22, 1.55, 0.72, fc=p["out_fc"], ec=p["out_fc"], lw=0.5, r=0.08)
        ax.text(10.40, y + 0.68, p["out"], ha="center", va="center", fontsize=10, fontweight="bold", color="white")
        ax.text(10.40, y + 0.42, p["out_sub"], ha="center", va="center", fontsize=7.5, color="#f3f3f3")

    ax.text(6.2, 0.42, "A merge-rate table scores this as 1 / 3.  The threads are not one kind of success and two kinds of “slow code”.",
            ha="center", fontsize=8.5, color="#333")
    ax.text(6.2, 0.18, "M = maintainer.  Path 1 dashed bubble = little or no review.  Do not add corpus percentages to the camera-ready drawing.",
            ha="center", fontsize=7.5, color="#999")

    PAPER.mkdir(parents=True, exist_ok=True)
    png = PAPER / "background_diverging_paths_sketch.png"
    fig.savefig(png, dpi=200, bbox_inches="tight", facecolor="#fafafa")
    plt.close(fig)
    print("wrote", png)


if __name__ == "__main__":
    main()
