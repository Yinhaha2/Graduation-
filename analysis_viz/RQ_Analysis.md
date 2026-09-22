# RQ 分析报告

> **最终数据集**：1183 PR，694 merged，489 closed。合并率 **58.7%**（694/1183）。全库统一口径：仅终态 merged / closed，不含 open。
> 数字由 `python generate_rq_analysis.py` 从 `finaldatabase/per_pr/{id}/{id}_analysis.json` 聚合生成。结论均为**描述性关联**，不是因果推断。`outcome_reason` 等为 LLM 分析标签，不是 GitHub 官方关闭原因。

## 数据与方法

- **语料**：与 `FullAnalysis.md` 同一批分析 JSON，宽表字段复用 `generate_full_analysis.flatten_record`。
- **状态口径**：`merged` = 已合入；`closed` = 终态未合入 / 被拒。仍开放的 PR 已从数据集剔除，不进入任何分母。
- **合并率**：merged / n，n 即最终数据集条数。
- **图**：`rq_analysis_figures/`。配套机器可读摘要：`rq_analysis_metrics.json`。

---

## RQ1 PR 分布：总体分布、Agent 差异、未合并是否等于被拒

### RQ1.1 总体分布与不同 Agent 的合并率表现如何

| 状态 | 操作定义 | 数量 | 占 n |
|---|---|---|---|
| merged | 已合入（`merged_at` 非空） | 694 | 58.7% |
| closed（被拒） | 终态未合入 | 489 | 41.3% |

- **合并率**（merged / n=1183）：**58.7%**；被拒率：**41.3%**。
- 下文对照均在该终态语料上计算。

![status](rq_analysis_figures/rq1_status.png)

**按 Agent**：合并率 = merged / 该 Agent 的终态 PR 数。

| Agent | PR 数 | merged | closed（被拒） | 合并率 |
|---|---|---|---|---|
| OpenAI_Codex | 629 | 460 | 169 | 73.1% |
| Devin | 225 | 74 | 151 | 32.9% |
| Copilot | 206 | 89 | 117 | 43.2% |
| Cursor | 89 | 49 | 40 | 55.1% |
| Claude_Code | 34 | 22 | 12 | 64.7% |

![agent merge](rq_analysis_figures/rq1_agent_merge.png)

n≥30 的断层仍然清楚：OpenAI_Codex 合并率最高，Devin / Copilot 明显更低。这是**表现差异**，可能混有任务类型、仓库、补丁规模等影响因素，不能直接写成模型能力证明。

**性能优化层面 Top 12**：

| optimization_layer | 数量 | 占 n |
|---|---|---|
| `application_service` | 193 | 16.3% |
| `build` | 163 | 13.8% |
| `frontend_ui` | 135 | 11.4% |
| `runtime_library` | 117 | 9.9% |
| `application_control_flow` | 83 | 7.0% |
| `compiler` | 45 | 3.8% |
| `infrastructure` | 33 | 2.8% |
| `runtime_vm` | 29 | 2.5% |
| `compiler_backend` | 26 | 2.2% |
| `compiler_optimization` | 15 | 1.3% |
| `compiler_codegen` | 14 | 1.2% |
| `test_infrastructure` | 12 | 1.0% |

上表是频次 Top 12（合计 865），其余层面 318 条未列，不是 1183 条的穷尽表。

**RQ1.1 小结**：终态语料里合入占 58.7%、被拒（closed）占 41.3%。不同 Agent 的合入机会差一倍以上；改动主要落在应用服务、构建和前端。

### RQ1.2 Merged 的真实情况如何划分

合入不是单一路径。按**行为规则**划分（优先「经审查迭代」，其次「极速低摩擦」，再次「无 formal review」）。这套 `merged_path` 与 `FullAnalysis.md` §2 的 `outcome_reason` 粗分组不是同一张表，不能把 small_scope 计数和快合并计数加在一起或互相替代。

| Merged 路径 | 数量 | 占 merged |
|---|---|---|
| 低摩擦快合并 | 507 | 73.1% |
| 经 review 迭代后合入 | 155 | 22.3% |
| 无 formal review 合入（非极速） | 32 | 4.6% |

上表合计 694/694。规则见附录 A，不要和 FullAnalysis §2 的 small_scope 分组混用。

配套行为事实：

| 指标 | merged |
|---|---|
| 存活时间中位数 | 0.122 小时（约 7 分钟） |
| fast_merge=true | 528（76.1%） |
| 评论数为 0 | 398（57.3%） |
| review_count=0 | 460（66.3%） |
| 无关联 Issue | 595（85.7%） |

另：全库无关联 Issue **980/1183**（82.8%）。上表该行分母是 merged（595/694），不是全库。

**低摩擦快合并示例：**

- [3165644329](https://github.com/ryokun6/ryos/pull/144) `Cursor` — Investigate ai prompt caching issue  
  `outcome_reason=merged_small_scope_low_risk`
- [3169508590](https://github.com/MontrealAI/AGI-Alpha-Agent-v0/pull/2526) `OpenAI_Codex` — [alpha_factory] enhance meta refinement  
  `outcome_reason=merged_fast_self_verify`
- [3114659416](https://github.com/MontrealAI/AGI-Alpha-Agent-v0/pull/1500) `OpenAI_Codex` — [alpha_factory] inline wasm assets  
  `outcome_reason=merged_small_scope_self_merge`

**经 review 迭代后合入示例：**

- [3135316626](https://github.com/microsoft/vs-mef/pull/594) `Copilot` — Fix static member exports to not instantiate declaring type  
  `outcome_reason=merged_after_review_fix`
- [3201567268](https://github.com/micropython/micropython/pull/17613) `Claude_Code` — stm32/eth: Improve Ethernet driver with link detection and static IP support.  
  `outcome_reason=merged_after_review_fix`
- [3083186670](https://github.com/dotnet/fsharp/pull/18592) `Copilot` — Auto-generate ILLink.Substitutions.xml to Remove F# Metadata Resources  
  `outcome_reason=merged_after_review_fix`

**小结**：Merged 的主流是短命、小范围、常常没有 formal review 的低摩擦合入；经审查来回修改再合入的是少数路径。把「合入」理解成「高质量审查通过」会严重高估审查深度。

### RQ1.3 Closed 的真实情况如何划分

**口径**：`closed` = 终态未合入 / 被拒（n=489，占语料 41.3%）。

Closed=被拒 是状态层定义，不是「维护者写了拒绝意见」。被拒内部还要按机制再拆，否则会把沉默遗弃和技术否决混成一类。

| Closed 内部类型（均属被拒） | 操作定义 | 数量 | 占 closed | 占 n |
|---|---|---|---|---|
| 真正拒绝 real rejection | 有否决信号：blocking / CHANGES_REQUESTED / 技术或设计类标签 | 154 | 31.5% | 13.0% |
| 沉默遗弃 silent abandonment | 关闭但无明确技术/设计否决：stale、无审查、作者放弃、自动过期 | 273 | 55.8% | 23.1% |
| 其他流程 other_process | 被替代 PR、误提交撤回、重复提交等（仍未合入） | 26 | 5.3% | 2.2% |
| 原因不明 unclear | 现有文本不足以归入以上三类（仍未合入） | 36 | 7.4% | 3.0% |
| **closed 合计（被拒）** | 终态未合入 | 489 | 100% | 41.3% |

![closed motivation](rq_analysis_figures/rq1_closed_motivation.png)

在 **489** 条被拒 PR 里，沉默遗弃约占 **55.8%**，真正拒绝约占 **31.5%**。也就是说：状态层全部算被拒；机制层里更多是没人跟、被放下，而不是审完后的技术否决。

沉默遗弃再拆（分母 = silent abandonment）：

| 遗弃子类 | 数量 | 占沉默遗弃 | 占 closed（被拒） |
|---|---|---|---|
| 作者自行关闭 / 放弃 | 100 | 36.6% | 20.4% |
| 无审查互动后被关 | 77 | 28.2% | 15.7% |
| 长期不活跃后关闭 | 58 | 21.2% | 11.9% |
| bot / 自动过期关闭 | 38 | 13.9% | 7.8% |

Closed 中 `blocking=true` 仅 81 条；「真正被审过或有否决信号」的子集 182 条（37.2% of closed）。其余多数被拒发生在几乎没有审查文本的情况下——这是遗弃，不是书面 reject，但终态仍是未合入。

**真正拒绝示例：**

- [2876006908](https://github.com/zenml-io/zenml/pull/3375) `Claude_Code` — Improve list and collection materializers performance  
  `outcome_reason=rejected_design_approach`；拒因摘要：Maintainer CHANGES_REQUESTED with inline comment stating the code is not using ZenML materializers and instead uses pickle for everything, requiring a major rework.
- [3096300821](https://github.com/dlt-hub/dlt/pull/2691) `OpenAI_Codex` — Update docs watcher to process changed files only  
  `outcome_reason=functional_regression_reintroduced_bug`；拒因摘要：Maintainer zilto CHANGES_REQUESTED due to reproduced ENOSPC error; author sh-rp subsequently closed the PR with comment 'closed in favor of branch'.
- [3194284966](https://github.com/vercel/turborepo/pull/10623) `Cursor` — perf: improve hashing performance for manual path  
  `outcome_reason=missing_benchmark`；拒因摘要：Maintainer anthonyshew closed the PR agreeing that real benchmarking is required before accepting the change.

**沉默遗弃示例：**

- [3075349977](https://github.com/unibeck/solstatus/pull/55) `Copilot` — Decrease OpenNext Bundle Size to Below 3MB  
  `outcome_reason=closed_no_explanation`；拒因摘要：Maintainer closed the PR without review or comment; only Copilot work-started/finished events and a review request with no response.
- [3146327522](https://github.com/microsoft/onnxruntime/pull/25061) `Copilot` — [WIP] Improve DFT implementation  
  `outcome_reason=abandoned_agent_failure`；拒因摘要：Agent workflow failure; PR marked [WIP] and closed without any review or merge.
- [3240409748](https://github.com/mochilang/mochi/pull/9390) `OpenAI_Codex` — Improve Zig backend constant folding  
  `outcome_reason=author_self_close`；拒因摘要：No review rejection; author self-closed.

**小结**：研究对照里 closed 就是被拒。被拒再分成真正拒绝、沉默遗弃、其他流程、原因不明四类；主导机制是沉默遗弃，真正技术/设计否决大约占被拒的三分之一。

---

## RQ2 成功路径与评审注意力：为何能极短周期低审查合入？为何不审？

本节在终态语料上对照 merged vs closed。

### RQ2.1 合并成功的 PR 呈现出哪些行为与特征？

| 存活时间 | PR 数 | 合并率 |
|---|---|---|
| <1h | 568 | 77.3% |
| 1–24h | 232 | 58.2% |
| 1–7d | 165 | 43.6% |
| >7d | 218 | 22.0% |

![lifespan](rq_analysis_figures/rq2_lifespan.png)

上图是各档**合并率**（不是条数），且只含有 lifespan 的 1183 条；缺失 0 条见上表，不在图中。

| changes 分箱 | PR 数 | 合并率 |
|---|---|---|
| ≤100 | 490 | 63.1% |
| 101–500 | 349 | 53.0% |
| 501–2k | 197 | 55.8% |
| 2k–10k | 98 | 61.2% |
| >10k | 49 | 61.2% |

分箱含 `changes=0`（计入 ≤100）：13 条，全部 closed。上表各档合计 1183/1183。

| 特征 | merged | closed |
|---|---|---|
| 存活时间中位数 | 0.122 h | 37.6 h |
| changes 中位数 | 143 | 170 |
| 评论数中位数 | 0 | 2 |
| 无 formal review | 66.3% | 77.1% |

成功侧常见 `perf_focus`：
`constant_folding`(24), `compiler_optimization`(21), `benchmark_infrastructure`(11), `cache`(8), `lazy_loading`(7), `compile_time_optimization`(7), `build_performance`(6), `caching`(6)

**小结**：能合入的性能 PR 显著更短命、略更小、互动更少。主流成功画像是「小补丁很快合」，不是「材料齐全、审完再合」。

### RQ2.2 维护者凭何放行？无人审更像质量门槛，还是注意力 / 流程错配？

维护者**可观测**的排查方式（`detection_method`，可多选；一行是 PR 命中，行合计可以超过 n）：

| detection_method | 全库 | merged | closed |
|---|---|---|---|
| `unknown` | 766（64.8%） | 436 | 330 |
| `code_reading` | 363（30.7%） | 237 | 126 |
| `ci_auto` | 92（7.8%） | 52 | 40 |
| `manual_testing` | 16（1.4%） | 8 | 8 |
| `manual_test` | 8（0.7%） | 7 | 1 |
| `benchmark` | 6（0.5%） | 4 | 2 |
| `load_test` | 4（0.3%） | 2 | 2 |
| `(empty)` | 4（0.3%） | 2 | 2 |
| `profiler` | 3（0.3%） | 0 | 3 |
| `unit_test` | 3（0.3%） | 3 | 0 |

边界标签在终态上的合并率：

| boundary_tag | n | 合并率 |
|---|---|---|
| `technical_stack` | 588 | 80.4% |
| `process` | 562 | 38.1% |
| `evidence_required` | 32 | 21.9% |
| `unknown` | 1 | 0.0% |

| 材料信号 | merged | closed |
|---|---|---|
| body_has_repro_steps | 4.0% | 5.1% |
| body_has_benchmark_table | 2.6% | 6.1% |
| body_has_numeric_perf_claim | 13.3% | 25.2% |
| reproducibility=sufficient | 2.3% | 1.6% |

全库材料评级：

| reproducibility | 数量 | 占全库 |
|---|---|---|
| `insufficient` | 730 | 61.7% |
| `partial` | 235 | 19.9% |
| `unknown` | 194 | 16.4% |
| `sufficient` | 24 | 2.0% |

**放行依据**：可观测时以静态读码为主，CI 自动化是少数，profiler / load_test / benchmark 几乎看不见。`technical_stack` 合并率 80.4%，小补丁更容易过。成功 PR 并不更常带 benchmark 表——材料不是这条快路径的通行证。

**为何不审**：无人审既可以合入也可以关闭。merged 中 66.3%、closed 中 77.1% 无 formal review。`process` 边界合并率只有 38.1%；82.8% 的 PR 没有关联 Issue，优化常是 Agent 主动发起，不在维护者既有队列里。存活超过 7 天的合并率掉到约 17%。这些更像评审注意力和流程错配，而不是「质量门槛把差 PR 拦下来」。

**小结**：维护者放行主要靠「改动小、读得懂、没把 CI 搞红」；大量 PR 无人审，成功与失败都发生在低注意力环境中。把这些 PR 留在未合入状态的，经常不是审查标准本身，而是有没有人愿意看。

---

## RQ3 失败模式与能力边界：真正被审 / 被拒的 PR 卡在哪里？

### RQ3.1 在真正被审过或被否决的子集中，核心失败类型是什么？

本问**不使用全部 489 条 closed**，只保留有 formal review、`blocking`、`CHANGES_REQUESTED`，或 `review_comment_bucket` 不是 `no_review_text` 的子集：**182** 条（37.2% of closed）。

全量 closed 的 review 分桶（对照用，含无文本）：

| review_comment_bucket | 数量 | 占 closed |
|---|---|---|
| `no_review_text` | 321 | 65.6% |
| `correctness_or_bug` | 62 | 12.7% |
| `design_or_approach` | 57 | 11.7% |
| `performance_related_concern` | 10 | 2.0% |
| `tests_missing_or_requested` | 9 | 1.8% |
| `ci_failure` | 2 | 0.4% |
| `scope` | 2 | 0.4% |
| `performance_regression` | 2 | 0.4% |
| 其余长尾标签 | 24 | 4.9% |

上表合计 489/489（含长尾）。

被审 / 被否决子集的失败类型：

| 失败类型 | 数量 | 占被审 closed 子集 |
|---|---|---|
| 功能 / 正确性失败 | 81 | 44.5% |
| 设计 / 方案否决 | 47 | 25.8% |
| 其他 / 混合 | 20 | 11.0% |
| 证据 / benchmark 不足 | 14 | 7.7% |
| CI / 测试失败 | 9 | 4.9% |
| 静默或缺乏说明 | 8 | 4.4% |
| 范围过大或越界 | 3 | 1.6% |

上表合计 182/182。

**功能 / 正确性示例：**

- [3096300821](https://github.com/dlt-hub/dlt/pull/2691) `OpenAI_Codex` — Update docs watcher to process changed files only  
  `outcome_reason=functional_regression_reintroduced_bug`；拒因摘要：Maintainer zilto CHANGES_REQUESTED due to reproduced ENOSPC error; author sh-rp subsequently closed the PR with comment 'closed in favor of branch'.
- [3198922993](https://github.com/dotnet/msbuild/pull/12109) `Copilot` — Detect and log dev drive at the start of build  
  `outcome_reason=functional_issues_unresolved`；拒因摘要：Maintainer CHANGES_REQUESTED due to incorrect volume path handling; no follow-up fix; PR closed without merge.
- [3176436231](https://github.com/dotnet/maui/pull/30215) `Copilot` — Fix XAML binding warnings in DeviceTests.Runners by adding x:DataType attributes  
  `outcome_reason=incorrect_csharp_changes_closed`；拒因摘要：Maintainer closed PR after noting AI could not do the fix correctly without human input.

**设计 / 方案否决示例：**

- [2876006908](https://github.com/zenml-io/zenml/pull/3375) `Claude_Code` — Improve list and collection materializers performance  
  `outcome_reason=rejected_design_approach`；拒因摘要：Maintainer CHANGES_REQUESTED with inline comment stating the code is not using ZenML materializers and instead uses pickle for everything, requiring a major rework.
- [3241523087](https://github.com/doodlum/skyrim-community-shaders/pull/1281) `Copilot` — perf: cache GetRuntimeData usage for improved performance  
  `outcome_reason=closed_minimal_perf_gain_no_evidence`；拒因摘要：PR closed after maintainer questioned evidence of hot path and Copilot's own analysis admitted minimal benefit; no benchmark or additional justification provided.
- [3184463362](https://github.com/dotnet/maui/pull/30291) `Copilot` — Fix RealParent garbage collection warning to reduce noise in production apps  
  `outcome_reason=abandoned_after_testing`；拒因摘要：Maintainer used PR as a test for Copilot instructions; after multiple resets and instruction updates, PR was closed without merge, likely because the process was experimental.

反模式（`inefficiency_antipattern` ≠ none）只作伴随现象：

- Merged 侧 Top：
`repeated_io`(33), `nested_loop`(10), `lock_misuse`(2), `main_thread_blocking`(2), `memory_leak`(2), `string_traversal`(2)

- Closed 侧 Top：
`repeated_io`(35), `nested_loop`(4), `lock_misuse`(3), `repeated_computation`(2), `redundant_computation`(2), `blocking_io`(2)

两侧都是 `repeated_io` 最多，数量接近，**不能当成主拒因**。

**小结**：一旦把「没人看就关了」的 PR 拿掉，剩下的失败更接近「补丁错了 / 方案不对 / CI 过不了 / 缺材料」。静默 maintainer 关闭仍需单独看待，它介于拒绝和遗弃之间。

### RQ3.2 证据生成、流程协作与同 PR 修复分别暴露了哪些能力边界？

三条既有 `boundary_tag` 是分析标签（不是测得的认知能力），对应三种非代码摩擦；`unknown` 仅 1 条，一并列出以免看起来像 1182。

| 边界 | 含义 | n | 合并率 |
|---|---|---|---|
| `technical_stack` | 常规技术栈改动（分析标签，不是能力测定） | 588 | 80.4% |
| `process` | 协作 / 审查 / 流程推进 | 562 | 38.1% |
| `evidence_required` | 维护者要求可复现性能证据 | 32 | 21.9% |
| `unknown` | 未归入以上三档 | 1 | 0.0% |

上表合计 1183/1183。

**证据边界示例（evidence_required × closed）：**

- [2839448717](https://github.com/pyth-network/pyth-crosschain/pull/2359) `Devin` — build: add parallel and concurrency flags to test:ci and build:ci  
  `outcome_reason=no_performance_improvement`；拒因摘要：Agent self-closed after concluding no performance improvement; no external CHANGES_REQUESTED.
- [3033886992](https://github.com/calcom/cal.com/pull/21052) `Devin` — perf: optimize app loading and rendering performance with CI fix  
  `outcome_reason=closed_harmful_ci_change_fabricated_benchmark`；拒因摘要：PR closed after retrogtx's 'insane, closing' comment on type-check CI change; no further fixes attempted.
- [3053649404](https://github.com/calcom/cal.com/pull/21220) `Devin` — perf: optimize .tz() calls with proper timezone detection  
  `outcome_reason=closed_not_performance_focused_approach`；拒因摘要：Devin AI bot closed the PR, stating the approach was not properly focused on performance optimization.

退化 / 审查问题处置（`regression_handling`）：

| regression_handling | 数量 | 占 n |
|---|---|---|
| `not_applicable` | 598 | 50.5% |
| `reject_close` | 398 | 33.6% |
| `fix_in_pr` | 143 | 12.1% |
| `ignore` | 18 | 1.5% |
| `unknown` | 17 | 1.4% |
| `revert` | 2 | 0.2% |
| `fix_followup` | 2 | 0.2% |
| `close_no_merge` | 1 | 0.1% |
| `abandon` | 1 | 0.1% |
| `recreated_in_new_pr` | 1 | 0.1% |
| `closed_no_merge` | 1 | 0.1% |
| `draft_converted_no_fix` | 1 | 0.1% |

上表合计 1183/1183。

`fix_in_pr` 共 143 条（12.1%）。修复主体启发式：

| 修复模式 | 数量 | 占 fix_in_pr |
|---|---|---|
| human_led_or_requested | 80 | 55.9% |
| ai_author_in_pr | 32 | 22.4% |
| human_ai_collaborative | 21 | 14.7% |
| unclear | 10 | 7.0% |

`antipattern_in_fix` 非 none 共 **7** 条（0.6%），只说明二次引入反模式是稀有风险，不能当核心发现。`revert` 极少。

**小结**：

- **证据生成**：一进入 `evidence_required`，合并率掉到约一成；sufficient 材料只有约 2%。
- **流程协作**：process 边界合入率大约只有 technical_stack 的一半；closed 里沉默遗弃仍是大头。
- **同 PR 修复**：能在原 PR 里把问题修完的是少数，且过半要人类主导。现有启发式并不支持把 CHANGES_REQUESTED 主要写成 Agent 独立消化。

---

## RQ4 核心差异：合入与关闭差在哪？能力边界是否影响结果？如何提高合并率？

### RQ4.1 成功合入与失败 / 搁置在核心维度上有何显著差异？

| 维度 | Merged | Closed | 读法 |
|---|---|---|---|
| 寿命 | 中位 0.122 h，fast_merge 76.1% | 中位 37.6 h，fast_merge 0 | 成功是快路径 |
| 规模 | 中位 changes 143；≤100 行档合并率最高 | 中位 170 | 小补丁占优，但 >10k 仍可合，不能写成越大越不能合 |
| 互动 | 评论中位 0；57.3% 为 0 | 评论中位 2 | 高评论量不对应更高合并率 |
| 材料 | benchmark 表 2.6%；数字声称 13.3% | benchmark 表 6.1%；数字声称 25.2% | Closed 更常给证据，证据是难 PR 门槛而非成功标配 |

**perf_focus 对照**

- Merged：
`constant_folding`(24), `compiler_optimization`(21), `benchmark_infrastructure`(11), `cache`(8), `lazy_loading`(7), `compile_time_optimization`(7), `build_performance`(6), `caching`(6)

- Closed：
`bundle_size_reduction`(12), `cache`(9), `constant_folding`(9), `lazy_load`(7), `build_performance`(6), `caching`(6), `code_splitting`(6), `compiler_optimization`(6)

成功侧更偏常量折叠、编译优化、缓存；关闭侧更常见包体积、复杂构建、code splitting。

### RQ4.2 合入和关闭在 AI 能力边界上有哪些区别？是否影响合并结果？

![boundary](rq_analysis_figures/rq4_boundary.png)

合并率按 `optimization_layer`（n≥20）：

| optimization_layer | n | 合并率 |
|---|---|---|
| `compiler_backend` | 26 | 84.6% |
| `compiler` | 45 | 80.0% |
| `application_control_flow` | 83 | 61.4% |
| `runtime_library` | 117 | 59.8% |
| `build` | 163 | 58.9% |
| `infrastructure` | 33 | 57.6% |
| `application_service` | 193 | 54.4% |
| `frontend_ui` | 135 | 51.1% |
| `runtime_vm` | 29 | 27.6% |

**现象（描述性）**：能力边界和合并结果同向变化。

- 落在 `technical_stack` 的 PR 合并率接近八成：小范围、可模板化的缓存 / 常量 / 编译类改动。
- 落在 `process` 的 PR 只有约三成合入：无人审、stale、作者放弃。这是协作边界，不一定是代码写错。
- 落在 `evidence_required` 的 PR 合并率约一成：维护者要数字，Agent 给的是叙述。
- 层面信号一致但样本更小：`compiler` / `compiler_backend` 合入高，`runtime_vm` 明显低。

因此：**存在「能力边界与合并结果一起分层」的现象**，但还不是「边界导致失败」的因果证明。流程边界尤其可能是维护者注意力问题，而不是 Agent 写不出补丁。

### RQ4.3 针对现有缺陷，有哪些可操作改进能提高合并率？

不要开一张万能药方。按 RQ1–RQ3 的两条真实路径分别改。

**路径 A — 已经在走的低摩擦合入（RQ1.2 / RQ2）**

- 保持原子补丁，优先 `technical_stack` 上的缓存、常量折叠、构建层改动。
- 降低维护者注意力成本：标题/正文写清「改了什么、为什么安全」，而不是先堆 benchmark。
- 无 Issue 的主动优化不要默认丢进需要深度审的队列；需要仓库侧的分诊（bot 标 `small/perf-safe`）。
- **不要**强制所有 PR <100 行：≤100 行合并率最高，但大 PR 仍有约一半合入。

**路径 B — 需要被认真审的难 PR（RQ1.3 / RQ3）**

- 工具链补可复现材料：前后对比表 + 复现步骤，对准 `evidence_required` 的悬崖，而不是给快合并路径加表。
- Review 阶段把 CHANGES_REQUESTED 当成一等任务；当前 `fix_in_pr` 过半是人类主导，不能默认审查意见会被自动消化。
- 对 `runtime_vm`、大范围控制流、包体积类改动提前声明风险，或拆成可独立合入的证据提交 + 代码提交。
- 沉默遗弃是注意力问题：超时提醒、把 stale bot 关闭改成「需要 maintainer 一句话」而不是直接关。

**明确不支持的说法**：Closed 组更常带数字声称和 benchmark 表，因此「给所有性能 PR 加 benchmark 就会提高合并率」与现有相关方向相反。Benchmark 应留给被要求举证的难 PR。

---

## 总结

1. **RQ1**：语料为终态 merged / closed。Closed 即被拒，内部以沉默遗弃为主，真正技术/设计拒绝约占被拒三分之一。Merged 以低摩擦快合并为主。Agent 之间合并率差一倍以上。
2. **RQ2**：成功 PR 极短命、常无审查；放行靠读码和小补丁，不靠 profiler。无人审同时出现在合入和关闭两侧，更像注意力 / 流程问题。
3. **RQ3**：真正被审的失败以正确性、设计、CI 为主；证据边界和流程边界比「又套了一层循环」更能解释合不进去；同 PR 修复少且依赖人类。
4. **RQ4**：寿命、边界类型、优化层面差异清楚，材料差异方向与「多写 benchmark 就能合」相反。改进必须分快路径和难路径。

## 附录 A 分类规则（可复现）

### Merged 路径 `merged_path`

1. `outcome_reason` 含 after_review / iterative / maintainer_fix → `reviewed_iteration`；否则若有 formal review 且非 fast_merge → 同类。
2. `fast_merge` 或（寿命 <1h 且 review_count=0）→ `fast_low_friction`。
3. 仍无 review 或标签含 no_review / self_merge → `no_formal_review`。
4. 其余 `other`。

### GitHub 状态（先于 Closed 动机）

- `merged`：已合入。
- `closed`：终态未合入 = 本研究的被拒。open 已从最终数据集剔除。

### Closed 动机 `close_motivation`（closed 的内部划分，全部仍是被拒）

1. 替代 PR / 误提交撤回等 → `other_process`（若同时有强技术否决则仍算真正拒绝）。
2. `blocking`、CHANGES_REQUESTED、技术类 `outcome_reason` / `primary_concern` / review 分桶、明确 rollback 文本 → `real_rejection`。
3. stale / 无审查 / 作者自行关闭 / 自动过期 → `silent_abandonment`。
4. 其余 `unclear`。

### 被审 closed 子集

`has_formal_review` 或 `blocking` 或 CHANGES_REQUESTED>0 或 `review_comment_bucket` 不是 `no_review_text`。

## 附录 B 方法边界

1. 标签来自 LLM 分析 JSON，建议对 real rejection / silent abandonment 各抽检数十条 `rejection_signals`。
2. Agent 差异、边界与合并率、benchmark 与合并率都是相关不是因果。合并率分母为最终数据集 n。
3. `fix_in_pr` 主体与 `antipattern_in_fix` 是启发式。
4. `FullAnalysis.md` §2 的 `outcome_reason` 粗分组（如 small_scope_low_risk）与本报告 RQ1.2 的 `merged_path`（如低摩擦快合并）是两套规则，数字不可互换。两侧都从同一终态 1183 条聚合。
