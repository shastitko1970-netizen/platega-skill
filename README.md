# Platega Agent Skill

Неофициальный community skill для [Platega.io](https://platega.io) — платёжного API (СБП/QR, эквайринг, крипто, подписки, возвраты, HMAC-выводы).

Версия skill: **1.2.0** ([CHANGELOG.md](CHANGELOG.md)).

Skill написан в формате [Agent Skills](https://agentskills.io/specification): агент читает `skills/platega/SKILL.md`, затем точечно подгружает `references/*.md`. Это **справочный** skill (документация API), не дисциплинарный.

**Источник истины:** [https://docs.platega.io/](https://docs.platega.io/) и [https://docs.platega.io/llms.txt](https://docs.platega.io/llms.txt). Последнее чтение: **2026-09-02**.

**Дисклеймер.** Репозиторий неофициальный. Сверяй эндпоинты, поля и статусы с живыми docs перед продом. Секреты (`X-Secret`, payout `SECRET`) в репозиторий не входят и не должны попадать в логи/git.

Старший GitBook ([platega-io.gitbook.io](https://platega-io.gitbook.io/platega.io-api-dokumentaciya/)) конфликтует с текущими docs — см. `skills/platega/references/legacy-gitbook.md`. Context7 когда-то показывал `api.platega.io`; официальный base URL — `https://app.platega.io/`.


---

## Why this skill / Зачем skill

Platega has two doc layers (current Apidog and older GitBook) and they **disagree**: client `id` on create vs optional `orderId` (current, 2026-09-01), methods 1–10 vs 2/3/11–14, H2H as card requisites vs QR, subscriptions as the same `POST /transaction/process` with `paymentMethod: 6`. An agent without the skill almost always mixes the layers.

Worked examples (prompt → without skill / with skill): [skills/platega/references/examples.md](skills/platega/references/examples.md).

Edge cases (antifraud `metadata`, H2H, subscriptions): [skills/platega/references/scenarios.md](skills/platega/references/scenarios.md).

## Установка

### 1. skills.sh (рекомендуется, 2026)

```bash
npx skills add shastitko1970-netizen/platega-skill
```

Замени `shastitko1970-netizen` на GitHub-владельца этого репозитория. CLI ([skills.sh](https://skills.sh)) ставит skill в каталоги нужных агентов.

Полезные флаги:

```bash
npx skills add shastitko1970-netizen/platega-skill --list
npx skills add shastitko1970-netizen/platega-skill --skill platega -a cursor -a claude-code -a codex
npx skills add shastitko1970-netizen/platega-skill -g          # глобально, для всех проектов
npx skills add shastitko1970-netizen/platega-skill -y          # без интерактива
```

### 2. Cursor

Скопируй или сделай symlink папки `skills/platega` в каталог скиллов Cursor:

```bash
# проект
mkdir -p .cursor/skills
cp -R skills/platega .cursor/skills/platega
# или: ln -s "$(pwd)/skills/platega" .cursor/skills/platega

# альтернатива 2026: .agents/skills
mkdir -p .agents/skills
cp -R skills/platega .agents/skills/platega
```

Пользовательский каталог: `~/.cursor/skills/platega`.

Вызов: `/platega` или естественный запрос («создай СБП-платёж через Platega»).

**Не клади `.cursor/skills/` и `.claude/skills/` в этот publisher-репозиторий** — это пути потребителя.

### 3. Claude Code

```bash
# проект
mkdir -p .claude/skills
cp -R skills/platega .claude/skills/platega

# пользователь
mkdir -p ~/.claude/skills
cp -R skills/platega ~/.claude/skills/platega
```

Вызов: `/platega`.

### 4. Codex и другие агенты (спека Agent Skills)

```bash
mkdir -p .agents/skills
cp -R skills/platega .agents/skills/platega
```

Codex: `$platega`. Другие агенты — укажи путь к `skills/platega/SKILL.md`.

---

## Что внутри

```
skills/platega/
  SKILL.md                 # роутер: обзор, индекс, правила, ссылки
  references/auth.md
  references/payments.md
  references/subscriptions.md
  references/callbacks.md
  references/refunds.md
  references/payouts.md
  references/reporting.md
  references/cms-sdks.md
  references/legacy-gitbook.md
  references/schemas.md
  references/scenarios.md
  references/examples.md
  scripts/payout_sign.py   # HMAC-подписчик Payout API (без секретов)
```

Покрытие официального каталога: [COVERAGE.md](COVERAGE.md). История версий: [CHANGELOG.md](CHANGELOG.md).

---

## English (install)

Unofficial community **Agent Skill** for the [Platega.io](https://platega.io) merchant API. Source of truth: [docs.platega.io](https://docs.platega.io/), last read **2026-09-02**. Verify against live docs. Never commit `X-Secret` or the payout `SECRET`.

```bash
npx skills add shastitko1970-netizen/platega-skill
```

Manual:

| Agent | Path | Invoke |
| --- | --- | --- |
| Cursor | copy/symlink `skills/platega` → `.cursor/skills/platega` or `.agents/skills/platega` | `/platega` |
| Claude Code | `.claude/skills/platega` or `~/.claude/skills/platega` | `/platega` |
| Codex / others | `.agents/skills/platega` (Agent Skills spec) | `$platega` |

This publisher repo does **not** ship `.cursor/skills/` or `.claude/skills/` trees.

---

## Лицензия

[MIT](LICENSE). Не аффилировано с Platega.
