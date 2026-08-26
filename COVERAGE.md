# Coverage: docs.platega.io/llms.txt

Источник каталога: `/workspace/platega-raw/llms.txt` и live https://docs.platega.io/llms.txt  
Дата чтения: **2026-08-26**.

Каждая строка официального каталога должна иметь «да» в колонке Covered и файл skill, где разобрана.

## Docs

| llms.txt entry | Official URL | Covered | Skill file |
| --- | --- | --- | --- |
| Авторизация | https://docs.platega.io/авторизация-1991638m0.md | да | `skills/platega/references/auth.md`, `SKILL.md` |
| Модули CMS | https://docs.platega.io/модули-cms-1991884m0.md | да | `skills/platega/references/cms-sdks.md` |
| SDK | https://docs.platega.io/sdk-1991993m0.md | да | `skills/platega/references/cms-sdks.md` |
| Выводы: Создаёт вывод на рублёвую карту через Payout API | https://docs.platega.io/создаёт-вывод-на-рублёвую-карту-через-payout-api-2232954m0.md | да | `skills/platega/references/payouts.md`, `auth.md`, `scripts/payout_sign.py` |

## API Docs — подписки

| llms.txt entry | Official URL | Covered | Skill file |
| --- | --- | --- | --- |
| Создать подписку | https://docs.platega.io/создать-подписку-40029698e0.md | да | `skills/platega/references/subscriptions.md` |
| Получить подписку | https://docs.platega.io/получить-подписку-40029717e0.md | да | `subscriptions.md` |
| Список подписок | https://docs.platega.io/список-подписок-40029720e0.md | да | `subscriptions.md` |
| Отменить подписку | https://docs.platega.io/отменить-подписку-40029730e0.md | да | `subscriptions.md` |
| Callback по списанию | https://docs.platega.io/callback-по-списанию-40029713e0.md | да | `callbacks.md`, `subscriptions.md` |
| Callback по статусу подписки | https://docs.platega.io/callback-по-статусу-подписки-40030962e0.md | да | `callbacks.md` |

## API Docs — платежи / баланс / возвраты / callback

| llms.txt entry | Official URL | Covered | Skill file |
| --- | --- | --- | --- |
| Создание платежной ссылки без заданного метода | https://docs.platega.io/создание-платежной-ссылки-без-заданного-метода-33845703e0.md | да | `payments.md` (`POST /v2/transaction/process`) |
| Создание платежной ссылки с заданным методом | https://docs.platega.io/создание-платежной-ссылки-с-заданным-методом-29203843e0.md | да | `payments.md` (`POST /transaction/process`) |
| Получение QR-кода для H2H-транзакции | https://docs.platega.io/получение-qr-кода-для-h2h-транзакции-34794775e0.md | да | `payments.md` |
| Проверка статуса оплаты платежа | https://docs.platega.io/проверка-статуса-оплаты-платежа-29203844e0.md | да | `payments.md` |
| Выгрузка транзакций в CSV | https://docs.platega.io/выгрузка-транзакций-в-csv-37963792e0.md | да | `reporting.md` |
| Выгрузка транзакций в Excel | https://docs.platega.io/выгрузка-транзакций-в-excel-37963794e0.md | да | `reporting.md` |
| Выгрузка транзакций в Json | https://docs.platega.io/выгрузка-транзакций-в-json-37991987e0.md | да | `reporting.md` |
| Получение балансов | https://docs.platega.io/получение-балансов-33582950e0.md | да | `reporting.md` |
| Проверка возможности отмены транзакции | https://docs.platega.io/проверка-возможности-отмены-транзакции-38219023e0.md | да | `refunds.md` |
| Отмена транзакции | https://docs.platega.io/отмена-транзакции-38225949e0.md | да | `refunds.md` |
| Получение сохранённых карт | https://docs.platega.io/получение-сохранённых-карт-39075563e0.md | да | `payouts.md`, `auth.md` |
| Callback об изменении статуса транзакции | https://docs.platega.io/callback-об-изменении-статуса-транзакции-29209725e0.md | да | `callbacks.md` |

## Schemas

| llms.txt entry | Official URL | Covered | Skill file |
| --- | --- | --- | --- |
| PaymentStatus | https://docs.platega.io/paymentstatus-13226215d0.md | да | `schemas.md`, `SKILL.md` |
| PaymentMethodInt | https://docs.platega.io/paymentmethodint-13226216d0.md | да | `schemas.md`, `payments.md` |
| CreateTransactionRequest | https://docs.platega.io/createtransactionrequest-13226217d0.md | да | `schemas.md`, `payments.md` |
| CreateTransactionResponse | https://docs.platega.io/createtransactionresponse-13226218d0.md | да | `schemas.md`, `payments.md` |
| TransactionStatusResponse | https://docs.platega.io/transactionstatusresponse-13226219d0.md | да | `schemas.md`, `payments.md` |
| SubscriptionStatus | https://docs.platega.io/subscriptionstatus-16438392d0.md | да | `schemas.md`, `subscriptions.md` |
| CallbackSubscriptionStatus | https://docs.platega.io/callbacksubscriptionstatus-16438868d0.md | да | `schemas.md`, `callbacks.md` |
| SubscriptionInterval | https://docs.platega.io/subscriptioninterval-16441018d0.md | да | `schemas.md`, `subscriptions.md` |
| CallbackPayload | https://docs.platega.io/callbackpayload-13226220d0.md | да | `schemas.md`, `callbacks.md` |

## Sitemap docs.platega.io

Все 31 URL из `/workspace/platega-raw/sitemap.xml` совпадают с каталогом llms.txt (те же slugs). Отдельных страниц вне llms.txt в sitemap нет.

## GitBook / extra (не в официальном llms.txt)

Помечены legacy/extra, не смешаны с текущим контрактом:

| Материал | Covered | Skill file |
| --- | --- | --- |
| GitBook auth, callback, create+id, H2H реквизиты, статусы EXPIRED/FAILED, фейковый callback, курсы | да | `legacy-gitbook.md`, `callbacks.md`, `reporting.md` |
| `GET /rates/payment_method_rate` | да (extra) | `reporting.md` |
| `GET /transaction/balance-unlock-operations` (docs `.md` 404) | да (extra, пустая схема) | `reporting.md` |
| Community `aioplatega` | да (пометка unofficial) | `cms-sdks.md` |
| `api.platega.io` (Context7) | да (не использовать) | `SKILL.md`, `auth.md`, `legacy-gitbook.md` |

## Итог

- Официальных пунктов llms.txt: **31** (4 Docs + 18 API Docs + 9 Schemas).
- Покрыто официальных: **31 / 31**.
- Выдуманных эндпоинтов в skill нет: каждый method+path либо из docs OpenAPI, либо явно помечен GitBook/Context7 extra.
