# Схемы (официальный OpenAPI)

Страницы docs.platega.io (2026-08-26):

- [PaymentStatus](https://docs.platega.io/paymentstatus-13226215d0.md)
- [PaymentMethodInt](https://docs.platega.io/paymentmethodint-13226216d0.md)
- [CreateTransactionRequest](https://docs.platega.io/createtransactionrequest-13226217d0.md)
- [CreateTransactionResponse](https://docs.platega.io/createtransactionresponse-13226218d0.md)
- [TransactionStatusResponse](https://docs.platega.io/transactionstatusresponse-13226219d0.md)
- [SubscriptionStatus](https://docs.platega.io/subscriptionstatus-16438392d0.md)
- [CallbackSubscriptionStatus](https://docs.platega.io/callbacksubscriptionstatus-16438868d0.md)
- [SubscriptionInterval](https://docs.platega.io/subscriptioninterval-16441018d0.md)
- [CallbackPayload](https://docs.platega.io/callbackpayload-13226220d0.md)

Ниже — поля **как в схемах**. Поведение ручек и конфликты required — в тематических reference.

---

## PaymentStatus

`type: string`. «Статус транзакции».

| Значение |
| --- |
| `PENDING` |
| `CANCELED` |
| `CONFIRMED` |
| `CHARGEBACKED` |

GitBook добавляет `EXPIRED`, `FAILED` — не эта схема.

---

## PaymentMethodInt

`type: integer`. «Способы оплаты».

| value | name |
| --- | --- |
| `2` | СБП (QR-код) |
| `3` | ЕРИП |
| `11` | Карточный эквайринг |
| `12` | Международная оплата |
| `13` | Криптовалюта |
| `14` | Sberpay |

`6` (подписка) в enum **нет**. GitBook `10` / P2P `1`–`9` — не эта схема.

---

## CreateTransactionRequest

`additionalProperties: false`. Description: «Тело запроса для создания транзакции. **Не указывайте поле `id` — оно генерируется системой автоматически.**»

Required схемы: `paymentMethod`, `paymentDetails`.

| Поле | Тип | Required | Описание схемы |
| --- | --- | --- | --- |
| `paymentMethod` | `PaymentMethodInt` | да | «Номер способа оплаты (к примеру, 2 для QR СБП)» |
| `paymentDetails` | object, additionalProperties false | да | |
| `paymentDetails.amount` | number (float) | да | Сумма платежа |
| `paymentDetails.currency` | string | да | Валюта (например, RUB) |
| `description` | string | нет | «Назначение (описание) платежа, указывайте по возможности всегда» |
| `return` | string (uri) | нет | Редирект при успешном платеже |
| `failedUrl` | string (uri) | нет | Редирект при неуспешном платеже |
| `payload` | string | нет | «Дополнительная информация для инициализации в вашей системе.» |

Поле `metadata` в **этой** схеме отсутствует (есть в OpenAPI ручек create).  
Required ручки `POST /transaction/process` (платёж) шире: + `description`, `return`, `failedUrl`.  
Схема не покрывает подписку (`interval`, `paymentMethod: 6`).

---

## CreateTransactionResponse

Required: `transactionId`, `status`.

| Поле | Тип | Описание схемы |
| --- | --- | --- |
| `paymentMethod` | string | «Человекочитаемое имя метода оплаты (например, 2)» |
| `transactionId` | string (uuid) | ID созданной транзакции |
| `redirect` | string (uri) | Ссылка для оплаты |
| `return` | string (uri) | Ваша ссылка после успешной оплаты |
| `paymentDetails` | string **или** `{amount: number, currency: string}` | |
| `status` | `PaymentStatus` | |
| `expiresIn` | string | Время до истечения (`HH:MM:SS`) |
| `merchantId` | string (uuid) | |
| `usdtRate` | number (float) | |

Ответ v2 process — **другая** inline-схема: `transactionId`, `status`, `url`, `expiresIn`, `rate`. Не этот объект.

Ответ create подписки — inline: `paymentMethod`, `transactionId`, `redirect`, `status`, `merchantId` (без `usdtRate` / `expiresIn` / `paymentDetails` в required).

---

## TransactionStatusResponse

Required не задан (все поля optional в схеме).

| Поле | Тип | Описание |
| --- | --- | --- |
| `id` | uuid | |
| `status` | `PaymentStatus` | |
| `paymentDetails.amount` | number | |
| `paymentDetails.currency` | string | |
| `merchantName` | string | |
| `mechantId` | uuid | опечатка сохранена |
| `comission` | number | опечатка сохранена |
| `paymentMethod` | string | «Название метода оплаты (например, SBPQR)» |
| `expiresIn` | string | |
| `return` | uri | |
| `comissionUsdt` | number | |
| `amountUsdt` | number | |
| `qr` | string | |
| `payformSuccessUrl` | uri | |
| `payload` | string | |
| `comissionType` | integer | |
| `externalId` | string | |
| `description` | string | |

---

## SubscriptionStatus

`type: string`. «Статус подписки».

| Значение | Description в x-apidog-enum |
| --- | --- |
| `PendingAgreement` | (пусто) |
| `Active` | (пусто) |
| `PastDue` | (пусто) |
| `Cancelled` | (пусто) |
| `Failed` | (пусто) |

GET одной подписки возвращает эти строки (`Active`). Список подписок возвращает `status` как **integer** (example `4`) — маппинг в этой схеме не задан.

Cancel example: `"status": "cancelled"` (lowercase) — не значение enum.

---

## SubscriptionInterval

`type: string`. «Интервал оплаты подписки».

| value | description |
| --- | --- |
| `'1'` | (пусто; проза create: день) |
| `'2'` | (пусто; проза create: неделя) |
| `'3'` | `30 дней` (проза create: месяц) |
| `'4'` | (пусто; проза create: год) |

Create example передаёт integer `3`. Лимиты `intervalCount` (день ≤31, неделя ≤4, месяц ≤12, год ≤3) живут в прозе create, не в этой схеме.

---

## CallbackSubscriptionStatus

`type: string`. «Статус подписки в Callback».

| Значение | Описание |
| --- | --- |
| `SUBSCRIPTION_ACTIVATED` | Подписка активна, списания выполняются по расписанию |
| `SUBSCRIPTION_PAST_DUE` | Перманентный, из него нет переходов в другой статус, если нет вебхука об успешной оплате или отмене |
| `SUBSCRIPTION_CANCELLED` | Переход из ACTIVATED или PAST_DUE — при явной отмене мерчантом или плательщиком (через ссылку отмены или API) |
| `SUBSCRIPTION_FAILED` | Переход из ACTIVATED — при невозможности привязки в момент первой активации (провайдер вернул ошибку или не подтвердил согласие) |

Это не `SubscriptionStatus` и не `PaymentStatus`.

---

## CallbackPayload

`additionalProperties: false`. Required: `id`, `amount`, `currency`, `status`.

| Поле | Тип | Required | Описание |
| --- | --- | --- | --- |
| `id` | uuid | да | ID транзакции |
| `amount` | number (float) | да | |
| `currency` | string | да | |
| `status` | string enum `CONFIRMED` \| `CANCELED` | да | «Статус транзакции в callback» |
| `paymentMethod` | integer | нет | ID метода оплаты |

Проза страницы callback платежа дополнительно называет `CHARGEBACKED`. Поля `payload` в этой схеме нет (есть в OpenAPI webhook платежа).

Подписочные callback **не** этот объект: PascalCase + `SubscriptionId` + `NextChargeAt`.

---

## Inline-схемы, которых нет отдельной страницей

Зафиксированы на страницах ручек (не invent):

| Контекст | Поля |
| --- | --- |
| v2 create response | `transactionId`, `status`, `url`, `expiresIn`, `rate` |
| H2H current | `amount`, `qr` |
| cancel-supported | `supported`, `totalDeductUsdt`, `penaltyNativeAmount`, `penaltyNativeCurrency`, `penaltyUsdt`, `penaltyConversionRate`, `blockReason` |
| cancel | `transactionId`, `accepted`, `manualControlRequired`, `message` |
| balance item | `amount`, `currency`, `frozenBalance` |
| export csv/excel | `{url}` |
| export json item | `recordId`, `createdAt`, `amount`, `currencyCode`, `status`, `paymentMethod`, `description`, `payload` |
| payout create response | `withdrawalRecordId`, `status`, `cardMasked`, `amountUsdtDebited` |
| card item | `cardId`, `masked`, `last4`, `brand`, `label`, `status` |
| subscription GET-one | см. [subscriptions.md](subscriptions.md) |
| subscription list wrapper | `items`, `total`, `page`, `size` |
| subscription chargeMetrics | `chargesTotal`, `chargesSuccess`, `chargesFailed`, `totalAmount`, `lastChargeAt`, `nextChargeAt` |
| subscription cancel | `subscriptionId`, `status` |
| subscription charge callback | `Id`, `Amount`, `Currency`, `Status`, `PaymentMethod`, `Payload`, `SubscriptionId`, `NextChargeAt` |

Metadata create (ручки, не CreateTransactionRequest): `userId`, `userName`; в example ещё `clientIp`.
