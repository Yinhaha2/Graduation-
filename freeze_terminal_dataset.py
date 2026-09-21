#!/usr/bin/env python3
"""Freeze a terminal-only corpus: drop still-open PRs from finaldatabase/.

GitHub `status==open` (same as `state==open`) is the deletion key. After this
snapshot the study corpus is merged + closed only; merge rate = merged / n.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

import refresh as R

ROOT = Path(__file__).resolve().parent
OUT = R.OUT
PER_PR = OUT / "per_pr"


def open_ids_from_master(master: pd.DataFrame) -> set[int]:
    return set(master.loc[master["status"] == "open", "id"].astype(int))


def open_ids_from_analyses() -> set[int]:
    found: set[int] = set()
    if not PER_PR.exists():
        return found
    for d in PER_PR.iterdir():
        if not d.is_dir():
            continue
        path = d / f"{d.name}_analysis.json"
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if (data.get("meta") or {}).get("status") == "open":
            found.add(int(d.name))
    return found


def filter_classification(remove_ids: set[int]) -> dict[str, int]:
    class_dir = OUT / "classification"
    stats: dict[str, int] = {}
    if not class_dir.exists():
        return stats
    for fpath in sorted(class_dir.glob("*")):
        if fpath.suffix.lower() not in {".parquet", ".csv"}:
            continue
        if fpath.suffix.lower() == ".parquet":
            df = pd.read_parquet(fpath)
        else:
            df = pd.read_csv(fpath)
        before = len(df)
        key = next((c for c in ("pr_id", "id") if c in df.columns), None)
        if key is None:
            continue
        sub = df[~df[key].isin(remove_ids)]
        if fpath.suffix.lower() == ".parquet":
            sub.to_parquet(fpath, index=False)
        else:
            sub.to_csv(fpath, index=False)
        stats[fpath.name] = before - len(sub)
    return stats


def recount_auxiliary() -> dict[str, dict[str, int]]:
    aux_dir = OUT / "auxiliary"
    tables: dict[str, dict[str, int]] = {}
    if not aux_dir.exists():
        return tables
    for fpath in sorted(aux_dir.glob("*.parquet")):
        df = pd.read_parquet(fpath)
        rec: dict[str, int] = {"rows": int(len(df))}
        if "pr_id" in df.columns and not df.empty:
            rec["prs_with_any_row"] = int(df["pr_id"].nunique())
        tables[fpath.name] = rec
    return tables


def prune_status_cache(remove_ids: set[int]) -> int:
    cache = R.load_cache()
    fetched = cache.get("fetched") or {}
    n = 0
    for pid in list(fetched):
        if int(pid) in remove_ids:
            fetched.pop(pid, None)
            n += 1
    cache["fetched"] = fetched
    R.save_cache(cache)
    return n


def prune_json_id_map(path: Path, remove_ids: set[int], *map_keys: str) -> int:
    if not path.exists():
        return 0
    data = json.loads(path.read_text(encoding="utf-8"))
    n = 0
    for key in map_keys:
        bucket = data.get(key)
        if not isinstance(bucket, dict):
            continue
        for pid in list(bucket):
            try:
                as_int = int(pid)
            except (TypeError, ValueError):
                continue
            if as_int in remove_ids:
                bucket.pop(pid, None)
                n += 1
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return n


def write_frozen_outputs(master: pd.DataFrame, report: dict) -> None:
    paper_cols = [c for c in master.columns if c not in R.PAPER_BASE_EXCLUDE]
    paper_df = master[paper_cols].copy()

    pr_master = OUT / "pr_master"
    pr_master.mkdir(parents=True, exist_ok=True)
    master.to_csv(pr_master / "perf_prs_expanded_final.csv", index=False)
    master.to_parquet(pr_master / "perf_prs_expanded_final.parquet", index=False)
    paper_df.to_csv(pr_master / "POP_PULL_Requests_LLM_filtered_final.csv", index=False)

    paper_copy = OUT / "paper_source_copy"
    paper_copy.mkdir(parents=True, exist_ok=True)
    paper_df.to_csv(paper_copy / "POP_PULL_Requests_LLM_filtered_final.csv", index=False)

    status_counts = master["status"].value_counts().to_dict()
    n = len(master)
    n_merged = int(status_counts.get("merged", 0))
    coverage = {
        "pr_count": n,
        "status_counts": status_counts,
        "corpus_definition": "terminal_only",
        "merge_rate": (n_merged / n) if n else None,
        "terminal_freeze": report,
        "auxiliary": {"tables": recount_auxiliary(), "pr_count": n},
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    summary_dir = OUT / "summary"
    summary_dir.mkdir(parents=True, exist_ok=True)
    prior_cov = summary_dir / "coverage_stats.json"
    if prior_cov.exists():
        old = json.loads(prior_cov.read_text(encoding="utf-8"))
        if "status_refresh" in old:
            coverage["prior_status_refresh"] = old["status_refresh"]
    (summary_dir / "coverage_stats.json").write_text(
        json.dumps(coverage, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (summary_dir / "terminal_freeze_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    readme = f"""# finaldatabase

更新于 {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}

## 概要
- **终态语料**（仅 merged / closed，已剔除 open）
- 性能 PR 主表：**{n}** 条
- 状态分布：{status_counts}
- 合并率（merged / n）：**{100 * n_merged / n:.1f}%**（{n_merged}/{n}）
- 本次剔除 open：**{report['removed_n']}** 条

## 目录
- `pr_master/`：终态主表 CSV/Parquet
- `auxiliary/`：PR 聚合附属表（parquet）
- `per_pr/{{pr_id}}/`：每条 PR 的独立 parquet 与分析 JSON
- `summary/terminal_freeze_report.json`：open 剔除明细
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8")


def main() -> None:
    master_path = OUT / "pr_master" / "perf_prs_expanded_final.csv"
    if not master_path.exists():
        raise SystemExit(f"Missing master table: {master_path}")

    master = R.attach_status(pd.read_csv(master_path))
    gh_open = open_ids_from_master(master)
    json_open = open_ids_from_analyses()
    remove_ids = gh_open | json_open
    if not remove_ids:
        print("No open PRs to remove.")
        return

    rows = master[master["id"].isin(remove_ids)][
        ["id", "html_url", "agent", "state", "status"]
    ].to_dict(orient="records")
    for row in rows:
        row["id"] = int(row["id"])

    print(f"Removing {len(remove_ids)} open PR(s). GitHub={len(gh_open)} JSON={len(json_open)}")
    updated = R.remove_prs(master, remove_ids)
    aux_removed = R.filter_auxiliary(remove_ids)
    class_removed = filter_classification(remove_ids)
    per_pr_removed = R.remove_per_pr_dirs(remove_ids)
    cache_pruned = prune_status_cache(remove_ids)
    aux_cache_pruned = prune_json_id_map(
        OUT / "summary" / "github_auxiliary_cache.json",
        remove_ids,
        "fetched",
        "errors",
    )

    leftover_open = int((updated["status"] == "open").sum())
    leftover_json = open_ids_from_analyses()
    report = {
        "frozen_at": datetime.now(timezone.utc).isoformat(),
        "corpus_definition": "terminal_only",
        "removed_n": len(remove_ids),
        "github_open_n": len(gh_open),
        "analysis_json_open_n": len(json_open),
        "ids_only_in_github": sorted(gh_open - json_open),
        "ids_only_in_json": sorted(json_open - gh_open),
        "removed_prs": rows,
        "auxiliary_rows_removed": aux_removed,
        "classification_rows_removed": class_removed,
        "per_pr_dirs_removed": per_pr_removed,
        "github_status_cache_pruned": cache_pruned,
        "github_auxiliary_cache_pruned": aux_cache_pruned,
        "remaining_pr_count": len(updated),
        "remaining_status_counts": updated["status"].value_counts().to_dict(),
        "leftover_open_in_master": leftover_open,
        "leftover_open_in_json": sorted(leftover_json),
    }
    write_frozen_outputs(updated, report)

    print("Done.")
    print(f"  remaining: {len(updated)}")
    print(f"  status:    {report['remaining_status_counts']}")
    print(f"  leftover open master/json: {leftover_open}/{len(leftover_json)}")


if __name__ == "__main__":
    main()
