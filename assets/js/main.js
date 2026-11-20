/* Stolz Consulting – Frontend-Skript (ohne Bibliotheken).
   Progressive Enhancement: Die Seite ist auch ohne dieses Skript vollständig lesbar.
   Module: Header · Menü · Sprachumschalter · Einblenden ·
           Akkordeon-Anker · Marquee · Fortschrittsbalken · Kontaktformular
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

  /* ---------- Mobile Navigation ---------- */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("nav");
  function setNav(open) {
    document.body.classList.toggle("nav-open", open);
    if (!toggle) return;
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    toggle.setAttribute("aria-label", toggle.getAttribute(open ? "data-label-close" : "data-label-open"));
  }
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = !document.body.classList.contains("nav-open");
      setNav(open);
      if (open) {
        var first = nav.querySelector("a");
        if (first) window.setTimeout(function () { first.focus({ preventScroll: true }); }, 350);
      }
    });
    nav.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () { setNav(false); });
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && document.body.classList.contains("nav-open")) {
        setNav(false);
        toggle.focus();
      }
      /* Fokus im geöffneten Menü halten */
      if (e.key === "Tab" && document.body.classList.contains("nav-open")) {
        var f = [toggle].concat(Array.prototype.slice.call(nav.querySelectorAll("a")));
        var i = f.indexOf(document.activeElement);
        if (e.shiftKey && i <= 0) { e.preventDefault(); f[f.length - 1].focus(); }
        else if (!e.shiftKey && i === f.length - 1) { e.preventDefault(); f[0].focus(); }
      }
    });
    window.matchMedia("(min-width: 901px)").addEventListener("change", function (m) { if (m.matches) setNav(false); });
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

  /* ---------- Marquee: Pausieren per Knopf, Hover und Fokus (WCAG 2.2.2) ---------- */
  document.querySelectorAll("[data-marquee]").forEach(function (m) {
    if (reduce.matches) return;
    var viewport = m.querySelector(".marquee__viewport");
    var label = m.getAttribute("data-pause-label");
    var bar = document.createElement("div");
    bar.className = "marquee__bar";
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "marquee__toggle";
    btn.setAttribute("aria-pressed", "false");
    btn.innerHTML = '<svg viewBox="0 0 12 12" aria-hidden="true"><rect x="1" y="1" width="3.5" height="10"/><rect x="7.5" y="1" width="3.5" height="10"/></svg><span></span>';
    btn.lastChild.textContent = label;
    btn.addEventListener("click", function () {
      var paused = m.classList.toggle("is-paused");
      btn.setAttribute("aria-pressed", paused ? "true" : "false");
    });
    bar.appendChild(btn);
    m.appendChild(bar);
    if (viewport) {
      viewport.addEventListener("mouseenter", function () { m.classList.add("is-paused"); });
      viewport.addEventListener("mouseleave", function () {
        if (btn.getAttribute("aria-pressed") !== "true") m.classList.remove("is-paused");
      });
    }
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
