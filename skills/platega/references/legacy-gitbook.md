# GitBook и прочие конфликты (legacy)

Старшая документация: [https://platega-io.gitbook.io/platega.io-api-dokumentaciya/](https://platega-io.gitbook.io/platega.io-api-dokumentaciya/)

Каталог GitBook `llms.txt` (2026-08-26):

- [Аутентификация запроса](https://platega-io.gitbook.io/platega.io-api-dokumentaciya/api-docs/autentifikaciya-zaprosa.md)
- [Callback](https://platega-io.gitbook.io/platega.io-api-dokumentaciya/api-docs/callback.md)
- [Создание ссылки на оплату](https://platega-io.gitbook.io/platega.io-api-dokumentaciya/api-docs/editor.md)
- [Создание платежа H2H — вывод реквизитов](https://platega-io.gitbook.io/platega.io-api-dokumentaciya/api-docs/markdown.md)
- [Проверка статуса оплаты платежа](https://platega-io.gitbook.io/platega.io-api-dokumentaciya/api-docs/images-and-media.md)
- [Фейковый CallBack](https://platega-io.gitbook.io/platega.io-api-dokumentaciya/feikovyi-callback-dlya-testirovaniya-platezhei.md)
- [Получение курсов](https://platega-io.gitbook.io/platega.io-api-dokumentaciya/poluchenie-kursov.md)

По умолчанию для новой интеграции — **docs.platega.io**. Ниже — только то, чего нет в текущих docs или что им противоречит. Всегда помечай источник.

GitBook base URL совпадает: `app.platega.io`. Auth платежей тот же: `X-MerchantId` + `X-Secret`.

---

## 1. Поле `id` при создании транзакции

**GitBook** (`editor.md`) в примере тела **передаёт клиентский UUID**:

```json
{
  "paymentMethod": 2,
  "id": "3fa85f64-5717-4562-b3fc-2c963f66aza6",
  "paymentDetails": { "amount": 970, "currency": "RUB" },
  "description": "test",
  "return": "https://google.com",
  "failedUrl": "https://yourdomain/fail",
  "payload": "1111"
}
```

(в исходнике GitBook после `return` и `failedUrl` пропущены запятые JSON.)

**docs.platega.io:** «ID транзакции генерируется системой автоматически — не передавайте поле `id` в запросе.» Схема `CreateTransactionRequest` поля `id` не содержит.

Считать GitBook-пример **устаревшим**. Не слать `id` на текущем API.

### Ошибка «Transaction already exists»

GitBook 400:

```json
{
  "statusCode": 400,
  "message": "Transaction 3fa85f64-5717-4562-b3fc-2c963f66afa6 already exists."
}
```

«Транзакция с таким айди уже существует в системе. Для исправления ситуации измените айди транзакции и сформируйте запрос по новой.»

Имеет смысл только в модели, где клиент задаёт `id`. На текущем API, если вдруг придёт — признак, что клиент всё ещё шлёт свой UUID.

---

## 2. Методы оплаты GitBook

Таблица GitBook «Список доступных методов оплат»:

| Название | Значение |
| --- | --- |
| СБП / QR | `2` — НСПК / QR |
| CardRu | `10` — Карточный 2дс, оплата картами МИР |
| International | `12` — Международный эквайринг |

Проза той же страницы: принцип тела для QR/СБП и P2P одинаков, отличается только `paymentMethod`. «В случае с QR / СБП мы всегда передаем цифру 2. Все остальные методы, включая метод 1, 2–9, связанны с P2P методами.»

Итого GitBook:

| int | GitBook |
| --- | --- |
| `1`–`9` | P2P (при этом `2` одновременно назван СБП/QR) |
| `10` | CardRu / 2dcs MIR |
| `12` | International |

Текущий `PaymentMethodInt`: `2, 3, 11, 12, 13, 14`. Нет `1`, `4`–`10`. `3` ЕРИП, `11` карточный эквайринг, `13` крипто, `14` Sberpay в GitBook-таблице отсутствуют. `6` подписок в GitBook нет.

Не подставлять `10` / P2P `1`–`9` в новый код, пока менеджер/текущие docs это не подтверждают.

---

## 3. Статусы GitBook

GitBook «Проверка статуса» (`images-and-media.md`):

| Status | Описание GitBook |
| --- | --- |
| `PENDING` | ожидание оплаты |
| `CONFIRMED` | подтверждение оплаты |
| `EXPIRED` | истек срок оплаты платежа |
| `CANCELED` | отмененный платеж |
| `FAILED` | ошибка создания платежа |

Текущий `PaymentStatus`: `PENDING`, `CANCELED`, `CONFIRMED`, `CHARGEBACKED`.  
`EXPIRED` и `FAILED` в официальной схеме **нет**. `CHARGEBACKED` в GitBook-списке **нет**.

Поля ответа статуса в GitBook совпадают с текущими, включая опечатки `mechantId`, `comission`, `comissionUsdt`, `comissionType`.

---

## 4. H2H — другой JSON

**docs.platega.io:** `{ "amount": 136.12, "qr": "https://qr.nspk.ru/..." }`

**GitBook** (`markdown.md`): сначала создать транзакцию, затем `GET app.platega.io/h2h/{id}` с id транзакции.

```json
{
  "accountNumber": "2200 7004 0146 3121",
  "maskedAccountNumber": "2200 7004 0146 3121",
  "accountName": "Jhon M",
  "method": "tinkoff",
  "amount": 2000
}
```

(в исходнике GitBook пропущена запятая после `"tinkoff"`.)

Полей `accountNumber` / `maskedAccountNumber` / `accountName` / `method` в текущем OpenAPI H2H нет. Для новой интеграции — `{amount, qr}`. Если живой ответ похож на GitBook — задокументировать факт, не ломать парсер на одном варианте.

H2H в обоих источниках требует включения менеджером (текущие docs).

---

## 5. P2P 400: No available requisites

GitBook:

```json
{
  "statusCode": 400,
  "message": "No available requisites"
}
```

«Система не смогла найти реквизитов на подходящую сумму. … попробуйте еще раз запросить реквизиты на другую сумму. Советуем запрашивать реквизиты на суммы **1001, 2002, 3001**.»

В текущем OpenAPI create этой ошибки нет (только общее `400` «Ошибка валидации»). Имеет смысл для legacy P2P.

---

## 6. Ответы create GitBook

200 СБП/QR — почти как текущий `CreateTransactionResponse` (`SBPQR`, `redirect`, `usdtRate`).

200 P2P:

```json
{
  "paymentMethod": null,
  "transactionId": "3fa85f64-5717-4562-b4fc-2c163f66afa6",
  "redirect": "https://pay.platega.io?id=...&mh=...",
  "return": "https://google.com",
  "paymentDetails": "2000 RUB",
  "status": "PENDING",
  "expiresIn": "00:15:00",
  "merchantId": "...",
  "usdtRate": 93.45
}
```

`paymentMethod: null` в текущей схеме не описан.

---

## 7. Callback GitBook

- URL в ЛК Настройки → Callback URLs — совпадает.
- Заголовки `X-MerchantId` + `X-Secret` — совпадает.
- Тело camelCase: `id`, `amount`, `currency`, `status`, `paymentMethod` — совпадает с текущим платежным callback.
- Успех `CONFIRMED`, неуспех `CANCELED`. **Нет** `CHARGEBACKED` в GitBook-прозе.
- Таймаут 60 с, 3 ретрая × 5 минут — совпадает.
- Нет требований HTTPS/CA/запрета private IP (они только в текущих docs).
- Нет подписочных PascalCase callback.

Фейковый callback: создать tx **в ЛК**, нажать кнопку, выбрать фейковый статус. GitBook: CONFIRMED / CANCELED.

---

## 8. Курсы и конвертации

`GET /rates/payment_method_rate` — только GitBook, см. [reporting.md](reporting.md).

`GET /transaction/balance-unlock-operations` — старая страница docs / Context7, **нет** в текущем llms.txt, `.md` 404. Пустая схема ответа.

---

## 9. Хост `api.platega.io`

Встречался в неофициальных индексах (Context7). Официальный и GitBook base — `https://app.platega.io/`. Payout-пример официальных docs — тоже `app.platega.io`. Не использовать `api.platega.io` по умолчанию.

---

## 10. Чего в GitBook нет (только текущие docs)

Подписки (`paymentMethod: 6`), v2 process (`url`), export csv/excel/json, баланс, cancel-supported/cancel, Payout HMAC, сохранённые карты, крипто `13`, Sberpay `14`, ЕРИП `3`, карточный эквайринг `11`, metadata/userId антифрод, Telegram-бот для крипто.

Не собирать интеграцию 2026 года только по GitBook.
