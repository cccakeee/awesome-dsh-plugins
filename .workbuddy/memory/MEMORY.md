# Project Memory — dsh-plugins curation

## Reusable conventions for the dsh-topic-curator workflow

- **Topic size scaling (CRITICAL):** the `dsh-plugin` GitHub topic had ~7,900 repos on
  2026-08-19, **10,554 in the morning of 2026-08-22, and 10,612 by night** — it is exploding
  (9923 of those repos were `pushed` in 2026-08 alone). Do NOT use WebFetch pagination for
  discovery — it needs 260+ pages. Use the authenticated `gh` Search API instead:
  `gh api "search/repositories?q=topic:dsh-plugin&sort=stars&order=desc&per_page=100"`
  (top 1000 by stars = 10 pages). Requires `gh` network access → run Bash with
  `dangerouslyDisableSandbox: true` (the sandbox blocks `gh api` network calls).
  **GOTCHA:** the Search API caps a single query at 1,000 results (`page=11` → HTTP 422
  "Only the first 1000 search results are available"); ~9,500 tail repos are never seen by a
  plain `sort=stars` query. **SOLVED by `scripts/full_topic_scan.py`** (in the
  dsh-topic-curator skill dir): partitions the topic into disjoint sub-queries — star tiers for
  `stars>10` (6 tiers, all <1000) + the `stars:<=10` remainder split by `created:` year
  through 2024 and month from 2025 onward, with overflowing periods split into days and
  hours — so every leaf is fully retrievable.
  **GOTCHA (measured 2026-08-23):** day-level `created:A..B` is END-INCLUSIVE
  (`created:2026-08-13..2026-08-14` = 522+1702 = both days, exact). Query a single day as
  `D..D`, a month as single-sided `YYYY-MM`, hours as adjacent buckets `T00..T01, T01..T02, …`
  (boundary overlap absorbed by dedupe). `pushed:` has no hour precision and `stars:`
  sub-filters are ignored in compound queries — `created:` is the only reliable dimension.
  Dry-run prints the partition plan; `--execute` fetches all (rate-limited, ~9 min). Outputs
  `/tmp/dsh_topic_full.json` (rich) + `/tmp/dsh_topic_repos.json` (diff_topic.py-compatible).
- **Diff:** `python3 .workbuddy/skills/dsh-topic-curator/scripts/diff_topic.py /tmp/topic_repos.json --catalog-dir data --star-floor 10`
  writes `/tmp/dsh_new_repos.json` with `above_floor` / `skipped` arrays of `[name, stars]`.
  Floor rule = skip stars ≤ 10 ("10 个 star 内的先不处理").
- **Verdict vocabulary (gotcha):** agent-prompt.md uses
  `verified/skill/watchlist/related/excluded`; `merge_audit_verdicts.py` expects
  `verified_plugin/verified_skill/rejected/watchlist`. Unify by setting `verdict` == `review_status`
  to one of `verified_plugin | verified_skill | related | rejected | watchlist`.
  Only `verified_plugin`/`verified_skill` get promoted into `verified-plugins.csv`.
- **Category enum (gotcha):** the CSV `category` column has drifted to ~66 slugs. The canonical doc
  generator is now `scripts/generate_docs.py`, which reads `data/verified-plugins.csv` and maps each
  `category` slug → one of the companion site's **22 categories** via `SLUG_MAP`. The 22 ids are the
  site's route params: ui-experience, sessions-messages, utilities, desktop, mcp, plugin-tools, web-ui,
  theme, security, chat-im, cli, voice, lists, billing, agents-workflows, integrations-sharing,
  developer-tools, knowledge-research, media-vision, web-browser, ecosystem-resources, fun. Unmapped
  slugs fall back to `utilities`. (The obsolete `insert_verified_into_readme.py` and
  `regen_readme_sections.py` are deleted — do not use them.)
- **README is now an index:** README.md / README.en.md are thin indexes (nav + top-10 per category,
  <600 lines) that point into `docs/categories/`. The full listing lives in `docs/categories/` — 44
  pages (22 category ids × CN/EN: `<id>.md` / `<id>.en.md`). Each page's top link points to the
  matching site category: `https://deepseekharnessplugins.com/plugins/category/<id>`. Page titles are
  **h2 with the plain category name** (CN `## 界面与体验`, EN `## UI & Experience`) — chosen to equal
  the site's `SECTION_MAP` keys so the site parser can consume the pages unchanged; the EN/CN name
  pair lives in the site-link line below the title.
- **Regenerate docs:** `python3 scripts/generate_docs.py` (rewrites the README index + all 44 category
  pages, updates nav/badge/snapshot/idempotent w.r.t. CSV). Re-run after any `verified-plugins.csv`
  change.
- **CSV append formats:**
  - `repositories.csv` columns: full_name,html_url,description,category,stars,license,language,
    topics,pushed_at,homepage,verified,sources. `topics` = pipe-separated (`a|b|c`),
    `verified` = `True`/`False`, `pushed_at` = ISO `2026-08-19T00:00:00Z`,
    `sources` = `topic-candidate-snapshot|verified`. Add ONLY `main_dir==true` (loadable) plugins.
  - `dsh-plugin-topic-candidates.csv` columns: repository,topic,review_status.
    `topic` = `dsh-plugin`; add ALL new repos with their `review_status`.
- **Merge order:** validate scan summary and review set → `merge_audit_verdicts.py --topic-repos ...`
  (backup plus atomic update of all four CSVs) → `aggregate.py --render-only` →
  `generate_docs.py --strict` (README index + 44 category pages).
- **Website ingestion (adapted 2026-08-19):** deepseekharnessplugins.com's `OUR_SOURCE` IS our own
  repo. Since README became an index, the site's `sync-plugins.ts` now fetches the **22
  `docs/categories/<id>.md` pages** (CN, raw.githubusercontent.com/cccakeee/awesome-dsh-plugins/main/docs/categories/<id>.md),
  concatenates them, and feeds the same `parseAwesomeReadme`. `SECTION_MAP` (site's
  `src/modules/plugins/merge.ts`) covers all 22 CN + EN titles. Verified: all 1550 curated repos
  land in `plugins.snapshot.json` (8169 plugins total), shrink guard passes.
- **GOTCHA (parser case):** the site parser lowercases every heading (`toLowerCase()`), and JS
  object keys are case-sensitive → any ASCII inside a SECTION_MAP key must be lowercase
  (`web 界面与前端`, `mcp 与协议`, `聊天与 im`, `agent、自动化与工作流` — NOT `Web`/`MCP`/`IM`/`Agent`).
  Mixed-case keys silently drop whole pages (lost 473 entries on first sync attempt).
- **Automation publishing:** only commit and push after all gates pass and the data refresh has
  real changes. Infrastructure repairs must be committed to `origin/main` before the next
  scheduled worktree is created.

## Run log

- **2026-08-30 (weekly / Sunday, Asia/Shanghai):** full scan coverage passed with
  `coverage_ok=true`, `planned/completed=43/43`, `failures=[]`, `over_cap=[]`, and 12,661
  unique repositories (`count_queries=170`, `fetch_queries=142`, `leaves=142`). Star floor was
  10; `above_floor=20`, `skipped=10,445`. Verdicts: 15 `verified_plugin`, 1 `verified_skill`,
  1 `watchlist`, 3 `related`, 0 `rejected`. Atomic merge added 16 rows to
  `repositories.csv`, 20 to `dsh-plugin-topic-candidates.csv`, 20 to `audit-results.csv`, and
  16 to `verified-plugins.csv`. Backup: `/tmp/dsh-curator-backup-wxztnda4`. Verification passed:
  `aggregate.py --render-only`, `generate_docs.py --strict` (`unmapped=[]`), 9 unittest cases,
  py_compile, `git diff --check`, and case-insensitive duplicate-key checks for all four tables.
- **2026-09-01 (daily / Tuesday, Asia/Shanghai; run at 02:48 +0800):** actionable scan coverage
  passed with `coverage_ok=true`, `planned/completed=6/6`, `count_queries=6`, `fetch_queries=6`,
  `leaves=6`, `failures=[]`, `over_cap=[]`, and 889 unique repositories. Star floor was 10;
  `above_floor=29`, `skipped=0`. Verdicts: 20 `verified_plugin`, 1 `verified_skill`, 1
  `watchlist`, 6 `related`, 1 `rejected`. Atomic merge added 21 rows to `repositories.csv`,
  29 to `dsh-plugin-topic-candidates.csv`, 29 to `audit-results.csv`, and 21 to
  `verified-plugins.csv`. Backup: `/tmp/dsh-curator-backup-ezpsm5fj`. Verification passed:
  `aggregate.py --render-only`, `generate_docs.py --strict` (`unmapped=[]`), 9 unittest cases,
  py_compile, `git diff --check`, and case-insensitive duplicate-key checks for all four tables.
- **2026-09-02 (daily / Wednesday, Asia/Shanghai; run at 02:04 +0800):** actionable scan coverage
  passed with `coverage_ok=true`, `planned/completed=6/6`, `count_queries=6`, `fetch_queries=6`,
  `leaves=6`, `failures=[]`, `over_cap=[]`, and 902 unique repositories. Star floor was 10;
  `above_floor=14`, `skipped=0`. Verdicts: 8 `verified_plugin`, 0 `verified_skill`, 0
  `watchlist`, 5 `related`, 1 `rejected`. Atomic merge added 8 rows to `repositories.csv`,
  14 to `dsh-plugin-topic-candidates.csv`, 14 to `audit-results.csv`, and 8 to
  `verified-plugins.csv`. Backup: `/tmp/dsh-curator-backup-mqxtb2ub`. An older temporary
  batch 4/5 pair was isolated at `/tmp/dsh-topic-curator-stale.P6rWS1` after the first merge
  attempt; the rerun passed the exact-set gate. Verification passed: `aggregate.py --render-only`,
  `generate_docs.py --strict` (`unmapped=[]`), 9 unittest cases, py_compile, `git diff --check`,
  and case-insensitive duplicate-key checks for all four tables.
- **2026-09-03 (daily / Thursday, Asia/Shanghai; run at 02:40 +0800):** actionable scan coverage
  passed with `coverage_ok=true`, `planned/completed=6/6`, `count_queries=6`, `fetch_queries=6`,
  `leaves=6`, `failures=[]`, `over_cap=[]`, and 920 unique repositories. Star floor was 10;
  `above_floor=17`, `skipped=0`. Verdicts: 8 `verified_plugin`, 2 `verified_skill`, 1
  `watchlist`, 5 `related`, 1 `rejected`. Atomic merge added 10 rows to `repositories.csv`,
  17 to `dsh-plugin-topic-candidates.csv`, 17 to `audit-results.csv`, and 10 to
  `verified-plugins.csv`. Backup: `/tmp/dsh-curator-backup-ftqj_4n8`. Verification passed:
  exact review-set/schema validation, `aggregate.py --render-only`, `generate_docs.py --strict`
  (`unmapped=[]`), 9 unittest cases, py_compile, `git diff --check`, and case-insensitive
  duplicate-key checks for all four tables.
- **2026-09-05 (daily / Saturday, Asia/Shanghai):** actionable refresh passed with
  `coverage_ok=true`, `planned/completed=6/6`, `count_queries=6`, `fetch_queries=6`,
  `leaves=6`, `failures=[]`, `over_cap=[]`, and 955 unique repositories. Star floor was 10;
  `above_floor=13`, `skipped=0`. Verdicts: 10 `verified_plugin`, 1 `verified_skill`, 0
  `watchlist`, 2 `related`, 0 `rejected`. Atomic merge added 11 rows to `repositories.csv`, 13
  to `dsh-plugin-topic-candidates.csv`, 13 to `audit-results.csv`, and 11 to
  `verified-plugins.csv`. Backup: `/tmp/dsh-curator-backup-9uc1ckz8`. An unexpected stale
  `/tmp/dsh_review_batch_4.json` was preserved at `/tmp/dsh-topic-curator-stale.m1CO6L`
  before the successful exact-set merge. Pre-commit verification passed:
  `aggregate.py --render-only`, `generate_docs.py --strict` (`unmapped=[]`), 9 unittest cases,
  py_compile, `git diff --check`, and case-insensitive duplicate-key checks for all four tables;
  post-commit synchronization recheck also passed.
- **2026-09-04 (daily / Friday, Asia/Shanghai; run at 02:03 +0800):** actionable scan coverage
  passed with `coverage_ok=true`, `planned/completed=6/6`, `count_queries=6`, `fetch_queries=6`,
  `leaves=6`, `failures=[]`, `over_cap=[]`, and 939 unique repositories. Star floor was 10;
  `above_floor=19`, `skipped=0`. Verdicts: 16 `verified_plugin`, 0 `verified_skill`, 2
  `watchlist`, 0 `related`, 1 `rejected`. Atomic merge added 16 rows to `repositories.csv`,
  19 to `dsh-plugin-topic-candidates.csv`, 19 to `audit-results.csv`, and 16 to
  `verified-plugins.csv`. Backup: `/tmp/dsh-curator-backup-2_gc709v`. Verification passed:
  exact review-set/schema validation, `aggregate.py --render-only`, `generate_docs.py --strict`
  (`unmapped=[]`), 9 unittest cases, py_compile, `git diff --check`, and case-insensitive
  duplicate-key checks for all four tables.
