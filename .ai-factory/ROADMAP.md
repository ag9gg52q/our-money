# Roadmap proiect

> O aplicație web frumoasă și elegantă care înlocuiește fișierul Excel de cheltuieli, venituri și economii, construită ca drum de învățare pentru Python (Django) și React + TypeScript.

Abordare: **verticală** — fiecare milestone livrează funcționalitatea completă (model + API Django + ecran React), ca rezultatul să fie vizibil în browser la fiecare pas.

## Milestones

- [x] **Scaffold Django** — proiectul Django inițial creat cu `startproject`
- [x] **Fundația backend** — PostgreSQL, setări din `.env`, Django REST Framework, pytest, fișier de dependențe
- [x] **Fundația frontend** — aplicație React + TypeScript (Vite), layout, routing, conectare la API
- [x] **Autentificare** — signup, login/logout cu sesiune, rute protejate, rol opțional și direcționare după rol
- [x] **Gospodării** — creare (creatorul devine admin), alăturare cu cod de invitație (devine user), datele izolate pe gospodărie
- [x] **Acasă și Setări sistem** — pagina Acasă, scheletul Setărilor (tab-uri, meniul nomenclatoarelor)
- [x] **Categorii** — adăugare, redenumire, dezactivare; doar adminul modifică
- [ ] **Subcategorii** — subcategoriile fiecărei categorii
- [ ] **Surse de venit** — nomenclatorul surselor de venit
- [ ] **Gospodărie** — numele, codul de invitație și membrii, în Nomenclatoare → Gospodărie
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
| Autentificare | 2026-10-23 |
| Gospodării | 2026-10-28 |
| Acasă și Setări sistem | 2026-10-29 |
| Categorii | 2026-10-29 |
