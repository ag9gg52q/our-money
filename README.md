# Our Money

## Cerințe

- Python 3.13+
- PostgreSQL 18

## Rulare locală

**1. Instalează dependențele**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**2. Creează baza de date** (în pgAdmin → Query Tool, ca user `postgres`)

```sql
CREATE ROLE ourmoney WITH LOGIN PASSWORD 'parola-ta' CREATEDB;
CREATE DATABASE ourmoney OWNER ourmoney;
```

**3. Creează `.env`**

```powershell
Copy-Item .env.example .env
```

În `.env` completează `SECRET_KEY` (generată cu comanda de mai jos, pusă între ghilimele simple) și parola din `DATABASE_URL`.

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**4. Pornește aplicația**

```powershell
python ourmoney\manage.py migrate
python ourmoney\manage.py runserver
```

Deschide http://127.0.0.1:8000/api/v1/health/ — trebuie să vezi `{"status": "ok"}`.

## Teste

```powershell
pytest
```
