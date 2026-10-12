// Pascal Academy: scroll-spy, search filters, copy-prompt buttons, the PDF email gate and the workshop sign-up form.
(() => {
  // Forms post to the live site's mail route (same contract as the existing Academy sign-up form).
  const MAIL_API = "/api/mail";
  const RECAPTCHA_KEY = "6Ld0Bp4sAAAAAFMo6-sqVlHlb7qqwzQDuopcfjI8"; // public v3 site key used by pascalailabs.com
  const LIVE = /(^|\.)pascalailabs\.com$/.test(location.hostname);

  // ---------- scroll-spy for any [data-spy] list of #anchors
  document.querySelectorAll("[data-spy]").forEach((list) => {
    const links = [...list.querySelectorAll('a[href^="#"]')];
    const targets = links.map((a) => document.getElementById(a.getAttribute("href").slice(1))).filter(Boolean);
    if (!targets.length) return;
    const set = () => {
      const y = window.scrollY + 180;
      let cur = null;
      for (const t of targets) if (t.getBoundingClientRect().top + window.scrollY <= y) cur = t;
      links.forEach((a) => a.classList.toggle("active", !!cur && a.getAttribute("href") === "#" + cur.id));
    };
    let raf = 0;
    window.addEventListener("scroll", () => { cancelAnimationFrame(raf); raf = requestAnimationFrame(set); }, { passive: true });
    set();
  });

  // ---------- search: filters [data-item] in the target, hides empty [data-group], toggles .ac-empty
  document.querySelectorAll("input[data-filter]").forEach((input) => {
    const root = document.querySelector(input.dataset.filter);
    if (!root) return;
    const items = [...root.querySelectorAll("[data-item]")];
    const groups = [...root.querySelectorAll("[data-group]")];
    const empty = root.querySelector(".ac-empty");
    const text = new Map(items.map((el) => [el, el.textContent.toLowerCase().replace(/\s+/g, " ")]));
    input.addEventListener("input", () => {
      const words = input.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
      let shown = 0;
      items.forEach((el) => {
        const hit = !words.length || words.every((w) => text.get(el).includes(w));
        el.hidden = !hit;
        if (hit) shown++;
      });
      groups.forEach((g) => { g.hidden = !g.querySelector("[data-item]:not([hidden])"); });
      if (empty) empty.hidden = shown > 0;
    });
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") { e.preventDefault(); root.scrollIntoView({ behavior: "smooth", block: "start" }); }
    });
  });

  // ---------- copy prompt / show full prompt
  document.querySelectorAll("[data-copy]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const pre = btn.closest(".pc").querySelector("pre");
      const label = btn.textContent;
      try { await navigator.clipboard.writeText(pre.textContent.trim()); btn.textContent = "Copied"; }
      catch (e) { const r = document.createRange(); r.selectNodeContents(pre); const s = getSelection(); s.removeAllRanges(); s.addRange(r); btn.textContent = "Selected"; }
      setTimeout(() => { btn.textContent = label; }, 1800);
    });
  });
  document.querySelectorAll("[data-expand]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const pc = btn.closest(".pc");
      const open = pc.classList.toggle("open");
      btn.textContent = open ? "Show less" : "Show full prompt";
      if (!open) pc.scrollIntoView({ block: "nearest", behavior: "smooth" });
    });
  });

  // ---------- expanding tiles (featured rows)
  document.querySelectorAll(".tls").forEach((row) => {
    const tiles = [...row.querySelectorAll("[data-tile]")];
    const on = (t) => tiles.forEach((x) => x.classList.toggle("on", x === t));
    tiles.forEach((t) => { t.addEventListener("mouseenter", () => on(t)); t.addEventListener("focus", () => on(t)); });
  });

  // ---------- reading progress (bar under the nav + contents rail)
  const art = document.getElementById("article");
  if (art) {
    const bar = document.querySelector(".rp");
    const rail = document.querySelector(".toc-track");
    const links = rail ? [...rail.querySelectorAll("a")] : [];
    const tick = () => {
      const r = art.getBoundingClientRect();
      const p = Math.min(1, Math.max(0, (window.innerHeight * 0.35 - r.top) / r.height));
      if (bar) bar.style.setProperty("--p", (p * 100).toFixed(2) + "%");
      if (rail) {
        const act = rail.querySelector("a.active") || links[0];
        const li = act ? act.parentElement : null;
        const h = li ? li.offsetTop + li.offsetHeight : 0;
        rail.style.setProperty("--tp", (p >= 0.999 ? rail.offsetHeight : h) + "px");
      }
    };
    let raf = 0;
    window.addEventListener("scroll", () => { cancelAnimationFrame(raf); raf = requestAnimationFrame(tick); }, { passive: true });
    window.addEventListener("resize", tick);
    setTimeout(tick, 50);
  }

  // ---------- open a workflow when its anchor is targeted
  const openHash = () => {
    const el = location.hash && document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if (el && el.tagName === "DETAILS") el.open = true;
  };
  window.addEventListener("hashchange", openHash);
  openHash();

  // ---------- form helpers
  let recaptcha = null;
  const loadRecaptcha = () => {
    if (!LIVE) return Promise.resolve(null);
    if (!recaptcha) {
      recaptcha = new Promise((resolve) => {
        const s = document.createElement("script");
        s.src = "https://www.google.com/recaptcha/api.js?render=" + RECAPTCHA_KEY;
        s.async = true;
        s.onload = () => window.grecaptcha.ready(() => resolve(window.grecaptcha));
        s.onerror = () => resolve(null);
        document.head.appendChild(s);
      });
    }
    return recaptcha;
  };
  const token = async (action) => {
    const g = await loadRecaptcha();
    if (!g) return "";
    try { return await g.execute(RECAPTCHA_KEY, { action }); } catch (e) { return ""; }
  };
  const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  const validate = (form, rules) => {
    let msg = "";
    form.querySelectorAll("input, select").forEach((el) => el.removeAttribute("aria-invalid"));
    for (const [name, test, text] of rules) {
      const el = form.elements[name];
      if (el && !test((el.value || "").trim())) { el.setAttribute("aria-invalid", "true"); if (!msg) { msg = text; el.focus(); } }
    }
    const err = form.querySelector(".ac-gate-err");
    err.textContent = msg; err.hidden = !msg;
    return !msg;
  };
  const send = async (payload) => {
    const res = await fetch(MAIL_API, { method: "POST", credentials: "include", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
    if (res.status === 200) return true;
    let m = "Request failed (" + res.status + ")";
    try { const j = await res.json(); if (j && j.message) m = String(j.message); } catch (e) {}
    throw new Error(m);
  };
  // On the preview host there is no mail route yet; show the confirmation without sending.
  const submit = async (payload) => (LIVE ? send(payload) : (console.info("[academy] preview: would POST", MAIL_API, payload), true));

  // ---------- PDF gate
  const gate = document.getElementById("pdf-gate");
  if (gate) {
    const form = gate.querySelector("[data-gate-form]");
    const done = gate.querySelector(".ac-gate-done");
    const open = () => { loadRecaptcha(); if (gate.showModal) gate.showModal(); else gate.setAttribute("open", ""); setTimeout(() => form.elements.name && !done.hidden ? 0 : form.elements.name.focus(), 50); };
    const close = () => { if (gate.close) gate.close(); else gate.removeAttribute("open"); };
    document.querySelectorAll("[data-gate-open]").forEach((b) => b.addEventListener("click", open));
    gate.querySelectorAll("[data-gate-close]").forEach((b) => b.addEventListener("click", close));
    gate.addEventListener("click", (e) => { if (e.target === gate) close(); });
    if (location.hash === "#download") open();
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const ok = validate(form, [["name", (v) => v.length > 1, "Please enter your full name."],
        ["email", (v) => EMAIL.test(v), "Please enter a valid work email."],
        ["organization", (v) => v.length > 1, "Please enter your organization."]]);
      if (!ok) return;
      const btn = form.querySelector("button[type=submit]");
      btn.disabled = true;
      try {
        const f = form.elements;
        await submit({ formType: "academy_download", name: f.name.value.trim(), email: f.email.value.trim(),
          organization: f.organization.value.trim(), guide: form.dataset.guide, guideUrl: location.origin + location.pathname,
          pdfUrl: location.origin + form.dataset.pdf, recaptchaToken: await token("academy_download") });
        gate.querySelector("[data-gate-email]").textContent = f.email.value.trim();
        form.hidden = true; done.hidden = false;
      } catch (err) {
        const box = form.querySelector(".ac-gate-err"); box.textContent = "Could not send: " + err.message; box.hidden = false;
      } finally { btn.disabled = false; }
    });
  }

  // ---------- workshop sign-up (same payload as the live Next.js form)
  const su = document.querySelector("[data-signup-form]");
  if (su) {
    loadRecaptcha();
    su.addEventListener("submit", async (e) => {
      e.preventDefault();
      const ok = validate(su, [["name", (v) => /^[A-Za-z][A-Za-z .'-]+$/.test(v), "Full name is required (letters only)."],
        ["email", (v) => EMAIL.test(v), "Please enter a valid email address."],
        ["organization", (v) => v.length > 1, "Organization is required."],
        ["teamSize", (v) => !!v, "Team size is required."],
        ["phone", (v) => !v || /^\d{7,15}$/.test(v.replace(/[\s-]/g, "")), "Phone number must be between 7-15 digits."]]);
      if (!ok) return;
      const btn = su.querySelector("button[type=submit]");
      btn.disabled = true;
      try {
        const f = su.elements, cc = f.countryCode, phone = f.phone.value.replace(/[\s-]/g, "");
        await submit({ formType: "academy_signup", name: f.name.value.trim(), email: f.email.value.trim(), organization: f.organization.value.trim(),
          teamSize: f.teamSize.value, focus: f.focus.value, countryCode: cc.value, countryName: cc.selectedOptions[0].dataset.country,
          phoneNumber: phone ? cc.value + phone : "", recaptchaToken: await token("academy_signup") });
        su.hidden = true; su.parentElement.querySelector(".ac-form-done").hidden = false;
      } catch (err) {
        const box = su.querySelector(".ac-gate-err"); box.textContent = "Could not submit: " + err.message; box.hidden = false;
      } finally { btn.disabled = false; }
    });
  }
})();
