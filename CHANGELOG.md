# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Skill version is `skills/platega/SKILL.md` → `metadata.version` (also stated in the body).

## [1.2.0] — 2026-09-02

### Changed

- Re-read all 31 official `docs.platega.io/llms.txt` pages. Catalog unchanged (31/31).
- Create payment pages (`POST /transaction/process`, `POST /v2/transaction/process`) were modified **2026-09-01**: new optional body field `orderId` (string, "ID of your internal payment"). Not in OpenAPI `required`, not in official examples, not in shared `CreateTransactionRequest` (that schema still has `additionalProperties: false` and no `orderId`).
- Subscriptions (auto-charges) and H2H: **no API change**. Create-subscription last modified 2026-08-25; H2H last modified 2026-08-08. Cancel-subscription `.md` only grew Apidog `x--orders` noise.
- Document `orderId` vs forbidden `id` vs response `externalId` (no documented mapping) in `payments.md`, `schemas.md`, `scenarios.md`, `examples.md`, `legacy-gitbook.md`.
- `last_read` / snapshot dates → 2026-09-02.

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
