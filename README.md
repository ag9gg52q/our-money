# Our Money

Aplicație web de finanțe personale care înlocuiește fișierul Excel de evidență a banilor:
cheltuieli, venituri, economii și rapoarte. Backend-ul este un API Django REST, iar frontend-ul
va fi o aplicație React + TypeScript.

> Stadiul curent: fundația backend (setări din `.env`, PostgreSQL, Django REST Framework,
> endpoint de health, teste). Planul complet este în [`.ai-factory/ROADMAP.md`](.ai-factory/ROADMAP.md).

## Tech stack

| | |
|---|---|
| Backend | Python 3.13, Django 6.1, Django REST Framework |
| Bază de date | PostgreSQL 18 |
| Teste | pytest + pytest-django |
| Frontend | React + TypeScript (planificat) |

## Cerințe

- [Python 3.13+](https://www.python.org/downloads/)
- [PostgreSQL 18](https://www.postgresql.org/download/) (pe Windows instalatorul include și pgAdmin)
- Git

## Pornire locală

Comenzile de mai jos sunt pentru PowerShell (Windows). Pe macOS/Linux diferă doar activarea
mediului virtual (vezi pasul 2).

### 1. Clonează repo-ul

```powershell
git clone https://github.com/ag9gg52q/our-money.git
cd our-money
```

### 2. Creează mediul virtual și instalează dependențele

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Dacă PowerShell refuză activarea (*execution policy*), rulează o dată
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

### 3. Creează baza de date

În pgAdmin (Query Tool pe baza `postgres`) sau în `psql`, ca user `postgres`:

```sql
CREATE ROLE ourmoney WITH LOGIN PASSWORD 'parola-ta' CREATEDB;
CREATE DATABASE ourmoney OWNER ourmoney;
```

`CREATEDB` este necesar pentru teste: pytest creează și șterge automat baza `test_ourmoney`.
Folosește în parolă doar litere și cifre (apare într-un URL).

### 4. Configurează `.env`

```powershell
Copy-Item .env.example .env
```

Completează în `.env`:

| Variabilă | Valoare |
|---|---|
| `SECRET_KEY` | o cheie nouă, între ghilimele simple — generează cu comanda de mai jos |
| `DEBUG` | `True` local |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` |
| `DATABASE_URL` | `postgres://ourmoney:parola-ta@localhost:5432/ourmoney` |

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

`.env` conține secrete și este ignorat de git — nu-l adăuga niciodată într-un commit.

### 5. Aplică migrațiile și pornește serverul

```powershell
python ourmoney\manage.py migrate
python ourmoney\manage.py createsuperuser     # opțional, pentru /admin/
python ourmoney\manage.py runserver
```

Verifică:

- http://127.0.0.1:8000/api/v1/health/ → `{"status": "ok"}`
- http://127.0.0.1:8000/admin/ → login cu superuser-ul creat

## Teste

Din rădăcina repo-ului, cu mediul virtual activ:

```powershell
pytest
```

Testele stau în `ourmoney/<app>/tests/test_*.py`; configurarea în `pytest.ini`.

## Structura proiectului

```
our-money/
├── ourmoney/              # Proiectul Django (conține manage.py)
│   ├── ourmoney/          # Setări și rutare
│   └── core/              # App comun: endpoint-ul de health
├── .ai-factory/           # Descriere, arhitectură, roadmap, reguli de cod
├── .claude/               # Skill-uri și agenți pentru Claude Code
├── requirements.txt
├── pytest.ini
└── .env.example
```

Detalii: [`AGENTS.md`](AGENTS.md) (harta proiectului) și
[`.ai-factory/ARCHITECTURE.md`](.ai-factory/ARCHITECTURE.md) (arhitectură și reguli de dependență).

## Cum lucrăm

- **Branch-uri:** nu se lucrează direct pe `main`. Fiecare funcționalitate pe un branch
  `feature/<nume>`, integrat prin Pull Request.
- **Commit-uri:** [Conventional Commits](https://www.conventionalcommits.org/) —
  `feat:` funcționalitate nouă, `fix:` corectură, `test:` teste, `chore:` configurare/întreținere,
  `docs:` documentație.
- **Convenții de cod:** [`.ai-factory/rules/base.md`](.ai-factory/rules/base.md). Sumele de bani
  se reprezintă doar cu `Decimal`, niciodată `float`.
- **Documentația ține pasul cu codul:** orice schimbare de structură, dependență sau configurare
  actualizează în același PR `README.md`, `AGENTS.md` și `.ai-factory/ARCHITECTURE.md`.
- **Dependențe noi:** se adaugă manual în `requirements.txt`, cu versiune fixă (`pachet==x.y.z`),
  doar pachetele folosite direct.