# AGENTS.md

> Hartă structurală a proiectului pentru agenți AI și dezvoltatori noi. Actualizează acest fișier când structura proiectului se schimbă semnificativ.

## Prezentare generală

Aplicație web de finanțe personale care înlocuiește un fișier Excel: cheltuieli, venituri, economii, rapoarte. Detalii în [`.ai-factory/DESCRIPTION.md`](.ai-factory/DESCRIPTION.md).

## Tech Stack

- **Limbaj:** Python 3 (backend), TypeScript (frontend planificat)
- **Framework:** Django 6.1 + Django REST Framework; React (planificat)
- **Bază de date:** PostgreSQL 18
- **ORM:** Django ORM
- **Teste:** pytest + pytest-django

## Structura proiectului

```
our-money/
├── ourmoney/                 # Proiectul Django (conține manage.py)
│   ├── manage.py             # CLI Django: runserver, migrate, makemigrations, startapp
│   ├── ourmoney/             # Pachetul de configurare al proiectului
│   │   ├── settings.py       # Setări din .env (django-environ), DRF, PostgreSQL
│   │   ├── urls.py           # admin/ și api/v1/ → core.urls
│   │   ├── asgi.py           # Entry point ASGI
│   │   └── wsgi.py           # Entry point WSGI
│   └── core/                 # App comun: endpoint-ul de health
│       ├── views.py          # health (GET, public)
│       ├── urls.py           # health/
│       └── tests/            # teste pytest
├── .ai-factory/              # Context AI Factory (descriere, arhitectură, reguli, roadmap)
├── .claude/                  # Skill-uri și agenți Claude Code
├── .env.example              # Variabilele de mediu necesare (copiază în .env)
├── requirements.txt          # Dependențe Python, versiuni fixate
├── pytest.ini                # Configurare pytest-django
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
| `ourmoney/ourmoney/wsgi.py` / `asgi.py` | Entry points pentru servere de producție |
| `.env.example` | Lista variabilelor de mediu: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DATABASE_URL` |
| `pytest.ini` | Configurarea testelor |

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
- Sumele de bani se reprezintă doar cu `Decimal` / `DecimalField`, niciodată `float`.
