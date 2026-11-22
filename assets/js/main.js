/* Stolz Consulting – Frontend-Skript (ohne Bibliotheken).
   Progressive Enhancement: Die Seite ist auch ohne dieses Skript vollständig lesbar.
   Module: Header · Menü · Sprachumschalter · Einblenden ·
           Akkordeon-Anker · Marquee (Hover-Pause) · Fortschrittsbalken · Kontaktformular
   ERWEITERUNG: weitere Module (z. B. Problem-Analyse-Popup) als eigene Datei in assets/js/. */
(function () {
  "use strict";

  var doc = document.documentElement;
  doc.classList.add("js");
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
  var scrollHandlers = [];

  /* ---------- Scroll-Schleife (ein rAF für alles) ---------- */
  var ticking = false;
  function onScroll() {
    if (ticking) return;
    ticking = true;
    window.requestAnimationFrame(function () {
      ticking = false;
      scrollHandlers.forEach(function (fn) { fn(window.scrollY || window.pageYOffset); });
    });
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll, { passive: true });

  /* ---------- Header: transparent -> solide ---------- */
  var header = document.querySelector(".site-header");
  scrollHandlers.push(function (y) {
    if (header) header.classList.toggle("is-scrolled", y > 24);
  });

  /* ---------- Fortschrittsbalken (nur wenn CSS-Scroll-Timeline fehlt) ---------- */
  var progress = document.querySelector(".progress");
  var cssTimeline = window.CSS && CSS.supports && CSS.supports("animation-timeline", "scroll()");
  if (progress && !cssTimeline) {
    scrollHandlers.push(function (y) {
      var max = doc.scrollHeight - window.innerHeight;
      progress.style.setProperty("--p", max > 0 ? Math.min(1, y / max).toFixed(4) : 0);
    });
  }

  /* ---------- Navigation: eine <nav> für beide Layouts ----------
     Schmal: natives Popover (popover="auto", Button mit popovertarget). Der Browser übernimmt
     Öffnen/Schließen, ESC, Klick daneben, aria-expanded und die Fokus-Rückgabe an den Button.
     Breit: popover-Attribut entfernt, die Liste steht normal in der Kopfzeile.
     Ohne Popover-API (ältere Browser): kleiner Fallback mit der Klasse ":popover-open". */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("nav");
  if (toggle && nav) {
    var narrow = window.matchMedia("(max-width: 900px)");
    var native = Object.prototype.hasOwnProperty.call(HTMLElement.prototype, "popover");
    var isNavOpen = function () { return native ? nav.matches(":popover-open") : nav.classList.contains(":popover-open"); };

    var sync = function (open) {
      document.body.classList.toggle("nav-open", open);
      toggle.setAttribute("aria-label", toggle.getAttribute(open ? "data-label-close" : "data-label-open"));
      if (!native) toggle.setAttribute("aria-expanded", open ? "true" : "false");
      if (open) {
        var first = nav.querySelector("a");
        if (first) first.focus({ preventScroll: true });
      }
    };
    var closeNav = function () {
      if (!isNavOpen()) return;
      if (native) nav.hidePopover();
      else { nav.classList.remove(":popover-open"); sync(false); }
    };

    /* Popover nur im schmalen Layout (setAttribute statt .popover, s. Leitfaden) */
    var setLayout = function () {
      if (narrow.matches) { if (native) nav.setAttribute("popover", "auto"); }
      else { closeNav(); nav.removeAttribute("popover"); }
    };
    setLayout();
    narrow.addEventListener("change", setLayout);

    if (native) {
      nav.addEventListener("toggle", function (e) { sync(e.newState === "open"); });
    } else {
      toggle.setAttribute("aria-expanded", "false");
      toggle.addEventListener("click", function () {
        var open = !isNavOpen();
        nav.classList.toggle(":popover-open", open);
        sync(open);
      });
      document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && isNavOpen()) { closeNav(); toggle.focus(); }
      });
    }

    nav.querySelectorAll("a").forEach(function (a) { a.addEventListener("click", closeNav); });
    /* Fokus verlässt das Vollbild-Menü (Tab nach dem letzten Link): schließen, statt in
       verdeckte Seiteninhalte zu springen */
    nav.addEventListener("focusout", function (e) {
      var to = e.relatedTarget;
      if (to && to !== toggle && !nav.contains(to)) closeNav();
    });
  }

  /* ---------- Sprachumschalter: Pfeiltasten, Pos1/Ende ---------- */
  document.querySelectorAll("[data-lang-switch]").forEach(function (group) {
    var items = Array.prototype.slice.call(group.querySelectorAll("a"));
    group.addEventListener("keydown", function (e) {
      var i = items.indexOf(document.activeElement);
      if (i < 0) return;
      var n = null;
      if (e.key === "ArrowRight" || e.key === "ArrowDown") n = (i + 1) % items.length;
      else if (e.key === "ArrowLeft" || e.key === "ArrowUp") n = (i - 1 + items.length) % items.length;
      else if (e.key === "Home") n = 0;
      else if (e.key === "End") n = items.length - 1;
      if (n !== null) { e.preventDefault(); items[n].focus(); }
    });
  });

  /* ---------- Einblenden (gestaffelt) ---------- */
  document.querySelectorAll("[data-stagger]").forEach(function (group) {
    var kids = group.querySelectorAll(":scope > .reveal");
    var step = kids.length > 6 ? 40 : 70;
    kids.forEach(function (el, i) { el.style.setProperty("--d", Math.min(i * step, 280) + "ms"); });
  });
  var reveals = document.querySelectorAll(".reveal, [data-draw], .timeline");
  function showAll() {
    reveals.forEach(function (el) { el.classList.add("is-visible", "is-drawn"); });
  }
  if (!("IntersectionObserver" in window) || reduce.matches) {
    showAll();
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible", "is-drawn");
        io.unobserve(entry.target);
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -6% 0px" });
    reveals.forEach(function (el) { io.observe(el); });
  }

  /* ---------- Marquee: pausiert bei Hover und Tastaturfokus; bei prefers-reduced-motion steht es still (CSS) ---------- */
  document.querySelectorAll("[data-marquee]").forEach(function (m) {
    if (reduce.matches) return;
    var viewport = m.querySelector(".marquee__viewport");
    if (!viewport) return;
    viewport.addEventListener("mouseenter", function () { m.classList.add("is-paused"); });
    viewport.addEventListener("mouseleave", function () { m.classList.remove("is-paused"); });
  });

  /* ---------- Leistungen: Anker öffnet das passende Akkordeon ---------- */
  function openFromHash() {
    var id = decodeURIComponent((location.hash || "").slice(1));
    var el = id && document.getElementById(id);
    if (el && el.tagName === "DETAILS") {
      el.open = true;
      window.setTimeout(function () { el.scrollIntoView({ block: "start" }); }, 30);
    }
  }
  openFromHash();
  window.addEventListener("hashchange", openFromHash);

  /* Sanfter Gold-Ring am Aufklapp-Button (CSS); endet, sobald ein Punkt geöffnet/bedient wurde */
  var accList = document.querySelector(".acc-list");
  if (accList) {
    var touched = function () { accList.classList.add("is-touched"); };
    accList.addEventListener("click", touched, { once: true });
    accList.addEventListener("toggle", touched, true);
    if (accList.querySelector(".acc[open]")) touched();
  }

  /* ---------- Magnetische Buttons (nur Maus, nur ohne Reduced Motion) ---------- */
  if (window.matchMedia("(pointer: fine)").matches && !reduce.matches) {
    document.querySelectorAll(".btn--primary, .btn--outline").forEach(function (b) {
      b.addEventListener("pointermove", function (e) {
        var r = b.getBoundingClientRect();
        b.style.setProperty("--mx", ((e.clientX - r.left - r.width / 2) * 0.12).toFixed(1) + "px");
        b.style.setProperty("--my", ((e.clientY - r.top - r.height / 2) * 0.2).toFixed(1) + "px");
      });
      b.addEventListener("pointerleave", function () {
        b.style.setProperty("--mx", "0px");
        b.style.setProperty("--my", "0px");
      });
    });
  }

  onScroll();

  /* ---------- Jahr im Footer ---------- */
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });

  /* ---------- Kontaktformular ----------
     Sendet per fetch an das action-Ziel (contact.php). Ist dort kein
     PHP verfügbar, öffnet sich als Fallback das E-Mail-Programm. */
  var form = document.querySelector("[data-contact-form]");
  if (!form) return;
  var status = form.querySelector(".form__status");
  var button = form.querySelector("button[type='submit']");

  function show(type, text) {
    status.className = "form__status is-" + type;
    status.textContent = text;
  }

  function mailtoFallback(data) {
    var to = form.getAttribute("data-mailto");
    var subject = (data.get("subject") || form.getAttribute("data-subject")) + "";
    var body =
      data.get("message") + "\n\n— \n" +
      data.get("name") + "\n" +
      (data.get("company") ? data.get("company") + "\n" : "") +
      data.get("email") +
      (data.get("phone") ? "\n" + data.get("phone") : "");
    window.location.href = "mailto:" + to +
      "?subject=" + encodeURIComponent(subject) +
      "&body=" + encodeURIComponent(body);
    show("ok", form.getAttribute("data-msg-mailto"));
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    if (!form.checkValidity()) {
      /* Klare Meldung statt nur Browser-Sprechblase; Fokus auf das erste fehlerhafte Feld */
      show("error", form.getAttribute("data-msg-invalid"));
      var bads = form.querySelectorAll(":invalid");
      Array.prototype.forEach.call(form.elements, function (f) { f.removeAttribute("aria-invalid"); });
      Array.prototype.forEach.call(bads, function (f) {
        f.setAttribute("aria-invalid", "true");
        var clear = function () { if (f.validity.valid) f.removeAttribute("aria-invalid"); };
        f.addEventListener("input", clear); f.addEventListener("change", clear);
      });
      if (bads[0]) bads[0].focus();
      return;
    }
    var data = new FormData(form);
    if (data.get("website")) { /* Spam-Honeypot: Bot sieht scheinbaren Erfolg, es wird nichts gesendet */
      form.reset();
      show("ok", form.getAttribute("data-msg-ok"));
      return;
    }

    button.disabled = true;
    status.className = "form__status";
    status.textContent = "";
    fetch(form.getAttribute("action"), {
      method: "POST",
      body: data,
      headers: { "Accept": "application/json" }
    })
      .then(function (res) {
        var type = res.headers.get("content-type") || "";
        /* Kein JSON = kein PHP-Backend vorhanden (z. B. statischer Webspace) -> E-Mail-Fallback */
        if (type.indexOf("application/json") === -1) throw new Error("no-backend");
        return res.json().then(function (json) { return { res: res, json: json }; });
      })
      .then(function (r) {
        if (r.res.ok && r.json && r.json.ok) {
          form.reset();
          show("ok", form.getAttribute("data-msg-ok"));
        } else if (r.res.status === 422) {
          show("error", form.getAttribute("data-msg-invalid"));
        } else {
          show("error", form.getAttribute("data-msg-error"));
        }
      })
      .catch(function () {
        mailtoFallback(data);
      })
      .then(function () {
        button.disabled = false;
      });
  });
})();
