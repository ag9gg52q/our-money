# Roadmap proiect

> O aplicație web frumoasă și elegantă care înlocuiește fișierul Excel de cheltuieli, venituri și economii, construită ca drum de învățare pentru Python (Django) și React + TypeScript.

Abordare: **verticală** — fiecare milestone livrează funcționalitatea completă (model + API Django + ecran React), ca rezultatul să fie vizibil în browser la fiecare pas.

## Milestones

- [x] **Scaffold Django** — proiectul Django inițial creat cu `startproject`
- [x] **Fundația backend** — PostgreSQL, setări din `.env`, Django REST Framework, pytest, fișier de dependențe
- [x] **Fundația frontend** — aplicație React + TypeScript (Vite), layout, routing, conectare la API
- [ ] **Autentificare** — login/logout, datele fiecărui utilizator izolate
- [ ] **Categorii și subcategorii** — gestionarea nomenclatorului de categorii și subcategorii
- [ ] **Persoane** — membrii cărora li se atribuie tranzacțiile
- [ ] **Cheltuieli** — adăugare/editare cu dată, persoană, categorie, subcategorie, sumă, notă; listă cu filtre
- [ ] **Venituri** — înregistrarea și lista veniturilor
- [ ] **Economii (savings)** — depuneri/retrageri, soldul economiilor, obiective de economisire
- [ ] **Dashboard și rapoarte** — sumar lunar, pe categorii și persoane, venituri vs cheltuieli, grafice
- [ ] **Bugete** — buget lunar pe categorie, semnalarea depășirii
- [ ] **Multi-valută** — sume în valute diferite, conversie la valuta de bază
- [ ] **Import/export** — import CSV din extrase bancare, export CSV/Excel
- [ ] **Finisaj UI și mobil** — design elegant, responsive, dark mode
- [ ] **Lansare** — Docker, CI, deploy în producție

## Finalizate

| Milestone | Data |
|-----------|------|
| Scaffold Django | 2026-10-16 |
| Fundația backend | 2026-10-16 |
| Fundația frontend | 2026-10-19 |
