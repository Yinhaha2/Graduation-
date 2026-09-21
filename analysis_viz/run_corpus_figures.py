#!/usr/bin/env python3
"""Execute perf_pr_visualization.ipynb plotting cells without Jupyter."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")


def main() -> None:
    here = Path(__file__).resolve().parent
    nb_path = here / "perf_pr_visualization.ipynb"
    nb = json.loads(nb_path.read_text(encoding="utf-8"))
    chunks: list[str] = []
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        src = "".join(cell.get("source") or [])
        src = src.replace("%matplotlib inline", "")
        src = src.replace("plt.show()", "")
        chunks.append(src)
    code = "\n\n".join(chunks)
    ns: dict = {}
    exec(compile(code, str(nb_path), "exec"), ns, ns)
    print("Wrote figures under", ns.get("FIG_DIR"))


if __name__ == "__main__":
    main()
