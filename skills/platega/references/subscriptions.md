# Recurrent SBP subscriptions

Official docs.platega.io pages (re-read 2026-09-02; no API change, create last modified 2026-08-25):

- [Create subscription](https://docs.platega.io/создать-подписку-40029698e0.md)
- [Get subscription](https://docs.platega.io/получить-подписку-40029717e0.md)
- [List subscriptions](https://docs.platega.io/список-подписок-40029720e0.md)
- [Cancel subscription](https://docs.platega.io/отменить-подписку-40029730e0.md)
- Callbacks: [charge](https://docs.platega.io/callback-по-списанию-40029713e0.md), [status](https://docs.platega.io/callback-по-статусу-подписки-40030962e0.md) — details in [callbacks.md](callbacks.md)
- Schemas: [SubscriptionStatus](https://docs.platega.io/subscriptionstatus-16438392d0.md), [SubscriptionInterval](https://docs.platega.io/subscriptioninterval-16441018d0.md), [CallbackSubscriptionStatus](https://docs.platega.io/callbacksubscriptionstatus-16438868d0.md)

Base: `https://app.platega.io/`
Auth: `X-MerchantId` + `X-Secret`.

## Essence

A subscription is a recurring auto-charge from the payer via SBP. The merchant creates the subscription once and sends the payer to the payment form; Platega does bind, activation, and all charges, and the merchant receives callbacks. Balance is credited on **every successful charge**.

On the form the payer enters email and confirms account bind in the bank (SBP/NSPK) — the subscription becomes `Active`. Then `amount` is charged automatically each period. The merchant does not need to call anything.

**No money transaction is created on create.** Transactions appear later, on each charge.

`paymentMethod` is **always `6` (number, not a string)**. Value `6` is **not** in schema `PaymentMethodInt` (2, 3, 11–14).

---

## POST `/transaction/process` — create subscription

Same path as a payment with a method. Difference is the body.

`operationId`: `createSubscription`

### Headers

`X-MerchantId`, `X-Secret` — required.

### Body

Required: `paymentMethod`, `paymentDetails`, `description`.
Fields `return` / `failedUrl` / `payload` / `metadata` are **not** described in this endpoint's OpenAPI.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `paymentMethod` | integer | yes | Always `6` |
| `paymentDetails.amount` | integer | yes | Amount of one recurring charge |
| `paymentDetails.currency` | string | yes | Description: `"RUB"` |
| `paymentDetails.interval` | see below | yes | 1 — day, 2 — week, 3 — month, 4 — year |
| `paymentDetails.intervalCount` | integer | yes | Limit depends on interval: day up to 31, week up to 4, month up to 12, year up to 3 |
| `description` | string | yes | Shown on the form and in email notifications |

#### `interval` type conflict

- Create prose: "1 — day, 2 — week, 3 — month, 4 — year"; body example: `"interval": 3` (**integer**).
- Schema `SubscriptionInterval`: `type: string`, enum `'1'`, `'2'`, `'3'`, `'4'`; `'3'` description is "30 дней".

Document both. Working examples on the official page use number `3`.

### 200 response

Required: `paymentMethod`, `transactionId`, `redirect`, `status`, `merchantId`.

| Field | Description |
| --- | --- |
| `paymentMethod` | Example: `Subscription` |
| `transactionId` | **This is the subscription ID (`subscriptionId`)**. Store it: callbacks and other endpoints use it |
| `redirect` | Send the payer **immediately**: **30 minutes** to confirm bind, then subscription → `Failed` |
| `status` | Example: `PENDING` |
| `merchantId` | UUID |

```json
{
  "paymentMethod": 6,
  "paymentDetails": {
    "amount": 500,
    "currency": "RUB",
    "interval": 3,
    "intervalCount": 1
  },
  "description": "Premium подписка"
}
```

```json
{
  "paymentMethod": "Subscription",
  "transactionId": "11111111-1111-1111-1111-111111111111",
  "redirect": "https://pay.platega.io/subscription/11111111-...",
  "status": "PENDING",
  "merchantId": "22222222-2222-2222-2222-222222222222"
}
```

### Errors

`400` validation, `401` auth.

---

## GET `/subscription/{subscriptionId}` — one subscription

`operationId`: `getSubscription`

### Parameters

| Name | In | Required |
| --- | --- | --- |
| `subscriptionId` | path | yes |
| `X-MerchantId` | header | yes |
| `X-Secret` | header | yes |

### 200 response

All listed fields are required in the schema.

| Field | Type | Example |
| --- | --- | --- |
| `id` | string | UUID |
| `status` | string | `Active` (see `SubscriptionStatus`) |
| `amount` | integer | `100` |
| `currencyCode` | string | `RUB` |
| `intervalUnit` | string | `Month` |
| `intervalCount` | integer | `1` |
| `startAt` | string | `2026-07-08T09:00:00Z` |
| `nextChargeAt` | string | `2026-08-09T09:10:00Z` |
| `lastChargeAt` | string | `2026-07-09T09:10:00Z` |
| `description` | string | |
| `createdAt` | string | |
| `customerEmail` | string | |
| `chargeMetrics` | object | required as a whole |

`chargeMetrics`:

| Field | Type |
| --- | --- |
| `chargesTotal` | integer |
| `chargesSuccess` | integer |
| `chargesFailed` | integer |
| `totalAmount` | integer |
| `lastChargeAt` | string |
| `nextChargeAt` | string |

```json
{
  "id": "11111111-1111-1111-1111-111111111111",
  "status": "Active",
  "amount": 100,
  "currencyCode": "RUB",
  "intervalUnit": "Month",
  "intervalCount": 1,
  "startAt": "2026-07-08T09:00:00Z",
  "nextChargeAt": "2026-08-09T09:10:00Z",
  "lastChargeAt": "2026-07-09T09:10:00Z",
  "description": "Premium подписка",
  "createdAt": "2026-07-08T09:00:00Z",
  "customerEmail": "payer@example.com",
  "chargeMetrics": {
    "chargesTotal": 1,
    "chargesSuccess": 1,
    "chargesFailed": 0,
    "totalAmount": 100,
    "lastChargeAt": "2026-07-09T09:10:00Z",
    "nextChargeAt": "2026-08-09T09:10:00Z"
  }
}
```

### Errors

`404` — "Transaction not found" (OpenAPI text; it means the subscription).

---

## GET `/subscription` — list

`operationId`: `getSubscriptions`

### Query

All optional, examples from OpenAPI:

| Name | Example |
| --- | --- |
| `status` | `"1"` (string; numeric meaning is not decoded in the schema) |
| `from` | `2026-07-01T00:00:00.000Z` |
| `to` | `2026-07-31T23:59:59.999Z` |
| `page` | `"1"` |
| `size` | `"20"` |

Plus headers `X-MerchantId`, `X-Secret`.

### 200 response

| Field | Type |
| --- | --- |
| `items` | array |
| `total` | integer |
| `page` | integer |
| `size` | integer |

`items` element (all fields required in the schema):

| Field | Schema type | Example |
| --- | --- | --- |
| `id` | string | |
| `status` | **integer** | `4` |
| `amount` | integer | `100` |
| `currencyCode` | string | `RUB` |
| `intervalUnit` | **integer** | `3` or `2` |
| `intervalCount` | integer | `1` |
| `nextChargeAt` | null in schema | `null` |
| `lastChargeAt` | null in schema | `null` |
| `customerEmail` | string, nullable | `null` / email |
| `description` | string | |
| `chargesCount` | integer | `0` |
| `createdAt` | string | |

**Do not guess** the mapping `status: 4` ↔ `SubscriptionStatus`. GET one subscription returns strings (`Active`), the list returns integers. There is no official mapping in llms.txt.

`intervalUnit: 3` matches create `interval: 3` (month) and GET-one `intervalUnit: "Month"`, but that is an observation from examples, not a separate schema.

```json
{
  "items": [
    {
      "id": "480bc68d-8114-4af1-9637-2ca73e5cfdfc",
      "status": 4,
      "amount": 100,
      "currencyCode": "RUB",
      "intervalUnit": 3,
      "intervalCount": 1,
      "nextChargeAt": null,
      "lastChargeAt": null,
      "customerEmail": null,
      "description": "вапвапвап",
      "chargesCount": 0,
      "createdAt": "2026-07-14T13:23:16.164247Z"
    }
  ],
  "total": 2,
  "page": 1,
  "size": 20
}
```

### Errors

`404` — "Transaction not found".

---

## POST `/subscription/{subscriptionId}/cancel`

Cancel stops future charges. The endpoint is **idempotent**.

The payer can cancel themselves via the link in the email after each charge; the merchant learns from callback `SUBSCRIPTION_CANCELLED`.

### Parameters

`subscriptionId` path + `X-MerchantId` + `X-Secret`. No body.

### 200 response

| Field | Example |
| --- | --- |
| `subscriptionId` | UUID |
| `status` | `cancelled` (example is **lowercase**; schema `SubscriptionStatus` is `Cancelled`) |

```json
{
  "subscriptionId": "11111111-1111-1111-1111-111111111111",
  "status": "cancelled"
}
```

### Errors

`400` validation, `401` auth.

---

## Subscription statuses (`SubscriptionStatus`)

| Value | Where seen |
| --- | --- |
| `PendingAgreement` | schema |
| `Active` | schema + GET-one example |
| `PastDue` | schema; after a failed charge (charge callback prose) |
| `Cancelled` | schema |
| `Failed` | schema; create prose: 30 min bind timeout |

Callback statuses are a **different** enum (`SUBSCRIPTION_ACTIVATED` etc.), see [callbacks.md](callbacks.md) and [schemas.md](schemas.md).

## Charges

- Success callback: `Status: CONFIRMED` — funds charged, balance credited (amount minus fee).
- Failure: `Status: CANCELED` — balance unchanged, `NextChargeAt = null`, subscription → `PastDue`. **The provider will not retry.**
- `PaymentMethod` in the charge callback: `6`.
- Charge callback fields are **PascalCase** (`Id`, `Amount`, …) + `SubscriptionId` + `NextChargeAt`.
- `Id` in the charge callback is the **charge transaction** ID (new on every charge), not subscriptionId.
- In the subscription status callback `Id` = `SubscriptionId`.
