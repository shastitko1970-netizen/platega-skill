# Callbacks

Официально (docs.platega.io, 2026-08-26):

- [Callback об изменении статуса транзакции](https://docs.platega.io/callback-об-изменении-статуса-транзакции-29209725e0.md)
- [CallbackPayload](https://docs.platega.io/callbackpayload-13226220d0.md)
- [Callback по списанию](https://docs.platega.io/callback-по-списанию-40029713e0.md)
- [Callback по статусу подписки](https://docs.platega.io/callback-по-статусу-подписки-40030962e0.md)
- [CallbackSubscriptionStatus](https://docs.platega.io/callbacksubscriptionstatus-16438868d0.md)

GitBook: [Callback](https://platega-io.gitbook.io/platega.io-api-dokumentaciya/api-docs/callback.md), [Фейковый CallBack](https://platega-io.gitbook.io/platega.io-api-dokumentaciya/feikovyi-callback-dlya-testirovaniya-platezhei.md).

Platega **вызывает ваш** endpoint. URL задаётся в ЛК: **Настройки → Callback URLs**. Это не исходящий вызов мерчанта.

## Общие правила доставки

Метод: **POST**, JSON-тело.

Заголовки от поставщика:

| Header | Назначение |
| --- | --- |
| `X-MerchantId` | ваш MerchantId (UUID) |
| `X-Secret` | ваш API ключ |

**Подписи тела нет.** Проверка — сравнить оба заголовка с эталоном через constant-time (`hmac.compare_digest` в Python, аналог в других языках). Не использовать `==`. Не «доверять» источнику по IP без сверки секрета.

Проза платежного callback (docs):

- успех — **CONFIRMED**
- неуспех — **CANCELED**
- возврат денежных средств — **CHARGEBACKED**

Схема `CallbackPayload` и enum поля `status` на странице callback платежа содержат только `CONFIRMED` и `CANCELED`. `CHARGEBACKED` есть в прозе и в `PaymentStatus`. Обрабатывай все три, если придёт `CHARGEBACKED`.

Таймаут: если нет успешного ответа за **60 секунд**, запрос отменяется, затем **до 3** повторов с интервалом **5 минут**.

GitBook формулирует то же: «Транзакция будет отправлена повторно 3 раза, с интервалом 5 минут».

### Требования к URL callback (только docs, не GitBook)

- Только **HTTPS** (HTTP запрещён)
- Только публичные IP или доменные имена
- Корректный SSL от доверенного CA
- Запрещены self-signed
- Запрещены частные диапазоны: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.0/8`
- Запрещены localhost и loopback

Отвечай **HTTP 200**, чтобы остановить ретраи.

## 1. Callback статуса обычного платежа

Webhook OpenAPI: `paymentStatus`.

Заголовки `X-MerchantId`, `X-Secret` — required в этой спецификации.

### Тело

Required: `id`, `amount`, `currency`, `status`.

| Поле | Тип | Описание |
| --- | --- | --- |
| `id` | uuid | ID транзакции |
| `amount` | number (float) | |
| `currency` | string | |
| `status` | string | enum схемы: `CONFIRMED`, `CANCELED`; проза также `CHARGEBACKED` |
| `paymentMethod` | integer | ID метода оплаты (example `2`) |
| `payload` | string | дополнительные данные |

Регистр полей — **camelCase** (`id`, `amount`, `paymentMethod`).

Схема `CallbackPayload`: `additionalProperties: false`; required без `paymentMethod`; `paymentMethod` optional integer.

### Примеры (официальные)

Успех:

```json
{
  "id": "00000000-0000-0000-0000-000000000000",
  "amount": 1000,
  "currency": "RUB",
  "status": "CONFIRMED",
  "paymentMethod": 2
}
```

Неуспех:

```json
{
  "id": "00000000-0000-0000-0000-000000000000",
  "amount": 1000,
  "currency": "RUB",
  "status": "CANCELED",
  "paymentMethod": 2
}
```

GitBook-пример без `payload`, те же четыре обязательных поля + `paymentMethod`.

Ожидаемый ответ мерчанта: `200`.

## 2. Callback по списанию подписки

«Приходит на каждое списание — успешное и неуспешное. Отличается от callback'а обычного платежа только двумя дополнительными полями: `SubscriptionId` и `NextChargeAt`.»

Фактически схема использует **PascalCase** (`Id`, `Amount`, …) — это не «те же поля в camelCase».

Заголовки `X-MerchantId`, `X-Secret` в OpenAPI этой ручки marked `required: false` (в отличие от платежного callback). Всё равно сверять, если пришли.

### Тело (все поля required в схеме)

| Поле | Тип | Описание |
| --- | --- | --- |
| `Id` | string | ID **транзакции-списания** (новый на каждое списание) |
| `Amount` | integer | |
| `Currency` | string | |
| `Status` | `PaymentStatus` | `CONFIRMED` — деньги списаны, баланс пополнен (сумма за вычетом комиссии). `CANCELED` — списание не прошло: баланс не меняется, `NextChargeAt = null`, подписка → `PastDue`, провайдер **не** ретраит |
| `PaymentMethod` | integer | example `6` |
| `Payload` | string | example `""` |
| `SubscriptionId` | string | ID подписки |
| `NextChargeAt` | string | ISO-8601 или `null` при CANCELED |

### Примеры

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

`CANCELED` по списанию ≠ отмена подписки мерчантом. Отмена подписки приходит отдельным callback статуса (`SUBSCRIPTION_CANCELLED`).

## 3. Callback по статусу подписки

«Приходит при смене статуса. В нём `Id` = `SubscriptionId` (ID подписки, не транзакции).»

### Тело

Те же имена полей, что у списания (PascalCase). `Status` — `CallbackSubscriptionStatus`, не `PaymentStatus`.

| Status | Описание схемы |
| --- | --- |
| `SUBSCRIPTION_ACTIVATED` | Подписка активна, списания по расписанию |
| `SUBSCRIPTION_PAST_DUE` | Перманентный: из него нет переходов в другой статус, если нет вебхука об успешной оплате или отмене |
| `SUBSCRIPTION_CANCELLED` | Переход из ACTIVATED или PAST_DUE — явная отмена мерчантом или плательщиком (ссылка отмены или API) |
| `SUBSCRIPTION_FAILED` | Переход из ACTIVATED — невозможность привязки при первой активации (провайдер вернул ошибку или не подтвердил согласие) |

Проза create: если за 30 минут привязки нет — подписка `Failed`. Соотносить с `SUBSCRIPTION_FAILED` осторожно: схема FAILED описывает ошибку привязки «из ACTIVATED».

### Пример (официальный «confirmed»)

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

Второй example на той же странице — **чужой** camelCase платежный callback (`id`/`status: CANCELED`/`paymentMethod: 2`). Не использовать как образец статуса подписки; это конфликт внутри страницы.

## Фейковый callback (GitBook + ЛК)

Страница GitBook: создать транзакцию **в личном кабинете**, нажать кнопку — откроется список доступных фейковых callback.

- успех: **CONFIRMED** («Потдвержденно» — орфография источника)
- неуспех: **CANCELED**

Официальный llms.txt эту страницу не включает; функциональность ЛК упоминается в задаче skill и в GitBook.

## Реализация приёмника (ориентир)

```python
import hmac
from flask import Flask, request, abort

app = Flask(__name__)
MERCHANT_ID = "..."  # из env, не из репозитория
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
    # camelCase платёж vs PascalCase подписка — смотри ключи
    return "", 200
```

Не логируй `X-Secret`. Идемпотентность: один и тот же callback может прийти повторно (ретраи).
