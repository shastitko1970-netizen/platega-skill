---
name: platega
description: "Use when integrating or debugging the Platega payment API (platega.io): creating payments, SBP/СБП QR, card acquiring, crypto, Sberpay, hosted checkout, H2H, refunds, recurrent subscriptions, callbacks, HMAC-signed payouts, saved cards, balances, or transaction export. Triggers: Platega, platega.io, SBP, СБП, payout, HMAC, subscription, callback, H2H, refund, MerchantId, X-MerchantId, X-Secret, PG-HMAC-SHA256."
license: MIT
metadata:
  author: community
  version: "1.0.0"
  source: "https://docs.platega.io/"
  last_read: "2026-08-26"
---

# Platega.io API

Справочный skill по merchant API Platega. Не выдумывай эндпоинты, поля и статусы. Если docs.platega.io и GitBook расходятся — документируй оба и помечай источник. Полные схемы — в `references/`.

**Базовый URL (официально):** `https://app.platega.io/`

`api.platega.io` встречался в неофициальных индексах (Context7) — не использовать по умолчанию.

**Кабинет:** Настройки → `MerchantId`, `X-Secret`, Callback URLs. Payout API (отдельный SECRET) — opt-in через менеджера.

## Роутинг

| Задача | Файл |
| --- | --- |
| `X-MerchantId` / `X-Secret`, HMAC payout, окна ts, секреты ЛК | [references/auth.md](references/auth.md) |
| Создать платёж, статус, H2H QR, методы 2/3/11/12/13/14 | [references/payments.md](references/payments.md) |
| Рекуррентные СБП-подписки (`paymentMethod: 6`) | [references/subscriptions.md](references/subscriptions.md) |
| Callback платежа и подписки, фейковый callback | [references/callbacks.md](references/callbacks.md) |
| `cancel-supported` / `cancel` | [references/refunds.md](references/refunds.md) |
| Вывод на карту, сохранённые карты, HMAC string_to_sign | [references/payouts.md](references/payouts.md) |
| Баланс, CSV/Excel/JSON export; курсы и конвертации (legacy) | [references/reporting.md](references/reporting.md) |
| CMS-модули и SDK | [references/cms-sdks.md](references/cms-sdks.md) |
| GitBook: `id` клиента, методы 1–10, EXPIRED/FAILED, H2H-реквизиты | [references/legacy-gitbook.md](references/legacy-gitbook.md) |
| OpenAPI-схемы полей | [references/schemas.md](references/schemas.md) |
| CLI подписи payout | [scripts/payout_sign.py](scripts/payout_sign.py) |

## Авторизация (кратко)

Две разные модели. Не смешивать заголовки.

| Область | Как |
| --- | --- |
| Платежи, статус, H2H, подписки, возвраты, баланс, export | Заголовки `X-MerchantId` + `X-Secret` из ЛК → Настройки |
| Выводы + сохранённые карты | `Authorization: PG-HMAC kid={MERCHANT_ID}, ts={unix}, sig={b64}`. SECRET **отдельный**, одноразовый показ. Окно `ts` ±300 с. На POST вывода обязателен `Idempotency-Key` |

Подпись HMAC и точные строки — [references/auth.md](references/auth.md) и [references/payouts.md](references/payouts.md).

## Методы оплаты (текущий PaymentMethodInt)

Официальная схема `PaymentMethodInt` (docs.platega.io):

| Значение | Имя |
| --- | --- |
| `2` | СБП (QR-код) / `SBPQR` |
| `3` | ЕРИП |
| `11` | Карточный эквайринг |
| `12` | Международная оплата |
| `13` | Криптовалюта (по умолчанию веб-пейформа; Telegram-бот — opt-in менеджера) |
| `14` | Sberpay |

`paymentMethod: 6` — **только подписки**. Его **нет** в enum `PaymentMethodInt`. GitBook-методы `10` CardRu / `1`–`9` P2P — [references/legacy-gitbook.md](references/legacy-gitbook.md).

## Статусы платежа (текущий PaymentStatus)

Официально: `PENDING`, `CANCELED`, `CONFIRMED`, `CHARGEBACKED`.

GitBook дополнительно: `EXPIRED`, `FAILED` — не считать текущей схемой.

В ответе статуса поля приходят как есть, включая опечатки `mechantId` и `comission` / `comissionUsdt` / `comissionType`.

## Индекс эндпоинтов (официальный llms.txt)

Все пути относительно `https://app.platega.io`.

| Метод | Путь | Auth | Назначение |
| --- | --- | --- | --- |
| `POST` | `/transaction/process` | X-* | Платёж с `paymentMethod` **или** подписка (`6`) |
| `POST` | `/v2/transaction/process` | X-* | Без метода; плательщик выбирает на hosted page; в ответе `url`, не `redirect` |
| `GET` | `/transaction/{id}` | X-* | Статус платежа |
| `GET` | `/h2h/{id}` | X-* | QR/ссылка H2H (включает менеджер) |
| `POST` | `/transaction/export/csv` | X-* | Выгрузка → `{url}` |
| `POST` | `/transaction/export/excel` | X-* | Выгрузка → `{url}` |
| `POST` | `/transaction/export/json` | X-* | Массив записей (не `{url}`) |
| `GET` | `/balance/all` | X-* | Балансы |
| `GET` | `/transaction/{id}/cancel-supported` | X-* | Можно ли отменить |
| `POST` | `/transaction/{id}/cancel` | X-* | Возврат |
| `GET` | `/subscription/{subscriptionId}` | X-* | Одна подписка |
| `GET` | `/subscription` | X-* | Список |
| `POST` | `/subscription/{subscriptionId}/cancel` | X-* | Отмена подписки (идемпотентна) |
| `POST` | `/api/v1/payouts/card-rub` | PG-HMAC | Вывод на карту RUB |
| `GET` | `/api/v1/cards` | PG-HMAC | Сохранённые карты |
| inbound POST | URL из ЛК Callback URLs | X-* на callback | Статус платежа / списание / статус подписки |

Не в текущем llms.txt (помечать extra/legacy): `GET /rates/payment_method_rate`, `GET /transaction/balance-unlock-operations`. Страница конвертаций на docs 404.

## Сценарии

1. **Обычный платёж с методом.** `POST /transaction/process` с `paymentMethod` ∈ {2,3,11,12,13,14}. **Не передавай `id`.** Редирект плательщика на `redirect`. Жди callback или опрашивай `GET /transaction/{id}`.
2. **Hosted page без метода.** `POST /v2/transaction/process` без `paymentMethod`. Редирект на `url`.
3. **H2H.** Создать транзакцию → `GET /h2h/{id}` → `{amount, qr}` (текущие docs). H2H включает менеджер.
4. **Подписка.** Тот же `POST /transaction/process`, но `paymentMethod: 6` + `interval` + `intervalCount`. `transactionId` = `subscriptionId`. Денег на create нет. 30 минут на привязку, иначе `Failed`. Callback списания: PascalCase + `SubscriptionId` + `NextChargeAt`.
5. **Возврат.** `GET .../cancel-supported` (нужен баланс USDT или RUB) → `POST .../cancel`. Возможен `accepted: false` + `manualControlRequired: true`.
6. **Вывод.** Opt-in. Подписать тело байт-в-байт (`separators=(",", ":")`), `data=` не `json=`. Новый `Idempotency-Key` на каждый новый вывод. `amountRub` 1000…87500. `cardId` XOR `cardNumber`.

## Никогда так не делать

1. Не передавай `id` при создании транзакции на текущем API — ID выдаёт система. GitBook-примеры с клиентским UUID устарели.
2. Не доверяй callback без constant-time сравнения `X-MerchantId` и `X-Secret` (`hmac.compare_digest`). Подписи тела нет.
3. Не переиспользуй `Idempotency-Key` для «повтора с другими данными» и не генерируй новый ключ, если хочешь идемпотентный retry того же вывода. Новый ключ = второй вывод.
4. Не отправляй payout через `json=` / повторную сериализацию — байты разъедутся с подписью. Используй те же байты, что хешировал.
5. Не путай `paymentMethod: 6` с таблицей `PaymentMethodInt` (2, 3, 11–14).
6. Не «исправляй» поля ответа `mechantId` / `comission` — так их возвращает API.
7. Не маппь export-фильтр `statuses: ['6','7']` на enum `PENDING`/`CONFIRMED`/… — официальный маппинг не опубликован.
8. Не логируй и не коммить `X-Secret` и payout `SECRET`. Payout-ключ показывается один раз.
9. Не ставь callback на HTTP, localhost, частные IP или self-signed сертификат.
10. Не считай create подписки списанием: денег нет, окно привязки 30 минут; `CANCELED` по списанию → `PastDue`, провайдер **не** ретраит.

## Кабинет (из docs)

- Настройки: MerchantId, Secret, Callback URLs.
- Фейковый callback: создать тестовую транзакцию в ЛК → кнопка списка фейковых callback.
- Payout API: генерация/сброс ключа (код на email, показ один раз; сброс инвалидирует старый ключ).
- Крипто `13`: веб-пейформа по умолчанию; Telegram-бот — менеджер.
- Для части категорий магазинов обязателен `metadata.userId` (антифрод). Отсутствие при требовании отключает антифрод и может отключить магазин. В примерах также `metadata.clientIp`.
- H2H и Payout API подключает менеджер.

## Источники

- Официально: https://docs.platega.io/ и https://docs.platega.io/llms.txt (2026-08-26)
- GitBook (старше): https://platega-io.gitbook.io/platega.io-api-dokumentaciya/
- Спека skill: https://agentskills.io/specification
