# Roadmap de entrega

Este roadmap é derivado do `multi-tenant-saas-platform-master-spec.md`. Os cartões são pequenos, verificáveis e mantêm a decisão arquitetural de PostgreSQL nativo, sem Docker.

| Fase | Cartões | Critério de aceite | Estado |
| --- | --- | --- | --- |
| Fundação | MTS-001–005 | repositório, configuração nativa, API/UI, migration reproduzível | concluído |
| Fronteiras de confiança | MTS-006–011 | Argon2/JWT, tenant resolver, membership, matriz RBAC, roles DB separadas, RLS | concluído |
| Controles SaaS | MTS-012–020 | CRUD tenant-scoped, quota transacional, feature overrides, audit, traces, probes e dataset | concluído |
| Explorer | MTS-021–026 | dashboard React, mapa XYFlow, estados de execução, timeline e ações ligadas à API | concluído |
| Entrega | MTS-027–028 | CI PostgreSQL 16 nativo, documentação, threat model, README e revisão final | concluído |

## Gate final

- `ruff check .`, `pytest`, `npm run lint` e `npm run build` passam localmente.
- A CI executa migration, seed, avaliação dos 14 cenários e build em PostgreSQL 16 nativo.
- O commit promovido para `main` é o mesmo commit validado pela CI.
- Capturas devem ser feitas pelo navegador contra a aplicação em execução; a pasta `docs/screenshots/` contém o protocolo e não aceita mockups.

## Execução futura

1. Instalar PostgreSQL 16 nativo.
2. Executar `scripts/bootstrap-postgres.sql`, `alembic upgrade head` e `python -m app.seed`.
3. Subir FastAPI e Vite, executar os cenários no Security Explorer e salvar as capturas reais em `docs/screenshots/`.
