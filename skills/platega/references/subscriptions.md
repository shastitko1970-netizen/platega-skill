# Рекуррентные СБП-подписки

Официальные страницы docs.platega.io (2026-08-26):

- [Создать подписку](https://docs.platega.io/создать-подписку-40029698e0.md)
- [Получить подписку](https://docs.platega.io/получить-подписку-40029717e0.md)
- [Список подписок](https://docs.platega.io/список-подписок-40029720e0.md)
- [Отменить подписку](https://docs.platega.io/отменить-подписку-40029730e0.md)
- Callback: [по списанию](https://docs.platega.io/callback-по-списанию-40029713e0.md), [по статусу](https://docs.platega.io/callback-по-статусу-подписки-40030962e0.md) — детали в [callbacks.md](callbacks.md)
- Схемы: [SubscriptionStatus](https://docs.platega.io/subscriptionstatus-16438392d0.md), [SubscriptionInterval](https://docs.platega.io/subscriptioninterval-16441018d0.md), [CallbackSubscriptionStatus](https://docs.platega.io/callbacksubscriptionstatus-16438868d0.md)

Base: `https://app.platega.io/`  
Auth: `X-MerchantId` + `X-Secret`.

## Суть

Подписка — регулярное автосписание с плательщика через СБП. Мерчант один раз создаёт подписку и отправляет плательщика на платёжную форму; привязку, активацию и все списания делает Platega, мерчанту приходят callback. Баланс пополняется по **каждому успешному списанию**.

Плательщик на форме вводит email, подтверждает привязку счёта в банке (СБП/НСПК) — подписка становится `Active`. Дальше автоматически списывается `amount` каждый период. Мерчанту ничего вызывать не нужно.

**Денежная транзакция на create не создаётся.** Транзакции появляются позже, по каждому списанию.

`paymentMethod` **всегда `6` (число, не строка)**. Значения `6` **нет** в схеме `PaymentMethodInt` (2, 3, 11–14).

---

## POST `/transaction/process` — создать подписку

Тот же путь, что у платежа с методом. Отличие — тело.

`operationId`: `createSubscription`

### Заголовки

`X-MerchantId`, `X-Secret` — required.

### Тело

Required: `paymentMethod`, `paymentDetails`, `description`.  
Поля `return` / `failedUrl` / `payload` / `metadata` в OpenAPI этой ручки **не** описаны.

| Поле | Тип | Required | Описание |
| --- | --- | --- | --- |
| `paymentMethod` | integer | да | Всегда `6` |
| `paymentDetails.amount` | integer | да | Сумма одного регулярного списания |
| `paymentDetails.currency` | string | да | Описание: `"RUB"` |
| `paymentDetails.interval` | см. ниже | да | 1 — день, 2 — неделя, 3 — месяц, 4 — год |
| `paymentDetails.intervalCount` | integer | да | Лимит зависит от interval: день до 31, неделя до 4, месяц до 12, год до 3 |
| `description` | string | да | На форме и в email-уведомлениях |

#### Конфликт типа `interval`

- Проза create: «1 — день, 2 — неделя, 3 — месяц, 4 — год»; example тела: `"interval": 3` (**integer**).
- Схема `SubscriptionInterval`: `type: string`, enum `'1'`, `'2'`, `'3'`, `'4'`; у `'3'` description «30 дней».

Документируй оба. В рабочих примерах официальной страницы — число `3`.

### Ответ 200

Required: `paymentMethod`, `transactionId`, `redirect`, `status`, `merchantId`.

| Поле | Описание |
| --- | --- |
| `paymentMethod` | Example: `Subscription` |
| `transactionId` | **Это ID подписки (`subscriptionId`)**. Сохранить: по нему callback и остальные ручки |
| `redirect` | Плательщика отправить **сразу**: на подтверждение привязки **30 минут**, затем подписка → `Failed` |
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

### Ошибки

`400` валидация, `401` аутентификация.

---

## GET `/subscription/{subscriptionId}` — одна подписка

`operationId`: `getSubscription`

### Параметры

| Имя | In | Required |
| --- | --- | --- |
| `subscriptionId` | path | да |
| `X-MerchantId` | header | да |
| `X-Secret` | header | да |

### Ответ 200

Все перечисленные поля — required в схеме.

| Поле | Тип | Example |
| --- | --- | --- |
| `id` | string | UUID |
| `status` | string | `Active` (см. `SubscriptionStatus`) |
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
| `chargeMetrics` | object | required целиком |

`chargeMetrics`:

| Поле | Тип |
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

### Ошибки

`404` — «Транзакция не найдена» (текст OpenAPI; речь о подписке).

---

## GET `/subscription` — список

`operationId`: `getSubscriptions`

### Query

Все optional, примеры из OpenAPI:

| Имя | Example |
| --- | --- |
| `status` | `"1"` (строка; числовой смысл в схеме не расшифрован) |
| `from` | `2026-07-01T00:00:00.000Z` |
| `to` | `2026-07-31T23:59:59.999Z` |
| `page` | `"1"` |
| `size` | `"20"` |

Плюс заголовки `X-MerchantId`, `X-Secret`.

### Ответ 200

| Поле | Тип |
| --- | --- |
| `items` | array |
| `total` | integer |
| `page` | integer |
| `size` | integer |

Элемент `items` (все поля required в схеме):

| Поле | Тип в схеме | Example |
| --- | --- | --- |
| `id` | string | |
| `status` | **integer** | `4` |
| `amount` | integer | `100` |
| `currencyCode` | string | `RUB` |
| `intervalUnit` | **integer** | `3` или `2` |
| `intervalCount` | integer | `1` |
| `nextChargeAt` | null в схеме | `null` |
| `lastChargeAt` | null в схеме | `null` |
| `customerEmail` | string, nullable | `null` / email |
| `description` | string | |
| `chargesCount` | integer | `0` |
| `createdAt` | string | |

**Не угадывать** соответствие `status: 4` ↔ `SubscriptionStatus`. GET одной подписки возвращает строки (`Active`), список — integers. Официального маппинга в llms.txt нет.

`intervalUnit: 3` согласуется с create `interval: 3` (месяц) и GET-one `intervalUnit: "Month"`, но это наблюдение по примерам, не отдельная схема.

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

### Ошибки

`404` — «Транзакция не найдена».

---

## POST `/subscription/{subscriptionId}/cancel`

Отмена останавливает будущие списания. Ручка **идемпотентна**.

Плательщик может отменить сам по ссылке из email после каждого списания; мерчант узнаёт из callback `SUBSCRIPTION_CANCELLED`.

### Параметры

`subscriptionId` path + `X-MerchantId` + `X-Secret`. Тела нет.

### Ответ 200

| Поле | Example |
| --- | --- |
| `subscriptionId` | UUID |
| `status` | `cancelled` (в example **lowercase**; схема `SubscriptionStatus` — `Cancelled`) |

```json
{
  "subscriptionId": "11111111-1111-1111-1111-111111111111",
  "status": "cancelled"
}
```

### Ошибки

`400` валидация, `401` аутентификация.

---

## Статусы подписки (`SubscriptionStatus`)

| Значение | Где встречается |
| --- | --- |
| `PendingAgreement` | схема |
| `Active` | схема + GET-one example |
| `PastDue` | схема; после неуспешного списания (проза callback списания) |
| `Cancelled` | схема |
| `Failed` | схема; проза create: таймаут 30 мин привязки |

Callback-статусы — **другой** enum (`SUBSCRIPTION_ACTIVATED` и т.д.), см. [callbacks.md](callbacks.md) и [schemas.md](schemas.md).

## Списания

- Успех callback: `Status: CONFIRMED` — деньги списаны, баланс пополнен (сумма за вычетом комиссии).
- Неуспех: `Status: CANCELED` — баланс не меняется, `NextChargeAt = null`, подписка → `PastDue`. **Провайдер не будет повторять попытки.**
- `PaymentMethod` в callback списания: `6`.
- Поля callback списания — **PascalCase** (`Id`, `Amount`, …) + `SubscriptionId` + `NextChargeAt`.
- `Id` в callback списания — ID **транзакции-списания** (новый на каждое списание), не subscriptionId.
- В callback статуса подписки `Id` = `SubscriptionId`.
