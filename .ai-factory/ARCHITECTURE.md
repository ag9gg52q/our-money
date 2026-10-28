# Arhitectură: Structured Modules (Technical Layer)

> Acest document descrie **starea curentă** a proiectului. Se actualizează în același commit cu orice
> schimbare de structură (aplicație nouă, modul nou, dependență nouă, mutare de fișiere).
> Ultima actualizare: 2026-10-27 — crearea gospodăriei din interfață (modal pe `/start`), pagina Setări sistem
> (cod de invitație, doar admin), eliminarea `users/admin.py` și a rolului dat automat la `createsuperuser`.

## Prezentare generală

Proiectul are două aplicații independente care comunică doar prin API REST:

- **Backend** (`ourmoney/`): proiect Django 6.1 care expune un API REST prin Django REST Framework,
  cu PostgreSQL ca bază de date. Configurarea vine din variabile de mediu (`.env`). App-uri proprii:
  `core` (endpoint-ul public `GET /api/v1/health/`) și `users` (modelul de utilizator propriu și
  API-ul de autentificare cu sesiune: signup, login, logout, me) și `households` (modelul
  `Household` și crearea unei gospodării). Nu există încă aplicații de domeniu.
- **Frontend** (`frontend/`): aplicație React + TypeScript construită cu Vite: autentificare
  (Login, Signup), rute protejate și direcționare după rol (`/start` pentru conturile fără rol,
  aplicația cu antet pentru cele cu rol), crearea unei gospodării (modal pe `/start`), plus paginile
  Acasă („Gospodăria noastră”, schiță), Setări sistem (codul de invitație, doar admin), Status și 404.

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
│   ├── conftest.py                # Fixture-uri pytest comune: api_client, csrf_client, user
│   ├── ourmoney/                  # Pachetul de configurare (composition root)
│   │   ├── __init__.py
│   │   ├── settings.py            # Setări citite din .env (django-environ), DRF, PostgreSQL
│   │   ├── urls.py                # admin/, api/v1/ → core.urls, api/v1/auth/ → users.urls,
│   │   │                          #   api/v1/households/ → households.urls
│   │   ├── asgi.py
│   │   └── wsgi.py
│   ├── core/                      # App comun (cross-cutting)
│   │   ├── views.py               # health — GET, public (AllowAny)
│   │   ├── urls.py                # health/ (name='health')
│   │   ├── apps.py                # CoreConfig
│   │   └── tests/
│   │       └── test_health.py     # GET → 200 {"status": "ok"}, POST → 405
│   ├── households/                # Gospodării
│   │   ├── models.py              # Household: id UUID, name, invite_code unic (XXXX-XXXX), created_at;
│   │   │                          #   generate_invite_code() cu `secrets`, fără 0/O/1/I/L
│   │   ├── serializers.py         # HouseholdSerializer: name (intrare), id + invite_code (doar ieșire);
│   │   │                          #   respinge userul care are deja gospodărie
│   │   ├── services.py            # create_household(): creează gospodăria, userul devine admin (atomic)
│   │   ├── views.py               # HouseholdCreateView (POST)
│   │   ├── urls.py                # '' (name='household-create')
│   │   ├── signals.py             # pre_delete: membrii gospodăriei șterse își pierd rolul
│   │   ├── apps.py                # ready() înregistrează signal-urile
│   │   ├── migrations/            # 0001_initial — tabelul households_household
│   │   └── tests/
│   │       ├── test_models.py     # formatul codului, unicitate, legătura cu userii, ștergerea
│   │       └── test_api.py        # creare, validarea numelui, user deja în gospodărie, auth, CSRF, /me/
│   └── users/                     # Utilizatori și autentificare
│       ├── models.py              # User (AbstractUser): id UUID, role admin/user/'' (implicit '' = fără rol),
│       │                          #   household (FK opțional, SET_NULL, related_name='members'), is_admin;
│       │                          #   CustomUserManager fără comportament propriu (referit de migrația 0001)
│       ├── serializers.py         # UserSerializer (ieșire, cu household), SignupSerializer, LoginSerializer
│       ├── services.py            # register_user()
│       ├── validators.py          # MinimumLengthValidator cu mesaje în română
│       ├── views.py               # CsrfView, SignupView, LoginView, LogoutView, MeView
│       ├── urls.py                # csrf/, signup/, login/, logout/, me/
│       ├── migrations/            # 0001_initial (tabelul users_user), 0002_optional_role, 0003_user_household
│       └── tests/
│           ├── test_auth_api.py   # csrf, signup, login, logout, me, CSRF obligatoriu, durata sesiunii
│           ├── test_models.py     # rolul implicit, superuser fără rol, is_admin, id UUID
│           └── test_validators.py # mesajul de parolă în română
├── frontend/                      # Aplicația React + TypeScript (Vite)
│   ├── index.html                 # Pagina HTML unică (<div id="root">)
│   ├── vite.config.ts             # Plugin React + proxy /api → http://127.0.0.1:8000 (changeOrigin: false)
│   ├── package.json               # Dependențe + scripturi: dev, build, lint, format, format:check
│   ├── eslint.config.js           # ESLint (recommended, TypeScript, react-hooks) + eslint-config-prettier
│   ├── .prettierrc.json           # Stil: ghilimele simple, fără punct și virgulă
│   ├── tsconfig*.json             # Configurare TypeScript
│   ├── public/favicon.svg
│   └── src/
│       ├── main.tsx               # Punctul de intrare: fontul Manrope, index.css, <App /> în StrictMode
│       ├── App.tsx                # AuthProvider + rutele: RedirectIfAuthenticated → /login, /signup;
│       │                          #   RequireAuth → RequireNoRole → /start;
│       │                          #   RequireAuth → RequireRole → Layout → /, /status, *;
│       │                          #   în Layout, RequireRole role="admin" → /settings
│       ├── index.css              # Variabilele de design (culori, rază, font) + stiluri globale
│       ├── auth/
│       │   ├── AuthContext.ts     # Contextul: user, isLoading, login(), logout(), refreshUser()
│       │   ├── AuthProvider.tsx   # La pornire: cookie CSRF + /me/; ține userul curent
│       │   ├── useAuth.ts         # Hook-ul prin care componentele citesc contextul
│       │   ├── RequireAuth.tsx    # Paznic: nelogat → /login (ține minte pagina cerută în state.from)
│       │   ├── RedirectIfAuthenticated.tsx  # Paznic: logat → state.from sau /
│       │   ├── RequireRole.tsx    # Paznic: logat fără rol → /start; cu `role`, alt rol → /
│       │   └── RequireNoRole.tsx  # Paznic: logat cu rol → /
│       ├── components/
│       │   ├── Layout/            # Antetul (logo + numele gospodăriei, meniu, Setări sistem pentru admin,
│       │   │                      #   rol, nume, Ieșire) + <Outlet />
│       │   ├── Modal/             # <dialog> nativ: se deschide la afișare; Esc / click pe fundal → onClose
│       │   ├── PageLoader/        # „Se încarcă...” cât timp se verifică sesiunea
│       │   ├── AuthLayout/        # Cadrul paginilor de autentificare (panou de brand + formular)
│       │   ├── Button/            # Buton primary / secondary (CSS Module)
│       │   └── TextField/         # Etichetă + input + mesaj de eroare (CSS Module)
│       ├── households/
│       │   ├── CreateHouseholdModal.tsx # Modalul de creare: nume → createHousehold() → refreshUser()
│       │   └── HouseholdForm.module.css # Stiluri comune formularelor de gospodărie
│       ├── pages/
│       │   ├── HomePage.tsx       # Schiță: „Gospodăria noastră” (doar cu rol)
│       │   ├── StartPage.tsx      # Creează o gospodărie (modal) / alătură-te (inactiv încă); doar fără rol
│       │   ├── SettingsPage.tsx   # Setări sistem: codul de invitație + Copiază (doar admin)
│       │   ├── LoginPage.tsx      # Formular login; mesaj după signup; redirecționarea o face paznicul
│       │   ├── SignupPage.tsx     # Formular signup (utilizator, parolă, confirmare); redirect la /login
│       │   ├── AuthPage.module.css # Stiluri comune formularelor (form, alerte)
│       │   ├── StatusPage.tsx     # Apelează fetchHealth(); stări loading / ok / error
│       │   └── NotFoundPage.tsx
│       └── api/
│           ├── client.ts          # apiFetch() (JSON, CSRF, ApiError), getErrorMessage()
│           ├── auth.ts            # csrf, signup, login, logout, fetchCurrentUser + tipul User
│           ├── households.ts      # createHousehold() + tipul Household
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
| `users` | Modelul de utilizator și autentificarea | `User` cu `id` UUID, `role` (`admin` / `user` / gol; contul nou nu are rol) și `household` (opțional); API de sesiune |
| `households` | Gospodăriile | Modelul `Household` cu cod de invitație unic; API de creare; fără interfață încă |

**Gospodării:** un user face parte din cel mult o gospodărie (`User.household`, `ForeignKey`).
La ștergerea unei gospodării, membrii rămân fără gospodărie (`on_delete=SET_NULL`) și își pierd
rolul (signal-ul `pre_delete` din `households/signals.py`, care rulează la orice ștergere — model,
`queryset.delete()`, panoul tehnic).

Nu există încă aplicații de domeniu.

## API curent

| Metodă | URL | Permisiune | Răspuns |
|--------|-----|------------|---------|
| GET | `/api/v1/health/` | public (`AllowAny`) | `200 {"status": "ok"}` |
| GET | `/api/v1/auth/csrf/` | public | `204`, setează cookie-ul `csrftoken` |
| POST | `/api/v1/auth/signup/` | public, cu CSRF | `201` user creat (fără rol); `400` erori de validare. Nu pornește sesiunea |
| POST | `/api/v1/auth/login/` | public, cu CSRF | `200` user + cookie `sessionid`; `400` date greșite |
| POST | `/api/v1/auth/logout/` | autentificat, cu CSRF | `204` |
| GET | `/api/v1/auth/me/` | autentificat | `200` userul curent; `403` fără sesiune |
| POST | `/api/v1/households/` | autentificat, cu CSRF | `201 {id, name, invite_code}` — userul devine `admin` al gospodăriei; `400` nume invalid sau userul are deja gospodărie |

Userul este întors ca `{id, username, email, first_name, last_name, role, household}`; `role` este
`"admin"`, `"user"` sau `null` (fără rol — în baza de date textul gol). `household` este `null` sau
`{id, name}`, plus `invite_code` doar pentru admin.

Toate rutele API sunt sub prefixul `/api/v1/`, inclus din `ourmoney/urls.py`.

## Configurare curentă

- **Variabile de mediu** (`.env` în rădăcina repo-ului, citit cu `django-environ`; model în `.env.example`):
  `SECRET_KEY` (obligatoriu), `DEBUG` (implicit `False`), `ALLOWED_HOSTS` (listă separată prin virgulă),
  `DATABASE_URL` (obligatoriu)
- **Baza de date:** PostgreSQL, configurată prin `DATABASES = {'default': env.db('DATABASE_URL')}`
- **Utilizator:** `AUTH_USER_MODEL = 'users.User'`. Rolul din aplicație este `role` și se primește
  doar din aplicație (creatorul unei gospodării devine `admin`); `createsuperuser` nu dă rol.
  `is_staff` / `is_superuser` controlează doar panoul tehnic `/admin/`, unde modelele proiectului
  nu sunt înregistrate
- **Autentificare:** doar sesiune Django (`SessionAuthentication`): cookie `sessionid` + protecție
  CSRF (cookie `csrftoken`, header `X-CSRFToken`). Signup și login au `csrf_protect` explicit
- **Durata sesiunii:** expiră după o zi de inactivitate (`SESSION_COOKIE_AGE = 86400`,
  `SESSION_SAVE_EVERY_REQUEST = True` — fiecare cerere reînnoiește termenul)
- **Limbă:** `LANGUAGE_CODE = 'ro'` — mesajele de validare Django/DRF sunt în română; regula de
  lungime minimă a parolei folosește `users.validators.MinimumLengthValidator` (traducere proprie)
- **DRF:** permisiunea implicită este `IsAuthenticated` — orice endpoint nou cere autentificare,
  cu excepția celor marcate explicit `AllowAny`
- **Calitate cod backend:** Ruff (`pyproject.toml`): reguli E, F, W, I, B, UP, DJ; ghilimele simple;
  rânduri de maximum 100 de caractere; migrațiile sunt excluse
- **Teste:** pytest + pytest-django, rulate din rădăcina repo-ului; `pytest.ini` setează
  `DJANGO_SETTINGS_MODULE = ourmoney.settings` și `pythonpath = ourmoney`. Fixture-urile comune sunt
  în `ourmoney/conftest.py`: `api_client` (fără CSRF), `csrf_client` (CSRF activ, ca browserul),
  `user` (cont fără rol, parola `PASSWORD`). 45 de teste (`core`, `users`, `households`)
- **Dependențe** (`requirements.txt`): Django, djangorestframework, psycopg[binary], django-environ,
  pytest, pytest-django, ruff
- Încă neconfigurate: CORS, logging, permisiuni pe roluri

## Frontend

### Comunicarea cu backend-ul

- În dezvoltare rulează două servere: Django pe `127.0.0.1:8000` și Vite pe `localhost:5173`.
- Frontend-ul face cereri la adrese relative (`/api/v1/...`); proxy-ul Vite (`vite.config.ts`) le
  trimite la Django. Browserul vorbește doar cu `:5173`, deci CORS nu este necesar.
- Proxy-ul păstrează header-ul `Host` (`changeOrigin: false`), ca verificarea CSRF a Django
  (`Origin` vs `Host`) să treacă — la fel ca în producție, unde frontend-ul și API-ul sunt pe același domeniu.
- Toate cererile trec prin `apiFetch()` (`api/client.ts`): trimite cookie-urile, adaugă `X-CSRFToken`
  la metodele care modifică date și transformă răspunsurile de eroare în `ApiError(status, data)`.
- Starea de autentificare stă în `AuthProvider`: la pornire cere cookie-ul CSRF și `/me/`;
  componentele o citesc prin `useAuth()`.
- Rutele sunt protejate de paznici (`auth/RequireAuth`, `auth/RedirectIfAuthenticated`), puși ca
  rute-layout în `App.tsx`; cât timp `isLoading` e `true` afișează `PageLoader`.
- Direcționarea după rol: un user logat fără rol vede doar `/start`; unul cu rol vede aplicația
  (Layout). Rolul se primește creând o gospodărie din modalul de pe `/start`: după creare,
  `refreshUser()` reîncarcă `/me/`, iar paznicul `RequireNoRole` trimite userul pe Acasă.
  Alăturarea cu cod de invitație nu e încă implementată.
- Flux: componentă din `pages/` → funcție din `api/` (`fetch`) → proxy Vite → `ourmoney/urls.py` →
  `<app>/urls.py` → view → răspuns JSON → înapoi în componentă, care își actualizează state-ul.

### Organizarea codului (`frontend/src/`)

| Folder | Conține | Regulă |
|--------|---------|--------|
| `pages/` | O componentă per rută | Afișează date și state; nu apelează `fetch` direct |
| `components/` | Componente reutilizabile (`Layout`, `AuthLayout`, `PageLoader`, `Button`, `TextField`, `Modal`); fiecare în folderul ei, cu CSS Module | Fără apeluri la API |
| `households/` | Componente de domeniu pentru gospodării (modalul de creare), folosite din `pages/` | Pot apela funcții din `api/` |
| `api/` | `client.ts` (apiFetch) + o funcție per endpoint + tipurile răspunsurilor | Singurul loc unde se folosește `fetch`, doar prin `apiFetch` |
| `auth/` | Contextul de autentificare (`AuthProvider`, `useAuth`) și paznicii de rute | Componentele citesc userul doar prin `useAuth()` |

Culorile, raza și fontul sunt variabile CSS în `index.css` (`--color-*`, `--radius`, `--font`);
componentele le folosesc prin `var(...)`, nu valori hardcodate.

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
2. **Izolarea datelor pe gospodărie.** Orice query pe date de domeniu filtrează după gospodăria utilizatorului autentificat (se aplică din milestone-ul Gospodării).
3. **Modele bogate, services subțiri.** Invariantele trăiesc în modele.
4. **Scrierile pe mai multe rânduri sunt atomice** (`transaction.atomic()`).
5. **Endpoint-urile sunt private implicit.** Doar endpoint-urile marcate explicit `AllowAny` sunt publice.
6. **Documentul reflectă realitatea.** Orice schimbare de structură actualizează acest fișier, `AGENTS.md`, `README.md` și, dacă e cazul, `.ai-factory/DESCRIPTION.md`.

## Anti-pattern-uri

- ❌ Logică de business în views sau serializers
- ❌ Modele anemice cu toate regulile în services
- ❌ `float` pentru sume de bani
- ❌ Query-uri pe date de domeniu nefiltrate după gospodăria utilizatorului
- ❌ Import circular între aplicații
- ❌ `fetch` direct în componente, în loc de o funcție din `frontend/src/api/`
- ❌ Documentarea în acest fișier a unor module care nu există încă în cod
