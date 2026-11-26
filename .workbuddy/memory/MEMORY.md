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
- **2026-09-05 (daily / Saturday, Asia/Shanghai):** actionable scan coverage passed with
  `coverage_ok=true`, `planned/completed=6/6`, `count_queries=6`, `fetch_queries=6`,
  `leaves=6`, `failures=[]`, `over_cap=[]`, and 968 unique repositories. Star floor was 10;
  `above_floor=11`, `skipped=0`. Verdicts: 11 `verified_plugin`, 0 `verified_skill`, 0
  `watchlist`, 0 `related`, 0 `rejected`. Atomic merge added 11 rows to `repositories.csv`,
  11 to `dsh-plugin-topic-candidates.csv`, 11 to `audit-results.csv`, and 11 to
  `verified-plugins.csv`. Backup: `/tmp/dsh-curator-backup-076xblkx`. Stale
  `/tmp/dsh_review_batch_3.json` was preserved at `/tmp/dsh-topic-curator-stale.9xDzDW/`.
  Verification passed: exact review-set/schema validation, `aggregate.py --render-only`,
  `generate_docs.py --strict` (`unmapped=[]`), 9 unittest cases, py_compile,
  `git diff --check`, and case-insensitive duplicate-key checks for all four tables. The
  pre-existing `data/README.md` change (working-tree hash
  `7ce1553dc72c8a03e2c284034b0a93f2c9388f12`) and existing stash were preserved; the
  `.workbuddy/automations/` directory was not read, staged, committed, or pushed.

- **2026-09-07 (daily / Monday, Asia/Shanghai; run at 02:06 +0800):** actionable scan coverage
  passed with `coverage_ok=true`, `planned/completed=6/6`, `count_queries=6`, `fetch_queries=6`,
  `leaves=6`, `failures=[]`, `over_cap=[]`, and 991 unique repositories. Star floor was 10;
  `above_floor=19`, `skipped=0`. Verdicts: 18 `verified_plugin`, 1 `verified_skill`, 0
  `watchlist`, 0 `related`, 0 `rejected`. Atomic merge added 19 rows to each of
  `repositories.csv`, `dsh-plugin-topic-candidates.csv`, `audit-results.csv`, and
  `verified-plugins.csv`. Backup: `/tmp/dsh-curator-backup-ljjj5d0b`. Verification passed:
  `aggregate.py --render-only`, `generate_docs.py --strict` (`unmapped=[]`, 44 category pages),
  9 unittest cases, py_compile, `git diff --check`, and case-insensitive duplicate-key checks
  for all four tables. The pre-existing `data/README.md` change (working-tree hash
  `7ce1553dc72c8a03e2c284034b0a93f2c9388f12`) and existing stash
  `bbf884d2e65f1be852a841e5ca6f5e517d7f583c` were preserved; `.workbuddy/automations/` was
  not read, staged, committed, or pushed.
- **2026-09-11 (manual daily / Friday, Asia/Shanghai; run at 00:11 +0800):** actionable scan
  coverage passed with `coverage_ok=true`, `planned/completed=6/6`, `count_queries=6`,
  `fetch_queries=6`, `leaves=6`, `failures=[]`, `over_cap=[]`, and 1,030 unique repositories.
  Star floor was 10; `above_floor=22`, `skipped=0`. Verdicts: 18 `verified_plugin`, 0
  `verified_skill`, 0 `watchlist`, 3 `related`, and 1 `rejected`. Atomic merge added 18 rows
  to `repositories.csv`, 22 to `dsh-plugin-topic-candidates.csv`, 22 to `audit-results.csv`,
  and 18 to `verified-plugins.csv`. Backup: `/tmp/dsh-curator-backup-qmjgl5w_`; stale review
  files were isolated at `/tmp/dsh-topic-curator-stale.W5kUvy`. Verification passed: exact
  review-set/schema validation, `aggregate.py --render-only`, `generate_docs.py --strict`
  (`unmapped=[]`, 44 category pages, 1,883 verified entries, 2,677 catalog entries), 9 unittest
  cases, py_compile, `git diff --check`, and case-insensitive duplicate-key checks for all four
  tables. The pre-existing `data/README.md` change (working-tree hash
  `7ce1553dc72c8a03e2c284034b0a93f2c9388f12`) and existing stash
  `bbf884d2e65f1be852a841e5ca6f5e517d7f583c` were preserved; `.workbuddy/automations/` was
  not staged, committed, or pushed.
- **2026-09-10 (daily / Thursday, Asia/Shanghai):** actionable scan coverage passed with
  `coverage_ok=true`, `planned/completed=6/6`, `count_queries=6`, `fetch_queries=6`,
  `leaves=6`, `failures=[]`, `over_cap=[]`, and 1,030 unique repositories. Star floor was 10;
  `above_floor=1`, `skipped=0` (`dushaobindoudou/dsh-freeroute`, 11 stars). The single review
  batch passed exact repository-set, 20-field schema, enum, timestamp, and verdict/main-directory
  checks; verdicts were 1 `verified_plugin`, 0 `verified_skill`, 0 `watchlist`, 0 `related`, and
  0 `rejected`. Atomic merge added 1 row to each of `repositories.csv`,
  `dsh-plugin-topic-candidates.csv`, `audit-results.csv`, and `verified-plugins.csv`. Backup:
  `/tmp/dsh-curator-backup-t193y462`. Documentation verification passed:
  `aggregate.py --render-only`, `generate_docs.py --strict` (`unmapped=[]`, 44 category pages,
  1,884 verified entries, 2,678 catalog entries), 9 unittest cases, py_compile,
  `git diff --check`, and case-insensitive duplicate-key checks for all four tables. The
  pre-existing `data/README.md` was restored byte-for-byte with hash
  `e32d1aae9ab46094030d4224175958671b81838caf790cb4b0fb19cbd9faac19`; stash
  `dsh-topic-curator-2026-09-10-preexisting-data-readme` and the historical stash remain
  preserved. The `.workbuddy/automations/` directory was not read, staged, committed, or pushed.

- **2026-09-11 (daily / Friday, applicable task date; scan window reported 2026-09-12 02:02-02:03 +0800):**
  Actionable scan coverage passed with `coverage_ok=true`, `planned/completed=6/6`,
  `count_queries=6`, `fetch_queries=6`, `leaves=6`, `failures=[]`, `over_cap=[]`, and 1,042
  unique repositories. Star floor was 10; `above_floor=14`, `skipped=0`. Three review batches
  passed exact-set/schema validation for all 14 repositories: 12 `verified_plugin`, 0
  `verified_skill`, 0 `watchlist`, 2 `related`, and 0 `rejected`. Atomic merge added 12 rows
  to `repositories.csv`, 14 to `dsh-plugin-topic-candidates.csv`, 14 to `audit-results.csv`,
  and 12 to `verified-plugins.csv`. Backup: `/tmp/dsh-curator-backup-lvuyph9o`; stale prior
  review files were preserved at `/tmp/dsh-topic-curator-stale.Ky9Agw`. Documentation generation
  passed: `aggregate.py --render-only`, `generate_docs.py --strict` (`unmapped=[]`, 44 category
  pages, 1,896 verified entries, 2,690 catalog entries). Nine unittest cases, py_compile,
  `git diff --check`, and case-insensitive duplicate-key checks for all four tables passed.
  The pre-existing `data/README.md` remained byte-for-byte unchanged with hash
  `e32d1aae9ab46094030d4224175958671b81838caf790cb4b0fb19cbd9faac19`; the new stash and
  historical stashes remain preserved. The `.workbuddy/automations/` directory was not read,
  staged, committed, or pushed.
- **2026-09-12 (daily / Saturday; runtime `2026-09-12T18:28:18Z`, host local clock
  `2026-09-13T02:28:18+0800`):** Main checkout preflight passed on `main` after
  `git fetch origin main` and `git rebase origin/main`; the pre-existing
  `data/README.md` was protected byte-for-byte (hash
  `7ce1553dc72c8a03e2c284034b0a93f2c9388f12`) and the existing stashes remained preserved.
  The requested `.workbuddy/skills/dsh-topic-curator` paths that do not exist in this
  checkout were replaced only by their canonical equivalents: `.workbuddy` supplies the
  scan/agent references, while `data/curation-criteria.yaml` and `scripts/{aggregate.py,
  merge_audit_verdicts.py,generate_docs.py}` are authoritative.
  Actionable scan coverage passed with `coverage_ok=true`, `planned/completed=6/6`,
  `count_queries=6`, `fetch_queries=6`, `leaves=6`, `failures=[]`, `over_cap=[]`, and 1,047
  unique repositories. Star floor was 10; `above_floor=6`, `skipped=0`:
  `reactive-resume/reactive-resume`, `yinnho/aginxbrowser`, `a86582751/dsh-nexttavern`,
  `zaizaizhao/dsh-branchmark`, `00080000/dsh-project-memory`, and
  `Zoria-Lind/dsh-token-optimizer`.
  Three exact two-repository review batches were dispatched. Batch 1 and Batch 3 passed;
  Batch 2 produced no file and was completed by the main agent from GitHub metadata,
  README, package manifests, patch files, and concrete load paths. An old temporary review
  set was preserved at `/tmp/dsh-topic-curator-stale.JgdcHP`; all six current reviews passed
  exact-set/20-field/schema checks and were `verified_plugin` (`reactive-resume`'s live API
  star count was 42,528 versus the scan input's 42,527 and the difference was recorded in
  evidence). Atomic merge added 6 rows to each of `repositories.csv`,
  `dsh-plugin-topic-candidates.csv`, `audit-results.csv`, and `verified-plugins.csv`;
  backup `/tmp/dsh-curator-backup-tozf1l11`.
  `aggregate.py --render-only` passed with 2,696 catalog rows and 1,564 repository verified
  flags; `generate_docs.py --strict` passed with 1,902 verified entries, 44 category pages,
  snapshot `2026-09-12`, and `unmapped=[]`. Nine unittest cases, py_compile,
  `git diff --check`, and case-insensitive primary-key checks passed. The project
  `.workbuddy/automations/` directory was not read, staged, committed, or pushed.
- **2026-09-16 (daily / Wednesday, Asia/Shanghai; run completed at 02:26 +0800):** Main
  checkout preflight passed on `main`; `HEAD` and `origin/main` were synchronized before
  and after the scan. The pre-existing `data/README.md` remained byte-for-byte unchanged
  with SHA-256 `e32d1aae9ab46094030d4224175958671b81838caf790cb4b0fb19cbd9faac19`; existing
  stashes were preserved, and `.workbuddy/automations/` was not read, staged, committed,
  or pushed. Actionable scan coverage passed with `coverage_ok=true`, `planned/completed=6/6`,
  `count_queries=6`, `fetch_queries=6`, `leaves=6`, `failures=[]`, `over_cap=[]`, and 1,067
  unique repositories. Star floor was 10; `above_floor=8`, `skipped=0`:
  `KaichenCurry/dsh-design-mode`, `wushi2333/dsh-computer-use_codex-style`,
  `claudejaune/OmaSeek`, `yan-mc/dsh-normify`, `nullptr-DZF/dsh-academic-research-skills`,
  `Clearailhc/clearai-dsh`, `KYinCode/dsh-hot-installer`, and
  `fuzhengwei/walioffice-dsh-plugin`. Two exact four-repository review batches passed
  schema and repository-set checks: 7 `verified_plugin`, 0 `verified_skill`, 0 `watchlist`,
  0 `related`, and 1 `rejected` (`KaichenCurry/dsh-design-mode`, a derived full DSH runtime
  rather than a standalone extension). Atomic merge added 7 rows to `repositories.csv`, 8
  to `dsh-plugin-topic-candidates.csv`, 8 to `audit-results.csv`, and 7 to
  `verified-plugins.csv`; backup `/tmp/dsh-curator-backup-vudf32vm`. Documentation checks
  passed: `aggregate.py --render-only` reported 2,723 catalog rows and 1,591 CSV verified
  flags; `generate_docs.py --strict` reported 1,929 deduplicated verified entries, 44
  category pages, snapshot `2026-09-16`, and `unmapped=[]`. Nine unittest cases, py_compile,
  `git diff --check`, and case-insensitive primary-key checks passed. Catalog commit
  `c33ae1f587a182b8f1cd9ca7cb379734133b179f` and memory-only follow-up commit
  `aee7878` were pushed to `origin/main`.

- **2026-09-17 (daily / Thursday, Asia/Shanghai; run completed at 02:32 +0800):** Main
  checkout preflight passed on `main`; `HEAD` and `origin/main` were synchronized. The
  pre-existing `data/README.md` was stashed and restored byte-for-byte with SHA-256
  `7ce1553dc72c8a03e2c284034b0a93f2c9388f12`; all six historical stashes were preserved.
  The protected `.workbuddy/automations/` directory was excluded from stash, not read,
  staged, committed, or pushed. Actionable scan coverage passed with `coverage_ok=true`,
  `planned/completed=6/6`, `count_queries=6`, `fetch_queries=6`, `leaves=6`,
  `failures=[]`, `over_cap=[]`, and 1,079 unique repositories. Star floor was 10;
  `above_floor=12`, `skipped=0`. Two exact six-repository review batches passed the
  repository-set/schema checks: 10 `verified_plugin`, 0 `verified_skill`, 0 `watchlist`,
  2 `related`, and 0 `rejected`. GitHub REST metadata was rate-limited, so the agents
  used GitHub HTML, raw files, codeload snapshots, and Atom feeds as primary evidence.
  Atomic merge added 10 rows to `repositories.csv`, 12 to
  `dsh-plugin-topic-candidates.csv`, 12 to `audit-results.csv`, and 10 to
  `verified-plugins.csv`; backup `/tmp/dsh-curator-backup-cu93px02`. Stale review files
  were preserved at `/tmp/dsh-topic-curator-stale.FgnaA4`. Documentation checks passed:
  `aggregate.py --render-only` reported 2,733 catalog rows and 1,601 repository verified
  flags; `generate_docs.py --strict` reported 1,939 deduplicated verified entries, 44
  category pages, snapshot `2026-09-17`, and `unmapped=[]`. Nine unittest cases,
  py_compile, `git diff --check`, and case-insensitive primary-key checks for all four
  tables passed. Catalog commit `a0700172e2c6db6e0f7bdf2a3b2dc6d07c824ea7` was pushed to
  `origin/main`; this run's final publication state is included in the memory-only follow-up
  commit.

- **2026-09-19 (weekly / Saturday, Asia/Shanghai; run timestamp `2026-09-19T18:45:37Z`):**
  Main checkout preflight passed on `main`; `HEAD` matched `origin/main`, the worktree was
  clean, no new stash was needed, and historical stashes were preserved. The full scan was
  date-pinned to the task date `2026-09-19` because the host clock was one day ahead. Full
  coverage passed with `coverage_ok=true`, `planned/completed=44/44`,
  `count_queries=192`, `fetch_queries=165`, `leaves=165`, `failures=[]`, `over_cap=[]`,
  and 15,454 unique repositories. Star floor was 10; 11 new repositories were above the
  floor, and 8 were deferred because their `pushed_at` converted to `2026-09-19`:
  `dataelement/dsh-desktop`, `loopx-project/loopx`, `slow-stack/dsh-mneme`,
  `myc0576/SmartMoney-Cub`, `qishuilalala/dsh-voice-mode`,
  `PerryLink/dsh-session-sync`, `bainianling/dsh-jailbreak-mode`, and
  `kendu76/dsh-music-player`. The remaining 3 were reviewed from GitHub metadata,
  README, package manifests, patch files, and concrete entry points: 2 `verified_plugin`
  (`xohmai/dsh-session-delete`, `Sivan757/dsh-agent-plugins-market`) and 1 `related`
  (`SheltonLiu-N/nano-cordis`), with 0 `verified_skill`, `watchlist`, or `rejected`.
  A read-only review agent was dispatched but produced no current artifact; stale review
  files were not reused and the main agent completed the bounded review. Atomic merge added
  2 rows to `repositories.csv`, 3 to `dsh-plugin-topic-candidates.csv`, 3 to
  `audit-results.csv`, and 2 to `verified-plugins.csv`; backup
  `/tmp/dsh-curator-backup-6plld4c_`. `aggregate.py --render-only` reported 2,749 catalog
  rows and 1,617 repository verified flags; `generate_docs.py --strict` reported 1,955
  deduplicated verified entries, 44 category pages, snapshot `2026-09-19`, and
  `unmapped=[]`. The exact-set merge dry-run and real merge passed; 9 unittest cases,
  py_compile, `git diff --check`, case-insensitive primary-key checks, and deferred-repo
  absence checks passed. The `.workbuddy/automations/` directory was not read, staged,
  committed, or pushed.

- **2026-09-21 (daily / Monday, Asia/Shanghai; host scan window `2026-09-22 02:04-02:05 +0800`):**
  Main checkout preflight passed on `main`; `HEAD` matched `origin/main`, the worktree was
  clean, no new stash was needed, and all seven historical stashes were preserved. The
  actionable scan passed with `coverage_ok=true`, `planned/completed=6/6`, `count_queries=6`,
  `fetch_queries=6`, `leaves=6`, `failures=[]`, `over_cap=[]`, and 1,118 unique repositories.
  Star floor was 10; `above_floor=34`, `skipped=0`. Six exact review batches covered all 34
  repositories and passed the 20-field/schema, enum, timestamp, and repository-set checks:
  28 `verified_plugin`, 0 `verified_skill`, 1 `watchlist`, 4 `related`, and 1 `rejected`.
  Atomic merge added 28 rows to `repositories.csv`, 34 to `dsh-plugin-topic-candidates.csv`,
  34 to `audit-results.csv`, and 28 to `verified-plugins.csv`; backup
  `/tmp/dsh-curator-backup-du3527v2`. Existing stale `/tmp/dsh_review_batch_*` artifacts
  were not reused; only the six exact current batch paths were merged. Documentation checks
  passed: `aggregate.py --render-only` reported 2,777 catalog rows and 1,645 repository
  verified flags; `generate_docs.py --strict` reported 1,983 deduplicated verified entries,
  44 category pages, snapshot `2026-09-21`, and `unmapped=[]`. Nine unittest cases,
  py_compile, `git diff --check`, and case-insensitive primary-key checks for all four tables
  passed. The `.workbuddy/automations/` directory was not read, staged, committed, or pushed.

- **2026-09-22 (weekly / Tuesday, Asia/Shanghai; host scan window `2026-09-23 02:04-02:33 +0800`):**
  Main checkout preflight passed on `main`; `HEAD` matched `origin/main`, the worktree was
  clean, no new stash was needed, and all seven historical stashes were preserved. The full
  scan was date-pinned to task date `2026-09-22` because the host clock was one day ahead.
  Coverage passed with `coverage_ok=true`, `planned/completed=44/44`, `count_queries=195`,
  `fetch_queries=168`, `leaves=168`, `failures=[]`, `over_cap=[]`, and 15,837 unique
  repositories. Star floor was 10; `above_floor=8`, `skipped=13,391`: `VDERR/dsh-echocat-skill-panel`,
  `A8Chann/dsh-pet-live2d`, `buberlo/dsh-jev`, `yu-wenchao/dsh-free-models-hub`,
  `better-er/dsh-pause`, `Coco-king/dsh-x-opencode-session`, `Innocent-children/dev-flow`,
  and `tingfeng347/dsh-vscode-workbench`.
  Two exact four-repository review artifacts passed the 20-field/schema, enum, timestamp,
  and repository-set checks: 7 `verified_plugin`, 0 `verified_skill`, 0 `watchlist`, 0
  `related`, and 1 `rejected` (`yu-wenchao/dsh-free-models-hub`). Stale six-item review
  artifacts were not reused; the current files were `/tmp/dsh_review_20260922_batch_1.json`
  and `/tmp/dsh_review_20260922_batch_2.json`. Atomic merge added 7 rows to
  `repositories.csv`, 8 to `dsh-plugin-topic-candidates.csv`, 8 to `audit-results.csv`,
  and 7 to `verified-plugins.csv`; backup `/tmp/dsh-curator-backup-lb1mlwk2`.
  Documentation checks passed: `aggregate.py --render-only` reported 2,784 catalog rows
  and 1,652 CSV verified flags; `generate_docs.py --strict` reported 1,990 deduplicated
  verified entries, 44 category pages, snapshot `2026-09-22`, and `unmapped=[]`. Nine
  unittest cases, py_compile, `git diff --check`, and case-insensitive primary-key checks
  for all four tables passed. The catalog changes were recorded in the current local
  commit (`chore: record dsh topic curator 2026-09-22`); push was pending at
  memory-update time. The
  `.workbuddy/automations/` directory was not read, staged, committed, or pushed.

- **2026-09-23 (daily / Wednesday; host scan window `2026-09-24 02:05-02:06 +0800`):**
  Actionable scan coverage passed with `coverage_ok=true`, `planned/completed=6/6`,
  `count_queries=6`, `fetch_queries=6`, `leaves=6`, `failures=[]`, `over_cap=[]`, and
  1,136 unique repositories. Star floor was 10; 10 candidates were reviewed. Two exact
  review batches passed the 20-field/schema, enum, timestamp, and repository-set checks:
  8 `verified_plugin`, 0 `verified_skill`, 0 `watchlist`, 2 `related`, and 0 `rejected`.
  The promoted plugins were `slow-stack/mneme`, `PerryLink/jevcore`, `JRJRJPRO/dsh-chat-tree`,
  `LAU-MARS/dsh-cad`, `Fantasality/dsh-origin-plugin`, `yanzwzz/dsh-whale-girl-pet`,
  `Wenaixi/dsh-ponytail`, and `fengyungithub/dsh-short-video-studio`; `MnemosyneOS/mnemosyne`
  and `klarkxy/dsh-editor` remained `related` because they are respectively an external MCP
  service and a multi-package desktop workspace rather than root-installable DSH bundles.
  Atomic merge added 8 rows to `repositories.csv`, 10 to `dsh-plugin-topic-candidates.csv`,
  10 to `audit-results.csv`, and 8 to `verified-plugins.csv`; backup
  `/tmp/dsh-curator-backup-16ozv1wb`. `LAU-MARS/dsh-cad` has a recorded license warning:
  README/package metadata says MIT while the root `LICENSE` and GitHub metadata identify
  Apache-2.0. Documentation checks passed: `aggregate.py --render-only` reported 2,792
  aggregated repositories and `generate_docs.py --strict` reported 1,998 document entries,
  44 category pages, and `unmapped=[]`. Nine unittest cases, py_compile, `git diff --check`,
  and case-insensitive uniqueness checks for all four tables passed. The protected
  `data/README.md` remained byte-for-byte unchanged with SHA-256
  `d00cc65af2883502e77c8c9ac27aefa3f72a1a18c4aef8296c1a76df763b0bcc`. Catalog commit
  `cdca8c52` (`chore: record dsh topic curator 2026-09-23`) was pushed to `origin/main`;
  the final memory state is recorded in the follow-up commit. The
  `.workbuddy/automations/` directory was not read, staged, committed, or pushed.

- **2026-09-25 (weekly / Friday; host scan window `2026-09-25 02:05-02:52 +0800`):**
  Main checkout preflight passed on `main`; `origin/main` was fetched and already current,
  the worktree was clean, historical stashes were preserved, and no current-run stash was
  needed. Full topic coverage passed with `coverage_ok=true`, `planned/completed=44/44`,
  `count_queries=198`, `fetch_queries=171`, `leaves=171`, `failures=[]`, `over_cap=[]`, and
  16,050 unique repositories. Star floor was 10; `above_floor=14`, `skipped=13,587`.
  Three exact review artifacts (`/tmp/dsh_review_20260925_batch_1.json` through batch 3)
  passed the 20-field/schema, enum, timestamp, and repository-set checks: 13
  `verified_plugin`, 0 `verified_skill`, 0 `watchlist`, 0 `related`, and 1 `rejected`
  (`jiujiezongheti/zen-useragent`, unsafe request-identity/file-rewrite behavior).
  Atomic merge added 13 rows to `repositories.csv`, 14 to `dsh-plugin-topic-candidates.csv`,
  14 to `audit-results.csv`, and 13 to `verified-plugins.csv`; backup
  `/tmp/dsh-curator-backup-wkvuchgf`. `aggregate.py --render-only` reported 2,805 unique
  repositories and 1,673 CSV verified flags; `generate_docs.py --strict` reported 2,011
  deduplicated verified entries, 44 category pages, snapshot `2026-09-25`, and
  `unmapped=[]`. Nine unittest cases, py_compile, `git diff --check`, case-insensitive
  uniqueness checks, and the expected-path boundary check passed. Protected `data/README.md`
  remained byte-for-byte unchanged with SHA-256
  `d00cc65af2883502e77c8c9ac27aefa3f72a1a18c4aef8296c1a76df763b0bcc`. The
  `.workbuddy/automations/` directory was not read, staged, committed, or pushed.

- **2026-09-26 (daily / Saturday; host scan window `2026-09-27 02:07-03:18 +0800`):**
  Main checkout started clean at `0432e9a`; all seven historical stashes were preserved.
  Actionable scan coverage passed with `coverage_ok=true`, planned/completed `6/6`,
  `1,175` unique repositories, no failures or over-cap partitions, and `22` candidates
  above the `>10` star floor (`skipped=0`). Four exact review arrays were validated against
  `above_floor`: `18 verified_plugin` and `4 related`, with no other verdicts. The merge
  initially rejected `jaibhasin/dsh-browser-agent` because its review category was the
  unsupported `web-browser`; it was normalized to the existing `automation` category and
  the second atomic merge passed, adding 18 repository rows, 22 candidate rows, 22 audit
  rows, and 18 verified rows; backup `/tmp/dsh-curator-backup-2sak_f8u`.
  Documentation checks passed: `aggregate.py --render-only` reported `2,823` unique
  repositories and `1,691` CSV verified flags; `generate_docs.py --strict` reported
  `2,029` deduplicated verified entries, 44 category pages, snapshot `2026-09-26`, and
  `unmapped=[]`. Nine unittest cases, py_compile, `git diff --check`, and case-insensitive
  uniqueness checks for all four tables passed. Protected `data/README.md` remained
  byte-for-byte unchanged with SHA-256
  `d00cc65af2883502e77c8c9ac27aefa3f72a1a18c4aef8296c1a76df763b0bcc`. Runtime summary
  recorded at `2026-09-27T03:22:11+0800`; catalog commit `dcad8a8` was pushed to
  `origin/main`, and final verification confirmed `HEAD == origin/main` with a clean
  worktree. The
  `.workbuddy/automations/` directory was not read, staged, committed, or pushed.

- **2026-09-27 (weekly / Sunday; task date pinned because the host clock was one day ahead; host scan window `2026-09-28 02:09-02:33 +0800`):**
  Main checkout preflight passed on `main`; `HEAD` matched `origin/main`, the worktree was
  clean, `data/README.md` SHA-256 was
  `d00cc65af2883502e77c8c9ac27aefa3f72a1a18c4aef8296c1a76df763b0bcc`, and all seven
  historical stashes were preserved. Full topic coverage passed with `coverage_ok=true`,
  planned/completed `44/44`, `count_queries=200`, `fetch_queries=174`, `leaves=174`,
  `failures=[]`, `over_cap=[]`, and `16,374` unique repositories. Star floor was `10`;
  `above_floor=7`, `skipped=13,895`: `voyager-crew/voyager`,
  `chiphoton/DeepSeek-Harness-Video-Director`, `Finderchangchang/brewreel`,
  `hikarioyama/Smart-DSH`, `mokuyoaxis/agent-guard`, `Yunado/dsh-qwen38-local-qol`,
  and `ppy-web/dsh-plugin-xiaomi-mimo-tts`. The two requested multi-agent batches did
  not produce artifacts after repeated waits, so they were closed and replaced with a
  bounded primary-evidence review; the exact seven-repository review set passed all
  schema/enum/timestamp checks: `6 verified_plugin`, `0 verified_skill`, `0 watchlist`,
  `1 related`, `0 rejected`. Atomic merge added 6 rows to `repositories.csv`, 7 to
  `dsh-plugin-topic-candidates.csv`, 7 to `audit-results.csv`, and 6 to
  `verified-plugins.csv`; backup `/tmp/dsh-curator-backup-8im_k5cl`. Documentation checks
  passed: `aggregate.py --render-only` reported 2,829 catalog rows and 1,697 CSV verified
  flags; `generate_docs.py --strict` reported 2,035 deduplicated verified entries, 44
  category pages, snapshot `2026-09-27`, and `unmapped=[]`. Nine unittest cases,
  py_compile, `git diff --check`, case-insensitive uniqueness, exact-set presence, and
  HEAD-to-working-tree preservation checks passed. The catalog changes were committed and
  pushed to `origin/main`; `.workbuddy/automations/` was not read, staged, committed, or
  pushed.

- **2026-09-28 (daily / Monday; task date pinned because the host clock was one day ahead;
  host scan window `2026-09-29 02:05-02:06 +0800`; runtime summary recorded at
  `2026-09-29T02:35:32+0800`):** Main checkout preflight passed on `main`; `HEAD` matched
  `origin/main`, the worktree was clean, and all seven historical stashes were preserved.
  The actionable scan passed with `coverage_ok=true`, planned/completed `6/6`,
  `count_queries=6`, `fetch_queries=6`, `leaves=6`, `failures=[]`, `over_cap=[]`, and
  `1,188` unique repositories. Star floor was `10`; `above_floor=12`, `skipped=0`:
  `YottaMeta/deepseek-harness`, `beiyege-01/dsh-voice-ai-girlfriend-plugin`,
  `PolinniZhong/dsh-knit`, `DSH-PackForge/dsh-pack-plugin`,
  `luobosibing2/deepseek-harness-jev`, `PerryLink/dsh-mask`, `IcyCreamDAS/shidi-skill`,
  `evoelsewhere/evoflux`, `pan17/dsh-wechat`, `Yurzi/dsh-web-fetch-enhanced`,
  `aa2246740/dsh-skillhub`, and `PeterTXPan/dsh-unreal-mcp`. Two exact six-repository
  review batches passed the 20-field/schema, enum, timestamp, and repository-set checks:
  `9 verified_plugin`, `0 verified_skill`, `1 watchlist`, `1 related`, and `1 rejected`.
  Atomic merge added 9 rows to `repositories.csv`, 12 to `dsh-plugin-topic-candidates.csv`,
  12 to `audit-results.csv`, and 9 to `verified-plugins.csv`; backup
  `/tmp/dsh-curator-backup-fm32xt9x`. The requested root `scripts/diff_topic.py` path was
  absent in this checkout, so the existing canonical implementation at
  `.workbuddy/skills/dsh-topic-curator/scripts/diff_topic.py` was used; the root
  `data/curation-criteria.yaml` remained the authoritative criteria file. Documentation
  checks passed: `aggregate.py --render-only` reported 2,838 unique repositories and
  1,706 CSV verified flags; `generate_docs.py --strict` reported 2,044 deduplicated
  verified entries, 44 category pages, snapshot `2026-09-28`, and `unmapped=[]`. Nine
  unittest cases, py_compile, `git diff --check`, and case-insensitive primary-key checks
  for all four tables passed. Protected `data/README.md` remained byte-for-byte unchanged
  with SHA-256 `d00cc65af2883502e77c8c9ac27aefa3f72a1a18c4aef8296c1a76df763b0bcc`.
  The `.workbuddy/automations/` directory was not read, staged, committed, or pushed.

- **2026-09-29 (daily / Tuesday; task date pinned because the host clock was one day
  ahead; host scan window `2026-09-30 02:06:27-02:07:38 +0800`, UTC date 2026-09-29):**
  Main checkout preflight passed on `main`;
  `origin/main` was fetched and already current, the worktree was clean, and all seven
  historical stashes were preserved. The actionable online preflight returned six
  partitions below the Search API cap (129, 77, 123, 141, 289, 446). Scan coverage passed
  with `coverage_ok=true`, planned/completed `6/6`, `count_queries=6`, `fetch_queries=6`,
  `leaves=6`, `failures=[]`, `over_cap=[]`, and 1,205 unique repositories. Star floor was
  `>10`; `above_floor=17`, `skipped=0`. Three exact review batches (6/6/5) passed the
  20-field/schema, enum, timestamp, and repository-set gates: 15 `verified_plugin`, 0
  `verified_skill`, 0 `watchlist`, 2 `related`, and 0 `rejected`. Atomic merge added 15
  rows to `repositories.csv`, 17 to `dsh-plugin-topic-candidates.csv`, 17 to
  `audit-results.csv`, and 15 to `verified-plugins.csv`; backup
  `/tmp/dsh-curator-backup-uk86k5xq`. `aggregate.py --render-only` reported 2,853 unique
  repositories and 1,721 CSV verified flags; `generate_docs.py --strict` reported 2,059
  verified entries, 44 category pages, snapshot `2026-09-29`, and `unmapped=[]`. Nine
  unittest cases, py_compile, `git diff --check`, and case-insensitive primary-key checks
  for all four tables passed; every verified candidate appeared in the generated docs and
  the two related projects were not promoted. A pre-existing six-record
  `/tmp/dsh_review_batch_2.json` was accidentally overwritten by a review agent; its JSON
  content was reconstructed from the agent transcript and restored, but the original hash
  was unavailable so byte-for-byte recovery cannot be asserted. The current batch review
  remains at `/tmp/dsh_review_batch_2.current.json`. The `.workbuddy/automations/` directory
  was not read, staged, committed, or pushed.

- **2026-09-30 (daily / Wednesday, Asia/Shanghai; task date pinned because the host clock was one day ahead; runtime summary recorded at `2026-09-30T02:29:45+0800`):** Main checkout preflight passed on `main`; `origin/main` was current, the worktree was clean before edits, and all seven historical stashes were preserved. The actionable scan passed with `coverage_ok=true`, planned/completed `6/6`, `count_queries=6`, `fetch_queries=6`, `leaves=6`, `failures=[]`, `over_cap=[]`, and `1,223` unique repositories. Star floor was `>10`; `above_floor=17`, `skipped=0`. Old `/tmp/dsh_review_batch*.json` files belonged to an earlier run and were ignored; three dated exact review batches (6/6/5) passed the 20-field/schema, enum, timestamp, and repository-set gates: `13 verified_plugin`, `0 verified_skill`, `0 watchlist`, `4 related`, and `0 rejected`. Atomic merge added 13 rows to `repositories.csv`, 17 to `dsh-plugin-topic-candidates.csv`, 17 to `audit-results.csv`, and 13 to `verified-plugins.csv`; backup `/tmp/dsh-curator-backup-wjlv65n6`. Documentation checks passed: `aggregate.py --render-only` reported `2,866` unique repositories and `1,734` CSV verified flags; `generate_docs.py --strict` reported `2,072` renderable verified entries, 44 category pages, snapshot `2026-09-30`, and `unmapped=[]`. Nine unittest cases, py_compile, `git diff --check`, case-insensitive uniqueness, exact review/candidate presence, generated-doc coverage for all renderable verified rows, and change-boundary checks passed. Protected `data/README.md` remained byte-for-byte unchanged with SHA-256 `d00cc65af2883502e77c8c9ac27aefa3f72a1a18c4aef8296c1a76df763b0bcc`. Catalog and documentation changes are ready for commit and push; `.workbuddy/automations/` was not read, staged, committed, or pushed.

- **2026-10-02 (daily / Friday, Asia/Shanghai; task date pinned because the host clock was one day ahead; runtime summary recorded at `2026-10-03T03:19:10+0800`):** Main checkout was `main`, `HEAD` and `origin/main` were both `9a568253`, and all eight historical stashes were preserved. The actionable scan passed with `coverage_ok=true`, planned/completed `6/6`, `1,235` unique repositories, `above_floor=20`, `skipped=0`, `failures=[]`, and `over_cap=[]`.
  The strict 20-object review artifact `/tmp/dsh_review_20261002_all20.json` combined the preserved manual 12, fresh 7, and the filtered `yu-wenchao/dsh-opencode-free-models` object; it passed exact-set and 20-field checks with `17 verified_plugin` and `3 related`. A full merge dry-run correctly rejected two stale existing star-count fields in the preserved 12 (`joeseesun/qiaomu-rss-dsh` 30 versus scan 36, and `kenz1117/dsh-engram` 12 versus scan 13), so the already-reviewed rows were left intact and the remaining exact 8 were merged atomically from `/tmp/dsh_new_repos_remaining8.json` and `/tmp/dsh_review_20261002_remaining8.json`.
  The merge added 7 rows to `repositories.csv`, 8 to `dsh-plugin-topic-candidates.csv`, 8 to `audit-results.csv`, and 7 to `verified-plugins.csv`; backup `/tmp/dsh-curator-backup-54ob1um4`. Documentation checks passed: `aggregate.py --render-only` reported `2,883` unique repositories and `1,751` CSV verified flags; `generate_docs.py --strict` reported `2,089` renderable verified entries, 44 category pages, snapshot `2026-10-02`, and `unmapped=[]`.
  Nine unittest cases, `py_compile`, `git diff --check`, case-insensitive uniqueness, exact 20-review coverage, related-entry exclusion, generated-doc coverage, and protected `data/README.md` SHA-256 `d00cc65af2883502e77c8c9ac27aefa3f72a1a18c4aef8296c1a76df763b0bcc` passed. The 17 catalog/document files are ready for commit and push; `stash@{0}` remains preserved.

- **2026-10-10 (daily / Saturday, Asia/Shanghai; runtime `2026-10-10T02:55+0800`):** Main checkout preflight passed on `main`; local `HEAD` and fetched `origin/main` were `63b29f3c`, with no local-only commits. The worktree had one pre-existing append to this memory file; it was stashed with `.workbuddy/automations/` excluded, restored and SHA-256 verified (`7079e78be1e002a7d7a8cc1792cbdf135af5b7d9a9c8e0bf1d67408fdc4d5c44`), and the eight prior stashes remain intact. The actionable scan passed with `coverage_ok=true`, planned/completed `6/6`, `count_queries=6`, `fetch_queries=6`, `leaves=6`, `failures=[]`, `over_cap=[]`, and 1,299 unique repositories. Star floor was `>10`; `above_floor=71`, `skipped=0`. Twelve review batches (6/6/6/6/6/6/6/6/6/6/6/5) exactly covered the candidate set and passed the 20-field schema checks: 58 `verified_plugin`, 3 `verified_skill`, 7 `related`, 3 `rejected`, 0 `watchlist`. Atomic merge added 61 rows to `repositories.csv`, 71 to `dsh-plugin-topic-candidates.csv`, 71 to `audit-results.csv`, and 61 to `verified-plugins.csv`; backup `/tmp/dsh-curator-backup-4uqus52o`. `aggregate.py --render-only` reported 2,944 unique repositories and 1,812 verified CSV flags; `generate_docs.py --strict` reported 2,150 verified entries, 44 category pages, snapshot `2026-10-10`, and `unmapped=[]`. Nine unittest cases, the specified `py_compile`, `git diff --check`, and case-insensitive primary-key uniqueness checks for all four tables passed. `.workbuddy/automations/` was not accessed.

- **2026-10-12 (daily / Monday, Asia/Shanghai; runtime `2026-10-12T03:09:15+0800`):** Main checkout preflight passed on `main`; `HEAD` matched `origin/main` at `cb95fe1b`, with no local-only commits. The pre-existing memory append was stashed with `.workbuddy/automations/` excluded, restored byte-for-byte with SHA-256 `d664eda0d5e76fa5ec0c0265a43a4a8bacc57255588accba4665549a06cf1a56`, and the eight historical stashes remain preserved. The actionable scan passed with `coverage_ok=true`, planned/completed `6/6`, `count_queries=6`, `fetch_queries=6`, `leaves=6`, `failures=[]`, `over_cap=[]`, and 1,325 unique repositories. Star floor was `>10`; `above_floor=30`, `skipped=0`. Five exact review batches (6/6/6/6/6) covered all 30 repositories and passed the 20-field/schema, enum, timestamp, load-path, and exact-set checks: 24 `verified_plugin`, 2 `verified_skill`, 1 `watchlist`, 3 `related`, and 0 `rejected`. Stale `/tmp/dsh_review_batch_6.json` through `_12.json` artifacts were preserved under `/tmp/dsh-topic-curator-stale.zUAHJe/`. Atomic merge added 26 rows to `repositories.csv`, 30 to `dsh-plugin-topic-candidates.csv`, 30 to `audit-results.csv`, and 26 to `verified-plugins.csv`; final backup `/tmp/dsh-curator-backup-8zp7k8ui`. `aggregate.py --render-only` reported 2,970 unique repositories and 1,838 CSV verified flags; `generate_docs.py --strict` reported 2,176 verified entries, 44 category pages, snapshot `2026-10-12`, and `unmapped=[]`. Nine unittest cases, the specified `py_compile`, `git diff --check`, and case-insensitive primary-key uniqueness checks for all four tables passed. `.workbuddy/automations/` was not accessed.

- **2026-10-13 (daily / Tuesday, Asia/Shanghai; scan `02:05:11-02:06:35 +0800`):** Main checkout remained on `main`, synchronized with `origin/main` at `d8e4a1de`; the pre-existing memory append was restored byte-for-byte (SHA-256 `56db06b6415e583a29a19c5c954b5511e9dc667cf788eed5b6de49e8304eda1b`), and all eight historical stashes remain preserved. The actionable scan passed with `coverage_ok=true`, planned/completed `6/6`, `count_queries=6`, `fetch_queries=6`, `leaves=6`, 1,343 unique repositories, `failures=[]`, and `over_cap=[]`. Star floor was `>10`; `above_floor=16`, `skipped=0`. Three exact review batches (6/6/4) passed the 20-field schema and repository-set checks: 14 `verified_plugin`, 2 `related`, and 0 `verified_skill`, `watchlist`, or `rejected`. Atomic merge added 14 rows to `repositories.csv`, 16 to `dsh-plugin-topic-candidates.csv`, 16 to `audit-results.csv`, and 14 to `verified-plugins.csv`; backup `/tmp/dsh-curator-backup-ed2mpmv8`. `aggregate.py --render-only` reported 2,984 unique repositories and 1,852 verified CSV flags; `generate_docs.py --strict` reported 2,190 verified entries, 44 category pages, snapshot `2026-10-13`, and `unmapped=[]`. Nine unittest cases, the specified `py_compile`, `git diff --check`, and case-insensitive primary-key checks for all four tables passed. Stale review artifacts and prior merge summary were preserved at `/tmp/dsh-topic-curator-stale.20261013.PsB2oK`; `.workbuddy/automations/` was not accessed.

- **2026-10-14 (daily / Wednesday, Asia/Shanghai; run `02:04-02:16 +0800`):** Main checkout was on `main` at `c7a7b73d`, with no local-only commits; fetch/rebase completed and `HEAD` matched `origin/main`. The pre-existing two-line append to `.workbuddy/memory/MEMORY.md` was saved in stash object `465d5c912eb5ca8c7384599abd163f5c33ec63c3`, restored byte-for-byte (SHA-256 `60ae2dda9572fff12fdc664001a9604d5ce129e31b1409d1ac4c549b807bb5dc`), and only that new stash was dropped after verification; all eight historical stashes remain. The skill-local `data/curation-criteria.yaml` is absent, so the tracked root `data/curation-criteria.yaml` was read as authoritative. The actionable scan passed with `coverage_ok=true`, planned/completed `6/6`, `count_queries=6`, `fetch_queries=6`, `leaves=6`, 1,355 unique repositories, `failures=[]`, and `over_cap=[]`. Star floor was `>10`; `above_floor=14`, `skipped=0`. Three exact review batches (6/6/2) covered all candidates: 12 `verified_plugin`, 0 `verified_skill`, 1 `watchlist`, 0 `related`, and 1 `rejected`. Atomic merge added 12 rows to `repositories.csv`, 14 to `dsh-plugin-topic-candidates.csv`, 14 to `audit-results.csv`, and 12 to `verified-plugins.csv`; backup `/tmp/dsh-curator-backup-u1dzf33k`. `aggregate.py --render-only` reported 2,996 unique repositories and 1,864 CSV verified flags; `generate_docs.py --strict` reported 2,202 verified entries, 44 category pages, snapshot `2026-10-14`, and `unmapped=[]`. Nine unittest cases, the specified `py_compile`, `git diff --check`, and case-insensitive primary-key checks passed; table sizes were 2,996 / 2,844 / 2,353 / 2,256 with no duplicate keys. `.workbuddy/automations/` was not read or modified. All pre-commit gates passed.

- **2026-10-15 (daily / Thursday, Asia/Shanghai; run `02:11-02:27 +0800`):** Main checkout was `main` at `f0c9c182`, with no local-only commits; `git fetch origin main` and `git rebase origin/main` completed with `HEAD == origin/main`. The pre-existing two-line MEMORY.md append was stashed as `405341e736450112ec18c6b4be023fd189823cf5`, restored byte-for-byte (SHA-256 `529f8bc8bd982848d64cdd8238503e0734a16a8e5f627ce5ea5d40711b0af36c`), and only the new stash was dropped; all eight historical stashes remain. The skill-local criteria YAML is absent, so root `data/curation-criteria.yaml` was used as authoritative. Daily actionable scan passed with `coverage_ok=true`, planned/completed `6/6`, `count_queries=6`, `fetch_queries=6`, `leaves=6`, 1,378 unique repositories, `failures=[]`, and `over_cap=[]`. Star floor was `>10`; `above_floor=17`, `skipped=0`. Three exact review batches (6/6/5) passed repository-set/schema checks: 14 `verified_plugin`, 3 `related`, and 0 `verified_skill`, `watchlist`, or `rejected`. Atomic merge added 14 rows to `repositories.csv`, 17 to `dsh-plugin-topic-candidates.csv`, 17 to `audit-results.csv`, and 14 to `verified-plugins.csv`; backup `/tmp/dsh-curator-backup-wz7kz7gg`. `aggregate.py --render-only` reported 3,010 unique repositories and 1,878 CSV verified flags; `generate_docs.py --strict` reported 2,216 verified entries, 44 category pages, snapshot `2026-10-15`, and `unmapped=[]`. Nine unittest cases, the specified `py_compile`, `git diff --check`, and case-insensitive primary-key checks for all four tables passed. Old batch artifacts were preserved byte-for-byte at `/tmp/dsh-topic-curator-stale.20261015.LrwPus`; `.workbuddy/automations/` was not accessed.

- **2026-10-16 (daily / Friday, Asia/Shanghai; scan `02:05:18-02:06:42 +0800`):** Main checkout was on `main` at `cc2b16ad` with no local-only commits; fetch/rebase completed and `HEAD == origin/main`. The pre-existing MEMORY.md append was stashed as `5f9e7b55491c749d87d88cb2a0989b7fa7e3d496`, restored with its original SHA-256 `a274e12aaf5efca709d1711c755424c2f22e3aef283adbfeba7d0048e6a3c42d`, and only the new stash was dropped; all eight historical stashes remain. The skill-local criteria YAML is absent, so root `data/curation-criteria.yaml` was used as authoritative. Daily actionable scan passed with `coverage_ok=true`, planned/completed `6/6`, `count_queries=6`, `fetch_queries=6`, `leaves=6`, 1,394 unique repositories, `failures=[]`, and `over_cap=[]`. Star floor was `>10`; `above_floor=20`, `skipped=0`. Four exact review batches (6/6/6/2) covered all 20 candidates and passed the 20-field/schema, enum, date, verified-load-path, and exact-set checks: 17 `verified_plugin`, 1 `verified_skill`, 1 `related`, 1 `rejected`, and 0 `watchlist`. Atomic merge added 18 rows to `repositories.csv`, 20 to `dsh-plugin-topic-candidates.csv`, 20 to `audit-results.csv`, and 18 to `verified-plugins.csv`; backup `/tmp/dsh-curator-backup-rohx81t2`. `aggregate.py --render-only` reported 3,028 unique repositories and 1,896 CSV verified flags; `generate_docs.py --strict` reported 2,234 verified entries, 44 category pages, snapshot `2026-10-16`, and `unmapped=[]`. Nine unittest cases, the specified `py_compile`, `git diff --check`, and case-insensitive primary-key checks for all four tables passed. `.workbuddy/automations/` was not read or modified.

- **2026-10-17 (daily / Saturday, Asia/Shanghai; scan `02:28:43-02:29:55 +0800`):** Main checkout was on `main` at `48776aca` with no local-only commits; fetch/rebase completed and `HEAD == origin/main`. The pre-existing two-line MEMORY.md append was stashed as `85e53bf2f85a3453d0ceac51c7eb3e7019342987`, restored byte-for-byte with SHA-256 `1649f8cdee33fc1034f77cc22fe7b84a33fa603d7152389357b35bcf26845194`, and only this run's stash was dropped; all eight historical stashes remain. The skill-local criteria YAML is absent, so root `data/curation-criteria.yaml` was used as authoritative. Daily actionable scan passed with `coverage_ok=true`, planned/completed `6/6`, `count_queries=6`, `fetch_queries=6`, `leaves=6`, 1,412 unique repositories, `failures=[]`, and `over_cap=[]`. Star floor was `>10`; `above_floor=18`, `skipped=0`. Three exact review batches (6/6/6) passed the 20-field/schema and repository-set checks: 16 `verified_plugin`, 0 `verified_skill`, 0 `watchlist`, 1 `related`, and 1 `rejected`. The stale `/tmp/dsh_review_batch_4.json` was preserved at `/tmp/dsh-topic-curator-stale.20261017/dsh_review_batch_4.json` (SHA-256 `d070207e680af080a9435f11a20cc155eff59125115f7e4e2401095f9b5ae954`) and excluded from the successful exact-set merge. Atomic merge added 16 rows to `repositories.csv`, 18 to `dsh-plugin-topic-candidates.csv`, 18 to `audit-results.csv`, and 16 to `verified-plugins.csv`; backup `/tmp/dsh-curator-backup-g7cy6fxa`. `aggregate.py --render-only` reported 3,044 unique repositories and 1,912 CSV verified flags; `generate_docs.py --strict` reported 2,250 verified entries, 44 category pages, snapshot `2026-10-17`, and `unmapped=[]`. Nine unittest cases, the specified `py_compile`, `git diff --check`, and case-insensitive primary-key checks for all four tables passed. `.workbuddy/automations/` was not read or modified.

- **2026-10-19 (daily / Monday, Asia/Shanghai; runtime `2026-10-19T02:24:32+0800`):** Main checkout was on `main`; fetch/rebase completed with `HEAD == origin/main == 91004b3d`. The pre-existing two-line MEMORY.md append (SHA-256 `740e1ef8eec6d0c229196041a510ade5bceae2749bef78b2ef6be0b536fa32e3`) was stashed as `123a40a54ee57a8a7a684a51d8001bee66dd4f7c`, restored byte-for-byte, and the run stash was removed. During cleanup, the pre-existing stash ref for object `930e3a8041cf72133d1c76661cd2b451ded31365` briefly disappeared; the commit object remained intact and was re-registered with its original message, preserving its hash/content, though its reflog selector timestamp now reflects restoration. All eight original stash object hashes are present. Daily actionable scan passed with `coverage_ok=true`, planned/completed `6/6`, `count_queries=6`, `fetch_queries=6`, `leaves=6`, 1,434 unique repositories, `failures=[]`, and `over_cap=[]`. Star floor was `>10`; `above_floor=23`, `skipped=0`. Four exact review batches (6/6/6/5) yielded 22 `verified_plugin`, 0 `verified_skill`, 0 `watchlist`, 1 `related`, and 0 `rejected`; `WindyPro-rourou/dsh-logcat` was 11 stars in the scan and 10 at review time, recorded in its evidence. Atomic merge added 22 rows to `repositories.csv`, 23 to `dsh-plugin-topic-candidates.csv`, 23 to `audit-results.csv`, and 22 to `verified-plugins.csv`; backup `/tmp/dsh-curator-backup-oie96i47`. `aggregate.py --render-only` reported 3,066 unique repositories and 1,934 CSV verified flags; `generate_docs.py --strict` reported 2,272 verified entries, 44 category pages, snapshot `2026-10-19`, and `unmapped=[]`. All 9 unittest cases, the specified `py_compile`, `git diff --check`, and case-insensitive primary-key checks passed before commit. The postcommit fetch/rebase completed without conflict; the pre-existing hunk was restored byte-for-byte and documentation generation, all 9 tests, `py_compile`, diff checks, and case-insensitive key checks passed again. Stale prior diff/review JSONs were preserved under `/tmp/dsh-topic-curator-stale.20261019.ojTcws/` and `/tmp/dsh-topic-curator-stale-reviews.20261019.wSztdB/`.

- **2026-10-20 (daily / Tuesday, Asia/Shanghai; finalized `2026-10-20T02:19:17+0800`):** Main checkout was `main` at `85b07768`, `HEAD == origin/main`, with no local-only commits. The pre-existing two-line MEMORY.md append (SHA-256 `fcabad2794384ca8ef816de4ce176a6f2d9cf43460cd727135af75af3ed198e6`) was saved in stash object `67b89d5617cb9774cb827321572a26b6bf4f2668`, restored byte-for-byte, and only that run stash was dropped; all eight original stash objects remain. The skill-local criteria YAML is absent; tracked root `data/curation-criteria.yaml` was read as authoritative. Daily actionable scan passed with `coverage_ok=true`, planned/completed `6/6`, `count_queries=6`, `fetch_queries=6`, `leaves=6`, 1,454 unique repositories, `failures=[]`, and `over_cap=[]`. Star floor was `>10`; `above_floor=17`, `skipped=0`. Three exact review batches (6/6/5) yielded 15 `verified_plugin`, 0 `verified_skill`, 1 `watchlist`, 0 `related`, and 1 `rejected`. GitHub REST was rate-limited during review; agents used public repository pages, raw files, and Atom feed timestamps, and disclosed the batch-1 language fallback in evidence. A stale `/tmp/dsh_review_batch_4.json` containing five non-candidate repositories was preserved at `/tmp/dsh-topic-curator-stale.20261020.LBfJSz/dsh_review_batch_4.json` (SHA-256 `b9f0aa0f30a26ec0096afa9deb2a9aee935c0186f85822dcab946c53e43f7d50`) and excluded from merge. Atomic merge added 15 rows to `repositories.csv`, 17 to `dsh-plugin-topic-candidates.csv`, 17 to `audit-results.csv`, and 15 to `verified-plugins.csv`; backup `/tmp/dsh-curator-backup-3ideb0t5`. `aggregate.py --render-only` reported 3,081 unique repositories and 1,949 CSV verified flags; `generate_docs.py --strict` reported 2,287 verified entries, 44 category pages, snapshot `2026-10-20`, and `unmapped=[]`. All 9 unittest cases, the specified `py_compile`, `git diff --check`, and case-insensitive primary-key checks passed; table sizes were 3,081 / 2,939 / 2,448 / 2,341 with no duplicate keys. `.workbuddy/automations/` was not accessed.

- **2026-10-21 (daily / Wednesday, Asia/Shanghai; scan `02:06:34-02:07:46 +0800`):** Main checkout was `main` at `643d1bb5`; the pre-existing two-line MEMORY.md append was stashed as `6e12a2e39acffb71694d7b9c8d2837e5ddf5c93e`, restored byte-for-byte (SHA-256 `3f11ee7c41f193c0abd1a3007335fe8a179b5678732c2640b4dfe520ecb87856`), and only that run stash was dropped; all eight historical stashes remain. The skill-local criteria YAML is absent; tracked root `data/curation-criteria.yaml` was read as authoritative. Daily actionable scan passed with `coverage_ok=true`, planned/completed `6/6`, `count_queries=6`, `fetch_queries=6`, `leaves=6`, 1,481 unique repositories, `failures=[]`, and `over_cap=[]`. Star floor was `>10`; `above_floor=30`, `skipped=0`. Five exact review batches (6/6/6/6/6) passed the 20-field/schema, enum, date, load-path, and exact-set checks: 27 `verified_plugin`, 0 `verified_skill`, 0 `watchlist`, 0 `related`, and 3 `rejected`. Stale 2026-10-20 review artifacts were preserved at `/tmp/dsh-topic-curator-stale.20261021.6ceYUP/`. Atomic merge added 27 rows to `repositories.csv`, 30 to `dsh-plugin-topic-candidates.csv`, 30 to `audit-results.csv`, and 27 to `verified-plugins.csv`; backup `/tmp/dsh-curator-backup-mvrf6mz3`. `aggregate.py --render-only` reported 3,108 unique repositories and 1,976 CSV verified flags; `generate_docs.py --strict` reported 2,314 verified entries, 44 category pages, snapshot `2026-10-21`, and `unmapped=[]`. Nine unittest cases, the specified `py_compile`, `git diff --check`, and case-insensitive primary-key checks for all four tables passed. `.workbuddy/automations/` was not read, staged, committed, or pushed.

- **2026-10-22 (daily / Thursday, Asia/Shanghai; scan `02:01:22-02:02:43 +0800`, finalized `02:50:32 +0800`):** Main checkout stayed on `main` at `a4117fe5`, with `HEAD == origin/main` after fetch/rebase. The pre-existing MEMORY.md append was stashed as `10770d4d65f17e5fe16c928850bf9ab83b44bb30`, restored byte-for-byte (SHA-256 `a414d0a51b0cafafc31a403d2a2c36f164477e74`), and only that run stash was dropped; all eight historical stashes remain. The skill-local `data/curation-criteria.yaml` is absent, so tracked root `data/curation-criteria.yaml` was read as authoritative. Daily actionable scan passed with `coverage_ok=true`, planned/completed `6/6`, `count_queries=6`, `fetch_queries=6`, `leaves=6`, 1,505 unique repositories, `failures=[]`, and `over_cap=[]`. Star floor was `>10`; `above_floor=29`, `skipped=0`. Five exact review batches (6/6/6/6/5) passed the 20-field/schema, enum, date, `main_dir`, and exact-set checks: 26 `verified_plugin`, 0 `verified_skill`, 0 `watchlist`, 2 `related`, and 1 `rejected`. Stale review/diff artifacts were isolated at `/tmp/dsh-topic-curator-stale.6X753f/`. Atomic merge added 26 rows to `repositories.csv`, 29 to `dsh-plugin-topic-candidates.csv`, 29 to `audit-results.csv`, and 26 to `verified-plugins.csv`; backup `/tmp/dsh-curator-backup-bcu6f9sw`. `aggregate.py --render-only` reported 3,134 unique repositories and 2,002 CSV verified flags; `generate_docs.py --strict` reported 2,340 verified entries, 44 category pages, snapshot `2026-10-22`, and `unmapped=[]`. Nine unittest cases, the specified `py_compile`, `git diff --check`, case-insensitive primary-key uniqueness for all four tables, and allowed-path boundary checks passed. `.workbuddy/automations/` was not read, staged, committed, or pushed.
- **2026-10-24 (daily / Saturday, Asia/Shanghai; runtime `2026-10-24T03:09:06+0800`):** Main checkout was on `main`; fetch/rebase completed with `HEAD == origin/main == fe692569bb76b58fd7d2c628dd0066ae39cbe21b`. The pre-existing two-line MEMORY.md append (SHA-256 `d192f634cd15636131367988fa8a3a7450dd2d0952261616959e346007141f41`) was saved as stash object `80aefceefe236fe16d7774e3db49094ba7c6c4fb`, restored byte-for-byte, and only the temporary stash was dropped; all eight historical stashes remain. The skill-local criteria YAML is absent, so tracked root `data/curation-criteria.yaml` was used as authoritative. Daily actionable scan passed with `coverage_ok=true`, planned/completed `6/6`, `count_queries=6`, `fetch_queries=6`, `leaves=6`, 1,523 unique repositories, `failures=[]`, and `over_cap=[]`; floor `>10`, `above_floor=29`, `skipped=0`. Five exact review batches yielded 29 `verified_plugin` and 0 `verified_skill`, `watchlist`, `related`, or `rejected`; where GitHub REST was rate-limited, agents used public repository HTML/raw files and main-branch Atom timestamps with the source recorded in evidence. Atomic merge added 29 rows to each of `repositories.csv`, `dsh-plugin-topic-candidates.csv`, `audit-results.csv`, and `verified-plugins.csv`; backup `/tmp/dsh-curator-backup-qkekfk8t`. `aggregate.py --render-only` reported 3,163 catalog repositories and 2,031 CSV verified flags; `generate_docs.py --strict` reported 2,369 verified entries, 44 category pages, snapshot `2026-10-24`, and `unmapped=[]`. Nine unittest cases, the specified `py_compile`, `git diff --check`, and case-insensitive primary-key uniqueness checks for all four tables passed.

- **2026-10-26 (daily / Monday, Asia/Shanghai; scan `02:14:17-02:15:26 +0800`):** Main checkout is `main` at `cc70f512f04a4f4b4134dc9cfa5cadefd268957d`, with `origin/main` matching and no local-only commits; the eight pre-existing stash entries remain. The skill-local criteria YAML is absent, so tracked `data/curation-criteria.yaml` was used as authoritative. The actionable scan passed with `coverage_ok=true`, planned/completed `6/6`, `count_queries=6`, `fetch_queries=6`, `leaves=6`, 1,557 unique repositories, `failures=[]`, and `over_cap=[]`. Star floor was `>10`; `above_floor=32`, `skipped=0`. Six review batches (6/6/6/6/6/2) passed exact-set and 20-field schema checks: 27 `verified_plugin`, 0 `verified_skill`, 0 `watchlist`, 3 `related`, and 2 `rejected`. Atomic merge added 27 rows to `repositories.csv`, 32 to `dsh-plugin-topic-candidates.csv`, 32 to `audit-results.csv`, and 27 to `verified-plugins.csv`; backup `/tmp/dsh-curator-backup-75pvk5id`. Documentation generation passed: `aggregate.py --render-only` reported 3,190 unique repositories and 2,058 CSV verified flags; `generate_docs.py --strict` reported 2,396 verified entries, 44 category pages, snapshot `2026-10-26`, and `unmapped=[]`. All 9 unittest cases, the specified `py_compile`, `git diff --check`, exact review-set validation, and case-insensitive primary-key checks for all four tables passed. The pre-existing memory change remains preserved separately from this run's log; `.workbuddy/automations/` was not accessed.
- **2026-10-27 (daily / Tuesday, Asia/Shanghai; scan `02:08:02-02:09:23 +0800`):** Main checkout was `main` at `74bc402f` with `origin/main` matching and no local-only commits; the eight pre-existing stash entries remain. The skill-local criteria YAML is absent, so tracked `data/curation-criteria.yaml` was used. The actionable scan passed with `coverage_ok=true`, planned/completed `6/6`, `count_queries=6`, `fetch_queries=6`, `leaves=6`, 1,584 unique repositories, `failures=[]`, and `over_cap=[]`. Star floor was `>10`; `above_floor=27`, `skipped=0`. Five exact review batches (6/6/6/6/3) passed schema and exact-set validation: 23 `verified_plugin`, 1 `verified_skill`, 1 `watchlist`, 1 `related`, and 1 `rejected`. The stale two-entry `/tmp/dsh_review_batch_6.json` was preserved at `/private/tmp/dsh-topic-curator-stale.20261027.vYWgcf/dsh_review_batch_6.json` and excluded from the exact merge. Atomic merge added 24 rows to `repositories.csv`, 27 to `dsh-plugin-topic-candidates.csv`, 27 to `audit-results.csv`, and 24 to `verified-plugins.csv`; backup `/tmp/dsh-curator-backup-sdya6o0i`. `aggregate.py --render-only` reported 3,214 unique repositories and 2,082 CSV verified flags; `generate_docs.py --strict` reported 2,420 verified entries, 44 category pages, snapshot `2026-10-27`, and `unmapped=[]`. All 9 unittest cases, the specified `py_compile`, `git diff --check`, and case-insensitive primary-key checks for all four tables passed. `.workbuddy/automations/` was not accessed.

- **2026-10-30 (daily / Friday, Asia/Shanghai; scan `02:06:23-02:08:20 +0800`):** Main checkout preflight passed on `main` at `cb11e5ff`, synchronized with `origin/main`; the worktree was clean and the nine pre-existing stash entries remained preserved. The required skill references and tracked root `data/curation-criteria.yaml` were read; `.workbuddy/automations/` was not accessed. The actionable scan passed with `coverage_ok=true`, planned/completed `6/6`, `count_queries=6`, `fetch_queries=6`, `leaves=6`, 1,642 unique repositories, `failures=[]`, and `over_cap=[]`. Star floor was `>10`; `above_floor=55`, `skipped=0`. Ten exact review batches covered all 55 repositories and passed the 20-field/schema, enum, `main_dir`, and exact-set checks: 51 `verified_plugin`, 3 `verified_skill`, 1 `related`, 0 `watchlist`, and 0 `rejected`. Atomic merge added 54 rows to `repositories.csv`, 55 to `dsh-plugin-topic-candidates.csv`, 55 to `audit-results.csv`, and 54 to `verified-plugins.csv`; backup `/tmp/dsh-curator-backup-28_1tewh`. `aggregate.py --render-only` reported 3,268 unique repositories and 2,136 CSV verified flags; `generate_docs.py --strict` reported 2,474 verified entries, 44 category pages, snapshot `2026-10-30`, and `unmapped=[]`. Nine unittest cases, the specified `py_compile`, `git diff --check`, and case-insensitive primary-key checks for all four tables passed; commit/push remained pending at this log point.

- **2026-10-31 (daily / Saturday, Asia/Shanghai; runtime `2026-10-31T03:13:52+0800`):** Main checkout ran on `main` at `0ce572695ee2a76e6f628a14585e2a15120f5ac5`, synchronized with `origin/main`; the pre-existing MEMORY.md hunk was saved as `stash@{0}` object `4fdef1129fb40839710f00705f76ee1058effd46`, restored byte-for-byte, and all prior stash objects remained preserved. The skill-local criteria YAML is absent, so tracked root `data/curation-criteria.yaml` was read as authoritative; `.workbuddy/automations/` was not accessed. The actionable scan passed with `coverage_ok=true`, planned/completed `6/6`, `count_queries=6`, `fetch_queries=6`, `leaves=6`, 1,660 unique repositories, `failures=[]`, and `over_cap=[]`. Star floor was `>10`; `above_floor=20`, `skipped=0`. Four exact review batches (6/6/6/2) covered all 20 repositories: 15 `verified_plugin`, 2 `verified_skill`, 2 `related`, 1 `rejected`, and 0 `watchlist`. Stale concurrent batch files were preserved under `/tmp/dsh-topic-curator-stale.20261031.Wfkv9V/`; atomic merge added 17 rows to `repositories.csv`, 20 to `dsh-plugin-topic-candidates.csv`, 20 to `audit-results.csv`, and 17 to `verified-plugins.csv`; backup `/tmp/dsh-curator-backup-wyx_qem2`. `aggregate.py --render-only` reported 3,285 unique repositories and 2,153 CSV verified flags; `generate_docs.py --strict` reported 2,491 verified entries, 44 category pages, snapshot `2026-10-31`, and `unmapped=[]`. Nine unittest cases, the specified `py_compile`, `git diff --check`, and case-insensitive primary-key checks for all four tables passed.

- **2026-11-02 (daily / Monday, Asia/Shanghai; scan `02:23:27-02:24:44 +0800`):** Main checkout was on `main` at `c95e1fa6beddb92c5392891a2d831b88bf2e2577`, synchronized with `origin/main`, with no local-only commits. The pre-existing two-line MEMORY.md append was saved as stash object `17e733339cab3f14dbcdcabe242141c42b349eb8`, restored byte-for-byte (SHA-256 `ce82694189fb65327bbd0149a36472b9cc3ad13819d63b79d6e00273f524758f`), and the temporary stash was dropped after verification; all eight historical stash entries remain. The skill-local `data/curation-criteria.yaml` is absent, so tracked root `data/curation-criteria.yaml` was used as authoritative; `.workbuddy/automations/` was not accessed. The actionable scan passed with `coverage_ok=true`, planned/completed `6/6`, `count_queries=6`, `fetch_queries=6`, `leaves=6`, 1,705 unique repositories, `failures=[]`, and `over_cap=[]`; the existing skill-local `diff_topic.py` path was used because the root `scripts/` directory has no copy. Star floor was `>10`; `above_floor=46`, `skipped=0`. Eight exact review batches (6/6/6/6/6/6/6/4) covered all 46 repositories and passed the 20-field schema, load-path, verdict, and exact-set checks: 37 `verified_plugin`, 0 `verified_skill`, 1 `watchlist`, 3 `related`, and 5 `rejected`. Stale batch files were preserved under `/tmp/dsh-topic-curator-stale.20261102.tO032G/`; atomic merge added 37 rows to `repositories.csv`, 46 to `dsh-plugin-topic-candidates.csv`, 46 to `audit-results.csv`, and 37 to `verified-plugins.csv`; backup `/tmp/dsh-curator-backup-zv0l1fp9`. `aggregate.py --render-only` reported 3,322 unique repositories and 2,190 CSV verified flags; `generate_docs.py --strict` reported 2,528 verified entries, 44 category files, snapshot `2026-11-02`, and `unmapped=[]`. Nine unittest cases, the specified `py_compile`, `git diff --check`, and case-insensitive primary-key checks passed; final table sizes were 3,322 / 3,207 / 2,716 / 2,582 with no duplicate keys.

- **2026-11-09 (daily / Monday, Asia/Shanghai; scan `02:03:26-02:04:50 +0800`, final validation `04:46 +0800`):** Main checkout was `main` at `353a5dcf`, with no local-only commits; `origin/main` was fetched and rebase was current. The pre-existing two-line MEMORY.md change was stashed as object `136a3d9429ff450a564e6a24fbd1808c59016ef9`, restored byte-for-byte with SHA-256 `5300979ee91ebb8157f74ca136e84ab1459dbdf3`, and only the temporary stash was dropped; the nine historical stashes remain. The skill-local criteria YAML is absent, so tracked root `data/curation-criteria.yaml` was used as authoritative; `.workbuddy/automations/` was not accessed. The actionable scan passed with `coverage_ok=true`, planned/completed `6/6`, `count_queries=6`, `fetch_queries=6`, `leaves=6`, 1,846 unique repositories, `failures=[]`, and `over_cap=[]`. Star floor was `>10`; `above_floor=149`, `skipped=0`. Twenty-five exact review batches (24 batches of 6 plus one corrective batch of 6) covered all 149 repositories after the initial full-set check identified and corrected one omitted six-repository group. The final exact-set/schema gate passed with 136 `verified_plugin`, 1 `verified_skill`, 1 `watchlist`, 7 `related`, and 4 `rejected`. Atomic merge added 137 rows to `repositories.csv`, 149 to `dsh-plugin-topic-candidates.csv`, 149 to `audit-results.csv`, and 137 to `verified-plugins.csv`; backup `/tmp/dsh-curator-backup-n_1oz5o1`. `aggregate.py --render-only` reported 3,459 unique repositories and 2,327 CSV verified flags; `generate_docs.py --strict` reported 2,665 verified entries, 44 category pages, snapshot `2026-11-09`, and `unmapped=[]`. Nine unittest cases, the specified `py_compile`, `git diff --check`, and case-insensitive primary-key checks for all four tables passed. No skill, script, test, protected `data/README.md`, or `.workbuddy/automations/` files changed; the data, catalog, documentation, and memory outputs are ready for commit and push.

- **2026-11-10 (daily / Tuesday, Asia/Shanghai; scan `02:01:31-02:03:16 +0800`):** Main checkout was on `main` at `61d683fbb266a419360e34031a1147a38a9b42aa`, synchronized with `origin/main` after fetch/rebase, with no local-only commits. The pre-existing two-line MEMORY.md change (SHA-256 `2094b926653266ef4348d6673e5faf5f22ba6c4ca8619fcda9c7741bcc83011c`) was saved as stash object `0ae4cb4a0d0b2db8a8d1a5edc1fd534d54a52dc0`, restored byte-for-byte, and only the temporary stash was dropped; all nine historical stash objects remain. The skill-local criteria YAML is absent, so tracked root `data/curation-criteria.yaml` was used as authoritative; the root `scripts/diff_topic.py` is absent, so the canonical `.workbuddy/skills/dsh-topic-curator/scripts/diff_topic.py` was used. The actionable scan passed with `coverage_ok=true`, planned/completed `6/6`, `count_queries=6`, `fetch_queries=6`, `leaves=6`, 1,860 unique repositories, `failures=[]`, and `over_cap=[]`. Star floor was `>10`; `above_floor=17`, `skipped=0`. Three exact review batches (6/6/5) passed the 20-field/schema, enum, date, `main_dir`, and exact-set checks: 15 `verified_plugin`, 0 `verified_skill`, 0 `watchlist`, 1 `related`, and 1 `rejected`. A stale set of 25 prior `/tmp/dsh_review_batch_*.json` files was preserved under `/tmp/dsh-topic-curator-stale.20261110.mEXi7j/`; an initially misassigned `lzzzz666/dsh-purge-optimized` review was isolated there and replaced by the exact `lzzzz666888/dsh-purge-optimized` review, which was rejected for high-risk red-team and reverse-shell capabilities. Atomic merge added 15 rows to `repositories.csv`, 17 to `dsh-plugin-topic-candidates.csv`, 17 to `audit-results.csv`, and 15 to `verified-plugins.csv`; backup `/tmp/dsh-curator-backup-ylpmbqb6`. `aggregate.py --render-only` reported 3,474 unique repositories and 2,342 CSV verified flags; `generate_docs.py --strict` reported 2,680 verified entries, 44 category pages, snapshot `2026-11-10`, and `unmapped=[]`. Nine unittest cases, the specified `py_compile`, `git diff --check`, and case-insensitive primary-key checks for all four tables passed; final table sizes were 3,474 / 3,373 / 2,882 / 2,734 with no duplicate keys. No skill, script, test, or `.workbuddy/automations/` files were changed; the data, catalog, documentation, and memory outputs are ready for commit and push.

- **2026-11-11 (external PR review / Wednesday, Asia/Shanghai; run from 01:30 +0800):** Processed the 12 oldest open external PRs (#26, #28, #29, #30, #31, #32, #34, #35, #37, #39, #40, #42) against `data/curation-criteria.yaml`. No PR was merged directly (all carried hand-edited README/docs or CRLF-rewritten CSVs); verified data rows were re-written from primary evidence and committed separately with `Co-authored-by` credit. New verified entries: miqian-nomad/dsh-browser-playwright-codex (high risk), xiaoyuyu6420/dsh-backup (high risk), exoticknight/dsh-system1, mhlywxl/dsh-coding-sound (category `ui`; the PR's `scripts/generate_docs.py` SLUG_MAP change was not adopted), mhlywxl/dsh-split-workspace, huanlin-labs/dsh-isolation-gate, nickzhangcomes/dsh-markup, 0352FL/prevent-peep. Refreshed: Clearailhc/clearai-dsh (category knowledge), Ultroncn/dsh-archived-chats (2.0.x), Sev7eEn7/dsh-sieve (0.4.1, context_management), lamost423/dsh-maze, q253595422/dsh-imagegen-video (npm install form; the PR's v1.7.7 pin was already stale vs v1.27.0). Removed redirected duplicates `Ultronen/dsh-archived-chats` and `lamost423/dsh-trace-compare` from all four tables. Every step passed `aggregate.py --render-only`, `generate_docs.py --strict` (`unmapped=[]`), unittest, `py_compile`, `git diff --check`, and case-insensitive primary-key checks.

- **2026-11-11 (DSH topic curator / Wednesday, daily mode, Asia/Shanghai; run from 02:12 +0800):** Actionable scan passed (`coverage_ok=true`, 6/6 partitions, 1,883 unique repos, `failures=[]`, `over_cap=[]`), floor `>10`, `above_floor=24`, `skipped=0`. Four review batches (6/6/6/6) passed schema and exact-set checks: 19 `verified_plugin`, 0 `verified_skill`, 2 `watchlist` (AIpRoBuilder/FlowX, Ethereal-Space-one/code2kb-agent-toolkit), 1 `related` (william-jin-cmu/cetus), 2 `rejected` (HanKuCha/DSH-Fujiang-Unrestricted for refusal-suppressing jailbreak persona; Nero0427/dsh-purge-lite for approval/sandbox-gate bypass patches). Atomic merge added 19 rows to `repositories.csv`, 24 to `dsh-plugin-topic-candidates.csv`, 24 to `audit-results.csv`, 19 to `verified-plugins.csv`; backup `/tmp/dsh-curator-backup-3nb1unxw`. `generate_docs.py --strict` reported 2,705 verified entries, 44 category pages, snapshot `2026-11-11`, `unmapped=[]`; unittest, `py_compile`, `git diff --check`, and case-insensitive primary-key checks passed (3,498 / 3,403 / 2,912 / 2,759, no duplicates).

- **2026-11-12 (external PR review / Thursday, Asia/Shanghai; run from 01:35 +0800):** Processed the 12 oldest open external PRs (#45, #46, #47, #48, #49, #50, #52, #55, #56, #57, #58, #59) against `data/curation-criteria.yaml`. No PR was merged directly (each touched only `verified-plugins.csv` and/or hand-edited README/docs, and #58 rewrote the whole CSV with CRLF); verified rows were written from primary evidence into all four tables and committed separately with `Co-authored-by` credit. New verified plugins: ShawnRen57/dsh-whale-trail (UNLICENSED disclosed), exoticknight/dsh-better-left-sidebar, orchivo/dsh-conversation-tree, zuwenyin/dsh-plugin-upgrader, Aily-DSH/dsh-approval-inbox, Aily-DSH/dsh-peak-guard, Aily-DSH/dsh-sidebar-tab-close, Aily-DSH/dsh-test-window, 1837458003-ctrl/dsh-memory-starmap, kcgoofee-jpg/dsh-secret-form (high risk). New verified skills: ShawnRen57/omni-learning-anything, huanlin-labs/dsh-policy-validator, huanlin-labs/dsh-superagent-win-startstop, huanlin-labs/superagent-github-mock. Rejected and closed: #45 curo22/dsh-wb400-guard (rewrites channel fingerprints to evade a gateway's "unapproved channel" check), #46 yinsang0910-star/dsh-feishu-plugin (archived one-way mirror; author pointed to the main repo). Every step passed `aggregate.py --render-only`, `generate_docs.py --strict` (`unmapped=[]`), 9 unittest cases, `py_compile`, `git diff --check`, and case-insensitive primary-key checks (final 3,512 / 3,417 / 2,926 / 2,773, no duplicates).

- **2026-11-12 (DSH topic curator / Thursday, daily mode, Asia/Shanghai; run from 02:19 +0800):** Actionable scan passed (`coverage_ok=true`, 6/6 partitions, 1,908 unique repos, `failures=[]`, `over_cap=[]`), floor `>10`, `above_floor=26`, `skipped=0`. Five review batches (6/6/6/6/2) passed schema and exact-set checks: 22 `verified_plugin`, 0 `verified_skill`, 1 `watchlist`, 2 `related`, 1 `rejected` (aishenkiki/dsh-go-exam-helper, exam-cheating purpose). Atomic merge added 22 rows to `repositories.csv`, 26 to `dsh-plugin-topic-candidates.csv`, 26 to `audit-results.csv`, 22 to `verified-plugins.csv`; backup `/tmp/dsh-curator-backup-724dgenn`. `generate_docs.py --strict` reported 2,741 verified entries, 44 category pages, snapshot `2026-11-12`, `unmapped=[]`; unittest, `py_compile`, `git diff --check`, and case-insensitive primary-key checks passed (3,534 / 3,443 / 2,952 / 2,795, no duplicates).

- **2026-11-13 (external PR review / Friday, Asia/Shanghai; run from 01:35 +0800):** Processed all 8 open external PRs (#60, #61, #62, #63, #64, #65, #67, #68) against `data/curation-criteria.yaml`. No PR was merged directly (each carried hand-edited README/docs or touched only `verified-plugins.csv`); verified rows were written from primary evidence into all four tables and committed separately with `Co-authored-by` credit. New verified plugins: opentandem/dsh-phone (remote_device, high risk: external launcher + background Runner, phone-triggered tasks), gongfpp/dsh-novel-fish (fun), gongfpp/dsh-cost-voice (cost_observability; bundled audio not MIT), gongfpp/dsh-thanks-carl (fun; bundled photo not MIT), bamboosir1109/dsh-lanya (communication, high risk: QQ/Bilibili accounts), jasoncai0/dsh-interview-coach (education; PR's `automation` category corrected), yinsang0910-star/dsh-feishu (chat_integration, high risk; replaces the archived mirror rejected in #46), h958661134/dsh-plugin-dot (agent_orchestration). Refreshed huliux/dsh-asr-plugin install pin 0.1.2 -> 0.1.6 (verified against Release v0.1.6, README and npm). Rejected and closed: #60 MorenLendan/dsh-moren-unlimited (unrestricted persona preset that defaults sessions to `approval: never` and bundles dsh-purge unrestricted mode; same class as earlier jailbreak/approval-bypass rejections). Every step passed `aggregate.py --render-only`, `generate_docs.py --strict` (`unmapped=[]`), unittest, `py_compile`, `git diff --check`, and case-insensitive primary-key checks (final 3,542 / 3,451 / 2,960 / 2,803, no duplicates).

- **2026-11-13 (DSH topic curator / Friday, daily mode, Asia/Shanghai; run from 02:15 +0800):** Actionable scan passed (`coverage_ok=true`, 6/6 partitions, 1,931 unique repos, `failures=[]`, `over_cap=[]`), floor `>10`, `above_floor=23`, `skipped=0`. Four review batches (6/6/6/5) passed schema and exact-set checks: 22 `verified_plugin`, 0 `verified_skill`, 1 `watchlist` (automagik-si/omni), 0 `related`, 0 `rejected`. Atomic merge added 22 rows to `repositories.csv`, 23 to `dsh-plugin-topic-candidates.csv`, 23 to `audit-results.csv`, 22 to `verified-plugins.csv`; backup `/tmp/dsh-curator-backup-3xn1vybb`. `generate_docs.py --strict` reported 2,771 verified entries, 44 category pages, snapshot `2026-11-13`, `unmapped=[]`; unittest, `py_compile`, `git diff --check`, and case-insensitive primary-key checks passed (3,564 / 3,474 / 2,983 / 2,825, no duplicates).

- **2026-11-14 (DSH topic curator / Saturday, daily mode, Asia/Shanghai; run from 02:15 +0800):** Actionable scan passed (`coverage_ok=true`, 6/6 partitions, 1,956 unique repos, `failures=[]`, `over_cap=[]`), floor `>10`, `above_floor=25`, `skipped=0`. Five review batches (one resumed after timeout) returned 25 verdicts: 21 verified (20 plugin, 1 skill), 2 related, 2 rejected (HandlerOne01/dsh-purge and MorenLendan/dsh-moren-unlimited, jailbreak/unrestricted presets). Merge ok, docs regenerated (unmapped=[]), unit tests, py_compile, diff check and CSV dedupe passed.

- **2026-11-15 (external PR review / Sunday, Asia/Shanghai; run from 01:30 +0800):** One open external PR (#70, flymysql/dsh-remote refresh to v1.1.2). Verified against GitHub metadata (MIT, 288 stars, not archived, dsh-plugin/deepseek-harness topics), Release v1.1.2, npm latest 1.1.2, package.json dsh.bundle + cordis.patch.yml, and README install `dsh plugin --profile web add dsh-remote`. Not merged directly (PR touched only verified-plugins.csv and hand-edited category pages, kept risk at medium); refreshed the row in verified-plugins/audit-results/repositories from primary evidence, raised risk to high (SSH/SFTP remote workspace with remote edit/build/terminal), and committed separately with Co-authored-by credit. `aggregate.py --render-only`, `generate_docs.py --strict` (`unmapped=[]`), 9 unittest cases, `py_compile`, `git diff --check`, and case-insensitive primary-key checks passed (3,585 / 3,499 / 3,008 / 2,846, no duplicates).


- **2026-11-16 (external PR review / Monday, Asia/Shanghai; run from 01:39 +0800):** Two open external PRs. #71 (Ultroncn/dsh-archived-chats sync to v2.0.3): PR only hand-edited generated CATALOG.md, so not merged; verified Release v2.0.3, npm latest 2.0.3, package.json dsh.engines (adds 0.2.2-rc.3) and 30 stars, then refreshed repositories/verified-plugins/audit-results rows from primary evidence. #72 (huanlin-labs, three bundles): PR only hand-edited README.md; added huanlin-labs/dsh-skill-cockpit (plugin_diagnostics, medium) and huanlin-labs/dsh-computer-browser (computer_use, high: drives real desktop and signed-in Chrome) to all four tables from primary evidence (npm-published, package.json dsh.bundle + cordis.patch.yml). huanlin-labs/dsh-vpn-guard (egress/AI-service IP-risk monitor with Clash node switching) held for owner review; PR #72 left open. aggregate.py --render-only, generate_docs.py --strict (unmapped=[]), 9 unittest cases, py_compile, git diff --check and case-insensitive primary-key checks passed (3,587 / 3,501 / 3,010 / 2,848, no duplicates).

- **2026-11-17 (daily / Tuesday, Asia/Shanghai; scan `02:12:41-02:14:30 +0800`):** Main checkout on `main`, clean and synchronized with `origin/main`. Actionable scan passed with `coverage_ok=true`, 6/6 partitions, 2,002 unique repositories, `failures=[]`, `over_cap=[]`. Star floor >10; `above_floor=50`, `skipped=0`. Nine review batches (8x6 + 2) via Pi passed schema and exact-set validation: 42 `verified_plugin`, 1 `verified_skill`, 2 `watchlist`, 2 `related`, 3 `rejected` (DSH-purge host jailbreak toolkit, dsh-wtq-pool third-party login grafting, dsh-plugin-image-workbench ChatGPT account pool). Stale batch files preserved in /tmp/dsh-stale.20261117. Atomic merge added 43 rows to repositories.csv/verified-plugins.csv and 50 to candidates/audit; backup /tmp/dsh-curator-backup-13wld7ok. generate_docs --strict: unmapped=[]; 9 unittest cases, py_compile, git diff --check and primary-key dedupe checks passed.


- **2026-11-18 (daily / Wednesday, Asia/Shanghai; scan `02:07:17-02:09:05 +0800`):** Main checkout on `main`, clean and synchronized with `origin/main` at `2391cc6`. No 1:30 PR lock. Actionable scan passed with `coverage_ok=true`, 6/6 partitions, 2,008 unique repositories, `failures=[]`, `over_cap=[]`. Star floor >10; `above_floor=18`, `skipped=0`. Three review batches (6/6/6) via Pi passed schema and exact-set validation: 14 `verified_plugin`, 0 `verified_skill`, 3 `watchlist` (slimeball2026/DSH-Coach-mode, wonderandyou/dsh-grow, morlay/dsh-plugin), 1 `related` (bruc3van/awesome-dsh-plugin-pro), 0 `rejected`. Independent spot-check of GitHub/npm evidence for verified plugins (including shuxidemosheng/dsh-todolist, BaiKe-Zhang/dsh-mindmark, and high-risk entries oneclickvirt/oneclickvirt, dennisyang1986/polymarket-proxy, nanxfu/dsh-our-imagen, Asuta/dsh-cdx-plus) found native load paths and no jailbreak / webshell / approval-bypass class issues; high risk was labeled, not auto-rejected. Atomic merge added 14 rows to repositories.csv/verified-plugins.csv and 18 to candidates/audit; backup /tmp/dsh-curator-backup-wkysz3zm. `aggregate.py --render-only` reported 3,644 unique repositories and 2,513 CSV verified flags; `generate_docs.py --strict` reported 2,851 verified entries, 44 category pages, snapshot `2026-11-18`, `unmapped=[]`. 9 unittest cases, py_compile, `git diff --check`, and case-insensitive primary-key checks passed (3,644 / 3,569 / 3,078 / 2,905, no duplicates).

- **2026-11-19 (external PR review / Thursday, Asia/Shanghai; run from 01:44 +0800):** Two open external PRs. #75 (wwewtech/numes-deepseek-harness, Chinese title, English body): PR only hand-edited README.md and placed the bullet above the related-projects intro, so it was not merged. Inspected GitHub metadata (public, not a fork or archived, MIT, JavaScript, 0 stars, pushed 2026-11-18), README.md, LICENSE, configs/numes.patch.yml, configs/numes-failover.patch.yml, and tools/numes-free-failover.mjs (binds 127.0.0.1 only, enforces :free suffix plus provider.max_price{0,0}, reads only NUMES_API_KEY from env or ~/.dsh/.credentials.yaml and does not log the value). No package.json, dsh.bundle, or `dsh plugin --profile` install path; it is a local proxy plus an optional provider block on the built-in llm-pi-ai adapter. Added as `related` / `model_gateway` / medium risk to dsh-plugin-topic-candidates.csv and audit-results.csv, and as a related-table row in README.md and README.en.md. Not added to repositories.csv or verified-plugins.csv. Default or auto-discovered chain may include uncensored or abliterated marketplace model ids; this is a model-gateway caution, not a DSH jailbreak or approval-bypass plugin, so it was not rejected. #72 (huanlin-labs / dsh-vpn-guard) had no new comments or updates since 2026-11-16; left open per the 2026-11-17 owner decision (do not include, merge, or close). aggregate.py --render-only, generate_docs.py --strict (unmapped=[]), 9 unittest cases, py_compile, git diff --check and case-insensitive primary-key checks passed (3,644 / 3,570 / 3,079 / 2,905, no duplicates).

- **2026-11-19 (daily / Thursday, Asia/Shanghai; scan `02:07:36-02:09:31 +0800`):** Main checkout on `main`, clean and synchronized with `origin/main` at `a68564a`. No 1:30 PR lock. Actionable scan passed with `coverage_ok=true`, 6/6 partitions, 2,030 unique repositories, `failures=[]`, `over_cap=[]`. Star floor >10; `above_floor=22`, `skipped=0`. Four review batches (6/6/6/4) via Pi passed schema and exact-set validation: 16 `verified_plugin`, 1 `verified_skill` (Rollstack/skills), 1 `watchlist` (1Lyn-en/dsh-whale: load evidence exists but compiled `lib/` is missing and the scoped package is unpublished), 0 `related`, 4 `rejected` (smallCoding1/dsh-go-unrestricted approval-bypass/sandbox-fence jailbreak, zhaofeng104/dsh-purge-custom unofficial dsh-purge jailbreak build, Vikrant-Aleph/dsh-opencode-bridge official-client TLS/UA fingerprint spoofing to use free models without an account, hulibuld/dsh-get-it-for-free cookie/CDP scraping plus fingerprint spoofing and free-tier account grafting). Independent spot-check of all four rejected GitHub pages confirmed the unsafe purpose; verified load paths were confirmed for oriliz/agent-crop, Jestions-dev/dsh-download-server, and KKL08/dsh-plastic-memory. High-risk verified entries (ikevss/dsh-ima, martinbear1/dsh-wechat-remote, hyqhyq3/dsh-gemini-oauth-bridge, 1015677515/dsh-cyberegg, wldxiaobai/dsh-project-mcp-manager) were labeled high, not auto-rejected: they have native load paths and are not jailbreak / webshell / approval-bypass class. Stale batch files preserved in /tmp/dsh-stale.20261119. Atomic merge added 17 rows to repositories.csv/verified-plugins.csv and 22 to candidates/audit; backup /tmp/dsh-curator-backup-td_l1mvf. `aggregate.py --render-only` reported 3,661 unique repositories and 2,530 CSV verified flags; `generate_docs.py --strict` reported 2,868 verified entries, 44 category pages, snapshot `2026-11-19`, `unmapped=[]`. 9 unittest cases, py_compile, `git diff --check`, and case-insensitive primary-key checks passed (3,661 / 3,592 / 3,101 / 2,922, no duplicates).

- **2026-11-20 (daily / Friday, Asia/Shanghai; scan `02:07:04-02:08:55 +0800`):** Main checkout on `main`, clean and synchronized with `origin/main` at `9afd15b`. No 1:30 PR lock. Actionable scan passed with `coverage_ok=true`, 6/6 partitions, 2,046 unique repositories, `failures=[]`, `over_cap=[]`. Star floor >10; `above_floor=15`, `skipped=0`. Three review batches (6/6/3) via Pi passed schema and exact-set validation: 10 `verified_plugin`, 0 `verified_skill`, 2 `watchlist` (HiSeax/dsh-windows-superagent: loadable packages exist under packages/ but the repo root is a private release snapshot with no dsh manifest and needs a manual link: install; vecnode/vn-code: multi-plugin pack requires a local checkout/pnpm bootstrap and ships alpha client forks), 2 `related` (ywsldxk/dsh-plugin-stars star-ranked directory/awesome-list with no DSH load path; whaojie797-design/video-reverse-engineering video-analysis skill for Codex/Claude Code/Cursor only), 1 `rejected` (devin667/dsh-purge-022 unofficial dsh-purge jailbreak/破甲 build with hooks deny→allow bypass, refusal-bypass patches, redteam/nolimit presets and offensive tooling). Independent spot-check of the rejected GitHub page confirmed the unsafe purpose (repo description and package.json both call it 破甲; topics include redteam; tree has lib/hooks-deny.js, lib/nolimit/, lib/redteam/, lib/refusal-patterns.js). Verified load paths were confirmed for chenkezhen480/dsh-world, YinkaiYu/chat-in-dsh, GooDAnDReaDY/dsh-clinebot (package.json `dsh.bundle.patch` + cordis.patch.yml), and additional root or published-package manifests for keli-wen/cospan, kadaliao/dsh-bots, SuCriss/dsh-leekbox, xuanfu-web/dsh-metaphysics, Big-Dao/dsh-plugin-wsl-env, pravets/dsh-edt-projects, and Starry0214/dsh-memory (root cordis.patch.yml plus documented install.sh/install.ps1). High-risk verified entries (chenkezhen480/dsh-world, keli-wen/cospan, kadaliao/dsh-bots, GooDAnDReaDY/dsh-clinebot) were labeled high, not auto-rejected: they have native load paths and are not jailbreak / webshell / approval-bypass class. Stale batch files preserved in /tmp/dsh-stale.20261120. Atomic merge added 10 rows to repositories.csv/verified-plugins.csv and 15 to candidates/audit; backup /tmp/dsh-curator-backup-ot9f35hb. `aggregate.py --render-only` reported 3,671 unique repositories and 2,540 CSV verified flags; `generate_docs.py --strict` reported 2,878 verified entries, 44 category pages, snapshot `2026-11-20`, `unmapped=[]`. 9 unittest cases, py_compile, `git diff --check`, and case-insensitive primary-key checks passed (3,671 / 3,607 / 3,116 / 2,932, no duplicates).
- **2026-11-21 (external PR review / Saturday, Asia/Shanghai; run from 01:35 +0800):** Two open external PRs. #76 (gongfpp/dsh-novel-fish refresh to 1.2.0): PR also regenerated README/docs and only updated verified-plugins.csv, so it was not merged directly. Verified GitHub Release v1.2.0 (2026-11-20T14:56:35Z, tarball SHA-256 79ba046141f18b4dd46f8cc9a08ace906e22522305f1fdf797596dec72f4c4b7), npm latest 1.2.0 (published 2026-11-20T15:01:49Z), README install commands, and package.json 1.2.0 dsh.bundle.patch + dsh.client web + cordis.patch.yml. Main is one docs-only commit ahead of the v1.2.0 tag (release receipts), so the stale caution about unreleased changes beyond v1.1.0 was dropped. Risk remains low (client-side reading UI; JSON backup is a local user export). Refreshed repositories/verified-plugins/audit-results from primary evidence; stars 2->3; noted that bundled sample ebooks retain their own Project Gutenberg / CC BY-SA licenses. #72 (huanlin-labs / dsh-vpn-guard) had no new comments or updates since 2026-11-16; left open per the 2026-11-17 owner decision (do not include, merge, or close). aggregate.py --render-only, generate_docs.py --strict (unmapped=[]), 9 unittest cases, py_compile, git diff --check and case-insensitive primary-key checks passed (3,671 / 3,607 / 3,116 / 2,932, no duplicates).

- **2026-11-21 (daily / Saturday, Asia/Shanghai; scan `02:14:10-02:16:09 +0800`):** Main checkout on `main`, clean and synchronized with `origin/main` at `65112b9`. No 1:30 PR lock. Actionable scan passed with `coverage_ok=true`, 6/6 partitions, 2,065 unique repositories, `failures=[]`, `over_cap=[]`. Star floor >10; `above_floor=22`, `skipped=0`. Four review batches (6/6/6/4) via Pi passed schema and exact-set validation: 19 `verified_plugin`, 0 `verified_skill`, 1 `watchlist` (QuantumKuba/dsh-graphify-plugin: source has a real Cordis bundle but `dsh-graphify` is unpublished on npm and no installable release was found), 1 `related` (ai-timon/timon: standalone Electron/Node agentic workstation that tags dsh-plugin but has no DSH bundle, `cordis.patch.yml`, or skill load path), 1 `rejected` (forelsket521-jpg/vvn-deepseek-harness: unofficial dsh-purge jailbreak/破甲 build that unlocks approval, sandbox and privilege-escalation limits, rewrites hooks deny→allow, and injects custom prompts; ships host-file patching plus an unsigned Windows executable). Independent spot-check of the rejected GitHub page confirmed the unsafe purpose (README title and body call it 破甲; topics include jailbreak, prompt-injection, red-team; tree has kit/, vvn.exe, and one-click host scrubbing scripts). Verified load paths were confirmed for Theflowyears/dsh-arknights-theme, ChimeSky/dsh-a2ui, feigo313/dsh-structured, omdsh-dev/dsh-ego-browser, and roost-qq/dsh-roost (package.json `dsh.bundle.patch` + `cordis.patch.yml` insert). Additional published or in-repo manifests were confirmed for AIcivilization/dsh-model and iroha1145/DSH-Modern-UI (`packages/modern-ui`). JoeyZzZzZz/treasure-map is a firmware-analysis MCP/CLI; `tmap init --client dsh` writes `$DSH_HOME/cordis.patch.yml` and installs a skill under `~/.dsh/skills`, so it was kept as verified rather than related. High-risk verified entries (omdsh-dev/dsh-ego-browser, roost-qq/dsh-roost, marsken88/dsh-studio, 1924225725-collab/dsh-DKN-Workbench, FukangZ/bilibili-subtitles, kaust-ark/ARK, AIcivilization/dsh-model, eghrhegpe/dsh-connect-sensenova-token-plan, OrderG-X/dsh-chrome-bridge) were labeled high, not auto-rejected: they have native load paths and are not jailbreak / webshell / approval-bypass class. Stale batch files preserved in /tmp/dsh-stale.20261121. Atomic merge added 19 rows to repositories.csv/verified-plugins.csv and 22 to candidates/audit; backup /tmp/dsh-curator-backup-ou4833no. `aggregate.py --render-only` reported 3,690 unique repositories and 2,559 CSV verified flags; `generate_docs.py --strict` reported 2,897 verified entries, 44 category pages, snapshot `2026-11-21`, `unmapped=[]`. 9 unittest cases, py_compile, `git diff --check`, and case-insensitive primary-key checks passed (3,690 / 3,629 / 3,138 / 2,951, no duplicates).

- **2026-11-23 (daily / Monday, Asia/Shanghai; scan `02:09:01-02:10:45 +0800`):** Main checkout on `main`, clean and synchronized with `origin/main` at `51a3876`. No 1:30 PR lock. Sunday 2026-11-22 full scan had failed coverage and left the catalog unchanged. Actionable scan passed with `coverage_ok=true`, 6/6 partitions, 2,094 unique repositories, `failures=[]`, `over_cap=[]`. Star floor >10; `above_floor=30`, `skipped=0`. Five review batches (6/6/6/6/6) via Pi passed schema and exact-set validation: 22 `verified_plugin`, 2 `verified_skill` (onlyLT/wow-gongwen-writing; hemu996/smart-ppt-designer), 0 `watchlist`, 1 `related` (kadaliao/dsh-plugins: marketplace.json index with plugin stubs, no mountable bundle), 5 `rejected` (edward-polat/final-cut-win: topic-spam Final Cut download funnel whose page builds an obfuscated `irm | iex` payload from windows-installer.pro; LIUFelix2004/dsh-workbuddy: genuine bundle that defeats WorkBuddy 11128 channel checks and injects a dsh-purge 破甲/jailbreak layer; xiaotianya14/apk-reverse-skill: skill-provider load path whose content is Android license/paywall circumvention, pairip patches, SSL unpinning and keystore dumping; HimLeoing/dsh-purge: unofficial 破甲 jailbreak that auto-grants approvals, widens sandbox/fs policy and ships red-team skills including reverse-shell/WebShell/scanner tooling; Venshell/dsh-zcode-startplan: multi-account ZCode free-plan farming that spoofs the official client fingerprint, mints Aliyun CAPTCHAs via Chromium CDP, and re-exports pooled quota). Independent GitHub spot-checks confirmed all five rejected repos and sample verified load paths (Fanqi89/dsh-craft-anything, mochi-fish/dsh-fish, NightFrost42/dsh-compaction-weave, ZhuFrank/dsh-master-plugin, shine-233/dsh-waimao, DDDMUC/dsh-delete-turn, BaronCyrus/dsh-kimi-subscription, dryw/dsh-egm). High-risk verified entries (mochi-fish/dsh-fish, qikairo7/dsh-gemini-pool, shine-233/dsh-waimao, 2710586329/dsh-qq, BaronCyrus/dsh-kimi-subscription, kuun993/dsh-loop-engine, arrow1031-dev/dsh-qq-bot) were labeled high, not auto-rejected: they have native load paths and are not jailbreak / webshell / approval-bypass / quota-farming class. Atomic merge added 24 rows to repositories.csv/verified-plugins.csv and 30 to candidates/audit; backup /tmp/dsh-curator-backup-_swiold5. `aggregate.py --render-only` reported 3,714 unique repositories and 2,583 CSV verified flags; `generate_docs.py --strict` reported 2,921 verified entries, 44 category pages, snapshot `2026-11-23`, `unmapped=[]`. 9 unittest cases, py_compile, `git diff --check`, and case-insensitive primary-key checks passed (3,714 / 3,659 / 3,168 / 2,975, no duplicates).

- **2026-11-24 (external PR review / Tuesday, Asia/Shanghai; run from 01:44 +0800):** Two open external PRs. #77 (PerryLink, English): refresh 10 already-listed PerryLink rows and add PerryLink/dsh-plugin-guide. The PR also regenerated README/docs and only edited verified-plugins.csv, so it was not squash-merged. Primary evidence checked for all 11 repositories (GitHub metadata, LICENSE, package.json dsh.bundle.patch -> cordis.patch.yml, README install commands, npm latest). dsh-plugin-guide was previously watchlist (docs-only, no load path); it is now an installable plugin that registers one bundled skill with filesystem:read only (npm 0.5.12, Apache-2.0, 72 stars) and was promoted to verified_plugin / plugin_development_skill / low risk. The 10 refreshes were factual (install commands, versions, last_activity, and a few capability/caution/risk updates): auto-review 0.15.5 (risk remains high; optional local Phocinae engine noted), memento 0.5.34, permission-rules 0.8.6 (risk remains high; 0.8.x adds a Codex-style process-level network policy with a built-in HTTP/CONNECT proxy for shell egress — a restriction layer, not a bypass; caution added), mcp-panel 0.6.35 (risk low→medium because approval-gated append-only server CRUD and a trial console that executes real MCP tools), doublecheck 0.9.35, lsp-actions 0.5.24 (caution added: only format/rename write), claude-move 0.4.22 (license MIT→Apache-2.0, confirmed against LICENSE), checkpoint-rewind 0.6.38, industry-research 0.3.29, research-report 0.4.5. Stars, pushed_at, and audit-results were synced on the four CSVs. #72 (huanlin-labs / dsh-vpn-guard) had no new comments or updates since 2026-11-16; left open per the 2026-11-17 owner decision (do not include, merge, or close). aggregate.py --render-only reported 3,714 unique repositories and 2,584 CSV verified flags; generate_docs.py --strict reported 2,922 verified entries, 44 category pages, snapshot 2026-11-24, unmapped=[]. 9 unittest cases, py_compile, git diff --check and case-insensitive primary-key checks passed (3,714 / 3,659 / 3,168 / 2,976, no duplicates).


- **2026-11-24 (daily / Tuesday, Asia/Shanghai; scan `02:14:29-02:16:32 +0800`):** Main checkout on `main`, clean and synchronized with `origin/main` at `dfc6c37` (after the 01:44 PR run merged #77). No 1:30 PR lock. Actionable scan passed with `coverage_ok=true`, 6/6 partitions, 2,109 unique repositories, `failures=[]`, `over_cap=[]`. Star floor >10; `above_floor=18`, `skipped=0`. Three review batches (6/6/6) via Pi passed schema and exact-set validation: 11 `verified_plugin`, 1 `verified_skill` (mvanhorn/last30days-skill), 2 `watchlist` (sasajun2345/dsh-minigame-plugin: Cordis skill-filesystem bundle exists but skills/minigame/SKILL.md lacks valid YAML frontmatter so the skill is not discoverable; Sjkhx/yukinoDigital: thin DSH web plugin with no npm package or documented `dsh plugin add` command), 1 `related` (omnimux-ai/omnimux-client: standalone desktop shell that vendors its own pinned DSH runtime under `~/.omnimux` and has no mount path into an existing DSH profile), 3 `rejected` (Minglink/dsh-jailbreak-workflow: a real DSH canvas bundle whose flagship shipped workflows are 破甲制作 v3 / 破甲炼化 v2 jailbreak-prompt production pipelines and a bundled jailbreak-research skill; yushang657/DSH-YS-pojia: installable jailbreak/unlock plugin with `hooksDenyBypass: true`, approval gate returning allowed-once, and sandbox deny-to-allow file-write patches; deemo0666/pallas-phone-control: Pallas Agent on-device plugin, not DSH-loadable — README install is the Pallas plugin market or offline ZIP, and `apply()` requires Pallas-only `lan_services` / `dsh.ios.lanTool`). Independent checkout and GitHub spot-checks confirmed all three rejected repos and sample verified load paths (Fei-Craft/DS-Bot, Nimbus318/dsh-niuma-broker, wanderer-yk/dsh-xueqiu, mvanhorn/last30days-skill). High-risk verified entries (mvanhorn/last30days-skill, Fei-Craft/DS-Bot, dptech-corp/bohrium-skills, wanderer-yk/dsh-xueqiu) were labeled high, not auto-rejected: they have native load paths and are not jailbreak / webshell / approval-bypass class. Stale batch files preserved in /tmp/dsh-stale.20261124. Atomic merge added 12 rows to repositories.csv/verified-plugins.csv and 18 to candidates/audit; backup /tmp/dsh-curator-backup-d70njfkp. `aggregate.py --render-only` reported 3,726 unique repositories and 2,596 CSV verified flags; `generate_docs.py --strict` reported 2,934 verified entries, 44 category pages, snapshot `2026-11-24`, `unmapped=[]`. 9 unittest cases, py_compile, `git diff --check`, and case-insensitive primary-key checks passed (3,726 / 3,677 / 3,186 / 2,988, no duplicates).
- **2026-11-25 (external PR review / Wednesday, Asia/Shanghai; run from 01:40 +0800):** Two new open external PRs, handled oldest first. #78 (super-new13/dsh-iTab, UI & Experience): PR hand-edited README/category page and appended a thin verified-plugins row, so it was not merged directly. Verified GitHub metadata (stars=1, fork=false, archived=false, LICENSE file MIT with an attribution note → GitHub NOASSERTION, pushed_at 2026-11-24T06:16:12Z), README install `dsh plugin --profile web add dsh-itab` / `github:super-new13/dsh-iTab#v0.3.10`, package.json dsh-itab 0.3.10 dsh.bundle.patch + dsh.client web, cordis.patch.yml insert `itab`, tag v0.3.10, npm latest 0.3.10. src/index.js registers two same-origin host routes (read-only `git symbolic-ref` via execFile; open folder/VS Code, cmd.exe on Windows which the README advises against) → risk medium, no high-risk class. Added to all four CSVs as verified_plugin / ui → 3c75ebf. #79 (gongfpp/dsh-novel-fish refresh to 1.2.1): verified Release v1.2.1 (2026-11-24T15:41:19Z, tgz + SHA256SUMS), npm latest 1.2.1, README install commands and package.json 1.2.1 at the tag (dsh.bundle.patch + dsh.client web, DSH >=0.2.1-rc.2 <0.3.0-0). v1.2.1 removed samples/ebooks LICENSE.md/NOTICE.md and Gutenberg headers; the two bundled sample texts are Lu Xun and Mark Twain classics, so the old Gutenberg/CC BY-SA caution was replaced. Refreshed verified-plugins/audit-results/repositories (host range, pushed_at); risk stays low. #72 (huanlin-labs / dsh-vpn-guard) had no new activity since 2026-11-16; left open per the 2026-11-17 owner decision. For each PR, aggregate.py --render-only, generate_docs.py --strict (verified=2935, unmapped=[]), 9 unittest cases, py_compile, git diff --check and case-insensitive primary-key checks passed (3,727 / 3,678 / 3,187 / 2,989, no duplicates).

- **2026-11-25 (daily / Wednesday, Asia/Shanghai; scan `02:06:26-02:08:29 +0800`):** Main checkout clean and synchronized with `origin/main` at `95377b9`. No 1:30 PR lock. Actionable scan passed with `coverage_ok=true`, 6/6 partitions, 2,125 unique repositories, `failures=[]`, `over_cap=[]`. Star floor >10; `above_floor=17`, `skipped=0`. Three review batches (6/6/5) via Pi passed schema and exact-set validation: 15 `verified_plugin`, 0 `verified_skill`, 1 `watchlist` (yb-zhai/agent-memory), 0 `related`, 1 `rejected` (codesensi/dsh-free-mode, jailbreak persona preset repackaged from dsh-pojia-mode; spot-checked README on GitHub). High-risk verified entries labeled (ximizhou/convenient_window_free, renjiegod/dsh-godbot, lemoncat7/dsh-ssh, copylee711/dsh-academic, dannndouglas/dsh-antigravity-acp, bruc3van/dsh-market-pro). Atomic merge added 15 rows to repositories.csv/verified-plugins.csv and 17 to candidates/audit; backup /tmp/dsh-curator-backup-j77kuq2z. generate_docs --strict: 2,950 verified entries, 44 category pages, snapshot 2026-11-25, unmapped=[]; 9 unittest cases, py_compile, git diff --check and primary-key dedupe checks passed.

- **2026-11-26 (daily / Thursday, Asia/Shanghai; scan 02:07:00-02:08:52 +0800):** Main checkout clean and synchronized with origin/main at 2b42e54. No 1:30 PR lock. Actionable scan passed with coverage_ok=true, 6/6 partitions, 2,140 unique repositories, failures=[], over_cap=[]. Star floor >10; above_floor=18, skipped=0. Three review batches (6/6/6) via Pi passed schema and exact-set validation: 16 verified_plugin, 0 verified_skill, 1 watchlist (L1ch404/jolink-runtime: generic stdio MCP / portable skill with no package.json, no cordis.patch.yml, and no documented dsh plugin path), 1 related (xing-shuyin/keel: standalone Node/Electron workspace formerly pi-web-ui; root package.json has no dsh field and it boots DSH as an optional out-of-process engine), 0 rejected. Independent GitHub spot-checks confirmed the related and watchlist placements and sample verified load paths (NEWJO123/dsh-douyin-scroll, LittleChenLiya/dsh-superagent, weiwenhao/dudu host/dudu-plugin, zman406986/Agent-Memory-CREMATOR / 2019wakeup/dsh-reader subpackages, Destinhue/dsh-video-vision, PeterBon/dsh-hooks). High-risk verified entries (NEWJO123/dsh-douyin-scroll, LittleChenLiya/dsh-superagent, weiwenhao/dudu, klarkxy/ds-dot, ywleeo/browser-mcp, PeterBon/dsh-hooks) were labeled high, not auto-rejected: they have native load paths and are not jailbreak / webshell / approval-bypass class (ds-dot Safe Auto escalates hard-risk approvals to the human; dsh-hooks observes approval/asked and runs user-configured commands). Stale batch files preserved in /tmp/dsh-stale.20261126. Atomic merge added 16 rows to repositories.csv/verified-plugins.csv and 18 to candidates/audit; backup /tmp/dsh-curator-backup-7ek7yekj. aggregate.py --render-only reported 3,758 unique repositories and 2,628 CSV verified flags; generate_docs.py --strict reported 2,966 verified entries, 44 category pages, snapshot 2026-11-26, unmapped=[]. 9 unittest cases, py_compile, git diff --check, and case-insensitive primary-key checks passed (3,758 / 3,713 / 3,222 / 3,020, no duplicates).

- **2026-11-27 (external PR review / Friday, Asia/Shanghai; run from 01:36 +0800):** One new open external PR, #81 (gpboyer2, five plugins). PR hand-edited README/category pages and appended thin verified-plugins rows, so it was not merged directly. All five repos checked via gh api + shallow clone (fork=false, archived=false, MIT, JavaScript, pushed 2026-11-26, stars 0-1, no tags/npm; install `dsh plugin --profile <profile> add github:gpboyer2/<repo>`, package.json dsh.bundle.patch + cordis.patch.yml insert). Accepted 4 as verified_plugin into all four CSVs: dsh-archived-open (session_chat, low; debug trace log on by default), dsh-session-title-on-turnend (session_chat, medium; sends user messages to the configured model, patch disables built-in session-title-llm, default route is the author's LAN model), dsh-finish-line (automation, high - PR said medium; auto edit + git commit/push when workspace idle, mandatory persona decides on the user's behalf, shipped dryRun false), dsh-toolcall-text-guard (automation, low). Rejected dsh-web-fetch-open (audit/candidates only, high): replaces web fetchProvider with one that drops all private-range/SSRF filtering, reads arbitrary file:// by default, follows cross-origin redirects, no allowlist - security-policy bypass; scoped CIDR/hostname allowlist (cf. Yurzi/dsh-web-fetch-enhanced) would be acceptable. aggregate.py --render-only: 3,762 catalog repositories; generate_docs.py --strict: 2,970 verified, 44 category pages, snapshot 2026-11-27, unmapped=[]; 9 unittest cases, py_compile, git diff --check and case-insensitive primary-key dedupe for all four tables passed. #72 left as is per owner decision (author posted a polite follow-up on 2026-11-26).
