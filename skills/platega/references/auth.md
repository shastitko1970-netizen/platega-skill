# Авторизация Platega

Источник: [Авторизация](https://docs.platega.io/авторизация-1991638m0.md) (docs.platega.io, 2026-08-26). Payout HMAC: [Создаёт вывод на рублёвую карту](https://docs.platega.io/создаёт-вывод-на-рублёвую-карту-через-payout-api-2232954m0.md) и [Получение сохранённых карт](https://docs.platega.io/получение-сохранённых-карт-39075563e0.md).

GitBook-двойник (не противоречит по заголовкам платежей): [Аутентификация запроса](https://platega-io.gitbook.io/platega.io-api-dokumentaciya/api-docs/autentifikaciya-zaprosa.md).

## Базовый URL

Официально:

```
https://app.platega.io/
```

Все запросы — **JSON** по **HTTPS**.

Неофициально/конфликт: в сторонних индексах (Context7) встречался хост `api.platega.io`. По умолчанию использовать только `https://app.platega.io/`. Пример Payout в официальных docs тоже ходит на `https://app.platega.io`.

## Модель 1 — платежи, отчёты, подписки, возвраты, баланс

Заголовки (оба обязательны):

| Key | Value | Где взять |
| --- | --- | --- |
| `X-MerchantId` | UUID мерчанта | ЛК → Настройки; также выдаёт менеджер при подключении |
| `X-Secret` | API ключ мерчанта | ЛК → Настройки |

Так авторизуются:

- `POST /transaction/process`
- `POST /v2/transaction/process`
- `GET /transaction/{id}`
- `GET /h2h/{id}`
- `POST /transaction/export/csv|excel|json`
- `GET /balance/all`
- `GET /transaction/{id}/cancel-supported`
- `POST /transaction/{id}/cancel`
- `GET /subscription`, `GET /subscription/{id}`, `POST /subscription/{id}/cancel`

Пример:

```http
POST /transaction/process HTTP/1.1
Host: app.platega.io
Content-Type: application/json
X-MerchantId: 1a021d91-9b26-4762-b303-5d4aac74e921
X-Secret: <X-Secret из ЛК>
```

Ошибки (как в OpenAPI платежей):

| HTTP | Смысл |
| --- | --- |
| `401` | Ошибка аутентификации (проверьте `X-MerchantId` / `X-Secret`) |
| `400` | Ошибка валидации запроса |

Не логировать и не коммитить `X-Secret`.

## Модель 2 — Payout API и сохранённые карты

Отдельный контур. Подключается менеджером; после этого в ЛК появляется раздел **Payout API**.

- SECRET **другой**, не `X-Secret` платежей.
- Ключ выдаётся в ЛК, хранится только у мерчанта: «Platega не имеет к нему доступа после выдачи».
- Показывается **один раз** сразу после генерации. Повторно просмотреть нельзя.
- Сброс: раздел Payout API, подтверждение кодом из email. Новый ключ тоже один раз. Сброс **немедленно** инвалидирует старый ключ — запросы со старой подписью начнут получать ошибку аутентификации.

### Заголовок

```
Authorization: PG-HMAC kid={MERCHANT_ID}, ts={unix}, sig={base64}
```

- `kid` — тот же MerchantId (UUID).
- `ts` — unix-время в секундах. Сервер принимает окно **±300 секунд**.
- `sig` — `Base64(HMAC-SHA256(SECRET, string_to_sign))`.

На **записях вывода** обязателен заголовок `Idempotency-Key` (уникальная строка, например UUID). Та же строка входит в `string_to_sign`.

### string_to_sign

Элементы через `\n` (LF).

**POST** `/api/v1/payouts/card-rub`:

```
METHOD
PATH
timestamp
idempotency-key
sha256_hex(body)
```

Пример каркаса:

```
POST
/api/v1/payouts/card-rub
1719403200
00000000-0000-0000-0000-446655440000
<sha256 hex тела, строчные буквы>
```

**GET** `/api/v1/cards`:

```
METHOD
PATH
timestamp
<пустая строка — idempotency-key не используется>
sha256_hex(empty)
```

То есть между timestamp и хешем тела — пустая строка (два перевода `\n` подряд).

SHA-256 пустого тела (документированная константа):

```
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

`sha256_hex(body)` — hex **строчными** буквами. Тело сериализуется **без лишних пробелов** (`json.dumps(..., separators=(",", ":"))`). Те же байты идут и в подпись, и в HTTP-тело. Если клиент сериализует заново (`json=` в requests), подпись не сойдётся.

Готовый CLI: [scripts/payout_sign.py](../scripts/payout_sign.py).

### Заголовки POST вывода

| Заголовок | Обязательный | Пример |
| --- | --- | --- |
| `Authorization` | да | `PG-HMAC kid=29ef0000-..., ts=1719403200, sig=abc123==` |
| `Idempotency-Key` | да | UUID |
| `Content-Type` | да | `application/json` |

### Заголовки GET карт

| Заголовок | Обязательный |
| --- | --- |
| `Authorization` | да (`PG-HMAC ...`) |

`X-MerchantId` / `X-Secret` для этих двух ручек **не** документированы как способ авторизации.

## Callback (входящий)

Platega вызывает URL из ЛК (Настройки → Callback URLs) и сама присылает заголовки `X-MerchantId` + `X-Secret`. **Подписи тела нет.** Сверяй оба заголовка через `hmac.compare_digest` (constant-time), не через `==`.

Подробности: [callbacks.md](callbacks.md).

## Практические правила

- Платежный `X-Secret` и payout `SECRET` — разные ключи.
- Не подставляй payout HMAC на `/transaction/*` и наоборот.
- `ts` вне ±300 с → отказ, даже при верной подписи.
- Новый `Idempotency-Key` = новый вывод. Повтор того же вывода — тот же ключ и то же тело.
