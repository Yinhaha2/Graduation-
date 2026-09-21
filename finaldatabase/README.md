# finaldatabase

更新于 2026-09-21 02:52 UTC

## 概要
- **终态语料**（仅 merged / closed，已剔除 open）
- 性能 PR 主表：**1183** 条
- 状态分布：{'merged': 672, 'closed': 511}
- 合并率（merged / n）：**56.8%**（672/1183）
- 本次剔除 open：**36** 条

## 目录
- `pr_master/`：终态主表 CSV/Parquet
- `auxiliary/`：PR 聚合附属表（parquet）
- `per_pr/{pr_id}/`：每条 PR 的独立 parquet 与分析 JSON
- `summary/terminal_freeze_report.json`：open 剔除明细
