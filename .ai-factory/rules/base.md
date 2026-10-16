# Reguli de bază ale proiectului

> Convenții detectate automat din analiza codului (scaffold Django standard) și din stack-ul ales. Editează după nevoie.

## Convenții de denumire

- Fișiere și module Python: `snake_case.py`
- Variabile și funcții: `snake_case`
- Clase (modele, serializers, views): `PascalCase` (ex. `Transaction`, `TransactionSerializer`, `TransactionViewSet`)
- Constante și setări Django: `UPPER_SNAKE_CASE`
- Aplicații Django: nume scurte, la plural, `snake_case` (ex. `accounts`, `transactions`, `budgets`)
- Stil de string-uri: ghilimele simple `'...'`, ca în codul generat de Django

## Structura modulelor

- Proiectul Django: `ourmoney/` (conține `manage.py`); setările în `ourmoney/ourmoney/settings.py`, rutele în `ourmoney/ourmoney/urls.py`
- Fiecare domeniu este o aplicație Django separată în `ourmoney/<app>/` cu `models.py`, `serializers.py`, `views.py`, `urls.py`, `tests/`
- Rutele fiecărei aplicații se includ în `ourmoney/ourmoney/urls.py` prin `include()`
- Frontend-ul React (planificat) stă separat de proiectul Django și comunică doar prin API

## Tratarea erorilor

- Validarea datelor de intrare în serializers DRF (`validate_<field>`, `validate`), nu în views
- Erorile ajung la client în formatul standard DRF; nu se întorc trace-uri sau detalii interne
- Se ridică excepții DRF (`ValidationError`, `NotFound`, `PermissionDenied`) în loc de răspunsuri construite manual
- Sumele de bani sunt `Decimal` / `models.DecimalField`; nu se folosește `float` pentru bani

## Control Flow

- Prefer flat, readable control flow over deeply nested conditionals. Use guard clauses, early `return`/`continue`, small named helper methods, or explicit classification logic when they make the code easier to follow. Handle edge cases and irrelevant branches early so the main path stays visible.

## Logging

- Modulul standard `logging`: `logger = logging.getLogger(__name__)` la nivel de modul
- Configurarea centralizată prin `LOGGING` în `settings.py`, nivel din variabila de mediu `LOG_LEVEL`
- Nu se loghează date sensibile (parole, token-uri, conținutul complet al extraselor bancare)

## Documentație de context

- `.ai-factory/ARCHITECTURE.md`, `AGENTS.md`, `README.md` și `.ai-factory/DESCRIPTION.md` descriu starea curentă a codului, nu planurile viitoare
- Orice schimbare de structură, modul, dependență sau configurare actualizează aceste fișiere în același commit
- O sarcină nu e considerată terminată dacă aceste fișiere nu mai corespund codului

## Teste

- pytest + pytest-django; testele în `ourmoney/<app>/tests/test_*.py`
- Fiecare endpoint testat inclusiv pentru izolarea datelor între utilizatori
