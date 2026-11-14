---
name: egm-openspec
description: Orquestra implementação OpenSpec criando uma worktree isolada como primeiro passo, seguida de EGM prévio, commit dos artefatos, apply instructions e QA iterativo até PASS. Ao digitar /egm-openspec pegará do contexto o nome do spec e já iniciará o workflow.
allowed-tools: Bash(openspec:*), Bash(npx playwright:*), Bash(git status:*), Bash(git add:*), Bash(git commit:*), Bash(git worktree:*), Bash(git rev-parse:*), Bash(./scripts/build.sh:*), Bash(docker:*), Bash(npm:*), Bash(dotnet:*)
license: MIT
metadata:
  author: plex-autoplay
  version: "1.3"
  specification:
    agent-source: antgravit
    required-agents: [frontend, backend, qa]
    excludes: [plan-writing, clean-code, tdd-workflow, verify-changes, testing-patterns, lint-and-validate, code-review-checklist, frontend-architecture, webapp-testing]
    docker:
      rebuild: true
      clean: true
      use-release: true
---

# Skill `egm-openspec` (`/egm-openspec`)

## Descrição

Fluxo orquestrado que obriga:

1. **Worktree isolada (PRIMEIRO PASSO OBRIGATÓRIO)** — Antes de absolutamente qualquer outra ação (inclusive EGM, preflight ou leitura de status), cria uma worktree dedicada com branch `feature/spec-<nome da spec>` e move a sessão para ela (`tools.opencode.session_move`). Tudo que o fluxo criar fica isolado nessa worktree; o worktree principal nunca recebe esses commits.
2. **EGM prévio (na worktree)** — Executa Goldfish Review (A/S/C) sobre requisitos e design antes de implementar, já dentro da worktree.
3. **Commit dos artefatos (na worktree)** — Commita os artefatos da change na branch da worktree antes do apply.
4. **Apply instructions** — Utiliza `openspec instructions apply` como fonte de verdade para dividir tarefas e validar schema.
5. **Implementação com agentes antgravit** — Cada agente carrega skills `antigravity-skills-manager` e é orquestrado via `/antigravity`. Os agentes incluem: frontend, backend e QA.
6. **QA independente** — Valida resultado contra o spec gerado: critérios do spec, tasks.md, lint/format/build, `openspec validate <change> --strict` e tema/menu (validação UI obrigatória).
7. **Loop até PASS** — Se QA der FAIL, descarta agentes e cria novos limpos com apenas spec + achados do QA, repetindo até PASS (máx. 5 iterações).
8. **Relatório HTML consolidado** — Ao final gera `openspec/changes/<change>/report.html` com árvore de alterações (adicionado/removido/alterado), relatórios QA de todas as rodadas, correções e evidências de teste; exibido no resultado do spec.

## Estrutura do fluxo

```
Worktree isolada (1º passo) → Preflight → EGM (A/S/C) → Commit artefatos → Apply → Implement → Build → QA → PASS? fim
                                                                                                  FAIL → volta à implementação
```

**Gate absoluto de isolamento:** a worktree DEVE ser criada e a sessão DEVE ser movida para ela antes de qualquer outra fase. Nenhum comando de EGM ou preflight roda no worktree principal. Nenhum artefato, commit ou código deste fluxo é escrito no worktree principal.

**Gate do apply:** `/opsx-apply` (opx:play) só inicia depois do commit dos artefatos na worktree.

## Fase 0 — Worktree isolada (primeiro passo)

**Obrigatório antes de tudo.** Nenhuma outra fase roda antes desta.

1. Determinar `<change>` (argumento; senão inferir do contexto; senão perguntar). O nome é a única entrada necessária nesta fase.
2. Verificar estado: `git status --porcelain`. Se houver mudanças não relacionadas à change, parar e perguntar (nunca usar `git add .`).
3. Criar worktree dedicada + branch a partir do HEAD atual:
   ```bash
   git worktree add "../<repo>-<change>" -b "feature/spec-<change>"
   ```
   Nome do branch: `feature/spec-<nome da spec>` (ex.: `feature/spec-add-user-auth`).
4. Se branch/worktree já existirem: reutilizar apenas se estiverem limpos e apontando para a change correta; caso contrário parar e reportar.
5. **Artefatos não commitados:** a worktree é criada do HEAD e não herda mudanças não commitadas. Se `openspec/changes/<change>` tiver artefatos não commitados no worktree principal, copiá-los para a worktree **antes** de sair do principal (ex.: `cp -r openspec/changes/<change> ../<repo>-<change>/openspec/changes/`). Esses arquivos são commitados na worktree na Fase 2, nunca no principal.
6. Mover a sessão para a worktree (`tools.opencode.session_move`) e executar **todo** o trabalho restante lá.

## Fase 1 — Preflight + EGM nos requisitos (na worktree)

Executar já dentro da worktree:

1. `openspec status --change "<change>" --json` (se change existir).
2. `openspec instructions apply --change "<change>" --json`.
3. Ler todos os `contextFiles`; se `state: blocked` ou `missingArtifacts` não vazio: parar e reportar.

Depois, Goldfish Review em paralelo, cada revisor lista achados numerados:

- **A**: arquitetura, dependências e integração.
- **S**: SOLID e coesão.
- **C**: Clean Code, escopo e testabilidade.

Cada achado classificado como aceito, rejeitado (com motivo) ou parcial. Registrar em `openspec/changes/<change>/deficiencias_resolvidas.md` (dentro da worktree).

Achados aceitos que mudem requisito exigem atualizar artefatos da change antes de implementar; depois reler `openspec instructions apply`.

## Fase 2 — Commit dos artefatos (na worktree)

**Pré-condição do `/opsx-apply` (opx:play).** Nenhuma implementação começa antes desta fase.

1. Verificar estado na worktree: `git status --porcelain`. Se houver mudanças não relacionadas à change, parar e perguntar (nunca usar `git add .`).
2. Commitar **somente** artefatos da change, na branch da worktree:
   ```bash
   git add openspec/changes/<change>
   git commit -m "docs(openspec): add <change> artifacts"
   ```
   Incluir `deficiencias_resolvidas.md` se gerado. Não commitar código de implementação.
3. Reexecutar `openspec instructions apply --change "<change>" --json` na worktree e confirmar `contextFiles` antes de spawnar implementadores.

## Fase 3 — Implementação orquestrada

O orquestrador:

1. Divide tarefas por domínio e dependência.
2. Spawna implementadores independentes (paralelo quando não houver conflito de arquivos).
3. Cada implementador recebe apenas: trecho do spec, design, tarefa e contrato de diretórios. Nunca recebe relatório QA de outra iteração.
4. Implementador marca `- [x]` quando comportamento especificado estiver completo.

**Após implementação concluída**, o orquestrador **constroi** a solução usando o pipeline canônico:
```bash
./scripts/build.sh
```
O script executa: `npm ci` + `npm run build` em `vue/plex-frontend`, substitui `src/PlexAutoplay.Web/wwwroot`, compila `PlexAutoplay.slnx -c Release`, e roda `docker compose -f infra/docker-compose.yml build` com label `org.opencontainers.image.revision`. Se o build falhar, volta ao início da Fase 3 para nova tentativa. Se passar, procede à Fase 4.

## Fase 4 — QA independente

**Build já foi validado na Fase 3** — QA foca em validação comportamental e de especificação:

1. Cada critério do spec (`specs/**` e `design.md`) tem implementação correspondente.
2. `tasks.md` reflete apenas trabalho realmente concluído.
3. Testes automatizados e lint/format passam (`npm run lint` em `vue/plex-frontend`; `dotnet build PlexAutoplay.slnx -c Release`).
4. `openspec validate <change> --strict` passa.
5. **Validação UI obrigatória** — O QA **deve acessar** `http://localhost:<port>` (ou URL publicada do container) **usando Playwright** (script de navegador real, nunca inspeção só de código) e validar obrigatoriamente:
   a) Tema (light/dark toggle/respeito ao theme config) está sendo aplicado corretamente em todos os componentes;
   b) Menus estão funcionando (abertura, navegação, fechamento, estados ativos);
   c) Não é necessário testar CRUD completo, apenas navegação/interação visual.
6. Registrar URL acessada como evidência (screenshot/asserts Playwright) e validar que não há impacto não identificado nas rotas/menu/item ativo.
7. **Docker acceptance**: build imagem limpa com `docker build --no-cache -f infra/Dockerfile -t plex-autoplay:<change> .` (ou `docker compose -f infra/docker-compose.yml build` com `GIT_COMMIT`); rodar container isolado; validar contra versão published/release `docker run plex-autoplay:<change>`.

Saída obrigatória em `openspec/changes/<change>/qa-report-<n>.md`: `PASS` ou `FAIL` + achados numerados com evidência, arquivo esperado e **URL de validação acessada**.

## Fase 5 — Loop de correção

Se `FAIL`:

1. Descartar contexto dos implementadores anteriores.
2. Voltar ao **Build gate** — Criar agentes limpos com apenas: spec, design, lista de achados do QA e diretório permitido.
3. Corrigir, rodar build novamente, e voltar à Fase 4 (QA).

Limite padrão: 5 iterações (configurável). Ao exceder, parar e reportar bloqueio com histórico de QA, sem mascarar falha.

## Fase 6 — Encerramento

Com PASS:

1. **Commit implementação** (na worktree): adicionar e commitar arquivos de implementação alterados:
   ```bash
   git add -A
   git commit -m "feat(<change>): implement <change>"
   ```
2. **Push + PR**: enviar branch para remote e abrir PR:
   ```bash
   git push -u origin feature/spec-<change>
   gh pr create --title "feat(<change>): implement <change>" --body "$(cat openspec/changes/<change>/report.html | head -200)" --base main
   ```
3. Reportar arquivos alterados, relatório QA final, progresso de tarefas, link do PR e próximos passos (`/opsx-archive`). A worktree e a branch `feature/spec-<change>` permanecem para revisão/merge.

## Fase 7 — Relatório HTML consolidado

Após o PASS final, gerar relatório HTML consolidado em `openspec/changes/<change>/report.html` contendo:

1. **Árvore de alterações** (estilo githud/copilot): estrutura de diretórios aninhada com ícones +/− por arquivo, linhas adicionadas/removidas, status (A/M/D/R).
2. **Relatórios QA por iteração**: cada `qa-report-<n>.md` renderizado como seção expansível, com sumário PASS/FAIL, critérios verificados, achados e URL de validação acessada.
3. **Rodadas de correção**: resumo de quantas iterações, o que mudou entre cada QA.
4. **Evidências de teste**: links para relatório Playwright HTML, screenshots, traces, logs da aplicação e URL de validação (extraídos dos QA reports).
4. **Próximos passos**: arquivos pendentes, sugestão de archive/merge.

Execução: `python3 scripts/generate-report.py <change> --repo <worktree>` (script incluído no skill). O caminho do relatório é impresso no resultado do spec para leitura imediata (`file://.../report.html`).

## Guardrails

- **A worktree isolada é o primeiro passo.** Nenhuma fase (preflight, EGM, apply, implementação) começa antes da worktree existir e da sessão estar nela.
- **Todo trabalho ocorre na worktree.** Nenhum commit, artefato ou código deste fluxo é escrito no worktree principal.
- Orquestrador nunca aprova o próprio trabalho; QA é sempre agente separado.
- Agente que falhou nunca é reutilizado; sempre recriado limpo.
- `tasks.md` é fonte de progresso; checkbox só após comportamento completo.
- Não reduzir escopo do spec para fazer o QA passar.
- Toda correção precisa de evidência de verificação.
- Segredos, credenciais e dados sensíveis nunca entram em relatórios ou prompts.
- Nunca implementar no worktree principal: após a Fase 0, todo trabalho ocorre na worktree `feature/spec-<change>`.
- Nunca usar `git add .` no commit dos artefatos; adicionar apenas `openspec/changes/<change>`.
- Sem worktree criada, o fluxo não prossegue; sem commit dos artefatos, `/opsx-apply` (opx:play) não pode iniciar.

## Comando /egm-openspec

### Uso

```unknown
/egm-openspec [nome-da-especificacao]
```

- Se um nome for fornecido como argumento, usá-lo como a especificação-alvo
- Se nenhum nome for fornecido, inferir o nome da especificação do contexto da conversa
- Se ambíguo, solicitar ao usuário para selecionar/especificar

### Como funciona

Ao digitar `/egm-openspec` ou `/egm-openspec MeuEspecificacao`:

1. **Inferir nome da especificação**
   - Se argumento fornecido: usar diretamente
   - Se não fornecido: ler contexto da conversa para encontrar referência a spec/change
   - Se múltiplas specs no contexto: solicitar usuário especificar qual

2. **Criar worktree isolada (primeiro passo)**
   - `git worktree add "../<repo>-<especificacao>" -b "feature/spec-<especificacao>"`
   - Preservar artefatos não commitados da change copiando-os para a worktree
   - Mover a sessão para a worktree (`tools.opencode.session_move`)
   - Nada é executado antes disso; todo trabalho restante ocorre na worktree

3. **Preflight + EGM (Goldfish Review → Resolve)**
   - Executar `openspec status` / `openspec instructions apply --json` na worktree
   - Iniciar 3 revisores paralelos (Arquitetura A, SOLID S, Clean Code C)
   - Cada revisor lista achados numerados contra o artefato alvo
   - Classificar cada achado: aceito, rejeitado (com motivo) ou parcial
   - Registrar em `deficiencias_resolvidas.md` (na worktree)

4. **Commit dos artefatos (na worktree)**
   - `git add openspec/changes/<especificacao>` e commit `docs(openspec): add <especificacao> artifacts`
   - Commits vão para a branch `feature/spec-<especificacao>`, nunca para o principal

5. **Aplicar instruções**
   - Executar `openspec instructions apply --change "<especificacao>" --json` na worktree
   - Dividir tarefas baseado no contexto retornado
   - Implementar tarefas minimamente

6. **Build gate**
   - Orquestrador constrói a solução
   - Se build falhar: volta ao início da Fase 3 (implementação)
   - Se passar: procede à validação QA

7. **QA independente**
   - Validar contra critérios do spec
   - Verificar `openspec validate <change> --strict`
   - Gerar relatório QA

8. **Loop até PASS**
   - Se QA der FAIL: descartar agentes, criar novos limpos, repetir do Build gate
   - Máximo 5 iterações antes de reportar bloqueio

9. **Relatório HTML consolidado (Fase 7)**
   - Após PASS: `python3 scripts/generate-report.py <change> --repo <worktree>`
   - Gera `openspec/changes/<change>/report.html`: árvore de alterações (A/M/D/R, +/−), relatórios QA por iteração, rodadas de correção e evidências de teste (Playwright, screenshots, traces, URL acessada)
   - Imprime o caminho `file://.../report.html` no resultado do spec para leitura

### Exemplos

```unknown
/egm-openspec              # Inferir nome do contexto, criar worktree isolada e iniciar o fluxo
/egm-openspec add-user-auth  # Criar worktree "feature/spec-add-user-auth" e usar como especificação-alvo
```
