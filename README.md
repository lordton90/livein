# LIVE-IN International — scrollom riadený web

Cinematický jednostránkový web pre [LIVE-IN International](https://live-in.international/) — správu krátkodobých prenájmov v Bratislave a Košiciach. Skrolovanie ovláda frame-by-frame prehrávanie filmu (pomalý nájazd prémiovým apartmánom na panorámu Bratislavy za modrej hodiny).

## Spustenie

Stránku treba servírovať cez HTTP (nie otvárať ako súbor):

```bash
python3 -m http.server 8080
# http://localhost:8080
```

## Štruktúra

```
index.html              — domovská stránka (scroll film); en/index.html = EN verzia
sluzby/  o-nas/  kontakt/  na-predaj/  clanky/        — SK podstránky
nehnutelnost/<slug>/    — 8 detailov nehnuteľností (SK)
en/services|about-us|contact|for-sale|articles/       — EN podstránky
en/real-estate/<slug>/  — 8 detailov nehnuteľností (EN)
clanky/<slug>/ · en/articles/<slug>/                  — 3 články v oboch jazykoch
frames/                 — 75 snímok WebP (desktop 1920×1080, mobil 960×540)
assets/fonts/           — self-hostované fonty Archivo + IBM Plex Mono
assets/img/properties/  — fotografie nehnuteľností (zo starého webu)
assets/source/hero.mp4  — zdrojové video (5 s, 1080p, Artlist AI)
content/                — extrahovaný obsah starého webu (JSON + články)
tools/build_pages.py    — generátor podstránok (python3 tools/build_pages.py)
```

Podstránky preberajú kompletný obsah pôvodného webu live-in.international
(služby, o nás, kontakt, ponuka nehnuteľností, články) v novom dizajne,
v slovenčine aj angličtine s prepínačom jazyka.

## Obsah a fakty

Texty vychádzajú z verejných informácií na live-in.international (08/2026):
výnos o 20–30 % vyšší než dlhodobý nájom, kompletná správa s províziou 17 %,
dlhodobá správa 10 %, garantovaný nájom na 1–5 rokov, Londýn od 2018,
Slovensko od januára 2023. Kontakt: info@live-in.co.uk.

## Technika

- Canvas sekvencia so scroll-remapom (dwell zóny okolo kapitol), LERP vyhladzovanie
- Kritické snímky sa načítajú prvé; fallback na najbližšiu načítanú snímku
- Responzívne art-direction: desktop cover, mobil filmový pás (aperture)
- `prefers-reduced-motion`: statický poster bez animácií
- Fonty self-hostované (bez externých závislostí)
