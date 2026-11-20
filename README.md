# Stolz Consulting – Website

Statische Neuauflage von [stolz-consulting.net](https://www.stolz-consulting.net/)
(Mag. Dr. Sabine Stolz, MSc) – vier Sprachen: Deutsch unter `/`, Englisch `/en/`,
Französisch `/fr/`, Russisch `/ru/`.

Inhalte, Farben und Bilder stammen von der bestehenden Website. EN/FR/RU sind
Übersetzungen der deutschen Originaltexte.
**FR und RU (insbesondere die rechtlichen Seiten) müssen vor dem Livegang von
Muttersprachler/innen bzw. einer Fachperson geprüft werden.**

## Seiten

| Seite | DE | EN | FR | RU |
|---|---|---|---|---|
| Start | `/` | `/en/` | `/fr/` | `/ru/` |
| Leistungen | `/leistungen/` | `/en/services/` | `/fr/services/` | `/ru/services/` |
| Profil | `/profil/` | `/en/profile/` | `/fr/profil/` | `/ru/profile/` |
| Referenzen | `/referenzen/` | `/en/references/` | `/fr/references/` | `/ru/references/` |
| Kontakt | `/kontakt/` | `/en/contact/` | `/fr/contact/` | `/ru/contact/` |
| Impressum | `/impressum/` | `/en/imprint/` | `/fr/mentions-legales/` | `/ru/imprint/` |
| Datenschutz | `/datenschutz/` | `/en/privacy/` | `/fr/confidentialite/` | `/ru/privacy/` |

## Struktur

```
build.py              Seitengenerator: HTML-Templates, Layout, hreflang, Sitemap
i18n/                 Texte – eine Datei je Sprache (de.py, en.py, fr.py, ru.py)
contact.php           Handler für das Kontaktformular (versendet per PHP mail())
assets/css/fonts.css  lokale @font-face-Regeln (Inter, Source Serif 4; latin, latin-ext, cyrillic)
assets/css/style.css  Stylesheet (Tokens, Komponenten, Motion, Responsive)
assets/js/main.js     Header, Menü, Sprachumschalter, Einblenden, Zähler, Parallax, Marquee, Formular
assets/fonts/         WOFF2-Schriften (selbst gehostet, DSGVO-freundlich)
assets/img/           Optimierte Bilder; original/ = unveränderte Downloads
sitemap.xml, robots.txt   werden von build.py erzeugt
index.html, */        Generierte Seiten (nicht direkt bearbeiten)
```

## Befehle

```bash
python build.py                 # alle Seiten, sitemap.xml und robots.txt neu erzeugen
python -m http.server 8080      # lokal ansehen: http://localhost:8080
```

Nach jeder Textänderung in `i18n/*.py` bzw. Template-Änderung in `build.py` neu bauen.
Es werden keine Zusatzpakete benötigt (nur Python 3).

## Texte und Sprachen

- Texte stehen ausschließlich in `i18n/<sprache>.py` (ein `DATA`-Dictionary je Sprache).
  `*Wort*` in Überschriften wird zu kursivem Gold-Akzent.
- **Neue Sprache:** `i18n/xx.py` nach dem Muster von `de.py` anlegen, in `i18n/__init__.py`
  in `LANGUAGES` eintragen, bauen. hreflang, Sitemap und Umschalter folgen automatisch.
- Französische Typografie (geschützte Leerzeichen vor `? ! : ;`) setzt `build.py` automatisch.
- Kennzahlen im Zahlenband: 2005 (seit), Anzahl `REFERENCES` in `build.py` und Anzahl der Leistungsfelder
  (`leistungen.fields` in den i18n-Dateien) werden automatisch eingesetzt (`{refs}`, `{svc}`, `{n}`). Keine weiteren Zahlen erfinden.

## Inhalte (Paket 2)

- **Leistungsseite:** Leistungsfelder (Titel, Nutzen, „Wann das hilfreich ist“, Fachtags) und die drei
  Arbeitsschritte stehen in `i18n/<sprache>.py` unter `leistungen`. Die Startseite verlinkt jedes Feld per Anker.
- **Referenzen:** `REFERENCES` in `build.py`; Gruppierung nur über `REF_GROUP_OF` (Bildung, Dienstleistung/Gesundheit –
  nur wo der Name es eindeutig hergibt, der Rest steht unter „Weitere Unternehmen“).
- **Fallbeispiele und Kundenstimmen:** Struktur vorbereitet (`CASE_STUDIES`, `TESTIMONIALS` in `build.py`,
  TODO-Kommentar). Solange die Listen leer sind, wird **nichts** ausgegeben. Nur mit echten, freigegebenen Inhalten füllen.
- **Rechtstexte:** Impressum (`impressum.todo_rows`, `sections`) und Datenschutz enthalten sichtbar markierte
  `[BITTE ERGÄNZEN]`-Platzhalter (gelb hinterlegt). `python build.py` meldet am Ende, wo noch welche offen sind.
  Alle Rechtstexte (alle Sprachen) sind **von einer Fachperson zu prüfen**.

## Erweiterungspunkte

- **Popup-Modul (Problem-Analyse):** eigenes Skript `assets/js/popup.js` in `EXTRA_SCRIPTS`,
  Styles in `EXTRA_STYLES`, Markup über `EXTRA_BODY` (alle in `build.py`).

## Kontaktformular

Das Formular sendet an `contact.php`, das die Anfrage an `office@stolz-consulting.net`
weiterleitet (Formularsprache DE/EN/FR/RU wird im Betreff vermerkt). Voraussetzung ist ein
Webspace mit PHP und funktionierendem Mailversand. Ist kein PHP verfügbar, öffnet sich als
Fallback das E-Mail-Programm des Besuchers mit der vorausgefüllten Nachricht.

Pflichtfelder: Name, E-Mail, Nachricht und Zustimmung zur Datenschutzerklärung (Checkbox mit Link). Spamschutz per
Honeypot-Feld `website`. `contact.php` validiert serverseitig, lehnt Zeilenumbrüche in einzeiligen Feldern ab
(Header-Injection) und antwortet als JSON (`ok`, `code`, `message`) in der Sprache des Formulars. Das Skript zeigt
klare Erfolgs-/Fehlermeldungen (Texte in `i18n/*.py` unter `kontakt`); eine Antwortzeit wird bewusst nicht zugesagt.

Noch offen: Mailversand auf dem Zielserver testen (`contact.php` wurde lokal nicht mit PHP ausgeführt).

## Design und Technik

- Farben: Creme `#f5f1ea`, Gold `#b88b4a` (Text auf Hell: `#7a5727`), Dunkelbraun `#221b11`.
- Schriften: Source Serif 4 (Überschriften), Inter (Fließtext) – **lokal gehostet**
  (`assets/fonts/`, `font-display: swap`, Preload der Latin-/Kyrillisch-Datei je Sprache).
  Es erfolgt keine Verbindung zu Google Fonts; die Datenschutzerklärung nennt das.
  Quelle: Google Fonts (SIL Open Font License).
- Bewegung: Intersection Observer, CSS-Scroll-Timeline (Fortschrittsbalken) und
  View Transitions (Seitenwechsel) als Progressive Enhancement. `prefers-reduced-motion`
  schaltet Animationen, Parallax, Marquee und Seitenübergang ab. Ohne JavaScript bleiben
  alle Inhalte sichtbar.
- Barrierefreiheit: Skip-Link, Landmarks, sichtbare Fokus-Stile, Pfeiltasten im
  Sprachumschalter, Menü mit Fokusfalle und Esc, Marquee pausierbar.
