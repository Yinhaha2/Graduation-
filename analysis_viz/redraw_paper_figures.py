#!/usr/bin/env python3
"""Copy RQ report figures into the EMSE pics/results folder.

Run after generate_rq_analysis.py so analysis_viz/rq_analysis_figures/ is current.
"""
from __future__ import annotations

import shutil
from pathlib import Path

SHADOW = Path(__file__).resolve().parent.parent
PAPER_RESULTS = Path(
    r"C:\Users\Y2698\Desktop\研究生\毕设\Agentic_Performance_PR_Analysis__EMSE_\pics\results"
)
FIG_DIR = SHADOW / "analysis_viz" / "rq_analysis_figures"
FIG_NAMES = (
    "rq1_status.png",
    "rq1_agent_merge.png",
    "rq1_closed_motivation.png",
    "rq2_lifespan.png",
    "rq4_boundary.png",
)


def main() -> None:
    PAPER_RESULTS.mkdir(parents=True, exist_ok=True)
    for name in FIG_NAMES:
        src = FIG_DIR / name
        if not src.exists():
            raise SystemExit(f"Missing figure: {src}")
        dst = PAPER_RESULTS / name
        shutil.copy2(src, dst)
        print(f"copied {src} -> {dst}")


if __name__ == "__main__":
    main()
