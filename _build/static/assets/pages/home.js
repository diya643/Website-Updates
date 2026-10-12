// Homepage interactions: logo marquee, product film (front, middle, back office), live counter,
// stat count-up, and the "What sets Pascal apart" panel.
(function () {
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const onView = (el, cb, opts) => {
    if (!("IntersectionObserver" in window)) { cb(true); return; }
    new IntersectionObserver((es) => es.forEach((e) => cb(e.isIntersecting)), opts || { threshold: 0.35 }).observe(el);
  };

  // Logo marquee: second set mirrors the first so the loop is seamless
  document.querySelectorAll(".hm-logos-track").forEach((t) => {
    const [a, b] = t.querySelectorAll(".hm-logos-set");
    if (a && b) b.innerHTML = a.innerHTML.replace(/ alt="[^"]*"/g, ' alt=""');
  });

  // Product film: for each desk, type the question, then show the answer; loops while on screen
  const app = document.querySelector("[data-film]");
  if (app) {
    const typed = app.querySelector(".hm-typed");
    const qs = [...app.querySelectorAll(".hm-s1")].map((s) => s.dataset.q);
    let timers = [], running = false, task = 0;
    const later = (fn, ms) => timers.push(setTimeout(fn, ms));
    const clear = () => { timers.forEach(clearTimeout); timers = []; };
    const setTask = (k) => {
      task = k;
      app.dataset.task = String(k);
    };
    const run = () => {
      clear();
      app.classList.remove("sent");
      app.dataset.step = "0";
      const text = qs[task];
      typed.textContent = "";
      if (reduce) { typed.textContent = text; app.dataset.step = "1"; later(() => { setTask((task + 1) % qs.length); run(); }, 9000); return; }
      let i = 0;
      const type = () => {
        typed.textContent = text.slice(0, ++i);
        if (i < text.length) later(type, 22 + Math.random() * 26);
        else later(() => {
          app.classList.add("sent");
          later(() => { app.dataset.step = "1"; }, 420);
          later(() => { setTask((task + 1) % qs.length); run(); }, 9200);
        }, 450);
      };
      later(type, 600);
    };
    setTask(0);
    onView(app, (vis) => {
      if (vis && !running) { running = true; run(); }
      else if (!vis && running) { running = false; clear(); }
    }, { threshold: 0.3 });
  }

  // Live counter: pages indexed ticks up while visible
  const cnt = document.querySelector(".hm-count-n[data-count]");
  if (cnt) {
    let n = +cnt.dataset.count, t = null;
    onView(cnt, (vis) => {
      clearInterval(t);
      if (vis && !reduce) t = setInterval(() => { n += 1 + Math.floor(Math.random() * 7); cnt.textContent = n.toLocaleString("en-GB"); }, 260);
    }, { threshold: 0 });
  }

  // Stats: count up once when the grid comes into view
  document.querySelectorAll(".hm-n[data-to]").forEach((el) => {
    if (reduce) return;
    const to = +el.dataset.to, dec = +(el.dataset.dec || 0), pre = el.dataset.pre || "", suf = el.dataset.suf || "";
    const final = el.textContent;
    let done = false;
    onView(el, (vis) => {
      if (!vis || done) return;
      done = true;
      const t0 = performance.now(), dur = 1400;
      const step = (now) => {
        const p = Math.min(1, (now - t0) / dur), e = 1 - Math.pow(1 - p, 3);
        el.textContent = p < 1 ? pre + (to * e).toFixed(dec) + suf : final;
        if (p < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    });
  });

  // What sets Pascal apart: the list switches the product clip and the product link; advances every 8s while visible
  const tour = document.querySelector("[data-tour]");
  if (tour) {
    const btns = [...tour.querySelectorAll(".gt-list button")];
    const panes = btns.map((b) => document.getElementById(b.dataset.pane));
    const link = tour.querySelector(".gt-link");
    let cur = 0, t = null, vis = false, hover = false;
    const play = () => panes.forEach((p, k) => {
      const v = p.querySelector("video");
      if (!v) return;
      if (k === cur && vis && !reduce) { v.preload = "auto"; v.play().catch(() => {}); }
      else v.pause();
    });
    const show = (i) => {
      cur = (i + btns.length) % btns.length;
      btns.forEach((b, k) => {
        const on = k === cur;
        b.classList.toggle("on", on);
        b.setAttribute("aria-pressed", String(on));
        panes[k].classList.toggle("on", on);
      });
      const v = panes[cur].querySelector("video");
      if (v) v.currentTime = 0;
      link.href = btns[cur].dataset.href;
      play(); schedule();
    };
    const schedule = () => {
      clearTimeout(t);
      tour.classList.toggle("paused", hover || !vis);
      if (vis && !hover && !reduce) t = setTimeout(() => show(cur + 1), 8000);
    };
    btns.forEach((b, k) => b.addEventListener("click", () => show(k)));
    tour.addEventListener("mouseenter", () => { hover = true; schedule(); });
    tour.addEventListener("mouseleave", () => { hover = false; schedule(); });
    onView(tour, (v) => { vis = v; play(); schedule(); }, { threshold: 0.25 });
  }
  // Feature clips: play while on screen, pause when off
  document.querySelectorAll(".hm-fx video").forEach((v) => {
    if (reduce) return;
    onView(v, (vis) => { if (vis) { v.preload = "auto"; v.play().catch(() => {}); } else v.pause(); }, { threshold: 0.4 });
  });
})();
