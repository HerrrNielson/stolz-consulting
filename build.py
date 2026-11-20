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
ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
ICON_PIN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true" focusable="false"><path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/></svg>'
ICON_PHONE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true" focusable="false"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/></svg>'
ICON_MAIL = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true" focusable="false"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>'


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
    """Escaped Text; *x* -> <em>x</em>."""
    return re.sub(r"\*(.+?)\*", r"<em>\1</em>", escape(text))


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
            out.append(f'<li class="reveal">{logo_img(key, lang, name, file)}<span class="logo-name">{esc(name)}</span></li>')
        else:
            out.append(f'<li class="reveal"><span class="logo-text">{esc(name)}</span></li>')
    return '<ul class="logo-grid" data-stagger>' + "".join(out) + "</ul>"


def marquee(key, lang, label, pause_label):
    items = [r for r in REFERENCES if r[1]]
    first = "".join(f"<li>{logo_img(key, lang, n, f)}</li>" for n, f in items)
    second = "".join(f'<li>{logo_img(key, lang, n, f, alt=False)}</li>' for n, f in items)
    return (f'<div class="marquee" data-marquee data-pause-label="{esc(pause_label)}">'
            f'<div class="marquee__viewport">'
            f'<ul class="marquee__track" aria-label="{esc(label)}">{first}</ul>'
            f'<ul class="marquee__track" aria-hidden="true">{second}</ul></div></div>')


def cta_block(key, lang):
    D = LANGS[lang]
    c = D["cta"]
    note = f'<p class="cta__note">{esc(c["text"])}</p>' if c.get("text") else ""
    return f"""
    <section class="section section--cta">
      <div class="container">
        <div class="cta reveal">
          <div class="cta__text">
            <p class="eyebrow">{esc(c['eyebrow'])}</p>
            <h2 class="h2">{em(c['h2'])}</h2>{note}
          </div>
          <a class="btn btn--primary" href="{rel(key, lang, 'kontakt')}"><span>{esc(c['btn'])}</span>{ARROW}</a>
        </div>
      </div>
    </section>"""


def page_hero(t, lead=True):
    lead_html = f'\n        <p class="lead reveal">{esc(t["lead"])}</p>' if lead and t.get("lead") else ""
    return f"""
    <section class="page-hero">
      <div class="page-hero__bg" aria-hidden="true"></div>
      <div class="container" data-stagger>
        <p class="eyebrow reveal">{esc(t['eyebrow'])}</p>
        <h1 class="h1 reveal">{em(t['h1'])}</h1>{lead_html}
      </div>
    </section>"""


# --------------------------------------------------------------------------
# Seiten – Inhalte kommen aus i18n/<sprache>.py
# --------------------------------------------------------------------------
def page_home(lang):
    k, D = "home", LANGS[lang]
    t, u = D["home"], D["ui"]
    a = lambda p: asset(k, lang, p)
    L = lambda to: rel(k, lang, to)
    fields = D["leistungen"]["fields"]
    n_refs = len(REFERENCES)

    def stat_value(v):
        return str(n_refs) if v == "{refs}" else str(len(fields)) if v == "{svc}" else v

    stats = "".join(
        f'<li class="reveal"><span class="stats__num"><span data-count="{stat_value(v)}" data-from="{f}">{stat_value(v)}</span></span>'
        f'<span class="stats__label">{esc(label)}</span></li>' for v, f, label in t["stats"])
    svc = "".join(
        f'<li class="reveal"><a class="svc-link" href="{L("leistungen")}#{f["id"]}">'
        f'<span class="svc-link__t">{esc(f["title"])}</span><span class="svc-link__d">{esc(f["teaser"])}</span>{ARROW}</a></li>'
        for f in fields)
    prose = "".join(f"<p>{esc(x)}</p>" for x in t["pr_p"])
    ref_lead = esc(t["ref_lead"].replace("{n}", str(n_refs)))
    return f"""
    <section class="hero">
      <div class="hero__bg" aria-hidden="true"><span class="hero__glow" data-parallax="0.12"></span><span class="hero__glow hero__glow--2" data-parallax="-0.06"></span></div>
      <div class="container hero__grid">
        <div class="hero__copy" data-stagger>
          <p class="eyebrow reveal">{esc(t['eyebrow'])}</p>
          <p class="hero__name reveal">Mag. Dr. Sabine Stolz, MSc</p>
          <h1 class="h1 h1--hero reveal">{em(t['h1'])}</h1>
          <div class="hero__text reveal">
            <p class="intro">{esc(t['intro'])}</p>
          </div>
          <blockquote class="hero__quote reveal">{esc(t['quote'])}</blockquote>
          <div class="hero__text reveal">
            <p>{esc(t['text'])}</p>
          </div>
          <div class="hero__actions reveal">
            <a class="btn btn--primary" href="{L('kontakt')}"><span>{esc(t['btn_primary'])}</span>{ARROW}</a>
            <a class="btn btn--outline" href="{L('profil')}"><span>{esc(t['btn_secondary'])}</span></a>
          </div>
        </div>
        <div class="hero__media" data-parallax="0.05">
          <div class="hero__frame">
            <picture>
              <source type="image/webp" srcset="{a('img/portrait.webp')}">
              <img src="{a('img/portrait.jpg')}" alt="{esc(t['portrait_alt'])}" width="313" height="474" fetchpriority="high" decoding="async">
            </picture>
          </div>
          <div class="hero__badge"><span>{esc(t['badge_k'])}</span><strong>{esc(t['badge_v'])}</strong></div>
        </div>
      </div>
    </section>

    <section class="stats" aria-label="{esc(t['stats_label'])}">
      <div class="container">
        <ul class="stats__list" data-stagger>{stats}</ul>
      </div>
    </section>

    <section class="section">
      <div class="container services__grid">
        <div class="reveal">
          <p class="eyebrow">{esc(t['svc_eyebrow'])}</p>
          <h2 class="h2">{em(t['svc_h2'])}</h2>
          <a class="link-arrow svc-all" href="{L('leistungen')}"><span>{esc(t['svc_all'])}</span>{ARROW}</a>
        </div>
        <ul class="service-list" data-stagger>{svc}</ul>
      </div>
    </section>

    <section class="section section--cream">
      <div class="container shortprofile">
        <div class="shortprofile__media reveal">
          <div class="frame">
            <picture>
              <source type="image/webp" srcset="{a('img/portrait.webp')}">
              <img src="{a('img/portrait.jpg')}" alt="{esc(t['portrait_alt'])}" width="313" height="474" loading="lazy" decoding="async">
            </picture>
          </div>
        </div>
        <div class="split__text" data-stagger>
          <p class="eyebrow reveal">{esc(t['pr_eyebrow'])}</p>
          <h2 class="h2 reveal">{esc(t['pr_h2'])}</h2>
          <div class="prose reveal">{prose}</div>
          <a class="link-arrow reveal" href="{L('profil')}"><span>{esc(t['ap_link'])}</span>{ARROW}</a>
        </div>
      </div>
    </section>

    <section class="section section--refs">
      <div class="container">
        <div class="section__head section__head--row reveal">
          <div>
            <p class="eyebrow">{esc(t['ref_eyebrow'])}</p>
            <h2 class="h2">{esc(t['ref_h2'])}</h2>
            <p class="section__lead">{ref_lead}</p>
          </div>
          <a class="link-arrow" href="{L('referenzen')}"><span>{esc(t['ref_all'])}</span>{ARROW}</a>
        </div>
      </div>
      {marquee(k, lang, u['marquee_label'], u['marquee_pause'])}
    </section>
{cta_block(k, lang)}"""


def page_leistungen(lang):
    k, D = "leistungen", LANGS[lang]
    t = D["leistungen"]
    chips = "".join(f'<li><a href="#{f["id"]}">{esc(f["title"])}</a></li>' for f in t["fields"])
    blocks = []
    for i, f in enumerate(t["fields"], 1):
        tags = ""
        if f.get("tags"):
            tags = (f'<p class="svc__tags-k">{esc(f["tags_k"])}</p>'
                    '<ul class="tags">' + "".join(f"<li>{esc(x)}</li>" for x in f["tags"]) + "</ul>")
        when = "".join(f"<li>{esc(x)}</li>" for x in f["when"])
        blocks.append(f"""
        <article class="svc reveal" id="{f['id']}" aria-labelledby="{f['id']}-h">
          <div class="svc__main">
            <p class="svc__num" aria-hidden="true">{i:02d}</p>
            <h3 class="h3" id="{f['id']}-h">{esc(f['title'])}</h3>
            <p class="svc__benefit">{esc(f['benefit'])}</p>
            {tags}
          </div>
          <div class="svc__when">
            <h4>{esc(t['when_k'])}</h4>
            <ul class="check-list">{when}</ul>
          </div>
        </article>""")
    steps = "".join(
        f'<li class="reveal"><span class="step__num" aria-hidden="true">{i}</span><h3>{esc(h)}</h3><p>{esc(p)}</p></li>'
        for i, (h, p) in enumerate(t["steps"], 1))
    return page_hero(t) + f"""

    <section class="section section--soft section--tight">
      <div class="container">
        <div class="note reveal">
          <p class="eyebrow">{esc(t['form_k'])}</p>
          <h2 class="h3">{esc(t['form_h'])}</h2>
          <p>{esc(t['form_p'])}</p>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section__head reveal">
          <p class="eyebrow">{esc(t['fields_eyebrow'])}</p>
          <h2 class="h2">{em(t['fields_h2'])}</h2>
          <ul class="chips" aria-label="{esc(t['fields_eyebrow'])}">{chips}</ul>
        </div>
        <div class="svc-list">{"".join(blocks)}
        </div>
      </div>
    </section>

    <section class="section section--cream">
      <div class="container">
        <div class="section__head reveal">
          <p class="eyebrow">{esc(t['process_eyebrow'])}</p>
          <h2 class="h2">{em(t['process_h2'])}</h2>
        </div>
        <ol class="steps" data-stagger>{steps}</ol>
      </div>
    </section>
{cta_block(k, lang)}"""


def page_profil(lang):
    k, D = "profil", LANGS[lang]
    t = D["profil"]
    a = lambda p: asset(k, lang, p)
    edu = "".join(f'<li class="reveal"><strong>{esc(x)}</strong><span>{esc(y)}</span></li>' for x, y in t["edu"])
    car = "".join(
        f'<li class="reveal{" is-current" if cur else ""}">'
        + (f'<span class="tl__period">{esc(period)}</span>' if period else "")
        + f'<strong>{esc(x)}</strong><span>{esc(y)}</span></li>'
        for x, y, period, cur in t["career"])
    tags = "".join(f"<li>{esc(x)}</li>" for x in t["tags"])
    chk = "".join(f'<li class="reveal">{esc(x)}</li>' for x in t["checks"])
    return page_hero(t) + f"""

    <section class="section">
      <div class="container profile">
        <aside class="profile__aside reveal">
          <div class="frame frame--portrait">
            <picture>
              <source type="image/webp" srcset="{a('img/portrait.webp')}">
              <img src="{a('img/portrait.jpg')}" alt="{esc(t['alt'])}" width="313" height="474" decoding="async">
            </picture>
          </div>
          <div class="profile__card">
            <p class="name">Mag. Dr. Sabine Stolz, MSc</p>
            <p class="role">{esc(t['role'])}</p>
            <dl>
              <dt>{esc(t['langs_k'])}</dt><dd>{esc(t['langs_v'])}</dd>
              <dt>{esc(t['since_k'])}</dt><dd>{esc(t['since_v'])}</dd>
            </dl>
          </div>
        </aside>

        <div class="profile__main">
          <div class="profile__block">
            <p class="eyebrow reveal">01</p>
            <h2 class="h3 reveal">{esc(t['h_edu'])}</h2>
            <ul class="edu-list" data-stagger>{edu}</ul>
          </div>
          <div class="profile__block">
            <p class="eyebrow reveal">02</p>
            <h2 class="h3 reveal">{esc(t['h_career'])}</h2>
            <ol class="timeline" data-stagger>{car}</ol>
          </div>
          <div class="profile__block">
            <p class="eyebrow reveal">03</p>
            <h2 class="h3 reveal">{esc(t['h_extra'])}</h2>
            <p class="svc__tags-k reveal">{esc(t['tags_k'])}</p>
            <ul class="tags reveal">{tags}</ul>
            <p class="svc__tags-k reveal">{esc(t['checks_k'])}</p>
            <ul class="check-list" data-stagger>{chk}</ul>
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
        <div class="section__head reveal"><p class="eyebrow">{esc(t['cases_eyebrow'])}</p><h2 class="h2">{esc(t['cases_h2'])}</h2></div>
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
        <div class="section__head reveal"><p class="eyebrow">{esc(t['quotes_eyebrow'])}</p><h2 class="h2">{esc(t['quotes_h2'])}</h2></div>
        <ul class="quote-list" data-stagger>{quotes}</ul>
      </div>
    </section>"""
    return out


def page_referenzen(lang):
    k, D = "referenzen", LANGS[lang]
    t = D["referenzen"]
    cards = "".join(
        f'<li class="reveal"><span class="label">{esc(t["label"])}</span><h3>{esc(h)}</h3><p>{esc(p)}</p></li>'
        for h, p in t["items"])
    groups = []
    for g in REF_GROUP_ORDER:
        items = [r for r in REFERENCES if REF_GROUP_OF.get(r[0], "weitere") == g]
        if g == "weitere":
            items = items + [(t["more"], None)]
        groups.append(f'<div class="ref-group"><h3 class="ref-group__h reveal">{esc(t["groups"][g])}</h3>{logo_grid(k, lang, items)}</div>')
    return page_hero(t) + f"""

    <section class="section section--soft">
      <div class="container">
        <ul class="expertise" data-stagger>{cards}</ul>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section__head reveal">
          <p class="eyebrow">{esc(t['e2'])}</p>
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
          <p class="role">Mag. Dr. Sabine Stolz, MSc · {esc(t['role'])}</p>
          <ul>
            <li>{ICON_PHONE}<div><span class="k">{esc(u['phone'])}</span><a href="{c['phone_href']}">{esc(u['phone_display'])}</a></div></li>
            <li>{ICON_MAIL}<div><span class="k">{esc(u['email'])}</span><a href="mailto:{c['email']}">{c['email']}</a></div></li>
            <li>{ICON_PIN}<div><span class="k">{esc(u['address'])}</span><address>{c['street']}<br>{c['city']}<br>{esc(u['country'])}</address></div></li>
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
    return page_hero(t, lead=False) + f"""
    <section class="section">
      <div class="container container--narrow legal">
        <h2>{esc(t['h_info'])}</h2>
        <address>Stolz Consulting<br>Mag. Dr. Sabine Stolz, MSc<br>{esc(t['role'])}<br>{c['street']}<br>{c['city']}<br>{esc(u['country'])}</address>
        <dl>
          <dt>{esc(t['k_phone'])}</dt><dd><a href="{c['phone_href']}">{esc(u['phone_display'])}</a></dd>
          <dt>{esc(t['k_email'])}</dt><dd><a href="mailto:{c['email']}">{c['email']}</a></dd>
          <dt>{esc(t['k_web'])}</dt><dd><a href="{DOMAIN}/">{DOMAIN}/</a></dd>
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
    return page_hero(t, lead=False) + f"""
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
    extra_css = "".join(f'\n  <link rel="stylesheet" href="{a(s)}">' for s in EXTRA_STYLES)
    extra_js = "".join(f'\n  <script src="{a(s)}" defer></script>' for s in EXTRA_SCRIPTS)
    ld = f'\n  <script type="application/ld+json">{json_ld(lang)}</script>' if key == "home" else ""
    others = "".join(
        f'<a href="{rel(key, lang, key, x)}" lang="{x}" hreflang="{x}">{esc(LANGS[x]["name"])}</a>'
        for x in CODES if x != lang)
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
  <meta name="twitter:card" content="summary_large_image">
  <meta name="theme-color" content="#221b11">
  <link rel="icon" type="image/svg+xml" href="{a('img/favicon.svg')}">
  {font_preloads(key, lang)}
  <link rel="stylesheet" href="{a('css/fonts.css')}">
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
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="nav"
              aria-label="{esc(u['menu_open'])}" data-label-open="{esc(u['menu_open'])}" data-label-close="{esc(u['menu_close'])}"><span></span></button>
      <nav class="nav" id="nav" aria-label="{esc(u['nav_label'])}">
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
          <p class="kicker">{esc(u['footer_kicker'])}</p>
          <p class="h2">{esc(u['footer_claim'])}</p>
        </div>
        <div class="site-footer__contact">
          <div><span class="k">{esc(u['phone'])}</span><a href="{c['phone_href']}">{esc(u['phone_display'])}</a></div>
          <div><span class="k">{esc(u['email'])}</span><a href="mailto:{c['email']}">{c['email']}</a></div>
          <div><span class="k">{esc(u['address'])}</span><address>{c['street']}<br>{c['city']}<br>{esc(u['country'])}</address></div>
        </div>
      </div>
      <div class="site-footer__bottom">
        <span>© <span data-year>2026</span> Stolz Consulting · Mag. Dr. Sabine Stolz, MSc</span>
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
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n", encoding="utf-8")


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
    print("geschrieben: sitemap.xml, robots.txt")
    for path, n in missing:
        print(f"OFFEN: {n}x [BITTE ERGAENZEN] in {path}")


if __name__ == "__main__":
    main()
