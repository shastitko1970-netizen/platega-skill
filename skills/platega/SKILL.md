---
name: platega
description: "Use when integrating or debugging the Platega payment API (platega.io): creating payments, SBP/СБП QR, card acquiring, crypto, Sberpay, hosted checkout, H2H, refunds, recurrent subscriptions, callbacks, HMAC-signed payouts, saved cards, balances, or transaction export. Triggers: Platega, platega.io, SBP, СБП, payout, HMAC, subscription, callback, H2H, refund, MerchantId, X-MerchantId, X-Secret, PG-HMAC-SHA256."
license: MIT
metadata:
  author: community
  version: "1.0.0"
  source: "https://docs.platega.io/"
  last_read: "2026-08-26"
---

# Platega.io API

Reference skill for the Platega merchant API. Do not invent endpoints, fields, or statuses. If docs.platega.io and GitBook diverge, document both and mark the source. Full schemas live in `references/`.

**Base URL (official):** `https://app.platega.io/`

`api.platega.io` appeared in unofficial indexes (Context7) — do not use it by default.

**Merchant cabinet:** Settings → `MerchantId`, `X-Secret`, Callback URLs. Payout API (separate SECRET) is opt-in via the account manager.

## Routing

| Task | File |
| --- | --- |
| `X-MerchantId` / `X-Secret`, HMAC payout, ts windows, cabinet secrets | [references/auth.md](references/auth.md) |
| Create payment, status, H2H QR, methods 2/3/11/12/13/14 | [references/payments.md](references/payments.md) |
| Recurrent SBP subscriptions (`paymentMethod: 6`) | [references/subscriptions.md](references/subscriptions.md) |
| Payment and subscription callbacks, fake callback | [references/callbacks.md](references/callbacks.md) |
| `cancel-supported` / `cancel` | [references/refunds.md](references/refunds.md) |
| Card payout, saved cards, HMAC string_to_sign | [references/payouts.md](references/payouts.md) |
| Balance, CSV/Excel/JSON export; rates and conversions (legacy) | [references/reporting.md](references/reporting.md) |
| CMS modules and SDKs | [references/cms-sdks.md](references/cms-sdks.md) |
| GitBook: client `id`, methods 1–10, EXPIRED/FAILED, H2H requisites | [references/legacy-gitbook.md](references/legacy-gitbook.md) |
| OpenAPI field schemas | [references/schemas.md](references/schemas.md) |
| Payout signing CLI | [scripts/payout_sign.py](scripts/payout_sign.py) |

## Auth (short)

Two different models. Do not mix headers.

| Scope | How |
| --- | --- |
| Payments, status, H2H, subscriptions, refunds, balance, export | Headers `X-MerchantId` + `X-Secret` from cabinet → Settings |
| Payouts + saved cards | `Authorization: PG-HMAC kid={MERCHANT_ID}, ts={unix}, sig={b64}`. SECRET is **separate**, shown once. `ts` window ±300 s. POST payout requires `Idempotency-Key` |

HMAC signature and exact strings: [references/auth.md](references/auth.md) and [references/payouts.md](references/payouts.md).

## Payment methods (current PaymentMethodInt)

Official `PaymentMethodInt` schema (docs.platega.io):

| Value | Name |
| --- | --- |
| `2` | SBP (QR code) / `SBPQR` |
| `3` | ERIP |
| `11` | Card acquiring |
| `12` | International payment |
| `13` | Cryptocurrency (web payform by default; Telegram bot is manager opt-in) |
| `14` | Sberpay |

`paymentMethod: 6` is **subscriptions only**. It is **not** in the `PaymentMethodInt` enum. GitBook methods `10` CardRu / `1`–`9` P2P — [references/legacy-gitbook.md](references/legacy-gitbook.md).

## Payment statuses (current PaymentStatus)

Official: `PENDING`, `CANCELED`, `CONFIRMED`, `CHARGEBACKED`.

GitBook extras: `EXPIRED`, `FAILED` — not the current schema.

Status response fields come as-is, including typos `mechantId` and `comission` / `comissionUsdt` / `comissionType`.

## Endpoint index (official llms.txt)

All paths relative to `https://app.platega.io`.

| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| `POST` | `/transaction/process` | X-* | Payment with `paymentMethod` **or** subscription (`6`) |
| `POST` | `/v2/transaction/process` | X-* | No method; payer picks on hosted page; response has `url`, not `redirect` |
| `GET` | `/transaction/{id}` | X-* | Payment status |
| `GET` | `/h2h/{id}` | X-* | H2H QR/link (manager enables) |
| `POST` | `/transaction/export/csv` | X-* | Export → `{url}` |
| `POST` | `/transaction/export/excel` | X-* | Export → `{url}` |
| `POST` | `/transaction/export/json` | X-* | Array of records (not `{url}`) |
| `GET` | `/balance/all` | X-* | Balances |
| `GET` | `/transaction/{id}/cancel-supported` | X-* | Whether cancel is allowed |
| `POST` | `/transaction/{id}/cancel` | X-* | Refund |
| `GET` | `/subscription/{subscriptionId}` | X-* | One subscription |
| `GET` | `/subscription` | X-* | List |
| `POST` | `/subscription/{subscriptionId}/cancel` | X-* | Cancel subscription (idempotent) |
| `POST` | `/api/v1/payouts/card-rub` | PG-HMAC | Payout to RUB card |
| `GET` | `/api/v1/cards` | PG-HMAC | Saved cards |
| inbound POST | URL from cabinet Callback URLs | X-* on callback | Payment status / charge / subscription status |

Not in current llms.txt (mark extra/legacy): `GET /rates/payment_method_rate`, `GET /transaction/balance-unlock-operations`. Conversions page on docs is 404.

## Scenarios

1. **Payment with a method.** `POST /transaction/process` with `paymentMethod` ∈ {2,3,11,12,13,14}. **Do not send `id`.** Redirect the payer to `redirect`. Wait for callback or poll `GET /transaction/{id}`.
2. **Hosted page, no method.** `POST /v2/transaction/process` without `paymentMethod`. Redirect to `url`.
3. **H2H.** Create transaction → `GET /h2h/{id}` → `{amount, qr}` (current docs). Manager enables H2H.
4. **Subscription.** Same `POST /transaction/process`, but `paymentMethod: 6` + `interval` + `intervalCount`. `transactionId` = `subscriptionId`. No money on create. 30 minutes to bind, else `Failed`. Charge callback: PascalCase + `SubscriptionId` + `NextChargeAt`.
5. **Refund.** `GET .../cancel-supported` (needs USDT or RUB balance) → `POST .../cancel`. Possible `accepted: false` + `manualControlRequired: true`.
6. **Payout.** Opt-in. Sign the body byte-for-byte (`separators=(",", ":")`), `data=` not `json=`. New `Idempotency-Key` for every new payout. `amountRub` 1000…87500. `cardId` XOR `cardNumber`.

## Never do this

1. Do not send `id` when creating a transaction on the current API — the system issues the ID. GitBook examples with a client UUID are stale.
2. Do not trust a callback without constant-time compare of `X-MerchantId` and `X-Secret` (`hmac.compare_digest`). There is no body signature.
3. Do not reuse `Idempotency-Key` for a "retry with different data", and do not generate a new key if you want an idempotent retry of the same payout. A new key = a second payout.
4. Do not send payouts via `json=` / re-serialization — bytes will drift from the signature. Send the same bytes you hashed.
5. Do not confuse `paymentMethod: 6` with the `PaymentMethodInt` table (2, 3, 11–14).
6. Do not "fix" response fields `mechantId` / `comission` — that is how the API returns them.
7. Do not map export filter `statuses: ['6','7']` onto enum `PENDING`/`CONFIRMED`/… — official mapping is unpublished.
8. Do not log or commit `X-Secret` or payout `SECRET`. The payout key is shown once.
9. Do not put the callback on HTTP, localhost, private IPs, or a self-signed certificate.
10. Do not treat subscription create as a charge: no money, 30-minute bind window; charge `CANCELED` → `PastDue`, provider does **not** retry.

## Merchant cabinet (from docs)

- Settings: MerchantId, Secret, Callback URLs.
- Fake callback: create a test transaction in the cabinet → fake-callback list button.
- Payout API: generate/reset key (email code, shown once; reset invalidates the old key).
- Crypto `13`: web payform by default; Telegram bot — manager.
- Some store categories require `metadata.userId` (antifraud). Missing it when required disables antifraud and may disable the store. Examples also include `metadata.clientIp`.
- H2H and Payout API are enabled by the manager.

## Sources

- Official: https://docs.platega.io/ and https://docs.platega.io/llms.txt (2026-08-26)
- GitBook (older): https://platega-io.gitbook.io/platega.io-api-dokumentaciya/
- Skill spec: https://agentskills.io/specification
