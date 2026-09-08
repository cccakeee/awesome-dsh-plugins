## Other

> Corresponding category on the site: [Other](https://deepseekharnessplugins.com/plugins/category/utilities)

| Plugin | Capability | Install or mount | License / Risk |
| --- | --- | --- | --- |
| [FishBottle7/opencode2dsh](https://github.com/FishBottle7/opencode2dsh) | Add OpenCode Zen's anonymous free model lane as a native DSH provider in the model picker. | `dsh plugin --profile web add @opencode2dsh/dsh-plugin; restart dsh web and select a model from the opencode2dsh group.` | MIT; The anonymous lane is quota-per-IP and external; inspect upstream/privacy and keep the default adapter mode because the legacy sidecar is not in the published package. |
| [EarzuChan/DshVibeLearning](https://github.com/EarzuChan/DshVibeLearning) | Adds a `/learn` workflow with interactive lessons, review scheduling, quizzes, persistent outlines and notes, and an in-app learning panel. | Run `dsh plugin --profile web add dsh-vibe-learning`, then `dsh web`; in a new session run `/learn`. | MIT; The README labels the project early-stage/POC, warns of breaking changes, missing background reminders, last-writer-wins outline edits, and possible UI desynchronization. |
| [PensiveFei/dsh-voice-scribe](https://github.com/PensiveFei/dsh-voice-scribe) | Voice dictation input for DSH composer with local/offline ASR default. | `dsh plugin --profile web add dsh-voice-scribe` | MIT; Unaffiliated third-party plugin; host-side /voice-input routes fenced (loopback/trustedHosts). |
| [Ramenne/DeepSeek-Harness-Gov](https://github.com/Ramenne/DeepSeek-Harness-Gov) | Mount a 3081 government-style WebUI and a /hongtou command that reads the current session and renders Word 2003 XML documents. | `repo_dir=$(pwd); dsh plugin --profile web add link:${repo_dir}/plugins/dsh-gov-portal; dsh plugin --profile web add link:${repo_dir}/plugins/dsh-tool-hongtou; dsh web` | MIT; The root repository is a bundle of two independently mountable plugins rather than one single root package; its public demo is not evidence of production security or government endorsement, and /hongtou writes XML into the current workspace/output. |
| [TencentCloud/tencentcloud-agentobs-sdk-dsh](https://github.com/TencentCloud/tencentcloud-agentobs-sdk-dsh) | Streams DSH GenAI traces to Tencent Cloud CLS log service with 5-layer span hierarchy, configurable batching/retry, content capture toggle. | `dsh plugin --profile web\|headless\|harness add tencentcloud-agentobs-sdk-dsh` | Apache-2.0; Content capture enabled by default; disable via captureContent:false; requires DSH >=0.1.0-rc.6 <0.2.0. |
| [lizhiyao/oh-my-knowledge](https://github.com/lizhiyao/oh-my-knowledge) | Runs controlled A/B evals, artifact health checks, evidence-gated promote/evolve/rollback version lifecycle, observability traces. | `dsh plugin --profile web add oh-my-knowledge && dsh --profile web` | MIT; Primarily a standalone npm CLI; DSH integration is one of several executors. |
| [ZSeven-W/dsh-harbor](https://github.com/ZSeven-W/dsh-harbor) | Scans installed third-party DSH bundles and reports 13 capabilities with file:line evidence, conflict detection, version drift tracking. | `dsh plugin --profile web add @zseven-w/dsh-harbor@next && dsh web` | MIT; Pre-release 0.1.0-rc.2 (install via @next tag); static analysis yields false pos/neg. |
| [Yan-Zero/dsh-std](https://github.com/Yan-Zero/dsh-std) | Protocol-definition meta-layer and DSH adapter loading standard dsh-plugin.json facets into DSH. | `dsh plugin --profile web add @dsh-std/adapter-dsh` | MIT; Explicitly early drafts (0.1.0-rc); package surface and rc protocol alignment still churning. |
| [lninghaha/dsh-coding-subscription-oauth](https://github.com/lninghaha/dsh-coding-subscription-oauth) | 为 DSH 提供编码订阅 OAuth 登录的模型路由插件，一个插件覆盖五个 Provider：SuperGrok/Grok Build、ChatGPT Plus/Pro Codex、Kimi Code、Claude Code 及 Google Antigravity。含本地 OAuth/device-code 登录、动态模型目录、凭据 0600 原子存储、可选本地 API 网关、Codex 搜索/用量/图像等可选能力 | `dsh plugin --profile web add dsh-coding-subscription-oauth@0.6.0（可选加 dsh plugin --profile web add dsh-agy@0.1.2），随后重启 DSH Web 进程；要求 DeepSeek Harness 0.1.0-rc.6+ 与 Node 22.19+` | Apache-2.0; 合规性：通过第三方 harness 使用厂商订阅账号处于各厂商条款灰色地带，项目声明仅限自有账号、不支持批量/配额转售/绕过付费墙；商业使用建议官方 API-key 渠道 |
| [zexadev/dsh-tether](https://github.com/zexadev/dsh-tether) | 通过 iroh P2P 打洞将开发机上的 DSH Web 界面端到端带到手机（Android 已签 APK / iOS 未签 beta IPA），支持多机配对、审批通知、跨网直连，无需公网 IP 或中转服务器；附 Rust sidecar 与 Tauri 手机应用 | 机器端：`dsh plugin --profile web add dsh-plugin-tether`；或源码：`cargo build --release -p tether-host && dsh plugin --profile web add .`；手机端从 GitHub Release 安装 APK | MIT; DSH 处于 developer preview，仅对 dsh 0.1.0-rc.7/rc.8 验证；iOS 为 beta（未真机运行、需自签、7 天过期）；README 建议不要在运行不可信代码的机器上启用本插件 |
| [lcgash/dsh-plugin-uw](https://github.com/lcgash/dsh-plugin-uw) | Merge multiple directories into one DSH session with configurable r/w scopes. | `dsh plugin add github:lcgash/dsh-plugin-uw` | Apache-2.0; License stated Apache-2.0 in README but GitHub license API null (no LICENSE file auto-detected) — verify LICENSE present before publishing. |
| [ZJU-LLMs/OpenStory](https://github.com/ZJU-LLMs/OpenStory) | Multi-agent story-world simulation registered as a DSH tool. | `npx -y @deepseek-ai/dsh plugin --profile web add dsh-openstory@0.2.0` | MIT; Heavy install (needs Redis + Python 3.11-3.13 + full source checkout). Freshly published; may trip DSH ERR_PNPM_MINIMUM_RELEASE_AGE_VIOLATION supply-chain guard - wait and retry, do not disable the policy. |
| [zuorn/Tydora](https://github.com/zuorn/Tydora) | Tauri v2 桌面 Markdown 编辑器（WYSIWYG/双向链接/思维导图/无限画布），仓库声明 dsh.bundle 补丁挂载最小 DSH 插件骨架 | see README（桌面应用，Release 安装）; DSH 装载：dsh plugin add 时应用 package.json dsh.bundle → cordis.patch.yml 补丁 | Apache-2.0; DSH 入口 dsh/index.ts 为最小可加载骨架，当前不注册任何能力；仓库主体是独立的桌面 Markdown 编辑器 |
| [Thanksgiver233/comm-protocol-hub](https://github.com/Thanksgiver233/comm-protocol-hub) | 3GPP 通信协议知识库插件：内置 70+ 条 Rel-15~18 协议结构化索引（TN/NTN/全息/近远场/混合/安全等 8 类），通过 3 个 DSH 工具（comm_protocol_query / comm_protocol_browse / comm_protocol_detail）供大模型按需查询，并附带 web 交互面板与对话内联卡片，数据本地内嵌、无需联网 | `npx -p @deepseek-ai/dsh dsh plugin --profile web add github:Thanksgiver233/comm-protocol-hub（本地开发可用 add <path-to-repo>）` | MIT; 仓库仅单次提交 'Add files via upload'（无开发历史）；package.json 的 repository.url 仍是 example.com 占位符；lib/ 构建产物未随仓库提供，需自行 pnpm build |
| [030611/dsh-context-provenance](https://github.com/030611/dsh-context-provenance) | Observe-only plugin tagging adjacent request evidence as Observed/Estimated/Unavailable without altering output. | `` | N/A |
| [030611/dsh-telemetry-redactor](https://github.com/030611/dsh-telemetry-redactor) | DSH 遥测数据脱敏插件，对上报/日志中的敏感字段做编辑后处理。 | `` | N/A |
| [030611/dsh-verification-receipt](https://github.com/030611/dsh-verification-receipt) | DSH 验证回执插件，为关键操作生成可审计的验证凭证。 | `` | N/A |
| [0lidaxiang/dsh-plugin-greet](https://github.com/0lidaxiang/dsh-plugin-greet) | greet 工具示例插件 | `` | MIT |
| [1624318455/dsh-plugin-tts](https://github.com/1624318455/dsh-plugin-tts) | DSH 文本转语音（TTS）插件，提供语音合成输出。 | `` | MIT |
| [3274375092/dsh-voice](https://github.com/3274375092/dsh-voice) | DSH 语音输入/语音交互插件。 | `` | MIT |
| [610la/dsh-notification-center](https://github.com/610la/dsh-notification-center) | DSH 通知中心插件（浏览器系统通知 + 21 种匹配音效） | `` | MIT |
| [940842546/dsh-usage-billing](https://github.com/940842546/dsh-usage-billing) | 用量与消费统计 | `` | MIT |
| [acidmoon/dizzy-dsh](https://github.com/acidmoon/dizzy-dsh) | DSH 扩展包（dizzy），具体能力需查看源码确认。 | `` | N/A |
| [akira399/dsh-novel-writer](https://github.com/akira399/dsh-novel-writer) | 网络小说创作插件：九阶段门禁式创作流程 + 世界书设定注入 + 本地书籍导入 + AI 一键润色 + 去 AI 味。 | cordis.patch.yml 挂载（见 README） | MIT |
| [asdf17128/dsh-doctor](https://github.com/asdf17128/dsh-doctor) | DSH 自检/诊断插件，检查配置与环境健康。 | `` | N/A |
| [ben7am1n/dsh-claude-marketplace](https://github.com/ben7am1n/dsh-claude-marketplace) | DSH 插件市场，可在 DSH 内浏览/安装 Claude 技能类扩展。 | `` | N/A |
| [benzhoupo/dsh-effort-config](https://github.com/benzhoupo/dsh-effort-config) | DSH 推理强度（effort）配置插件，调节模型推理投入。 | `` | N/A |
| [CH4ACKO3/dsh-harmony](https://github.com/CH4ACKO3/dsh-harmony) | Runtime patch framework that modifies other DSH plugins via source patches. | `` | MIT |
| [chaos-03x/dsh-agy](https://github.com/chaos-03x/dsh-agy) | Google Antigravity OAuth adapter for DSH (multi-account, 429 rotation). | `` | N/A |
| [cokiscarazo-rgb/dsh-session-management](https://github.com/cokiscarazo-rgb/dsh-session-management) | 会话归档/真删/批量导出 | `` | MIT |
| [dfycaly98931680/dsh-trajectory-governance](https://github.com/dfycaly98931680/dsh-trajectory-governance) | Agent trajectory governance: multi-branch trajectory trees, loop-deadlock/invalid-retry/goal-drift detection and alerts. | `` | MIT |
| [dragonbaba/dsh-routing-suite](https://github.com/dragonbaba/dsh-routing-suite) | Smart routing mode preset/plugin for DSH (read-only system-prompt guidance). | `` | MIT |
| [EdgeTypE/dsh-better-deepseek](https://github.com/EdgeTypE/dsh-better-deepseek) | DSH 桥接插件：为 Better DeepSeek Chrome 扩展提供 HTTP 握手与 SSE 会话端点 | `` | MIT |
| [errorcode7/dsh-prompt-manager](https://github.com/errorcode7/dsh-prompt-manager) | 提示词管理器 | `` | N/A |
| [fff122/dsh-agent-arcade](https://github.com/fff122/dsh-agent-arcade) | 确定性贪吃蛇小游戏 DSH 插件，agent 逐步决策。 | `` | MIT |
| [fff122/dsh-prompt-presets](https://github.com/fff122/dsh-prompt-presets) | 本地可复用提示词预设 DSH 插件，支持变量占位符。 | `` | MIT |
| [Gumiho12345/dsh-plugin-net-access](https://github.com/Gumiho12345/dsh-plugin-net-access) | DSH 网络访问插件，提供联网/请求能力。 | `` | MIT |
| [howmp/dsh-pentest](https://github.com/howmp/dsh-pentest) | DSH 渗透测试插件，提供安全测试能力。 | `` | MIT |
| [huguangyu666/dsh-store](https://github.com/huguangyu666/dsh-store) | DSH 插件商店/分发插件。 | `` | MIT |
| [hyls9527/dsh-plugins](https://github.com/hyls9527/dsh-plugins) | DSH 插件集合（已归档），含可加载 bundle。 | `` | MIT |
| [imlishiyuan/deepseek-harness-zh-cn](https://github.com/imlishiyuan/deepseek-harness-zh-cn) | DSH 中文本地化/文档与配置资源包。 | `` | Apache-2.0 |
| [jasper-zsh/dsh-plugin-provider-quota](https://github.com/jasper-zsh/dsh-plugin-provider-quota) | DSH provider 配额/预算监控插件。 | `` | MIT |
| [jiesou/dsh-commandcode-go-provider](https://github.com/jiesou/dsh-commandcode-go-provider) | DSH 的 command/code provider 插件。 | `` | MIT |
| [jleon-account/dsh-client-usage](https://github.com/jleon-account/dsh-client-usage) | DSH 客户端用量统计插件。 | `` | MIT |
| [kinoward/dsh-plugin-subhub](https://github.com/kinoward/dsh-plugin-subhub) | DSH 第三方订阅账户接入插件（当前支持 OpenAI/ChatGPT 订阅的文本/图像对话）。 | `` | MIT |
| [KunIsMe/dsh-filescope](https://github.com/KunIsMe/dsh-filescope) | DSH 文件作用域/可见性控制插件。 | `` | MIT |
| [LeemanCheung/dsh-token-usage](https://github.com/LeemanCheung/dsh-token-usage) | DSH 本地优先 Token 用量持久化 / 预算 / 轨迹审计插件 | `` | MIT |
| [Len7183/DSH-Think-zh](https://github.com/Len7183/DSH-Think-zh) | DSH 插件：强制思考用简体中文、回复跟随提问语言（注入 system prompt） | `` | MIT |
| [liguobao/deepseek-harness-remote](https://github.com/liguobao/deepseek-harness-remote) | 基于 DSH 插件机制的多端远程访问方案（桌面 + 安卓客户端操作远程 Harness） | `` | MIT |
| [loongsuite/dsh-plugin](https://github.com/loongsuite/dsh-plugin) | DSH OpenTelemetry 可观测性插件（GenAI trace/metrics 经 OTLP 导出到 Jaeger/Grafana 等） | `` | Apache-2.0 |
| [lxzy-7/dsh-plugin-guard](https://github.com/lxzy-7/dsh-plugin-guard) | DSH 防护/校验插件，对运行期行为做守卫与限制。 | `` | MIT |
| [MicroMilo/upstream-radar](https://github.com/MicroMilo/upstream-radar) | Continuous dependency monitor for DSH plugins surfacing precise vulnerability paths and breaking updates. | `` | Apache-2.0 |
| [Mochabafey/whale-notify](https://github.com/Mochabafey/whale-notify) | 鲸鱼通知（飞书/QQ/微信/邮件双向触发 agent） | `` | MIT |
| [Mr-remon219/dsh-search-boost](https://github.com/Mr-remon219/dsh-search-boost) | Search boost bundle for DSH (multi-engine fused search, X search, deep research). | `` | MIT |
| [multica-ai/dsh-multica-runtime](https://github.com/multica-ai/dsh-multica-runtime) | Private out-of-tree DSH runtime bridge for the Multica agent platform. | `` | N/A |
| [MutaLucem/dsh-plugin-integration](https://github.com/MutaLucem/dsh-plugin-integration) | DSH 插件集成/互通辅助插件。 | `` | MIT |
| [nanshan1995/DSH-Plugin-Market](https://github.com/nanshan1995/DSH-Plugin-Market) | In-DSH plugin market with GitHub topic browse, cross-language search and a pre-install static security audit gate. | `` | MIT |
| [Noob-stupid/dsh-github-login](https://github.com/Noob-stupid/dsh-github-login) | DSH GitHub 登录/OAuth 集成插件。 | `` | MIT |
| [oil-oil/dsh-oil-creator](https://github.com/oil-oil/dsh-oil-creator) | AI 辅助本地创作工作台：核心片库独立可用，Screen Studio 录屏、字幕、封面、公众号文章与发布能力按需安装。 | `npx @deepseek-ai/dsh plugin --profile web add github:oil-oil/dsh-oil-creator` | MIT |
| [omdsh-dev/dsh-sidechain](https://github.com/omdsh-dev/dsh-sidechain) | DSH side-conversation plugin (/side persistent, /btw one-shot forks). | `` | N/A |
| [Owen718/snapgrep](https://github.com/Owen718/snapgrep) | 进程内 Rust 三元组索引插件，让 Pi/DSH 代码搜索比 ripgrep 快最高 70× 且结果一致 | `` | MIT |
| [sugarforever/dsh-lark](https://github.com/sugarforever/dsh-lark) | Lark/Feishu integration host plugin for DSH (WebSocket channel). | `` | N/A |
| [taichuy/deepseek-harness-auth](https://github.com/taichuy/deepseek-harness-auth) | Out-of-tree authenticated web proxy bundle for DSH web profile. | `` | Apache-2.0 |
| [timeance/dsh-approve-for-me](https://github.com/timeance/dsh-approve-for-me) | Rule-gated automatic sandbox approval for DSH (optional LLM review). | `` | MIT |
| [TomoyoNatsume/dsh-qq-bridge](https://github.com/TomoyoNatsume/dsh-qq-bridge) | DSH QQ 消息桥接插件，将 QQ 频道消息接入智能体触发。 | `` | MIT |
| [w2112515/dsh-plugin-marketplace](https://github.com/w2112515/dsh-plugin-marketplace) | 树外插件市场 | `` | N/A |
| [wdsjwzl/session-seed-plugin](https://github.com/wdsjwzl/session-seed-plugin) | 会话自动注入种子 | `` | MIT |
| [WNJXYK/dsh-codex-oauth](https://github.com/WNJXYK/dsh-codex-oauth) | 通过 OpenAI/ChatGPT OAuth 在 DSH 使用 GPT/生图/联网的插件（共享订阅额度） | `` | MIT |
| [wz-heng/dsh-feishu-bridge](https://github.com/wz-heng/dsh-feishu-bridge) | DSH 飞书桥接插件，将飞书消息接入智能体触发。 | `` | MIT |
| [xmanrui/dsh-feishu](https://github.com/xmanrui/dsh-feishu) | 飞书机器人接入 | `` | MIT |
| [ymh0000123/dsh-client-masquerade](https://github.com/ymh0000123/dsh-client-masquerade) | 客户端身份伪装 | `` | MIT |
| [yuko0331/DSH-telegram](https://github.com/yuko0331/DSH-telegram) | DSH Telegram 桥接插件，将 Telegram 消息接入智能体。 | `` | MIT |
| [yun520-1/deepseek-heartflow](https://github.com/yun520-1/deepseek-heartflow) | DSH 心流/对话节奏类插件，调整交互体验。 | `` | MIT |
| [zetaluolang-cyber/deepseek-harness-phone-remote](https://github.com/zetaluolang-cyber/deepseek-harness-phone-remote) | Remote filesystem/phone bridge for DSH over Tailscale/LAN (device pairing). | `` | MIT |
| [zhouzhencheng07/dsh-tavily-search](https://github.com/zhouzhencheng07/dsh-tavily-search) | Free multi-source web search provider for DSH web seam (keyless Tavily etc.); repo renamed to dsh-free-search. | `` | MIT |
| [zoahdev/dsh-github-intelligence](https://github.com/zoahdev/dsh-github-intelligence) | DSH 开发者情报插件：196+ 只读工具覆盖 GitHub/GitLab/npm/PyPI/ArXiv 等 16+ 生态。 | `` | MIT |

← [Back to README](../../README.md)
