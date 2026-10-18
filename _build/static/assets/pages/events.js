// Event pages: the "Request an invitation" form. Posts to the live site's mail route (same contract as the Academy forms).
(() => {
  const MAIL_API = "/api/mail";
  const RECAPTCHA_KEY = "6Ld0Bp4sAAAAAFMo6-sqVlHlb7qqwzQDuopcfjI8"; // public v3 site key used by pascalailabs.com
  const LIVE = /(^|\.)pascalailabs\.com$/.test(location.hostname);

  const form = document.querySelector("[data-event-form]");
  if (!form) return;

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
  const send = async (payload) => {
    const res = await fetch(MAIL_API, { method: "POST", credentials: "include", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
    if (res.status === 200) return true;
    let m = "Request failed (" + res.status + ")";
    try { const j = await res.json(); if (j && j.message) m = String(j.message); } catch (e) {}
    throw new Error(m);
  };
  // On the preview host there is no mail route yet; show the confirmation without sending.
  const submit = async (payload) => (LIVE ? send(payload) : (console.info("[events] preview: would POST", MAIL_API, payload), true));

  const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  const rules = [
    ["name", (v) => /^[A-Za-z][A-Za-z .'-]+$/.test(v), "Full name is required (letters only)."],
    ["email", (v) => EMAIL.test(v), "Please enter a valid work email."],
    ["organization", (v) => v.length > 1, "Company name is required."],
    ["jobTitle", (v) => v.length > 1, "Job title is required."],
    ["phone", (v) => /^\d{7,15}$/.test(v.replace(/[\s-]/g, "")), "Phone number is required (7-15 digits)."],
  ];
  const err = form.querySelector(".ev-err");
  const validate = () => {
    let msg = "";
    form.querySelectorAll("input, select, textarea").forEach((el) => el.removeAttribute("aria-invalid"));
    for (const [name, test, text] of rules) {
      const el = form.elements[name];
      if (el && !test((el.value || "").trim())) { el.setAttribute("aria-invalid", "true"); if (!msg) { msg = text; el.focus(); } }
    }
    err.textContent = msg; err.hidden = !msg;
    return !msg;
  };

  form.addEventListener("focusin", loadRecaptcha, { once: true });
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!validate()) return;
    const btn = form.querySelector("button[type=submit]");
    btn.disabled = true;
    try {
      const f = form.elements, cc = f.countryCode, phone = f.phone.value.replace(/[\s-]/g, "");
      await submit({
        formType: "event_invite_request", event: form.dataset.event, eventName: form.dataset.eventName,
        eventCity: form.dataset.city, eventDate: form.dataset.date, pageUrl: location.origin + location.pathname,
        name: f.name.value.trim(), email: f.email.value.trim(), organization: f.organization.value.trim(),
        jobTitle: f.jobTitle.value.trim(), countryCode: cc.value, countryName: cc.selectedOptions[0].dataset.country,
        phoneNumber: phone ? cc.value + phone : "", topics: f.topics.value.trim(),
        recaptchaToken: await token("event_invite_request"),
      });
      form.hidden = true;
      const done = form.parentElement.querySelector(".ev-done");
      done.querySelector("[data-done-email]").textContent = f.email.value.trim();
      done.hidden = false;
    } catch (ex) {
      err.textContent = "Could not submit: " + ex.message; err.hidden = false;
    } finally { btn.disabled = false; }
  });
})();
