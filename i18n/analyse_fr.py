# -*- coding: utf-8 -*-
"""Texte des Orientierungs-Checks (Popup) – Français. Struktur siehe analyse_de.py.
Von Muttersprachler/in zu prüfen. Geschützte Leerzeichen vor ? ! : ; setzt build.py (fr_typo) automatisch."""


def _t(id, label, q, plan, act, second, sentence):
    return dict(id=id, label=label, q=q, opts=[("plan", plan), ("act", act), ("second", second)], sentence=sentence)


ANALYSE = dict(
    fab="Entretien d’orientation", fab_title="Entretien d’orientation sans engagement",
    kicker="Sans engagement", title="Bilan d’orientation",
    lead="Quelques questions brèves pour mieux cerner votre situation – cela prend environ une minute.",
    close="Fermer", back="Retour", next="Continuer", progress="Étape {n} sur {m}",
    s1_q="Quel sujet vous préoccupe actuellement ?", s1_hint="Plusieurs choix possibles.",
    topics=[
        _t("controlling", "Contrôle de gestion et pilotage financier", "Quelle est la situation de départ pour la planification et le reporting ?",
           "Je prévois encore de le mettre en place ou de le revoir", "Il y a un besoin d’agir concret", "Je cherche un deuxième avis sur des solutions existantes",
           "En contrôle de gestion et pilotage financier, il s’agit d’abord de savoir ce qui existe déjà en planification et en reporting, et ce dont vous avez besoin pour décider."),
        _t("finanzierung", "Financement", "Votre projet de financement est-il déjà concret ?",
           "Je suis encore en phase de planification et j’explore des options", "Une décision concrète est à prendre", "Je souhaite vérifier une offre ou un concept existant",
           "En matière de financement, l’essentiel est que la solution corresponde à la situation et aux projets de votre entreprise."),
        _t("international", "Croissance et internationalisation", "Où en êtes-vous de votre démarche vers l’étranger ou de nouveaux marchés ?",
           "Je réfléchis encore à la question du si et du comment", "Il y a des projets concrets ou un besoin d’agir", "Je cherche un deuxième avis sur des projets existants",
           "En croissance et internationalisation, on peut bien clarifier quelles questions d’organisation et de gestion se posent en premier."),
        _t("erp", "ERP et processus informatiques (p. ex. SAP)", "Où en êtes-vous avec votre solution ERP ou informatique ?",
           "Je prévois encore une introduction ou une modification", "Il y a un besoin d’agir concret dans l’exploitation courante", "Je cherche un deuxième avis sur une solution ou une offre",
           "En ERP et processus informatiques, il s’agit de réunir les exigences de gestion et des solutions praticables."),
        _t("training", "Formation", "Qu’avez-vous en tête ?",
           "Je suis encore en phase de planification et je recueille des idées", "Il y a un besoin ou une date concrets", "Je cherche une évaluation du contenu et du format",
           "En formation, un entretien permet de clarifier quels contenus et quel format conviennent à votre équipe."),
        dict(id="unklar", label="Pas encore clair", q="Qu’est-ce qui vous aiderait le plus en ce moment ?",
             opts=[("first", "Une première mise en perspective de ma situation"), ("second", "Un deuxième avis"), ("info", "Je souhaite d’abord m’informer")],
             sentence="S’il n’est pas encore clair quel sujet est prioritaire pour vous, c’est un bon point de départ pour un entretien – les questions peuvent être ordonnées ensemble."),
    ],
    size_q="Quelle est la taille de votre entreprise ?", size_opt="(facultatif)",
    sizes=[("micro", "Très petite |entreprise"), ("sme", "PME jusqu’à 50 collaborateurs"), ("large", "Entreprise plus grande")],
    s3_q="Une première mise en perspective", fb_intro="Votre sélection – {topics} – peut être bien cernée lors d’un entretien.",
    fb_kind=dict(
        plan="Si vous êtes encore en phase de planification, un échange précoce est souvent utile : les questions peuvent être ordonnées avant que les décisions ne se présentent.",
        act="En cas de besoin d’agir concret, l’entretien vise d’abord à clarifier la situation et à ordonner les prochaines étapes possibles.",
        second="Un deuxième avis peut aider à situer des réflexions ou des offres existantes – de façon factuelle et sans parti pris.",
        first="Une première mise en perspective est un bon début, sans que vous ayez à vous engager.",
        info="Vous pouvez d’abord vous informer – un entretien s’y prête aussi, sans aucune obligation."),
    fb_close="Un entretien d’orientation est sans engagement. Nous clarifions ensemble si et comment je peux vous soutenir utilement.",
    fb_note="Vos indications ne sont transmises que lorsque vous envoyez le formulaire à l’étape suivante.",
    cta="Demander un entretien d’orientation", direct="Écrire directement", **{"and": " et "},
    s4_q="Comment puis-je vous joindre ?", s4_lead="Je vous contacterai personnellement pour convenir d’un rendez-vous pour l’entretien d’orientation.",
    summary_label="Vos indications", req_note="Les champs marqués d’un * sont obligatoires.", opt="(facultatif)",
    name="Nom", email="Adresse e-mail", phone="Téléphone", msg="Message",
    msg_ph="Y a-t-il quelque chose que je devrais savoir au préalable ? (p. ex. secteur, contexte, période souhaitée)",
    consent="J’ai lu la {a}politique de confidentialité{/a} et j’accepte que mes indications soient utilisées pour traiter ma demande. *",
    send="Envoyer la demande", sending="Envoi en cours …",
    invalid="Veuillez indiquer votre nom et une adresse e-mail valide et confirmer la politique de confidentialité.",
    ok_h="Merci", ok_p="Votre demande m’est bien parvenue. Je vous contacterai personnellement pour convenir de l’entretien d’orientation.",
    done="Fermer la fenêtre",
    err_h="Cela n’a malheureusement pas fonctionné", err_p="Votre demande n’a pas pu être envoyée. Veuillez réessayer ou écrire directement à {email}.",
    retry="Réessayer", mail_cta="Écrire un e-mail",
)
