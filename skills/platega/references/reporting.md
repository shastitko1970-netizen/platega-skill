# Отчёты, балансы, курсы

Официально в llms.txt (docs.platega.io, 2026-08-26):

- [Получение балансов](https://docs.platega.io/получение-балансов-33582950e0.md) — `GET /balance/all`
- [Выгрузка транзакций в CSV](https://docs.platega.io/выгрузка-транзакций-в-csv-37963792e0.md)
- [Выгрузка транзакций в Excel](https://docs.platega.io/выгрузка-транзакций-в-excel-37963794e0.md)
- [Выгрузка транзакций в Json](https://docs.platega.io/выгрузка-транзакций-в-json-37991987e0.md)

Auth для всех официальных ручек ниже: `X-MerchantId` + `X-Secret`. Base: `https://app.platega.io/`.

---

## GET `/balance/all`

Описание: «Получение балансов».

### Заголовки

| Header | Required | Schema |
| --- | --- | --- |
| `X-MerchantId` | да | uuid |
| `X-Secret` | да | string |

### Ответ 200

Массив объектов:

| Поле | Тип | Required | Описание |
| --- | --- | --- | --- |
| `amount` | number | да | |
| `currency` | string | да | example: `RUB`, `USDT` |
| `frozenBalance` | integer | нет | в example есть у USDT |

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

Нужен для возвратов: `cancel-supported` требует достаточный USDT **или** RUB.

Других HTTP-кодов страница не описывает.

---

## Общий фильтр выгрузок

Три export-ручки принимают одно и то же JSON-тело. Все поля в схеме optional (required не задан).

| Поле | Тип | Example |
| --- | --- | --- |
| `statuses` | array of string | `"6"`, `"7"` |
| `paymentMethods` | array of string | `"2"`, `"11"` |
| `from` | string | `2026-05-01T00:00:00.000Z` |
| `to` | string | `2026-06-16T08:50:04.820Z` |
| `timeZoneId` | string | `UTC` |

**Не маппить** `statuses: ['6','7']` на `PaymentStatus` (`PENDING` / `CANCELED` / `CONFIRMED` / `CHARGEBACKED`). Официальный маппинг чисел → enum **не опубликован**. Передавай как в спецификации. `paymentMethods` в фильтре — строковые числа методов (`"2"`, `"11"`), в JSON-ответе выгрузки `paymentMethod` приходит уже именем (`SBPQR`).

### Общие заголовки export

| Header | Required | Example |
| --- | --- | --- |
| `X-MerchantId` | да | |
| `X-Secret` | да | |
| `accept` | нет | `text/plain` |
| `Content-Type` | нет | `application/json` |

В OpenAPI examples снова встречаются реальные-looking секреты — не копировать.

---

## POST `/transaction/export/csv`

«Возвращает ссылку на CSV-файл с транзакциями по заданным фильтрам.»

### Ответ 200

```json
{ "url": "string" }
```

| Поле | Required |
| --- | --- |
| `url` | да |

---

## POST `/transaction/export/excel`

«Возвращает ссылку на Excel-файл с транзакциями по заданным фильтрам.»

### Ответ 200

Тот же объект `{ "url": "string" }`, `url` required.

---

## POST `/transaction/export/json`

Конфликт внутри официальной страницы:

- Description: «Возвращает ссылку на Json-файл с транзакциями по заданным фильтрам.»
- Схема ответа: **массив записей**, не `{url}`.

По схеме и example — массив. Поле `url` в JSON-ответе **нет**.

Элемент массива (все поля required в схеме):

| Поле | Тип | Example |
| --- | --- | --- |
| `recordId` | string | UUID |
| `createdAt` | string | `2026-06-15 13:44:13` (не ISO в example) |
| `amount` | integer в схеме; в example бывает `1150` и `1.15` | не угадывать единый тип — схема говорит integer, example содержит дробь |
| `currencyCode` | string | `RUB` |
| `status` | string | `CANCELED` (здесь уже enum-имя, не `'6'`) |
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

### Пример запроса (общий для csv/excel/json)

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

## Extra / legacy (нет в официальном llms.txt)

Не использовать как текущий контракт без сверки с живыми docs. Страница конвертаций на docs.platega.io по `.md` даёт **404** (проверено 2026-08-26).

### GET `/rates/payment_method_rate` (GitBook)

Источник: [Получение курсов](https://platega-io.gitbook.io/platega.io-api-dokumentaciya/poluchenie-kursov.md) (`poluchenie-kursov.md` в дампе).

```
GET https://app.platega.io/rates/payment_method_rate
```

Query:

| Параметр | Тип | Описание |
| --- | --- | --- |
| `merchantId` | UUID | ID мерчанта |
| `paymentMethod` | integer | ID платёжного метода |
| `currencyFrom` | string | например `RUB` |
| `currencyTo` | string | например `USDT` |

Заголовки: `accept` (`text/plain` или `application/json`), `X-MerchantId`, `X-Secret`.

Пример ответа GitBook:

```json
{
  "paymentMethod": 2,
  "currencyFrom": "RUB",
  "currencyTo": "USDT",
  "rate": 0.0105,
  "updatedAt": "2025-08-11T10:15:00Z"
}
```

Текущий create-платёж уже возвращает `usdtRate` / `rate` в ответе — отдельный rates-эндпоинт в llms.txt отсутствует.

### GET `/transaction/balance-unlock-operations` (Context7 / старая страница docs)

Источники: Context7-снимок и страница «Метод получения конвертаций» (id `24236037e0`), которой **нет** в текущем `llms.txt` и `.md` которой 404.

Задокументировано там:

| Query | Required | Example |
| --- | --- | --- |
| `from` | да | `2025-01-01T00:00:00Z` |
| `to` | да | `2025-11-13T23:59:59Z` |
| `page` | да | `1` |
| `size` | да | `20` |

Заголовки: `accept` (example `text/plain`), `X-MerchantId`, `X-Secret`.

Ответ 200: `application/json`, схема `object` с **пустыми** `properties` — поля записей официально не описаны.

Помечать extra/legacy. Не выдумывать структуру элементов.
