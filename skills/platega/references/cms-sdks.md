# CMS-модули и SDK

Официально (docs.platega.io, 2026-08-26):

- [Модули CMS](https://docs.platega.io/модули-cms-1991884m0.md)
- [SDK](https://docs.platega.io/sdk-1991993m0.md)

Тексты страниц: «Для быстрой интеграции с нашим сервисом, вы можете использовать готовые модули.» / «Для быстрой интеграции используйте SDK для популярных языков программирования.»

## CMS-модули

Хост загрузок: `https://platega-modules.plategadrive.com/`

Все карточки помечены «Встраиваемый модуль».

| CMS | URL файла | Имя файла как на сайте |
| --- | --- | --- |
| Simpla | https://platega-modules.plategadrive.com/Simpla.zip | `Simpla.zip` |
| HopeBilling | https://platega-modules.plategadrive.com/HopeBilling.zip | `HopeBilling.zip` |
| WHMCS | https://platega-modules.plategadrive.com/WHCMS.zip | **`WHCMS.zip`** (опечатка WHMCS→WHCMS в имени файла) |
| DLE | https://platega-modules.plategadrive.com/DLE.zip | `DLE.zip` |
| XenForo | https://platega-modules.plategadrive.com/XenForo.zip | `XenForo.zip` |
| Opencart | https://platega-modules.plategadrive.com/Opencart.zip | `Opencart.zip` |
| BILLmanager — ISP | https://platega-modules.plategadrive.com/BillManager.zip | `BillManager.zip` |
| Joomla! (JoomShopping5) | https://platega-modules.plategadrive.com/Joomla-JoomShopping5.zip | `Joomla-JoomShopping5.zip` |
| WooCommerce | https://platega-modules.plategadrive.com/WooCommerce.zip | `WooCommerce.zip` |

Инструкций установки в официальной странице нет — только ссылки скачивания.

## Официальные SDK

Хост: `https://sdk-s.plategadrive.com/`

| Язык | URL |
| --- | --- |
| PHP SDK | https://sdk-s.plategadrive.com/platega-sdk-php.zip |
| Python SDK | https://sdk-s.plategadrive.com/platega-sdk-python.zip |
| Node.js SDK | https://sdk-s.plategadrive.com/platega-sdk-nodejs.zip |

Карточки тоже подписаны «Встраиваемый модуль». Состав zip и API-покрытие на странице не описаны.

## Community (не в llms.txt)

Неофициальные пакеты, покрывают больше ручек, чем видно из zip-карточек. Это **не** официальные SDK.

| Пакет | Где | Заметки |
| --- | --- | --- |
| `aioplatega` | [PyPI](https://pypi.org/project/aioplatega/), [GitHub](https://github.com/DOFER998/aioplatega) | Async Python (aiohttp, Pydantic v2). Docs: https://DOFER998.github.io/aioplatega/ |
| `platega` | PyPI / GitHub komarukomaru | Sync+async, webhooks |
| `plategaio` | PyPI / GitHub ploki1337 | Async httpx |

При конфликте поведения SDK vs docs.platega.io — верить docs.

## Когда что брать

- CMS-магазин из таблицы — сначала официальный zip.
- Свой бэкенд PHP/Python/Node — официальный zip SDK, сверять с текущими docs (подписки, HMAC payouts, v2 process могли появиться позже zip).
- Нужны подписки / payout HMAC / export — читай reference этого skill и/или community SDK, не предполагай, что официальный zip всё умеет.
