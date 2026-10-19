# Arhitectură: Structured Modules (Technical Layer)

> Acest document descrie **starea curentă** a proiectului. Se actualizează în același commit cu orice
> schimbare de structură (aplicație nouă, modul nou, dependență nouă, mutare de fișiere).
> Ultima actualizare: 2026-10-19 — eliminate fișierele goale din `core` (`models.py`, `admin.py`, `migrations/`).

## Prezentare generală

Backend-ul Our Money este un proiect Django 6.1 care expune un API REST prin Django REST Framework,
cu PostgreSQL ca bază de date. Configurarea vine din variabile de mediu (`.env`). Există un singur
app propriu, `core`, cu endpoint-ul public `GET /api/v1/health/`. Nu există încă aplicații de
domeniu sau modele proprii.

Pattern-ul ales este **Structured Modules (Technical Layer)**: fiecare zonă de domeniu este o
aplicație Django separată, iar în interiorul ei codul se împarte pe straturi tehnice
(`views` → `services`/`selectors` → `models`). Regulile de mai jos se aplică fiecărei aplicații
în momentul în care este adăugată.

## Motivarea deciziei

- **Tipul proiectului:** aplicație de finanțe personale (vezi `.ai-factory/DESCRIPTION.md`)
- **Tech stack curent:** Python 3.13, Django 6.1, Django REST Framework 3.18, PostgreSQL 18, pytest
- **Factor cheie:** echipă mică și domeniu de complexitate medie → module clare, fără formalismul DDD complet

## Structura folderelor (curentă)

```
our-money/
├── ourmoney/                      # Rădăcina proiectului Django
│   ├── manage.py                  # CLI Django
│   ├── ourmoney/                  # Pachetul de configurare (composition root)
│   │   ├── __init__.py
│   │   ├── settings.py            # Setări citite din .env (django-environ), DRF, PostgreSQL
│   │   ├── urls.py                # admin/ și api/v1/ → core.urls
│   │   ├── asgi.py
│   │   └── wsgi.py
│   └── core/                      # App comun (cross-cutting)
│       ├── views.py               # health — GET, public (AllowAny)
│       ├── urls.py                # health/ (name='health')
│       ├── apps.py                # CoreConfig
│       └── tests/
│           └── test_health.py     # GET → 200 {"status": "ok"}, POST → 405
├── .ai-factory/                   # Context AI Factory (descriere, arhitectură, reguli, roadmap)
├── .claude/                       # Skill-uri și agenți Claude Code
├── .env.example                   # Variabilele de mediu necesare (fără valori reale)
├── requirements.txt               # Dependențe directe, versiuni fixate
├── pytest.ini                     # Configurare pytest-django
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

Nu există încă aplicații de domeniu.

## API curent

| Metodă | URL | Permisiune | Răspuns |
|--------|-----|------------|---------|
| GET | `/api/v1/health/` | public (`AllowAny`) | `200 {"status": "ok"}` |

Toate rutele API sunt sub prefixul `/api/v1/`, inclus din `ourmoney/urls.py`.

## Configurare curentă

- **Variabile de mediu** (`.env` în rădăcina repo-ului, citit cu `django-environ`; model în `.env.example`):
  `SECRET_KEY` (obligatoriu), `DEBUG` (implicit `False`), `ALLOWED_HOSTS` (listă separată prin virgulă),
  `DATABASE_URL` (obligatoriu)
- **Baza de date:** PostgreSQL, configurată prin `DATABASES = {'default': env.db('DATABASE_URL')}`
- **DRF:** permisiunea implicită este `IsAuthenticated` — orice endpoint nou cere autentificare,
  cu excepția celor marcate explicit `AllowAny`
- **Teste:** pytest + pytest-django, rulate din rădăcina repo-ului; `pytest.ini` setează
  `DJANGO_SETTINGS_MODULE = ourmoney.settings` și `pythonpath = ourmoney`
- **Dependențe** (`requirements.txt`): Django, djangorestframework, psycopg[binary], django-environ,
  pytest, pytest-django
- Încă neconfigurate: CORS, logging, autentificare pentru API (sesiune/token)

## Reguli de dependență

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
- ❌ Documentarea în acest fișier a unor module care nu există încă în cod
