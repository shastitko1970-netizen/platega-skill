# Scenarios and edge cases

Companion to the short list in `SKILL.md`. These are the cases that break in production when an agent reads GitBook or invents a Stripe-like API.

---

## 1. Antifraud `metadata`

**When:** the manager said this shop category needs a payer id. If you are unsure, ask — but design the integration with the field present.

**Docs rule:** missing `metadata.userId` when it is required disables antifraud and **may disable the shop**.

### What to send

On `POST /transaction/process` and `POST /v2/transaction/process`:

```json
"metadata": {
  "userId": "123456789",
  "userName": "@username",
  "clientIp": "111.47.86.11"
}
```

| Field | In OpenAPI properties | Required if object sent | In official example |
| --- | --- | --- | --- |
| `userId` | yes | yes | yes — Telegram user id or your stable internal id |
| `userName` | yes | yes | yes — any extra payer data |
| `clientIp` | **no** | — | yes. Safe to send; the schema does not list it |

`userId` must be a **stable** payer id in your system, not a new UUID per payment. Otherwise antifraud cannot join history.

### Typical mistakes

- Omit `metadata` entirely on a "plain SBP" charge.
- Put `userId` in `payload` (your field; antifraud does not read it).
- Mint a new `userId` on every checkout.
- Treat `metadata` as required for every shop (docs: "ask your manager"). For shops without the requirement the field does not break the request — prefer sending it.

Subscription create (`paymentMethod: 6`) OpenAPI does **not** describe `metadata`. Do not invent that subscription create takes the same object until docs say so.

---

## 1b. Merchant `orderId` vs system `id`

**When:** you want to store your shop's order / invoice number on the Platega transaction.

**Docs (create pages, modified 2026-09-01):** optional string `orderId` — "ID вашего внутреннего платежа".

| Field | Who sets it | Send on create? |
| --- | --- | --- |
| `id` | Platega | **No.** System generates `transactionId`. GitBook client UUID is stale. |
| `orderId` | You | **Optional.** Your internal payment id. |
| `externalId` | Response on `GET /transaction/{id}` | Do not send. Docs do not say this is `orderId` echoed back. |

Official examples still omit `orderId`. Shared schema `CreateTransactionRequest` still lacks it. Subscription create OpenAPI still lacks it.

### Typical mistakes

- Put the shop order number in `id` (old GitBook).
- Skip `orderId` and invent a header or `payload` parser as the only correlation key.
- Assume `orderId` is required (it is not).
- Send `orderId` on subscription create because "payments have it" — not in that OpenAPI.

---

## 2. H2H

**When:** the merchant renders QR/requisites in their own UI, without hosted `pay.platega.io`. Docs: "If you want H2H — contact your manager."

### Current contract (docs.platega.io)

1. Create a transaction: `POST /transaction/process` (usually `paymentMethod: 2`). **No `id`.** Optional `orderId` is fine.
2. Take `transactionId` from the response.
3. `GET /h2h/{id}` with `X-MerchantId` + `X-Secret`.
4. Response: `{ "amount": 136.12, "qr": "https://qr.nspk.ru/..." }`.
5. Show the QR to the payer. Status via callback or `GET /transaction/{id}`.

H2H `400`: "Transaction not found" (not created yet / wrong id / H2H not enabled).

### Edge cases

- H2H is **not enabled**: do not fix this by changing the URL. Cabinet / manager first.
- **Do not expect the GitBook body.** Old GitBook returns `accountNumber`, `maskedAccountNumber`, `accountName`, `method`, `amount`. Current docs return only `amount` + `qr`.
- Do not call `GET /h2h/{id}` before create.
- Do not confuse H2H `qr` with the `qr` field on `GET /transaction/{id}` (example there is `base64-qr-data-or-url`) — different endpoint.
- H2H payers do **not** have to open hosted `redirect`. The point is your UI.

---

## 3. Subscriptions (SBP, method 6)

**When:** recurring charges, not a one-off payment.

### Create

Same path as a method payment, different body:

```json
{
  "paymentMethod": 6,
  "paymentDetails": {
    "amount": 500,
    "currency": "RUB",
    "interval": 3,
    "intervalCount": 1
  },
  "description": "Premium subscription"
}
```

- `6` is a number, not a string. **Not** in `PaymentMethodInt`.
- `interval`: prose 1 day / 2 week / 3 month / 4 year; example is integer `3`. Schema `SubscriptionInterval` is strings `'1'..'4'`. Official page examples use a number.
- `intervalCount` caps: day ≤ 31, week ≤ 4, month ≤ 12, year ≤ 3.
- Subscription-create OpenAPI does **not** describe `return` / `failedUrl` / `payload` / `metadata` / `orderId`.

Response: `transactionId` **is** `subscriptionId`. Persist it. Send the payer to `redirect` **immediately**. Bind window is 30 minutes, then `Failed`.

**No money on create.** Do not wait for `CONFIRMED` on this id as if it were a one-off payment.

### Afterwards

| Action | Call |
| --- | --- |
| Subscription status | `GET /subscription/{subscriptionId}` — `PendingAgreement`, `Active`, `PastDue`, `Cancelled`, `Failed` |
| List | `GET /subscription?status=&from=&to=&page=&size=` (list uses **numbers** for `status` / `intervalUnit`; get-one uses strings like `Active` / `Month`) |
| Merchant cancel | `POST /subscription/{id}/cancel` — idempotent, response `status: cancelled` |
| Payer cancel | link in the email after a charge → you get `SUBSCRIPTION_CANCELLED` |

### Callbacks — two different webhooks

1. **Charge** (every attempt, success or fail): **PascalCase** `Id`, `Amount`, `Currency`, `Status`, `PaymentMethod` (6), `Payload`, `SubscriptionId`, `NextChargeAt`. Not the camelCase one-off payload.
2. **Subscription status:** `Id` = SubscriptionId, not a transaction id. Values: `SUBSCRIPTION_ACTIVATED`, `SUBSCRIPTION_PAST_DUE`, `SUBSCRIPTION_CANCELLED`, `SUBSCRIPTION_FAILED`.

### Traps

- Treat create as a charge and grant access before `SUBSCRIPTION_ACTIVATED` / first `CONFIRMED` charge.
- Do not send the payer to `redirect` immediately — 30 minutes and `Failed`.
- After charge `CANCELED`, wait for an automatic retry: docs say `NextChargeAt = null`, subscription → `PastDue`, provider does **not** retry.
- `SUBSCRIPTION_PAST_DUE` stays until a success or cancel webhook.
- `SUBSCRIPTION_FAILED` — bind failed at first activation (provider / consent).
- Look up method 6 in `PaymentMethodInt` and "correct" it to 2.

---

## 4. Nearby edge cases

- **Crypto 13:** web payform by default. Telegram bot is a separate manager opt-in, not a request field.
- **Callback URL:** HTTPS only, public IP/domain, CA certificate. HTTP, localhost, RFC1918, self-signed — rejected. 60 s timeout, then up to 3 retries every 5 minutes. Verify with `hmac.compare_digest` on headers; no body signature.
- **v1 vs v2 create:** v1 → `redirect`, v2 → `url`. Do not read `redirect` from v2.
- **Refund:** `cancel-supported` first (enough USDT/RUB), then `cancel`. `accepted: false` + `manualControlRequired: true` — talk to support, do not loop.
