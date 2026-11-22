/* Stolz Consulting – Orientierungs-Check (Popup), ohne Bibliotheken.

   Ablauf: 1 Thema  ·  2 Folgefrage (+ optional Unternehmensgröße)  ·  3 Rückmeldung  ·  4 Kontakt.
   Sendet nur beim Absenden in Schritt 4 an contact.php (Feld source=analyse). Alle Antworten
   bleiben bis dahin im Arbeitsspeicher; es werden keine Analysedaten gespeichert.

   Texte: komplett aus <script type="application/json" id="analyse-data"> (i18n/analyse_<sprache>.py).
   Progressive Enhancement: Ohne JavaScript ist .analyse-fab ein normaler Link zur Kontaktseite.

   Auslöser (automatisch):  40 s Verweildauer ODER ca. 50 % Scrolltiefe (was zuerst eintritt)
     - höchstens einmal pro Besuch   (sessionStorage "sc-analyse-shown")
     - nach dem Schließen 14 Tage Pause (localStorage "sc-analyse-closed" = Zeitstempel)
   Manuell: Klick auf den Button „Orientierungsgespräch“ (öffnet immer).

   Testen / Debuggen:
     ?analyse=now     in der URL: Dialog öffnet sofort, Speicherregeln werden ignoriert
     ?analyse=reset   in der URL: setzt die Speichereinträge zurück
     Konsole:         StolzAnalyse.open()   StolzAnalyse.reset()   StolzAnalyse.config  */
(function () {
  "use strict";

  var dataEl = document.getElementById("analyse-data");
  if (!dataEl) return; /* Seite ohne Orientierungs-Check (Impressum, Datenschutz, Kontakt) */
  var T;
  try { T = JSON.parse(dataEl.textContent); } catch (e) { return; }

  var DELAY_MS = 40000, SCROLL_RATIO = 0.5, PAUSE_DAYS = 14, TOTAL = 4;
  var KEY_SESSION = "sc-analyse-shown", KEY_CLOSED = "sc-analyse-closed";
  var doc = document.documentElement;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
  var ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M5 12h14M13 6l6 6-6 6"/></svg>';

  /* ---------- Storage (kann blockiert sein -> immer try/catch) ---------- */
  function store(kind, op, key, val) {
    try {
      var s = window[kind];
      if (op === "get") return s.getItem(key);
      if (op === "set") s.setItem(key, val);
      if (op === "del") s.removeItem(key);
    } catch (e) { /* Storage nicht verfügbar: Dialog funktioniert trotzdem */ }
    return null;
  }
  function recentlyClosed() {
    var t = parseInt(store("localStorage", "get", KEY_CLOSED), 10);
    return !isNaN(t) && Date.now() - t < PAUSE_DAYS * 864e5;
  }

  /* ---------- DOM-Helfer ---------- */
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }
  function attr(n, o) { for (var k in o) n.setAttribute(k, o[k]); return n; }
  function fill(str, map) { return str.replace(/\{(\w+)\}/g, function (m, k) { return map[k] != null ? map[k] : m; }); }
  function topicById(id) { return T.topics.filter(function (x) { return x.id === id; })[0]; }
  function joinList(arr) {
    return arr.length < 2 ? arr.join("") : arr.slice(0, -1).join(", ") + T["and"] + arr[arr.length - 1];
  }

  /* ---------- Zustand ---------- */
  var state, dlg, headTitleId = "analyse-title";
  function isOpen() { return !!(dlg && dlg.open); }
  var built = false, bodyEl, stepText, bar, xBtn;
  function resetState() {
    state = { step: 1, topics: [], phase: "", size: "", contact: { name: "", email: "", phone: "", message: "", consent: false },
              view: "form", status: "" };
  }
  resetState();

  /* Folgefrage richtet sich nach dem ersten gewählten Thema (konkrete Themen vor „Noch unklar“) */
  function leadTopic() {
    var order = T.topics.map(function (x) { return x.id; });
    var chosen = order.filter(function (id) { return state.topics.indexOf(id) > -1; });
    return topicById(chosen[0]);
  }

  /* ---------- Aufbau des Dialogs (einmalig) ----------
     Natives <dialog> mit showModal(): Der Browser übernimmt inerte Seite, Fokusfalle, Top-Layer,
     ::backdrop, ESC/Zurück-Geste und die Fokus-Rückgabe an den Auslöser. */
  function build() {
    if (built) return;
    built = true;
    dlg = attr(el("dialog", "analyse__dialog"), { "aria-labelledby": headTitleId, closedby: "any" });

    xBtn = attr(el("button", "analyse__x"), { type: "button", "aria-label": T.close });
    xBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true" focusable="false"><path d="M6 6l12 12M18 6 6 18"/></svg>';
    xBtn.addEventListener("click", function () { close(); });

    var head = el("header", "analyse__head");
    head.appendChild(el("p", "analyse__kicker", T.kicker));
    var h = el("h2", "analyse__title", T.title); h.id = headTitleId;
    head.appendChild(h);
    var prog = attr(el("div", "analyse__progress"), { role: "progressbar", "aria-valuemin": "1", "aria-valuemax": String(TOTAL) });
    stepText = el("p", "analyse__step");
    bar = el("div", "analyse__bar");
    for (var i = 0; i < TOTAL; i++) bar.appendChild(el("span"));
    prog.appendChild(stepText); prog.appendChild(bar);
    head.appendChild(prog);

    bodyEl = el("div", "analyse__body");
    dlg.appendChild(xBtn); dlg.appendChild(head); dlg.appendChild(bodyEl);
    document.body.appendChild(dlg);

    /* ESC, Zurück-Geste und Klick neben den Dialog (closedby="any") laufen über "cancel":
       abfangen, damit auch diese Wege die Ausblend-Animation zeigen. */
    dlg.addEventListener("cancel", function (e) { e.preventDefault(); close(); });
    /* "close" feuert bei jedem Schließen, auch wenn der Browser "cancel" nicht abbrechen lässt */
    dlg.addEventListener("close", function () {
      dlg.removeAttribute("data-closing");
      if (dlg.open) return; /* vor dem Ereignis schon wieder geöffnet */
      store("localStorage", "set", KEY_CLOSED, String(Date.now())); /* 14 Tage keine automatische Anzeige */
    });

    /* Klick neben den Dialog ohne closedby-Unterstützung (Safari): Drücken UND Loslassen außerhalb
       der Dialogfläche, damit ein Markier-Zug, der auf dem Hintergrund endet, nicht schließt. */
    if (!("closedBy" in HTMLDialogElement.prototype)) {
      var outside = function (e) {
        var r = dlg.getBoundingClientRect();
        return e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom;
      };
      var pressedOutside = false;
      dlg.addEventListener("pointerdown", function (e) { pressedOutside = outside(e); });
      dlg.addEventListener("pointerup", function (e) { if (pressedOutside && outside(e)) close(); });
    }
  }

  /* ---------- Öffnen / Schließen ---------- */
  function open() {
    if (isOpen() && !dlg.hasAttribute("data-closing")) return;
    build();
    store("sessionStorage", "set", KEY_SESSION, "1"); /* pro Besuch nur einmal automatisch */
    resetState();
    render(true);
    dlg.removeAttribute("data-closing"); /* falls während des Ausblendens erneut geöffnet */
    if (!dlg.open) dlg.showModal();
    focusStepHeading();
  }

  /* Ausblenden: data-closing startet die CSS-Übergänge, der Dialog bleibt bis zu deren Ende im
     Top-Layer und wird dann geschlossen. Funktioniert ohne CSS "overlay"/display-Übergänge. */
  function close() {
    if (!isOpen() || dlg.hasAttribute("data-closing")) return;
    dlg.setAttribute("data-closing", "");
    var anims = dlg.getAnimations ? dlg.getAnimations({ subtree: true }) : [];
    var finished = Promise.all(anims.map(function (a) { return a.finished.catch(function () {}); }));
    Promise.race([finished, new Promise(function (r) { setTimeout(r, 600); })]).then(function () {
      if (!dlg.hasAttribute("data-closing")) return; /* inzwischen wieder geöffnet */
      dlg.close();
    });
  }

  function focusStepHeading() {
    var h = bodyEl.querySelector("[data-focus]");
    (h || xBtn).focus({ preventScroll: true });
  }

  /* ---------- Rendering der Schritte ---------- */
  function go(step, dir) {
    state.status = "";
    var apply = function () { state.step = step; render(false, dir); focusStepHeading(); };
    var old = bodyEl.firstChild;
    if (old && !reduce.matches) {
      old.classList.add("is-leave", dir < 0 ? "is-back" : "is-fwd");
      setTimeout(apply, 170);
    } else apply();
  }

  function setProgress() {
    var done = state.view !== "form" && state.view !== "error" ? TOTAL : state.step;
    var txt = fill(T.progress, { n: done, m: TOTAL });
    stepText.textContent = txt;
    var p = bar.parentNode;
    p.setAttribute("aria-valuenow", String(done));
    p.setAttribute("aria-valuetext", txt);
    Array.prototype.forEach.call(bar.children, function (s, i) { s.classList.toggle("is-done", i < done); });
  }

  function render(initial, dir) {
    setProgress();
    bodyEl.textContent = "";
    var panel = el("div", "analyse__panel" + (initial ? "" : (dir < 0 ? " is-enter is-back" : " is-enter is-fwd")));
    var content = el("div", "analyse__content");
    var actions = el("div", "analyse__actions");
    panel.appendChild(content); panel.appendChild(actions);
    bodyEl.appendChild(panel);

    if (state.view === "ok") renderOk(content, actions);
    else if (state.view === "error") renderError(content, actions);
    else if (state.step === 1) renderTopics(content, actions);
    else if (state.step === 2) renderFollow(content, actions);
    else if (state.step === 3) renderFeedback(content, actions);
    else renderContact(content, actions);
  }

  function heading(text, parent) {
    var h = attr(el("h3", "analyse__q", text), { tabindex: "-1", "data-focus": "" });
    parent.appendChild(h);
    return h;
  }

  function primary(label, handler, type) {
    var b = attr(el("button", "btn btn--primary analyse__next"), { type: type || "button" });
    b.appendChild(el("span", null, label));
    b.insertAdjacentHTML("beforeend", ARROW);
    if (handler) b.addEventListener("click", handler);
    return b;
  }
  function backBtn(handler) {
    var b = attr(el("button", "analyse__back", T.back), { type: "button" });
    b.addEventListener("click", handler);
    return b;
  }

  /* Auswahlkarte (Checkbox oder Radio) */
  function choice(type, name, value, label, checked, onChange) {
    var l = el("label", "analyse__opt");
    var i = attr(el("input"), { type: type, name: name, value: value });
    i.checked = !!checked;
    i.addEventListener("change", function () { onChange(i); });
    l.appendChild(i);
    var lab = el("span", "analyse__opt-label", typeof label === "string" ? label : null);
    if (typeof label !== "string") lab.appendChild(label);
    l.appendChild(lab);
    return l;
  }

  /* Kontrollierter Umbruch in Kacheln: "|" markiert die Stelle (nach Buchstaben mit Bindestrich) */
  function tileLabel(s) {
    var parts = s.split("|");
    if (parts.length < 2) return s;
    var f = el("span", "tile-txt");
    f.appendChild(document.createTextNode(parts[0]));
    if (!/[-\s]$/.test(parts[0])) f.appendChild(el("span", "tile-h", "-"));
    f.appendChild(el("br", "tile-br"));
    f.appendChild(document.createTextNode(parts[1]));
    return f;
  }

  /* Schritt 1: Thema (Mehrfachauswahl; „Noch unklar“ schließt die anderen aus) */
  function renderTopics(content, actions) {
    var fs = el("fieldset", "analyse__set");
    var lg = el("legend", "analyse__legend");
    var h = el("span", "analyse__q", T.s1_q); h.setAttribute("tabindex", "-1"); h.setAttribute("data-focus", "");
    lg.appendChild(h);
    fs.appendChild(lg);
    fs.appendChild(el("p", "analyse__hint", T.s1_hint));
    var grid = el("div", "analyse__grid");
    var next;
    T.topics.forEach(function (t) {
      grid.appendChild(choice("checkbox", "topic", t.id, t.label, state.topics.indexOf(t.id) > -1, function (inp) {
        if (inp.checked) {
          state.topics = t.id === "unklar" ? ["unklar"] : state.topics.filter(function (x) { return x !== "unklar"; }).concat(t.id);
        } else state.topics = state.topics.filter(function (x) { return x !== t.id; });
        Array.prototype.forEach.call(grid.querySelectorAll("input"), function (n) { n.checked = state.topics.indexOf(n.value) > -1; });
        next.disabled = !state.topics.length;
      }));
    });
    fs.appendChild(grid);
    content.appendChild(fs);
    next = primary(T.next, function () { if (state.topics.length) go(2, 1); });
    next.disabled = !state.topics.length;
    actions.appendChild(next);
  }

  /* Schritt 2: Folgefrage zum Thema + optional Unternehmensgröße */
  function renderFollow(content, actions) {
    var lead = leadTopic();
    if (state.phase && !lead.opts.some(function (o) { return o[0] === state.phase; })) state.phase = "";
    var fs = el("fieldset", "analyse__set");
    var lg = el("legend", "analyse__legend");
    var h = el("span", "analyse__q", lead.q); h.setAttribute("tabindex", "-1"); h.setAttribute("data-focus", "");
    lg.appendChild(h); fs.appendChild(lg);
    var list = el("div", "analyse__list");
    var next;
    lead.opts.forEach(function (o) {
      list.appendChild(choice("radio", "phase", o[0], o[1], state.phase === o[0], function () {
        state.phase = o[0]; next.disabled = false;
      }));
    });
    fs.appendChild(list);
    content.appendChild(fs);

    var fs2 = el("fieldset", "analyse__set analyse__set--size");
    var lg2 = el("legend", "analyse__legend analyse__legend--small", T.size_q + " ");
    lg2.appendChild(el("span", "analyse__opt-note", T.size_opt));
    fs2.appendChild(lg2);
    var row = el("div", "analyse__chips");
    T.sizes.forEach(function (s) {
      row.appendChild(choice("radio", "size", s[0], tileLabel(s[1]), state.size === s[0], function () { state.size = s[0]; }));
    });
    fs2.appendChild(row);
    content.appendChild(fs2);

    actions.appendChild(backBtn(function () { go(1, -1); }));
    next = primary(T.next, function () { if (state.phase) go(3, 1); });
    next.disabled = !state.phase;
    actions.appendChild(next);
  }

  /* Schritt 3: kurze, allgemeine Rückmeldung (keine Zahlen, keine Erfolgsversprechen) */
  function renderFeedback(content, actions) {
    heading(T.s3_q, content);
    var labels = state.topics.map(function (id) { return topicById(id).label; });
    content.appendChild(el("p", "analyse__fb-lead", fill(T.fb_intro, { topics: joinList(labels) })));
    var ul = el("ul", "analyse__fb-list");
    state.topics.forEach(function (id) { ul.appendChild(el("li", null, topicById(id).sentence)); });
    content.appendChild(ul);
    if (T.fb_kind[state.phase]) content.appendChild(el("p", null, T.fb_kind[state.phase]));
    content.appendChild(el("p", null, T.fb_close));
    content.appendChild(el("p", "analyse__note", T.fb_note));

    actions.appendChild(backBtn(function () { go(2, -1); }));
    var direct = attr(el("a", "analyse__direct", T.direct), { href: T.contact_url });
    actions.appendChild(direct);
    actions.appendChild(primary(T.cta, function () { go(4, 1); }));
  }

  /* Text mit {a}…{/a} -> Link auf Datenschutzseite */
  function consentNode(str) {
    var span = el("span");
    var m = str.match(/^(.*?)\{a\}(.*?)\{\/a\}(.*)$/);
    if (!m) { span.textContent = str; return span; }
    span.appendChild(document.createTextNode(m[1]));
    var a = attr(el("a", null, m[2]), { href: T.privacy_url, target: "_blank", rel: "noopener" });
    span.appendChild(a);
    span.appendChild(document.createTextNode(m[3]));
    return span;
  }

  /* Schritt 4: Kontakt */
  function renderContact(content, actions) {
    heading(T.s4_q, content);
    content.appendChild(el("p", "analyse__lead", T.s4_lead));

    var sum = el("div", "analyse__summary");
    sum.appendChild(el("span", "analyse__summary-k", T.summary_label));
    var chips = el("ul", "analyse__tags");
    state.topics.forEach(function (id) { chips.appendChild(el("li", null, topicById(id).label)); });
    var lead = leadTopic(), ph = lead.opts.filter(function (o) { return o[0] === state.phase; })[0];
    if (ph) chips.appendChild(el("li", null, ph[1]));
    var sz = T.sizes.filter(function (s) { return s[0] === state.size; })[0];
    if (sz) chips.appendChild(el("li", null, sz[1].replace("|", "")));
    sum.appendChild(chips);
    content.appendChild(sum);

    var form = attr(el("form", "analyse__form"), { novalidate: "", action: T.action, method: "post", id: "analyse-form" });
    var c = state.contact;
    function field(id, name, label, type, auto, req, value, tag) {
      var f = el("div", "field");
      var l = el("label", null, label + " ");
      l.setAttribute("for", id);
      if (req) { var s = el("span", "req", "*"); s.setAttribute("aria-hidden", "true"); l.appendChild(s); }
      else l.appendChild(el("span", "opt", T.opt));
      var i = el(tag || "input");
      attr(i, { id: id, name: name });
      if (tag !== "textarea") i.type = type;
      if (tag === "textarea") { i.rows = 3; i.placeholder = T.msg_ph; i.maxLength = 5000; }
      if (auto) i.setAttribute("autocomplete", auto);
      if (req) { i.required = true; i.setAttribute("aria-required", "true"); }
      i.maxLength = tag === "textarea" ? 5000 : 160;
      i.value = value;
      i.addEventListener("input", function () { c[name] = i.value; });
      f.appendChild(l); f.appendChild(i);
      return f;
    }
    var row1 = el("div", "analyse__row");
    row1.appendChild(field("a-name", "name", T.name, "text", "name", true, c.name));
    row1.appendChild(field("a-email", "email", T.email, "email", "email", true, c.email));
    form.appendChild(row1);
    form.appendChild(field("a-phone", "phone", T.phone, "tel", "tel", false, c.phone));
    form.appendChild(field("a-message", "message", T.msg, "text", "", false, c.message, "textarea"));

    var hp = attr(el("div", "hp"), { "aria-hidden": "true" });
    var hpl = el("label", null, "Website"); hpl.setAttribute("for", "a-website");
    var hpi = attr(el("input"), { id: "a-website", name: "website", type: "text", tabindex: "-1", autocomplete: "off" });
    hp.appendChild(hpl); hp.appendChild(hpi);
    form.appendChild(hp);

    var chk = el("label", "check");
    var ci = attr(el("input"), { type: "checkbox", name: "consent", value: "1", required: "", "aria-required": "true" });
    ci.checked = !!c.consent;
    ci.addEventListener("change", function () { c.consent = ci.checked; });
    chk.appendChild(ci); chk.appendChild(consentNode(T.consent));
    form.appendChild(chk);
    form.appendChild(el("p", "analyse__req", T.req_note));

    var status = attr(el("p", "form__status"), { role: "alert" });
    form.appendChild(status);
    content.appendChild(form);

    var send = primary(T.send, null, "submit");
    send.setAttribute("form", "analyse-form");
    actions.appendChild(backBtn(function () { go(3, -1); }));
    var directMail = attr(el("a", "analyse__direct", T.direct), { href: T.contact_url });
    actions.appendChild(directMail);
    actions.appendChild(send);

    form.addEventListener("submit", function (e) { e.preventDefault(); submit(form, status, send); });
  }

  function showStatus(node, type, text) {
    node.className = "form__status is-" + type;
    node.textContent = text;
  }

  function submit(form, status, send) {
    if (!form.checkValidity()) {
      showStatus(status, "error", T.invalid);
      var bad = form.querySelector(":invalid"); if (bad) bad.focus();
      return;
    }
    var data = new FormData(form);
    data.append("lang", T.lang);
    data.append("source", "analyse");
    data.append("analyse_topics", state.topics.join(","));
    data.append("analyse_phase", state.phase);
    data.append("analyse_size", state.size);
    if (data.get("website")) { /* Honeypot: scheinbarer Erfolg, nichts wird gesendet */
      state.view = "ok"; render(false, 1); focusStepHeading(); return;
    }
    send.disabled = true;
    send.firstChild.textContent = T.sending;
    status.className = "form__status"; status.textContent = "";

    fetch(form.getAttribute("action"), { method: "POST", body: data, headers: { "Accept": "application/json" } })
      .then(function (res) {
        var type = res.headers.get("content-type") || "";
        if (type.indexOf("application/json") === -1) throw new Error("no-backend");
        return res.json().then(function (json) { return { res: res, json: json }; });
      })
      .then(function (r) {
        if (r.res.ok && r.json && r.json.ok) {
          state.contact = { name: "", email: "", phone: "", message: "", consent: false }; /* nichts behalten */
          state.view = "ok";
        } else if (r.res.status === 422) {
          send.disabled = false; send.firstChild.textContent = T.send;
          showStatus(status, "error", T.invalid);
          return;
        } else state.view = "error";
        go(state.step, 1);
      })
      .catch(function () { state.view = "error"; go(state.step, 1); });
  }

  /* Erfolgsansicht */
  function renderOk(content, actions) {
    heading(T.ok_h, content);
    content.appendChild(el("p", "analyse__lead", T.ok_p));
    var b = attr(el("button", "btn btn--primary analyse__next"), { type: "button" });
    b.appendChild(el("span", null, T.done));
    b.addEventListener("click", function () { close(); });
    actions.appendChild(b);
  }

  /* Fehleransicht: Eingaben bleiben erhalten (state.contact) */
  function renderError(content, actions) {
    heading(T.err_h, content);
    var p = el("p", "analyse__lead");
    var parts = T.err_p.split("{email}");
    p.appendChild(document.createTextNode(parts[0]));
    p.appendChild(attr(el("a", null, T.mail_to), { href: "mailto:" + T.mail_to }));
    p.appendChild(document.createTextNode(parts[1] || ""));
    content.appendChild(p);
    actions.appendChild(primary(T.retry, function () { state.view = "form"; state.step = 4; go(4, -1); }));
  }

  /* ---------- Auslöser ---------- */
  var autoDone = false;
  function eligible() {
    return !autoDone && !isOpen() && !recentlyClosed() && !store("sessionStorage", "get", KEY_SESSION);
  }
  function tryAuto(retries) {
    if (!eligible()) return;
    var a = document.activeElement;
    var busy = document.body.classList.contains("nav-open") ||
      (a && /^(INPUT|TEXTAREA|SELECT)$/.test(a.tagName) && a.type !== "checkbox") ||
      document.hidden;
    if (busy && (retries || 0) < 12) { setTimeout(function () { tryAuto((retries || 0) + 1); }, 5000); return; }
    if (busy) return;
    autoDone = true;
    open(null);
  }

  var timer = null;
  function arm() {
    if (!eligible()) return;
    timer = setTimeout(function () { stopWatching(); tryAuto(0); }, DELAY_MS);
    window.addEventListener("scroll", onScrollDepth, { passive: true });
  }
  function onScrollDepth() {
    var max = doc.scrollHeight - window.innerHeight;
    if (max < window.innerHeight * 0.5) return; /* Seite kaum scrollbar: nur der Timer zählt */
    var y = window.scrollY || window.pageYOffset;
    if ((y + window.innerHeight) / doc.scrollHeight >= SCROLL_RATIO) { stopWatching(); tryAuto(0); }
  }
  function stopWatching() {
    clearTimeout(timer);
    window.removeEventListener("scroll", onScrollDepth);
  }

  /* Einstiegsbutton(s): öffnet immer manuell; ohne JS bleibt es ein Link zur Kontaktseite */
  Array.prototype.forEach.call(document.querySelectorAll("[data-analyse-open]"), function (b) {
    b.addEventListener("click", function (e) {
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.button === 1) return;
      e.preventDefault();
      stopWatching();
      open();
    });
  });

  function reset() { store("sessionStorage", "del", KEY_SESSION); store("localStorage", "del", KEY_CLOSED); autoDone = false; }
  window.StolzAnalyse = { open: function () { open(null); }, reset: reset, config: { delayMs: DELAY_MS, scrollRatio: SCROLL_RATIO, pauseDays: PAUSE_DAYS } };

  var q = new URLSearchParams(window.location.search).get("analyse");
  if (q === "reset") reset();
  if (q === "now") { setTimeout(function () { open(null); }, 400); }
  else arm();
})();
