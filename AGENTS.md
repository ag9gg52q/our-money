# AGENTS.md

> Hartă structurală a proiectului pentru agenți AI și dezvoltatori noi. Actualizează acest fișier când structura proiectului se schimbă semnificativ.

## Prezentare generală

Aplicație web de finanțe personale care înlocuiește un fișier Excel: cheltuieli, venituri, economii, rapoarte. Detalii în [`.ai-factory/DESCRIPTION.md`](.ai-factory/DESCRIPTION.md).

## Tech Stack

- **Limbaj:** Python 3 (backend), TypeScript (frontend planificat)
- **Framework:** Django 6.1 + Django REST Framework; React (planificat)
- **Bază de date:** PostgreSQL (momentan SQLite în scaffold)
- **ORM:** Django ORM

## Structura proiectului

```
our-money/
├── ourmoney/                 # Proiectul Django (rădăcina pentru manage.py)
│   ├── manage.py             # CLI Django: runserver, migrate, makemigrations, test
│   └── ourmoney/             # Pachetul de configurare al proiectului
│       ├── settings.py       # Setări Django (DB, INSTALLED_APPS, middleware)
│       ├── urls.py           # Rutele principale (momentan doar admin/)
│       ├── asgi.py           # Entry point ASGI
│       └── wsgi.py           # Entry point WSGI
├── .ai-factory/              # Context AI Factory (descriere, reguli, planuri)
├── .claude/                  # Skill-uri și agenți Claude Code
├── .mcp.json                 # Configurare servere MCP (github, playwright, postgres)
├── skills-lock.json          # Versiunile skill-urilor externe instalate
├── AGENTS.md                 # Acest fișier
├── CLAUDE.md                 # Instrucțiuni Claude Code (include AGENTS.md)
└── README.md
```

## Puncte de intrare cheie

| Fișier | Scop |
|--------|------|
| `ourmoney/manage.py` | Comenzi de management Django |
| `ourmoney/ourmoney/settings.py` | Configurarea proiectului (DB, aplicații, securitate) |
| `ourmoney/ourmoney/urls.py` | Rutarea URL de nivel superior |
| `ourmoney/ourmoney/wsgi.py` / `asgi.py` | Entry points pentru servere de producție |

## Documentație

| Document | Cale | Descriere |
|----------|------|-----------|
| README | README.md | Pagina de start a proiectului |

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

- Nu combina comenzi shell cu `&&`; rulează-le separat, pas cu pas.
  - Greșit: `git checkout main && git pull`
  - Corect: mai întâi `git checkout main`, apoi `git pull origin main`
- Comenzile Django se rulează din directorul `ourmoney/` (unde se află `manage.py`).
- Sumele de bani se reprezintă doar cu `Decimal` / `DecimalField`, niciodată `float`.
