# Platega auth

Source: [Authorization](https://docs.platega.io/авторизация-1991638m0.md) (docs.platega.io, 2026-08-26). Payout HMAC: [Create a RUB card payout](https://docs.platega.io/создаёт-вывод-на-рублёвую-карту-через-payout-api-2232954m0.md) and [List saved cards](https://docs.platega.io/получение-сохранённых-карт-39075563e0.md).

GitBook twin (does not conflict on payment headers): [Request authentication](https://platega-io.gitbook.io/platega.io-api-dokumentaciya/api-docs/autentifikaciya-zaprosa.md).

## Base URL

Official:

```
https://app.platega.io/
```

All requests are **JSON** over **HTTPS**.

Unofficial/conflict: third-party indexes (Context7) used host `api.platega.io`. By default use only `https://app.platega.io/`. Official payout examples also hit `https://app.platega.io`.

## Model 1 — payments, reports, subscriptions, refunds, balance

Headers (both required):

| Key | Value | Where |
| --- | --- | --- |
| `X-MerchantId` | merchant UUID | cabinet → Settings; also issued by the manager on onboarding |
| `X-Secret` | merchant API key | cabinet → Settings |

Used by:

- `POST /transaction/process`
- `POST /v2/transaction/process`
- `GET /transaction/{id}`
- `GET /h2h/{id}`
- `POST /transaction/export/csv|excel|json`
- `GET /balance/all`
- `GET /transaction/{id}/cancel-supported`
- `POST /transaction/{id}/cancel`
- `GET /subscription`, `GET /subscription/{id}`, `POST /subscription/{id}/cancel`

Example:

```http
POST /transaction/process HTTP/1.1
Host: app.platega.io
Content-Type: application/json
X-MerchantId: 1a021d91-9b26-4762-b303-5d4aac74e921
X-Secret: <X-Secret from cabinet>
```

Errors (as in payments OpenAPI):

| HTTP | Meaning |
| --- | --- |
| `401` | Auth error (check `X-MerchantId` / `X-Secret`) |
| `400` | Request validation error |

Do not log or commit `X-Secret`.

## Model 2 — Payout API and saved cards

Separate contour. Enabled by the manager; then a **Payout API** section appears in the cabinet.

- SECRET is **different**, not the payments `X-Secret`.
- Key is issued in the cabinet and stored only by the merchant: "Platega has no access to it after issuance."
- Shown **once** right after generation. Cannot be viewed again.
- Reset: Payout API section, confirm with an email code. New key also shown once. Reset **immediately** invalidates the old key — requests with the old signature start getting auth errors.

### Header

```
Authorization: PG-HMAC kid={MERCHANT_ID}, ts={unix}, sig={base64}
```

- `kid` — same MerchantId (UUID).
- `ts` — unix time in seconds. Server accepts a **±300 second** window.
- `sig` — `Base64(HMAC-SHA256(SECRET, string_to_sign))`.

On **payout writes**, header `Idempotency-Key` is required (unique string, e.g. UUID). The same string is part of `string_to_sign`.

### string_to_sign

Elements joined by `\n` (LF).

**POST** `/api/v1/payouts/card-rub`:

```
METHOD
PATH
timestamp
idempotency-key
sha256_hex(body)
```

Skeleton:

```
POST
/api/v1/payouts/card-rub
1719403200
00000000-0000-0000-0000-446655440000
<sha256 hex of body, lowercase>
```

**GET** `/api/v1/cards`:

```
METHOD
PATH
timestamp
<empty string — idempotency-key is unused>
sha256_hex(empty)
```

So between timestamp and body hash there is an empty line (two consecutive `\n`).

SHA-256 of empty body (documented constant):

```
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

`sha256_hex(body)` is hex in **lowercase**. Body is serialized **with no extra spaces** (`json.dumps(..., separators=(",", ":"))`). Those same bytes go into both the signature and the HTTP body. If the client re-serializes (`json=` in requests), the signature will not match.

Ready CLI: [scripts/payout_sign.py](../scripts/payout_sign.py).

### POST payout headers

| Header | Required | Example |
| --- | --- | --- |
| `Authorization` | yes | `PG-HMAC kid=29ef0000-..., ts=1719403200, sig=abc123==` |
| `Idempotency-Key` | yes | UUID |
| `Content-Type` | yes | `application/json` |

### GET cards headers

| Header | Required |
| --- | --- |
| `Authorization` | yes (`PG-HMAC ...`) |

`X-MerchantId` / `X-Secret` are **not** documented as auth for these two endpoints.

## Callback (inbound)

Platega calls the URL from the cabinet (Settings → Callback URLs) and itself sends headers `X-MerchantId` + `X-Secret`. **No body signature.** Compare both headers with `hmac.compare_digest` (constant-time), not `==`.

Details: [callbacks.md](callbacks.md).

## Practical rules

- Payments `X-Secret` and payout `SECRET` are different keys.
- Do not put payout HMAC on `/transaction/*` or vice versa.
- `ts` outside ±300 s → reject, even with a valid signature.
- A new `Idempotency-Key` = a new payout. Retry the same payout with the same key and the same body.
