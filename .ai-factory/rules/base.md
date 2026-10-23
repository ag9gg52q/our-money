# Reguli de bază ale proiectului

> Convenții detectate automat din analiza codului (scaffold Django standard) și din stack-ul ales. Editează după nevoie.

## Convenții de denumire

- Fișiere și module Python: `snake_case.py`
- Variabile și funcții: `snake_case`
- Clase (modele, serializers, views): `PascalCase` (ex. `Transaction`, `TransactionSerializer`, `TransactionViewSet`)
- Constante și setări Django: `UPPER_SNAKE_CASE`
- Aplicații Django: nume scurte, la plural, `snake_case` (ex. `accounts`, `transactions`, `budgets`)
- Stil de string-uri: ghilimele simple `'...'`, ca în codul generat de Django
- Formatarea și importurile backend sunt făcute de Ruff (`ruff format ourmoney`, `ruff check ourmoney --fix`) — nu se formatează manual; rânduri de maximum 100 de caractere

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
- Fixture-urile comune stau în `ourmoney/conftest.py`; pentru endpoint-uri care modifică date se testează
  și cu `csrf_client` (verificarea CSRF activă), nu doar cu `force_authenticate`
- Testele care ating baza de date folosesc `pytestmark = pytest.mark.django_db`; URL-urile se obțin cu `reverse()`

## Frontend (React + TypeScript)

- Componente: funcții în PascalCase, `export default`; numele funcției = numele fișierului (`StatusPage.tsx` → `StatusPage`)
- Fișiere non-componentă (ex. `src/api/health.ts`): camelCase; funcții camelCase (`fetchHealth`); tipuri PascalCase (`HealthResponse`)
- Pagini în `src/pages/`, componente reutilizabile în `src/components/`, apeluri la API în `src/api/`
- `fetch` doar în `src/api/`; fiecare funcție verifică `response.ok` și aruncă `Error` altfel
- Adresele API se termină cu `/`
- Importuri fără extensie (`'../api/health'`); importurile din biblioteci separate printr-un rând gol de cele din proiect
- Formatarea: Prettier (ghilimele simple, fără `;`, 2 spații) — `npm run format` înainte de commit; nu se formatează manual
- Fragmentul `<>...</>` doar când se returnează mai multe elemente
