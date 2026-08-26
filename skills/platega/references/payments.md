# Платежи

Официальные страницы docs.platega.io (2026-08-26):

- [Создание платежной ссылки с заданным методом](https://docs.platega.io/создание-платежной-ссылки-с-заданным-методом-29203843e0.md) — `POST /transaction/process`
- [Создание платежной ссылки без заданного метода](https://docs.platega.io/создание-платежной-ссылки-без-заданного-метода-33845703e0.md) — `POST /v2/transaction/process`
- [Проверка статуса оплаты платежа](https://docs.platega.io/проверка-статуса-оплаты-платежа-29203844e0.md) — `GET /transaction/{id}`
- [Получение QR-кода для H2H-транзакции](https://docs.platega.io/получение-qr-кода-для-h2h-транзакции-34794775e0.md) — `GET /h2h/{id}`
- Схемы: [CreateTransactionRequest](https://docs.platega.io/createtransactionrequest-13226217d0.md), [CreateTransactionResponse](https://docs.platega.io/createtransactionresponse-13226218d0.md), [TransactionStatusResponse](https://docs.platega.io/transactionstatusresponse-13226219d0.md), [PaymentMethodInt](https://docs.platega.io/paymentmethodint-13226216d0.md), [PaymentStatus](https://docs.platega.io/paymentstatus-13226215d0.md)

Base: `https://app.platega.io/`  
Auth: `X-MerchantId` + `X-Secret` (см. [auth.md](auth.md)).

**Не передавай поле `id` при создании.** Официальный текст обеих create-ручек: «ID транзакции генерируется системой автоматически — не передавайте поле `id` в запросе.» Схема `CreateTransactionRequest`: «Не указывайте поле `id`». GitBook-примеры с клиентским UUID — устарели ([legacy-gitbook.md](legacy-gitbook.md)).

`POST /transaction/process` также создаёт **подписку**, если `paymentMethod` равен `6`. Это не метод из `PaymentMethodInt`. См. [subscriptions.md](subscriptions.md).

---

## Методы оплаты (текущий PaymentMethodInt)

Официальный enum схемы `PaymentMethodInt`:

| int | Имя в схеме | Имя в ответе (пример) |
| --- | --- | --- |
| `2` | СБП (QR-код) | `SBPQR` |
| `3` | ЕРИП | — |
| `11` | Карточный эквайринг | — |
| `12` | Международная оплата | — |
| `13` | Криптовалюта | — |
| `14` | Sberpay | — |

Вне этой таблицы:

| int | Где | Заметки |
| --- | --- | --- |
| `6` | Create subscription | Всегда число `6`, не строка. Нет в `PaymentMethodInt`. |
| `10` | GitBook CardRu | «Карточный 2дс, оплата картами МИР». Нет в текущей схеме. |
| `1`–`9` | GitBook P2P | «Все остальные методы, включая метод 1, 2–9, связаны с P2P». Конфликт: `2` в текущих docs — СБП QR. |

### Крипто (`13`)

По умолчанию пользователь уходит на **веб-пейформу**. Оплата через Telegram-бота — обратиться к менеджеру.

### Метаданные / антифрод

Для магазинов отдельных категорий нужно передавать `metadata` с идентификатором плательщика. Уточнять у менеджера.

Отсутствие **`metadata.userId`** при наличии требования отключает антифрод и **может привести к отключению магазина**.

В примерах create (оба endpoint) `metadata` содержит `userId`, `userName`, `clientIp`. В OpenAPI объекта `metadata` required указаны `userId` и `userName`; `clientIp` есть в example, в properties схемы его нет.

---

## POST `/transaction/process` — ссылка с заданным методом

`operationId`: `createTransaction`

### Заголовки

| Header | Required |
| --- | --- |
| `X-MerchantId` | да |
| `X-Secret` | да |

`Content-Type: application/json` подразумевается (JSON API).

### Тело

По OpenAPI **этой** ручки `required`: `paymentMethod`, `paymentDetails`, `description`, `return`, `failedUrl`.

Отдельная схема `CreateTransactionRequest` требует только `paymentMethod` + `paymentDetails` и описывает остальные как optional. Для вызова **платежа** ориентируйся на required ручки (пять полей). Для **подписки** required другие — см. [subscriptions.md](subscriptions.md).

| Поле | Тип | Required (ручка платежа) | Описание |
| --- | --- | --- | --- |
| `paymentMethod` | integer (`PaymentMethodInt`) | да | `2`, `3`, `11`, `12`, `13`, `14` |
| `paymentDetails` | object | да | |
| `paymentDetails.amount` | number | да | Сумма |
| `paymentDetails.currency` | string | да | Например `RUB` |
| `description` | string | да | Назначение. Схема: «указывайте по возможности всегда» |
| `return` | string (uri) | да | Редирект при успехе |
| `failedUrl` | string (uri) | да | Редирект при неуспехе |
| `payload` | string | нет | Доп. информация для вашей системы |
| `metadata` | object | нет* | *обязателен для части категорий |
| `metadata.userId` | string | если есть metadata | Уникальный ID плательщика (напр. Telegram user ID), антифрод |
| `metadata.userName` | string | если есть metadata | Доп. данные о плательщике |
| `id` | — | **не передавать** | Генерирует система |

### Ответ 200 — `CreateTransactionResponse`

Required схемы: `transactionId`, `status`.

| Поле | Тип | Описание |
| --- | --- | --- |
| `paymentMethod` | string | Человекочитаемое имя (описание схемы: «например, 2»; example: `SBPQR`) |
| `transactionId` | string (uuid) | ID созданной транзакции |
| `redirect` | string (uri) | Ссылка для оплаты |
| `return` | string (uri) | Ваш success-редирект |
| `paymentDetails` | string **или** `{amount, currency}` | В example — строка `"100 RUB"` |
| `status` | `PaymentStatus` | Обычно `PENDING` |
| `expiresIn` | string | Время до истечения `HH:MM:SS` (example `00:15:00`) |
| `merchantId` | string (uuid) | |
| `usdtRate` | number (float) | Курс конвертации в USDT в момент оплаты (GitBook-комментарий к тому же полю) |

### Ошибки

| HTTP | Описание в OpenAPI |
| --- | --- |
| `400` | Ошибка валидации запроса |
| `401` | Ошибка аутентификации (проверьте X-MerchantId / X-Secret) |

GitBook 400 для P2P (не в текущем OpenAPI): `No available requisites`, `Transaction … already exists` — [legacy-gitbook.md](legacy-gitbook.md).

### Пример

```http
POST /transaction/process HTTP/1.1
Host: app.platega.io
Content-Type: application/json
X-MerchantId: 1a021d91-9b26-4762-b303-5d4aac74e921
X-Secret: <secret>
```

```json
{
  "paymentMethod": 2,
  "paymentDetails": {
    "amount": 500,
    "currency": "RUB"
  },
  "description": "Оплата мешков картошки клиенту №293",
  "return": "https://google.com/success",
  "failedUrl": "https://google.com/fail",
  "payload": "Дополнительная информация о платеже",
  "metadata": {
    "userId": "123456789",
    "userName": "@username",
    "clientIp": "111.47.86.11"
  }
}
```

Ответ (официальный example):

```json
{
  "paymentMethod": "SBPQR",
  "transactionId": "3fa85f64-5717-4562-b3fc-2c463f66afa6",
  "redirect": "https://pay.platega.io?qrsbp",
  "return": "https://google.com",
  "paymentDetails": "100 RUB",
  "status": "PENDING",
  "expiresIn": "00:15:00",
  "merchantId": "1a021d91-9b26-4762-b303-5d4aac74e921",
  "usdtRate": 93.45
}
```

Плательщика отправить на `redirect`.

---

## POST `/v2/transaction/process` — без заданного метода

Плательщик сам выбирает способ на hosted page.

`operationId` в OpenAPI тоже `createTransaction` (коллизия имени с v1).

### Заголовки

Те же: `X-MerchantId`, `X-Secret` (required).

### Тело

**Нет** `paymentMethod`. Required: `paymentDetails`, `description`, `return`, `failedUrl`.

| Поле | Тип | Required | Описание |
| --- | --- | --- | --- |
| `paymentDetails.amount` | number | да | |
| `paymentDetails.currency` | string | да | |
| `description` | string | да | |
| `return` | string | да | Success URL |
| `failedUrl` | string | да | Fail URL |
| `payload` | string | нет | |
| `metadata.userId` / `userName` | string | если передаёте metadata | Те же правила антифрода |
| `id` | — | **не передавать** | |

Текст про `paymentMethod: 13` / Telegram-бота присутствует и на этой странице, хотя метода в запросе нет (копипаст описания).

### Ответ 200

Required: `transactionId`, `status`, `url`, `expiresIn`, `rate`.

| Поле | Тип | vs v1 |
| --- | --- | --- |
| `transactionId` | string | то же |
| `status` | string | то же |
| `url` | string | **не** `redirect` |
| `expiresIn` | string | то же |
| `rate` | number | **не** `usdtRate` |

Нет `paymentMethod`, `redirect`, `return`, `paymentDetails`, `merchantId` в схеме ответа v2.

### Ошибки

`400` валидация, `401` аутентификация.

### Пример

```json
{
  "paymentDetails": {
    "amount": 500,
    "currency": "RUB"
  },
  "description": "Оплата мешков картошки клиенту №293",
  "return": "https://google.com/success",
  "failedUrl": "https://google.com/fail",
  "payload": "Дополнительная информация о платеже",
  "metadata": {
    "userId": "123456789",
    "userName": "@username",
    "clientIp": "111.47.86.11"
  }
}
```

```json
{
  "transactionId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "PENDING",
  "url": "https://pay.platega.io/?id=f8000067-a4a0-0000-0000-2556a0b40000&mh=0a0000a4-0000-0000-0000-200004060000",
  "expiresIn": "00:15:00",
  "rate": 91.2
}
```

Плательщика отправить на `url`.

---

## GET `/transaction/{id}` — статус

`operationId`: `getTransactionStatus`

### Параметры

| Имя | In | Required | Описание |
| --- | --- | --- | --- |
| `id` | path | да | UUID транзакции |
| `X-MerchantId` | header | да | |
| `X-Secret` | header | да | |

### Ответ 200 — `TransactionStatusResponse`

Поля **как в схеме** (опечатки сохранены):

| Поле | Тип | Описание |
| --- | --- | --- |
| `id` | uuid | |
| `status` | `PaymentStatus` | `PENDING` \| `CANCELED` \| `CONFIRMED` \| `CHARGEBACKED` |
| `paymentDetails` | `{amount, currency}` | |
| `merchantName` | string | |
| `mechantId` | uuid | Опечатка в API: нет «r» |
| `comission` | number | Опечатка: одно «m» |
| `paymentMethod` | string | Например `SBPQR` |
| `expiresIn` | string | |
| `return` | uri | |
| `comissionUsdt` | number | |
| `amountUsdt` | number | |
| `qr` | string | Example: `base64-qr-data-or-url` |
| `payformSuccessUrl` | uri | |
| `payload` | string | |
| `comissionType` | integer | Example: `1` |
| `externalId` | string | |
| `description` | string | |

### Ошибки

| HTTP | Описание |
| --- | --- |
| `404` | Транзакция не найдена |

### Пример ответа (официальный)

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "PENDING",
  "paymentDetails": {
    "amount": 2000,
    "currency": "RUB"
  },
  "merchantName": "Demo Merchant",
  "mechantId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "comission": 0,
  "paymentMethod": "SBPQR",
  "expiresIn": "00:15:00",
  "return": "https://example.com/success",
  "comissionUsdt": 1.64044944,
  "amountUsdt": 10.8988764,
  "qr": "base64-qr-data-or-url",
  "payformSuccessUrl": "https://pay.platega.io/success",
  "payload": "custom-payload",
  "comissionType": 1,
  "externalId": "0000a4f3-0000-0000-b8ac-fcb675a0000a",
  "description": "Оплата заказа #12345"
}
```

GitBook для этой же ручки перечисляет ещё `EXPIRED` и `FAILED` — [legacy-gitbook.md](legacy-gitbook.md).

---

## GET `/h2h/{id}` — QR / ссылка H2H

«Если вы хотите принимать платежи в режиме H2H — обратитесь к вашему менеджеру для подключения.»

`operationId` в OpenAPI снова `createTransaction` (коллизия имён).

### Параметры

| Имя | In | Required |
| --- | --- | --- |
| `id` | path (uuid транзакции) | да |
| `X-MerchantId` | header | да |
| `X-Secret` | header | да |

### Ответ 200 (текущие docs)

Required: `amount`, `qr`.

| Поле | Тип |
| --- | --- |
| `amount` | number |
| `qr` | string (example — URL `https://qr.nspk.ru/...`) |

```json
{
  "amount": 136.12,
  "qr": "https://qr.nspk.ru/00000000000000000000000000?type=00&bank=000000000000&sum=00000&cur=RUB&crc=0000"
}
```

### Ошибки

| HTTP | Описание в OpenAPI |
| --- | --- |
| `400` | Транзакция не найдена |

(На статусе платежа «не найдена» — `404`. Здесь в спецификации указан `400`.)

### GitBook H2H (конфликт)

GitBook «Создание платежа H2H — вывод реквизитов» описывает другой JSON: `accountNumber`, `maskedAccountNumber`, `accountName`, `method`, `amount`. См. [legacy-gitbook.md](legacy-gitbook.md). По умолчанию для текущей интеграции использовать `{amount, qr}`.

---

## Статусы платежа

Официальный `PaymentStatus`: `PENDING`, `CANCELED`, `CONFIRMED`, `CHARGEBACKED`.

Callback платежа в схеме enum только `CONFIRMED` и `CANCELED`, но проза той же страницы добавляет `CHARGEBACKED` при возврате. См. [callbacks.md](callbacks.md).

---

## Практический порядок

1. Создать транзакцию (v1 с методом или v2 без).
2. Сохранить `transactionId` из ответа (не из запроса).
3. Отправить плательщика на `redirect` (v1) или `url` (v2).
4. Для H2H: после create вызвать `GET /h2h/{transactionId}`.
5. Ждать callback и/или поллить `GET /transaction/{id}`.
6. Идемпотентность учёта строить на `transactionId`, не на клиентском UUID.
