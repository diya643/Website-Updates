// Customer stories: copy-link button and product clip on view (story pages); industry filter (hub).
(function () {
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const io = (cb, opts) => ("IntersectionObserver" in window) ? new IntersectionObserver(cb, opts) : null;

  // Share: copy the page link
  document.querySelectorAll("[data-copy]").forEach((b) => b.addEventListener("click", () => {
    const done = () => { b.classList.add("done"); b.setAttribute("aria-label", "Link copied"); setTimeout(() => { b.classList.remove("done"); b.setAttribute("aria-label", "Copy link"); }, 1800); };
    if (navigator.clipboard) navigator.clipboard.writeText(location.href.split("#")[0]).then(done, () => {});
  }));

  // Product clip plays while on screen
  document.querySelectorAll(".cs2-fig video").forEach((v) => {
    if (reduce) return;
    const ob = io((es) => es.forEach((e) => { if (e.isIntersecting) { v.preload = "auto"; v.play().catch(() => {}); } else v.pause(); }), { threshold: 0.4 });
    if (ob) ob.observe(v);
  });

  // Hub: filter the grid by industry
  const filt = document.querySelector(".csh-filter");
  if (filt) {
    const btns = [...filt.querySelectorAll("button")];
    const cards = [...document.querySelectorAll(".csh-all .csc")];
    btns.forEach((b) => b.addEventListener("click", () => {
      btns.forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
      const f = b.dataset.f;
      cards.forEach((c) => { c.hidden = f !== "all" && c.dataset.ind !== f; });
    }));
  }
})();
