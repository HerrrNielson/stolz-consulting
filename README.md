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
assets/css/tokens.css Design-Tokens (Farben, Schriften, Skalen); base.css Basisregeln
assets/css/style.css  Stylesheet (Komponenten, Motion, Responsive)
mapdata.py            Kartengeometrie (erzeugt von tools/make_map.py, nicht von Hand bearbeiten)
tools/make_map.py     erzeugt mapdata.py aus Natural-Earth-Daten
assets/css/map.css, assets/js/map.js   Weltkarte (nur auf der Referenzseite geladen)
assets/js/main.js     Header, Menü, Sprachumschalter, Einblenden, Akkordeon-Anker, Logo-Laufband (Hover-Pause), Formular
assets/fonts/         WOFF2-Schriften (selbst gehostet, DSGVO-freundlich)
assets/img/           Optimierte Bilder; original/ = unveränderte Downloads
sitemap.xml, robots.txt, 404.html   werden von build.py erzeugt
site.webmanifest      Web-App-Manifest (Name, Farben, Icons)
.htaccess             Apache: HTTPS/www-Umleitung, Sicherheits-Header (CSP), Caching, 404
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
  `*Wort*` in Überschriften bleibt als Auszeichnung im Text erlaubt, wird aber als normaler Text ausgegeben.
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

## Weltkarte (Referenzseite)

Auf `/referenzen/` (und `/en/references/`, `/fr/references/`, `/ru/references/`) zeigt eine Inline-SVG-Weltkarte, wo Auslandserfahrung besteht:
Sitz Österreich (Ring-Marker mit sanftem Puls), Auslandserfahrung in Russland, Baltikum, China, USA, Frankreich, Deutschland (Punkt-Marker,
gestrichelte Bögen vom Sitz). Darunter eine Legende/Liste (auch für Screenreader und Mobil). Keine externen Bibliotheken oder Requests.

- **Orte ergänzen:** `MAP_PLACES` oben in `build.py` – ein Eintrag je Ort (`id`, `kind` "home"/"abroad", `lon`/`lat`, `iso`, `region`,
  `label` in DE/EN/FR/RU, `stations`). Nur belegte Orte eintragen. Ein Land, das noch nicht in `HIGHLIGHT` (`tools/make_map.py`) steht,
  dort ergänzen und `python tools/make_map.py <ne_110m_admin_0_countries.geojson>` ausführen (erzeugt `mapdata.py`), dann `python build.py`.
  Die Marker stehen nur ungefähr im Land bzw. in der Region (keine Stadtangabe). Das Baltikum ist eine Region (Estland/Lettland/Litauen
  zart getönt), nicht auf ein Land festgelegt.
- **Belege (Stand Nov. 2026, Profil „Berufliche Laufbahn“, in `i18n/de.py`):** VAE AG – Russland, Baltikum; AVL – Russland, China, USA, Frankreich;
  Ceram Catalysts – Frankreich, Deutschland. Auf den öffentlichen Seiten /profil/ und /referenzen/ werden keine weiteren Orte als Stationen genannt
  (Steiermark/Graz/Hamburg stehen nur in Namen von Kunden und sind bewusst nicht aufgenommen).
- **Texte:** `map_*`-Schlüssel unter `referenzen` in `i18n/<sprache>.py`; Überschrift „Auslandserfahrung auf drei Kontinenten“ (Europa, Asien/China, Nordamerika/USA).
- **Quelle/Lizenz der Geometrie:** Natural Earth, `ne_110m_admin_0_countries` (Public Domain, naturalearthdata.com), vereinfacht
  (Douglas-Peucker), Miller-Projektion, Ausschnitt 56° S – 80° N; Frankreich ohne Überseegebiete. Hinweis steht auch als Kommentar im SVG.
- **Animation:** beim Einscrollen (Intersection Observer): Länder blenden gestaffelt ein, Bögen werden gezeichnet (`stroke-dashoffset` auf einer Maske),
  Marker „poppen“ auf, Ring am Sitz pulsiert 3×, danach Ruhe. `prefers-reduced-motion` und ohne JavaScript: fertige statische Karte.
  Staffelung über Klassen `.s0`–`.s12`, keine Inline-Styles (CSP); der Tooltip wird per CSSOM positioniert.
- **Bedienung:** Hover, Tastaturfokus (Tab) oder Tippen auf einen Marker zeigt „Ort: Stationen“; Esc/Klick daneben schließt. Auf Mobil sind die Marker vergrößert.
- **Ungeprüft:** Screenreader, echte Touch-Geräte, emuliertes `prefers-reduced-motion` im Browser (nur per Code/CSS geprüft), Safari.

## Erweiterungspunkte

- Weitere Skripte/Styles/Markup für alle Seiten: `EXTRA_SCRIPTS`, `EXTRA_STYLES`, `EXTRA_BODY` in `build.py`.

## Orientierungs-Check (Popup, Paket 3)

Dezenter Dialog „Orientierungs-Check“ in 4 Schritten: Thema (Mehrfachauswahl, „Noch unklar“ schließt andere aus) →
Folgefrage zum Thema + optional Unternehmensgröße → kurze, allgemeine Rückmeldung → Kontakt (Name, E-Mail, optional
Telefon/Nachricht, Datenschutz-Checkbox) → Erfolgs- bzw. Fehleransicht. Ziel ist ein *unverbindliches Orientierungsgespräch*
(kein „gratis“, kein Countdown, keine Knappheit).

- **Dateien:** `assets/js/analyse.js`, `assets/css/analyse.css`, Texte in `i18n/analyse_<de|en|fr|ru>.py`
  (von `build.py` als JSON `#analyse-data` je Seite eingebettet – im JS stehen keine Texte), `analyse_block()` in `build.py`,
  Handler `contact.php` (`source=analyse`).
- **Auslöser:** frühestens nach 40 s **oder** ca. 50 % Scrolltiefe (was zuerst eintritt), nur einmal pro Besuch
  (`sessionStorage` `sc-analyse-shown`), nach dem Schließen 14 Tage Pause (`localStorage` `sc-analyse-closed`).
  Nicht auf Impressum, Datenschutz und Kontakt (`NO_ANALYSE` in `build.py`). Dauerhafter Einstieg: Button unten rechts
  „Orientierungsgespräch“ (ohne JavaScript ein Link zur Kontaktseite); er öffnet den Dialog immer.
- **Sperre zurücksetzen (wichtig beim Testen):** Nach dem Schließen gilt 14 Tage Ruhe, pro Besuch öffnet sich der Dialog nur einmal. Wer lokal getestet und ihn geschlossen hat, sieht ihn deshalb nicht mehr automatisch. Zurücksetzen: URL `?analyse=reset` aufrufen, oder Konsole `StolzAnalyse.reset()`, oder `sessionStorage.removeItem("sc-analyse-shown"); localStorage.removeItem("sc-analyse-closed")`. In einem Hintergrund-Tab wartet der Auslöser, bis der Tab sichtbar ist.
- **Größen-Kacheln:** Umbruchstelle per `|` im Label (`sizes` in `analyse_<sprache>.py`, z. B. `Kleinst|unternehmen`); ab 3 Spalten (>600 px) wird dort umgebrochen (mit Bindestrich), einspaltig nicht.
- **Testen:** `?analyse=now` öffnet sofort (ignoriert die Speicherregeln), `?analyse=reset` löscht die Einträge;
  in der Konsole `StolzAnalyse.open()` / `StolzAnalyse.reset()`. Werte (40 s, 0,5, 14 Tage) stehen oben in `analyse.js`.
- **Verhalten/Barrierefreiheit:** `role="dialog"`, `aria-modal`, Fokusfalle, Hintergrund `inert`, Scroll-Lock, Schließen per
  X/ESC/Klick auf den Hintergrund, Fokus zurück an den Auslöser, Fortschrittsanzeige (`role="progressbar"`), Zurück-Button,
  Auswahl über echte Checkboxen/Radios, `prefers-reduced-motion`, ab 600 px Breite zentriert, darunter Bottom-Sheet (getestet bis 320 px).
- **Datenschutz:** keine Tracker, keine Cookies, keine externen Dienste. Antworten liegen nur im Arbeitsspeicher und gehen
  erst beim Absenden an `contact.php`. Die Datenschutzseite hat in allen Sprachen einen Abschnitt dazu (rechtlich zu prüfen).
- **Mail:** `contact.php` übersetzt die IDs über Whitelists (`ANALYSE_TOPICS/PHASES/SIZES`) in einen übersichtlichen Block
  „Orientierungs-Check“; bei `source=analyse` ist die Nachricht optional. Neue Themen: in `analyse_<sprache>.py` (alle 4) und
  in der Whitelist ergänzen.
- **Ungeprüft:** echter Mailversand und `php -l` (PHP lokal nicht installiert); FR/RU-Texte brauchen Muttersprachler/innen-Prüfung.

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

Designsystem „Ledger“ (Hallmark-Redesign, `design.md`): die Farbwelt der ursprünglichen Website (Weiß, ein Beige, Gold, warmes Dunkelbraun),
neu komponiert. Alle Tokens in `assets/css/tokens.css`, Basisregeln in `assets/css/base.css`, Seitenstile in `assets/css/style.css`
(die ersten Zeilen sind der Hallmark-Stempel mit Waivern).

- **Farben:** Grund `#fbf9f5`, Beige `#f5f1ea` (Wechselflächen, Footer), dunkleres Beige `#e9dfcd` (Chips), Gold `#b88b4a` (Flächen, Linien),
  `#8f6934` (Hover, große Zahlen), `#7a5727` (Gold als Text), Dunkelbraun `#2a2118` (Text, Schlussband). Keine Verläufe, keine Glanzeffekte.
  Alte Tokennamen (`--gold`, `--paper`, `--ink` …) bleiben als Aliase für `analyse.css` und `map.css`.
- **Komposition:** Hero mit Porträt rechts, Kennzahlen als Hauptbuch (eine Zeile je belegter Zahl), Leistungen als nummeriertes Register,
  Vorgehen in drei Spalten, Kurzprofil mit großem Zitat, Referenzen-Laufband, dunkles Schlussband mit der einen Handlung.
  Keine Eyebrows, keine kursiven Wörter in Überschriften (`*Wort*` in den Texten wird als normaler Text ausgegeben), keine Pfeile an Links.
- **Buttons:** ein einziger Primärstil (flaches Gold), Sekundär als Textlink oder Outline; kein Lift, kein Glanz, kein Magnet-Effekt.
- **Porträt:** Klasse `.frame`, Format 5:6, feine versetzte Goldlinie.
- **Schriften:** Source Serif 4 (Überschriften, Gewicht 400) und Inter (Text), lokal gehostet (`assets/fonts/`, Kyrillisch für RU), keine Verbindung zu Google Fonts.
- **Umbrüche:** keine automatische Silbentrennung, `text-wrap: balance` bzw. `pretty`, `clamp()`-Schriftgrößen.
- **Bewegung:** nur kurzes, leises Einblenden (Intersection Observer), Fortschrittslinie, View Transitions als Progressive Enhancement.
  `prefers-reduced-motion` schaltet alles ab; ohne JavaScript bleiben alle Inhalte sichtbar.
- **CSP:** keine Inline-Styles im HTML (`style-src 'self'`); das Inline-Skript im `<head>` ist unverändert (Hash in `.htaccess`).
- Barrierefreiheit: Skip-Link, Landmarks, sichtbare Fokus-Stile, Pfeiltasten im Sprachumschalter, Menü als natives Popover,
  Logo-Laufband pausiert bei Hover und Fokus und steht bei `prefers-reduced-motion` still, Akkordeons nativ per Tastatur bedienbar.

## Veröffentlichen

**Voraussetzungen:** Webspace mit PHP (für `contact.php` und `mail()`), HTTPS-Zertifikat, Apache mit
`mod_rewrite`, `mod_headers`, `mod_expires` (bei den meisten Anbietern Standard).

1. `python build.py` ausführen und den **gesamten Ordnerinhalt** per (S)FTP in das Web-Root der Domain hochladen
   (`.htaccess` nicht vergessen – versteckte Datei). `build.py`, `i18n/`, `README.md` werden vom Server nicht
   ausgeliefert (Sperre in `.htaccess`), müssen aber nicht hochgeladen werden.
2. **Domain/DNS prüfen:** `www.stolz-consulting.net` und `stolz-consulting.net` müssen auf den neuen Webspace zeigen;
   das Zertifikat muss **beide** Namen abdecken. `.htaccess` leitet `http://` und die Adresse ohne `www` per 301 auf
   `https://www.stolz-consulting.net` um (Canonical, Sitemap und hreflang verwenden genau diese Adresse). Soll die Domain
   ohne `www` die Hauptadresse sein, `DOMAIN` in `build.py` und die Rewrite-Regel in `.htaccess` anpassen und neu bauen.
3. **Mail-Test:** über `/kontakt/` (und über den Orientierungs-Check) je ein Testformular absenden, prüfen, dass die Mail an
   `office@stolz-consulting.net` ankommt (auch Spam-Ordner; Absenderadresse/SPF beim Hoster prüfen). Kommt nichts an,
   `mail()`-Freischaltung beim Hoster erfragen. Ohne PHP greift nur der mailto-Fallback.
4. **Header kontrollieren** (z. B. Browser-Entwicklertools, Netzwerk → Antwort-Header): `Content-Security-Policy`,
   `X-Content-Type-Options`, `Referrer-Policy` vorhanden? Wenn der Hoster `.htaccess` ignoriert, die Werte dort im
   Kundenbereich setzen. Browser-Konsole auf CSP-Meldungen prüfen. Das Inline-Skript im `<head>` ist per Hash erlaubt –
   Änderungen daran erfordern einen neuen Hash in `.htaccess`. HSTS ist vorbereitet, aber auskommentiert: erst aktivieren,
   wenn HTTPS dauerhaft funktioniert.
5. **404-Seite:** eine nicht existierende Adresse aufrufen (z. B. `/gibtsnicht`) → `404.html` erscheint.
6. **Suchmaschinen:** `https://www.stolz-consulting.net/sitemap.xml` in der Google Search Console / Bing Webmaster Tools
   einreichen; Social-Vorschau mit dem Facebook-Sharing-Debugger bzw. LinkedIn Post Inspector testen.
7. **Platzhalter schließen:** `python build.py` listet am Ende alle offenen `[BITTE ERGÄNZEN]`-Stellen (Impressum, Hosting im
   Datenschutz). Vor Livegang alle ergänzen und die Rechtstexte juristisch prüfen lassen.
8. Alte Website: Vor dem Umschalten die alten URLs prüfen; wenn sie sich unterscheiden, 301-Weiterleitungen in `.htaccess` ergänzen.

**Andere Server:** nginx/IIS ignorieren `.htaccess`. Dort gleichwertig einrichten: Weiterleitung auf `https://www…`,
`error_page 404 /404.html`, die Header aus `.htaccess`, Cache-Zeiten (HTML kurz, Schriften 1 Jahr, CSS/JS 1 Woche) und
`contact.php` über PHP-FPM.

## Qualitätssicherung (Paket 4)

Geprüft: alle 28 Seiten bei 320/375/768/1440 px auf horizontalen Überlauf und abgeschnittenen Text (keine Funde),
Überschriftenhierarchie, Alt-Texte, tote interne Links, deutsche Reste in EN/FR/RU, Farbkontraste, Formular- und
Popup-Bedienung (Tastatur, Esc, Fokus), keine externen Requests, CLS 0. Nicht automatisch prüfbar: Lighthouse (nicht
ausgeführt), echter Mailversand, `php -l`, Screenreader.
