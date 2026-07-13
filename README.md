# Lead Response SLA Agent

Paused reference workload for a tenant-scoped, human-approved lead-response
pipeline. It demonstrates intake, retrieval boundaries, deterministic policy,
handoff, audit, and provider-adapter contracts without using live lead data.

Статус: paused reference implementation. Текущие public artifacts используют
только 50 synthetic garage-door scenarios и injectable/fake provider paths.
Реального pilot tenant, live CRM/lead flow, operator outcome, conversion lift,
production deployment или autonomous-send evidence в репозитории нет. Проект
не развивается как продукт без реального lead flow, CRM и оператора.

## Five-minute reference path

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt -e .
python scripts/replay_demo_leads.py --output-dir /tmp/lead-sla-replay
diff -qr docs/market/demo_replays /tmp/lead-sla-replay
python -m pytest tests/eval/test_pre_pilot_replay.py \
  tests/unit/test_reference_evidence_manifest.py -q --tb=short
```

The run is credential-free and deterministic. Start with
[`docs/REFERENCE_EVIDENCE_LEDGER.md`](docs/REFERENCE_EVIDENCE_LEDGER.md) for
checksums, claims, and limitations. A passing replay proves only fixture-level
contract behavior.

## Portfolio relationship

This repository is an independent reference workload and possible adapter
example for Eval Ground Truth Lab. It is not a flagship, is not a runtime
dependency of the reliability lab, and does not transfer its lead/tenant domain
assumptions into Runtime Grid, Workflow Studio, or the Playbook. The canonical
portfolio role and resume gate are in [`docs/PROJECT_PLAN.md`](docs/PROJECT_PLAN.md).

## Цель проекта

Собрать проверяемый pilot workflow, который принимает входящий лид из формы, мессенджера, email или webhook, быстро отвечает клиенту, квалифицирует запрос, отвечает только из утвержденной базы знаний, записывает структурированные данные в CRM/хранилище и передает рискованные случаи человеку.

Проект не пытается заменить продавца или оператора. Цель v1 - проверить, может ли AI закрыть ранний участок воронки: быстро принять обращение, не потерять контекст, задать правильный следующий вопрос и безопасно довести лид до записи, слота или human handoff.

## Гипотеза

Если малому сервисному бизнесу дать защищенный AI workflow для первого ответа и квалификации лида, то:

1. p95 первого AI-assisted ответа будет ниже 30 секунд.
2. Детерминированное подтверждение получения заявки будет уходить быстрее 2 секунд там, где это возможно.
3. Не менее 80% входящих лидов будут превращаться в структурированные записи с нужными полями.
4. Количество booked calls или qualified handoffs улучшится относительно текущего ручного процесса.
5. Операторы будут доверять системе, если у каждого ответа есть transcript, audit trail, retrieved evidence и понятная причина handoff.

## Что именно проверяем

### Скорость реакции

Проверяем, снижает ли система задержку первого ответа по сравнению с ручным мониторингом inbox, CRM notifications и шаблонными ответами.

Основные метрики:

- first-response latency p95
- deterministic acknowledgement latency p95
- доля лидов, получивших ответ до SLA threshold
- количество SLA breaches

### Качество квалификации

Проверяем, может ли AI стабильно извлекать полезные поля из грязного входящего сообщения и выбирать следующий безопасный шаг.

Основные метрики:

- доля лидов со структурированной записью
- полнота contact/service/urgency fields
- доля корректных next actions
- частота handoff из-за missing fields или low confidence

### Безопасность ответов

Проверяем, не начинает ли система придумывать цены, условия, доступность, policy или регулируемые советы.

Основные метрики:

- no-answer accuracy для unsupported questions
- доля ответов с привязкой к approved knowledge
- количество unsafe replies, остановленных human gate
- отсутствие customer-facing ответа после `insufficient_evidence`

### RAG качество

Проверяем, достаточно ли text-only RAG для FAQ, pricing ranges, service-area rules, booking rules и escalation instructions.

Основные метрики:

- hit@3 / hit@5
- MRR
- citation precision
- no-answer accuracy
- retrieval latency p95
- tenant isolation failures: должно быть 0

### Tool-use и side effects

Проверяем, можно ли безопасно подключать CRM, calendar, messaging и human-review queue без дублей и несанкционированных действий.

Основные метрики:

- schema validation pass rate
- idempotency rejection для повторных writes
- unsafe-action gate pass rate
- provider timeout fallback
- calendar booking только после fresh slot lookup и явного customer acceptance

### Операторское доверие

Проверяем, может ли оператор понять, почему система ответила, остановилась или передала лид человеку.

Основные метрики:

- доля handoff задач с transcript, reason code и evidence IDs
- время оператора на review
- доля сообщений, отредактированных оператором перед отправкой
- outcome labels для booked / qualified / lost / unsafe / unsupported

## Что не проверяем в v1

- Полную замену sales team.
- Автономные переговоры о цене или скидках.
- Legal, medical, financial или другой regulated advice.
- Multimodal retrieval.
- Live web search.
- Arbitrary external tool execution.
- Production-ready решение для всех вертикалей.

## Критерии успеха пилота

Пилот можно считать успешным, если на одном выбранном вертикальном кейсе:

- первый AI-assisted ответ стабильно укладывается в p95 ниже 30 секунд;
- минимум 80% лидов получают структурированную запись;
- unsupported и regulated вопросы уходят в human review без fabricated answer;
- RAG eval не показывает регрессий по no-answer behavior и tenant isolation;
- оператор может проверить transcript, evidence и audit trail без ручного расследования;
- booked calls или qualified handoffs лучше, чем в pre-pilot baseline.

## Критерии остановки или pivot

Проект нужно пересмотреть, если:

- настройка занимает больше времени, чем ручное улучшение процесса;
- система дает unsafe или unsupported customer-facing ответы;
- невозможно подключить основной intake channel пилотного клиента;
- first-response latency не улучшается;
- операторы не доверяют transcript, audit trail или handoff reasons;
- eval показывает tenant leakage, fabricated answers или неконтролируемые side effects.

## Текущий статус

Implementation task history сохранена в `docs/`, но продуктовый gate закрыт.
Подтверждены только synthetic/fixture contracts: human approval требуется во
всех 50 replay cases, а семь injected failure cases остаются no-send handoffs.
Это не измерение реального reliability или business outcome. Следующая
разработка допустима только после появления consented operator-owned flow,
baseline и privacy-reviewed evaluation material.

## Ключевые документы

- `docs/ARCHITECTURE.md` - архитектура и adoption reality.
- `docs/spec.md` - продуктовая спецификация.
- `docs/tasks.md` - task graph.
- `docs/IMPLEMENTATION_CONTRACT.md` - обязательные правила реализации.
- `docs/retrieval_eval.md` - RAG eval gate.
- `docs/tool_eval.md` - tool-use eval gate.
- `docs/agent_eval.md` - bounded agent loop eval gate.
- `docs/RAG_REFERENCE.md` - reference patterns из Dream Motif Interpreter.
- `docs/REFERENCE_EVIDENCE_LEDGER.md` - воспроизводимый reference evidence и
  claim boundaries.
