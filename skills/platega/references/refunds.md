# Refunds (transaction cancel)

Official (docs.platega.io, 2026-08-26):

- [Check whether a transaction can be cancelled](https://docs.platega.io/проверка-возможности-отмены-транзакции-38219023e0.md)
- [Cancel a transaction](https://docs.platega.io/отмена-транзакции-38225949e0.md)

Base: `https://app.platega.io/`
Auth: `X-MerchantId` + `X-Secret` (model 1, not payout HMAC).

Order: first `GET /transaction/{id}/cancel-supported`, then `POST /transaction/{id}/cancel`.

For `supported: true`, one of the merchant balances (**USDT or RUB**) must have enough funds for the refund amount.

After a successful refund the payment callback (prose) carries status **CHARGEBACKED**.

---

## GET `/transaction/{id}/cancel-supported`

Returns whether cancel is available and how much USDT will be deducted from the balance.

### Parameters

| Name | In | Required | Notes |
| --- | --- | --- | --- |
| `id` | path | yes | transaction ID |
| `accept` | header | yes in OpenAPI | example: `text/plain` |
| `X-MerchantId` | header | yes | |
| `X-Secret` | header | yes | |

The official OpenAPI example includes concrete MerchantId/Secret values — **do not copy them into code or the repo**, they are spec samples.

### 200 response

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `supported` | boolean | yes | `true` — cancel is available and balance is sufficient; `false` — not possible |
| `totalDeductUsdt` | number | yes | Total USDT amount that will be deducted from the balance |
| `penaltyNativeAmount` | number | no | |
| `penaltyNativeCurrency` | string | no | Penalty currency (RUB, EUR, etc.) |
| `penaltyUsdt` | number | yes | |
| `penaltyConversionRate` | number | no | Conversion rate used for the penalty |
| `blockReason` | string | no | Block reason if `supported: false` due to balance. E.g. `"Insufficient funds"` |

```json
{
  "supported": true,
  "totalDeductUsdt": 0.01236094,
  "penaltyNativeAmount": null,
  "penaltyNativeCurrency": null,
  "penaltyUsdt": null,
  "penaltyConversionRate": null,
  "blockReason": null
}
```

The page describes no other HTTP codes.

---

## POST `/transaction/{id}/cancel`

Initiates cancel and a refund to the payer.

### Parameters

| Name | In | Required |
| --- | --- | --- |
| `id` | path | yes |
| `accept` | header | yes in OpenAPI (example `text/plain`) |
| `X-MerchantId` | header | yes |
| `X-Secret` | header | yes |

No request body in the spec.

### 200 response

All four fields required:

| Field | Type | Description |
| --- | --- | --- |
| `transactionId` | string | Transaction ID |
| `accepted` | boolean | Whether cancel was accepted. `false` means manual handling is required |
| `manualControlRequired` | boolean | If `true` — automatic cancel is impossible, contact support |
| `message` | string | Cancel status message |

Official example is the "not automatic" case:

```json
{
  "transactionId": "71f1375c-ba7a-4e9d-84a5-452f3f9cf4c3",
  "accepted": false,
  "manualControlRequired": true,
  "message": "Возврат в процессе"
}
```

`accepted: false` + `manualControlRequired: true` is a documented outcome, not necessarily a client bug.

The page describes no other HTTP codes.

---

## Call example

```http
GET /transaction/71f1375c-ba7a-4e9d-84a5-452f3f9cf4c3/cancel-supported HTTP/1.1
Host: app.platega.io
Accept: text/plain
X-MerchantId: <MerchantId>
X-Secret: <X-Secret>
```

```http
POST /transaction/71f1375c-ba7a-4e9d-84a5-452f3f9cf4c3/cancel HTTP/1.1
Host: app.platega.io
Accept: text/plain
X-MerchantId: <MerchantId>
X-Secret: <X-Secret>
```

Check balance via `GET /balance/all` ([reporting.md](reporting.md)) if `supported: false` and `blockReason` is about insufficient funds.

Do not confuse with `POST /subscription/{id}/cancel` — that stops future subscription charges, it is not a payment refund.
