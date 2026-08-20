#!/usr/bin/env python3
"""Generate all LIVE-IN International subpages (SK + EN) from content/ data.

Usage: python3 tools/build_pages.py   (run from repo root)

Copy sourced verbatim from the previous live-in.international site (mirrored
2026-08). The homepage (index.html) is hand-maintained; en/index.html is
derived from it by the translation table at the bottom.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
C = ROOT / "content"

BOOKING = "https://booking.live-in.international/en/properties"
FACEBOOK = "https://www.facebook.com/profile.php?id=61559819081423"
INSTAGRAM = "https://www.instagram.com/livein_sk/"
PHONE = "+421 940 213 613"
EMAIL = "info@live-in.international"
ADDRESS = "Čermeľská cesta 3, Košice, SK"

NAV = {
    "sk": [
        ("Domov", "/"), ("Naše služby", "/sluzby/"), ("Zarezervuj si", BOOKING),
        ("Na predaj", "/na-predaj/"), ("Články", "/clanky/"),
        ("O nás", "/o-nas/"), ("Kontakt", "/kontakt/"),
    ],
    "en": [
        ("Home", "/en/"), ("Our services", "/en/services/"), ("Book now", BOOKING),
        ("For sale", "/en/for-sale/"), ("Articles", "/en/articles/"),
        ("About us", "/en/about-us/"), ("Contact", "/en/contact/"),
    ],
}

T = {
    "sk": {
        "lang_label": "EN", "other": "en",
        "footer_tag": "Naša cesta začala v roku 2018 v srdci londýnskeho finančného sveta, kde sme sa naučili využívať najnovšie technológie a trendy.",
        "footer_services": "Naše služby",
        "footer_services_items": [
            ("Správa krátkodobých prenájmov", "/sluzby/#kratkodobe"),
            ("Garantovaný nájom s pevným mesačným príjmom", "/sluzby/#garantovany"),
            ("Dlhodobý prenájom a správa nehnuteľností", "/sluzby/#dlhodobe"),
            ("Predaj nehnuteľností", "/sluzby/#predaj"),
        ],
        "footer_contact": "Kontakt",
        "phone_label": "Telefón", "where": "Kde pôsobíme",
        "where_val": "Bratislava · Košice · Londýn",
        "cta_title": "Zistite, koľko môže zarábať váš byt.",
        "cta_btn": "Bezplatná analýza",
        "sold": "Predané", "forsale": "Na predaj",
        "beds": "spálne", "baths": "kúpeľne",
        "back_list": "← Späť na ponuku",
        "facts": "Parametre", "desc_h": "Popis",
        "interest": "Mám záujem o obhliadku",
        "read": "Čítať článok",
        "published": "28. júla 2025",
        "articles_lead": "Rady a skúsenosti z praxe správy krátkodobých prenájmov v Bratislave a Košiciach.",
        "more_articles": "Ďalšie články",
    },
    "en": {
        "lang_label": "SK", "other": "sk",
        "footer_tag": "Our journey began in 2018 in the heart of London's financial world, where we learned to embrace the latest technologies and trends.",
        "footer_services": "Our services",
        "footer_services_items": [
            ("Management of short-term rentals", "/en/services/#kratkodobe"),
            ("Guaranteed rent with fixed monthly income", "/en/services/#garantovany"),
            ("Long-term rental and property management", "/en/services/#dlhodobe"),
            ("Sale of real estate", "/en/services/#predaj"),
        ],
        "footer_contact": "Contact",
        "phone_label": "Phone", "where": "Where we operate",
        "where_val": "Bratislava · Košice · London",
        "cta_title": "Find out how much your apartment could earn.",
        "cta_btn": "Free analysis",
        "sold": "Sold", "forsale": "For sale",
        "beds": "bedrooms", "baths": "bathrooms",
        "back_list": "← Back to listings",
        "facts": "Details", "desc_h": "Description",
        "interest": "Request a viewing",
        "read": "Read article",
        "published": "July 28, 2025",
        "articles_lead": "Advice and hands-on experience from managing short-term rentals in Bratislava and Košice.",
        "more_articles": "More articles",
    },
}


def head(title, desc, root, lang):
    return f"""<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="theme-color" content="#0a0f16">
  <meta name="description" content="{html.escape(desc, quote=True)}">
  <title>{html.escape(title)}</title>
  <link rel="icon" href="{root}assets/img/favicon-32.png" sizes="32x32">
  <link rel="icon" href="{root}assets/img/favicon-192.png" sizes="192x192">
  <link rel="apple-touch-icon" href="{root}assets/img/favicon-192.png">
  <link href="{root}assets/fonts/fonts.css" rel="stylesheet">
  <link href="{root}assets/site.css" rel="stylesheet">
</head>
<body>
"""


def nav(root, lang, current):
    t = T[lang]
    links = []
    for label, href in NAV[lang]:
        if href.startswith("http"):
            links.append(f'<a class="is-external" href="{href}">{label}</a>')
        else:
            cur = ' aria-current="page"' if href == current else ""
            links.append(f'<a href="{root}{href.lstrip("/")}"{cur}>{label}</a>')
    other_href = LANG_MAP.get(current, "/" if lang == "sk" else "/en/")
    links.append(f'<a class="site-nav__lang" href="{root}{other_href.lstrip("/") or "."}" lang="{t["other"]}">{t["lang_label"]}</a>')
    home = root if lang == "sk" else root + "en/"
    return f"""<header class="site-nav">
  <a class="site-nav__brand" href="{home}" aria-label="LIVE-IN International">
    <img src="{root}assets/img/logo-on-light.png" alt="LIVE-IN International" width="335" height="141">
  </a>
  <nav class="site-nav__links" aria-label="{'Hlavná navigácia' if lang == 'sk' else 'Main navigation'}">
    {' '.join(links)}
  </nav>
</header>
"""


def footer(root, lang):
    t = T[lang]
    items = "".join(
        f'<li><a href="{root}{href.lstrip("/")}">{label}</a></li>'
        for label, href in t["footer_services_items"]
    )
    return f"""<footer class="site-footer">
  <div class="site-footer__grid">
    <div>
      <p class="site-footer__brand"><img src="{root}assets/img/logo-on-light.png" alt="LIVE-IN International" width="335" height="141"></p>
      <p>{t["footer_tag"]}</p>
    </div>
    <div>
      <h3 class="micro">{t["footer_services"]}</h3>
      <ul>{items}</ul>
    </div>
    <div>
      <h3 class="micro">{t["footer_contact"]}</h3>
      <ul>
        <li><p>{ADDRESS}</p></li>
        <li><a href="tel:{PHONE.replace(' ', '')}">{PHONE}</a></li>
        <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
        <li><p class="micro" style="margin-top:10px">{t["where"]}</p><p>{t["where_val"]}</p></li>
      </ul>
    </div>
  </div>
  <div class="site-footer__meta micro">
    <span>© 2026 LIVE-IN International</span>
    <span><a href="{FACEBOOK}">Facebook</a> · <a href="{INSTAGRAM}">Instagram</a> · <a href="{BOOKING}">Booking</a></span>
  </div>
</footer>
</body>
</html>
"""


def cta_band(root, lang):
    t = T[lang]
    contact = f"{root}kontakt/" if lang == "sk" else f"{root}en/contact/"
    return f"""<section class="cta-band">
  <h2>{t["cta_title"]}</h2>
  <a class="cta-solid" href="{contact}">{t["cta_btn"]}</a>
</section>
"""


def page_hero(root, eyebrow, title, lead="", frame="frame-0042"):
    lead_html = f'<p class="page-hero__lead">{lead}</p>' if lead else ""
    return f"""<section class="page-hero">
  <div class="page-hero__film" style="background-image:url('{root}frames/desktop/{frame}.webp')" aria-hidden="true"></div>
  <p class="page-hero__eyebrow micro">{eyebrow}</p>
  <h1>{title}</h1>
  {lead_html}
</section>
"""


def write(path, content):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    print("wrote", path)


# ---------------------------------------------------------------- services

SERVICES = {
    "sk": [
        {
            "id": "kratkodobe",
            "title": "Správa krátkodobých prenájmov",
            "sub": "Získajte maximum z vášho bytu bez každodenných starostí",
            "fee": ("17 %", "z príjmov"),
            "body": [
                "Postaráme sa o home staging a dekorovanie interiéru tak, aby bol atraktívny pre hostí a ľahšie sa prenajímal. Zabezpečíme profesionálne fotenie a videoprezentácie, ktoré zaujmú už na prvý pohľad.",
                "Vytvoríme a budeme spravovať inzeráty na platformách ako Airbnb, Booking.com a ďalších, vrátane dynamického nacenenia pomocou umelej inteligencie (PriceLabs), ktoré optimalizuje ceny podľa sezóny, dopytu a konkurencie.",
                "Komunikáciu s hosťami zabezpečujeme automatizovane – od prvotnej správy až po pokyny na príchod a hodnotenie po odchode. Vaša nehnuteľnosť bude vybavená smart zámkami, kamerami a senzormi pre bezkľúčový vstup a zvýšenú bezpečnosť.",
                "Po každom pobyte zabezpečíme profesionálne upratovanie, pranie a údržbu. Každý mesiac vám zašleme detailný výkaz výnosov, nákladov a obsadenosti.",
            ],
            "note": ("Táto služba je ideálna pre",
                     "Majiteľov bytov, ktorí chcú zarobiť viac než pri dlhodobom prenájme, investorov hľadajúcich aktívne riadenie s vysokým výnosom a zaneprázdnených vlastníkov, ktorí chcú prenájom zveriť profesionálom."),
        },
        {
            "id": "garantovany",
            "title": "Garantovaný nájom",
            "sub": "Stabilný príjem bez výpadkov a starostí",
            "fee": ("1–5 rokov", "fixný mesačný nájom"),
            "body": [
                "Uzavrieme s vami nájomnú zmluvu na obdobie 1 až 5 rokov – my sme vaším nájomcom, nie konečný hosť. Platíme vám fixný mesačný nájom bez ohľadu na obsadenosť bytu.",
                "Preberáme zodpovednosť za bežnú údržbu, drobné opravy a starostlivosť o spotrebiče. Vaša nehnuteľnosť bude využívaná ako krátkodobý prenájom (serviced accommodation), no celý proces správy ostáva na nás.",
            ],
            "note": ("Výhody",
                     "Nulové riziko neobsadenosti alebo neplatičov, plynulý cashflow ideálny najmä pre investorov či vlastníkov žijúcich v zahraničí a žiadny kontakt s hosťami, upratovaním či reklamáciami."),
        },
        {
            "id": "dlhodobe",
            "title": "Správa dlhodobého prenájmu",
            "sub": "Zabezpečíme všetko potrebné, vy si užívate pokoj a výnosy",
            "fee": ("10 %", "z nájmu"),
            "body": [
                "Nájdeme vhodného nájomníka vrátane overenia referencií, preverenia solventnosti a osobného pohovoru. Pripravíme a zabezpečíme podpis nájomných zmlúv vrátane jasne definovaných podmienok, výšky depozitu a možného predĺženia alebo ukončenia.",
                "Každý mesiac sledujeme platby, posielame upomienky a riešime prípadné oneskorenia. Fyzické kontroly bytu vykonávame každé 3 až 6 mesiacov a výsledky vám pravidelne reportujeme.",
                "Zabezpečujeme údržbu, servis a riešenie havárií cez overených dodávateľov. Reprezentujeme vás pred spoločenstvom vlastníkov, správcami a dodávateľmi energií.",
            ],
            "note": ("Pre koho je to vhodné",
                     "Pre majiteľov, ktorí preferujú stabilitu a dlhodobé výnosy, aj pre investorov hľadajúcich spoľahlivého partnera bez nutnosti aktívne sa zapájať do správy."),
        },
        {
            "id": "predaj",
            "title": "Predaj nehnuteľností s kompletným servisom",
            "sub": "Predajte svoju nehnuteľnosť pod kontrolou a s maximálnym ziskom",
            "fee": ("Od ocenenia", "po kataster"),
            "body": [
                "Začneme bezplatným ohodnotením, kde zohľadníme lokalitu, stav bytu, výnosový potenciál a aktuálnu situáciu na trhu. Postaráme sa o profesionálnu prezentáciu – fotografie, 3D vizualizácie, videá aj pôdorysy.",
                "Inzerujeme na najväčších realitných portáloch a v zahraničných sieťach. Zabezpečíme individuálny marketing vrátane cielenej reklamy na sociálnych sieťach, Google Ads a emailových kampaní.",
                "Realizujeme obhliadky, vyjednávame ceny, poskytujeme hypotekárne poradenstvo a kompletne zastrešujeme právny servis – zmluvy, kataster, preberacie protokoly.",
            ],
            "note": ("Prečo predať cez nás",
                     "Oslovíme aj zahraničných investorov vďaka našej medzinárodnej sieti. Byt dokážeme predať aj s existujúcimi hosťami alebo ako hotový investičný produkt so zabehnutým manažmentom."),
        },
    ],
    "en": [
        {
            "id": "kratkodobe",
            "title": "Managing short-term rentals",
            "sub": "Get the most out of your apartment without everyday worries",
            "fee": ("17 %", "of income"),
            "body": [
                "We take care of the home staging and interior decorating to make it attractive for guests and easier to rent. We will provide professional photography and video presentations that will catch the eye at first glance.",
                "We'll create and manage listings on platforms like Airbnb, Booking.com and more, including dynamic pricing using artificial intelligence (PriceLabs) that optimizes prices based on season, demand and competition.",
                "We automate communication with guests – from the initial message to check-in instructions and post-departure reviews. Your property will be equipped with smart locks, cameras and sensors for keyless entry and enhanced security.",
                "We provide professional cleaning, laundry and maintenance after each stay. Each month we will send you a detailed statement of income, expenses and occupancy.",
            ],
            "note": ("This service is ideal for",
                     "Apartment owners looking to earn more than with long-term rentals, investors looking for active management with high returns, and busy owners who want to entrust renting to professionals."),
        },
        {
            "id": "garantovany",
            "title": "Guaranteed Rent",
            "sub": "Stable income without downtimes and worries",
            "fee": ("1–5 years", "fixed monthly rent"),
            "body": [
                "We will enter into a lease agreement with you for a period of 1 to 5 years – we are your tenant, not the final guest. We pay you a fixed monthly rent regardless of the occupancy of the apartment.",
                "We take responsibility for routine maintenance, minor repairs and appliance care. Your property will be used as a short-term rental (serviced accommodation), but the entire management process remains with us.",
            ],
            "note": ("Advantages",
                     "Zero risk of vacancy or non-payment, smooth cash flow ideal especially for investors or owners living abroad and no contact with guests, cleaning or complaints."),
        },
        {
            "id": "dlhodobe",
            "title": "Long-Term Let Management",
            "sub": "We provide everything you need, you enjoy peace of mind and returns",
            "fee": ("10 %", "of rent"),
            "body": [
                "We will find a suitable tenant including reference checks, solvency checks and a personal interview. We will prepare and arrange the signing of lease agreements including clearly defined terms, deposit amount and possible extension or termination.",
                "We monitor payments each month, send reminders and deal with any delays. We carry out physical inspections of the apartment every 3 to 6 months and report the results to you on a regular basis.",
                "We arrange maintenance, servicing and breakdown resolution through vetted contractors. We represent you before the owners' association, managing agents and energy suppliers.",
            ],
            "note": ("For whom it is suitable",
                     "For owners who prefer stability and long-term returns, as well as for investors looking for a reliable partner without the need to be actively involved in management."),
        },
        {
            "id": "predaj",
            "title": "Full-service real estate sales",
            "sub": "Sell your property under control and with maximum profit",
            "fee": ("Valuation", "to closing"),
            "body": [
                "We will start with a free valuation where we will take into account the location, condition of the apartment, income potential and the current market situation. We will take care of a professional presentation – photos, 3D visualizations, videos and floor plans.",
                "We advertise on the largest real estate portals and in foreign networks. We provide individual marketing including targeted advertising on social networks, Google Ads and email campaigns.",
                "We carry out viewings, negotiate prices, provide mortgage advice and complete legal service – contracts, cadastre, acceptance protocols.",
            ],
            "note": ("Why sell through us",
                     "We also reach out to foreign investors thanks to our international network. We can also sell the apartment with existing guests or as a finished investment product with established management."),
        },
    ],
}


def build_services(lang, path, current, root):
    t = T[lang]
    eyebrow = "LIVE-IN International / Bratislava · Košice"
    title = "Naše služby" if lang == "sk" else "Our services"
    lead = ("Špecializujeme sa na štyri služby: krátkodobé prenájmy, garantovaný nájom, dlhodobú správu a predaj nehnuteľností."
            if lang == "sk" else
            "We specialize in four services: short-term rentals, guaranteed rent, long-term management and real estate sales.")
    blocks = ""
    for i, s in enumerate(SERVICES[lang], 1):
        paras = "".join(f"<p>{p}</p>" for p in s["body"])
        blocks += f"""<article class="service-article" id="{s["id"]}">
  <div>
    <p class="micro" style="color:var(--alloy-dark)">0{i}</p>
    <h2>{s["title"]}</h2>
    <p class="service-sub">{s["sub"]}</p>
    <p class="service-fee"><strong>{s["fee"][0]}</strong><span class="micro" style="color:var(--alloy-dark)">{s["fee"][1]}</span></p>
  </div>
  <div class="service-body">
    {paras}
    <div class="service-note"><span class="micro">{s["note"][0]}</span><p>{s["note"][1]}</p></div>
  </div>
</article>
"""
    body = page_hero(root, eyebrow, title, lead, "frame-0030") + f'<main class="section">{blocks}</main>' + cta_band(root, lang)
    write(path, head(f"{title} — LIVE-IN International",
                     lead, root, lang) + nav(root, lang, current) + body + footer(root, lang))


# ---------------------------------------------------------------- about

ABOUT = {
    "sk": {
        "title": "Od Londýna k lídrovi na Slovensku",
        "lead": "LIVE-IN International je spojenie globálnej expertízy a lokálneho know-how v správe nehnuteľností.",
        "story": [
            "Naša cesta začala v roku 2018 v Londýne – jednom z najkonkurencieschopnejších realitných trhov sveta – kde sme vyvinuli osvedčené stratégie, dynamické oceňovanie a profesionálny marketing.",
            "Od januára 2023 prinášame túto londýnsku inováciu na slovenský trh, najmä do Bratislavy a Košíc, aby sme majiteľom nehnuteľností zabezpečili až o 30 % vyššie výnosy z prenájmu.",
        ],
        "mission_h": "Naša misia",
        "mission": "Stať sa vaším dlhodobým partnerom, ktorý vám uľahčí život a maximalizuje návratnosť investície. Veríme, že každá nehnuteľnosť je jedinečná, a preto ku každej pristupujeme s osobným nasadením, transparentnosťou a špičkovými technológiami – od AI oceňovania cez smart home riešenia až po 24/7 komunikáciu s hosťami.",
        "values_h": "Naše hodnoty",
        "values": [
            ("Partnerstvo", "Váš úspech je naším úspechom. Každý klient je pre nás rovnako dôležitý a cíti sa ako súčasť nášho tímu."),
            ("Inovácia", "Neustále sledujeme nové trendy a technológie, aby sme vám prinášali maximálne efektívne riešenia."),
            ("Profesionalita", "Dodržiavame medzinárodné štandardy kvality, od upratovania a údržby až po strategický predaj."),
            ("Transparentnosť", "Žiadne skryté poplatky, jasné reporty a otvorená komunikácia každý mesiac."),
        ],
        "why_h": "Prečo LIVE-IN?",
        "why": "S nami získate kompletnú starostlivosť o vašu nehnuteľnosť: od marketingu na Airbnb a Booking.com, cez dynamické stanovenie cien až po garantovaný nájom. Naša provízia je iba 17 % z krátkodobých príjmov (10 % pri dlhodobom prenájme) a nič viac – jasne, férovo a bez starostí. Pridajte sa k desiatkam spokojných klientov, ktorým sme už pomohli optimalizovať výnosy a vyťažiť z nehnuteľnosti maximum.",
    },
    "en": {
        "title": "From London to a leader in Slovakia",
        "lead": "LIVE-IN International is a combination of global expertise and local know-how in property management.",
        "story": [
            "Our journey began in 2018 in London – one of the most competitive real estate markets in the world – where we developed proven strategies, dynamic pricing and professional marketing.",
            "Since January 2023, we have been bringing this London innovation to the Slovak market, especially to Bratislava and Košice, to provide property owners with up to 30% higher rental yields.",
        ],
        "mission_h": "Our mission",
        "mission": "To become your long-term partner, making your life easier and maximizing your return on investment. We believe that every property is unique, which is why we approach each one with personal commitment, transparency and cutting-edge technology – from AI pricing to smart home solutions to 24/7 guest communication.",
        "values_h": "Our values",
        "values": [
            ("Partnership", "Your success is our success. Every client is equally important to us and feels like part of our team."),
            ("Innovation", "We constantly follow new trends and technologies to bring you maximally effective solutions."),
            ("Professionalism", "We maintain international quality standards, from cleaning and maintenance to strategic sales."),
            ("Transparency", "No hidden fees, clear reports and open communication every month."),
        ],
        "why_h": "Why LIVE-IN?",
        "why": "With us, you get complete care for your property: from marketing on Airbnb and Booking.com, through dynamic pricing, to guaranteed rent. Our commission is only 17% of short-term income (10% for long-term rentals) and nothing more – clear, fair and worry-free. Join dozens of satisfied clients whom we have already helped optimize their yields and get the maximum out of their property.",
    },
}


def build_about(lang, path, current, root):
    a = ABOUT[lang]
    story = "".join(f"<p>{p}</p>" for p in a["story"])
    values_html = "".join(
        f'<div class="value-tile"><h3>{v[0]}</h3><p>{v[1]}</p></div>' for v in a["values"]
    )
    body = page_hero(root, "LIVE-IN International / 2018 → 2026", a["title"], a["lead"], "frame-0060")
    body += f"""<main>
  <section class="section">
    <div class="prose">
      {story}
      <h2>{a["mission_h"]}</h2>
      <p>{a["mission"]}</p>
    </div>
  </section>
  <section class="section section--tight">
    <div class="section__head"><h2 class="section__title">{a["values_h"]}</h2></div>
    <div class="value-grid">{values_html}</div>
  </section>
  <section class="section section--tight">
    <div class="prose">
      <h2>{a["why_h"]}</h2>
      <p>{a["why"]}</p>
    </div>
  </section>
</main>
"""
    body += cta_band(root, lang)
    write(path, head(f"{a['title']} — LIVE-IN International", a["lead"], root, lang)
          + nav(root, lang, current) + body + footer(root, lang))


# ---------------------------------------------------------------- contact

FORM = {
    "sk": {
        "form_h": "Zanechajte nám správu",
        "name": "Meno a priezvisko", "email": "Email", "phone": "Telefón (nepovinné)",
        "msg": "Správa", "msg_ph": "Napíšte nám, o akú nehnuteľnosť ide a čo potrebujete…",
        "send": "Odoslať správu",
        "note": "Odoslaním správy súhlasíte, že vás budeme kontaktovať na uvedený email alebo telefón.",
        "subject": "Nová správa z webu LIVE-IN International",
        "thanks_slug": "kontakt/dakujeme/index.html",
        "thanks_url": "dakujeme/",
        "thanks_title": "Ďakujeme za správu",
        "thanks_lead": "Vaša správa bola odoslaná. Ozveme sa vám čo najskôr — zvyčajne do 24 hodín.",
        "thanks_back": "← Späť na domovskú stránku",
    },
    "en": {
        "form_h": "Leave us a message",
        "name": "Full name", "email": "Email", "phone": "Phone (optional)",
        "msg": "Message", "msg_ph": "Tell us about your property and what you need…",
        "send": "Send message",
        "note": "By sending the message you agree to be contacted at the email or phone provided.",
        "subject": "New message from the LIVE-IN International website",
        "thanks_slug": "en/contact/thank-you/index.html",
        "thanks_url": "thank-you/",
        "thanks_title": "Thank you for your message",
        "thanks_lead": "Your message has been sent. We will get back to you as soon as possible — usually within 24 hours.",
        "thanks_back": "← Back to the homepage",
    },
}


def build_contact(lang, path, current, root):
    t = T[lang]
    f = FORM[lang]
    title = "Kontakt" if lang == "sk" else "Contact"
    lead = ("Zanechajte nám správu – ozveme sa vám s bezplatnou analýzou výnosového potenciálu vašej nehnuteľnosti."
            if lang == "sk" else
            "Leave us a message – we will get back to you with a free analysis of your property's earning potential.")
    addr_label = "Adresa" if lang == "sk" else "Address"
    body = page_hero(root, "LIVE-IN International / Bratislava · Košice · " + ("Londýn" if lang == "sk" else "London"), title, lead, "frame-0070")
    body += f"""<main class="section">
  <div class="contact-grid">
    <div class="contact-tile"><span class="micro">{addr_label}</span><p>{ADDRESS}</p></div>
    <div class="contact-tile"><span class="micro">{t["phone_label"]}</span><a href="tel:{PHONE.replace(' ', '')}">{PHONE}</a></div>
    <div class="contact-tile"><span class="micro">Email</span><a href="mailto:{EMAIL}">{EMAIL}</a></div>
    <div class="contact-tile"><span class="micro">{t["where"]}</span><p>{t["where_val"]}</p></div>
  </div>

  <form class="contact-form" action="https://formsubmit.co/{EMAIL}" method="POST">
    <h2>{f["form_h"]}</h2>
    <input type="hidden" name="_subject" value="{f["subject"]}">
    <input type="hidden" name="_template" value="table">
    <input type="hidden" name="_captcha" value="false">
    <input type="hidden" name="_next" value="" id="form-next">
    <input type="text" name="_honey" style="display:none" tabindex="-1" autocomplete="off" aria-hidden="true">
    <div class="form-grid">
      <div class="form-field">
        <label for="cf-name">{f["name"]}</label>
        <input id="cf-name" name="name" type="text" required autocomplete="name">
      </div>
      <div class="form-field">
        <label for="cf-email">{f["email"]}</label>
        <input id="cf-email" name="email" type="email" required autocomplete="email">
      </div>
      <div class="form-field form-field--full">
        <label for="cf-phone">{f["phone"]}</label>
        <input id="cf-phone" name="phone" type="tel" autocomplete="tel">
      </div>
      <div class="form-field form-field--full">
        <label for="cf-msg">{f["msg"]}</label>
        <textarea id="cf-msg" name="message" required placeholder="{f["msg_ph"]}"></textarea>
      </div>
      <div class="form-field--full">
        <button class="paper-cta" type="submit">{f["send"]}</button>
        <p class="form-note">{f["note"]}</p>
      </div>
    </div>
  </form>
  <script>document.getElementById("form-next").value = new URL("{f["thanks_url"]}", window.location.href).href;</script>

  <div style="margin-top:clamp(28px,4vw,48px)">
    <a class="paper-cta" href="{BOOKING}">{'Zarezervuj si pobyt' if lang == 'sk' else 'Book a stay'}</a>
  </div>
</main>
"""
    write(path, head(f"{title} — LIVE-IN International", lead, root, lang)
          + nav(root, lang, current) + body + footer(root, lang))

    # thank-you page (one level deeper than the contact page)
    troot = "../" + root
    tbody = page_hero(troot, "LIVE-IN International", f["thanks_title"], f["thanks_lead"], "frame-0070")
    home = troot if lang == "sk" else troot + "en/"
    tbody += f"""<main class="section">
  <p><a class="paper-cta" href="{home}">{f["thanks_back"]}</a></p>
</main>
"""
    write(f["thanks_slug"], head(f"{f['thanks_title']} — LIVE-IN International", f["thanks_lead"], troot, lang)
          + nav(troot, lang, current) + tbody + footer(troot, lang))


# ---------------------------------------------------------------- properties

def parse_params(raw, lang):
    keys = ([("Cena za m2", "Cena za m²"), ("Typ", "Typ"), ("Spálne", "Spálne"), ("Kúpelne", "Kúpeľne"),
             ("Počet izieb", "Počet izieb"), ("Počet poschodí", "Počet poschodí"), ("Podlažie", "Podlažie"),
             ("Úžitková plocha", "Úžitková plocha"), ("Rok výstavby", "Rok výstavby"), ("Rok rekonštrukcie", "Rok rekonštrukcie")]
            if lang == "sk" else
            [("Price per m2", "Price per m²"), ("Type", "Type"), ("Bedrooms", "Bedrooms"), ("Bathrooms", "Bathrooms"),
             ("Number of rooms", "Rooms"), ("Number of floors", "Floors"), ("Floor", "Floor"),
             ("Usable area", "Usable area"), ("Year of construction", "Built"), ("Year of reconstruction", "Renovated")])
    out = []
    for key, label in keys:
        m = re.search(re.escape(key) + r"\s*:\s*([\d,\.]+ ?(?:€|m²)?|\w[\w\s²-]*?)(?=\s+[A-ZÚŽČĽŠ]|$)", raw)
        if m:
            out.append((label, m.group(1).strip()))
    return out


def prop_paths(lang, slug):
    return (f"nehnutelnost/{slug}/index.html", f"/nehnutelnost/{slug}/") if lang == "sk" \
        else (f"en/real-estate/{slug}/index.html", f"/en/real-estate/{slug}/")


def build_properties(lang, list_path, list_current, root_list):
    t = T[lang]
    props = json.loads((C / ("properties.json" if lang == "sk" else "properties-en.json")).read_text())
    title = "Na predaj" if lang == "sk" else "For sale"
    lead = ("Aktuálna ponuka nehnuteľností na predaj v Bratislave, Košiciach a okolí."
            if lang == "sk" else
            "Current offer of properties for sale in Bratislava, Košice and the surrounding area.")

    def img_of(p):
        img_slug = p.get("sk_slug") or p["slug"]
        return f"assets/img/properties/{img_slug}.webp"

    cards = ""
    for p in props:
        _, url = prop_paths(lang, p["slug"])
        sold = p["status"] in ("Predané", "Sold")
        status_cls = " prop-card__status--sold" if sold else ""
        params = dict(parse_params(p["params"], lang))
        area = params.get("Úžitková plocha") or params.get("Usable area") or ""
        rooms = params.get("Počet izieb") or params.get("Rooms") or ""
        meta = " · ".join(x for x in [f"{rooms} {'izb.' if lang == 'sk' else 'rooms'}" if rooms else "", area] if x)
        cards += f"""<a class="prop-card" href="{root_list}{url.lstrip('/')}">
  <div class="prop-card__media">
    <img src="{root_list}{img_of(p)}" alt="{html.escape(p["title"], quote=True)}" loading="lazy" width="1400" height="933">
    <span class="prop-card__status micro{status_cls}">{p["status"]}</span>
  </div>
  <div class="prop-card__body">
    <h2 class="prop-card__title">{html.escape(p["title"])}</h2>
    <p class="prop-card__loc">{html.escape(p["loc"])}</p>
    <div class="prop-card__foot">
      <span class="prop-card__price">{p["price"]}</span>
      <span class="prop-card__meta micro">{meta}</span>
    </div>
  </div>
</a>
"""
    body = page_hero(root_list, "LIVE-IN International / " + ("Predaj nehnuteľností" if lang == "sk" else "Real estate sales"), title, lead, "frame-0012")
    body += f'<main class="section"><div class="prop-grid">{cards}</div></main>'
    body += cta_band(root_list, lang)
    write(list_path, head(f"{title} — LIVE-IN International", lead, root_list, lang)
          + nav(root_list, lang, list_current) + body + footer(root_list, lang))

    # detail pages
    for p in props:
        path, url = prop_paths(lang, p["slug"])
        root = "../../" if lang == "sk" else "../../../"
        params = parse_params(p["params"], lang)
        dl = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in params)
        desc = re.sub(r"(Show all description|Zobraziť celý popis|Zobrazit celý popis)\s*$", "", p["desc"]).strip()
        desc_paras = "".join(f"<p>{html.escape(s.strip())}</p>" for s in re.split(r"(?<=[.!?])\s+(?=[A-ZÚŽČĽŠVPN0-9])", desc) if s.strip())
        sold = p["status"] in ("Predané", "Sold")
        status_cls = " prop-card__status--sold" if sold else ""
        list_url = f"{root}na-predaj/" if lang == "sk" else f"{root}en/for-sale/"
        img_slug = p.get("sk_slug") or p["slug"]
        gallery_files = sorted((ROOT / "assets/img/properties/gallery" / img_slug).glob("*.webp"))
        gallery_h = "Fotogaléria" if lang == "sk" else "Photo gallery"
        alt_base = html.escape(p["title"], quote=True)
        gallery_html = ""
        if gallery_files:
            shots = "".join(
                f'<a href="{root}assets/img/properties/gallery/{img_slug}/{f.name}" target="_blank" rel="noopener">'
                f'<img src="{root}assets/img/properties/gallery/{img_slug}/{f.name}" alt="{alt_base} — {gallery_h.lower()} {i}" loading="lazy" width="1400" height="933"></a>'
                for i, f in enumerate(gallery_files, 1)
            )
            gallery_html = f"""<section class="prop-gallery-wrap">
      <h2 class="micro" style="color:var(--alloy-dark);margin:0 0 14px">{gallery_h}</h2>
      <div class="prop-gallery">{shots}</div>
    </section>
"""
        body = f"""<main>
  <img class="prop-hero" src="{root}assets/img/properties/{img_slug}.webp" alt="{html.escape(p["title"], quote=True)}" width="1400" height="933">
  <div class="section">
    <p class="micro" style="margin:0 0 14px"><a href="{list_url}" style="text-decoration:none">{T[lang]["back_list"]}</a></p>
    <div class="section__head" style="margin-bottom:clamp(20px,3vw,36px)">
      <h1 class="section__title" style="max-width:22ch">{html.escape(p["title"])}</h1>
      <span class="prop-card__status micro{status_cls}" style="position:static">{p["status"]}</span>
    </div>
    <p class="prop-card__loc" style="font-size:16px;margin:-10px 0 30px">{html.escape(p["loc"])}</p>
    <div class="prop-layout">
      <div class="prop-desc">
        <h2 class="micro" style="color:var(--alloy-dark);margin:0 0 14px">{T[lang]["desc_h"]}</h2>
        {desc_paras}
      </div>
      <aside class="prop-facts">
        <h2>{T[lang]["facts"]}</h2>
        <p class="prop-facts__price">{p["price"]}</p>
        <dl>{dl}</dl>
        <a class="paper-cta" style="width:100%;margin-top:18px" href="mailto:{EMAIL}?subject={html.escape(p["title"], quote=True)}">{T[lang]["interest"]}</a>
      </aside>
    </div>
    {gallery_html}
  </div>
</main>
"""
        write(path, head(f"{p['title']} — LIVE-IN International", p["desc"][:200], root, lang)
              + nav(root, lang, url if False else ("/na-predaj/" if lang == "sk" else "/en/for-sale/"))
              + body + cta_band(root, lang) + footer(root, lang))


# ---------------------------------------------------------------- articles

ARTICLES = {
    "sk": [
        ("kratkodoby-vs-dlhodoby-prenajom", "kratkodoby-vs-dlhodoby-prenajom"),
        ("airbnb-v-bratislave-sprievodca", "airbnb-v-bratislave-sprievodca"),
        ("checklist-priprava-nehnutelnosti", "checklist-priprava-nehnutelnosti"),
    ],
    "en": [
        ("short-term-vs-long-term-rental", "en--short-term-vs-long-term-rental"),
        ("airbnb-in-bratislava-guide", "en--airbnb-in-bratislava-guide"),
        ("short-term-rent-checklist", "en--short-term-rent-checklist"),
    ],
}


EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FBFF\u2600-\u27BF\u2B00-\u2BFF\uFE0F\u200D\u20E3\u2934\u2935\u3297\u3299\u303D\u3030\u24C2\u2049\u203C]"
)


def strip_emoji(text):
    text = EMOJI_RE.sub("", text)
    text = re.sub(r"(<(?:h[1-4]|p|li|td|th)>)[\s\u00A0]+", r"\1", text)
    text = re.sub(r"[ \u00A0]{2,}", " ", text)
    return text.strip()


def art_url(lang, slug):
    return f"/clanky/{slug}/" if lang == "sk" else f"/en/articles/{slug}/"


def wrap_tables(html_content):
    return re.sub(r"(<table>.*?</table>)", r'<div class="table-wrap">\1</div>', html_content, flags=re.S)


def build_articles(lang, list_path, list_current, root_list):
    t = T[lang]
    meta = json.loads((C / "articles-meta.json").read_text())
    title = "Články" if lang == "sk" else "Articles"
    cards = ""
    for slug, key in ARTICLES[lang]:
        m = meta[key]
        cards += f"""<a class="article-card" href="{root_list}{art_url(lang, slug).lstrip('/')}">
  <span class="micro">{t["published"]}</span>
  <h2>{html.escape(strip_emoji(m["title"]))}</h2>
  <p>{html.escape(strip_emoji(m["desc"]))}</p>
  <span class="micro article-card__more">{t["read"]} →</span>
</a>
"""
    body = page_hero(root_list, "LIVE-IN International / Blog", title, t["articles_lead"], "frame-0022")
    body += f'<main class="section"><div class="article-grid">{cards}</div></main>'
    body += cta_band(root_list, lang)
    write(list_path, head(f"{title} — LIVE-IN International", t["articles_lead"], root_list, lang)
          + nav(root_list, lang, list_current) + body + footer(root_list, lang))

    for slug, key in ARTICLES[lang]:
        m = dict(meta[key])
        m["title"] = strip_emoji(m["title"])
        m["desc"] = strip_emoji(m["desc"])
        content = strip_emoji(wrap_tables((C / f"article-{key}.html").read_text()))
        root = "../../" if lang == "sk" else "../../../"
        others = "".join(
            f'<li><a href="{root}{art_url(lang, s).lstrip("/")}">{html.escape(strip_emoji(meta[k]["title"]))}</a></li>'
            for s, k in ARTICLES[lang] if s != slug
        )
        list_url = f"{root}clanky/" if lang == "sk" else f"{root}en/articles/"
        body = f"""<section class="page-hero">
  <div class="page-hero__film" style="background-image:url('{root}frames/desktop/frame-0022.webp')" aria-hidden="true"></div>
  <div class="article-head">
    <p class="page-hero__eyebrow micro"><a href="{list_url}" style="text-decoration:none">{title}</a> / {t["published"]}</p>
    <h1>{html.escape(m["title"])}</h1>
  </div>
</section>
<main class="section">
  <article class="prose">{content}</article>
  <div style="max-width:46rem;margin-top:clamp(40px,6vw,64px);padding-top:22px;border-top:1px solid var(--line-ink)">
    <h2 class="micro" style="color:var(--alloy-dark)">{t["more_articles"]}</h2>
    <ul style="padding-left:1.2em">{others}</ul>
  </div>
</main>
"""
        write(("clanky" if lang == "sk" else "en/articles") + f"/{slug}/index.html",
              head(f"{m['title']} — LIVE-IN International", m["desc"], root, lang)
              + nav(root, lang, "/clanky/" if lang == "sk" else "/en/articles/")
              + body + cta_band(root, lang) + footer(root, lang))


# ---------------------------------------------------------------- language map

LANG_MAP = {
    "/": "/en/",
    "/en/": "/",
    "/sluzby/": "/en/services/",
    "/en/services/": "/sluzby/",
    "/o-nas/": "/en/about-us/",
    "/en/about-us/": "/o-nas/",
    "/kontakt/": "/en/contact/",
    "/en/contact/": "/kontakt/",
    "/na-predaj/": "/en/for-sale/",
    "/en/for-sale/": "/na-predaj/",
    "/clanky/": "/en/articles/",
    "/en/articles/": "/clanky/",
}

# ---------------------------------------------------------------- EN homepage (derived from index.html)

HOME_TRANSLATIONS = [
    ('<html lang="sk">', '<html lang="en">'),
    ("LIVE-IN International — správa krátkodobých prenájmov v Bratislave a Košiciach. Zvýšte príjem z prenájmu o 20–30 %.",
     "LIVE-IN International — short-term rental management in Bratislava and Košice. Increase your rental income by 20–30%."),
    ("<title>LIVE-IN International — Váš byt. Vyšší výnos.</title>",
     "<title>LIVE-IN International — Your apartment. Higher yield.</title>"),
    ("Bratislava — ranné svetlo", "Bratislava — morning light"),
    ("5,04 s · 75 snímok", "5.04 s · 75 frames"),
    ("Pripravujem film", "Preparing film"),
    ("Načítava sa filmová sekvencia", "Loading the film sequence"),
    ("Správa krátkodobých prenájmov</div>", "Short-term rental management</div>"),
    ("Bratislava · Košice<br>Londýn od 2018", "Bratislava · Košice<br>London since 2018"),
    ("Film ovládaný skrolovaním", "A film driven by scroll"),
    ("Prémiový apartmán s výhľadom na Bratislavský hrad — záber sa pohybuje pri skrolovaní",
     "Premium apartment overlooking Bratislava Castle — the shot moves as you scroll"),
    ('data-label="Váš byt"', 'data-label="Your apartment"'),
    ("<span>Váš byt.<br>Vyšší výnos.</span>", "<span>Your apartment.<br>Higher yield.</span>"),
    ("<span>Prémiová správa krátkodobých prenájmov. Vy vlastníte, my sa staráme.</span>",
     "<span>Premium short-term rental management. You own it, we take care of it.</span>"),
    ('data-label="Výnos"', 'data-label="Yield"'),
    ("01 / Výnos", "01 / Yield"),
    ("<span>O&nbsp;20–30&nbsp;%<br>viac</span>", "<span>20–30&nbsp;%<br>more</span>"),
    ("<span>Krátkodobý prenájom s dynamickými cenami zarobí viac než klasický dlhodobý nájom.</span>",
     "<span>Short-term rental with dynamic pricing earns more than a classic long-term lease.</span>"),
    ("Dynamické ceny · Airbnb · Booking", "Dynamic pricing · Airbnb · Booking"),
    ('data-label="Správa"', 'data-label="Management"'),
    ("02 / Kompletná správa", "02 / Full management"),
    ("<span>Bez starostí</span>", "<span>Zero worries</span>"),
    ("<span>Hostia, upratovanie, údržba aj marketing. Provízia 17 %, žiadne skryté poplatky.</span>",
     "<span>Guests, cleaning, maintenance and marketing. 17 % commission, no hidden fees.</span>"),
    ("Komunikácia s hosťami 24/7", "Guest communication 24/7"),
    ('data-label="Istota"', 'data-label="Certainty"'),
    ("03 / Istota", "03 / Certainty"),
    ("<span>Garantovaný nájom</span>", "<span>Guaranteed rent</span>"),
    ("<span>Fixný mesačný príjem na 1 až 5 rokov. Nájomcom je LIVE-IN — žiadne prázdne mesiace.</span>",
     "<span>Fixed monthly income for 1 to 5 years. LIVE-IN is your tenant — no empty months.</span>"),
    ("Ideálne pre investorov a majiteľov v zahraničí", "Ideal for investors and owners abroad"),
    ('data-label="Ďalší krok"', 'data-label="Next step"'),
    ("Londýn 2018 → Slovensko 2023", "London 2018 → Slovakia 2023"),
    ("<span>Koľko zarobí ten váš?</span>", "<span>How much could yours earn?</span>"),
    ('aria-label="Vyžiadajte si bezplatnú analýzu výnosu vášho bytu"', 'aria-label="Request a free analysis of your apartment\'s yield"'),
    (">Bezplatná analýza</a>", ">Free analysis</a>"),
    (">Váš byt</span>", ">Your apartment</span>"),
    ("Výnos +0,0 %", "Yield +0.0 %"),
    ('`Výnos +${(effective * 30).toFixed(1).replace(".", ",")} %`', '`Yield +${(effective * 30).toFixed(1)} %`'),
    ("Skrolujte", "Scroll"),
    ("Byt, ktorý pracuje za vás.", "An apartment that works for you."),
    ("Od marketingu a dynamických cien po odovzdanie kľúčov — jeden partner pre celý prenájom v Bratislave a Košiciach.",
     "From marketing and dynamic pricing to key handover — one partner for the whole rental in Bratislava and Košice."),
    ("Krátkodobá správa</h3>", "Short-term management</h3>"),
    ("Kompletný manažment prenájmu s províziou 17 % z príjmu. Transparentný reporting.",
     "Complete rental management with a 17% commission on income. Transparent reporting."),
    ("Garantovaný nájom</h3>", "Guaranteed rent</h3>"),
    ("Fixný mesačný príjem na 1–5 rokov bez ohľadu na obsadenosť bytu.",
     "Fixed monthly income for 1–5 years regardless of occupancy."),
    ("Dlhodobá správa</h3>", "Long-term management</h3>"),
    ("Správa klasického dlhodobého prenájmu s províziou 10 %.",
     "Classic long-term rental management with a 10% commission."),
    ("Predaj nehnuteľností</h3>", "Real estate sales</h3>"),
    ("Predaj investičných bytov v Bratislave a Košiciach.",
     "Sale of investment apartments in Bratislava and Košice."),
    ("Obývačka apartmánu s výhľadom na Bratislavský hrad", "Apartment living room overlooking Bratislava Castle"),
    ("Detail sedačky a lampy pred panoramatickými oknami", "Sofa and lamp in front of panoramic windows"),
    ("Bratislavský hrad a mesto za oknami apartmánu", "Bratislava Castle and the city outside the windows"),
    ("Panoráma Dunaja a mosta SNP z apartmánu", "Danube and SNP Bridge panorama from the apartment"),
    ("Obývačka / modrá hodina", "Living room / blue hour"),
    ("Interiér", "Interior"),
    (">Hrad<", ">Castle<"),
    ("Nábrežie", "Riverfront"),
    ("Skúsenosti z Londýna. Výsledky na Slovensku.", "London experience. Slovak results."),
    ("LIVE-IN International pôsobí v Londýne od roku 2018 a na Slovensku od januára 2023. Napíšte nám na",
     "LIVE-IN International has operated in London since 2018 and in Slovakia since January 2023. Write to us at"),
    ("a zistite, koľko môže zarábať váš byt.", "and find out how much your apartment could earn."),
    ("Snímky sa nepodarilo načítať — obnovte stránku", "Frames failed to load — reload the page"),
    ("Filmové snímky sa nepodarilo načítať. Obnovte stránku.", "The film frames could not be loaded. Reload the page."),
    ("LIVE-IN International — expert na krátkodobé prenájmy. Čermeľská cesta 3, Košice · Bratislava · Londýn.",
     "LIVE-IN International — short-term rental experts. Čermeľská cesta 3, Košice · Bratislava · London."),
    ('aria-label="Informácie o stránke"', 'aria-label="Site information"'),
    ('aria-label="Hlavná navigácia"', 'aria-label="Main navigation"'),
    ('aria-label="Odkazy"', 'aria-label="Links"'),
    (">Rezervácie ↗</a>", ">Booking ↗</a>"),
    ('aria-label="LIVE-IN International — domov"', 'aria-label="LIVE-IN International — home"'),
    ("Ročný príjem z 3-izbového bytu v Starom Meste", "Annual income from a 3-room apartment in the Old Town"),
    ('aria-label="Porovnanie ročného príjmu: dlhodobý prenájom 16 800 eur, krátkodobý prenájom so správou LIVE-IN 21 930 eur — rozdiel 30,5 percenta."',
     'aria-label="Annual income comparison: long-term rental 16,800 euros, short-term rental managed by LIVE-IN 21,930 euros — a 30.5 percent difference."'),
    (">Dlhodobý prenájom</text>", ">Long-term rental</text>"),
    (">Krátkodobý s LIVE-IN</text>", ">Short-term with LIVE-IN</text>"),
    ("<title>Dlhodobý prenájom: 16 800 € ročne (1 400 € mesačne)</title>",
     "<title>Long-term rental: €16,800 per year (€1,400 per month)</title>"),
    ("<title>Krátkodobý prenájom so správou LIVE-IN: cca 21 930 € ročne pri 70 % obsadenosti</title>",
     "<title>Short-term rental managed by LIVE-IN: approx. €21,930 per year at 70% occupancy</title>"),
    ("Reálny prípad z praxe LIVE-IN: 3-izbový byt v Starom Meste Bratislavy, máj 2025. Krátkodobý prenájom pri priemernej obsadenosti 70 %.",
     "A real case from LIVE-IN's practice: a 3-room apartment in Bratislava's Old Town, May 2025. Short-term rental at an average occupancy of 70%."),
    ("<strong>+30,5 %</strong>", "<strong>+30.5 %</strong>"),
    ("Vyšší ročný príjem oproti dlhodobému prenájmu", "Higher annual income vs. a long-term lease"),
    ("Priemerná obsadenosť našich bytov v roku 2024", "Average occupancy of our apartments in 2024"),
    ("Provízia za kompletnú správu — žiadne skryté poplatky", "Commission for full management — no hidden fees"),
    (">Vyžiadajte si bezplatnú analýzu</a>", ">Request a free analysis</a>"),
]


def build_en_home():
    src = (ROOT / "index.html").read_text()
    for a, b in HOME_TRANSLATIONS:
        src = src.replace(a, b)
    # asset paths one level deeper
    src = src.replace('href="assets/', 'href="../assets/')
    src = src.replace('src="assets/', 'src="../assets/')
    src = src.replace('src="frames/', 'src="../frames/')
    src = src.replace('createFrameStore("frames/', 'createFrameStore("../frames/')
    # nav links (SK → EN targets), language switch back to SK root
    src = src.replace('href="sluzby/"', 'href="services/"').replace('href="na-predaj/"', 'href="for-sale/"')
    src = src.replace('href="clanky/"', 'href="articles/"').replace('href="o-nas/"', 'href="about-us/"')
    src = src.replace('href="kontakt/"', 'href="contact/"')
    src = src.replace('>Služby</a>', '>Services</a>').replace('>Na predaj</a>', '>For sale</a>')
    src = src.replace('>Články</a>', '>Articles</a>').replace('>O nás</a>', '>About</a>')
    src = src.replace('>Kontakt</a>', '>Contact</a>')
    src = src.replace('href="en/" class="lang-switch" lang="en">EN', 'href="../" class="lang-switch" lang="sk">SK')
    write("en/index.html", src)


# ---------------------------------------------------------------- main

def main():
    # SK
    build_services("sk", "sluzby/index.html", "/sluzby/", "../")
    build_about("sk", "o-nas/index.html", "/o-nas/", "../")
    build_contact("sk", "kontakt/index.html", "/kontakt/", "../")
    build_properties("sk", "na-predaj/index.html", "/na-predaj/", "../")
    build_articles("sk", "clanky/index.html", "/clanky/", "../")
    # EN
    build_services("en", "en/services/index.html", "/en/services/", "../../")
    build_about("en", "en/about-us/index.html", "/en/about-us/", "../../")
    build_contact("en", "en/contact/index.html", "/en/contact/", "../../")
    build_properties("en", "en/for-sale/index.html", "/en/for-sale/", "../../")
    build_articles("en", "en/articles/index.html", "/en/articles/", "../../")
    build_en_home()


if __name__ == "__main__":
    main()
