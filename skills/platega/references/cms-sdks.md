# CMS modules and SDKs

Official (docs.platega.io, re-read 2026-09-02, unchanged):

- [CMS modules](https://docs.platega.io/модули-cms-1991884m0.md)
- [SDK](https://docs.platega.io/sdk-1991993m0.md)

Page copy: "For a faster integration with our service, you can use ready-made modules." / "For a faster integration use SDKs for popular programming languages."

## CMS modules

Download host: `https://platega-modules.plategadrive.com/`

All cards are labeled "Embeddable module".

| CMS | File URL | Filename on the site |
| --- | --- | --- |
| Simpla | https://platega-modules.plategadrive.com/Simpla.zip | `Simpla.zip` |
| HopeBilling | https://platega-modules.plategadrive.com/HopeBilling.zip | `HopeBilling.zip` |
| WHMCS | https://platega-modules.plategadrive.com/WHCMS.zip | **`WHCMS.zip`** (typo WHMCS→WHCMS in the filename) |
| DLE | https://platega-modules.plategadrive.com/DLE.zip | `DLE.zip` |
| XenForo | https://platega-modules.plategadrive.com/XenForo.zip | `XenForo.zip` |
| Opencart | https://platega-modules.plategadrive.com/Opencart.zip | `Opencart.zip` |
| BILLmanager — ISP | https://platega-modules.plategadrive.com/BillManager.zip | `BillManager.zip` |
| Joomla! (JoomShopping5) | https://platega-modules.plategadrive.com/Joomla-JoomShopping5.zip | `Joomla-JoomShopping5.zip` |
| WooCommerce | https://platega-modules.plategadrive.com/WooCommerce.zip | `WooCommerce.zip` |

The official page has no install instructions — download links only.

## Official SDKs

Host: `https://sdk-s.plategadrive.com/`

| Language | URL |
| --- | --- |
| PHP SDK | https://sdk-s.plategadrive.com/platega-sdk-php.zip |
| Python SDK | https://sdk-s.plategadrive.com/platega-sdk-python.zip |
| Node.js SDK | https://sdk-s.plategadrive.com/platega-sdk-nodejs.zip |

Cards are also labeled "Embeddable module". Zip contents and API coverage are not described on the page.

## Community (not in llms.txt)

Unofficial packages; they cover more endpoints than the zip cards show. These are **not** official SDKs.

| Package | Where | Notes |
| --- | --- | --- |
| `aioplatega` | [PyPI](https://pypi.org/project/aioplatega/), [GitHub](https://github.com/DOFER998/aioplatega) | Async Python (aiohttp, Pydantic v2). Docs: https://DOFER998.github.io/aioplatega/ |
| `platega` | PyPI / GitHub komarukomaru | Sync+async, webhooks |
| `plategaio` | PyPI / GitHub ploki1337 | Async httpx |

On SDK vs docs.platega.io behavior conflict — trust docs.

## What to pick

- CMS store from the table — official zip first.
- Own PHP/Python/Node backend — official zip SDK, check against current docs (subscriptions, HMAC payouts, v2 process may post-date the zip).
- Need subscriptions / payout HMAC / export — read this skill's references and/or a community SDK; do not assume the official zip covers everything.
