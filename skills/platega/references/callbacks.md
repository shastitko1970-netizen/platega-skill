# Callbacks

Official (docs.platega.io, 2026-08-26):

- [Callback on transaction status change](https://docs.platega.io/callback-об-изменении-статуса-транзакции-29209725e0.md)
- [CallbackPayload](https://docs.platega.io/callbackpayload-13226220d0.md)
- [Charge callback](https://docs.platega.io/callback-по-списанию-40029713e0.md)
- [Subscription status callback](https://docs.platega.io/callback-по-статусу-подписки-40030962e0.md)
- [CallbackSubscriptionStatus](https://docs.platega.io/callbacksubscriptionstatus-16438868d0.md)

GitBook: [Callback](https://platega-io.gitbook.io/platega.io-api-dokumentaciya/api-docs/callback.md), [Fake CallBack](https://platega-io.gitbook.io/platega.io-api-dokumentaciya/feikovyi-callback-dlya-testirovaniya-platezhei.md).

Platega **calls your** endpoint. URL is set in the cabinet: **Settings → Callback URLs**. This is not an outbound merchant call.

## Delivery rules

Method: **POST**, JSON body.

Headers from the provider:

| Header | Purpose |
| --- | --- |
| `X-MerchantId` | your MerchantId (UUID) |
| `X-Secret` | your API key |

**No body signature.** Verify by comparing both headers to the expected values with constant-time (`hmac.compare_digest` in Python, equivalent elsewhere). Do not use `==`. Do not "trust" the source by IP without checking the secret.

Payment callback prose (docs):

- success — **CONFIRMED**
- failure — **CANCELED**
- funds returned — **CHARGEBACKED**

The `CallbackPayload` schema and the `status` enum on the payment callback page contain only `CONFIRMED` and `CANCELED`. `CHARGEBACKED` is in the prose and in `PaymentStatus`. Handle all three if `CHARGEBACKED` arrives.

Timeout: if there is no successful response within **60 seconds**, the request is cancelled, then **up to 3** retries at **5 minute** intervals.

GitBook says the same: "The transaction will be resent 3 times, at 5 minute intervals."

### Callback URL requirements (docs only, not GitBook)

- **HTTPS** only (HTTP forbidden)
- Public IPs or domain names only
- Valid SSL from a trusted CA
- Self-signed forbidden
- Private ranges forbidden: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.0/8`
- localhost and loopback forbidden

Respond **HTTP 200** to stop retries.

## 1. Regular payment status callback

OpenAPI webhook: `paymentStatus`.

Headers `X-MerchantId`, `X-Secret` are required in this spec.

### Body

Required: `id`, `amount`, `currency`, `status`.

| Field | Type | Description |
| --- | --- | --- |
| `id` | uuid | transaction ID |
| `amount` | number (float) | |
| `currency` | string | |
| `status` | string | schema enum: `CONFIRMED`, `CANCELED`; prose also `CHARGEBACKED` |
| `paymentMethod` | integer | payment method ID (example `2`) |
| `payload` | string | extra data |

Field case is **camelCase** (`id`, `amount`, `paymentMethod`).

`CallbackPayload` schema: `additionalProperties: false`; required without `paymentMethod`; `paymentMethod` optional integer.

### Examples (official)

Success:

```json
{
  "id": "00000000-0000-0000-0000-000000000000",
  "amount": 1000,
  "currency": "RUB",
  "status": "CONFIRMED",
  "paymentMethod": 2
}
```

Failure:

```json
{
  "id": "00000000-0000-0000-0000-000000000000",
  "amount": 1000,
  "currency": "RUB",
  "status": "CANCELED",
  "paymentMethod": 2
}
```

GitBook example has no `payload`, same four required fields + `paymentMethod`.

Expected merchant response: `200`.

## 2. Subscription charge callback

"Arrives on every charge — success and failure. Differs from a regular payment callback only by two extra fields: `SubscriptionId` and `NextChargeAt`."

In practice the schema uses **PascalCase** (`Id`, `Amount`, …) — not "the same fields in camelCase".

Headers `X-MerchantId`, `X-Secret` are marked `required: false` in this endpoint's OpenAPI (unlike the payment callback). Still verify them if they arrive.

### Body (all fields required in the schema)

| Field | Type | Description |
| --- | --- | --- |
| `Id` | string | **charge transaction** ID (new on every charge) |
| `Amount` | integer | |
| `Currency` | string | |
| `Status` | `PaymentStatus` | `CONFIRMED` — funds charged, balance credited (amount minus fee). `CANCELED` — charge failed: balance unchanged, `NextChargeAt = null`, subscription → `PastDue`, provider does **not** retry |
| `PaymentMethod` | integer | example `6` |
| `Payload` | string | example `""` |
| `SubscriptionId` | string | subscription ID |
| `NextChargeAt` | string | ISO-8601 or `null` on CANCELED |

### Examples

```json
{
  "Id": "33333333-3333-3333-3333-333333333333",
  "Amount": 100,
  "Currency": "RUB",
  "Status": "CONFIRMED",
  "PaymentMethod": 6,
  "Payload": "",
  "SubscriptionId": "11111111-1111-1111-1111-111111111111",
  "NextChargeAt": "2026-08-09T09:10:00Z"
}
```

```json
{
  "Id": "33333333-3333-3333-3333-333333333333",
  "Amount": 100,
  "Currency": "RUB",
  "Status": "CANCELED",
  "PaymentMethod": 6,
  "Payload": "",
  "SubscriptionId": "11111111-1111-1111-1111-111111111111",
  "NextChargeAt": null
}
```

Charge `CANCELED` ≠ merchant-cancelled subscription. Subscription cancel arrives as a separate status callback (`SUBSCRIPTION_CANCELLED`).

## 3. Subscription status callback

"Arrives on status change. Here `Id` = `SubscriptionId` (subscription ID, not a transaction)."

### Body

Same field names as the charge callback (PascalCase). `Status` is `CallbackSubscriptionStatus`, not `PaymentStatus`.

| Status | Schema description |
| --- | --- |
| `SUBSCRIPTION_ACTIVATED` | Subscription is active, charges on schedule |
| `SUBSCRIPTION_PAST_DUE` | Permanent: no transitions out unless there is a webhook of a successful payment or a cancel |
| `SUBSCRIPTION_CANCELLED` | Transition from ACTIVATED or PAST_DUE — explicit cancel by merchant or payer (cancel link or API) |
| `SUBSCRIPTION_FAILED` | Transition from ACTIVATED — bind failed on first activation (provider returned an error or did not confirm consent) |

Create prose: if there is no bind within 30 minutes — subscription `Failed`. Map to `SUBSCRIPTION_FAILED` carefully: the FAILED schema describes a bind error "from ACTIVATED".

### Example (official "confirmed")

```json
{
  "Id": "11111111-1111-1111-1111-111111111111",
  "Amount": 100,
  "Currency": "RUB",
  "Status": "SUBSCRIPTION_ACTIVATED",
  "PaymentMethod": 6,
  "Payload": "",
  "SubscriptionId": "11111111-1111-1111-1111-111111111111",
  "NextChargeAt": "2026-08-09T09:10:00Z"
}
```

The second example on the same page is a **foreign** camelCase payment callback (`id`/`status: CANCELED`/`paymentMethod: 2`). Do not use it as a subscription-status sample; it is an in-page conflict.

## Fake callback (GitBook + cabinet)

GitBook page: create a transaction **in the merchant cabinet**, press the button — a list of available fake callbacks opens.

- success: **CONFIRMED** ("Потдвержденно" — source spelling)
- failure: **CANCELED**

Official llms.txt does not include this page; cabinet functionality is mentioned in the skill brief and in GitBook.

## Receiver implementation (guide)

```python
import hmac
from flask import Flask, request, abort

app = Flask(__name__)
MERCHANT_ID = "..."  # from env, not from the repo
SECRET = "..."


@app.post("/platega/callback")
def callback():
    mid = request.headers.get("X-MerchantId", "")
    sec = request.headers.get("X-Secret", "")
    if not (
        hmac.compare_digest(mid, MERCHANT_ID)
        and hmac.compare_digest(sec, SECRET)
    ):
        abort(401)
    body = request.get_json(force=True, silent=False)
    # camelCase payment vs PascalCase subscription — look at keys
    return "", 200
```

Do not log `X-Secret`. Idempotency: the same callback may arrive again (retries).
