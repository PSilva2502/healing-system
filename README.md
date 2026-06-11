# HEALING — Sistema de Gestão Clínica

Sistema web para gestão de clínicas médicas desenvolvido como Trabalho de Conclusão de Curso (TCC). Permite o gerenciamento completo de pacientes, médicos, consultas e atendimentos, com interface moderna e recursos clínicos avançados.

---

## Funcionalidades

- **Autenticação por perfil** — Administrador, Médico e Recepcionista com painéis distintos
- **Gestão de pacientes** — Cadastro, histórico e prontuário
- **Gestão de médicos** — Cadastro por especialidade
- **Agendamento de consultas** — Controle de horários e conflitos automático
- **Registro de atendimento** — Anamnese, diagnóstico, prescrição e resultado de exames
- **Mapa corporal interativo** — Silhueta estilo raio-x para marcação de regiões de dor
- **Relatórios e auditoria** — Log de todas as operações realizadas no sistema
- **Design Aurora Glass** — Interface navy + coral com animação ECG e efeitos anti-gravidade

---

## Tecnologias

| Camada | Tecnologia |
|--------|------------|
| Backend | Python 3.12+ / Django 6 |
| Banco de dados | SQLite (desenvolvimento) |
| Frontend | HTML5, CSS3, JavaScript (vanilla) |
| Autenticação | Django Auth (modelo customizado) |
| Fontes | Sora, Space Mono, Inter (Google Fonts) |

---

## Pré-requisitos

- [Python 3.12+](https://www.python.org/downloads/)
- Git

---

## Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/PSilva2502/healing-system.git
cd healing-system
```

### 2. Crie e ative o ambiente virtual

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

> Se der erro de permissão no Windows, execute primeiro:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Aplique as migrações do banco de dados

```bash
cd healing
python manage.py migrate
```

### 5. Crie um superusuário (opcional)

```bash
python manage.py createsuperuser
```

### 6. Popule o banco com dados de exemplo (opcional)

```bash
python popular_dados.py
```

### 7. Inicie o servidor

```bash
python manage.py runserver
```

Acesse **http://127.0.0.1:8000** no navegador.

---

## Estrutura do Projeto

```
healing-system/
├── requirements.txt
└── healing/
    ├── manage.py
    ├── config/              # Configurações Django (settings, urls, wsgi)
    ├── static/
    │   └── css/
    │       └── aurora.css   # Design system principal
    ├── core/                # App base: usuários, autenticação, painéis, auditoria
    ├── pacientes/           # Cadastro e gestão de pacientes
    ├── medicos/             # Cadastro e gestão de médicos
    ├── consultas/           # Agendamento e registro de atendimentos
    └── relatorios/          # Relatórios e log de auditoria
```

---

## Perfis de Acesso

| Perfil | Acesso |
|--------|--------|
| Administrador | Painel completo, gestão de usuários, relatórios |
| Médico | Consultas do dia, registro de atendimento, mapa corporal |
| Recepcionista | Agendamento de consultas, cadastro de pacientes |

---

## Licença

Projeto acadêmico — TCC. Todos os direitos reservados ao autor.
