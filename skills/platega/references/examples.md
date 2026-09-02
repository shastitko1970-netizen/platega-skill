# Why this skill: prompt → agent without it / with it

These are not a recorded chat. They are worked examples of typical prompts. "Without skill" is assembled from real doc traps: the agent reads GitBook or invents a Stripe-like API. "With skill" is the docs.platega.io contract as of 2026-09-02.

If an agent without the skill already emits the right-hand request, you do not need the skill for that step. On Platega you almost always do: two doc layers, field typos, two auth models.

---

## 1. One-off SBP + antifraud

**Prompt**

> Write Python: create a Platega payment of 500 RUB via SBP. This shop is in a category where the manager required userId for antifraud. Payer telegram id `80422110`. After pay, return to `https://shop.example/ok`, on error `/fail`.

### Without skill

The agent googles GitBook, injects a client UUID, uses a stale method table, and stuffs antifraud into `payload`:

```python
# typical miss
body = {
    "id": str(uuid.uuid4()),          # current API: do not send
    "paymentMethod": 10,              # GitBook CardRu; SBP is 2 now
    "paymentDetails": {"amount": 500, "currency": "RUB"},
    "description": "order",
    "return": "https://shop.example/ok",
    "payload": "user=80422110",       # antifraud does not read this
}
requests.post("https://app.platega.io/transaction/process", json=body, headers=headers)
```

What happens: `400` / "already exists" on a reused `id`, antifraud off, shop risk of disable.

### With skill

Reads `SKILL.md` → `payments.md` + `scenarios.md`. No `id`. Method `2`. Stable `metadata.userId`.

```python
headers = {
    "Content-Type": "application/json",
    "X-MerchantId": MERCHANT_ID,
    "X-Secret": SECRET,
}
body = {
    "paymentMethod": 2,
    "paymentDetails": {"amount": 500, "currency": "RUB"},
    "description": "Order 500 RUB",
    "return": "https://shop.example/ok",
    "failedUrl": "https://shop.example/fail",
    "metadata": {
        "userId": "80422110",
        "userName": "telegram:80422110",
    },
}
r = requests.post("https://app.platega.io/transaction/process", json=body, headers=headers, timeout=30)
data = r.json()
# send payer to data["redirect"]; status: callback or GET /transaction/{data["transactionId"]}
```

---

## 2. H2H QR in your own UI

**Prompt**

> I need H2H: I draw the QR on my site, no redirect to pay.platega.io. SBP, 136.12 RUB.

### Without skill

Either `GET /h2h/{random uuid}` immediately, or parse GitBook and wait for a card number:

```python
# miss A — no transaction
requests.get(f"https://app.platega.io/h2h/{uuid.uuid4()}", headers=headers)
# 400 "Transaction not found"

# miss B — GitBook fields
acc = data["accountNumber"]   # not in current docs
```

### With skill

1. Confirm the manager enabled H2H.
2. `POST /transaction/process` with method `2`, no `id`.
3. `GET /h2h/{transactionId}`.
4. Render `qr` (NSPK URL) and `amount`. Status is a separate poll/callback.

```python
created = requests.post(
    "https://app.platega.io/transaction/process",
    headers=headers,
    json={
        "paymentMethod": 2,
        "paymentDetails": {"amount": 136.12, "currency": "RUB"},
        "description": "H2H order",
        "return": "https://shop.example/ok",
        "failedUrl": "https://shop.example/fail",
        "metadata": {"userId": "80422110", "userName": "site:80422110"},
    },
    timeout=30,
).json()
h2h = requests.get(
    f"https://app.platega.io/h2h/{created['transactionId']}",
    headers=headers,
    timeout=30,
).json()
# h2h == {"amount": 136.12, "qr": "https://qr.nspk.ru/..."}
```

---

## 3. Monthly subscription

**Prompt**

> Recurring: 500 RUB every month via SBP. Grant access immediately after create.

### Without skill

Confuses subscription with payment method 2, or sends method 6 but treats create as money:

```python
body = {
    "paymentMethod": 2,  # one-off SBP, not a subscription
    "paymentDetails": {"amount": 500, "currency": "RUB"},
    ...
}
# or method 6, but:
if created["status"] == "PENDING":
    grant_premium(user)   # no money yet, no bind yet
```

Callback code waits for camelCase `id` / `status` and misses charges.

### With skill

```python
created = requests.post(
    "https://app.platega.io/transaction/process",
    headers=headers,
    json={
        "paymentMethod": 6,
        "paymentDetails": {
            "amount": 500,
            "currency": "RUB",
            "interval": 3,
            "intervalCount": 1,
        },
        "description": "Premium subscription",
    },
    timeout=30,
).json()
subscription_id = created["transactionId"]  # this is subscriptionId
# redirect to created["redirect"] IMMEDIATELY, 30-minute window
# grant access only after SUBSCRIPTION_ACTIVATED or a CONFIRMED charge
```

Charge webhook (PascalCase):

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

`Status: CANCELED` → do not retry: `PastDue`, `NextChargeAt` null.

---

## 4. Callback "just check headers =="

**Prompt**

> Write a FastAPI callback for Platega.

### Without skill

Looks for a Stripe/YooKassa body HMAC, or compares secrets with `==` (timing leak), or listens on `http://`.

### With skill

Platega echoes your own `X-MerchantId` and `X-Secret`. No body signature. Compare only with `hmac.compare_digest`. URL must be HTTPS, public, real CA cert. Answer 200 within 60 seconds.

```python
import hmac
from fastapi import FastAPI, Header, Request, Response

app = FastAPI()

@app.post("/platega/callback")
async def cb(
    request: Request,
    x_merchantid: str = Header(default=""),
    x_secret: str = Header(default=""),
):
    ok_m = hmac.compare_digest(x_merchantid, MERCHANT_ID)
    ok_s = hmac.compare_digest(x_secret, SECRET)
    if not (ok_m and ok_s):
        return Response(status_code=401)
    payload = await request.json()
    # one-off: payload["id"], payload["status"] in {CONFIRMED, CANCELED, CHARGEBACKED}
    # subscription charge: keys Id / SubscriptionId / NextChargeAt
    return Response(status_code=200)
```

---

## 5. Card payout

**Prompt**

> Pay out 1500 RUB to card `2200…0000`. If it fails, just retry the request.

### Without skill

Sends payment `X-Secret`, or `json=body` (bytes ≠ signature), or on retry mints a new UUID and pays out twice.

### With skill

Separate payout SECRET, `PG-HMAC`, same bytes you signed, one `Idempotency-Key` per payout. Script: `scripts/payout_sign.py`.

```bash
python skills/platega/scripts/payout_sign.py \
  --merchant-id "$MERCHANT_ID" \
  --secret "$PAYOUT_SECRET" \
  --card-number 2200000000000000 \
  --amount 1500 \
  --idempotency-key order-42-payout
```

Retry of the same payout = same `--idempotency-key`. A new key = another 1500 RUB.

---

## 6. Shop order number (`orderId`)

**Prompt**

> Create an SBP payment for 1500 RUB. My internal order id is `INV-8841`. I need to find this payment later by that id.

### Without skill

Puts `INV-8841` in `id` (GitBook) or invents `externalId` / `merchantOrderId` on create:

```python
body = {
    "id": "INV-8841",                 # current API: do not send; not even a UUID
    "paymentMethod": 2,
    ...
}
```

### With skill

`id` is issued by Platega. Your number is optional `orderId` (create pages since 2026-09-01). Not required. Not documented as coming back as `externalId`.

```python
body = {
    "paymentMethod": 2,
    "paymentDetails": {"amount": 1500, "currency": "RUB"},
    "description": "Invoice INV-8841",
    "return": "https://shop.example/ok",
    "failedUrl": "https://shop.example/fail",
    "orderId": "INV-8841",
    "metadata": {"userId": "80422110", "userName": "shop:80422110"},
}
```

Correlate on the `transactionId` from the response; keep `orderId` in your DB. Subscription create OpenAPI still has no `orderId`.

---

## What the skill changes in the agent's head

| Topic | Without skill | With skill |
| --- | --- | --- |
| Create `id` | client UUID / shop order like GitBook | do not send; optional `orderId` for your number |
| SBP | method 10 / "P2P 1–9" | `2` |
| Antifraud | `payload` or nothing | `metadata.userId` |
| Hosted v2 | reads `redirect` | reads `url` |
| H2H | GitBook card / GET without create | create → `{amount, qr}` |
| Subscription | method 2 + "access now" | method `6`, wait for activation |
| Callback | body HMAC | compare_digest on headers |
| Payout | same X-* headers | PG-HMAC + idempotency |
