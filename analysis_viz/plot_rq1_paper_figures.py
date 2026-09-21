#!/usr/bin/env python3
"""RQ1 paper figures: Sankey, agent stacked bars, optimization-layer bars.

Numbers are computed from the frozen terminal corpus
(最终数据集: merged / closed only; no open).
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
from matplotlib.path import Path as MPath
from matplotlib.ticker import NullLocator
import pandas as pd
import json

SHADOW = Path(__file__).resolve().parent.parent
CSV = SHADOW / "full_analysis_distilled.csv"
METRICS = SHADOW / "analysis_viz" / "rq_analysis_metrics.json"
PAPER = Path(
    r"C:\Users\Y2698\Desktop\研究生\毕设\Agentic_Performance_PR_Analysis__EMSE_\pics\results"
)

# Colorblind-safer academic palette
C_ALL = "#3D5A80"
C_MERGED = "#2F6F4E"
C_CLOSED = "#A33B32"
C_OPEN = "#B7B7B7"
C_FAST = "#1F4E3A"
C_REVIEW = "#6FAF86"
C_MERGED_OTHER = "#C5D9CC"
C_SILENT = "#5C5C5C"
C_REJECT = "#8C2F28"
C_PROCESS = "#D4A574"
C_UNCLEAR = "#C8C8C8"

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
    png = PAPER / f"{stem}.png"
    pdf = PAPER / f"{stem}.pdf"
    fig.savefig(png, dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(pdf, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", png.name, "and", pdf.name)


def flow(ax, x0, x1, y0_top, y0_bot, y1_top, y1_bot, color, alpha=0.42, lw=0.0):
    cx = (x0 + x1) / 2.0
    verts = [
        (x0, y0_top),
        (cx, y0_top),
        (cx, y1_top),
        (x1, y1_top),
        (x1, y1_bot),
        (cx, y1_bot),
        (cx, y0_bot),
        (x0, y0_bot),
        (x0, y0_top),
    ]
    codes = [
        MPath.MOVETO,
        MPath.CURVE4,
        MPath.CURVE4,
        MPath.CURVE4,
        MPath.LINETO,
        MPath.CURVE4,
        MPath.CURVE4,
        MPath.CURVE4,
        MPath.CLOSEPOLY,
    ]
    patch = PathPatch(
        MPath(verts, codes),
        facecolor=color,
        edgecolor="none",
        alpha=alpha,
        lw=lw,
        zorder=1,
    )
    ax.add_patch(patch)


def rect(ax, x, y_bot, width, height, color):
    ax.add_patch(
        plt.Rectangle(
            (x, y_bot),
            width,
            height,
            facecolor=color,
            edgecolor="white",
            linewidth=0.6,
            zorder=3,
        )
    )


def load_metrics() -> dict:
    if not METRICS.exists():
        raise SystemExit(f"Missing {METRICS}; run python generate_rq_analysis.py first.")
    return json.loads(METRICS.read_text(encoding="utf-8"))


def plot_sankey() -> None:
    m = load_metrics()
    n_term = int(m["n"])
    n_merged = int(m["merged"])
    n_closed = int(m["closed"])
    path = m["merged_path"]
    mot = m["close_motivation"]
    fast = int(path.get("fast_low_friction", 0))
    review = int(path.get("reviewed_iteration", 0))
    other_m = int(path.get("no_formal_review", 0)) + int(path.get("other", 0))
    silent = int(mot.get("silent_abandonment", 0))
    reject = int(mot.get("real_rejection", 0))
    other_c = int(mot.get("other_process", 0))
    unclear = int(mot.get("unclear", 0))
    if fast + review + other_m != n_merged:
        other_m = n_merged - fast - review
    if silent + reject + other_c + unclear != n_closed:
        unclear = n_closed - silent - reject - other_c

    gap3 = 22
    s3_vals = [fast, review, other_m, silent, reject, other_c, unclear]
    s3_gaps = [gap3, gap3, 40, gap3, gap3, gap3, 0]

    y = sum(s3_vals) + sum(s3_gaps[:-1])
    s3 = []
    for v, g in zip(s3_vals, s3_gaps):
        top = y
        bot = y - v
        s3.append((bot, top))
        y = bot - g

    def centered(span_bot, span_top, height):
        mid = (span_bot + span_top) / 2.0
        return mid - height / 2.0, mid + height / 2.0

    m_bot, m_top = centered(s3[2][0], s3[0][1], n_merged)
    c_bot, c_top = centered(s3[6][0], s3[3][1], n_closed)
    l_bot, l_top = centered(c_bot, m_top, n_term)

    fig, ax = plt.subplots(figsize=(10.6, 5.8))
    x0, x1, x2 = 0.0, 280.0, 590.0
    w = 150.0

    flow(ax, x0 + w, x1, l_top, l_top - n_merged, m_top, m_bot, C_MERGED, 0.40)
    flow(ax, x0 + w, x1, l_top - n_merged, l_bot, c_top, c_bot, C_CLOSED, 0.40)

    m_cursor = m_top
    for (bot, top), col, val in zip(
        s3[:3], [C_FAST, C_REVIEW, C_MERGED_OTHER], [fast, review, other_m]
    ):
        flow(ax, x1 + w, x2, m_cursor, m_cursor - val, top, bot, col, 0.55)
        m_cursor -= val

    c_cursor = c_top
    for (bot, top), col, val in zip(
        s3[3:], [C_SILENT, C_REJECT, C_PROCESS, C_UNCLEAR], [silent, reject, other_c, unclear]
    ):
        flow(ax, x1 + w, x2, c_cursor, c_cursor - val, top, bot, col, 0.50)
        c_cursor -= val

    rect(ax, x0, l_bot, w, n_term, C_ALL)
    ax.text(x0 + w / 2, (l_bot + l_top) / 2 + 16, "Terminal PRs", ha="center", va="center", color="white", fontsize=9.2, zorder=4)
    ax.text(x0 + w / 2, (l_bot + l_top) / 2 - 16, f"n = {n_term:,}", ha="center", va="center", color="white", fontsize=8.2, zorder=4)

    rect(ax, x1, m_bot, w, n_merged, C_MERGED)
    ax.text(x1 + w / 2, (m_bot + m_top) / 2 + 16, "Merged", ha="center", va="center", color="white", fontsize=9.2, zorder=4)
    ax.text(x1 + w / 2, (m_bot + m_top) / 2 - 16, f"{n_merged}  ({100*n_merged/n_term:.1f}%)", ha="center", va="center", color="white", fontsize=8.2, zorder=4)

    rect(ax, x1, c_bot, w, n_closed, C_CLOSED)
    ax.text(x1 + w / 2, (c_bot + c_top) / 2 + 16, "Closed", ha="center", va="center", color="white", fontsize=9.2, zorder=4)
    ax.text(x1 + w / 2, (c_bot + c_top) / 2 - 16, f"{n_closed}  ({100*n_closed/n_term:.1f}%)", ha="center", va="center", color="white", fontsize=8.2, zorder=4)

    s3_spec = [
        (C_FAST, "Low-friction fast merge", f"{fast} ({100*fast/n_merged:.1f}%)"),
        (C_REVIEW, "Review iteration", f"{review} ({100*review/n_merged:.1f}%)"),
        (C_MERGED_OTHER, "Other merge", f"{other_m} ({100*other_m/n_merged:.1f}%)"),
        (C_SILENT, "Silent abandonment", f"{silent} ({100*silent/n_closed:.1f}%)"),
        (C_REJECT, "Real rejection", f"{reject} ({100*reject/n_closed:.1f}%)"),
        (C_PROCESS, "Other process", f"{other_c} ({100*other_c/n_closed:.1f}%)"),
        (C_UNCLEAR, "Unclear", f"{unclear} ({100*unclear/n_closed:.1f}%)"),
    ]
    for (bot, top), (col, lab, sub) in zip(s3, s3_spec):
        h = top - bot
        rect(ax, x2, bot, w, h, col)
        ax.text(
            x2 + w + 12,
            bot + h / 2,
            f"{lab}   {sub}",
            ha="left",
            va="center",
            color="#222",
            fontsize=8.2,
            zorder=4,
        )

    ax.set_xlim(-20, 1120)
    ax.set_ylim(s3[-1][0] - 30, s3[0][1] + 30)
    ax.axis("off")
    ax.set_title("Outcome paths of agent-authored performance PRs", fontsize=11, pad=6, color="#222")
    save(fig, "rq1_sankey")


def plot_agent_stacked() -> None:
    m = load_metrics()
    n_all = int(m["n"])
    n_merged = int(m["merged"])
    order = ["OpenAI_Codex", "Claude_Code", "Cursor", "Copilot", "Devin"]
    labels_map = {
        "OpenAI_Codex": "OpenAI Codex",
        "Claude_Code": "Claude Code",
        "Cursor": "Cursor",
        "Copilot": "Copilot",
        "Devin": "Devin",
    }
    rows = []
    for key in order:
        rec = (m.get("agent") or {}).get(key) or {}
        if not rec:
            continue
        rows.append((labels_map.get(key, key), int(rec["merged"]), int(rec["closed"])))
    labels = [r[0] for r in rows]
    merged = [r[1] for r in rows]
    closed = [r[2] for r in rows]
    n = [a + b for a, b in zip(merged, closed)]
    m_pct = [a / tot for a, tot in zip(merged, n)]
    c_pct = [b / tot for b, tot in zip(closed, n)]

    fig, ax = plt.subplots(figsize=(6.6, 3.55))
    y = list(range(len(rows)))[::-1]
    ax.barh(y, m_pct, color=C_MERGED, height=0.62, label="Merged")
    ax.barh(y, c_pct, left=m_pct, color="#D0D0D0", height=0.62, label="Closed", edgecolor="none")

    for yi, mp, tot, m_n, c_n in zip(y, m_pct, n, merged, closed):
        ax.text(1.015, yi, f"$n$={tot:,}", ha="left", va="center", fontsize=8.4, color="#333")
        if mp >= 0.18:
            ax.text(
                mp / 2,
                yi,
                f"{mp*100:.1f}%",
                ha="center",
                va="center",
                color="white",
                fontsize=8.2,
                fontweight="medium",
            )
        else:
            ax.text(
                mp + 0.02,
                yi,
                f"{mp*100:.1f}%",
                ha="left",
                va="center",
                color="#333",
                fontsize=8.2,
            )

    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlim(0, 1.22)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"])
    ax.axvline(n_merged / n_all, color="#8A8A8A", lw=0.8, ls="--", zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.42, 1.16), ncol=2, fontsize=8.5)
    ax.set_xlabel("Share of terminal PRs")
    fig.tight_layout()
    save(fig, "rq1_agent_stacked")


def plot_layer() -> None:
    df = pd.read_csv(CSV)
    n_all = len(df)
    counts = df["optimization_layer"].fillna("unknown").value_counts()
    keep = [
        ("application_service", "Application service"),
        ("build", "Build"),
        ("frontend_ui", "Frontend UI"),
        ("runtime_library", "Runtime library"),
        ("application_control_flow", "Application control flow"),
        ("compiler", "Compiler"),
        ("infrastructure", "Infrastructure"),
        ("runtime_vm", "Runtime VM"),
        ("compiler_backend", "Compiler backend"),
    ]
    vals = [int(counts.get(k, 0)) for k, _ in keep]
    labs = [lab for _, lab in keep]

    fig, ax = plt.subplots(figsize=(6.4, 3.95))
    y = list(range(len(labs)))[::-1]
    ax.barh(y, vals, color="#4C78A8", height=0.68)
    xmax = max(vals)
    for yi, v in zip(y, vals):
        ax.text(
            v + xmax * 0.02,
            yi,
            f"{v:,}  ({100 * v / n_all:.1f}%)",
            ha="left",
            va="center",
            fontsize=8.3,
            color="#222",
        )
    ax.set_yticks(y)
    ax.set_yticklabels(labs)
    ax.set_xlim(0, xmax * 1.42)
    ax.set_xlabel("Number of PRs")
    ax.set_xticks([0, 50, 100, 150, 200])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    save(fig, "rq1_layer")


if __name__ == "__main__":
    plot_sankey()
    plot_agent_stacked()
    plot_layer()
