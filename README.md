# 影子仓（Graduation PR Dataset）

本仓库是毕业设计用的 **AI Agent 性能 Pull Request** 数据集与研究工作流：在 `finaldatabase/` 中维护结构化 PR 数据，并通过脚本对 GitHub 状态做增量刷新、对单条 PR 调用 LLM 生成结构化分析 JSON。

当前主表规模：**1219** 条 PR（`merged` 669 / `closed` 511 / `open` 39）。更细的统计见 [`finaldatabase/summary/coverage_stats.json`](finaldatabase/summary/coverage_stats.json) 与 [`finaldatabase/README.md`](finaldatabase/README.md)。

## 目录结构

```
.
├── finaldatabase/          # 核心数据集（主表、附属表、按 PR 拆分文件、汇总报告）
├── refresh.py              # 向 GitHub 复核 open PR 状态，移除 404，写回主表
├── run_pr_analysis.py      # 组装 prompt，调用 DeepSeek，输出 {pr_id}_analysis.json
├── prompt.md               # LLM 系统提示词（固定指令块）
├── schema.json             # 分析结果 JSON 字段说明 / 输出模板
└── README.md
```

### `finaldatabase/` 要点

| 路径 | 说明 |
|------|------|
| `pr_master/` | 主表 CSV/Parquet（`perf_prs_expanded_final.*`）及论文用筛选表 |
| `auxiliary/` | 按 PR 聚合的 commits、reviews、comments、timeline 等 parquet |
| `per_pr/{pr_id}/` | 单条 PR 的附属 parquet；分析结果 `{pr_id}_analysis.json` 等 |
| `summary/` | 覆盖率、`status_refresh_report.json`、GitHub 状态缓存等 |

## 环境依赖

- Python 3.10+
- 主要第三方库：`pandas`、`numpy`、`requests`、`pyarrow`（读写 parquet）

```bash
pip install pandas numpy requests pyarrow
```

## 本地密钥（勿提交 Git）

| 文件 / 变量 | 用途 |
|-------------|------|
| `.github_token` 或 `GITHUB_TOKEN` | `refresh.py` 访问 GitHub API |
| `.deepseekToken` 或 `DEEPSEEK_API_KEY` | `run_pr_analysis.py` 调用 DeepSeek |

以上文件已列入 `.gitignore`，请只在本地保存。

## 常用命令

### 刷新 PR 状态（open → merged/closed，删除 404）

```bash
python refresh.py
```

行为概要：

1. 重扫主表中所有 `state == open` 的 PR；
2. 将 GitHub 上已删除（404）的 PR 从主表、`auxiliary/`、`per_pr/` 中移除；
3. 对有状态变更的 PR 更新 `state`、`merged_at`、`closed_at` 等；
4. 更新 `finaldatabase/summary/status_refresh_report.json` 与主表导出文件。

### LLM 单条 / 批量分析

```bash
# 单条 PR
python run_pr_analysis.py --pr-id 3228424652

# 批量 N 条（跳过已有输出与 few-shot 样例）
python run_pr_analysis.py --batch 10

# 指定 ID 列表
python run_pr_analysis.py --pr-ids 3228424652,3074351366

# 仅生成 prompt，不调用 API
python run_pr_analysis.py --pr-id 3228424652 --dry-run
```

输出默认写入对应 `finaldatabase/per_pr/{pr_id}/` 目录（如 `{pr_id}_analysis.json`）。字段含义见 `schema.json`，提示词见 `prompt.md`。

## 数据与安全说明

- 部分 PR 的 commit `patch` 中曾出现第三方仓库误提交的密钥字符串；推送前已对 parquet 中 `AKIA*` 等模式做脱敏占位，**请勿**将含真实密钥的原始 patch 再次提交到公开仓库。
- 若需复现论文表，优先使用 `pr_master/POP_PULL_Requests_LLM_filtered_final.csv`（相对完整主表去掉部分研究用扩展列）。

## 相关仓库

远程：`github.com:Yinhaha2/Graduation-.git`（分支 `master`）。
