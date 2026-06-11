# HEALING — Como Rodar o Projeto

## Pré-requisitos
- Python 3.10+
- MySQL 8.0+

## 1. Criar o banco de dados

Abra o MySQL e execute:
```sql
-- Copie o conteúdo de criar_banco.sql
```

Ou via terminal:
```bash
mysql -u root -p < criar_banco.sql
```

## 2. Criar e ativar ambiente virtual

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

## 3. Instalar dependências

```bash
pip install -r requirements.txt
```

## 4. Configurar variáveis de ambiente

Copie `.env.example` para `.env` e preencha:
```
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
BD_SENHA=Healing@2024
BD_NOME=bd_healing
BD_USUARIO=usuario_healing
BD_HOST=localhost
BD_PORTA=3306
```

## 5. Aplicar migrações

```bash
python manage.py makemigrations
python manage.py migrate
```

## 6. Popular dados de exemplo

```bash
python popular_dados.py
```

## 7. Rodar o servidor

```bash
python manage.py runserver
```

Acesse: http://127.0.0.1:8000/entrar/

## Credenciais de Acesso

| Perfil   | E-mail                 | Senha       |
|----------|------------------------|-------------|
| Admin    | admin@healing.com      | admin123    |
| Médico   | ana@healing.com        | medico123   |
| Paciente | joao@email.com         | paciente123 |
