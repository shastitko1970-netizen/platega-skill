# Reports, balances, rates

Official in llms.txt (docs.platega.io, 2026-08-26):

- [Get balances](https://docs.platega.io/получение-балансов-33582950e0.md) — `GET /balance/all`
- [Export transactions to CSV](https://docs.platega.io/выгрузка-транзакций-в-csv-37963792e0.md)
- [Export transactions to Excel](https://docs.platega.io/выгрузка-транзакций-в-excel-37963794e0.md)
- [Export transactions to Json](https://docs.platega.io/выгрузка-транзакций-в-json-37991987e0.md)

Auth for all official endpoints below: `X-MerchantId` + `X-Secret`. Base: `https://app.platega.io/`.

---

## GET `/balance/all`

Description: "Get balances".

### Headers

| Header | Required | Schema |
| --- | --- | --- |
| `X-MerchantId` | yes | uuid |
| `X-Secret` | yes | string |

### 200 response

Array of objects:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `amount` | number | yes | |
| `currency` | string | yes | example: `RUB`, `USDT` |
| `frozenBalance` | integer | no | present on USDT in the example |

```json
[
  {
    "amount": 15000.5,
    "currency": "RUB"
  },
  {
    "amount": 200,
    "currency": "USDT",
    "frozenBalance": 500
  }
]
```

Needed for refunds: `cancel-supported` requires sufficient USDT **or** RUB.

The page describes no other HTTP codes.

---

## Shared export filter

The three export endpoints take the same JSON body. All schema fields are optional (required is unset).

| Field | Type | Example |
| --- | --- | --- |
| `statuses` | array of string | `"6"`, `"7"` |
| `paymentMethods` | array of string | `"2"`, `"11"` |
| `from` | string | `2026-05-01T00:00:00.000Z` |
| `to` | string | `2026-06-16T08:50:04.820Z` |
| `timeZoneId` | string | `UTC` |

**Do not map** `statuses: ['6','7']` onto `PaymentStatus` (`PENDING` / `CANCELED` / `CONFIRMED` / `CHARGEBACKED`). Official number → enum mapping is **unpublished**. Send as in the spec. Filter `paymentMethods` are string method numbers (`"2"`, `"11"`); in the JSON export response `paymentMethod` already arrives as a name (`SBPQR`).

### Shared export headers

| Header | Required | Example |
| --- | --- | --- |
| `X-MerchantId` | yes | |
| `X-Secret` | yes | |
| `accept` | no | `text/plain` |
| `Content-Type` | no | `application/json` |

OpenAPI examples again include real-looking secrets — do not copy them.

---

## POST `/transaction/export/csv`

"Returns a link to a CSV file of transactions matching the given filters."

### 200 response

```json
{ "url": "string" }
```

| Field | Required |
| --- | --- |
| `url` | yes |

---

## POST `/transaction/export/excel`

"Returns a link to an Excel file of transactions matching the given filters."

### 200 response

Same object `{ "url": "string" }`, `url` required.

---

## POST `/transaction/export/json`

In-page conflict on the official page:

- Description: "Returns a link to a Json file of transactions matching the given filters."
- Response schema: an **array of records**, not `{url}`.

Per schema and example — an array. There is **no** `url` field in the JSON response.

Array item (all fields required in the schema):

| Field | Type | Example |
| --- | --- | --- |
| `recordId` | string | UUID |
| `createdAt` | string | `2026-06-15 13:44:13` (not ISO in the example) |
| `amount` | integer in schema; example has both `1150` and `1.15` | do not assume a single type — schema says integer, example contains a fraction |
| `currencyCode` | string | `RUB` |
| `status` | string | `CANCELED` (here already an enum name, not `'6'`) |
| `paymentMethod` | string | `SBPQR` |
| `description` | string | |
| `payload` | string | `""` |

```json
[
  {
    "recordId": "486c22ef-3524-4a1c-9740-3fe8c3e859d9",
    "createdAt": "2026-06-15 13:44:13",
    "amount": 1150,
    "currencyCode": "RUB",
    "status": "CANCELED",
    "paymentMethod": "SBPQR",
    "description": "1234",
    "payload": ""
  }
]
```

### Request example (shared for csv/excel/json)

```http
POST /transaction/export/json HTTP/1.1
Host: app.platega.io
Content-Type: application/json
X-MerchantId: <MerchantId>
X-Secret: <X-Secret>
```

```json
{
  "statuses": ["6", "7"],
  "paymentMethods": ["2", "11"],
  "from": "2026-05-01T00:00:00.000Z",
  "to": "2026-06-16T08:50:04.820Z",
  "timeZoneId": "UTC"
}
```

---

## Extra / legacy (not in official llms.txt)

Do not treat as the current contract without checking live docs. The conversions page on docs.platega.io returns **404** for `.md` (checked 2026-08-26).

### GET `/rates/payment_method_rate` (GitBook)

Source: [Get rates](https://platega-io.gitbook.io/platega.io-api-dokumentaciya/poluchenie-kursov.md) (`poluchenie-kursov.md` in the dump).

```
GET https://app.platega.io/rates/payment_method_rate
```

Query:

| Parameter | Type | Description |
| --- | --- | --- |
| `merchantId` | UUID | merchant ID |
| `paymentMethod` | integer | payment method ID |
| `currencyFrom` | string | e.g. `RUB` |
| `currencyTo` | string | e.g. `USDT` |

Headers: `accept` (`text/plain` or `application/json`), `X-MerchantId`, `X-Secret`.

GitBook response example:

```json
{
  "paymentMethod": 2,
  "currencyFrom": "RUB",
  "currencyTo": "USDT",
  "rate": 0.0105,
  "updatedAt": "2025-08-11T10:15:00Z"
}
```

Current payment create already returns `usdtRate` / `rate` in the response — a separate rates endpoint is absent from llms.txt.

### GET `/transaction/balance-unlock-operations` (Context7 / old docs page)

Sources: Context7 snapshot and page "Get conversions method" (id `24236037e0`), which is **not** in current `llms.txt` and whose `.md` is 404.

Documented there:

| Query | Required | Example |
| --- | --- | --- |
| `from` | yes | `2025-01-01T00:00:00Z` |
| `to` | yes | `2025-11-13T23:59:59Z` |
| `page` | yes | `1` |
| `size` | yes | `20` |

Headers: `accept` (example `text/plain`), `X-MerchantId`, `X-Secret`.

200 response: `application/json`, schema `object` with **empty** `properties` — record fields are not officially described.

Mark extra/legacy. Do not invent element structure.
