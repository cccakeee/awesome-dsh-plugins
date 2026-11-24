## Lists & Resources

> Corresponding category on the site: [Lists & Resources](https://deepseekharnessplugins.com/plugins/category/lists)

| Plugin | Capability | Install or mount | License / Risk |
| --- | --- | --- | --- |
| [bruc3van/dsh-market-pro](https://github.com/bruc3van/dsh-market-pro) | Browse, install and batch-update DSH plugins, install curated skills and MCP servers, and let the agent pick and audit them from chat with /market-pro. | `dsh plugin --profile web add dsh-market-pro  (npm 1.15.2), or install dsh-market-pro from DSH's Plugins page; then open Plugins -> Market Pro, or type /market-pro in a session.` | MIT; Catalog/market data is third-party metadata (the plugin mitigates prompt injection with untrusted-data boundaries); the same author publishes awesome-dsh-plugin-pro and other market/desktop repos, so 'curated/verified' counts are its own curation. Ships no repo-level SKILL.md, so the skill path is embedded rather than DSH-discoverable from the repo. |
| [polang233/dsh-plugin-index](https://github.com/polang233/dsh-plugin-index) | Add the dshopen.org community index to DSH Discover so users can browse and install community plugins. | `dsh plugin --profile desktop add "git+https://github.com/polang233/dsh-plugin-index.git#main&path:/packages/dsh-open-market"` | GPL-3.0-only; The root package is private and the npm registry has no dsh-open-market release; use the documented Git path. Only packages/dsh-open-market is the loadable DSH plugin, while the rest of the repository builds the aggregate market/index. |
| [losebird/dsh-plugin-market](https://github.com/losebird/dsh-plugin-market) | Browse marketplace entries and install or remove them from the DSH interface. | `dsh plugin --profile web add @ace-zone/dsh-market` | Not found; Review each marketplace source before installing; install actions enable package build scripts and execute external package code. |
| [baosfeng/my-dsh-plugins](https://github.com/baosfeng/my-dsh-plugins) | Install individual panels, memory, rendering, workflow, and integration plugins from one repository. | `dsh plugin --profile web add dsh-file-activity --trust-lockfile` | MIT; The root repository is not a single plugin bundle; install packages individually. The cited command installs only dsh-file-activity; high risk reflects optional remote-control plugins in the collection. |
| [Eray114514/dsh-find-plugins](https://github.com/Eray114514/dsh-find-plugins) | Lets an agent find and compare DSH plugins from multiple community catalogs and live sources. | `dsh plugin --profile <profile> add dsh-find-plugins; restart DSH.` | MIT; Results aggregate third-party plugin listings; inspect a selected repository before installing it. |
| [bruc3van/dsh-desktop-safe-market](https://github.com/bruc3van/dsh-desktop-safe-market) | 先审后装插件市场 | `` | MIT |
| [qichuang321/dsh-plugin-browser](https://github.com/qichuang321/dsh-plugin-browser) | 插件市场入口+运维面板 | `` | MIT |

← [Back to README](../../README.md)
