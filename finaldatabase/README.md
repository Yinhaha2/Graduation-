# finaldatabase

更新于 2026-09-21

## 概要
- **终态语料**（仅 merged / closed，已剔除 open）
- 性能 PR 主表：**1183** 条
- 状态分布：{'merged': 694, 'closed': 489}
- 合并率（merged / n）：**58.7%**（694/1183）
- 本次剔除 open：**36** 条

状态拆分以主表 / `summary/coverage_stats.json` 顶层 `status_counts` 为准。`terminal_freeze_report.json` 只记录剔除了哪些 open PR。

## 目录
- `pr_master/`：终态主表 CSV/Parquet
- `auxiliary/`：PR 聚合附属表（parquet）
- `per_pr/{pr_id}/`：每条 PR 的独立 parquet 与分析 JSON
- `summary/coverage_stats.json`：当前语料总览
- `summary/terminal_freeze_report.json`：open 剔除明细
