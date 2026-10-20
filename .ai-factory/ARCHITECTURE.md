# Arhitectură: Structured Modules (Technical Layer)

> Acest document descrie **starea curentă** a proiectului. Se actualizează în același commit cu orice
> schimbare de structură (aplicație nouă, modul nou, dependență nouă, mutare de fișiere).
> Ultima actualizare: 2026-10-20 — model de utilizator propriu (`users.User`, UUID, rol), API de autentificare cu sesiune, Ruff.

## Prezentare generală

Proiectul are două aplicații independente care comunică doar prin API REST:

- **Backend** (`ourmoney/`): proiect Django 6.1 care expune un API REST prin Django REST Framework,
  cu PostgreSQL ca bază de date. Configurarea vine din variabile de mediu (`.env`). App-uri proprii:
  `core` (endpoint-ul public `GET /api/v1/health/`) și `users` (modelul de utilizator propriu și
  API-ul de autentificare cu sesiune: signup, login, logout, me). Nu există încă aplicații de domeniu.
- **Frontend** (`frontend/`): aplicație React + TypeScript construită cu Vite, cu un layout comun,
  routing și trei pagini (Acasă, Status, 404). Pagina Status afișează starea API-ului.

Pentru backend, pattern-ul ales este **Structured Modules (Technical Layer)**: fiecare zonă de
domeniu este o aplicație Django separată, iar în interiorul ei codul se împarte pe straturi tehnice
(`views` → `services`/`selectors` → `models`). Regulile de mai jos se aplică fiecărei aplicații
în momentul în care este adăugată.

## Motivarea deciziei

- **Tipul proiectului:** aplicație de finanțe personale (vezi `.ai-factory/DESCRIPTION.md`)
- **Tech stack curent (backend):** Python 3.13, Django 6.1, Django REST Framework 3.18, PostgreSQL 18, pytest, Ruff
- **Tech stack curent (frontend):** React 19.3, TypeScript 6.0, Vite 8.3, React Router 8.4, ESLint 10, Prettier 3.9
- **Factor cheie:** echipă mică și domeniu de complexitate medie → module clare, fără formalismul DDD complet

## Structura folderelor (curentă)

```
our-money/
├── ourmoney/                      # Rădăcina proiectului Django
│   ├── manage.py                  # CLI Django
│   ├── ourmoney/                  # Pachetul de configurare (composition root)
│   │   ├── __init__.py
│   │   ├── settings.py            # Setări citite din .env (django-environ), DRF, PostgreSQL
│   │   ├── urls.py                # admin/, api/v1/ → core.urls, api/v1/auth/ → users.urls
│   │   ├── asgi.py
│   │   └── wsgi.py
│   ├── core/                      # App comun (cross-cutting)
│   │   ├── views.py               # health — GET, public (AllowAny)
│   │   ├── urls.py                # health/ (name='health')
│   │   ├── apps.py                # CoreConfig
│   │   └── tests/
│   │       └── test_health.py     # GET → 200 {"status": "ok"}, POST → 405
│   └── users/                     # Utilizatori și autentificare
│       ├── models.py              # User (AbstractUser): id UUID, role admin/user (implicit user), is_admin
│       ├── admin.py               # User în /admin/, cu secțiunea și filtrul „Rol”
│       ├── serializers.py         # UserSerializer (ieșire), SignupSerializer, LoginSerializer
│       ├── services.py            # register_user()
│       ├── views.py               # CsrfView, SignupView, LoginView, LogoutView, MeView
│       ├── urls.py                # csrf/, signup/, login/, logout/, me/
│       └── migrations/            # 0001_initial — tabelul users_user
├── frontend/                      # Aplicația React + TypeScript (Vite)
│   ├── index.html                 # Pagina HTML unică (<div id="root">)
│   ├── vite.config.ts             # Plugin React + proxy /api → http://127.0.0.1:8000
│   ├── package.json               # Dependențe + scripturi: dev, build, lint, format, format:check
│   ├── eslint.config.js           # ESLint (recommended, TypeScript, react-hooks) + eslint-config-prettier
│   ├── .prettierrc.json           # Stil: ghilimele simple, fără punct și virgulă
│   ├── tsconfig*.json             # Configurare TypeScript
│   ├── public/favicon.svg
│   └── src/
│       ├── main.tsx               # Punctul de intrare: montează <App /> în StrictMode
│       ├── App.tsx                # Rutele (BrowserRouter): / → HomePage, /status → StatusPage, * → NotFoundPage
│       ├── index.css              # Stiluri globale
│       ├── components/
│       │   └── Layout.tsx         # Antet + meniu (NavLink) + <Outlet /> pentru pagina curentă
│       ├── pages/
│       │   ├── HomePage.tsx
│       │   ├── StatusPage.tsx     # Apelează fetchHealth(); stări loading / ok / error
│       │   └── NotFoundPage.tsx
│       └── api/
│           └── health.ts          # fetchHealth() + tipul HealthResponse
├── .ai-factory/                   # Context AI Factory (descriere, arhitectură, reguli, roadmap)
├── .claude/                       # Skill-uri și agenți Claude Code
├── .env.example                   # Variabilele de mediu necesare (fără valori reale)
├── requirements.txt               # Dependențe directe, versiuni fixate
├── pytest.ini                     # Configurare pytest-django
├── pyproject.toml                 # Configurare Ruff (lint + formatare backend)
├── .gitattributes                 # Toate fișierele text cu terminații LF (cerut de Prettier)
├── .mcp.json                      # Servere MCP: github, playwright, postgres
├── AGENTS.md
├── CLAUDE.md
└── README.md
```

## Aplicații / module curente

| Modul | Scop | Stare |
|-------|------|-------|
| `ourmoney` (pachet de configurare) | Setări, rutare, entry points ASGI/WSGI | Setări din `.env`, DRF configurat |
| `core` | Funcționalități comune întregului proiect | Doar endpoint-ul de health; fără modele (deci fără `models.py`, `admin.py`, `migrations/`) |
| `users` | Modelul de utilizator și autentificarea | `User` cu `id` UUID și `role` (`admin` / `user`, implicit `user`); API de sesiune |

Nu există încă aplicații de domeniu.

## API curent

| Metodă | URL | Permisiune | Răspuns |
|--------|-----|------------|---------|
| GET | `/api/v1/health/` | public (`AllowAny`) | `200 {"status": "ok"}` |
| GET | `/api/v1/auth/csrf/` | public | `204`, setează cookie-ul `csrftoken` |
| POST | `/api/v1/auth/signup/` | public, cu CSRF | `201` user creat (rol `user`); `400` erori de validare. Nu pornește sesiunea |
| POST | `/api/v1/auth/login/` | public, cu CSRF | `200` user + cookie `sessionid`; `400` date greșite |
| POST | `/api/v1/auth/logout/` | autentificat, cu CSRF | `204` |
| GET | `/api/v1/auth/me/` | autentificat | `200` userul curent; `403` fără sesiune |

Userul este întors ca `{id, username, email, first_name, last_name, role}`.

Toate rutele API sunt sub prefixul `/api/v1/`, inclus din `ourmoney/urls.py`.

## Configurare curentă

- **Variabile de mediu** (`.env` în rădăcina repo-ului, citit cu `django-environ`; model în `.env.example`):
  `SECRET_KEY` (obligatoriu), `DEBUG` (implicit `False`), `ALLOWED_HOSTS` (listă separată prin virgulă),
  `DATABASE_URL` (obligatoriu)
- **Baza de date:** PostgreSQL, configurată prin `DATABASES = {'default': env.db('DATABASE_URL')}`
- **Utilizator:** `AUTH_USER_MODEL = 'users.User'`; `createsuperuser` setează rolul `admin`.
  `is_staff` / `is_superuser` controlează doar panoul tehnic `/admin/`; rolul din aplicație este `role`
- **Autentificare:** doar sesiune Django (`SessionAuthentication`): cookie `sessionid` + protecție
  CSRF (cookie `csrftoken`, header `X-CSRFToken`). Signup și login au `csrf_protect` explicit
- **DRF:** permisiunea implicită este `IsAuthenticated` — orice endpoint nou cere autentificare,
  cu excepția celor marcate explicit `AllowAny`
- **Calitate cod backend:** Ruff (`pyproject.toml`): reguli E, F, W, I, B, UP, DJ; ghilimele simple;
  rânduri de maximum 100 de caractere; migrațiile sunt excluse
- **Teste:** pytest + pytest-django, rulate din rădăcina repo-ului; `pytest.ini` setează
  `DJANGO_SETTINGS_MODULE = ourmoney.settings` și `pythonpath = ourmoney`
- **Dependențe** (`requirements.txt`): Django, djangorestframework, psycopg[binary], django-environ,
  pytest, pytest-django, ruff
- Încă neconfigurate: CORS, logging, permisiuni pe roluri

## Frontend

### Comunicarea cu backend-ul

- În dezvoltare rulează două servere: Django pe `127.0.0.1:8000` și Vite pe `localhost:5173`.
- Frontend-ul face cereri la adrese relative (`/api/v1/...`); proxy-ul Vite (`vite.config.ts`) le
  trimite la Django. Browserul vorbește doar cu `:5173`, deci CORS nu este necesar.
- Flux: componentă din `pages/` → funcție din `api/` (`fetch`) → proxy Vite → `ourmoney/urls.py` →
  `<app>/urls.py` → view → răspuns JSON → înapoi în componentă, care își actualizează state-ul.

### Organizarea codului (`frontend/src/`)

| Folder | Conține | Regulă |
|--------|---------|--------|
| `pages/` | O componentă per rută | Afișează date și state; nu apelează `fetch` direct |
| `components/` | Componente reutilizabile (acum: `Layout`) | Fără apeluri la API |
| `api/` | O funcție per endpoint + tipurile răspunsurilor | Singurul loc unde se folosește `fetch`; verifică `response.ok` |

### Reguli

- ✅ `pages` → `api` → backend; `pages` și `components` pot folosi `components`
- ❌ `fetch` în afara folderului `api/`
- ✅ Adresele API se termină cu `/` (ca rutele Django), altfel Django răspunde cu redirect 301
- ✅ Componentele se numesc în PascalCase, iar numele funcției este identic cu numele fișierului
- ✅ Datele încărcate de la API au cele trei stări tratate explicit: încărcare, succes, eroare
- ✅ Efectele care fac cereri au cleanup (`ignore`), pentru `StrictMode` și pentru navigarea în afara paginii
- ✅ Formatarea este făcută de Prettier (`npm run format`); ESLint doar semnalează probleme de cod

## Reguli de dependență (backend)

Se aplică fiecărei aplicații Django adăugate în `ourmoney/`:

- ✅ `urls → views → services/selectors → models`; `serializers` sunt folosite doar de `views`
- ✅ `views` validează input-ul și apelează un singur service (scriere) sau selector (citire)
- ✅ Regulile de domeniu (invariante, calcule) stau în `models`; `services` doar orchestrează și persistă
- ✅ O aplicație poate apela funcțiile publice din `services`/`selectors` ale altei aplicații
- ❌ `views` nu interoghează direct ORM-ul și nu conțin logică de business
- ❌ `models` nu importă din `services`, `views` sau `serializers`
- ❌ O aplicație nu importă `views`/`serializers` ale alteia
- ❌ Dependențe circulare între aplicații

## Comunicarea între straturi și module

- View → Service/Selector: apel de funcție cu argumente explicite (keyword-only), nu cu `request` întreg
- Service → Model: metode pe model pentru reguli; service-ul le compune și salvează
- Între aplicații: doar prin funcții publice din `services.py` / `selectors.py`
- Sisteme externe: izolate în module adaptor dedicate în aplicația care le folosește

## Principii cheie

1. **Banii sunt `Decimal` + cod de valută (ISO 4217).** Niciodată `float`.
2. **Izolarea datelor per utilizator.** Orice query pe date de utilizator filtrează după utilizatorul autentificat.
3. **Modele bogate, services subțiri.** Invariantele trăiesc în modele.
4. **Scrierile pe mai multe rânduri sunt atomice** (`transaction.atomic()`).
5. **Endpoint-urile sunt private implicit.** Doar endpoint-urile marcate explicit `AllowAny` sunt publice.
6. **Documentul reflectă realitatea.** Orice schimbare de structură actualizează acest fișier, `AGENTS.md`, `README.md` și, dacă e cazul, `.ai-factory/DESCRIPTION.md`.

## Anti-pattern-uri

- ❌ Logică de business în views sau serializers
- ❌ Modele anemice cu toate regulile în services
- ❌ `float` pentru sume de bani
- ❌ Query-uri pe date de utilizator nefiltrate după utilizator
- ❌ Import circular între aplicații
- ❌ `fetch` direct în componente, în loc de o funcție din `frontend/src/api/`
- ❌ Documentarea în acest fișier a unor module care nu există încă în cod
