# -*- coding: utf-8 -*-
"""Texte des Orientierungs-Checks (Popup) – English. Struktur siehe analyse_de.py."""


def _t(id, label, q, plan, act, second, sentence):
    return dict(id=id, label=label, q=q, opts=[("plan", plan), ("act", act), ("second", second)], sentence=sentence)


ANALYSE = dict(
    fab="Orientation call", fab_title="Non-binding orientation call",
    kicker="Non-binding", title="Orientation check",
    lead="A few short questions so I can better understand your situation – it takes about a minute.",
    close="Close", back="Back", next="Next", progress="Step {n} of {m}",
    s1_q="Where does the shoe pinch?", s1_hint="You can select more than one.",
    topics=[
        _t("controlling", "Controlling and financial management", "What is the starting point for planning and reporting?",
           "I am still planning to set it up or rework it", "There is a concrete need to act", "I am looking for a second opinion on existing solutions",
           "With controlling and financial management, the first question is what planning and reporting you already have and what you need from it for decisions."),
        _t("finanzierung", "Financing", "How concrete is your financing project?",
           "I am still planning and exploring options", "A concrete decision is coming up", "I would like to double-check an existing offer or concept",
           "With financing, what matters is that the solution fits your company's situation and plans."),
        _t("international", "Growth and internationalisation", "How far along is the step abroad or into new markets?",
           "I am still considering whether and how", "There are concrete plans or a need to act", "I am looking for a second opinion on existing plans",
           "With growth and internationalisation, it is easy to clarify which organisational and economic questions come first."),
        _t("erp", "ERP and IT processes (e.g. SAP)", "Where do you stand with your ERP or IT solution?",
           "I am still planning an introduction or change", "There is a concrete need to act in day-to-day operations", "I am looking for a second opinion on a solution or an offer",
           "With ERP and IT processes, the aim is to bring business requirements and practical solutions together."),
        _t("training", "Training and workshops", "What do you have in mind?",
           "I am still planning and collecting ideas", "There is a concrete need or date", "I am looking for an assessment of content and format",
           "With training, a conversation can clarify which content and format make sense for your team."),
        dict(id="unklar", label="Not sure yet", q="What would help you most right now?",
             opts=[("first", "A first assessment of my situation"), ("second", "A second opinion"), ("info", "I would like to find out more first")],
             sentence="If it is still unclear where exactly the shoe pinches, that is a good starting point for a conversation – the questions can be sorted out together."),
    ],
    size_q="How large is your company?", size_opt="(optional)",
    sizes=[("micro", "Micro-enterprise"), ("sme", "SME up to 50 employees"), ("large", "Larger company")],
    s3_q="A first assessment", fb_intro="Your selection – {topics} – can be put into context well in a conversation.",
    fb_kind=dict(
        plan="If you are still planning, an early exchange is often helpful: questions can be sorted before decisions are due.",
        act="With a concrete need to act, the conversation first aims to clarify the situation and organise possible next steps.",
        second="A second opinion can help put existing considerations or offers into perspective – factually and without commitment.",
        first="A first assessment is a good start, without you having to commit to anything.",
        info="You can start by finding out more – a conversation is suitable for that too, with no obligation."),
    fb_close="An orientation call is non-binding. Together we clarify whether and how I can usefully support you – not every question needs consulting.",
    fb_note="Your details are only sent when you submit in the next step.",
    cta="Request an orientation call", direct="Prefer to write directly", **{"and": " and "},
    s4_q="How may I reach you?", s4_lead="I will get in touch personally to arrange a time for the orientation call.",
    summary_label="Your answers", req_note="Fields marked * are required.", opt="(optional)",
    name="Name", email="Email address", phone="Phone", msg="Message",
    msg_ph="Anything I should know beforehand? (e.g. industry, occasion, preferred timing)",
    consent="I have read the {a}privacy policy{/a} and agree that my details may be used to process my enquiry. *",
    send="Send request", sending="Sending …",
    invalid="Please enter your name and a valid email address and confirm the privacy policy.",
    ok_h="Thank you", ok_p="Your request has reached me. I will get in touch personally to arrange the orientation call.",
    done="Close window",
    err_h="That did not work", err_p="Your request could not be sent. Please try again or write directly to {email}.",
    retry="Try again", mail_cta="Write an email",
)
