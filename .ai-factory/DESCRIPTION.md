# Our Money — Descrierea proiectului

## Prezentare generală

**Our Money** este o aplicație web de finanțe personale care înlocuiește un fișier Excel folosit
în prezent pentru evidența banilor. În Excel se introduc cheltuieli (dată, persoană, categorie,
subcategorie, sumă și alte detalii), venituri și economii, iar pe baza lor se generează rapoarte.
Aplicația trebuie să facă același lucru, dar mai frumos și mai elegant. Backend-ul este un API
Django, iar interfața va fi o aplicație React + TypeScript separată.

Proiectul are și un scop de **învățare**: dezvoltarea lui este drumul prin care se învață
Python (Django) și React + TypeScript. Aplicația pornește de la zero — istoricul din Excel nu se importă.

Stadiul curent: fundațiile backend și frontend și autentificarea sunt gata. Utilizatorii își creează
singuri contul (fără rol), se autentifică prin sesiune Django și sunt direcționați după rol: fără rol →
pagina de început (creare / alăturare la o gospodărie, deocamdată schiță), cu rol → aplicația
(„Gospodăria noastră”, schiță). Rolurile sunt `admin` și `user`. Modelul de gospodărie există (cu cod de invitație), iar
API-ul de creare (creatorul devine admin) e gata; interfața de creare și alăturarea nu sunt încă implementate.
Nu există încă funcționalități de domeniu (cheltuieli, venituri).
Planul de implementare este în `.ai-factory/ROADMAP.md`.

## Funcționalități principale

- **Conturi și roluri** — înregistrare, autentificare; rolurile `admin` (gestionează setările de
  sistem) și `user` (cheltuieli și venituri).
- **Gospodării** — un user creează o gospodărie (devine admin) sau se alătură uneia cu un cod de
  invitație (devine user); fiecare user face parte din cel mult o gospodărie.
- **Cheltuieli** — dată, persoană, categorie, subcategorie, sumă, notă; listă cu filtre.
- **Venituri** — înregistrarea și lista veniturilor.
- **Economii (savings)** — depuneri/retrageri, soldul economiilor, obiective.
- **Categorii, subcategorii și persoane** — nomenclatoarele folosite la înregistrare.
- **Rapoarte și grafice** — sumar lunar, pe categorii și persoane, venituri vs cheltuieli.
- **Bugete** — buget lunar pe categorie, semnalare la depășire.
- **Multi-valută și import/export** — sume în valute diferite, import CSV din extrase bancare, export CSV/Excel.

## Tech Stack

- **Limbaj (backend):** Python 3
- **Framework (backend):** Django 6.1 + Django REST Framework (API REST)
- **Bază de date:** PostgreSQL 18
- **ORM:** Django ORM
- **Configurare:** django-environ (`.env`)
- **Frontend:** React + TypeScript, Vite, React Router (aplicație separată în `frontend/`, consumă API-ul)
- **Autentificare:** sesiune Django (cookie `sessionid` + CSRF), model de utilizator propriu cu rol
- **Calitate cod:** Ruff (backend), ESLint + Prettier (frontend)
- **Teste:** pytest + pytest-django
- **Integrări:** import CSV extrase bancare; sursă de cursuri valutare (de stabilit)

## Note de arhitectură

- Backend-ul expune exclusiv un API REST (DRF); nu se folosesc Django templates pentru UI.
- Proiectul Django se află în `ourmoney/` (`ourmoney/manage.py`, pachetul de setări `ourmoney/ourmoney/`).
  Aplicațiile de domeniu (ex. `accounts`, `transactions`, `budgets`, `reports`) vor fi adăugate în `ourmoney/`.
- Frontend-ul React trăiește separat, în `frontend/`, și comunică doar prin API (în dezvoltare, prin proxy-ul Vite).
- Sumele de bani: întotdeauna `Decimal` / `DecimalField` (niciodată `float`), stocate împreună cu
  codul valutei (ISO 4217).
- Datele vor fi izolate pe gospodărie — fiecare query va filtra după gospodăria utilizatorului
  autentificat.

## Arhitectură

Ghidurile detaliate de arhitectură sunt în `.ai-factory/ARCHITECTURE.md`.
Pattern: Structured Modules (Technical Layer)

## Cerințe non-funcționale

- **Logging:** modulul standard `logging` din Python, nivel configurabil prin `LOG_LEVEL`.
- **Tratarea erorilor:** răspunsuri de eroare structurate (format DRF consistent), validare în serializers.
- **Configurare:** secrete și setări per mediu din variabile de mediu (`.env`), nu în cod.
- **Securitate:** autentificare obligatorie pe toate endpoint-urile, izolare strictă a datelor
  între utilizatori, CORS restrâns la originea frontend-ului, validarea fișierelor CSV importate.
- **Precizie financiară:** calcule cu `Decimal`, rotunjire explicită, fără pierderi la conversia valutară.
