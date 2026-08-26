# Возвраты (отмена транзакции)

Официально (docs.platega.io, 2026-08-26):

- [Проверка возможности отмены транзакции](https://docs.platega.io/проверка-возможности-отмены-транзакции-38219023e0.md)
- [Отмена транзакции](https://docs.platega.io/отмена-транзакции-38225949e0.md)

Base: `https://app.platega.io/`  
Auth: `X-MerchantId` + `X-Secret` (модель 1, не payout HMAC).

Порядок: сначала `GET /transaction/{id}/cancel-supported`, затем `POST /transaction/{id}/cancel`.

Для `supported: true` на одном из балансов мерчанта (**USDT или RUB**) должно быть достаточно средств на сумму возврата.

После успешного возврата платежный callback (проза) несёт статус **CHARGEBACKED**.

---

## GET `/transaction/{id}/cancel-supported`

Возвращает, доступна ли отмена, и какую сумму в USDT спишут с баланса.

### Параметры

| Имя | In | Required | Заметки |
| --- | --- | --- | --- |
| `id` | path | да | ID транзакции |
| `accept` | header | да в OpenAPI | example: `text/plain` |
| `X-MerchantId` | header | да | |
| `X-Secret` | header | да | |

В официальном example OpenAPI присутствуют конкретные значения MerchantId/Secret — **не копировать в код и репозиторий**, это образцы спецификации.

### Ответ 200

| Поле | Тип | Required | Описание |
| --- | --- | --- | --- |
| `supported` | boolean | да | `true` — отмена доступна и баланс достаточен; `false` — невозможна |
| `totalDeductUsdt` | number | да | Итоговая сумма в USDT, которая будет списана с баланса |
| `penaltyNativeAmount` | number | нет | |
| `penaltyNativeCurrency` | string | нет | Валюта штрафа (RUB, EUR и т.д.) |
| `penaltyUsdt` | number | да | |
| `penaltyConversionRate` | number | нет | Курс конвертации при расчёте штрафа |
| `blockReason` | string | нет | Причина блокировки, если `supported: false` по балансу. Например: `"Insufficient funds"` |

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

Других HTTP-кодов страница не описывает.

---

## POST `/transaction/{id}/cancel`

Инициирует отмену и возврат средств плательщику.

### Параметры

| Имя | In | Required |
| --- | --- | --- |
| `id` | path | да |
| `accept` | header | да в OpenAPI (example `text/plain`) |
| `X-MerchantId` | header | да |
| `X-Secret` | header | да |

Тела запроса в спецификации нет.

### Ответ 200

Все четыре поля required:

| Поле | Тип | Описание |
| --- | --- | --- |
| `transactionId` | string | Идентификатор транзакции |
| `accepted` | boolean | Принята ли отмена. `false` означает, что требуется ручная обработка |
| `manualControlRequired` | boolean | Если `true` — автоматическая отмена невозможна, обратиться в поддержку |
| `message` | string | Сообщение о статусе отмены |

Официальный example — как раз «не автоматом»:

```json
{
  "transactionId": "71f1375c-ba7a-4e9d-84a5-452f3f9cf4c3",
  "accepted": false,
  "manualControlRequired": true,
  "message": "Возврат в процессе"
}
```

`accepted: false` + `manualControlRequired: true` — штатный документированный исход, не обязательно баг клиента.

Других HTTP-кодов страница не описывает.

---

## Пример вызова

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

Проверяй баланс через `GET /balance/all` ([reporting.md](reporting.md)), если `supported: false` и `blockReason` про insufficient funds.

Не путать с `POST /subscription/{id}/cancel` — это остановка будущих списаний подписки, не возврат платежа.
