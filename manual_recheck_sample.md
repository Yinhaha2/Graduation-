# 人工复检抽样名单

每个 PR 只核对摘要里用到的三个标签：关闭机制（只看关闭的 PR）、`boundary_tag`、`detection_method`。
对照表最后三列填写判断，每格一个整数：

| 取值 | 含义 |
|---:|---|
| 1 | 对 |
| -1 | 错 |
| 0 | 说不清 |
| 2 | 无效。合并 PR 的关闭机制默认是 2，不再判断。关闭 PR 的关闭机制，以及全部 PR 的 `boundary_tag`、`detection_method`，由复检人填写 1、-1 或 0。 |

抽样框为终态语料 1,183 条（merged 694 / closed 489）。其中 6 条 prompt few-shot 已从抽样框剔除，剩余 1,177 条。随机种子 `20260925`。合并与关闭各 60 条。
每个 agent 在 A、B、A&B 三份名单里都出现。A 与 B 各 50 条专属工作量，且各自合并 25、关闭 25；A&B 为 20 条公共工作量。

分层配额（agent × status；每层先保底 4，其余 40 个名额按该状态下的层规模用最大余数法分配）：

| Agent | Merged | Closed |
|---|---:|---:|
| OpenAI_Codex | 31 | 18 |
| Devin | 8 | 16 |
| Copilot | 9 | 14 |
| Cursor | 7 | 7 |
| Claude_Code | 5 | 5 |

```json
{
  "A": [
    2859112713,
    2899450757,
    2918513256,
    3070333952,
    3071302729,
    3078500498,
    3081407923,
    3088220705,
    3096586088,
    3099818675,
    3104271017,
    3107327866,
    3122714770,
    3127179519,
    3131847694,
    3137786825,
    3140239245,
    3142771614,
    3147147049,
    3150133933,
    3154548302,
    3154652967,
    3155310952,
    3165644329,
    3166859797,
    3167979829,
    3171559766,
    3176059878,
    3183820232,
    3189026488,
    3189851555,
    3195541807,
    3195588879,
    3196526840,
    3199875911,
    3200433499,
    3203378195,
    3216660550,
    3218984690,
    3219880512,
    3225994185,
    3230465602,
    3241691177,
    3254647682,
    3261727113,
    3261747303,
    3261933492,
    3266937953,
    3275676664,
    3276475340
  ],
  "B": [
    2838837697,
    2855302194,
    2876006908,
    2986072834,
    3006546708,
    3027146476,
    3078523741,
    3080621090,
    3085814797,
    3088785176,
    3094144121,
    3097996516,
    3098274260,
    3098597632,
    3098890364,
    3104768514,
    3125710825,
    3126110678,
    3128593850,
    3128738345,
    3147883994,
    3148127134,
    3153056941,
    3158727370,
    3164861006,
    3171715437,
    3172600798,
    3174654401,
    3182184191,
    3185047320,
    3186315425,
    3189032906,
    3193198936,
    3204234091,
    3206997775,
    3209397522,
    3210885983,
    3213895675,
    3216548273,
    3234031765,
    3235395709,
    3239403987,
    3241523087,
    3246161753,
    3253059537,
    3258420806,
    3261008079,
    3262707090,
    3262887238,
    3274990408
  ],
  "A&B": [
    2927184629,
    2976324699,
    3099825876,
    3106804055,
    3133544722,
    3137902575,
    3138324206,
    3138362649,
    3140054883,
    3161909204,
    3188612213,
    3197078069,
    3197380367,
    3207831434,
    3208320625,
    3219088212,
    3226043406,
    3242428313,
    3257102140,
    3258539679
  ]
}
```

## 对照表

下表便于打开 GitHub。`workload` 与上面的 JSON 分组一致，`pr_id` 是主表 `id`。
最后三列是复检打分。合并 PR 的关闭机制已填 2；其余判断格留空。

| pr_id | workload | status | agent | repo | number | url | 关闭机制 | boundary_tag | detection_method |
|---|---|---|---|---|---:|---|---:|---:|---:|
| 2859112713 | A | closed | Devin | different-ai/note-companion | 325 | https://github.com/different-ai/note-companion/pull/325 |  |  |  |
| 2899450757 | A | closed | Devin | OneKeyHQ/app-monorepo | 6827 | https://github.com/OneKeyHQ/app-monorepo/pull/6827 |  |  |  |
| 2918513256 | A | closed | Devin | Cap-go/capgo | 1060 | https://github.com/Cap-go/capgo/pull/1060 |  |  |  |
| 3070333952 | A | merged | OpenAI_Codex | julep-ai/julep | 1373 | https://github.com/julep-ai/julep/pull/1373 | 2 |  |  |
| 3071302729 | A | merged | Devin | yamadashy/repomix | 566 | https://github.com/yamadashy/repomix/pull/566 | 2 |  |  |
| 3078500498 | A | closed | OpenAI_Codex | elixr-games/elics | 24 | https://github.com/elixr-games/elics/pull/24 |  |  |  |
| 3081407923 | A | merged | Copilot | microsoft/ApplicationInsights-JS | 2547 | https://github.com/microsoft/ApplicationInsights-JS/pull/2547 | 2 |  |  |
| 3088220705 | A | closed | Copilot | openops-cloud/openops | 684 | https://github.com/openops-cloud/openops/pull/684 |  |  |  |
| 3096586088 | A | closed | OpenAI_Codex | superagent-ai/vibekit | 12 | https://github.com/superagent-ai/vibekit/pull/12 |  |  |  |
| 3099818675 | A | closed | Cursor | tokens-studio/figma-plugin | 3393 | https://github.com/tokens-studio/figma-plugin/pull/3393 |  |  |  |
| 3104271017 | A | merged | Devin | vercel/next.js | 80002 | https://github.com/vercel/next.js/pull/80002 | 2 |  |  |
| 3107327866 | A | merged | OpenAI_Codex | MontrealAI/AGI-Alpha-Agent-v0 | 1342 | https://github.com/MontrealAI/AGI-Alpha-Agent-v0/pull/1342 | 2 |  |  |
| 3122714770 | A | merged | OpenAI_Codex | MontrealAI/AGI-Alpha-Agent-v0 | 1637 | https://github.com/MontrealAI/AGI-Alpha-Agent-v0/pull/1637 | 2 |  |  |
| 3127179519 | A | closed | Devin | different-ai/zero-finance | 146 | https://github.com/different-ai/zero-finance/pull/146 |  |  |  |
| 3131847694 | A | merged | OpenAI_Codex | cartography-cncf/cartography | 1622 | https://github.com/cartography-cncf/cartography/pull/1622 | 2 |  |  |
| 3137786825 | A | closed | Devin | jodendaal/OpenAI.Net | 89 | https://github.com/jodendaal/OpenAI.Net/pull/89 |  |  |  |
| 3140239245 | A | merged | Devin | openvm-org/openvm | 1731 | https://github.com/openvm-org/openvm/pull/1731 | 2 |  |  |
| 3142771614 | A | closed | OpenAI_Codex | moonbitlang/core | 2267 | https://github.com/moonbitlang/core/pull/2267 |  |  |  |
| 3147147049 | A | closed | Copilot | microsoft/lisa | 3862 | https://github.com/microsoft/lisa/pull/3862 |  |  |  |
| 3150133933 | A | merged | OpenAI_Codex | mochilang/mochi | 1134 | https://github.com/mochilang/mochi/pull/1134 | 2 |  |  |
| 3154548302 | A | merged | OpenAI_Codex | carverauto/serviceradar | 951 | https://github.com/carverauto/serviceradar/pull/951 | 2 |  |  |
| 3154652967 | A | merged | Copilot | dotnet/sdk | 49459 | https://github.com/dotnet/sdk/pull/49459 | 2 |  |  |
| 3155310952 | A | closed | Devin | liam-hq/liam | 2057 | https://github.com/liam-hq/liam/pull/2057 |  |  |  |
| 3165644329 | A | merged | Cursor | ryokun6/ryos | 144 | https://github.com/ryokun6/ryos/pull/144 | 2 |  |  |
| 3166859797 | A | merged | OpenAI_Codex | jdereg/java-util | 347 | https://github.com/jdereg/java-util/pull/347 | 2 |  |  |
| 3167979829 | A | closed | Copilot | microsoft/genaiscript | 1633 | https://github.com/microsoft/genaiscript/pull/1633 |  |  |  |
| 3171559766 | A | closed | Cursor | browser-use/browser-use | 2085 | https://github.com/browser-use/browser-use/pull/2085 |  |  |  |
| 3176059878 | A | closed | Devin | antiwork/flexile | 413 | https://github.com/antiwork/flexile/pull/413 |  |  |  |
| 3183820232 | A | closed | OpenAI_Codex | mochilang/mochi | 3871 | https://github.com/mochilang/mochi/pull/3871 |  |  |  |
| 3189026488 | A | closed | OpenAI_Codex | mochilang/mochi | 4268 | https://github.com/mochilang/mochi/pull/4268 |  |  |  |
| 3189851555 | A | merged | OpenAI_Codex | prebid/Prebid.js | 13464 | https://github.com/prebid/Prebid.js/pull/13464 | 2 |  |  |
| 3195541807 | A | merged | Cursor | module-federation/core | 3876 | https://github.com/module-federation/core/pull/3876 | 2 |  |  |
| 3195588879 | A | merged | Copilot | mlflow/mlflow | 16531 | https://github.com/mlflow/mlflow/pull/16531 | 2 |  |  |
| 3196526840 | A | closed | Cursor | 567-labs/instructor | 1645 | https://github.com/567-labs/instructor/pull/1645 |  |  |  |
| 3199875911 | A | closed | Copilot | chrxh/alien | 125 | https://github.com/chrxh/alien/pull/125 |  |  |  |
| 3200433499 | A | closed | Copilot | microsoft/ebpf-for-windows | 4495 | https://github.com/microsoft/ebpf-for-windows/pull/4495 |  |  |  |
| 3203378195 | A | merged | OpenAI_Codex | MontrealAI/AGI-Alpha-Agent-v0 | 2949 | https://github.com/MontrealAI/AGI-Alpha-Agent-v0/pull/2949 | 2 |  |  |
| 3216660550 | A | merged | OpenAI_Codex | MontrealAI/AGI-Alpha-Agent-v0 | 3147 | https://github.com/MontrealAI/AGI-Alpha-Agent-v0/pull/3147 | 2 |  |  |
| 3218984690 | A | merged | Copilot | microsoft/vscode | 255114 | https://github.com/microsoft/vscode/pull/255114 | 2 |  |  |
| 3219880512 | A | merged | Claude_Code | Significant-Gravitas/AutoGPT | 10340 | https://github.com/Significant-Gravitas/AutoGPT/pull/10340 | 2 |  |  |
| 3225994185 | A | closed | OpenAI_Codex | BLAKE3-team/BLAKE3 | 495 | https://github.com/BLAKE3-team/BLAKE3/pull/495 |  |  |  |
| 3230465602 | A | closed | OpenAI_Codex | openai/codex | 1574 | https://github.com/openai/codex/pull/1574 |  |  |  |
| 3241691177 | A | merged | OpenAI_Codex | mochilang/mochi | 9436 | https://github.com/mochilang/mochi/pull/9436 | 2 |  |  |
| 3254647682 | A | closed | Claude_Code | JuliaLang/julia | 59071 | https://github.com/JuliaLang/julia/pull/59071 |  |  |  |
| 3261727113 | A | merged | OpenAI_Codex | mochilang/mochi | 12867 | https://github.com/mochilang/mochi/pull/12867 | 2 |  |  |
| 3261747303 | A | merged | OpenAI_Codex | mochilang/mochi | 12879 | https://github.com/mochilang/mochi/pull/12879 | 2 |  |  |
| 3261933492 | A | closed | OpenAI_Codex | mochilang/mochi | 12958 | https://github.com/mochilang/mochi/pull/12958 |  |  |  |
| 3266937953 | A | merged | OpenAI_Codex | mochilang/mochi | 13718 | https://github.com/mochilang/mochi/pull/13718 | 2 |  |  |
| 3275676664 | A | closed | Copilot | halo-dev/halo | 7645 | https://github.com/halo-dev/halo/pull/7645 |  |  |  |
| 3276475340 | A | merged | OpenAI_Codex | MihaiCristianCondrea/Smart-Cleaner-for-Android | 240 | https://github.com/MihaiCristianCondrea/Smart-Cleaner-for-Android/pull/240 | 2 |  |  |
| 2838837697 | B | merged | Devin | pyth-network/pyth-crosschain | 2351 | https://github.com/pyth-network/pyth-crosschain/pull/2351 | 2 |  |  |
| 2855302194 | B | closed | Devin | pdfme/pdfme | 711 | https://github.com/pdfme/pdfme/pull/711 |  |  |  |
| 2876006908 | B | closed | Claude_Code | zenml-io/zenml | 3375 | https://github.com/zenml-io/zenml/pull/3375 |  |  |  |
| 2986072834 | B | merged | Claude_Code | JoshuaC215/agent-service-toolkit | 202 | https://github.com/JoshuaC215/agent-service-toolkit/pull/202 | 2 |  |  |
| 3006546708 | B | closed | Devin | saturday06/VRM-Addon-for-Blender | 799 | https://github.com/saturday06/VRM-Addon-for-Blender/pull/799 |  |  |  |
| 3027146476 | B | closed | Devin | reflex-dev/reflex-web | 1321 | https://github.com/reflex-dev/reflex-web/pull/1321 |  |  |  |
| 3078523741 | B | closed | Copilot | lutzroeder/netron | 1460 | https://github.com/lutzroeder/netron/pull/1460 |  |  |  |
| 3080621090 | B | closed | Devin | novuhq/novu | 8360 | https://github.com/novuhq/novu/pull/8360 |  |  |  |
| 3085814797 | B | closed | OpenAI_Codex | CapSoftware/Cap | 569 | https://github.com/CapSoftware/Cap/pull/569 |  |  |  |
| 3088785176 | B | closed | OpenAI_Codex | oven-sh/bun | 19894 | https://github.com/oven-sh/bun/pull/19894 |  |  |  |
| 3094144121 | B | merged | Copilot | mlflow/mlflow | 15909 | https://github.com/mlflow/mlflow/pull/15909 | 2 |  |  |
| 3097996516 | B | merged | Devin | adrgs/requestrepo | 67 | https://github.com/adrgs/requestrepo/pull/67 | 2 |  |  |
| 3098274260 | B | closed | OpenAI_Codex | prebid/Prebid.js | 13200 | https://github.com/prebid/Prebid.js/pull/13200 |  |  |  |
| 3098597632 | B | merged | OpenAI_Codex | PyLabRobot/pylabrobot | 529 | https://github.com/PyLabRobot/pylabrobot/pull/529 | 2 |  |  |
| 3098890364 | B | closed | Copilot | giselles-ai/giselle | 993 | https://github.com/giselles-ai/giselle/pull/993 |  |  |  |
| 3104768514 | B | merged | OpenAI_Codex | MontrealAI/AGI-Alpha-Agent-v0 | 1251 | https://github.com/MontrealAI/AGI-Alpha-Agent-v0/pull/1251 | 2 |  |  |
| 3125710825 | B | merged | Copilot | celestiaorg/celestia-core | 1936 | https://github.com/celestiaorg/celestia-core/pull/1936 | 2 |  |  |
| 3126110678 | B | merged | OpenAI_Codex | theepicsaxguy/homelab | 829 | https://github.com/theepicsaxguy/homelab/pull/829 | 2 |  |  |
| 3128593850 | B | merged | OpenAI_Codex | phellipeandrade/rbac | 42 | https://github.com/phellipeandrade/rbac/pull/42 | 2 |  |  |
| 3128738345 | B | merged | OpenAI_Codex | mochilang/mochi | 207 | https://github.com/mochilang/mochi/pull/207 | 2 |  |  |
| 3147883994 | B | merged | Cursor | haydenbleasel/kibo | 153 | https://github.com/haydenbleasel/kibo/pull/153 | 2 |  |  |
| 3148127134 | B | closed | Devin | sikanhe/gqtx | 79 | https://github.com/sikanhe/gqtx/pull/79 |  |  |  |
| 3153056941 | B | closed | OpenAI_Codex | mochilang/mochi | 1277 | https://github.com/mochilang/mochi/pull/1277 |  |  |  |
| 3158727370 | B | closed | Copilot | tomhrr/cosh | 181 | https://github.com/tomhrr/cosh/pull/181 |  |  |  |
| 3164861006 | B | closed | Cursor | oven-sh/bun | 20535 | https://github.com/oven-sh/bun/pull/20535 |  |  |  |
| 3171715437 | B | merged | Cursor | TanStack/db | 198 | https://github.com/TanStack/db/pull/198 | 2 |  |  |
| 3172600798 | B | closed | Copilot | evstack/ev-node | 2387 | https://github.com/evstack/ev-node/pull/2387 |  |  |  |
| 3174654401 | B | merged | Cursor | getsentry/relay | 4855 | https://github.com/getsentry/relay/pull/4855 | 2 |  |  |
| 3182184191 | B | closed | Devin | crewAIInc/crewAI | 3077 | https://github.com/crewAIInc/crewAI/pull/3077 |  |  |  |
| 3185047320 | B | merged | OpenAI_Codex | MontrealAI/AGI-Alpha-Agent-v0 | 2708 | https://github.com/MontrealAI/AGI-Alpha-Agent-v0/pull/2708 | 2 |  |  |
| 3186315425 | B | closed | OpenAI_Codex | mochilang/mochi | 3985 | https://github.com/mochilang/mochi/pull/3985 |  |  |  |
| 3189032906 | B | merged | OpenAI_Codex | mochilang/mochi | 4282 | https://github.com/mochilang/mochi/pull/4282 | 2 |  |  |
| 3193198936 | B | merged | Claude_Code | tphakala/birdnet-go | 841 | https://github.com/tphakala/birdnet-go/pull/841 | 2 |  |  |
| 3204234091 | B | closed | Cursor | gmathi/NovelLibrary | 243 | https://github.com/gmathi/NovelLibrary/pull/243 |  |  |  |
| 3206997775 | B | closed | Devin | bolna-ai/bolna | 221 | https://github.com/bolna-ai/bolna/pull/221 |  |  |  |
| 3209397522 | B | merged | OpenAI_Codex | mochilang/mochi | 6114 | https://github.com/mochilang/mochi/pull/6114 | 2 |  |  |
| 3210885983 | B | closed | Copilot | ant-design/ant-design | 54325 | https://github.com/ant-design/ant-design/pull/54325 |  |  |  |
| 3213895675 | B | merged | OpenAI_Codex | jscarle/LightResults | 77 | https://github.com/jscarle/LightResults/pull/77 | 2 |  |  |
| 3216548273 | B | merged | OpenAI_Codex | mochilang/mochi | 6882 | https://github.com/mochilang/mochi/pull/6882 | 2 |  |  |
| 3234031765 | B | merged | OpenAI_Codex | stanford-crfm/levanter | 1066 | https://github.com/stanford-crfm/levanter/pull/1066 | 2 |  |  |
| 3235395709 | B | closed | Claude_Code | zed-industries/zed | 34529 | https://github.com/zed-industries/zed/pull/34529 |  |  |  |
| 3239403987 | B | merged | OpenAI_Codex | mochilang/mochi | 9329 | https://github.com/mochilang/mochi/pull/9329 | 2 |  |  |
| 3241523087 | B | closed | Copilot | doodlum/skyrim-community-shaders | 1281 | https://github.com/doodlum/skyrim-community-shaders/pull/1281 |  |  |  |
| 3246161753 | B | merged | OpenAI_Codex | MihaiCristianCondrea/Smart-Cleaner-for-Android | 214 | https://github.com/MihaiCristianCondrea/Smart-Cleaner-for-Android/pull/214 | 2 |  |  |
| 3253059537 | B | merged | Copilot | GMPrakhar/MAUI-Designer | 53 | https://github.com/GMPrakhar/MAUI-Designer/pull/53 | 2 |  |  |
| 3258420806 | B | closed | OpenAI_Codex | deepflowio/deepflow | 10177 | https://github.com/deepflowio/deepflow/pull/10177 |  |  |  |
| 3261008079 | B | merged | Devin | mendableai/firecrawl | 1840 | https://github.com/mendableai/firecrawl/pull/1840 | 2 |  |  |
| 3262707090 | B | closed | OpenAI_Codex | mochilang/mochi | 13030 | https://github.com/mochilang/mochi/pull/13030 |  |  |  |
| 3262887238 | B | closed | OpenAI_Codex | mochilang/mochi | 13066 | https://github.com/mochilang/mochi/pull/13066 |  |  |  |
| 3274990408 | B | merged | OpenAI_Codex | copper-project/copper-rs | 410 | https://github.com/copper-project/copper-rs/pull/410 | 2 |  |  |
| 2927184629 | A&B | merged | Devin | onlook-dev/onlook | 1634 | https://github.com/onlook-dev/onlook/pull/1634 | 2 |  |  |
| 2976324699 | A&B | closed | Devin | digitaldemocracy2030/kouchou-ai | 246 | https://github.com/digitaldemocracy2030/kouchou-ai/pull/246 |  |  |  |
| 3099825876 | A&B | merged | Devin | neondatabase/neon | 12057 | https://github.com/neondatabase/neon/pull/12057 | 2 |  |  |
| 3106804055 | A&B | merged | OpenAI_Codex | OpenHFT/Chronicle-Core | 814 | https://github.com/OpenHFT/Chronicle-Core/pull/814 | 2 |  |  |
| 3133544722 | A&B | merged | Claude_Code | meilisearch/meilisearch-mcp | 42 | https://github.com/meilisearch/meilisearch-mcp/pull/42 | 2 |  |  |
| 3137902575 | A&B | merged | Copilot | PowerShell/vscode-powershell | 5212 | https://github.com/PowerShell/vscode-powershell/pull/5212 | 2 |  |  |
| 3138324206 | A&B | merged | Cursor | elie222/inbox-zero | 505 | https://github.com/elie222/inbox-zero/pull/505 | 2 |  |  |
| 3138362649 | A&B | merged | Claude_Code | evmts/tevm-monorepo | 1847 | https://github.com/evmts/tevm-monorepo/pull/1847 | 2 |  |  |
| 3140054883 | A&B | closed | Copilot | tokens-studio/figma-plugin | 3422 | https://github.com/tokens-studio/figma-plugin/pull/3422 |  |  |  |
| 3161909204 | A&B | closed | Devin | ateliee/jquery.schedule | 58 | https://github.com/ateliee/jquery.schedule/pull/58 |  |  |  |
| 3188612213 | A&B | closed | OpenAI_Codex | mochilang/mochi | 4190 | https://github.com/mochilang/mochi/pull/4190 |  |  |  |
| 3197078069 | A&B | merged | Cursor | epicweb-dev/restore-scroll | 13 | https://github.com/epicweb-dev/restore-scroll/pull/13 | 2 |  |  |
| 3197380367 | A&B | closed | OpenAI_Codex | featureform/enrichmcp | 104 | https://github.com/featureform/enrichmcp/pull/104 |  |  |  |
| 3207831434 | A&B | closed | Cursor | nnstreamer/nntrainer | 3293 | https://github.com/nnstreamer/nntrainer/pull/3293 |  |  |  |
| 3208320625 | A&B | closed | Copilot | NG-ZORRO/ng-zorro-antd | 9278 | https://github.com/NG-ZORRO/ng-zorro-antd/pull/9278 |  |  |  |
| 3219088212 | A&B | closed | Cursor | selfxyz/self | 756 | https://github.com/selfxyz/self/pull/756 |  |  |  |
| 3226043406 | A&B | closed | Claude_Code | promptfoo/promptfoo | 4902 | https://github.com/promptfoo/promptfoo/pull/4902 |  |  |  |
| 3242428313 | A&B | merged | OpenAI_Codex | xrdevrob/QuestCameraKit | 23 | https://github.com/xrdevrob/QuestCameraKit/pull/23 | 2 |  |  |
| 3257102140 | A&B | closed | Claude_Code | oxcaml/oxcaml | 4363 | https://github.com/oxcaml/oxcaml/pull/4363 |  |  |  |
| 3258539679 | A&B | merged | Copilot | CarGuo/gsy_github_app_flutter | 913 | https://github.com/CarGuo/gsy_github_app_flutter/pull/913 | 2 |  |  |
