# Выводы (Payout API) и сохранённые карты

Официально (docs.platega.io, 2026-08-26):

- [Создаёт вывод на рублёвую карту через Payout API](https://docs.platega.io/создаёт-вывод-на-рублёвую-карту-через-payout-api-2232954m0.md)
- [Получение сохранённых карт](https://docs.platega.io/получение-сохранённых-карт-39075563e0.md)

Base URL в официальном Python-примере: `https://app.platega.io`

Функциональность **opt-in**: по умолчанию недоступна. Доступ выдаёт менеджер; после этого в ЛК появляется раздел **Payout API**.

Auth — **не** `X-MerchantId`/`X-Secret`, а отдельный HMAC. Полная модель: [auth.md](auth.md). CLI: [scripts/payout_sign.py](../scripts/payout_sign.py).

---

## Секрет

- Отдельный SECRET (не платёжный `X-Secret`).
- Показ один раз после генерации. Повторно не посмотреть.
- Сброс в ЛК → код на email → новый ключ один раз. Старый ключ инвалидируется сразу.
- Не логировать, не коммитить.

## Подпись

```
string_to_sign = METHOD + "\n" + PATH + "\n" + timestamp + "\n" + idempotency-key + "\n" + sha256_hex(body)
sig            = Base64(HMAC-SHA256(SECRET, string_to_sign))
Authorization  = PG-HMAC kid={MERCHANT_ID}, ts={timestamp}, sig={sig}
```

- `timestamp` — unix seconds, окно сервера **±300 с**.
- `sha256_hex(body)` — hex **lowercase**.
- Тело: `json.dumps(obj, separators=(",", ":")).encode("utf-8")`. Эти же байты в HTTP (`data=`, не `json=`).

### POST вывода

`idempotency-key` — уникальная строка на каждый **новый** вывод (например UUID). Та же строка в заголовке `Idempotency-Key`. Повтор запроса с тем же ключом — идемпотентный retry. Новый ключ — второй вывод.

### GET карт

`idempotency-key` в строке подписи — **пустая строка**. Тело пустое, хеш:

```
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

То есть:

```
GET
/api/v1/cards
1719403200

e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

(пустая строка между timestamp и хешем).

---

## POST `/api/v1/payouts/card-rub`

Создаёт вывод на рублёвую карту.

### Заголовки

| Заголовок | Обязательный | Пример |
| --- | --- | --- |
| `Authorization` | да | `PG-HMAC kid=29ef0000-..., ts=1719403200, sig=abc123==` |
| `Idempotency-Key` | да | UUID |
| `Content-Type` | да | `application/json` |

### Тело

Передай **либо** `cardId` сохранённой карты, **либо** `cardNumber` полного PAN (XOR).

Сумма одного вывода: **от 1000 до 87500 RUB**.

| Поле | Тип | Обязательное | Описание |
| --- | --- | --- | --- |
| `cardId` | string | нет | ID сохранённой карты (альтернатива `cardNumber`) |
| `cardNumber` | string | нет | Номер карты получателя (16 цифр) |
| `amountRub` | integer | да | Сумма вывода в рублях |
| `payoutMethod` | string | да | Всегда `CARD` |
| `currencyRequested` | string | да | Всегда `RUB` |

```json
{"cardNumber":"2200000000000000","amountRub":1500,"payoutMethod":"CARD","currencyRequested":"RUB"}
```

(компактная сериализация без пробелов — именно её хешировать.)

### Ответ (документированный example)

```json
{
  "withdrawalRecordId": "3c0d321d-40c4-46e3-97f0-7a8f50ce03a6",
  "status": "CREATED",
  "cardMasked": "**** 0000",
  "amountUsdtDebited": 13.270341
}
```

| Поле | Тип | Описание |
| --- | --- | --- |
| `withdrawalRecordId` | string | Идентификатор созданного вывода |
| `status` | string | Сразу после создания — `CREATED`. Других значений страница не перечисляет |
| `cardMasked` | string | Маскированный номер карты |
| `amountUsdtDebited` | number | Сумма, списанная с USDT-баланса мерчанта |

HTTP-коды ошибок на странице не таблицированы. Сброшенный/неверный ключ: «ошибка аутентификации».

### Официальный Python-фрагмент (смысл)

```python
import base64, hashlib, hmac, json, time, uuid, requests

MERCHANT_ID = "ваш-merchant-id"
SECRET      = "ваш-secret-ключ"
BASE        = "https://app.platega.io"
PATH        = "/api/v1/payouts/card-rub"

body = {
    "cardNumber": "2200000000000000",  # или "cardId": "uuid сохранённой карты"
    "amountRub": 1500,                 # от 1000 до 87500 RUB
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

# Важно: data=body_bytes, не json=body
resp = requests.post(BASE + PATH, headers=headers, data=body_bytes, timeout=30)
```

Рабочий CLI без хардкода секретов: `python scripts/payout_sign.py --body '...'`.

---

## GET `/api/v1/cards`

По умолчанию только активные карты. `onlyActive=false` — также `DISABLED` и `PENDING`.

### Параметры

| Имя | In | Required | Описание |
| --- | --- | --- | --- |
| `onlyActive` | query | нет | По умолчанию можно не передавать. При `false` вернёт DISABLED и PENDING |
| `Authorization` | header | да | `PG-HMAC kid=<merchantId>, ts=<unix_timestamp>, sig=<base64_signature>` |

Example query: `onlyActive=true` (строка).

### Ответ 200

Массив объектов. Required поля каждого:

| Поле | Тип | Example |
| --- | --- | --- |
| `cardId` | string | UUID |
| `masked` | string | `•••• •••• •••• 4242` |
| `last4` | string | `4242` |
| `brand` | string | `Visa` / во втором example `Запасная` |
| `label` | string | `Основная карта` / `""` |
| `status` | string | `ACTIVE`, `DISABLED`; проза также упоминает `PENDING` |

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

Документированные статусы карт: `ACTIVE` (default-выдача), `DISABLED`, `PENDING`.

### Подпись GET

Как в шапке файла: пустой idempotency-key, хеш пустого тела. Query `onlyActive` в официальной формуле string_to_sign **не** фигурирует: в подпись идёт `PATH` = `/api/v1/cards` (как написано в docs). Не добавлять query в PATH, если docs этого не требуют.

---

## Ошибки и ловушки

- `json=` / pretty-print / другой порядок ключей после повторного dumps → неверная подпись.
- `ts` старше/новее 300 с.
- Повтор вывода с **новым** Idempotency-Key.
- Смешение `X-Secret` платежей с payout SECRET.
- `amountRub` вне 1000…87500.
- Одновременно или ни `cardId`, ни `cardNumber` (нужен ровно один вариант — так сформулировано: «либо … либо»).
