# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# CONTEXTO DO PROJETO — MPUB Intelligence

## Stack & Estado
- **Produto:** conversor RTM/ReportBuilder (Delphi) → JRXML (JasperReports) via Claude API.
- **Legado (desativado 2026-06-12):** Flask em `_legado_flask/` (`app.py` ~13k linhas + `modules/*.py`). Fora de produção desde a migração. Não usar nem refatorar.
- **Prod / em uso:** Django em `django_app/` na branch `main` (refatoracao já mergeada). **Fases 1–7 ✅** + **Paridade Flask→Django 100% (round 37, 2026-05-06)**. Stack: auth, dashboard+SQL Server, conversão RTM, blueprints PDF/imagem/adjuster/editor/support+analytics+PPR, hardening AuditLog+rate limit+CSP, Celery+Redis+Docker, **Testes 943 verdes + CI gate 75% + pre-commit ruff**, rotas analíticas (`/architecture`, `/graph`, `/api/graph-data`, `/api/feedback-stats`).
- **Parser RTM→JRXML:** §4.1–§4.9 ✅ todos resolvidos.
- **URLs:** tudo sob `/agente/`. Raiz `/` → login.
- **Layout do repo (reorg 2026-06-12):** `django_app/` (sistema em uso) · `_legado_flask/` (Flask desativado) · `docs/` (PRD, CONSULTAS_PPR, PLANO_HARDENING) · `mapeamento/` (fixtures de conversão **por tipo**: `pdf/ md/ jrxml/ jasper/ json/ rtm/ txt/ xml/ jpeg/` — ex-`Mapa RTM/`). Testes leem fixtures de `mapeamento/rtm/` e `mapeamento/md/`. Git versiona só `django_app/` + meta.

## Arquitetura Django
- **Templates:** Jinja2 (não DTL). Backend: `mpub/jinja2.py`.
- **User:** `accounts.User(AbstractUser)` + `modulos` (JSONField) + `grupo` + `WerkzeugPBKDF2PasswordHasher`.
- **Auth:** `LoginRequiredMiddleware` (allowlist: login, static, healthcheck).
- **DB interno:** SQLite (`users.db`, `history.db`). **DB cliente:** SQL Server dinâmico via pyodbc (credenciais por sessão).
- **Async:** `threading.Thread` + `task_runner`. Celery+Redis = Fase 6.

## Comandos de desenvolvimento
Tudo roda de dentro de `django_app/` com a venv ativa (`venv\Scripts\activate`). Em Docker, prefixar `manage.py` com `docker compose exec web python` (ver seção Docker).

### Testes — pytest + pytest-django (`DJANGO_SETTINGS_MODULE=mpub.settings` já no `pytest.ini`; banco forçado `:memory:`)
```bash
pytest                                   # suíte completa (~950 testes)
pytest tests/test_converter.py           # um arquivo
pytest tests/test_converter.py::test_x   # UM teste isolado
pytest -k "listagem"                     # por substring do nome
pytest -m smoke                          # só smoke (auth + URLs básicas)
pytest -m "not slow"                     # pula os que chamam IA/serviços externos
pytest --cov --cov-fail-under=75         # com coverage gate (espelha o CI)
```
Os 54 arquivos de teste ficam **todos em `django_app/tests/`** (não dentro dos apps). `conftest.py` + `factories.py` estão lá.

### Lint/format — ruff (config em `pyproject.toml`, regras `E,F,W,I,B`)
```bash
ruff check .                 # lint
ruff check . --fix           # autofix
ruff format .                # format
pre-commit run --all-files   # hooks (ruff + whitespace/EOF/YAML); pytest NÃO está aqui, só no CI
```

### manage.py (local)
```bash
python manage.py runserver 0.0.0.0:8000
python manage.py migrate <app>     # OBRIGATÓRIO após qualquer mudança em models.py
python manage.py shell
python manage.py sync_sip_users    # importa usuários do SIP_MP (idempotente)
```

## Mapa dos apps Django (rotas sob `/agente/`)
| App | Rota | Função |
|---|---|---|
| `accounts` | `/agente/` | Auth (LoginView, modules), User custom, sync SIP |
| `dashboard` | `/agente/` | Home + analytics + rotas `/architecture`, `/graph`, `/api/graph-data`, `/api/feedback-stats` |
| `converter` | `/agente/convert/` | RTM/ReportBuilder → JRXML (usa o Pipeline core abaixo) |
| `pdf_analyzer` | `/agente/pdf/` | PDF → JRXML (schema-aware AI; introspeta o banco conectado) |
| `image_analyzer` | `/agente/image/` | Imagem → JRXML |
| `rtm_adjuster` | `/agente/rtm/` | Edita RTM por linguagem natural |
| `report_editor` | `/agente/editor/` | Edita JRXML existente |
| `report_creator` | `/agente/criar/` | Gera JRXML do zero a partir de descrição em texto |
| `support` | `/agente/support/` | Integração SIP (chamados) + analytics |
| `listagem_maker_ia` | `/agente/listagem-v2/` | Conversão `FR_LISTAGEM` LST_JSON OLD→NEW; lógica real em `core/services/listagem_v2/` (`converter`, `persist`, `jrxml_builder`, `db_io`) |
| `core` | — | Biblioteca compartilhada: `services/` (pipeline **INTOCÁVEL**), `security/`, `db_connection.py` |
| `tools` | — | Utilitários sem rotas HTTP (ex: `batch_smoke.py`) |

## Pipeline core (em `core/services/` — INTOCÁVEL durante migração)
| Arquivo | Função |
|---|---|
| `rtm_parser.py` | DFM → dict (26 classes Delphi, 45 cores, mm/px, `#NNN`) |
| `ai_converter.py` | Orquestrador AI vs regex; `_is_header_pipeline()` / `_is_aux_pipeline()` |
| `jrxml_generator.py` | XML string (rota principal) |
| `jpype_generator.py` | Gera via JPype → `.jasper` direto |
| `pascal_to_jasper.py` | Transpila Pascal (OnGetText/OnCalc/BeforePrint) → Java JasperReports |
| `auto_fixer.py` | Pós-proc: encoding `#NNN`, enums, BandType |
| `rtm/ai_rtm_adjuster.py` | Edita RTM por linguagem natural |

## Docker — operação e ambiente

### Topologia (3 services em `docker-compose.yml`)
- **redis** (`redis:7-alpine`): broker Celery + cache + session. AOF persistence, 512MB max, `allkeys-lru`.
- **web** (build de `django_app/Dockerfile`): gunicorn na porta `5050`, `DJANGO_ENV=prod`.
- **worker**: `celery -A mpub worker --concurrency=4 -Q celery,batch --prefetch-multiplier=1`
  - Fila `celery` (default): PDF, RTM, converter, support, image — interativo.
  - Fila `batch`: `listagem_maker_ia.convert_one/finalize` — lote 40+ que saturava worker (vide CELERY_TASK_ROUTES em `mpub/settings.py`).
  - `prefetch-multiplier=1`: 1 task por slot — sem reserva de 4 (que bloqueava UI).

### Variáveis críticas (`.env` na raiz)
- `MPUB_RUNNING_IN_DOCKER=1`: `core/db_connection` reescreve `localhost`/`127.0.0.1` informados pelo user → `host.docker.internal` (compose já declara `extra_hosts` pra funcionar em Linux).
- `MPUB_DB_ENGINE=sqlserver` + `MPUB_DB_SERVER/PORT/NAME/USER/PASSWORD`: banco interno do MPUB (`MPUB_INTELLIGENCE`). Sem isso usa SQLite.
- `CELERY_BROKER_URL=redis://redis:6379/0` (hostname interno do compose, NÃO `localhost`).
- `ANTHROPIC_API_KEY`: passada via env_file pro worker e web.

### Volumes persistentes
- `./data/redis` → estado do Redis (sobrevive `down`).
- `./data/media` → uploads runtime.
- `./data/output` → outputs gerados (JRXML, PDFs, etc).
- `./users.db` → SQLite (só usado se `MPUB_DB_ENGINE=sqlite`).

### Deploy PROD (servidor 244 — `centos@244-mpub-inteligence`)
Pedro testa em PROD direto. Workflow padrão de subida:
```bash
git pull
docker compose down
docker compose build --no-cache
docker compose up -d
docker compose logs -f web
```
- **NUNCA** rodar `git commit/push` no PROD — push só do local, sempre.
- Após alterar `requirements.txt`: `--no-cache` é obrigatório.
- Alteração só em `.py` (sem deps novas): `docker compose build && docker compose up -d` é suficiente.
- Toda alteração em `models.py` exige `docker compose exec web python manage.py migrate <app>` ANTES de testar.

### Comandos comuns em runtime
```bash
# Logs
docker compose logs -f web
docker compose logs -f worker

# Shell Django
docker compose exec web python manage.py shell
docker compose exec web python manage.py migrate <app>

# Script ad-hoc sem criar arquivo (uso frequente p/ banco-cliente):
docker compose exec -T web python << 'PYEOF'
import pyodbc, json
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=<ip>;DATABASE=<db>;UID=<user>;PWD=<pwd>;"
    "TrustServerCertificate=yes;Encrypt=no"
)
cur = conn.cursor()
cur.execute("SELECT ...")
conn.close()
PYEOF
```

### Build gotchas conhecidos
- `parent snapshot does not exist` (buildkit, 2026-06-03): resolve com `docker compose build --no-cache`. Pode reaparecer após `docker system prune`.
- Worker sobrecarregado por chord de listagem (TimeLimitExceeded 300s) → resolvido com fila `batch` + `prefetch=1` + capturar `SoftTimeLimitExceeded` em `task_runner.py` (2026-06-03).

## Regras de trabalho (OBRIGATÓRIAS)
1. **Zero Fluff** — código primeiro. Não explique a menos que eu diga `"Explique:"`.
2. **Diffs pequenos** — mostre só a função/classe alterada + contexto. Nunca reescreva arquivo inteiro.
3. **Modular** — 1 app/módulo por tarefa. Ao concluir, pergunte: `"Posso prosseguir?"`.
4. **Core intocável** — `core/services/` (originado de `_legado_flask/modules/*.py` na migração). Zero refatoração.

## 🧠 Segundo Cérebro Obsidian — REGRA PERMANENTE

**Vault:** `C:/Users/pedro/Documents/Claude Brain/`
**Nota principal do projeto:** `Cerebro Migrações/MPUB Intelligence - Migração Django.md`
**Referência RTM:** `Cerebro Migrações/RTM ReportBuilder - Mapeamento Técnico.md`

### Quando atualizar (SEMPRE, não só no fim de fase):
- ✅ Qualquer **decisão arquitetural** tomada na sessão
- ✅ Qualquer **bug encontrado e resolvido** (causa + solução)
- ✅ Qualquer **padrão novo descoberto** no RTM/DFM/JasperReports
- ✅ Qualquer **comportamento inesperado** do Django, Jinja2, pyodbc, JPype
- ✅ Ao **concluir uma função, view ou serviço** — registrar o que foi feito e por quê
- ✅ Ao **finalizar uma fase** — resumo do que foi implementado
- ✅ Se **atualizar conhecimento existente** — sobrescrever/complementar o que já está na nota

### Formato padrão para cada entrada no Obsidian:
```markdown
## [DATA] — [Tarefa ou Descoberta]
**O que foi feito:** ...
**Decisão tomada:** ...
**Motivo:** ...
**Arquivos alterados:** ...
**Atenção futura:** ... (se houver)
```

### Ao iniciar cada sessão:
Leia a nota principal antes de qualquer tarefa para recuperar o estado atual.
Se a nota estiver desatualizada em relação ao código, sinalize: `"⚠️ Obsidian desatualizado em: [tópico]"`.

## Alertas ativos
- **Auth centralizada no SIP_MP (2026-05-13)**: usuários/senhas/equipes vêm de `SIP_MP.FR_USUARIO` (SQL Server `10.15.41.251`) via `python manage.py sync_sip_users` (idempotente, agendado 03:30 via Celery Beat). Senha guardada como `sip_md5$<hex>` — hasher `SIPMD5PasswordHasher` valida MD5 e **não re-hasheia** (SIP é fonte da verdade). Cadastro local desabilitado (view `register` redireciona). Coordenador (EQM_TIPO='C') vira superuser; Líder ('L') vira staff. Equipes mapeiam pra módulos via `TEAM_TO_MODULES` no comando — **adicionar entrada antes que apareça equipe nova no SIP** (senão user fica sem módulos).
- Senhas default (`admin/admin`) ainda ativas → Fase 5.
- API key Anthropic exposta no histórico `.env` → rotacionar no console.
- **Schema-aware AI (2026-05-12)**: PDF/Image→JRXML agora introspeta o banco conectado e valida tabelas referenciadas em `<queryString>`. Sem conexão ativa no momento do upload, IA volta a chutar nomes — sempre conectar antes.
- **Banco interno em SQL Server (2026-05-12)**: `MPUB_DB_ENGINE` no `.env` controla SQLite (dev) vs SQL Server (prod, `MPUB_INTELLIGENCE`). Pytest força `:memory:`. mssql-django 1.5 precisa de 2 patches inline (Dockerfile aplica).
- Parser §4: 9 de 9 itens resolvidos ✅.
- **Gaps RTM "Extrato da Dívida" (2026-05-05) — 3 fixes aplicados em 2026-05-05**:
  - ✅ **Pascal accumulator `Value := Value + X`** detectado em `pascal_to_jasper.detect_variable_handlers` → emite `<variable calculation="Sum">` + textField com `$V{name}`. Cobre 8 das 13 TppVariables do RTM extrato (era expression Java inválida `Value + $F{X}`).
  - ✅ **Sintaxe oficial Maker `<dbtext datapipeline='X' displayformat='Y'>FIELD</dbtext>`** em `rtf_to_html._MERGE_TAG_RE` (4ª regex). Suporta displayformat opcional → `_render_rich_text_field` aplica mask CPF/CNPJ/CEP via `_convert_mask_expression` ou DecimalFormat/SimpleDateFormat inline.
  - ✅ **PassSetting=psTwoPass** detectado em `RTMParser._parse_pass_setting()`. Quando ativo + variável Sum em title/pageHeader/columnHeader/groupHeader → textField recebe `evaluationTime="Report"` (totais agregados disponíveis na 1ª renderização).
  - ✅ **Pascal `variable1.value` (lowercase) → `$V{Variable1}`** (2026-05-08, Rel-Eduardin `Execucao Fiscal Novo_01.rtm`): Pascal é case-insensitive, RTM declara `UserName='Variable1'` mas handler usa `variable1.value`. Sem tradução, JR Studio falha com "variable1.value cannot be resolved to a type". Fix em `pascal_to_jasper._pascal_to_java_expr`: regex `\b([A-Za-z_]\w*)\.[Vv]alue\b` → `$V{<Ident>}` (capitaliza 1ª letra).
  - 🟡 Restantes: TppDBImageEx props (AlignH/V, Stretch, GraphicType), TppRegion.OnPrint, DisplayFormat com escape `\\.` `\-` complexo (CEP/CNPJ no `<dbtext>` já cobertos via mask), Multi-coluna ChildReport, ShiftRelativeTo, vtPageSetDesc.

## 🔴 Bugs em investigação (2026-06-04) — `listagem_maker_ia` (JSON_OLD → JSON_NEW)

**Sintoma**: ao abrir uma `FR_LISTAGEM` NEW gerada pelo conversor V2 no MAKER (página "Listagens e Relatórios"), Tomcat estoura `OutOfMemoryError` em `wfr.com.systems.system_fpg.rules.ListagemListaDeVersoesRelatorio.java:117` (linha do `ebfReplaceAll`). StringBuilder cresce >2GB. Tela trava ou carrega vazia.

**Repro empírico** (LST_COD 226, banco `FPG_PMCABOFRIO_FIVE`):
- ❌ NEW gerada pelo conversor V2 → trava.
- ✅ JSON do OLD (LST_COD 94) copiado pro 226 com **chave externa renomeada pra bater com LST_NOME** → abre, gera PDF 96 páginas.

### Bug 1 — CONFIRMADO: mismatch chave externa do JSON vs LST_NOME
- `LST_NOME = "<Nome> - NEW"`, mas a chave externa do JSON fica `"<Nome>"` (sem o sufixo).
- MAKER procura `JSON["<Nome> - NEW"]`, não acha, fallback Java entra em loop no `ebfReplaceAll`.
- **Fix pendente**: em `core/services/listagem_v2/task_runner.py` (após `convert_lst_json_old_to_new`), renomear a chave externa do JSON pra bater com `LST_NOME` do NEW antes de gravar.

### Bug 2 — CONFIRMADO: regex de parse SQL não cobre T-SQL sem `AS`
- `_SELECT_FIELD_RE` em `core/services/listagem_v2/converter.py:183-188` EXIGE `AS` antes do apelido.
- SQL real do MAKER usa formato T-SQL: `OEN.OEN_COD [Código da Entidade]`, `FUN.FUN_MATRICULA Matrícula` (sem `AS`).
- Resultado: `propriedades.<campo>.tabelasql` e `camposql` ficam vazios; `CamposTela.<campo>` sem esses campos.
- **Fix pendente**: tornar `AS` opcional na regex → `r"(?:\s+(?:AS\s+)?(?P<apelido>...))?"`. Cobre 4 formatos T-SQL: `col AS [X]`, `col AS X`, `col [X]`, `col X`.
- Não trava o MAKER (Bug 1 é o gatilho do OOM), mas afeta features de filtro/agrupamento.

### Bug correlato — `CamposTela` não recebe `tabelasql`/`camposql`
- O conversor adiciona em `propriedades.<campo>` mas **não propaga** pra `CamposTela.<campo>`.
- Gold do gerente do Pedro (formato esperado) tem ambos.
- **Fix pendente**: em `convert_lst_json_old_to_new` (linha 434-440), depois de popular `meta["tabelasql"]`/`meta["camposql"]`, o body["CamposTela"][field_name] já reflete (mesma referência) — confirmar se Bug 2 causa raiz é só a regex.

### Re-conversão dos 107 NEW existentes
Após aplicar fixes 1+2, script ad-hoc no PROD pra re-processar tudo:
- Chamar `convert_lst_json_old_to_new(json_str, force_recreate_propriedades=True)`.
- Renomear chave externa pra `LST_NOME`.
- `UPDATE FR_LISTAGEM SET LST_JSON = ? WHERE LST_COD = ?`.

### Histórico relacionado (resolvido)
- ChordError TimeLimitExceeded(300): saturava worker → fila `batch` + `prefetch=1` + capturar `SoftTimeLimitExceeded` (2026-06-03).
- Anthropic API timeout 90s/2 retries cortava demais → 240s/0 retries (`core/services/ai_client.py`).

## ⚠️ Lição RTM→JRXML — parâmetros (REGRA PERMANENTE)

**Regra:** parâmetros têm 2 sintaxes que NÃO podem ser confundidas:
- **RTM (origem, RB Delphi)**: `:PARAM` (Oracle named parameter)
- **JRXML (destino, JasperReports)**: `$P{PARAM}` + obrigatório `<parameter name="PARAM">` declarado **dentro do escopo onde é usado** (no `<jasperReport>` master ou em CADA `<subDataset>`)

**Conversão**: `build_query_string()` faz `:PARAM` → `$P{PARAM}`. Toda extração de params **depois** dele deve detectar `$P{}`, não `:PARAM`.

**Toda nova rotina que extraia parâmetros do SQL precisa de AMBAS as regex**:
```python
params_in_sql  = set(re.findall(r":(\w+)", sql_apos_build_query_string))
params_in_sql |= set(re.findall(r"[$]P[{](\w+)[}]", sql_apos_build_query_string))
```

**Bugs históricos dessa classe:**
- 2026-05-07 (`_add_subdatasets`): só detectava `:PARAM`, perdia `$P{OEN_COD}` no SQL final → JR rejeitava com `Unknown parameter X in dataset Y`. Fix + teste de regressão `test_subdataset_declares_dollarp_parameters`.

## Hardening recente (2026-05-04)
- ✅ `converter.py:_generate_preview_json` — dict mutation during iteration. Fix: `list(self.result['files'].items())`. Agora todos os JRXMLs (>1) recebem preview.json.
- ✅ `jrxml_visual_parser.py:79,113,115` — `find() or find()` truth-value gotcha com Element vazio. Fix: `if x is None: x = ...`. Agora `<band height="X"/>` vazia em groupHeader/Footer aparece no preview.
- ✅ `sip_client.py` SQL injection — substituído blacklist `_sql_escape` por `_sql_quote` (escape padrão SQL `'`→`''`), `_sql_quote_like` (escapa wildcards `%`/`_`/`[`) e `_validate_cls_filter` (whitelist). Todos os métodos públicos cobertos por testes de regressão de injeção em `test_sip_client_sql_safety.py`.
- ✅ Dependências CVE — Django 5.2.5→**5.2.13** (18 CVEs SQL injection/DoS), Jinja2 3.1.4→**3.1.6** (3 CVEs sandbox escape), python-dotenv 1.0.1→**1.2.2** (CVE symlink). Restou apenas pytest 8.4.2 (dev-only, UNIX-local DoS, baixa prioridade).
- ✅ XML XXE/billion-laughs — substituído `xml.etree.ElementTree.fromstring` por `defusedxml.ElementTree.fromstring` em 4 arquivos (`jrxml_visual_parser.py`, `validator.py`, `editor/jrxml_handler.py`, `jrxml_generator.py`). Testes de regressão em `test_jrxml_visual_parser.py` (billion laughs + external entity SYSTEM file://).
- ✅ **Rate-limit bypass via X-Forwarded-For** — `_client_ip` em `ratelimit.py` e `audit.py` confiava cegamente no header forjável. Fix: só usa XFF quando `settings.TRUST_X_FORWARDED_FOR=True` (atrás de proxy confiável) e pega o **rightmost** (adicionado pelo proxy), não leftmost (forjado). Default False. 11 testes em `test_client_ip.py` cobrindo proxy on/off + tentativa de forge.
- ✅ **Upload validation gaps fechados** — `rtm_adjuster` (single + batch + image), `report_editor` (JRXML) e `support/_process_attachments` agora usam `validate_upload(kind=...)` com magic bytes. Antes só checava size + extensão (fácil burlar). Texto plano em support tem allowlist explícito (`.log`, `.txt`, `.csv`, `.json`, `.xml`, `.md`, `.html`, `.ini`, `.yaml`, `.yml`).
- ✅ **Merge tags do RB em RichText** — `<%FieldName%>` (RAP/Maker oficial), `<<FieldName>>` (MS Word/mail merge clássico) e `«FieldName»` (chevrons franceses, import .docx) agora detectados em `TppMakerRichText` e convertidos para `<textField>` com expression `"prefix " + $F{FIELD} + " suffix"`. Antes virava `staticText` com texto literal. Suportado via sentinels antes do parse RTF (`rtf_to_html._embed_merge_sentinels`) + `split_html_with_merge_fields` no gerador.
- ✅ **Bug `verticalAlignment="Middle"` em RichText/Memo** — RichText com height grande e texto curto centralizava verticalmente, sobrepondo elementos abaixo (visível no preview do JasperSoft Studio do WEB Declaração de Bens). Fix: classes `Tpp*RichText`/`Tpp*Memo` agora usam `verticalAlignment="Top"` (cresce do topo). Labels comuns continuam Middle.
- ✅ **Default markup TppDBRichText/TppRichText invertido** — antes `rtf` por default, agora `html`. Só usa `rtf` se `SaveFormat=sfRTF` for declarado explicitamente. Razão: viewers modernos do JasperReports renderizam HTML melhor; campos do BD geralmente já entregam HTML.
- ✅ **§4.9 fechado: `mode="Transparent"` explícito em reportElement** — antes só emitia `mode=` quando opaco; default Transparent ficava implícito. Agora sempre emite explicitamente em text + rectangle, igualando JRXML de produção. Cosmético mas facilita diff. Parser §4 agora 9/9 ✅.
- ✅ **Preview do conversor robustecido (2026-05-05)** — `jrxml_visual_parser._extract_elements` agora recursa em `<frame>` (containers que aninham filhos) e emite o frame como retângulo no preview. `_parse_regex` fallback (acionado quando ElementTree falha em XML mal-formado) passou de "só extrai bandas vazias" pra extrair `<staticText>`/`<textField>`/`<image>`/`<rectangle>`/`<line>`/`<subreport>` com coords + texto/expression (CDATA suportado). `converter._generate_preview_json` agora detecta preview com 0 elementos em todas as bandas e adiciona warning explícito no log. View `preview_page` usa `messages.warning` em vez de redirect mudo quando não há preview.
- ✅ **Bug crítico CDATA → IA fallback indevido (2026-05-05)** — `jrxml_generator._fix_xsd_errors` re-serializava via `lxml.etree.tostring` que **destrói CDATA** (converte em texto literal escapado). RTMs com subDataset (multi-pipeline, ex: extrato da dívida) acionavam essa rota. Resultado: textFieldExpression sem CDATA → acentos legítimos em strings (ex: "DÍVIDA ATIVA") vazavam como caracteres acentuados fora de CDATA → validação `_check_accents` falhava → pipeline escalava pra IA por engano (60-120s + tokens). **Fix duplo:** (1) `_fix_xsd_errors` re-aplica `_process_cdata` no output do lxml; (2) `validator._check_xml_valid` parou de remover CDATA pré-validação (CDATA preserva `<` literais válidos em expressões Java tipo `len < 14`). Resultado: extrato da dívida agora converte em **0.13s no modo rule** vs 60-120s antes (~500-1000x speedup + 0 tokens IA).
- ✅ **Built-ins Pascal de string traduzidos pra Java (2026-05-06, round 39)** — JasperReports compila expressões em Java. Funções Pascal como `UpperCase(s)` geram `"The method UpperCase(String) is undefined for the type region1_..."` ao tentar gerar o relatório no JasperSoft Studio. **Fix em `pascal_to_jasper._pascal_to_java_expr`:** novo bloco `_STRING_BUILTINS` traduz `UpperCase`/`AnsiUpperCase` → `String.valueOf(x).toUpperCase()`, `LowerCase`/`AnsiLowerCase` → `.toLowerCase()`, `Trim` → `.trim()`, `Length(s)` → `String.valueOf(s).length()`, `Copy(s,start,n)` → `substring((start)-1, (start)-1+(n))` (Pascal 1-indexed → Java 0-indexed), `Pos(sub,s)` → `(indexOf(sub) + 1)` (preserva semântica 1-indexed/0=not-found). Wrapper `String.valueOf(x)` é defensivo: funciona pra null/Object/primitivo. Aplicado **antes** da conversão `'texto'` → `"texto"` pra preservar arg detection. 6 testes de regressão (`test_pascal_to_java_translates_*`). 952 testes verdes. Validação empírica do extrato: 0 ocorrências de built-ins Pascal vazando em qualquer dos 5 JRXMLs.
- ✅ **Defesa em profundidade contra XSD order errors (2026-05-06, round 38)** — JasperSoft Studio rejeita JRXML com `cvc-complex-type.2.4.a: Invalid content was found starting with element 'subDataset'` quando a ordem dos children de `<jasperReport>` está errada (ex: subDataset depois de parameter/field). O `_fix_xsd_errors` cobria a rota XML do `JRXMLGenerator`, mas não rotas alternativas (IA direta, jpype, edits ao vivo). **Fix:** novo `_enforce_xsd_order(root)` chamado em **toda** serialização (`_to_xml_string`) — reordena children pra ordem oficial do XSD (`property, import, template, style, subDataset, parameter, queryString, field, sortField, variable, filterExpression, group, background, title, pageHeader, columnHeader, detail, columnFooter, pageFooter, lastPageFooter, summary, noData`). Idempotente + sort estável. Resultado: XML sempre sai válido, independente de qual path gerou. 3 testes de regressão (`test_enforce_xsd_order_*`).
- ✅ **A/B com gold standard da equipe humana (2026-05-06)** — mapeamento dos 16 JRXMLs em `mapeamento/jrxml/` (ex-`Mapa RTM/EXTRATO/`, round 36). 7 fixes + validação empírica: (1) `validator._check_accents` ignora acentos em metadados `<field name>`/`<property value>` (causa adicional de IA fallback indevido em RTMs com nomes acentuados como `END_MUNICÍPIO`); (2) `_create_root` emite `whenResourceMissingType="Empty"` quando há subreports — defesa contra `.jasper` não compilado; (3) `jasper_zebra_style` default `ZebraStyle` → `Cinza_Alternado` (alinhado ao gold); (4) `_render_text_field` emite `isStretchWithOverflow="true"` também quando `auto_size=True` (antes só `stretch` ou DBMemo); (5) `_generate_subreport` força `pageHeight≥2000` em subreports puros (container alongável); (6) **page-numbering "N de M"**: parser preserva `system_var_type` distinguindo `vtPageNo` de `vtPageCount`; generator emite `evaluationTime="Report"` no segundo; (7) **inferência de tipo em subDataset por nome** (descoberto na validação empírica): antes todos fields viravam `java.lang.String`; agora `*_COD`/`*_NUMERO`/`EXE_ANO` → Integer, `*_DATA`/`DATA_*`/`DT_*` → Timestamp, `_VALOR`/`VL_*`/`*_TOTAL`/`*_PORC` → BigDecimal. Validação empírica do extrato da dívida: **0.13s rule-only, 35/35 validações OK, 5 JRXMLs** (1 master + 4 ppsubreports do TppSubReport). Documentado em `Cerebro Migrações/RTM ReportBuilder - Mapeamento Técnico.md` §17. Testes 936 verdes.

## Referência RTM
Antes de qualquer comportamento RTM, consultar:
`Claude Brain/Cerebro Migrações/RTM ReportBuilder - Mapeamento Técnico.md`

## Operação de produção (Sprint 6)

### Rotação de SECRET_KEY
Gere nova chave:
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```
Substituir `DJANGO_SECRET_KEY` no `.env` da prod e reiniciar gunicorn. **Impacto**: invalida sessões ativas (forca re-login). Bom como rotação periódica (semestral) ou após incidente.

Validar que não está no histórico do git:
```bash
git log -p --all | grep -i "SECRET_KEY"
```
Se aparecer (chave hardcoded em commit antigo), considerar a chave comprometida e rotacionar.

### Brute-force protection (LoginView)
- `@rate_limit` por IP: 10/60s — pega flood de IP único
- Lockout per-username em [core/security/lockout.py](MPUB-Intelligence/django_app/core/security/lockout.py): 5 falhas em 5min → bloqueio de 15min do username (mesmo de IPs diferentes — pega botnet rotativa)
- Reset automático no primeiro `login.ok` daquele username
- Audit log registra `login.fail` com `detail.lockout` e `detail.reason='locked'` (curto-circuito)

### Defesa em profundidade contra leak de senha SQL Server
- [core/db_connection.py:connect()](MPUB-Intelligence/django_app/core/db_connection.py) sanitiza `PWD=...;` de qualquer exception/log antes de propagar
- Helper `_sanitize(text)` exportado via regex `\bPWD=[^;]*;?`

### Tarefas operacionais do Pedro (não automatizadas)
- **Rotacionar API key Anthropic**: console Anthropic → revogar key antiga, gerar nova, atualizar `.env` em prod. A key antiga ficou no `.env.example` históricamente; revogar mesmo que aparente seguro.
- **Trocar senhas default**: `admin/admin` (ou variantes) ainda ativos. Login no Django admin → alterar senha. Revisar AuditLog `login.ok` em prod buscando usernames não-rotacionados.
- **Sessão configurável**: `SESSION_COOKIE_AGE = 3600` (1h) com `SESSION_SAVE_EVERY_REQUEST = True` → idle timeout 1h. Se aparecer demanda de timeout absoluto (ex: forçar relogin a cada 8h independente de atividade), implementar via custom middleware.

## Qualidade contínua (Sprint 5)

- **Coverage gate** ativo no CI: `--cov-fail-under=75` em `.github/workflows/test.yml`.
  Baseline atual 76.01% (928 testes) com omits em `.coveragerc` (`jpype_generator.py`, `*/management/commands/*`).
  Histórico: 50 (Sprint 5) → 55 (A) → 60 (B) → 65 (C) → 68 (D) → 70 (E) → 71 (F) → 73 (G) → 74 (H) → 75 (I). Subir gradualmente conforme suite cresce — não baixar nunca.
- **Pre-commit hooks**: `.pre-commit-config.yaml` na raiz.
  Instalar com:
  ```
  pip install pre-commit
  pre-commit install
  ```
  Rodar manual em tudo: `pre-commit run --all-files`. Bypass de emergência: `git commit --no-verify` (não usar pra fugir de erro real).
- **Hooks ativos**: ruff lint + format, trailing whitespace / EOF / YAML / merge conflict / arquivo grande (>2MB). Pytest fica no CI (suite full + coverage gate) — não no pre-commit, pra não bloquear commits com 2min de execução.
