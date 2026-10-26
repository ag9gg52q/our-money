# Our Money

## Cerințe

- Python 3.13+
- PostgreSQL 18
- Node.js 24+

## Rulare locală

### Backend

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

**4. Pornește backend-ul**

```powershell
python ourmoney\manage.py migrate
python ourmoney\manage.py runserver
```

Deschide http://127.0.0.1:8000/api/v1/health/ — trebuie să vezi `{"status": "ok"}`.

### Frontend

Într-un al doilea terminal, cu backend-ul pornit:

```powershell
cd frontend
npm install
npm run dev
```

Deschide http://localhost:5173 — apare pagina de autentificare.

- **Cont nou:** „Creează unul” → după înregistrare te autentifici; contul nou nu are rol, deci ajungi pe pagina de început.
- **Cont cu acces la aplicație:** rulează `python ourmoney\manage.py createsuperuser` (primește rolul de administrator) și autentifică-te cu el.

## Teste și verificări

Din rădăcina repo-ului, cu `.venv` activ:

```powershell
pytest
ruff check ourmoney
ruff format --check ourmoney
```

```powershell
cd frontend
npm run lint
npm run format:check
```
