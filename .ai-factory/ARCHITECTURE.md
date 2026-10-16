# Arhitectură: Structured Modules (Technical Layer)

> Acest document descrie **starea curentă** a proiectului. Se actualizează în același commit cu orice
> schimbare de structură (aplicație nouă, modul nou, dependență nouă, mutare de fișiere).
> Ultima actualizare: 2026-10-16 — scaffold Django inițial.

## Prezentare generală

Backend-ul Our Money este un proiect Django 6.1 creat cu `django-admin startproject`. În acest moment
conține doar pachetul de configurare `ourmoney/ourmoney/`; nu există încă aplicații de domeniu,
API REST, modele proprii sau teste.

Pattern-ul ales este **Structured Modules (Technical Layer)**: fiecare zonă de domeniu este o
aplicație Django separată, iar în interiorul ei codul se împarte pe straturi tehnice
(`views` → `services`/`selectors` → `models`). Regulile de mai jos se aplică fiecărei aplicații
în momentul în care este adăugată.

## Motivarea deciziei

- **Tipul proiectului:** aplicație de finanțe personale (vezi `.ai-factory/DESCRIPTION.md`)
- **Tech stack curent:** Python 3, Django 6.1, SQLite (setarea implicită din scaffold)
- **Factor cheie:** echipă mică și domeniu de complexitate medie → module clare, fără formalismul DDD complet

## Structura folderelor (curentă)

```
our-money/
├── ourmoney/                      # Rădăcina proiectului Django
│   ├── manage.py                  # CLI Django
│   └── ourmoney/                  # Pachetul de configurare (composition root)
│       ├── __init__.py
│       ├── settings.py            # INSTALLED_APPS: doar aplicațiile contrib Django; DB: SQLite
│       ├── urls.py                # Singura rută: admin/
│       ├── asgi.py
│       └── wsgi.py
├── .ai-factory/                   # Context AI Factory (descriere, arhitectură, reguli)
├── .claude/                       # Skill-uri și agenți Claude Code
├── .mcp.json                      # Servere MCP: github, playwright, postgres
├── AGENTS.md
└── README.md
```

## Aplicații / module curente

| Modul | Scop | Stare |
|-------|------|-------|
| `ourmoney` (pachet de configurare) | Setări, rutare, entry points ASGI/WSGI | Generat de `startproject`, nemodificat |

Nu există încă aplicații de domeniu.

## Configurare curentă

- `SECRET_KEY`, `DEBUG = True` și `ALLOWED_HOSTS = []` sunt definite direct în `settings.py`
- Baza de date: `django.db.backends.sqlite3` (`db.sqlite3`)
- Fără Django REST Framework, CORS, logging configurat sau runner de teste instalat
- Nu există fișier de dependențe (`requirements.txt` / `pyproject.toml`)

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
5. **Documentul reflectă realitatea.** Orice schimbare de structură actualizează acest fișier, `AGENTS.md` și, dacă e cazul, `.ai-factory/DESCRIPTION.md`.

## Anti-pattern-uri

- ❌ Logică de business în views sau serializers
- ❌ Modele anemice cu toate regulile în services
- ❌ `float` pentru sume de bani
- ❌ Query-uri pe date de utilizator nefiltrate după utilizator
- ❌ Import circular între aplicații
- ❌ Documentarea în acest fișier a unor module care nu există încă în cod
