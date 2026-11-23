# -*- coding: utf-8 -*-
"""
Stolz Consulting – statischer Seitengenerator (vier Sprachen: DE, EN, FR, RU).

Erzeugt alle HTML-Seiten sowie sitemap.xml und robots.txt. Nach jeder Änderung
einfach neu ausführen:

    python build.py

Wo liegt was?
  i18n/<sprache>.py   alle Texte je Sprache (Deutsch unter /, andere unter /<code>/)
  build.py            Seitenaufbau (HTML-Templates), Layout, Sitemap
  assets/             CSS, JS, Schriften, Bilder (HTML-Dateien nie direkt bearbeiten)

Erweiterungspunkte (siehe Markierungen "ERWEITERUNG" / "TODO" unten):
  * Fallbeispiele und Kundenstimmen: CASE_STUDIES / TESTIMONIALS befüllen (siehe unten) –
    bis dahin wird nichts davon ausgegeben.
  * Orientierungs-Check (Popup): assets/js/analyse.js + assets/css/analyse.css, Texte in
    i18n/analyse_<sprache>.py, Markup/JSON aus analyse_block() (siehe README).

Inhalte stammen von https://www.stolz-consulting.net/ (Stand Nov. 2026).
"""
import json
import re
import struct
from html import escape
from pathlib import Path

from i18n import DEFAULT_LANG, LANGUAGES
import mapdata  # Kartengeometrie (erzeugt von tools/make_map.py)

ROOT = Path(__file__).resolve().parent
DOMAIN = "https://www.stolz-consulting.net"
LANGS = {d["code"]: d for d in LANGUAGES}
CODES = [d["code"] for d in LANGUAGES]

CONTACT = {
    "phone_href": "tel:+436645302624",
    "email": "office@stolz-consulting.net",
    "street": "Brünngraben 10",
    "city": "8444 St. Andrä-Höch",
}

# ERWEITERUNG: Skripte/Styles/Markup, die auf jeder Seite geladen werden sollen
EXTRA_STYLES = ["css/analyse.css"]  # Orientierungs-Check (Popup)
EXTRA_SCRIPTS = ["js/analyse.js"]
EXTRA_BODY = ""                     # weiteres Markup vor </body>; das Popup-Markup erzeugt analyse_block()


# --------------------------------------------------------------------------
# WELTKARTE auf der Referenzseite (Inline-SVG, siehe README "Weltkarte")
# Orte hier ergaenzen: eine Zeile in MAP_PLACES. Nur belegte Orte eintragen!
#   id        eindeutiges Kuerzel (CSS-/ID-tauglich)
#   kind      "home" = Sitz, "abroad" = Auslandserfahrung
#   lon, lat  Position des Markers (Grad; ungefaehre Lage im Land bzw. in der Region, keine Stadtangabe)
#   iso       Laender, die auf der Karte golden eingefaerbt werden (ISO-3166-Alpha-2; nur Laender aus
#             mapdata.MAP_COUNTRIES; weitere: HIGHLIGHT in tools/make_map.py ergaenzen und neu erzeugen)
#   region    True = Region (z. B. Baltikum): Laender nur zart getoent, Marker nicht auf ein Land festgelegt
#   label     Beschriftung je Sprache
#   stations  belegende Stationen (Quelle: Profil, "Berufliche Laufbahn")
# --------------------------------------------------------------------------
MAP_PLACES = [
    dict(id="at", kind="home", lon=15.4, lat=46.8, iso=["AT"], region=False, stations=[],
         label=dict(de="Österreich", en="Austria", fr="Autriche", ru="Австрия")),
    dict(id="ru", kind="abroad", lon=45, lat=56, iso=["RU"], region=False, stations=["VAE AG", "AVL"],
         label=dict(de="Russland", en="Russia", fr="Russie", ru="Россия")),
    dict(id="baltic", kind="abroad", lon=24.5, lat=57.2, iso=["EE", "LV", "LT"], region=True, stations=["VAE AG"],
         label=dict(de="Baltikum", en="Baltic region", fr="Pays baltes", ru="Прибалтика")),
    dict(id="cn", kind="abroad", lon=104, lat=35, iso=["CN"], region=False, stations=["AVL"],
         label=dict(de="China", en="China", fr="Chine", ru="Китай")),
    dict(id="us", kind="abroad", lon=-98, lat=39, iso=["US"], region=False, stations=["AVL"],
         label=dict(de="USA", en="USA", fr="États-Unis", ru="США")),
    dict(id="fr", kind="abroad", lon=2.5, lat=46.6, iso=["FR"], region=False, stations=["AVL", "Ceram Catalysts"],
         label=dict(de="Frankreich", en="France", fr="France", ru="Франция")),
    dict(id="de", kind="abroad", lon=10.3, lat=51, iso=["DE"], region=False, stations=["Ceram Catalysts"],
         label=dict(de="Deutschland", en="Germany", fr="Allemagne", ru="Германия")),
]

# Zusaetzliche Dateien nur auf einzelnen Seiten: {Seitenschluessel: (Styles, Skripte)}
PAGE_EXTRA = {"referenzen": (["css/map.css"], ["js/map.js"])}

# Seiten ohne Orientierungs-Check (Popup und Einstiegsbutton)
NO_ANALYSE = {"impressum", "datenschutz", "kontakt"}

# Referenzen in der Reihenfolge des Originals; None = kein Logo vorhanden
REFERENCES = [
    ("ams - austriamicrosystems AG", "ams.svg"),
    ("ATB Austria Antriebstechnik AG", "atb.svg"),
    ("AVL List GmbH", "avl.png"),
    ("BFI Steiermark", "bfi.jpg"),
    ("Efkon AG", "efkon.jpeg"),
    ("FH Campus 02", "campus-02.jpeg"),
    ("FH Hamburg", "fh-hamburg.png"),
    ("Frauenthal Holding AG", "frauenthal.jpeg"),
    ("Kurzentrum Althofen GmbH", "kurzentrum-althofen.png"),
    ("Land- und forstwirtschaftliche Ausbildungsstätte Steiermark", None),
    ("Meadwestvaco GmbH", "meadwestvaco.png"),
    ("Pädagogische Hochschule Steiermark", "ph-steiermark.svg"),
    ("Saubermacher Dienstleistungs AG", "saubermacher.jpeg"),
    ("Security KAG", "security-kag.png"),
    ("VAE GmbH", "vae.png"),
    ("voestalpine AG", "voestalpine.png"),
    ("Universität Graz", "universitaet-graz.svg"),
    ("WIFI Steiermark", "wifi.png"),
    ("ZAT GmbH", None),
]

# Gruppierung der Referenzen – nur, wo sie sich eindeutig aus dem Namen ergibt
# (Hochschule/Universität/FH/Ausbildungsstätte/BFI/WIFI = Bildung; Kurzentrum, Dienstleistungs-AG
# = Dienstleistung/Gesundheit). Alles andere bleibt unter "weitere" (keine Branchen-Vermutungen).
REF_GROUP_OF = {
    "BFI Steiermark": "bildung", "FH Campus 02": "bildung", "FH Hamburg": "bildung",
    "Land- und forstwirtschaftliche Ausbildungsstätte Steiermark": "bildung",
    "Pädagogische Hochschule Steiermark": "bildung", "Universität Graz": "bildung", "WIFI Steiermark": "bildung",
    "Kurzentrum Althofen GmbH": "dienst", "Saubermacher Dienstleistungs AG": "dienst",
}
REF_GROUP_ORDER = ["bildung", "dienst", "weitere"]

# TODO(Inhalt): Fallbeispiele und Kundenstimmen – Struktur ist vorbereitet, aber absichtlich LEER.
# Es gibt derzeit keine freigegebenen Inhalte; solange die Listen leer sind, wird auf der Live-Seite
# nichts ausgegeben (kein Fake-Content). Befüllen nur mit echten, von den Kund/innen freigegebenen Inhalten:
#   CASE_STUDIES.append({"title": {"de": "...", "en": "...", "fr": "...", "ru": "..."},
#                        "text":  {"de": "...", ...},               # Ausgangslage / Vorgehen / Ergebnis
#                        "meta":  {"de": "Branche · Thema", ...}})
#   TESTIMONIALS.append({"quote": {"de": "...", ...}, "author": "Name, Funktion, Unternehmen"})
CASE_STUDIES = []
TESTIMONIALS = []

REQ = '<span class="req" aria-hidden="true">*</span>'
ROW_ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
ARROW = ""   # Buttons und Textlinks tragen keine Pfeile mehr; nur das Leistungsregister nutzt ROW_ARROW


# --------------------------------------------------------------------------
# Helfer
# --------------------------------------------------------------------------
def url_path(lang, key):
    """Pfad einer Seite relativ zur Domain, z. B. 'en/profile/' oder ''."""
    prefix = "" if lang == DEFAULT_LANG else lang + "/"
    return prefix + LANGS[lang]["slugs"][key]


def rel(from_key, lang, to_key, to_lang=None):
    """Relativer Link von einer Seite zu einer anderen."""
    src = url_path(lang, from_key)
    dst = url_path(to_lang or lang, to_key)
    return ("../" * src.count("/") + dst) or "./"


def asset(key, lang, path):
    return "../" * url_path(lang, key).count("/") + "assets/" + path


def em(text):
    """Escaped Text. Die *x*-Auszeichnung der Texte wird nicht mehr als Kursiv ausgegeben: Ueberschriften bleiben aufrecht."""
    return escape(text).replace("*", "")


def esc(text):
    return escape(text)


def fr_typo(html):
    """Französische Typografie: geschützte Leerzeichen vor ? ! : ; »."""
    html = re.sub(r"(?<=[^\s<>]) ([?!;:»])", " \\1", html)
    return html.replace("« ", "« ")


_dim_cache = {}


def img_size(rel_path):
    """(Breite, Höhe) eines Bildes aus dem Dateikopf (PNG, JPEG, SVG) – ohne Zusatzpakete."""
    if rel_path in _dim_cache:
        return _dim_cache[rel_path]
    p = ROOT / "assets" / rel_path
    data = p.read_bytes()
    w = h = None
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        w, h = struct.unpack(">II", data[16:24])
    elif data[:2] == b"\xff\xd8":
        i = 2
        while i < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            m = data[i + 1]
            if 0xC0 <= m <= 0xCF and m not in (0xC4, 0xC8, 0xCC):
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                break
            i += 2 + struct.unpack(">H", data[i + 2:i + 4])[0]
    elif p.suffix == ".svg":
        s = data.decode("utf-8", "ignore")
        vb = re.search(r'viewBox="[\d.\-]+[ ,]+[\d.\-]+[ ,]+([\d.]+)[ ,]+([\d.]+)"', s)
        if vb:
            w, h = float(vb.group(1)), float(vb.group(2))
        else:
            mw = re.search(r'<svg[^>]*\swidth="([\d.]+)', s)
            mh = re.search(r'<svg[^>]*\sheight="([\d.]+)', s)
            if mw and mh:
                w, h = float(mw.group(1)), float(mh.group(1))
    if not w or not h:
        raise ValueError(f"Bildgröße nicht ermittelbar: {rel_path}")
    _dim_cache[rel_path] = (round(w), round(h))
    return _dim_cache[rel_path]


def logo_img(key, lang, name, file, alt=True, lazy=True):
    w, h = img_size("img/referenzen/" + file)
    a = esc(name) if alt else ""
    ld = ' loading="lazy" decoding="async"' if lazy else ""
    return f'<img src="{asset(key, lang, "img/referenzen/" + file)}" alt="{a}" width="{w}" height="{h}"{ld}>'


def logo_grid(key, lang, items):
    out = []
    for name, file in items:
        if file:
            out.append(f'<li class="reveal">{logo_img(key, lang, name, file, alt=False)}<span class="logo-name">{esc(name)}</span></li>')
        else:
            out.append(f'<li class="reveal"><span class="logo-text">{esc(name)}</span></li>')
    return '<ul class="logo-grid" data-stagger>' + "".join(out) + "</ul>"


def marquee(key, lang, label):
    items = [r for r in REFERENCES if r[1]]
    first = "".join(f"<li>{logo_img(key, lang, n, f)}</li>" for n, f in items)
    second = "".join(f'<li>{logo_img(key, lang, n, f, alt=False)}</li>' for n, f in items)
    return (f'<div class="marquee" data-marquee>'
            f'<div class="marquee__viewport">'
            f'<ul class="marquee__track" aria-label="{esc(label)}">{first}</ul>'
            f'<ul class="marquee__track" aria-hidden="true">{second}</ul></div></div>')


def svg(inner, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<svg{c} viewBox="0 0 24 24" aria-hidden="true" focusable="false">{inner}</svg>'


# Eigene Strichgrafik-Icons (24er Raster, nur Leistungskarten); Klasse "ac" = Akzentlinie in Gold
SERVICE_ICONS = {
    "controlling": '<path d="M3 20h18"/><path d="M6 16v-4M11 16V9M16 16v-6"/><path class="ac" d="m5 7 5-3 4 2 5-3"/>',
    "finanzierung": '<ellipse cx="12" cy="6" rx="7" ry="3"/><path d="M5 6v6c0 1.7 3.1 3 7 3s7-1.3 7-3V6"/><path class="ac" d="M5 12v6c0 1.7 3.1 3 7 3s7-1.3 7-3v-6"/>',
    "international": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path class="ac" d="M12 3c3.2 3 3.2 15 0 18M12 3c-3.2 3-3.2 15 0 18"/>',
    "erp": '<rect x="3" y="4" width="7" height="7" rx="1.5"/><rect x="14" y="4" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><path class="ac" d="M14 17.5h7M17.5 14v7"/>',
    "training": '<path d="m2 9 10-5 10 5-10 5z"/><path d="M6 11.5V16c0 1.5 2.7 3 6 3s6-1.5 6-3v-4.5"/><path class="ac" d="M22 9v6"/>',
}
CHEVRON = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="m6 9 6 6 6-6"/></svg>'


def icon_box(inner):
    return f'<span class="icon">{svg(inner)}</span>'


def cta_block(key, lang):
    D = LANGS[lang]
    c = D["cta"]
    note = f'<p class="cta__note">{esc(c["text"])}</p>' if c.get("text") else ""
    return f"""
    <section class="section section--cta">
      <div class="container">
        <div class="cta reveal">
          <div class="cta__text">
            <h2 class="h2">{em(c['h2'])}</h2>{note}
          </div>
          <a class="btn btn--primary" href="{rel(key, lang, 'kontakt')}"><span>{esc(c['btn'])}</span></a>
        </div>
      </div>
    </section>"""


def page_hero(t, lead=True, plain=False):
    lead_html = f'\n        <p class="lead reveal">{esc(t["lead"])}</p>' if lead and t.get("lead") else ""
    cls = "page-hero page-hero--plain" if plain else "page-hero"
    return f"""
    <section class="{cls}">
      <div class="container" data-stagger>
        <h1 class="h1 reveal">{em(t['h1'])}</h1>{lead_html}
      </div>
    </section>"""


def steps_html(steps):
    return "".join(
        f'<li class="reveal"><span class="step__num" aria-hidden="true">{i}</span><h3>{esc(h)}</h3><p>{esc(p)}</p></li>'
        for i, (h, p) in enumerate(steps, 1))


# --------------------------------------------------------------------------
# Seiten – Inhalte kommen aus i18n/<sprache>.py
# --------------------------------------------------------------------------
def page_home(lang):
    k, D = "home", LANGS[lang]
    t, u, lt = D["home"], D["ui"], D["leistungen"]
    a = lambda p: asset(k, lang, p)
    L = lambda to: rel(k, lang, to)
    fields = lt["fields"]
    n_refs = len(REFERENCES)

    def stat_value(v):
        return str(n_refs) if v == "{refs}" else str(len(fields)) if v == "{svc}" else v

    stats = "".join(
        f'<li class="reveal"><span class="facts__num">{stat_value(v)}</span><span class="facts__label">{esc(label)}</span></li>'
        for v, _f, label in t["stats"])
    svc = "".join(
        f'<li class="reveal"><a class="svc-row" href="{L("leistungen")}#{f["id"]}"><span class="svc-row__n" aria-hidden="true">{i:02d}</span>'
        f'<span class="svc-row__t">{esc(f["title"])}</span><span class="svc-row__d">{esc(f["teaser"])}</span>'
        f'<span class="svc-row__go" aria-hidden="true">{ROW_ARROW}</span></a></li>'
        for i, f in enumerate(fields, 1))
    prose = "".join(f"<p>{esc(x)}</p>" for x in t["pr_p"])
    ref_lead = esc(t["ref_lead"].replace("{n}", str(n_refs)))
    return f"""
    <section class="hero">
      <div class="container hero__grid">
        <div class="hero__copy" data-stagger>
          <h1 class="h1 reveal">{em(t['h1'])}</h1>
          <p class="hero__sub reveal">{esc(t['intro'])}</p>
          <div class="hero__actions reveal">
            <a class="btn btn--primary" href="{L('kontakt')}"><span>{esc(t['btn_primary'])}</span></a>
            <a class="link-text" href="{L('leistungen')}"><span>{esc(t['svc_all'])}</span></a>
          </div>
        </div>
        <div class="hero__media"><div class="frame">
          <picture>
            <source type="image/webp" srcset="{a('img/portrait.webp')}">
            <img src="{a('img/portrait.jpg')}" alt="{esc(t['portrait_alt'])}" width="313" height="376" fetchpriority="high" decoding="async">
          </picture>
        </div></div>
      </div>
    </section>

    <section class="facts" aria-label="{esc(t['stats_label'])}">
      <div class="container">
        <ul class="facts__list" data-stagger>{stats}</ul>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section__head section__head--row reveal">
          <h2 class="h2">{em(t['svc_h2'])}</h2>
          <a class="link-text" href="{L('leistungen')}"><span>{esc(t['svc_all'])}</span></a>
        </div>
        <ul class="svc-index" data-stagger>{svc}</ul>
      </div>
    </section>

    <section class="section section--paper2">
      <div class="container">
        <div class="section__head reveal">
          <h2 class="h2">{em(lt['process_h2'])}</h2>
        </div>
        <ol class="steps" data-stagger>{steps_html(lt['steps'])}</ol>
      </div>
    </section>

    <section class="section">
      <div class="container shortprofile">
        <div class="shortprofile__head reveal">
          <h2 class="h2">{esc(t['pr_h2'])}</h2>
          <a class="link-text" href="{L('profil')}"><span>{esc(t['ap_link'])}</span></a>
        </div>
        <div class="prose reveal">{prose}</div>
        <blockquote class="pullquote reveal">{esc(t['quote'])}</blockquote>
      </div>
    </section>

    <section class="section section--paper2 section--refs">
      <div class="container">
        <div class="section__head section__head--row reveal">
          <div>
            <h2 class="h2">{esc(t['ref_h2'])}</h2>
            <p class="section__lead">{ref_lead}</p>
          </div>
          <a class="link-text" href="{L('referenzen')}"><span>{esc(t['ref_all'])}</span></a>
        </div>
      </div>
      {marquee(k, lang, u['marquee_label'])}
    </section>
{cta_block(k, lang)}"""


def page_leistungen(lang):
    k, D = "leistungen", LANGS[lang]
    t = D["leistungen"]
    blocks = []
    for i, f in enumerate(t["fields"]):
        tags = ""
        if f.get("tags"):
            tags = (f'<p class="k k--gap">{esc(f["tags_k"])}</p>'
                    '<ul class="tags">' + "".join(f"<li>{esc(x)}</li>" for x in f["tags"]) + "</ul>")
        when = "".join(f"<li>{esc(x)}</li>" for x in f["when"])
        opened = ""
        blocks.append(f"""
        <details class="acc reveal" id="{f['id']}"{opened}>
          <summary>{icon_box(SERVICE_ICONS[f['id']])}
            <span><span class="acc__t">{esc(f['title'])}</span><span class="acc__d">{esc(f['teaser'])}</span></span>
            <span class="acc__chev">{CHEVRON}</span></summary>
          <div class="acc__body">
            <div><p>{esc(f['benefit'])}</p>{tags}</div>
            <div class="acc__when"><p class="k">{esc(t['when_k'])}</p><ul class="check-list">{when}</ul></div>
          </div>
        </details>""")
    return page_hero(t) + f"""

    <section class="section section--tight">
      <div class="container">
        <div class="form-note reveal">
          <h2 class="h3">{esc(t['form_h'])}</h2>
          <p>{esc(t['form_p'])}</p>
        </div>
      </div>
    </section>

    <section class="section section--flush">
      <div class="container">
        <div class="acc-list" data-stagger>{"".join(blocks)}
        </div>
      </div>
    </section>

    <section class="section section--paper2">
      <div class="container">
        <div class="section__head reveal">
          <h2 class="h2">{em(t['process_h2'])}</h2>
        </div>
        <ol class="steps" data-stagger>{steps_html(t['steps'])}</ol>
      </div>
    </section>
{cta_block(k, lang)}"""


def page_profil(lang):
    k, D = "profil", LANGS[lang]
    t = D["profil"]
    a = lambda p: asset(k, lang, p)
    edu = "".join(f'<li class="reveal"><strong>{esc(x)}</strong><span>{esc(y)}</span></li>' for x, y in t["edu"])

    def career(items):
        return "".join(
            f'<li class="reveal{" is-current" if cur else ""}">'
            + (f'<span class="tl__period">{esc(period)}</span>' if period else "")
            + f'<strong>{esc(x)}</strong><span>{esc(y)}</span></li>'
            for x, y, period, cur in items)
    car = t["career"]
    glance = "".join(f'<li class="reveal"><strong>{esc(v)}</strong><span>{esc(lbl)}</span></li>' for v, lbl in
                     [(car[4][2], car[4][0]), (car[5][2], car[5][0]), (t["langs_v"], t["langs_k"])])
    tags = "".join(f"<li>{esc(x)}</li>" for x in t["tags"])
    seminars = next(f for f in D["leistungen"]["fields"] if f["id"] == "training")["tags"]
    sem = "".join(f"<li>{esc(x)}</li>" for x in seminars)
    return page_hero(t) + f"""

    <section class="section section--flush">
      <div class="container profile">
        <aside class="profile__aside reveal">
          <div class="frame"><picture>
            <source type="image/webp" srcset="{a('img/portrait.webp')}">
            <img src="{a('img/portrait.jpg')}" alt="{esc(t['alt'])}" width="313" height="376" decoding="async">
          </picture></div>
          <div class="profile__card">
            <p class="name">Mag. Dr. Sabine Stolz, MSc</p>
            <p class="role">{esc(t['role'])}</p>
          </div>
        </aside>

        <div class="profile__main">
          <ul class="glance" data-stagger>{glance}</ul>

          <div class="profile__block">
            <h2 class="h3 reveal">{esc(t['h_edu'])}</h2>
            <ul class="edu-list" data-stagger>{edu}</ul>
          </div>
          <div class="profile__block">
            <h2 class="h3 reveal">{esc(t['h_career'])}</h2>
            <h3 class="profile__sub reveal">{esc(t['career_g1'])}</h3>
            <ol class="timeline" data-stagger>{career(car[:4])}</ol>
            <h3 class="profile__sub reveal">{esc(t['career_g2'])}</h3>
            <ol class="timeline" data-stagger>{career(car[4:])}</ol>
          </div>
          <div class="profile__block">
            <h2 class="h3 reveal">{esc(t['h_extra'])}</h2>
            <p class="k reveal">{esc(t['tags_k'])}</p>
            <ul class="tags reveal">{tags}</ul>
            <p class="k k--gap reveal">{esc(t['checks_k'])}</p>
            <ul class="tags reveal">{sem}</ul>
          </div>
        </div>
      </div>
    </section>
{cta_block(k, lang)}"""


def render_case_studies(lang, t):
    """Fallbeispiele und Kundenstimmen – gibt NUR etwas aus, wenn CASE_STUDIES / TESTIMONIALS befüllt sind."""
    out = ""
    if CASE_STUDIES:
        cards = "".join(
            f'<li class="case reveal"><p class="label">{esc(c["meta"][lang])}</p><h3>{esc(c["title"][lang])}</h3>'
            f'<p>{esc(c["text"][lang])}</p></li>' for c in CASE_STUDIES)
        out += f"""
    <section class="section section--soft">
      <div class="container">
        <div class="section__head reveal"><h2 class="h2">{esc(t['cases_h2'])}</h2></div>
        <ul class="case-list" data-stagger>{cards}</ul>
      </div>
    </section>"""
    if TESTIMONIALS:
        quotes = "".join(
            f'<li class="quote-card reveal"><blockquote>{esc(q["quote"][lang])}</blockquote><cite>{esc(q["author"])}</cite></li>'
            for q in TESTIMONIALS)
        out += f"""
    <section class="section">
      <div class="container">
        <div class="section__head reveal"><h2 class="h2">{esc(t['quotes_h2'])}</h2></div>
        <ul class="quote-list" data-stagger>{quotes}</ul>
      </div>
    </section>"""
    return out


def world_map(lang, t):
    """Weltkarte als Inline-SVG + Legende. Ohne JS vollstaendig sichtbar (Progressive Enhancement)."""
    import math
    W, H = mapdata.MAP_W, mapdata.MAP_H

    def mill(lat):  # Projektion wie in tools/make_map.py
        return 1.25 * math.log(math.tan(math.pi / 4 + 0.4 * math.radians(lat)))
    y_top, k = mill(80.0), W / (2 * math.pi)

    def proj(lon, lat):
        return round((lon + 180) / 360 * W, 1), round((y_top - mill(lat)) * k, 1)
    home = next(p for p in MAP_PLACES if p["kind"] == "home")
    hx, hy = proj(home["lon"], home["lat"])
    countries, arcs, pins, legend = [], [], [], []
    ci = 0
    for i, pl in enumerate(MAP_PLACES):
        x, y = proj(pl["lon"], pl["lat"])
        name = pl["label"][lang]
        stations = ", ".join(pl["stations"]) if pl["stations"] else t["map_home_note"]
        tip = f"{name}: {stations}"
        for iso in pl["iso"]:
            ci += 1
            cls = "wmap__c wmap__c--region" if pl["region"] else "wmap__c"
            countries.append(f'<path class="{cls} s{min(ci, 12)}" d="{mapdata.MAP_COUNTRIES[iso]}"/>')
        if pl["kind"] == "abroad":
            dist = math.hypot(x - hx, y - hy)
            cx, cy = (hx + x) / 2, (hy + y) / 2 - max(10, dist * .28)
            d = f"M{hx:g},{hy:g} Q{cx:.1f},{cy:.1f} {x:g},{y:g}"
            arcs.append(
                f'<mask id="wmm-{pl["id"]}" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H:g}">'
                f'<path class="wmap__mask s{i}" d="{d}" pathLength="100"/></mask>'
                f'<path class="wmap__arc" d="{d}" mask="url(#wmm-{pl["id"]})"/>')
            pin = (f'<g class="wmap__pin s{i}" data-place="{pl["id"]}" data-tip="{esc(tip)}" tabindex="0" role="img" aria-label="{esc(tip)}">'
                   f'<g class="wmap__mk"><circle class="wmap__hit" cx="{x:g}" cy="{y:g}" r="13"/>'
                   f'<circle class="wmap__ring" cx="{x:g}" cy="{y:g}" r="7.5"/>'
                   f'<circle class="wmap__dot" cx="{x:g}" cy="{y:g}" r="3.8"/></g></g>')
        else:
            pin = (f'<g class="wmap__pin wmap__pin--home s{i}" data-place="{pl["id"]}" data-tip="{esc(tip)}" tabindex="0" role="img" aria-label="{esc(tip)}">'
                   f'<g class="wmap__mk"><circle class="wmap__hit" cx="{x:g}" cy="{y:g}" r="14"/>'
                   f'<circle class="wmap__pulse" cx="{x:g}" cy="{y:g}" r="11"/>'
                   f'<circle class="wmap__ring" cx="{x:g}" cy="{y:g}" r="10"/>'
                   f'<circle class="wmap__dot" cx="{x:g}" cy="{y:g}" r="5.6"/></g></g>')
        pins.append(pin)
        sym = "wmap__sym wmap__sym--home" if pl["kind"] == "home" else "wmap__sym"
        legend.append(
            f'<li data-place="{pl["id"]}"><span class="{sym}" aria-hidden="true"></span>'
            f'<span><strong>{esc(name)}</strong> <span class="wmap__st">{esc(stations)}</span></span></li>')
    pins.sort(key=lambda h: 'wmap__pin--home' in h)  # Sitz zuletzt zeichnen (liegt oben)
    return f"""
    <section class="section wmap-section" aria-labelledby="wmap-h">
      <div class="container">
        <div class="section__head reveal">
          <h2 class="h2" id="wmap-h">{em(t['map_h2'])}</h2>
          <p class="lead">{esc(t['map_lead'])}</p>
        </div>
        <figure class="wmap" data-wmap>
          <svg class="wmap__svg" viewBox="0 0 {W} {H:g}" role="group" aria-label="{esc(t['map_aria'])}" focusable="false">
            <!-- Kartengeometrie: Natural Earth 110m (Public Domain), vereinfacht, Miller-Projektion; erzeugt von tools/make_map.py -->
            <path class="wmap__land" d="{mapdata.MAP_LAND}" aria-hidden="true"/>
            <g aria-hidden="true">{"".join(countries)}</g>
            <g aria-hidden="true">{"".join(arcs)}</g>
            <g>{"".join(pins)}</g>
          </svg>
          <div class="wmap__tip" aria-hidden="true" hidden></div>
          <figcaption class="wmap__key">
            <span class="wmap__k"><span class="wmap__sym wmap__sym--home" aria-hidden="true"></span>{esc(t['map_key_home'])}</span>
            <span class="wmap__k"><span class="wmap__sym" aria-hidden="true"></span>{esc(t['map_key_abroad'])}</span>
          </figcaption>
        </figure>
        <ul class="wmap__list">{"".join(legend)}</ul>
      </div>
    </section>
"""


def page_referenzen(lang):
    k, D = "referenzen", LANGS[lang]
    t = D["referenzen"]
    cards = "".join(
        f'<li class="reveal"><h3>{esc(h)}</h3><p>{esc(p)}</p></li>'
        for h, p in t["items"])
    groups = []
    for g in REF_GROUP_ORDER:
        items = [r for r in REFERENCES if REF_GROUP_OF.get(r[0], "weitere") == g]
        if g == "weitere":
            items = items + [(t["more"], None)]
        groups.append(f'<div class="ref-group"><h3 class="ref-group__h reveal">{esc(t["groups"][g])}</h3>{logo_grid(k, lang, items)}</div>')
    return page_hero(t) + f"""

    <section class="section section--flush">
      <div class="container">
        <h2 class="h2 focus-h reveal">{esc(t['focus_h'])}</h2>
        <ul class="focus" data-stagger>{cards}</ul>
      </div>
    </section>
{world_map(lang, t)}
    <section class="section section--paper2">
      <div class="container">
        <div class="section__head reveal">
          <h2 class="h2">{esc(t['h2'])}</h2>
        </div>
        {"".join(groups)}
      </div>
    </section>
{render_case_studies(lang, t)}
{cta_block(k, lang)}"""


def page_kontakt(lang):
    k, D = "kontakt", LANGS[lang]
    t, u = D["kontakt"], D["ui"]
    c = CONTACT
    action = "../" * url_path(lang, k).count("/") + "contact.php"
    privacy = rel(k, lang, "datenschutz")
    consent = esc(t["consent"]).replace("{a}", f'<a href="{privacy}">').replace("{/a}", "</a>")
    return page_hero(t) + f"""

    <section class="section section--soft">
      <div class="container contact-grid">
        <form class="form reveal" action="{action}" method="post" novalidate data-contact-form
              data-mailto="{c['email']}" data-subject="{esc(t['subject'])}"
              data-msg-ok="{esc(t['ok'])}" data-msg-error="{esc(t['err'])}" data-msg-mailto="{esc(t['mailto'])}"
              data-msg-invalid="{esc(t['invalid'])}">
          <input type="hidden" name="lang" value="{lang}">
          <p class="form__note">{esc(t['req_note'])}</p>
          <div class="form__row">
            <div class="field">
              <label for="f-name">{esc(t['name'])} {REQ}</label>
              <input id="f-name" name="name" type="text" autocomplete="name" maxlength="120" required aria-required="true">
            </div>
            <div class="field">
              <label for="f-company">{esc(t['company'])} <span class="opt">{esc(t['opt'])}</span></label>
              <input id="f-company" name="company" type="text" autocomplete="organization" maxlength="160">
            </div>
          </div>
          <div class="form__row">
            <div class="field">
              <label for="f-email">{esc(t['email'])} {REQ}</label>
              <input id="f-email" name="email" type="email" autocomplete="email" maxlength="160" required aria-required="true">
            </div>
            <div class="field">
              <label for="f-phone">{esc(t['phone'])} <span class="opt">{esc(t['opt'])}</span></label>
              <input id="f-phone" name="phone" type="tel" autocomplete="tel" maxlength="60">
            </div>
          </div>
          <div class="field">
            <label for="f-message">{esc(t['msg'])} {REQ}</label>
            <textarea id="f-message" name="message" rows="6" maxlength="5000" required aria-required="true"></textarea>
          </div>
          <div class="hp" aria-hidden="true">
            <label for="f-website">Website</label>
            <input id="f-website" name="website" type="text" tabindex="-1" autocomplete="off">
          </div>
          <label class="check">
            <input type="checkbox" name="consent" value="1" required aria-required="true">
            <span>{consent}</span>
          </label>
          <button class="btn btn--primary" type="submit"><span>{esc(t['send'])}</span>{ARROW}</button>
          <p class="form__status" role="status" aria-live="polite"></p>
        </form>

        <aside class="contact-info reveal" aria-label="{esc(t['info'])}">
          <p class="name">Stolz Consulting</p>
          <p class="role">Mag. Dr. Sabine Stolz, MSc</p>
          <p class="role">{esc(t['role'])}</p>
          <ul>
            <li><span class="k">{esc(u['phone'])}</span><a href="{c['phone_href']}">{esc(u['phone_display'])}</a></li>
            <li><span class="k">{esc(u['email'])}</span><a href="mailto:{c['email']}">{c['email']}</a></li>
            <li><span class="k">{esc(u['address'])}</span><address>{c['street']}<br>{c['city']}<br>{esc(u['country'])}</address></li>
          </ul>
        </aside>
      </div>
    </section>"""


TODO_RE = re.compile(r"\[BITTE ERGÄNZEN[^\]]*\]")


def legal_text(text):
    """Escaped Text; [BITTE ERGÄNZEN …] wird als sichtbare Markierung (mark.todo) ausgegeben."""
    return TODO_RE.sub(lambda m: f'<mark class="todo">{m.group(0)}</mark>', esc(text))


def legal_sections(sections):
    out = []
    for h, paras in sections:
        out.append(f"<h2>{esc(h)}</h2>" + "".join(f"<p>{legal_text(p)}</p>" for p in paras))
    return "\n        ".join(out)


def page_impressum(lang):
    # RECHTLICH: von Fachperson zu prüfen (ECG § 5, GewO § 63, MedienG § 25). Fehlende Angaben stehen als
    # [BITTE ERGÄNZEN] in i18n/<sprache>.py (todo_rows, sections) und werden sichtbar markiert.
    D = LANGS[lang]
    t, u, c = D["impressum"], D["ui"], CONTACT
    todo = "".join(f'<dt>{esc(lbl)}</dt><dd>{legal_text("[BITTE ERGÄNZEN]")}</dd>' for lbl in t["todo_rows"])
    return page_hero(t, lead=False, plain=True) + f"""
    <section class="section">
      <div class="container container--narrow legal">
        <h2>{esc(t['h_info'])}</h2>
        <address>Stolz Consulting<br>Mag. Dr. Sabine Stolz, MSc<br>{esc(t['role'])}<br>{c['street']}<br>{c['city']}<br>{esc(u['country'])}</address>
        <dl>
          <dt>{esc(t['k_phone'])}</dt><dd><a href="{c['phone_href']}">{esc(u['phone_display'])}</a></dd>
          <dt>{esc(t['k_email'])}</dt><dd><a href="mailto:{c['email']}">{c['email']}</a></dd>
          <dt>{esc(t['k_owner'])}</dt><dd>{esc(t['v_owner'])}</dd>
          {todo}
        </dl>
        {legal_sections(t['sections'])}
      </div>
    </section>"""


def page_datenschutz(lang):
    # RECHTLICH: von Fachperson zu prüfen (DSGVO Art. 13/14, DSG, TKG 2021 § 165). Die Abschnitte zu Kontaktformular
    # und lokal gehosteten Schriften beschreiben den technischen Ist-Stand; der Hosting-Anbieter fehlt noch.
    D = LANGS[lang]
    t, u, c = D["datenschutz"], D["ui"], CONTACT
    return page_hero(t, lead=False, plain=True) + f"""
    <section class="section">
      <div class="container container--narrow legal">
        <h2>{esc(t['h_ctrl'])}</h2>
        <address>Stolz Consulting<br>Mag. Dr. Sabine Stolz, MSc<br>{c['street']}<br>{c['city']}<br>{esc(u['country'])}</address>
        <dl>
          <dt>{esc(t['k_email'])}</dt><dd><a href="mailto:{c['email']}">{c['email']}</a></dd>
          <dt>{esc(t['k_phone'])}</dt><dd><a href="{c['phone_href']}">{esc(u['phone_display'])}</a></dd>
        </dl>
        {legal_sections(t['sections'])}
      </div>
    </section>"""


# ERWEITERUNG: weitere Seiten hier eintragen – und in jeder i18n-Datei unter
# slugs/meta/nav ergänzen. Sitemap und Sprachumschalter folgen automatisch.
PAGES = {
    "home": page_home, "leistungen": page_leistungen, "profil": page_profil, "referenzen": page_referenzen,
    "kontakt": page_kontakt, "impressum": page_impressum, "datenschutz": page_datenschutz,
}


# --------------------------------------------------------------------------
# Layout
# --------------------------------------------------------------------------
def json_ld(lang):
    D = LANGS[lang]
    data = {
        "@context": "https://schema.org",
        "@type": "ProfessionalService",
        "name": "Stolz Consulting",
        "url": DOMAIN + "/",
        "image": DOMAIN + "/assets/img/og-image.jpg",
        "telephone": "+43 664 5302624",
        "email": CONTACT["email"],
        "founder": {"@type": "Person", "name": "Mag. Dr. Sabine Stolz, MSc"},
        "foundingDate": "2005",
        "address": {"@type": "PostalAddress", "streetAddress": CONTACT["street"],
                    "postalCode": "8444", "addressLocality": "St. Andrä-Höch", "addressCountry": "AT"},
    }
    return json.dumps(data, ensure_ascii=False)


def switcher(key, lang):
    D = LANGS[lang]
    items = []
    for code in CODES:
        d = LANGS[code]
        cur = ' aria-current="true"' if code == lang else ""
        items.append(f'<a class="lang__item" href="{rel(key, lang, key, code)}" lang="{code}" hreflang="{code}" '
                     f'aria-label="{esc(d["name"])}"{cur}>{d["short"]}</a>')
    return (f'<div class="lang" role="group" aria-label="{esc(D["ui"]["lang_label"])}" data-lang-switch>'
            + "".join(items) + "</div>")


def font_preloads(key, lang):
    names = ["inter-normal-latin", "source-serif-4-normal-latin"]
    if lang == "ru":
        names = ["inter-normal-cyrillic", "source-serif-4-normal-cyrillic"]
    return "\n  ".join(
        f'<link rel="preload" href="{asset(key, lang, "fonts/" + n + ".woff2")}" as="font" type="font/woff2" crossorigin>'
        for n in names)


ICON_COMPASS = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="9"/><path d="m15.5 8.5-2 5-5 2 2-5z"/></svg>'


def analyse_block(key, lang):
    """Einstiegsbutton + eingebettete Texte (JSON) für assets/js/analyse.js.
    Ohne JavaScript bleibt der Button ein normaler Link zur Kontaktseite."""
    if key in NO_ANALYSE:
        return ""
    D = LANGS[lang]
    t = D["analyse"]
    cfg = dict(t, lang=lang, action=asset(key, lang, "")[:-len("assets/")] + "contact.php",
               contact_url=rel(key, lang, "kontakt"), privacy_url=rel(key, lang, "datenschutz"), mail_to=CONTACT["email"])
    data = json.dumps(cfg, ensure_ascii=False).replace("</", "<\\/")
    return f"""<a class="analyse-fab" href="{rel(key, lang, 'kontakt')}" data-analyse-open aria-haspopup="dialog" title="{esc(t['fab_title'])}">{ICON_COMPASS}<span>{esc(t['fab'])}</span></a>
  <script type="application/json" id="analyse-data">{data}</script>"""


def layout(key, lang, body):
    D = LANGS[lang]
    u = D["ui"]
    title, desc = D["meta"][key]
    canonical = DOMAIN + "/" + url_path(lang, key)
    a = lambda path: asset(key, lang, path)
    L = lambda to: rel(key, lang, to)
    c = CONTACT

    cur = ' aria-current="page"'
    nav = "".join(
        f'<li><a class="nav__link" href="{L(k)}"{cur if k == key else ""}><span class="nav__num" aria-hidden="true">{i:02d}</span><span>{esc(label)}</span></a></li>'
        for i, (k, label) in enumerate(D["nav"], 1))
    alternates = "\n  ".join(
        f'<link rel="alternate" hreflang="{code}" href="{DOMAIN}/{url_path(code, key)}">' for code in CODES)
    alternates += f'\n  <link rel="alternate" hreflang="x-default" href="{DOMAIN}/{url_path(DEFAULT_LANG, key)}">'
    og_alt = "\n  ".join(f'<meta property="og:locale:alternate" content="{LANGS[x]["locale"]}">'
                         for x in CODES if x != lang)
    pg_css, pg_js = PAGE_EXTRA.get(key, ([], []))
    extra_css = "".join(f'\n  <link rel="stylesheet" href="{a(s)}">' for s in EXTRA_STYLES + pg_css)
    extra_js = "".join(f'\n  <script src="{a(s)}" defer></script>' for s in EXTRA_SCRIPTS + pg_js)
    ld = f'\n  <script type="application/ld+json">{json_ld(lang)}</script>' if key == "home" else ""
    others = "".join(   # alle vier Sprachen, die aktuelle ist markiert
        f'<a href="{rel(key, lang, key, x)}" lang="{x}" hreflang="{x}"' + (' aria-current="true"' if x == lang else "") + f'>{esc(LANGS[x]["name"])}</a>'
        for x in CODES)
    t_ = escape(title)
    d_ = escape(desc)

    html = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{t_}</title>
  <meta name="description" content="{d_}">
  <link rel="canonical" href="{canonical}">
  {alternates}
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Stolz Consulting">
  <meta property="og:locale" content="{D['locale']}">
  {og_alt}
  <meta property="og:title" content="{t_}">
  <meta property="og:description" content="{d_}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{DOMAIN}/assets/img/og-image.jpg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="624">
  <meta property="og:image:alt" content="Stolz Consulting, Mag. Dr. Sabine Stolz, MSc">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{t_}">
  <meta name="twitter:description" content="{d_}">
  <meta name="twitter:image" content="{DOMAIN}/assets/img/og-image.jpg">
  <meta name="theme-color" content="#fbf9f5">
  <link rel="icon" type="image/svg+xml" href="{a('img/favicon.svg')}">
  <link rel="apple-touch-icon" href="{a('img/apple-touch-icon.png')}">
  <link rel="manifest" href="{asset(key, lang, '')[:-len('assets/')]}site.webmanifest">
  {font_preloads(key, lang)}
  <link rel="stylesheet" href="{a('css/fonts.css')}">
  <link rel="stylesheet" href="{a('css/tokens.css')}">
  <link rel="stylesheet" href="{a('css/base.css')}">
  <link rel="stylesheet" href="{a('css/style.css')}">{extra_css}
  <script>document.documentElement.classList.add("js")</script>{ld}
</head>
<body class="page-{key}">
  <a class="skip-link" href="#main">{esc(u['skip'])}</a>
  <div class="progress" aria-hidden="true"><span></span></div>

  <header class="site-header">
    <div class="container site-header__inner">
      <a class="brand" href="{L('home')}" aria-label="{esc(u['home_label'])}">
        <span class="brand__name">Stolz Consulting</span>
        <span class="brand__sub">{esc(u['brand_sub'])}</span>
      </a>
      <button class="nav-toggle" type="button" popovertarget="nav" aria-controls="nav"
              aria-label="{esc(u['menu_open'])}" data-label-open="{esc(u['menu_open'])}" data-label-close="{esc(u['menu_close'])}"><span aria-hidden="true"></span></button>
      <nav class="nav" id="nav" popover="auto" aria-label="{esc(u['nav_label'])}">
        <ul class="nav__list">{nav}</ul>
        {switcher(key, lang)}
        <div class="nav__foot">
          <a class="nav__mail" href="mailto:{c['email']}">{c['email']}</a>
          <a class="nav__tel" href="{c['phone_href']}">{esc(u['phone_display'])}</a>
        </div>
      </nav>
    </div>
  </header>

  <main id="main" tabindex="-1">{body}
  </main>

  <footer class="site-footer">
    <div class="container">
      <div class="site-footer__top">
        <div class="site-footer__claim">
          <p class="site-footer__mark">{esc(u['footer_kicker'])}</p>
          <p>{esc(u['footer_claim'])}</p>
        </div>
        <div class="site-footer__contact">
          <div><span class="k">{esc(u['phone'])}</span><a href="{c['phone_href']}">{esc(u['phone_display'])}</a></div>
          <div><span class="k">{esc(u['email'])}</span><a href="mailto:{c['email']}">{c['email']}</a></div>
          <div><span class="k">{esc(u['address'])}</span><address>{c['street']}<br>{c['city']}<br>{esc(u['country'])}</address></div>
        </div>
      </div>
      <div class="site-footer__bottom">
        <span>© <span data-year>2026</span> Stolz Consulting, Mag. Dr. Sabine Stolz, MSc</span>
        <nav class="site-footer__links" aria-label="{esc(u['footer_nav'])}">
          <a href="{L('impressum')}">{esc(u['imprint'])}</a>
          <a href="{L('datenschutz')}">{esc(u['privacy'])}</a>
          {others}
        </nav>
      </div>
    </div>
  </footer>
  {analyse_block(key, lang)}
  {EXTRA_BODY}
  <script src="{a('js/main.js')}" defer></script>{extra_js}
</body>
</html>
"""
    return fr_typo(html) if lang == "fr" else html


def write_sitemap():
    urls = []
    for key in PAGES:
        for lang in CODES:
            loc = f"{DOMAIN}/{url_path(lang, key)}"
            alts = "".join(
                f'\n    <xhtml:link rel="alternate" hreflang="{x}" href="{DOMAIN}/{url_path(x, key)}"/>' for x in CODES)
            alts += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{DOMAIN}/{url_path(DEFAULT_LANG, key)}"/>'
            prio = "1.0" if key == "home" else ("0.3" if key in ("impressum", "datenschutz") else "0.8")
            urls.append(f"  <url>\n    <loc>{loc}</loc>{alts}\n    <priority>{prio}</priority>\n  </url>")
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
           + "\n".join(urls) + "\n</urlset>\n")
    (ROOT / "sitemap.xml").write_text(xml, encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /contact.php\n\nSitemap: {DOMAIN}/sitemap.xml\n", encoding="utf-8")


NOT_FOUND = {  # 404-Seite: sprachneutral, alle vier Sprachen untereinander (Hauptpfade absolut, da beliebig tief aufrufbar)
    "de": ("Seite nicht gefunden", "Diese Adresse gibt es nicht (mehr). Bitte gehen Sie zur Startseite.", "Zur Startseite", "/"),
    "en": ("Page not found", "This address does not exist (any more). Please go to the home page.", "Go to home page", "/en/"),
    "fr": ("Page introuvable", "Cette adresse n’existe pas (ou plus). Veuillez retourner à la page d’accueil.", "Page d’accueil", "/fr/"),
    "ru": ("Страница не найдена", "Такого адреса нет (или больше нет). Пожалуйста, перейдите на главную страницу.", "На главную", "/ru/"),
}


def write_404():
    blocks = "".join(
        f'<div class="nf__item" lang="{c}"><h2 class="h3">{esc(v[0])}</h2><p>{esc(v[1])}</p>'
        f'<a class="btn {"btn--primary" if c == "de" else "btn--outline"}" href="{v[3]}"><span>{esc(v[2])}</span>{ARROW}</a></div>'
        for c, v in NOT_FOUND.items())
    pre = "\n  ".join(
        f'<link rel="preload" href="/assets/fonts/{n}.woff2" as="font" type="font/woff2" crossorigin>'
        for n in ["inter-normal-latin", "source-serif-4-normal-latin"])
    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>404: Seite nicht gefunden, Stolz Consulting</title>
  <meta name="robots" content="noindex">
  <meta name="description" content="Seite nicht gefunden. Page not found. Page introuvable. Страница не найдена.">
  <meta name="theme-color" content="#fbf9f5">
  <link rel="icon" type="image/svg+xml" href="/assets/img/favicon.svg">
  {pre}
  <link rel="stylesheet" href="/assets/css/fonts.css">
  <link rel="stylesheet" href="/assets/css/tokens.css">
  <link rel="stylesheet" href="/assets/css/base.css">
  <link rel="stylesheet" href="/assets/css/style.css">
</head>
<body class="page-404">
  <a class="skip-link" href="#main">Zum Inhalt springen</a>
  <header class="site-header">
    <div class="container site-header__inner">
      <a class="brand" href="/" aria-label="Stolz Consulting"><span class="brand__name">Stolz Consulting</span><span class="brand__sub">Mag. Dr. Sabine Stolz, MSc</span></a>
    </div>
  </header>
  <main id="main" tabindex="-1">
    <section class="page-hero page-hero--plain">
      <div class="container">
        <h1 class="h1">404: Seite nicht gefunden, page not found</h1>
      </div>
    </section>
    <section class="section">
      <div class="container nf">{blocks}</div>
    </section>
  </main>
  <footer class="site-footer"><div class="container"><div class="site-footer__bottom">
    <span>© Stolz Consulting, Mag. Dr. Sabine Stolz, MSc</span>
    <nav class="site-footer__links" aria-label="Sprachen / Languages"><a href="/" lang="de" hreflang="de">Deutsch</a><a href="/en/" lang="en" hreflang="en">English</a><a href="/fr/" lang="fr" hreflang="fr">Français</a><a href="/ru/" lang="ru" hreflang="ru">Русский</a></nav>
  </div></div></footer>
</body>
</html>
"""
    (ROOT / "404.html").write_text(html, encoding="utf-8")
    print("geschrieben: 404.html")


def main():
    missing = []
    for key, fn in PAGES.items():
        for lang in CODES:
            body = fn(lang)
            if lang == "fr":
                body = fr_typo(body)
            out = ROOT / url_path(lang, key) / "index.html"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(layout(key, lang, body), encoding="utf-8")
            print("geschrieben:", out.relative_to(ROOT))
            todos = out.read_text(encoding="utf-8").count('<mark class="todo">')
            if todos:
                missing.append((str(out.relative_to(ROOT)), todos))
    write_sitemap()
    write_404()
    print("geschrieben: sitemap.xml, robots.txt")
    for path, n in missing:
        print(f"OFFEN: {n}x [BITTE ERGAENZEN] in {path}")


if __name__ == "__main__":
    main()
