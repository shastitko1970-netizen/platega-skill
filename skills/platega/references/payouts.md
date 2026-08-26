# Payouts (Payout API) and saved cards

Official (docs.platega.io, 2026-08-26):

- [Create a RUB card payout via Payout API](https://docs.platega.io/создаёт-вывод-на-рублёвую-карту-через-payout-api-2232954m0.md)
- [List saved cards](https://docs.platega.io/получение-сохранённых-карт-39075563e0.md)

Base URL in the official Python example: `https://app.platega.io`

Functionality is **opt-in**: unavailable by default. Access is granted by the manager; then a **Payout API** section appears in the cabinet.

Auth is **not** `X-MerchantId`/`X-Secret`, but a separate HMAC. Full model: [auth.md](auth.md). CLI: [scripts/payout_sign.py](../scripts/payout_sign.py).

---

## Secret

- Separate SECRET (not the payments `X-Secret`).
- Shown once after generation. Cannot be viewed again.
- Reset in the cabinet → email code → new key shown once. Old key is invalidated immediately.
- Do not log, do not commit.

## Signature

```
string_to_sign = METHOD + "\n" + PATH + "\n" + timestamp + "\n" + idempotency-key + "\n" + sha256_hex(body)
sig            = Base64(HMAC-SHA256(SECRET, string_to_sign))
Authorization  = PG-HMAC kid={MERCHANT_ID}, ts={timestamp}, sig={sig}
```

- `timestamp` — unix seconds, server window **±300 s**.
- `sha256_hex(body)` — hex **lowercase**.
- Body: `json.dumps(obj, separators=(",", ":")).encode("utf-8")`. Same bytes in HTTP (`data=`, not `json=`).

### POST payout

`idempotency-key` — unique string for every **new** payout (e.g. UUID). Same string in header `Idempotency-Key`. Repeat with the same key — idempotent retry. New key — second payout.

### GET cards

`idempotency-key` in the sign string is an **empty string**. Body is empty, hash:

```
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

That is:

```
GET
/api/v1/cards
1719403200

e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

(empty line between timestamp and hash).

---

## POST `/api/v1/payouts/card-rub`

Creates a payout to a RUB card.

### Headers

| Header | Required | Example |
| --- | --- | --- |
| `Authorization` | yes | `PG-HMAC kid=29ef0000-..., ts=1719403200, sig=abc123==` |
| `Idempotency-Key` | yes | UUID |
| `Content-Type` | yes | `application/json` |

### Body

Send **either** `cardId` of a saved card **or** `cardNumber` of a full PAN (XOR).

Amount of one payout: **1000 to 87500 RUB**.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `cardId` | string | no | Saved card ID (alternative to `cardNumber`) |
| `cardNumber` | string | no | Recipient card number (16 digits) |
| `amountRub` | integer | yes | Payout amount in rubles |
| `payoutMethod` | string | yes | Always `CARD` |
| `currencyRequested` | string | yes | Always `RUB` |

```json
{"cardNumber":"2200000000000000","amountRub":1500,"payoutMethod":"CARD","currencyRequested":"RUB"}
```

(compact serialization with no spaces — hash exactly that.)

### Response (documented example)

```json
{
  "withdrawalRecordId": "3c0d321d-40c4-46e3-97f0-7a8f50ce03a6",
  "status": "CREATED",
  "cardMasked": "**** 0000",
  "amountUsdtDebited": 13.270341
}
```

| Field | Type | Description |
| --- | --- | --- |
| `withdrawalRecordId` | string | Created payout ID |
| `status` | string | Right after create — `CREATED`. The page lists no other values |
| `cardMasked` | string | Masked card number |
| `amountUsdtDebited` | number | Amount debited from the merchant USDT balance |

HTTP error codes are not tabulated on the page. Reset/wrong key: "authentication error".

### Official Python fragment (meaning)

```python
import base64, hashlib, hmac, json, time, uuid, requests

MERCHANT_ID = "your-merchant-id"
SECRET      = "your-secret-key"
BASE        = "https://app.platega.io"
PATH        = "/api/v1/payouts/card-rub"

body = {
    "cardNumber": "2200000000000000",  # or "cardId": "saved-card-uuid"
    "amountRub": 1500,                 # 1000 to 87500 RUB
    "payoutMethod": "CARD",
    "currencyRequested": "RUB",
}

idem_key   = str(uuid.uuid4())
body_bytes = json.dumps(body, separators=(",", ":")).encode("utf-8")
ts         = int(time.time())

body_hash      = hashlib.sha256(body_bytes).hexdigest()
string_to_sign = "\n".join(["POST", PATH, str(ts), idem_key, body_hash])

sig = base64.b64encode(
    hmac.new(SECRET.encode("utf-8"), string_to_sign.encode("utf-8"), hashlib.sha256).digest()
).decode("ascii")

headers = {
    "Authorization":   f"PG-HMAC kid={MERCHANT_ID}, ts={ts}, sig={sig}",
    "Idempotency-Key": idem_key,
    "Content-Type":    "application/json",
}

# Important: data=body_bytes, not json=body
resp = requests.post(BASE + PATH, headers=headers, data=body_bytes, timeout=30)
```

Working CLI without hardcoded secrets: `python scripts/payout_sign.py --body '...'`.

---

## GET `/api/v1/cards`

By default only active cards. `onlyActive=false` — also `DISABLED` and `PENDING`.

### Parameters

| Name | In | Required | Description |
| --- | --- | --- | --- |
| `onlyActive` | query | no | Can be omitted by default. `false` also returns DISABLED and PENDING |
| `Authorization` | header | yes | `PG-HMAC kid=<merchantId>, ts=<unix_timestamp>, sig=<base64_signature>` |

Example query: `onlyActive=true` (string).

### 200 response

Array of objects. Required fields of each:

| Field | Type | Example |
| --- | --- | --- |
| `cardId` | string | UUID |
| `masked` | string | `•••• •••• •••• 4242` |
| `last4` | string | `4242` |
| `brand` | string | `Visa` / in the second example `Запасная` |
| `label` | string | `Основная карта` / `""` |
| `status` | string | `ACTIVE`, `DISABLED`; prose also mentions `PENDING` |

```json
[
  {
    "cardId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "masked": "•••• •••• •••• 4242",
    "last4": "4242",
    "brand": "Visa",
    "label": "Основная карта",
    "status": "ACTIVE"
  },
  {
    "cardId": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "masked": "•••• •••• •••• 1234",
    "last4": "1234",
    "brand": "Запасная",
    "label": "",
    "status": "DISABLED"
  }
]
```

Documented card statuses: `ACTIVE` (default listing), `DISABLED`, `PENDING`.

### GET signature

As at the top of this file: empty idempotency-key, hash of empty body. Query `onlyActive` does **not** appear in the official string_to_sign formula: the signed `PATH` is `/api/v1/cards` (as written in docs). Do not add the query to PATH unless docs require it.

---

## Errors and traps

- `json=` / pretty-print / different key order after a second dumps → bad signature.
- `ts` older/newer than 300 s.
- Repeating a payout with a **new** Idempotency-Key.
- Mixing payments `X-Secret` with payout SECRET.
- `amountRub` outside 1000…87500.
- Both or neither of `cardId` and `cardNumber` (exactly one is required — phrased as "either … or").
