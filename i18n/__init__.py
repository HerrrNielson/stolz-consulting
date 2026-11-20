# -*- coding: utf-8 -*-
"""
Sprachdaten für build.py – eine Datei pro Sprache (de.py, en.py, fr.py, ru.py).

Neue Sprache ergänzen:
  1. i18n/xx.py nach dem Muster von de.py anlegen (Variable DATA)
  2. unten in LANGUAGES eintragen (Reihenfolge = Reihenfolge im Sprachumschalter)
  3. python build.py

Aufbau von DATA:
  code, short, name, locale          Sprachcode, Kürzel im Umschalter, Eigenbezeichnung, og:locale
  slugs                              URL-Pfade je Seite (relativ zum Sprachordner, mit Slash am Ende)
  nav                                Hauptnavigation: [(Seitenschlüssel, Beschriftung), ...]
  ui                                 allgemeine Oberflächentexte (Header, Footer, Aria-Labels)
  meta                               {Seitenschlüssel: (Titel, Beschreibung)}
  home/profil/referenzen/kontakt/    Inhalte je Seite
  impressum/datenschutz/cta
Auszeichnung *Text* in Überschriften wird zu <em>Text</em>.

Deutsch liegt unter /, alle anderen Sprachen unter /<code>/.
"""
from . import de, en, fr, ru
from . import analyse_de, analyse_en, analyse_fr, analyse_ru

# Texte des Orientierungs-Checks (Popup) liegen in analyse_<sprache>.py und hängen als DATA["analyse"] an
for _d, _a in ((de, analyse_de), (en, analyse_en), (fr, analyse_fr), (ru, analyse_ru)):
    _d.DATA["analyse"] = _a.ANALYSE

LANGUAGES = [de.DATA, en.DATA, fr.DATA, ru.DATA]
DEFAULT_LANG = "de"
