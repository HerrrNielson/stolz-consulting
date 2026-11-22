/* Weltkarte (Referenzseite): Einblend-Animation beim Einscrollen, Tooltip per Hover/Fokus/Tippen.
   Ohne JS bleibt die Karte vollständig sichtbar. Keine Inline-Styles: Position per CSSOM (el.style.left). */
(function () {
  "use strict";
  var fig = document.querySelector("[data-wmap]");
  if (!fig) return;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)");

  /* Animation */
  if ("IntersectionObserver" in window && !reduce.matches) {
    fig.classList.add("wmap--ready");
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        fig.classList.add("is-in");
        io.disconnect();
      });
    }, { threshold: 0.3 });
    io.observe(fig);
  }

  /* Tooltip */
  var tip = fig.querySelector(".wmap__tip");
  var pins = Array.prototype.slice.call(fig.querySelectorAll(".wmap__pin"));
  var items = Array.prototype.slice.call(document.querySelectorAll(".wmap__list li"));
  var current = null;

  function setActive(id) {
    pins.forEach(function (p) { p.classList.toggle("is-active", p.getAttribute("data-place") === id); });
    items.forEach(function (li) { li.classList.toggle("is-active", li.getAttribute("data-place") === id); });
  }
  function hide() {
    tip.hidden = true; current = null; setActive(null);
  }
  function show(pin) {
    current = pin;
    setActive(pin.getAttribute("data-place"));
    tip.textContent = pin.getAttribute("data-tip");
    tip.hidden = false;
    tip.classList.remove("is-below");
    var fr = fig.getBoundingClientRect();
    var dr = pin.querySelector(".wmap__dot").getBoundingClientRect();
    var x = dr.left + dr.width / 2 - fr.left;
    var y = dr.top - fr.top;
    var half = tip.offsetWidth / 2;
    x = Math.max(half + 4, Math.min(fr.width - half - 4, x));
    if (y - tip.offsetHeight - 20 < 0) { tip.classList.add("is-below"); y = dr.bottom - fr.top; }
    tip.style.left = x + "px";
    tip.style.top = y + "px";
  }
  pins.forEach(function (p) {
    p.addEventListener("pointerenter", function (e) { if (e.pointerType === "mouse") show(p); });
    p.addEventListener("pointerleave", function (e) { if (e.pointerType === "mouse" && document.activeElement !== p) hide(); });
    p.addEventListener("focus", function () { show(p); });
    p.addEventListener("blur", hide);
    p.addEventListener("click", function (e) { e.stopPropagation(); show(p); });
  });
  items.forEach(function (li) {
    var pin = fig.querySelector('.wmap__pin[data-place="' + li.getAttribute("data-place") + '"]');
    if (!pin) return;
    li.addEventListener("mouseenter", function () { setActive(li.getAttribute("data-place")); });
    li.addEventListener("mouseleave", function () { setActive(current ? current.getAttribute("data-place") : null); });
    li.addEventListener("click", function () { show(pin); });
  });
  document.addEventListener("click", function (e) { if (current && !fig.contains(e.target)) hide(); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && current) hide(); });
  window.addEventListener("resize", function () { if (current) show(current); });
})();
