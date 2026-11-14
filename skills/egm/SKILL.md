---
name: EGM
description: Executa o fluxo EGM (Goldfish Review → Resolve) — 3 revisores paralelos e resolução verificada dos achados. Quando chamado dentro do /egm-openspec, já roda na worktree isolada criada na Fase 0; quando chamado isolado, o caller deve garantir a worktree isolada como primeiro passo. metadata: author: openspec version: "1.1" ---

Acione 3 revisores em paralelo, cada um com um escopo:
- **A** — Arquitetura
- **S** — SOLID
- **C** — Clean Code / Escopo

Cada revisor lista achados numerados (`A-01`, `S-01`, `C-01`) contra o artefato alvo (`design.md`, código, etc.).

## Fase 2 — Resolve

Para cada achado:
1. Classifique: **aceito**, **rejeitado** (com motivo) ou **parcial**.
2. Verifique com evidência (grep, referência `arquivo:linha`, build/teste).
3. Registre em `deficiencias_resolvidas.md`:

| id | achado | resolução/verificação | onde entra |
|---|---|---|---|

## Regras

- Rejeite falso positivo com a verificação que o derruba.
- Não aceite sugestão invertida (ex.: deletar caso de uso para manter lógica no endpoint).
- Cada aceite precisa de verificação que o sustente.
