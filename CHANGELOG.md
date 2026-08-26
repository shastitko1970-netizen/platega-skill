# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Skill version is `skills/platega/SKILL.md` → `metadata.version` (also stated in the body).

## [1.1.0] — 2026-08-26

### Added

- `skills/platega/references/examples.md` — prompt → what an agent does without the skill vs with it (SBP+antifraud, H2H, subscription, callback, payout).
- `skills/platega/references/scenarios.md` — edge cases: antifraud `metadata`, H2H vs GitBook, subscription lifecycle and two callback shapes.

### Changed

- `SKILL.md`: `metadata.version` 1.1.0, links to examples/scenarios, slightly richer happy paths (antifraud, H2H, PastDue).
- README: "Why this skill" and links to the new files.

## [1.0.0] — 2026-08-26

### Added

- First public release. Official `docs.platega.io/llms.txt` covered 31/31.
- Router `SKILL.md`, references for auth/payments/subscriptions/callbacks/refunds/payouts/reporting/cms-sdks/legacy-gitbook/schemas.
- `scripts/payout_sign.py` matching the official HMAC sample.
