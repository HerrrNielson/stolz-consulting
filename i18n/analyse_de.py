# -*- coding: utf-8 -*-
"""Texte des Orientierungs-Checks (Popup, assets/js/analyse.js) – Deutsch.

build.py bettet diese Daten als JSON in jede Seite ein; im JS stehen keine Texte.
topics[].opts: (id, Beschriftung) – ids plan/act/second/first/info steuern die Rückmeldung (fb_kind)
und werden von contact.php in eine Klartext-Zeile für die Mail übersetzt (Whitelist).
Platzhalter: {n}/{m} Schritt, {topics} Auswahl, {a}…{/a} Link, {email} Adresse.
"""


def _t(id, label, q, plan, act, second, sentence):
    return dict(id=id, label=label, q=q, opts=[("plan", plan), ("act", act), ("second", second)], sentence=sentence)


ANALYSE = dict(
    fab="Orientierungsgespräch", fab_title="Unverbindliches Orientierungsgespräch",
    kicker="Unverbindlich", title="Orientierungs-Check",
    lead="Ein paar kurze Fragen, damit ich Ihre Situation besser einordnen kann – es dauert etwa eine Minute.",
    close="Schließen", back="Zurück", next="Weiter", progress="Schritt {n} von {m}",
    s1_q="Welches Thema beschäftigt Sie derzeit?", s1_hint="Mehrfachauswahl möglich.",
    topics=[
        _t("controlling", "Controlling und Finanzsteuerung", "Wie ist die Ausgangslage bei Planung und Reporting?",
           "Ich plane den Aufbau oder Umbau noch", "Es gibt konkreten Handlungsbedarf", "Ich suche eine zweite Meinung zu bestehenden Lösungen",
           "Bei Controlling und Finanzsteuerung geht es zunächst darum, was an Planung und Reporting schon vorhanden ist und was Sie davon für Entscheidungen brauchen."),
        _t("finanzierung", "Finanzierung", "Wie konkret ist Ihr Finanzierungsvorhaben?",
           "Ich plane noch und sondiere Möglichkeiten", "Es steht eine konkrete Entscheidung an", "Ich möchte ein bestehendes Angebot oder Konzept gegenprüfen",
           "Bei Finanzierungsfragen zählt, dass die Lösung zur Situation und zur Planung Ihres Unternehmens passt."),
        _t("international", "Wachstum und Internationalisierung", "Wie weit ist der Schritt ins Ausland oder in neue Märkte?",
           "Ich überlege noch, ob und wie", "Es gibt konkrete Pläne oder Handlungsbedarf", "Ich suche eine zweite Meinung zu bestehenden Plänen",
           "Bei Wachstum und Internationalisierung lässt sich gut klären, welche organisatorischen und wirtschaftlichen Fragen als Erstes anstehen."),
        _t("erp", "ERP und IT-Prozesse (z. B. SAP)", "Wo stehen Sie bei Ihrer ERP- oder IT-Lösung?",
           "Ich plane eine Einführung oder Änderung noch", "Es gibt konkreten Handlungsbedarf im laufenden Betrieb", "Ich suche eine zweite Meinung zu einer Lösung oder einem Angebot",
           "Bei ERP und IT-Prozessen geht es darum, betriebswirtschaftliche Anforderungen und praxistaugliche Lösungen zusammenzubringen."),
        _t("training", "Schulung und Training", "Was haben Sie vor?",
           "Ich plane noch und sammle Ideen", "Es gibt einen konkreten Bedarf oder Termin", "Ich suche eine Einschätzung zu Inhalt und Format",
           "Bei Schulung und Training lässt sich im Gespräch klären, welche Inhalte und welches Format für Ihr Team sinnvoll sind."),
        dict(id="unklar", label="Noch unklar", q="Was würde Ihnen jetzt am meisten helfen?",
             opts=[("first", "Eine erste Einordnung meiner Situation"), ("second", "Eine zweite Meinung"), ("info", "Ich möchte mich zunächst informieren")],
             sentence="Wenn noch unklar ist, welches Thema für Sie im Vordergrund steht, ist das ein guter Ausgangspunkt für ein Gespräch – die Fragen lassen sich gemeinsam sortieren."),
    ],
    size_q="Wie groß ist Ihr Unternehmen?", size_opt="(optional)",
    sizes=[("micro", "Kleinst|unternehmen"), ("sme", "KMU bis 50 Mitarbeitende"), ("large", "Größeres Unternehmen")],
    s3_q="Eine erste Einordnung", fb_intro="Ihre Auswahl – {topics} – lässt sich in einem Gespräch gut einordnen.",
    fb_kind=dict(
        plan="Wenn Sie noch in der Planung sind, ist ein früher Austausch oft hilfreich: Fragen lassen sich sortieren, bevor Entscheidungen anstehen.",
        act="Bei konkretem Handlungsbedarf geht es im Gespräch zunächst darum, die Lage zu klären und mögliche nächste Schritte zu ordnen.",
        second="Eine zweite Meinung kann helfen, bestehende Überlegungen oder Angebote einzuordnen – sachlich und ohne Vorfestlegung.",
        first="Eine erste Einordnung ist ein guter Anfang, ohne dass Sie sich schon festlegen müssen.",
        info="Sie können sich zunächst informieren – auch dafür ist ein Gespräch geeignet, ganz ohne Verpflichtung."),
    fb_close="Ein Orientierungsgespräch ist unverbindlich. Gemeinsam klären wir, ob und wie ich Sie sinnvoll unterstützen kann.",
    fb_note="Ihre Angaben werden erst übermittelt, wenn Sie im nächsten Schritt absenden.",
    cta="Orientierungsgespräch anfragen", direct="Lieber direkt schreiben", **{"and": " und "},
    s4_q="Wie darf ich Sie erreichen?", s4_lead="Ich melde mich persönlich bei Ihnen, um einen Termin für das Orientierungsgespräch abzustimmen.",
    summary_label="Ihre Angaben", req_note="Felder mit * sind Pflichtfelder.", opt="(optional)",
    name="Name", email="E-Mail-Adresse", phone="Telefon", msg="Nachricht",
    msg_ph="Was soll ich vorab wissen? (z. B. Branche, Anlass, Wunschzeitraum)",
    consent="Ich habe die {a}Datenschutzerklärung{/a} gelesen und bin einverstanden, dass meine Angaben zur Bearbeitung meiner Anfrage verwendet werden. *",
    send="Anfrage senden", sending="Wird gesendet …",
    invalid="Bitte geben Sie Ihren Namen und eine gültige E-Mail-Adresse an und bestätigen Sie die Datenschutzerklärung.",
    ok_h="Vielen Dank", ok_p="Ihre Anfrage ist bei mir eingegangen. Ich melde mich persönlich bei Ihnen, um das Orientierungsgespräch abzustimmen.",
    done="Fenster schließen",
    err_h="Das hat leider nicht geklappt", err_p="Ihre Anfrage konnte nicht gesendet werden. Bitte versuchen Sie es erneut oder schreiben Sie direkt an {email}.",
    retry="Erneut versuchen", mail_cta="E-Mail schreiben",
)
