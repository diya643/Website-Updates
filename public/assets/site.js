// Pascal AI — website v2 interactions. No dependencies.
(function () {
  const nav = document.querySelector(".nav");

  // Nav: transparent over the dark hero, frosted paper once scrolled
  if (nav && !nav.classList.contains("solid")) {
    const onScroll = () => nav.classList.toggle("scrolled", window.scrollY > 24);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  // Mega menus: hover on pointer devices, click/keyboard everywhere
  document.querySelectorAll(".nav-item[data-menu]").forEach((item) => {
    const btn = item.querySelector(".nav-link");
    let t;
    const open = () => {
      clearTimeout(t);
      document.querySelectorAll(".nav-item.open").forEach((o) => o !== item && close(o));
      item.classList.add("open");
      btn.setAttribute("aria-expanded", "true");
    };
    const close = (el = item) => {
      el.classList.remove("open");
      el.querySelector(".nav-link").setAttribute("aria-expanded", "false");
    };
    item.addEventListener("mouseenter", open);
    item.addEventListener("mouseleave", () => { t = setTimeout(() => close(), 140); });
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      item.classList.contains("open") ? close() : open();
    });
    item.addEventListener("keydown", (e) => {
      if (e.key === "Escape") { close(); btn.focus(); }
    });
    item.addEventListener("focusout", (e) => {
      if (!item.contains(e.relatedTarget)) close();
    });
  });

  // Mobile menu
  const burger = document.querySelector(".nav-burger");
  const mm = document.querySelector(".mobile-menu");
  if (burger && mm) {
    burger.addEventListener("click", () => {
      const isOpen = mm.classList.toggle("open");
      burger.setAttribute("aria-expanded", String(isOpen));
      nav.classList.toggle("solid", isOpen || window.scrollY > 24);
      document.body.style.overflow = isOpen ? "hidden" : "";
    });
  }

  // Tabs: any [role=tablist] controls its tabpanels via aria-controls
  document.querySelectorAll('[role="tablist"]').forEach((list) => {
    const tabs = [...list.querySelectorAll('[role="tab"]')];
    const select = (tab) => {
      tabs.forEach((t) => {
        const on = t === tab;
        t.setAttribute("aria-selected", String(on));
        t.tabIndex = on ? 0 : -1;
        const panel = document.getElementById(t.getAttribute("aria-controls"));
        if (panel) panel.hidden = !on;
      });
    };
    tabs.forEach((tab, i) => {
      tab.addEventListener("click", () => select(tab));
      tab.addEventListener("keydown", (e) => {
        const d = e.key === "ArrowRight" || e.key === "ArrowDown" ? 1 : e.key === "ArrowLeft" || e.key === "ArrowUp" ? -1 : 0;
        if (!d) return;
        e.preventDefault();
        const next = tabs[(i + d + tabs.length) % tabs.length];
        select(next);
        next.focus();
      });
    });
  });

  // Carousels
  document.querySelectorAll("[data-carousel]").forEach((root) => {
    const track = root.querySelector(".track");
    const prev = root.querySelector("[data-prev]");
    const next = root.querySelector("[data-next]");
    const step = () => track.firstElementChild.getBoundingClientRect().width + 20;
    const sync = () => {
      prev.disabled = track.scrollLeft < 8;
      next.disabled = track.scrollLeft + track.clientWidth > track.scrollWidth - 8;
    };
    prev.addEventListener("click", () => track.scrollBy({ left: -step() }));
    next.addEventListener("click", () => track.scrollBy({ left: step() }));
    track.addEventListener("scroll", sync, { passive: true });
    window.addEventListener("resize", sync);
    sync();
  });

  // In-page sub-nav: highlight the section in view
  const sub = document.querySelector(".subnav");
  if (sub && "IntersectionObserver" in window) {
    const links = [...sub.querySelectorAll('a[href^="#"]')];
    const map = new Map(links.map((a) => [a.getAttribute("href").slice(1), a]));
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (en.isIntersecting) {
          links.forEach((l) => l.classList.remove("active"));
          const a = map.get(en.target.id);
          if (a) {
            a.classList.add("active");
            a.scrollIntoView({ block: "nearest", inline: "nearest" });
          }
        }
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    map.forEach((_, id) => { const s = document.getElementById(id); if (s) io.observe(s); });
  }

  // Flip cards: tap / Enter to flip (hover handles pointer devices)
  document.querySelectorAll(".cap.flip").forEach((c) => {
    c.addEventListener("click", (e) => { if (!c.getAttribute("href")) { e.preventDefault(); c.classList.toggle("flipped"); } });
    c.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); c.classList.toggle("flipped"); } });
  });

  // Connector browser: category filter, search, count, detail sheet
  document.querySelectorAll("[data-connectors]").forEach((root) => {
    const cats = [...root.querySelectorAll(".cx-cat")];
    const cards = [...root.querySelectorAll(".cx-card")];
    const input = root.querySelector(".cx-search input");
    const count = root.querySelector(".cx-count span");
    const empty = root.querySelector(".cx-empty");
    const sheet = root.parentElement.querySelector(".cx-sheet");
    let cat = "all";
    const apply = () => {
      const q = (input.value || "").trim().toLowerCase();
      let n = 0;
      cards.forEach((c) => {
        const show = (cat === "all" || c.dataset.cat === cat) && (!q || c.dataset.name.includes(q) || c.dataset.catname.toLowerCase().includes(q));
        c.hidden = !show;
        if (show) n++;
      });
      count.textContent = n;
      empty.hidden = n !== 0;
    };
    cats.forEach((b) => b.addEventListener("click", () => {
      cat = b.dataset.cat;
      cats.forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
      apply();
    }));
    input.addEventListener("input", apply);
    cards.forEach((c) => c.addEventListener("click", () => {
      if (!sheet || !sheet.showModal) return;
      sheet.querySelector(".cx-sheet-logo").innerHTML = c.querySelector(".cx-logo").outerHTML;
      sheet.querySelector(".cx-sheet-cat").textContent = c.dataset.catname;
      sheet.querySelector("h3").textContent = c.querySelector(".cx-name").textContent;
      sheet.querySelector(".cx-sheet-desc").textContent = c.dataset.desc;
      sheet.showModal();
    }));
    if (sheet) sheet.addEventListener("click", (e) => { if (e.target === sheet) sheet.close(); });
  });

  // Interactive workflow run (Event Brief demo)
  document.querySelectorAll("[data-wf-demo]").forEach((root) => {
    const sel = root.querySelector("select");
    const run = root.querySelector(".wf-run");
    const steps = [...root.querySelectorAll(".wf-steps li")];
    const bar = root.querySelector(".wf-bar i");
    const pct = root.querySelector(".wf-pct");
    const names = root.querySelectorAll(".wf-co");
    const quick = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let timer;
    const sync = () => { run.disabled = !sel.value; };
    const set = (st) => { root.dataset.state = st; };
    sel.addEventListener("change", sync);
    root.querySelector(".wf-clear").addEventListener("click", () => { sel.value = ""; sync(); sel.focus(); });
    const again = root.querySelector(".wf-again");
    if (again) again.addEventListener("click", () => { set("setup"); sel.focus(); });
    run.addEventListener("click", () => {
      if (!sel.value) return;
      names.forEach((n) => (n.textContent = sel.value));
      steps.forEach((li) => (li.className = ""));
      bar.style.width = "0%"; pct.textContent = "0%";
      set("running");
      let i = 0;
      const tick = () => {
        if (i > 0) steps[i - 1].className = "ok";
        if (i === steps.length) { bar.style.width = "100%"; pct.textContent = "100%"; timer = setTimeout(() => set("done"), quick ? 0 : 450); return; }
        steps[i].className = "on";
        const p = Math.round((i / steps.length) * 100);
        bar.style.width = p + "%"; pct.textContent = p + "%";
        i++;
        timer = setTimeout(tick, quick ? 0 : 750);
      };
      clearTimeout(timer); tick();
    });
    sync();
  });

  // Reveal on scroll
  const rev = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
    }, { rootMargin: "0px 0px -8% 0px" });
    rev.forEach((el) => io.observe(el));
  } else {
    rev.forEach((el) => el.classList.add("in"));
  }
})();

// Use-case player: [data-ucp] cycles its .ucp-scene children like a ~30s GIF.
// Builds the step track from each scene's data-label, plays only while on screen,
// restarts when it becomes visible (e.g. a newly selected office tab), pauses on hover or the play button.
(function () {
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const fmt = (ms) => { const s = Math.round(ms / 1000); return Math.floor(s / 60) + ":" + String(s % 60).padStart(2, "0"); };
  document.querySelectorAll("[data-ucp]").forEach((root) => {
    const scenes = [...root.querySelectorAll(".ucp-scene")];
    if (!scenes.length) return;
    const durs = scenes.map((s) => +(s.dataset.dur || 6000));
    const total = durs.reduce((a, b) => a + b, 0);
    const track = root.querySelector(".ucp-track");
    const time = root.querySelector(".ucp-time");
    const pp = root.querySelector(".ucp-pp");
    const segs = scenes.map((s, i) => {
      const b = document.createElement("button");
      b.type = "button"; b.className = "ucp-seg"; b.style.setProperty("--dur", durs[i] + "ms");
      b.setAttribute("aria-label", "Step " + (i + 1) + ": " + (s.dataset.label || ""));
      b.innerHTML = "<i></i><span>" + (s.dataset.label || "") + "</span>";
      b.addEventListener("click", () => { go(i); });
      track && track.appendChild(b);
      return b;
    });
    let cur = -1, timer = null, started = 0, left = 0, paused = false, hover = false, visible = false, tick = null;
    const elapsedBefore = (i) => durs.slice(0, i).reduce((a, b) => a + b, 0);
    function show(i) {
      cur = i;
      scenes.forEach((s, k) => {
        s.classList.remove("on");
        if (k === i) { void s.offsetWidth; s.classList.add("on"); }
      });
      segs.forEach((g, k) => {
        g.classList.toggle("done", k < i);
        g.classList.remove("on");
        if (k === i) { void g.offsetWidth; g.classList.add("on"); }
      });
    }
    function schedule(ms) {
      clearTimeout(timer);
      started = Date.now(); left = ms;
      timer = setTimeout(() => go((cur + 1) % scenes.length), ms);
    }
    function go(i) {
      show(i);
      if (reduce) { if (time) time.textContent = "Step " + (i + 1) + " of " + scenes.length; return; }
      if (paused || hover || !visible) { left = durs[i]; started = Date.now(); clearTimeout(timer); return; }
      schedule(durs[i]);
    }
    function stop() { if (timer) { clearTimeout(timer); timer = null; left = Math.max(0, left - (Date.now() - started)); } }
    function resume() { if (!reduce && !paused && !hover && visible && cur >= 0) schedule(left); }
    const setPaused = () => root.classList.toggle("paused", paused || hover);
    if (time && !reduce) tick = setInterval(() => {
      if (cur < 0) return;
      const run = (paused || hover || !visible) ? durs[cur] - left : Math.min(durs[cur], Date.now() - started + (durs[cur] - left));
      time.textContent = fmt(elapsedBefore(cur) + Math.max(0, run)) + " / " + fmt(total);
    }, 250);
    pp && pp.addEventListener("click", () => { paused = !paused; setPaused(); paused ? stop() : resume(); });
    root.addEventListener("mouseenter", () => { hover = true; setPaused(); stop(); });
    root.addEventListener("mouseleave", () => { hover = false; setPaused(); resume(); });
    if ("IntersectionObserver" in window) {
      new IntersectionObserver((es) => es.forEach((e) => {
        const was = visible; visible = e.isIntersecting;
        if (visible && !was) go(0);            // replay from the start whenever it comes into view
        else if (!visible && was) stop();
      }), { threshold: 0.35 }).observe(root);
    } else { visible = true; go(0); }
    if (cur < 0) show(0);
  });
})();

// Industries menu: hovering or focusing an industry shows its detail pane (first one shows without JS)
(function () {
  document.querySelectorAll(".mega-ind").forEach((m) => {
    const items = m.querySelectorAll(".ind-item"), panes = m.querySelectorAll(".ind-pane");
    const show = (k) => {
      items.forEach((i) => i.classList.toggle("on", i.dataset.ind === k));
      panes.forEach((p) => p.classList.toggle("on", p.dataset.pane === k));
    };
    items.forEach((i) => ["mouseenter", "focus"].forEach((ev) => i.addEventListener(ev, () => show(i.dataset.ind))));
  });
})();

// Context graph (Digital Twin): play the build-up once it scrolls into view
(function () {
  const els = document.querySelectorAll("[data-cgt]");
  if (!("IntersectionObserver" in window)) { els.forEach((e) => e.classList.add("play")); return; }
  const io = new IntersectionObserver((es) => es.forEach((e) => {
    if (e.isIntersecting) { e.target.classList.add("play"); io.unobserve(e.target); }
  }), { threshold: 0.3 });
  els.forEach((e) => io.observe(e));
})();
