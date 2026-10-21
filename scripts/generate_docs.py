#!/usr/bin/env python3
"""generate_docs.py — regenerate the awesome-dsh-plugins documentation.

Reads data/verified-plugins.csv and:
  1. Writes docs/categories/<id>.md and docs/categories/<id>.en.md — one pair per
     the companion site's 22 categories
     (deepseekharnessplugins.com/plugins/categories). Each page carries a link to
     the matching site category at the top and the FULL list of verified repos in
     that category. The page's h2 title equals the site's SECTION_MAP key
     (merge.ts) so the site's parser can consume the page unchanged.
  2. Rewrites the "Verified directory" region of README.md / README.en.md into a
     compact index: navigation + the top-N most-recently-active repos per category,
     with a "view full list ->" link to the category page.

The CSV `category` slug is mapped onto the 22 site categories via SLUG_MAP.

Usage:
  python3 scripts/generate_docs.py            # write in place
  python3 scripts/generate_docs.py --dry /tmp # write to /tmp (README*.new.md + categories/)
"""
import argparse
import csv
import datetime as dt
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT_DIR = os.path.join(ROOT, "docs", "categories")
SITE = "https://deepseekharnessplugins.com"
TOP_N = 10  # featured rows shown per category inside the README index

# 22 categories in the website's order (id, zh, en). ids == site route params.
CATEGORIES = [
    ("ui-experience",        "界面与体验",            "UI & Experience"),
    ("sessions-messages",    "会话与消息",            "Sessions & Messages"),
    ("utilities",            "其他",                  "Other"),
    ("desktop",              "桌面与应用",            "Desktop & Apps"),
    ("mcp",                  "MCP 与协议",            "MCP & Protocols"),
    ("plugin-tools",         "插件工具",              "Plugin Tooling"),
    ("web-ui",               "Web 界面与前端",        "Web UI & Frontend"),
    ("theme",                "主题与皮肤",            "Themes & Skins"),
    ("security",             "安全与鉴权",            "Security & Auth"),
    ("chat-im",              "聊天与 IM",             "Chat & IM"),
    ("cli",                  "命令行与终端",          "CLI & Terminal"),
    ("voice",                "语音",                  "Voice & Speech"),
    ("lists",                "清单与资源",            "Lists & Resources"),
    ("billing",              "用量与计费",            "Usage & Billing"),
    ("agents-workflows",     "Agent、自动化与工作流", "Agents, Automation & Workflows"),
    ("integrations-sharing", "集成与分享",            "Integrations & Sharing"),
    ("developer-tools",      "开发者工具",            "Developer Tools"),
    ("knowledge-research",   "知识与研究",            "Knowledge & Research"),
    ("media-vision",         "设计、媒体与视觉",      "Design, Media & Vision"),
    ("web-browser",          "网页与浏览器",          "Web & Browser"),
    ("ecosystem-resources",  "生态与资源",            "Ecosystem & Resources"),
    ("fun",                  "纯属好玩",              "Just for Fun"),
]
CAT_IDS = [c[0] for c in CATEGORIES]

# CSV `category` slug -> site category id
SLUG_MAP = {
    "vision": "media-vision",
    "web_ui": "web-ui",
    "tui": "ui-experience",
    "voice": "voice",
    "fun": "fun",
    "session_chat": "sessions-messages",
    "memory_persona": "sessions-messages",
    "search_browser": "web-browser",
    "data_tools": "knowledge-research",
    "automation": "agents-workflows",
    "communication": "chat-im",
    "remote_device": "desktop",
    "developer_tools": "developer-tools",
    "diagnostics": "plugin-tools",
    "ecosystem": "ecosystem-resources",
    "uncategorized": "utilities",
    "skills": "ecosystem-resources",
    "ui": "ui-experience",
    "other": "utilities",
    "model_gateway": "developer-tools",
    "agent_orchestration": "agents-workflows",
    "cost_observability": "billing",
    "agent-os": "agents-workflows",
    "agent_os": "agents-workflows",
    "knowledge": "knowledge-research",
    "analysis": "knowledge-research",
    "prompt": "developer-tools",
    "security": "security",
    "memory": "knowledge-research",
    "security_audit": "security",
    "web_ui_customization": "web-ui",
    "mcp": "mcp",
    "context_management": "agents-workflows",
    "launcher": "desktop",
    "notifications": "chat-im",
    "developer_skills": "developer-tools",
    "task_management": "agents-workflows",
    "knowledge_management": "knowledge-research",
    "observability": "billing",
    "desktop": "desktop",
    "plugin_diagnostics": "plugin-tools",
    "deterministic_tools": "developer-tools",
    "long_term_memory": "knowledge-research",
    "education": "knowledge-research",
    "prompt_persona": "sessions-messages",
    "browser_automation": "web-browser",
    "game": "fun",
    "response_presentation": "ui-experience",
    "conversation_interface": "chat-im",
    "remote_execution": "desktop",
    "plugin_development_skill": "plugin-tools",
    "desktop_automation": "desktop",
    "developer_panel": "developer-tools",
    "conversation_sharing": "integrations-sharing",
    "computer_use": "desktop",
    "list": "lists",
    "session_diagnostics": "sessions-messages",
    "translation": "knowledge-research",
    "terminal_ui": "cli",
    "agent_memory_orchestration": "agents-workflows",
    "legal": "ecosystem-resources",
    # extra slugs discovered in the data
    "web_search": "web-browser",
    "chat_integration": "chat-im",
    "skill": "ecosystem-resources",
    "developer_tooling": "developer-tools",
    "plan_review": "agents-workflows",
    "sidebar_workbench": "ui-experience",
    "companion_memory": "knowledge-research",
    "qq_meme_sending": "fun",
    "device_bridge": "desktop",
    "web_review": "web-browser",
    "tui_bridge": "ui-experience",
}


# ---- markdown helpers -------------------------------------------------------
def esc(s):
    return (s or "").replace("|", "\\|").replace("\n", " ").strip()


def build_row(r, lang):
    repo = r["repository"]
    cap = esc(r.get("capability"))
    if not cap:
        return None
    install = re.sub(r"\s*\n\s*", "; ", (r.get("install_or_usage") or "")).strip()
    install = esc(install)
    lic = esc(r.get("license"))
    caution = esc(r.get("caution"))
    if "`" in install or re.search(r"see README|见 README", install, re.I):
        inst = install
    else:
        inst = f"`{install}`"
    if lang == "cn":
        lic_txt = "未发现" if lic.lower() in ("not found", "none") else lic
        cell = f"{lic_txt}；{caution}" if caution else lic_txt
    else:
        cell = f"{lic}; {caution}" if caution else lic
    return f"| [{repo}]({r['url']}) | {cap} | {inst} | {cell} |"


def load():
    verified_path = os.path.join(ROOT, "data", "verified-plugins.csv")
    with open(verified_path, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    cap = [r for r in rows if (r.get("capability") or "").strip()]
    seen = {}
    assigned = {cid: [] for cid in CAT_IDS}
    unmapped = []
    for r in cap:
        repo = r["repository"]
        key = repo.lower()
        if key in seen:
            continue
        seen[key] = True
        slug = (r.get("category") or "").strip()
        cid = SLUG_MAP.get(slug)
        if cid is None or cid not in assigned:
            cid = "utilities"
            if slug:
                unmapped.append(slug)
        assigned[cid].append(r)
    # most-recently-active first; stable sort keeps repo name asc as tiebreak
    for cid in assigned:
        assigned[cid].sort(key=lambda r: r["repository"].lower())
        assigned[cid].sort(key=lambda r: r.get("last_activity") or "", reverse=True)

    checked_dates = [
        (r.get("checked_at") or "")[:10]
        for r in cap
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", (r.get("checked_at") or "")[:10])
    ]
    snapshot_date = max(checked_dates, default=dt.date.today().isoformat())

    repositories_path = os.path.join(ROOT, "data", "repositories.csv")
    with open(repositories_path, newline="", encoding="utf-8") as handle:
        repository_rows = list(csv.DictReader(handle))
    repository_keys = [
        (row.get("full_name") or "").strip().lower()
        for row in repository_rows
    ]
    if any(not key for key in repository_keys):
        raise ValueError(f"{repositories_path}: empty full_name")
    if len(repository_keys) != len(set(repository_keys)):
        raise ValueError(f"{repositories_path}: duplicate full_name")

    return assigned, len(seen), unmapped, snapshot_date, len(repository_keys)


# ---- category pages ---------------------------------------------------------
def build_category_doc(cid, zh, en, rows, lang):
    site_url = f"{SITE}/plugins/category/{cid}"
    if lang == "cn":
        # h2 title == EXACT SECTION_MAP key used by the companion site's parser
        # (merge.ts) so the page can be consumed as-is; the EN name lives in the
        # site-link line below.
        title = f"## {zh}"
        link = f"> 对应网站分类：[{zh} · {en}]({site_url})"
        hdr = ("| 插件 | 能力 | 安装或挂载方式 | 许可 / 风险 |",
               "| --- | --- | --- | --- |")
        empty = "> 暂无已核验条目。"
        footer = "← [返回 README](../../README.md)"
    else:
        title = f"## {en}"
        link = f"> Corresponding category on the site: [{en}]({site_url})"
        hdr = ("| Plugin | Capability | Install or mount | License / Risk |",
               "| --- | --- | --- | --- |")
        empty = "> No verified entries yet."
        footer = "← [Back to README](../../README.md)"
    body = [title, "", link, "", hdr[0], hdr[1]]
    if rows:
        for r in rows:
            row = build_row(r, lang)
            if row:
                body.append(row)
    else:
        body.append("")
        body.append(empty)
    body.append("")
    body.append(footer)
    return "\n".join(body) + "\n"


def write_category_docs(assigned, dry, outdir):
    for cid, zh, en in CATEGORIES:
        rows = assigned.get(cid, [])
        cn = build_category_doc(cid, zh, en, rows, "cn")
        en = build_category_doc(cid, zh, en, rows, "en")
        if dry:
            d = os.path.join(outdir, "categories")
            os.makedirs(d, exist_ok=True)
            open(os.path.join(d, f"{cid}.md"), "w", encoding="utf-8").write(cn)
            open(os.path.join(d, f"{cid}.en.md"), "w", encoding="utf-8").write(en)
        else:
            os.makedirs(CAT_DIR, exist_ok=True)
            open(os.path.join(CAT_DIR, f"{cid}.md"), "w", encoding="utf-8").write(cn)
            open(os.path.join(CAT_DIR, f"{cid}.en.md"), "w", encoding="utf-8").write(en)


# ---- README index -----------------------------------------------------------
def build_nav(lang, catalog_total):
    if lang == "cn":
        nav = [
            "| 导航 | 内容 |",
            "| --- | --- |",
            f"| [全量聚合目录](#全量聚合目录) | **{catalog_total} 个** DSH 相关仓库的完整聚合（含未审核候选）；[审计日志](data/audit-results.csv) |",
        ]
        cats = " · ".join(f"[{zh}](docs/categories/{cid}.md)" for cid, zh, _ in CATEGORIES)
        nav.append(f"| 分类目录（完整清单） | {cats} |")
        nav += [
            "| [官方内置能力](#官方内置能力不是社区插件) | 随 DSH 源码发行的官方运行时构件 |",
            "| [相关项目与观察名单](#相关项目与观察名单不计入主目录) | 相关但并非已核验原生插件的项目 |",
            "| [安装与安全](#安装与安全) | 安装惯例、权限提示与审计建议 |",
            "| [贡献与维护](#贡献与维护) | 新项目的提交格式与审核门槛 |",
        ]
    else:
        nav = [
            "| Navigation | Purpose |",
            "| --- | --- |",
            f"| [Full aggregated catalog](#full-aggregated-catalog) | **All {catalog_total:,}** DSH-related repositories, including unreviewed candidates; [audit log](data/audit-results.csv) |",
        ]
        cats = " · ".join(f"[{en}](docs/categories/{cid}.en.md)" for cid, _, en in CATEGORIES)
        nav.append(f"| Category pages (full listings) | {cats} |")
        nav += [
            "| [Built-in DSH components](#official-built-in-capabilities-not-community-plugins) | Runtime components shipped in the official source tree |",
            "| [Watchlist and related projects](#watchlist-and-related-projects) | Related but unverified or non-loadable projects |",
            "| [Safety](#installation-and-safety) | Permission-aware installation guidance |",
            "| [Contributing and maintenance](#contributing-and-maintenance) | Submission format and review bar for new projects |",
        ]
    return "\n".join(nav)


def regen_readme(text, lang, assigned, total, unmapped, snapshot_date,
                 catalog_total):
    if lang == "cn":
        heading = "## 已核验插件目录"
        intro = ("下列条目已核验至少一个原生特征：可复现的 `dsh plugin` 安装命令、"
                 "`dsh.bundle` / `cordis.patch.yml` 声明，或 DSH/Cordis 可挂载的 `apply` 入口。"
                 "**“已核验”不代表作者、代码质量或安全性背书。**\n\n"
                 "> 每个分类的**完整清单**已拆到 [`docs/categories/`](docs/categories/) 下的独立页面，"
                 "顶部均附有对应网站分类的链接；下方仅展示每类最近活跃的若干条目。\n")
        hdr = ("| 插件 | 能力 | 安装或挂载方式 | 许可 / 风险 |",
               "| --- | --- | --- | --- |")
        empty = "> 暂无已核验条目。"
        tail = lambda n, cid: (f"> 该分类共 **{n}** 个已核验条目，"
                               f"[查看完整清单 →](docs/categories/{cid}.md)")
    else:
        heading = "## Verified directory"
        intro = ("An entry in this section has at least one verified native signal: a reproducible "
                 "`dsh plugin` command, a `dsh.bundle` / `cordis.patch.yml` declaration, or a "
                 "DSH-compatible Cordis `apply` entry. **Verified does not mean audited, endorsed, "
                 "safe, or stable.**\n\n"
                 "> The **full listing** for each category lives in its own page under "
                 "[`docs/categories/`](docs/categories/), each linked to the matching site category "
                 "at the top; below we show only the most recently active entries per category.\n")
        hdr = ("| Plugin | Capability | Install or mount | License / Risk |",
               "| --- | --- | --- | --- |")
        empty = "> No verified entries yet."
        tail = lambda n, cid: (f"> This category has **{n}** verified entries, "
                               f"[view the full list →](docs/categories/{cid}.en.md)")

    blocks = [
        heading, "", intro.rstrip("\n"), "",
        build_nav(lang, catalog_total), "",
    ]
    for cid, zh, en in CATEGORIES:
        name = zh if lang == "cn" else en
        rows = assigned.get(cid, [])
        block = [f"### {name}", ""]
        if rows:
            block += [hdr[0], hdr[1]]
            for r in rows[:TOP_N]:
                row = build_row(r, lang)
                if row:
                    block.append(row)
            block.append("")
            block.append(tail(len(rows), cid))
        else:
            block.append(empty)
        blocks.append("\n".join(block))

    new_body = "\n\n".join(blocks) + "\n"

    # ---- splice: replace region between start/end markers ----
    if lang == "cn":
        start_marker = "## 已核验插件目录"
        end_marker = "## 官方内置能力（不是社区插件）"
    else:
        start_marker = "## Verified directory"
        end_marker = "## Official built-in capabilities (not community plugins)"

    lines = text.split("\n")
    si = next((i for i, l in enumerate(lines) if l.strip() == start_marker), None)
    ei = next((i for i, l in enumerate(lines) if l.strip() == end_marker), None)
    if si is None or ei is None:
        raise SystemExit(f"[{lang}] markers not found: start={si} end={ei}")
    lines[si:ei] = [new_body.rstrip("\n")]
    text = "\n".join(lines)

    # ---- badge + snapshot paragraph ----
    text = re.sub(r"catalog-\d+", f"catalog-{catalog_total}", text)
    text = re.sub(r"verified-\d+", f"verified-{total}", text)
    if lang == "cn":
        text = re.sub(
            r"\*\*[\d,]+ 个\*\* DSH 相关仓库",
            f"**{catalog_total} 个** DSH 相关仓库",
            text,
        )
        new_snap = (f"**快照日期：{snapshot_date}。** 本版主目录收录 **{total} 个**"
                    "经源码或安装清单核验的插件与 Skill，按 22 个能力分类组织（与配套网站 "
                    "[deepseekharnessplugins.com](https://deepseekharnessplugins.com) 同构）；"
                    "完整清单已拆分到 [`docs/categories/`](docs/categories/) 的 22 个分类页面。"
                    f"同时提供 **全量聚合目录 [`CATALOG.md`](CATALOG.md)（{catalog_total} 个仓库）**，合并 GitHub 搜索与多个社区目录去重后得到。"
                    "**聚合 ≠ 可装载、可兼容、可安全运行**；只有本目录核验子集进入主目录，证据见 "
                    "[data/verified-plugins.csv](data/verified-plugins.csv) 与 [data/audit-results.csv](data/audit-results.csv)。[3]")
    else:
        text = re.sub(
            r"\*\*All [\d,]+\*\* DSH-related repositories",
            f"**All {catalog_total:,}** DSH-related repositories",
            text,
        )
        new_snap = (f"**Snapshot: {snapshot_date}.** This edition's main directory includes "
                    f"**{total} verified plugins and skills whose source or install manifests were inspected**, "
                    "organized into 22 capability categories (aligned with the companion site "
                    "[deepseekharnessplugins.com](https://deepseekharnessplugins.com)); the full listing is split "
                    "into 22 category pages under [`docs/categories/`](docs/categories/). Plus a **full aggregated "
                    f"catalog — [`CATALOG.md`](CATALOG.md), {catalog_total:,} repositories** — merged and deduplicated from GitHub "
                    "search and several community directories. **Aggregation is not an installation, compatibility, "
                    "maintenance, or security certification**; only the verified subset enters the main directory, with "
                    "evidence in [data/verified-plugins.csv](data/verified-plugins.csv) and "
                    "[data/audit-results.csv](data/audit-results.csv).[3]")
    text = re.sub(r"^\*\*快照日期：.*$", new_snap, text, flags=re.M, count=1)
    text = re.sub(r"^\*\*Snapshot:.*$", new_snap, text, flags=re.M, count=1)

    return text, total, unmapped


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry", metavar="OUTPUT_DIR",
        help="write README previews and category pages outside the repository",
    )
    parser.add_argument(
        "--strict", action="store_true",
        help="fail before writing when any verified category is unmapped",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    dry = args.dry is not None
    outdir = args.dry
    assigned, total, unmapped, snapshot_date, catalog_total = load()
    if args.strict and unmapped:
        print(f"[error] unmapped categories: {sorted(set(unmapped))}")
        return 2
    if dry:
        os.makedirs(outdir, exist_ok=True)
    write_category_docs(assigned, dry, outdir)
    for lang, fn in [("cn", "README.md"), ("en", "README.en.md")]:
        path = os.path.join(ROOT, fn)
        text = open(path, encoding="utf-8").read()
        new_text, count, unm = regen_readme(
            text, lang, assigned, total, unmapped, snapshot_date, catalog_total
        )
        if dry:
            out = os.path.join(outdir, fn.replace(".md", ".new.md"))
            open(out, "w", encoding="utf-8").write(new_text)
            print(f"[{lang}] {fn}: verified={count}, unmapped={sorted(set(unm))}, -> {out}")
        else:
            open(path, "w", encoding="utf-8").write(new_text)
            print(f"[{lang}] {fn}: written, verified={count}, unmapped={sorted(set(unm))}")
    print(
        f"[done] category pages: {len(CATEGORIES) * 2} files, "
        f"verified total={total}, catalog total={catalog_total}, "
        f"snapshot={snapshot_date}, unmapped={sorted(set(unmapped))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
