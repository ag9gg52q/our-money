# AGENTS.md

> Hartă structurală a proiectului pentru agenți AI și dezvoltatori noi. Actualizează acest fișier când structura proiectului se schimbă semnificativ.

## Prezentare generală

Aplicație web de finanțe personale care înlocuiește un fișier Excel: cheltuieli, venituri, economii, rapoarte. Detalii în [`.ai-factory/DESCRIPTION.md`](.ai-factory/DESCRIPTION.md).

## Tech Stack

- **Backend:** Python 3.13, Django 6.1 + Django REST Framework, Django ORM
- **Frontend:** React 19 + TypeScript 6, Vite 8, React Router 8
- **Bază de date:** PostgreSQL 18
- **Teste:** pytest + pytest-django (backend)
- **Calitate cod frontend:** ESLint (probleme de cod) + Prettier (formatare)
- **Calitate cod backend:** Ruff (lint + formatare)
- **Autentificare:** sesiune Django (cookie `sessionid` + CSRF), model de utilizator propriu `users.User`

## Structura proiectului

```
our-money/
├── ourmoney/                 # Proiectul Django (conține manage.py)
│   ├── manage.py             # CLI Django: runserver, migrate, makemigrations, startapp
│   ├── conftest.py           # Fixture-uri pytest comune (api_client, csrf_client, user)
│   ├── ourmoney/             # Pachetul de configurare al proiectului
│   │   ├── settings.py       # Setări din .env (django-environ), DRF, PostgreSQL
│   │   ├── urls.py           # admin/, api/v1/ → core.urls, api/v1/auth/ → users.urls,
│   │   │                     #   api/v1/households/ → households.urls, api/v1/categories/ → categories.urls
│   │   ├── asgi.py           # Entry point ASGI
│   │   └── wsgi.py           # Entry point WSGI
│   ├── core/                 # App comun: endpoint-ul de health
│   │   ├── views.py          # health (GET, public)
│   │   ├── urls.py           # health/
│   │   └── tests/            # teste pytest
│   ├── categories/           # Categoriile de cheltuieli ale gospodăriei
│   │   ├── models.py         # Category: nume unic per gospodărie, activă / dezactivată
│   │   ├── selectors.py      # household_categories() — citirea filtrată pe gospodărie
│   │   ├── services.py       # create_category(), update_category()
│   │   ├── serializers.py    # validarea numelui (inclusiv duplicat)
│   │   ├── views.py          # listă + adăugare (GET, POST), editare (PATCH)
│   │   ├── urls.py           # rutele /api/v1/categories/
│   │   └── tests/            # teste pytest: model, API
│   ├── households/           # Gospodării
│   │   ├── models.py         # Household: id UUID, nume, cod de invitație unic
│   │   ├── serializers.py    # validarea creării (nume) și a alăturării (cod de invitație)
│   │   ├── services.py       # create_household() — admin; join_household() — user
│   │   ├── views.py          # creare gospodărie și alăturare cu cod (POST)
│   │   ├── urls.py           # rutele /api/v1/households/
│   │   ├── permissions.py    # IsHouseholdMember, IsHouseholdAdminOrReadOnly
│   │   ├── signals.py        # la ștergerea gospodăriei, membrii își pierd rolul
│   │   └── tests/            # teste pytest: model, API
│   └── users/                # Utilizatori și autentificare
│       ├── models.py         # User: id UUID, role admin/user sau gol (cont nou), household (opțional)
│       ├── serializers.py    # validare signup/login, formatul userului
│       ├── services.py       # register_user()
│       ├── validators.py     # validator de parolă cu mesaje în română
│       ├── views.py          # csrf, signup, login, logout, me
│       ├── urls.py           # rutele /api/v1/auth/
│       └── tests/            # teste pytest: API de autentificare, model, validator
├── frontend/                 # Aplicația React + TypeScript (Vite)
│   ├── vite.config.ts        # Proxy /api → Django (127.0.0.1:8000)
│   ├── package.json          # Dependențe + scripturi (dev, build, lint, format)
│   └── src/
│       ├── main.tsx          # Punctul de intrare
│       ├── App.tsx           # Rutele: /login, /signup (nelogați); /start (logați fără rol); restul (cu rol), în Layout; /settings doar admin, cu sub-rute (nomenclatoare, template-uri, rapoarte)
│       ├── index.css         # Variabilele de design (culori, font) + stiluri globale
│       ├── auth/             # Contextul de autentificare (user, login, logout, refreshUser) + paznicii (RequireAuth, RequireRole, RequireNoRole, RedirectIfAuthenticated)
│       ├── components/       # Componente reutilizabile (Layout, AuthLayout, PageLoader, Button, TextField, Modal)
│       ├── categories/       # Modalul de adăugare / editare a unei categorii
│       ├── households/       # Modalurile de creare și alăturare la o gospodărie
│       ├── pages/            # O componentă per pagină (Home, Start, Settings, Login, Signup, Status, NotFound);
│       │                     #   settings/ — sub-paginile Setărilor sistem (Categorii funcțională)
│       └── api/              # client.ts (apiFetch + CSRF) și funcțiile per endpoint
├── .ai-factory/              # Context AI Factory (descriere, arhitectură, reguli, roadmap)
├── .claude/                  # Skill-uri și agenți Claude Code
├── .env.example              # Variabilele de mediu necesare (copiază în .env)
├── requirements.txt          # Dependențe Python, versiuni fixate
├── pytest.ini                # Configurare pytest-django
├── pyproject.toml            # Configurare Ruff
├── .gitattributes            # Terminații de linie LF pentru toate fișierele text
├── .mcp.json                 # Configurare servere MCP (github, playwright, postgres)
├── skills-lock.json          # Versiunile skill-urilor externe instalate
├── AGENTS.md                 # Acest fișier
├── CLAUDE.md                 # Instrucțiuni Claude Code (include AGENTS.md)
└── README.md                 # Pașii de rulare locală
```

## Puncte de intrare cheie

| Fișier | Scop |
|--------|------|
| `ourmoney/manage.py` | Comenzi de management Django |
| `ourmoney/ourmoney/settings.py` | Configurarea proiectului (DB, aplicații, DRF, securitate) |
| `ourmoney/ourmoney/urls.py` | Rutarea URL de nivel superior; API sub `/api/v1/` |
| `ourmoney/core/views.py` | Endpoint-ul `GET /api/v1/health/` |
| `ourmoney/users/models.py` | Modelul de utilizator (`AUTH_USER_MODEL = 'users.User'`) |
| `ourmoney/households/models.py` | Modelul `Household` și generarea codului de invitație |
| `ourmoney/users/views.py` | API-ul de autentificare `/api/v1/auth/` (csrf, signup, login, logout, me) |
| `ourmoney/households/views.py` | API-ul gospodăriilor `/api/v1/households/` (creare, alăturare) |
| `ourmoney/categories/views.py` | API-ul categoriilor `/api/v1/categories/` (listă, adăugare, editare) |
| `ourmoney/households/permissions.py` | Permisiunile pe gospodărie, folosite de API-urile datelor gospodăriei |
| `pyproject.toml` | Regulile Ruff pentru backend |
| `ourmoney/ourmoney/wsgi.py` / `asgi.py` | Entry points pentru servere de producție |
| `.env.example` | Lista variabilelor de mediu: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DATABASE_URL` |
| `pytest.ini` | Configurarea testelor |
| `frontend/src/main.tsx` | Punctul de intrare al aplicației React |
| `frontend/src/App.tsx` | Rutele frontend-ului |
| `frontend/src/api/client.ts` | `apiFetch()` — toate cererile către backend (JSON, CSRF, erori) |
| `frontend/src/auth/AuthProvider.tsx` | Userul curent, login, logout și refreshUser, disponibile prin `useAuth()` |
| `frontend/vite.config.ts` | Configurare Vite + proxy `/api` |

## Documentație

| Document | Cale | Descriere |
|----------|------|-----------|
| README | README.md | Doar pașii de rulare locală și rularea testelor, descriși simplu |

## Fișiere de context AI

| Fișier | Scop |
|--------|------|
| AGENTS.md | Harta structurală a proiectului (acest fișier) |
| .ai-factory/DESCRIPTION.md | Specificația proiectului și tech stack-ul |
| .ai-factory/ARCHITECTURE.md | Decizii de arhitectură și reguli de dependențe |
| .ai-factory/rules/base.md | Convenții de cod ale proiectului |
| .ai-factory/ROADMAP.md | Milestone-urile proiectului și progresul |
| .ai-factory/config.yaml | Configurarea AI Factory (limbă, căi, git) |
| CLAUDE.md | Instrucțiuni pentru Claude Code; importă AGENTS.md |

## Reguli pentru agenți

- **Documentația de context reflectă starea curentă a codului, nu planurile.** Orice schimbare a
  proiectului (aplicație/modul nou, model, endpoint, dependență, schimbare de configurare, mutare de
  fișiere) actualizează în aceeași sarcină și în același commit:
  - `.ai-factory/ARCHITECTURE.md` — structura folderelor, modulele existente, configurarea curentă
  - `AGENTS.md` — structura proiectului și punctele de intrare
  - `.ai-factory/DESCRIPTION.md` — tech stack-ul și funcționalitățile, dacă s-au schimbat
  - `README.md` — pașii de setup, dacă s-au schimbat dependențele, variabilele de mediu sau comenzile

- Nu combina comenzi shell cu `&&`; rulează-le separat, pas cu pas.
  - Greșit: `git checkout main && git pull`
  - Corect: mai întâi `git checkout main`, apoi `git pull origin main`
- Comenzile Django și `pytest` se rulează din rădăcina repo-ului, cu `.venv` activ:
  `python ourmoney/manage.py <comandă>`. Excepție: `startapp` se rulează din `ourmoney/`,
  ca app-ul nou să fie creat lângă `core/`.
- Înainte de commit pe backend: `ruff format ourmoney`, `ruff check ourmoney`, `pytest` (din rădăcină).
- Modelele referă utilizatorul prin `settings.AUTH_USER_MODEL` (ForeignKey) sau `get_user_model()`, niciodată direct `User` din Django.
- Comenzile frontend (`npm install`, `npm run dev`, `npm run lint`, `npm run format`) se rulează din `frontend/`.
  Înainte de commit pe frontend: `npm run format`, `npm run lint`, `npx tsc -b`.
- În frontend, cererile către backend se fac doar prin `apiFetch` din `frontend/src/api/client.ts`;
  adresele API încep și se termină cu `/`.
- Nu se adaugă configurări pentru panoul tehnic Django (`admin.py`); tot ce e configurabil se face din aplicație.
- Sumele de bani se reprezintă doar cu `Decimal` / `DecimalField`, niciodată `float`.
