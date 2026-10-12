// Pascal Data Agent: interactive vault viewer on /pascal-agents/data-agent#vault-viewer.
// Vanilla JS, no dependencies. Illustrative sample data. The page ships a static render of the
// default view (All documents, last 90 days) inside [data-vv]; this script replaces it with the live app.
(function () {
  "use strict";
  const root = document.querySelector("[data-vv]");
  if (!root) return;

  /* ------------------------------------------------------------------ sample data */
  const TODAY = new Date("2026-10-07T12:00:00");
  const TYPES = {
    all:    { label: "All documents", pill: "All", one: "document", many: "documents", src: "All sources", vault: "6,711", dateL: "Date", hidden: 3, why: "unlicensed broker, restricted note", fl: "Type" },
    broker: { label: "Broker reports", pill: "Broker report", one: "broker report", many: "broker reports", src: "BluMatrix", vault: "4,212", sync: "12 min ago", dateL: "Published", hidden: 2, why: "unlicensed broker", fl: "Broker" },
    expert: { label: "Expert calls", pill: "Expert call", one: "expert call", many: "expert calls", src: "Expert network transcripts", vault: "1,947", sync: "1 hr ago", dateL: "Call date", hidden: 0, fl: "Relationship" },
    note:   { label: "Internal research notes", pill: "Research note", one: "research note", many: "research notes", src: "SharePoint", vault: "538", sync: "35 min ago", dateL: "Written", hidden: 1, why: "restricted note", fl: "Stance" },
    unc:    { label: "Unclassified", pill: "Unclassified", one: "unclassified file", many: "unclassified files", src: "No type assigned", vault: "14", sync: "35 min ago", dateL: "Created", hidden: 0, fl: "Suggested type" }
  };
  const ENT = {
    NVDA: { name: "NVIDIA Corporation", sec: "Semiconductors", alias: "nvidia, blackwell, blackwell ultra, gb300, h20" },
    TSM:  { name: "Taiwan Semiconductor Mfg.", sec: "Semiconductors", alias: "tsmc, 2330.tw, cowos" },
    AMD:  { name: "Advanced Micro Devices", sec: "Semiconductors", alias: "amd, mi400, instinct" },
    AVGO: { name: "Broadcom Inc.", sec: "Semiconductors", alias: "broadcom, vmware" },
    MU:   { name: "Micron Technology", sec: "Semiconductors", alias: "micron, hbm4" },
    ASML: { name: "ASML Holding", sec: "Semiconductor equipment", alias: "asml, high-na, euv" },
    MSFT: { name: "Microsoft Corporation", sec: "Software & cloud", alias: "microsoft, azure" }
  };
  const D = [
    { id: "b1", t: "broker", title: "US Semis: AI capex tracker, Q3 update", date: "2026-09-30", org: "Goldman Sachs", rtype: "Sector", pages: 44,
      ents: { NVDA: "p", AMD: "p", TSM: "p", AVGO: "p", MU: "p" }, rate: { NVDA: ["Buy", 245, 15], AMD: ["Neutral", 185, 0], TSM: ["Buy", 265, 10], AVGO: ["Buy", 390, 5], MU: ["Buy", 160, 0] },
      sum: "Sector update across AI compute, foundry and memory. Raises estimates on supply-chain checks.",
      spans: {
        NVDA: { loc: "pp. 9–11 of 44 · “NVIDIA: supply sets the pace”", text: "We raise our NVDA PT to $245 (from $230). Blackwell Ultra shipments tracked ahead of our model in August, and our supply-chain checks point to CoWoS-L as the binding constraint through 1H27. We now model data center revenue of $61B for FQ3.", hl: ["NVDA", "Blackwell Ultra", "CoWoS-L"], via: [["Ticker", "NVDA", 9], ["Product line", "Blackwell Ultra → NVIDIA", 8], ["Name variant", "Nvidia", 6]] },
        AMD: { loc: "pp. 12–13 of 44 · “AMD: MI400 timing is the swing factor”", text: "We keep AMD at Neutral with a $185 PT. MI400 sampling has moved to late Q4 in our checks. A clean ramp in 1H27 is missing from consensus, which leaves room for upside if timing holds.", hl: ["AMD", "MI400"], via: [["Ticker", "AMD", 7], ["Product line", "MI400 → AMD", 5]] },
        TSM: { loc: "pp. 20–22 of 44 · “Foundry”", text: "TSMC remains our top pick in foundry. CoWoS capacity reaching about 95k wafers per month by end-2027 supports both the NVIDIA and Broadcom ramps.", hl: ["TSMC", "CoWoS"], via: [["Name variant", "TSMC", 11], ["Ticker", "TSM", 3]] } } },
    { id: "b2", t: "broker", title: "NVIDIA: Blackwell Ultra ramp ahead of plan", date: "2026-09-29", org: "J.P. Morgan", rtype: "Update", pages: 14, ents: { NVDA: "p", TSM: "m" }, rate: { NVDA: ["Overweight", 250, 20] },
      sum: "Raises FQ3 and FQ4 estimates on GB300 rack shipments. Gross margin held at 74% through the product transition.",
      spans: {
        NVDA: { loc: "pp. 1–3 of 14 · Summary", text: "We raise our NVDA December-2027 PT to $250. GB300 rack shipments ran roughly 15% above our prior estimate in August, and gross margin held at 74% despite the product transition.", hl: ["NVDA", "GB300"], via: [["Ticker", "NVDA", 14], ["Product line", "GB300 → NVIDIA", 9]] },
        TSM: { loc: "p. 8 of 14 · Supply chain", text: "TSMC CoWoS allocation to NVIDIA rises again in 1H27, per our checks.", hl: ["TSMC", "CoWoS"], via: [["Name variant", "TSMC", 2]] } } },
    { id: "b10", t: "broker", title: "Microsoft: Azure capacity constraints ease in 1H27", date: "2026-10-01", org: "Bernstein", rtype: "Update", pages: 18, ents: { MSFT: "p", NVDA: "m" }, rate: { MSFT: ["Outperform", 560, 20] },
      sum: "Azure growth re-accelerates as new data center capacity comes online in 1H27.",
      spans: { NVDA: { loc: "p. 9 of 18 · “Supply”", text: "Microsoft remains one of the largest buyers of NVIDIA GB300 racks in our model, with power availability pacing deployment.", hl: ["NVIDIA", "GB300"], via: [["Name variant", "NVIDIA", 4]] } } },
    { id: "b3", t: "broker", title: "TSMC: CoWoS capacity raise and 2027 outlook", date: "2026-09-26", org: "Morgan Stanley", rtype: "Update", pages: 22, ents: { TSM: "p", NVDA: "m", AVGO: "m" }, rate: { TSM: ["Overweight", 265, 10] },
      sum: "Raises 2027 CoWoS capacity estimate. AI accelerator revenue now 28% of 2027 sales.",
      spans: {
        NVDA: { loc: "p. 6 of 22 · “Customer mix”", text: "We estimate NVIDIA takes about 60% of CoWoS-L output in 2027, down from 65% as custom ASIC programs scale. NVIDIA volumes still grow; the change is in mix.", hl: ["NVIDIA", "CoWoS-L"], via: [["Name variant", "NVIDIA", 4]] },
        TSM: { loc: "pp. 1–4 of 22 · Summary", text: "We raise TSMC 2027 CoWoS capacity to 95k wafers per month and our ADR PT to $265. Advanced packaging is now the gating factor for AI accelerator supply.", hl: ["TSMC", "CoWoS"], via: [["Name variant", "TSMC", 21], ["Ticker", "TSM", 6]] } } },
    { id: "b4", t: "broker", title: "AMD: MI400 checks mixed, stay on the sidelines", date: "2026-09-24", org: "UBS", rtype: "Update", pages: 11, ents: { AMD: "p", NVDA: "m" }, rate: { AMD: ["Neutral", 180, -10] },
      sum: "Cuts PT on later MI400 timing. Share gain versus NVIDIA pushed to 2H27.",
      spans: {
        NVDA: { loc: "p. 5 of 11 · “Competitive position”", text: "Hyperscaler buyers told us NVIDIA remains the default for training clusters through 2027. MI400 wins are concentrated in inference.", hl: ["NVIDIA"], via: [["Name variant", "NVIDIA", 3]] },
        AMD: { loc: "pp. 1–2 of 11 · Summary", text: "We lower our AMD PT to $180 (from $190). MI400 volume shipments now look like a 2H27 event in our checks.", hl: ["AMD", "MI400"], via: [["Ticker", "AMD", 12]] } } },
    { id: "b9", t: "broker", title: "ASML: High-NA orders pull forward", date: "2026-09-23", org: "Barclays", rtype: "Update", pages: 20, ents: { ASML: "p", TSM: "m" }, rate: { ASML: ["Overweight", 1050, 50] },
      sum: "Two more High-NA orders in Q3. Raises 2027 EUV shipment estimate to 62 tools.",
      spans: { TSM: { loc: "p. 7 of 20 · “Customer adoption”", text: "We now expect TSMC to take its first High-NA tools in 2H27 for A14 development.", hl: ["TSMC", "High-NA"], via: [["Name variant", "TSMC", 3]] } } },
    { id: "b5", t: "broker", title: "Memory: HBM4 pricing reset for 2027", date: "2026-09-19", org: "Deutsche Bank", rtype: "Sector", pages: 26, ents: { MU: "p", NVDA: "m" }, rate: { MU: ["Buy", 165, 5] },
      sum: "HBM4 contract pricing for 2027 settles higher than feared.",
      spans: { NVDA: { loc: "p. 14 of 26 · “Customer negotiations”", text: "NVIDIA accepted a mid-single-digit HBM4 price increase for 2027 in exchange for volume commitments, per our checks.", hl: ["NVIDIA", "HBM4"], via: [["Name variant", "NVIDIA", 2]] } } },
    { id: "b6", t: "broker", title: "Broadcom: custom ASIC pipeline widens", date: "2026-09-12", org: "Goldman Sachs", rtype: "Update", pages: 16, ents: { AVGO: "p" }, rate: { AVGO: ["Buy", 390, 0] },
      sum: "Custom accelerator pipeline now spans five hyperscale customers.", spans: {} },
    { id: "b7", t: "broker", title: "Semis flash: revised export licence rules", date: "2026-09-05", org: "J.P. Morgan", rtype: "Flash", pages: 3, ents: { NVDA: "p", AMD: "p" }, rate: { NVDA: ["Overweight", 230, 0], AMD: ["Neutral", 190, 0] },
      sum: "First read on the revised export licence framework. Sees a $1–2B annual headwind for NVIDIA.",
      spans: { NVDA: { loc: "pp. 1–2 of 3", text: "The new licence framework caps shipments of H20-class parts to restricted markets. We see a $1–2B annual revenue headwind for NVIDIA, already in our numbers.", hl: ["NVIDIA", "H20"], via: [["Name variant", "NVIDIA", 5], ["Product line", "H20 → NVIDIA", 2]] } } },
    { id: "b8", t: "broker", title: "NVIDIA: the gross margin debate", date: "2026-09-04", org: "Morgan Stanley", rtype: "Update", pages: 18, ents: { NVDA: "p" }, rate: { NVDA: ["Equal-weight", 220, -5] },
      sum: "Argues rack-scale mix caps gross margin near 73%.",
      spans: { NVDA: { loc: "pp. 1–4 of 18 · Summary", text: "We trim our NVDA PT to $220. Rack-scale systems carry more pass-through content, and we think gross margin settles near 73%, below the 75% peak.", hl: ["NVDA"], via: [["Ticker", "NVDA", 16]] } } },

    { id: "e5", t: "expert", title: "Azure capacity planning for 2027", date: "2026-09-29", expert: "Former Director, Datacenter Planning", emp: "Microsoft", vendor: "GLG", by: "AL", mins: 47, ents: { MSFT: "p", NVDA: "m", AMD: "m" },
      rel: { MSFT: "Ex-employee", NVDA: "Customer view", AMD: "Customer view" }, sum: "How a hyperscaler sizes GPU orders against power and site availability.",
      spans: { NVDA: { loc: "21:30–26:00 of 47:00", text: "Expert: “Power sets our 2027 build. We have NVIDIA allocation we cannot energise until new sites come online in the second half.”", hl: ["NVIDIA"], via: [["Name variant", "NVIDIA", 8]] } } },
    { id: "e1", t: "expert", title: "CoWoS capacity and allocation into 2027", date: "2026-09-25", expert: "Former Director, Advanced Packaging", emp: "TSMC", vendor: "Third Bridge", by: "RK", mins: 52, ents: { TSM: "p", NVDA: "p", AVGO: "m" },
      rel: { TSM: "Ex-employee", NVDA: "Supplier view", AVGO: "Supplier view" }, sum: "Capacity build, allocation process and customer mix for advanced packaging.",
      spans: {
        NVDA: { loc: "14:10–19:40 of 52:00", text: "Expert: “NVIDIA books capacity eighteen months out. For 2027 they locked in the majority of CoWoS-L early, and the allocation meetings are really about who gets the incremental lines.”", hl: ["NVIDIA", "CoWoS-L"], via: [["Name variant", "NVIDIA", 17]] },
        TSM: { loc: "02:30–11:05 of 52:00", text: "Expert: “The 2027 target is achievable. Tool orders for the new packaging lines went in during Q2, and the constraint now is qualified substrate supply.”", hl: ["packaging"], via: [["Employer", "Former TSMC", 1], ["Name variant", "TSMC", 22]] } } },
    { id: "e2", t: "expert", title: "Hyperscaler GPU procurement for 2027", date: "2026-09-17", expert: "Former Procurement Lead, Cloud Infrastructure", emp: "Hyperscaler (US)", vendor: "Tegus", by: "SP", mins: 45, ents: { NVDA: "p", AMD: "p", AVGO: "p" },
      rel: { NVDA: "Customer", AMD: "Customer", AVGO: "Customer" }, sum: "How a large cloud buyer splits spend between merchant GPUs and custom silicon.",
      spans: { NVDA: { loc: "05:00–16:20 of 45:00", text: "Expert: “Training stays on NVIDIA. Where we moved spend is inference, and that went to our own ASIC first, then AMD. NVIDIA pricing did not move in the last negotiation.”", hl: ["NVIDIA"], via: [["Name variant", "NVIDIA", 21]] } } },
    { id: "e6", t: "expert", title: "EUV tool lead times and High-NA adoption", date: "2026-09-15", expert: "Former Account Manager, EUV", emp: "ASML", vendor: "Third Bridge", by: "SP", mins: 36, ents: { ASML: "p", TSM: "m" },
      rel: { ASML: "Ex-employee", TSM: "Customer view" }, sum: "Order book, lead times and which fabs adopt High-NA first.",
      spans: { TSM: { loc: "12:00–17:45 of 36:00", text: "Expert: “TSMC will be a fast follower on High-NA. They want the tool proven on another fab’s line first.”", hl: ["TSMC"], via: [["Name variant", "TSMC", 6]] } } },
    { id: "e4", t: "expert", title: "Substrate supply for AI accelerators", date: "2026-09-09", expert: "Engineering Manager, OSAT supplier", emp: "OSAT supplier (Taiwan)", vendor: "Third Bridge", by: "SP", mins: 38, ents: { TSM: "p", NVDA: "m" },
      rel: { TSM: "Supplier view", NVDA: "Supplier view" }, sum: "ABF substrate lead times and qualification.",
      spans: { NVDA: { loc: "19:00–22:30 of 38:00", text: "Expert: “Blackwell Ultra substrates need a new qualification cycle. We shipped first lots in July, volume in October.”", hl: ["Blackwell Ultra"], via: [["Product line", "Blackwell Ultra → NVIDIA", 4]] } } },
    { id: "e3", t: "expert", title: "MI400 customer pipeline", date: "2026-09-06", expert: "Former Sales Director, Data Center", emp: "AMD", vendor: "AlphaSights", by: "RK", mins: 40, ents: { AMD: "p", NVDA: "m" },
      rel: { AMD: "Ex-employee", NVDA: "Competitor view" }, sum: "AMD accelerator pipeline and competitive dynamics with NVIDIA.",
      spans: { NVDA: { loc: "27:45–31:10 of 40:00", text: "Expert: “Every deal we lost, we lost on software and networking. NVIDIA sells the whole rack. That gap is closing.”", hl: ["NVIDIA"], via: [["Name variant", "NVIDIA", 9]] } } },

    { id: "m6", t: "note", title: "Semis: Q4 positioning review", date: "2026-10-03", ntype: "IC", stance: "Mixed", conv: "Medium", cat: "NVDA Q3 print; MI400 sampling; HBM4 contracts", by: "RK", ents: { NVDA: "p", AMD: "p", TSM: "p", MU: "m" },
      sum: "Stay long NVDA and TSM, keep AMD short into the MI400 slip. Trim MU on HBM pricing.",
      spans: { NVDA: { loc: "p. 1 of 5 · Book summary", text: "NVDA stays our largest long. Supply sets the pace through 1H27 and we add on any pullback below $200.", hl: ["NVDA"], via: [["Ticker", "NVDA", 7]] } } },
    { id: "m4", t: "note", title: "MSFT: capex digestion fears are early", date: "2026-10-01", ntype: "Update", stance: "Long", conv: "Medium", cat: "FQ1 Azure growth; 2027 capex guide", by: "AL", ents: { MSFT: "p", NVDA: "m" },
      sum: "Azure capacity comes online in 1H27. Argues the market prices capex digestion two quarters too early.",
      spans: { NVDA: { loc: "p. 2 of 3 · “Supply”", text: "Microsoft GPU orders, mostly NVIDIA, stay on plan. Power is the gating item.", hl: ["NVIDIA"], via: [["Name variant", "NVIDIA", 2]] } } },
    { id: "m1", t: "note", title: "NVDA: Q3 update, raising conviction", date: "2026-09-27", ntype: "Update", stance: "Long", conv: "High", cat: "Q3 print Nov 19; GB300 volume", by: "RK", ents: { NVDA: "p", TSM: "m" },
      sum: "Thesis intact: supply is the constraint. Raises conviction to High and model PT to $240.",
      spans: { NVDA: { loc: "Full note · 3 pages", text: "Thesis intact. Supply is the constraint. Our checks and two expert calls this month agree on CoWoS-L allocation. Raising conviction to High; model PT moves to $240. Key risk is gross margin mix from rack-scale systems.", hl: ["CoWoS-L", "$240"], via: [["Ticker", "NVDA", 6]] } } },
    { id: "m2", t: "note", title: "AMD: short pitch on MI400 slip", date: "2026-09-22", ntype: "Initiation", stance: "Short", conv: "Medium", cat: "MI400 sampling; Q3 guide", by: "AL", ents: { AMD: "p", NVDA: "m" },
      sum: "Short idea: MI400 volume slips to 2H27, which consensus does not price in.",
      spans: { NVDA: { loc: "p. 2 of 4 · “Why now”", text: "Buy-side expects MI400 to take share from NVIDIA in 1H27. Our channel work says 2H27 at best.", hl: ["NVIDIA", "MI400"], via: [["Name variant", "NVIDIA", 3]] } } },
    { id: "m5", t: "note", title: "ASML: initiate on the High-NA cycle", date: "2026-09-18", ntype: "Initiation", stance: "Long", conv: "Medium", cat: "Q3 orders; TSMC High-NA decision", by: "SP", ents: { ASML: "p", TSM: "m" },
      sum: "High-NA EUV orders from leading-edge fabs set up a 2027–28 upgrade cycle.",
      spans: { TSM: { loc: "p. 3 of 6 · “Customers”", text: "TSMC is the swing customer. A High-NA commitment for A14 would add about 8 tools to our 2028 estimate.", hl: ["TSMC", "High-NA"], via: [["Name variant", "TSMC", 5]] } } },
    { id: "m3", t: "note", title: "TSMC: IC note, add on CoWoS", date: "2026-09-15", ntype: "IC", stance: "Long", conv: "High", cat: "Monthly sales; 2027 capex", by: "RK", ents: { TSM: "p", NVDA: "m" },
      sum: "Recommends adding to the position as CoWoS capacity raises 2027 revenue visibility.", spans: {} },

    { id: "u1", t: "unc", title: "Mgmt_mtg_notes_0930.pdf", date: "2026-09-30", from: "SharePoint", ents: { NVDA: "p" }, sug: "Internal research note", conf: 0.48, alt: "Expert call", altc: 0.37,
      sum: "Notes from a management meeting at an investor conference, in question-and-answer format.", spans: {} },
    { id: "u2", t: "unc", title: "Untitled (3).docx", date: "2026-09-26", from: "SharePoint", ents: { AMD: "p", NVDA: "m" }, sug: "Internal research note", conf: 0.41, alt: "Broker report", altc: 0.33,
      sum: "Short draft comparing MI400 and Blackwell rack pricing. No author or date in the file.", spans: {} },
    { id: "u3", t: "unc", title: "BluMatrix_attach_88213.pdf", date: "2026-09-22", from: "BluMatrix", ents: { TSM: "p" }, sug: "Broker report", conf: 0.55, alt: "Public filing", altc: 0.31,
      sum: "Monthly revenue table for TSMC with no cover page or broker disclosures.", spans: {} }
  ];
  const byId = Object.fromEntries(D.map((d) => [d.id, d]));
  const SECTORS = [...new Set(Object.values(ENT).map((e) => e.sec))];

  const S = { type: "all", cos: [], secs: [], range: "90", from: "", to: "", f: "", view: "ui", open: null };

  /* ------------------------------------------------------------------ helpers */
  const $ = (s) => root.querySelector(s);
  const $$ = (s) => [...root.querySelectorAll(s)];
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  const fmt = (d) => MON[+d.slice(5, 7) - 1] + " " + +d.slice(8, 10);
  const iso = (dt) => dt.getFullYear() + "-" + String(dt.getMonth() + 1).padStart(2, "0") + "-" + String(dt.getDate()).padStart(2, "0");
  const days = (d) => Math.round((TODAY - new Date(d + "T12:00:00")) / 864e5);
  const chg = (n) => n > 0 ? `<span class="vv-up">+${n}</span>` : n < 0 ? `<span class="vv-dn">−${Math.abs(n)}</span>` : '<span class="vv-mu">0</span>';
  const I = {
    close: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>',
    lock: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>',
    search: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>',
    spark: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/></svg>',
    send: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 19V5"/><path d="m5 12 7-7 7 7"/></svg>',
    down: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>',
    mark: '<svg class="pui-mark" viewBox="0 0 64 64" aria-hidden="true"><path d="M20 12h28v38H20z" fill="none" stroke="currentColor" stroke-width="4" stroke-linejoin="round"/><path d="M20 12l-6 6v38l6-6M14 56h28l6-6" fill="none" stroke="currentColor" stroke-width="4" stroke-linejoin="round"/><path d="M25 17h18v28H25z" fill="#55C390"/></svg>'
  };

  const prim = (d) => Object.keys(d.ents).filter((k) => d.ents[k] === "p");
  const secsOf = (d) => [...new Set(prim(d).map((k) => ENT[k].sec))];
  const secOf = (d) => { const s = secsOf(d); return s.length === 1 ? s[0] : "Multiple"; };
  const focusFor = (d) => S.cos.find((k) => d.ents[k]) || "";
  // drawer focus: the filtered company, else the first company this document has a stored section for
  const drawerFocus = (d) => focusFor(d) || prim(d).find((k) => d.spans[k]) || Object.keys(d.spans)[0] || "";
  const relKey = (d) => { const f = focusFor(d); return f && d.rel && d.rel[f] ? f : prim(d)[0]; };
  function rating(d) { const f = focusFor(d); if (f) return d.rate[f] || null; const p = prim(d); return p.length === 1 ? d.rate[p[0]] || null : "multi"; }
  function facetVal(d) { return S.type === "all" ? TYPES[d.t].label : { broker: d.org, expert: d.rel && d.rel[relKey(d)], note: d.stance, unc: d.sug }[d.t]; }
  function orig(d) { return { broker: d.org, expert: d.vendor, note: "Author " + d.by, unc: d.from }[d.t]; }
  function dateOk(d) {
    if (S.range === "all") return true;
    if (S.range === "custom") return (!S.from || d.date >= S.from) && (!S.to || d.date <= S.to);
    return days(d.date) <= +S.range;
  }
  const inScope = (d) => (!S.cos.length || S.cos.some((k) => d.ents[k])) && (!S.secs.length || secsOf(d).some((x) => S.secs.includes(x))) && dateOk(d);
  const ofType = (d) => S.type === "all" || d.t === S.type;
  const rows = () => D.filter((d) => ofType(d) && inScope(d) && (!S.f || facetVal(d) === S.f)).sort((a, b) => b.date.localeCompare(a.date));
  function json(o) {
    return JSON.stringify(o, null, 2).replace(/("(?:\\.|[^\\"])*"(\s*:)?|\b(?:true|false|null)\b|-?\d+(?:\.\d+)?)/g, (m) => {
      const c = m[0] === '"' ? (/:$/.test(m) ? "k" : "s") : m === "null" ? "z" : /true|false/.test(m) ? "b" : "n";
      return `<span class="${c}">${esc(m)}</span>`;
    });
  }

  /* ------------------------------------------------------------------ columns */
  function coCell(d) {
    const p = prim(d), f = focusFor(d), t = esc(p.map((k) => ENT[k].name).join(", "));
    let tk;
    if (p.length === 1) tk = p[0] === f ? `<b>${p[0]}</b>` : p[0];
    else if (f && p.includes(f)) tk = `<b>${f}</b> +${p.length - 1}`;
    else tk = `Multiple (${p.length})`;
    return `<span class="vv-tk" title="${t}">${tk}</span><span class="vv-s">${esc(secOf(d))}</span>`;
  }
  const docCell = (d) => {
    const f = focusFor(d), men = f && d.ents[f] === "m" ? `<span class="vv-men">Mentions ${f}</span>` : "";
    return `<span class="vv-ttl${d.t === "unc" ? " vv-file" : ""}">${esc(d.title)}</span>${men}<span class="vv-ext">${esc(d.sum)}</span>`;
  };
  const COL_DATE = ["Date", (d) => `<span class="vv-dt">${fmt(d.date)}</span>`, "c-date"];
  const COL_DOC = ["Document", docCell, "c-doc"];
  const COL_CO = ["Company", coCell, "c-co"];
  const ALLCOLS = [COL_DATE, ["Type", (d) => `<span class="vv-pill t-${d.t}">${TYPES[d.t].pill}</span>`, "c-type"], COL_DOC, COL_CO, ["Source", (d) => esc(orig(d)), "c-src"]];
  const STANCE = { Long: "", Short: " amber", Mixed: " grey" };
  const TCOLS = {
    broker: [["Broker", (d) => esc(d.org), "c-org"], ["Report type", (d) => `<span class="pui-tag grey">${d.rtype}</span>`, "c-rt"],
      ["Rating", (d) => { const r = rating(d); return r === "multi" ? `<span class="vv-mu">${Object.keys(d.rate).length} names</span>` : r ? esc(r[0]) : '<span class="vv-mu">Not rated</span>'; }, "c-rate"],
      ["PT", (d) => { const r = rating(d); return Array.isArray(r) ? `<span class="vv-num">$${r[1].toLocaleString("en-US")}</span>` : '<span class="vv-mu">–</span>'; }, "c-num"],
      ["PT Δ", (d) => { const r = rating(d); return Array.isArray(r) ? `<span class="vv-num">${chg(r[2])}</span>` : '<span class="vv-mu">–</span>'; }, "c-num"]],
    expert: [["Expert", (d) => `<span class="vv-ttl vv-sm">${esc(d.expert)}</span><span class="vv-s">${esc(d.emp)}</span>`, "c-exp"],
      ["Relationship", (d) => { const k = relKey(d); return `<span class="pui-tag navy">${esc(d.rel[k] || "–")}</span> <span class="vv-tk vv-mu">${k}</span>`; }, "c-rel"],
      ["Network", (d) => esc(d.vendor), "c-net"], ["Length", (d) => `<span class="vv-num">${d.mins} min</span>`, "c-num"]],
    note: [["Author", (d) => `<span class="pui-av vv-av">${d.by}</span>`, "c-auth"], ["Note type", (d) => `<span class="pui-tag grey">${d.ntype}</span>`, "c-rt"],
      ["Stance", (d) => `<span class="pui-tag${STANCE[d.stance]}">${d.stance}</span>`, "c-st"], ["Conviction", (d) => d.conv, "c-conv"]],
    unc: [["Suggested type", (d) => `<span class="vv-pill t-sug">${esc(d.sug)}</span>`, "c-sug"],
      ["Confidence", (d) => `<span class="vv-conf"><i style="width:${Math.round(d.conf * 100)}%"></i></span><span class="vv-num">${d.conf.toFixed(2)}</span>`, "c-conf"],
      ["Runner-up", (d) => `${esc(d.alt)} <span class="vv-num vv-mu">${d.altc.toFixed(2)}</span>`, "c-alt"]]
  };
  function typeMeta(d) {
    if (d.t === "broker") return { broker: d.org, report_type: d.rtype, pages: d.pages, ratings: Object.fromEntries(Object.entries(d.rate).map(([k, r]) => [k, { rating: r[0], pt: r[1], pt_change: r[2] }])) };
    if (d.t === "expert") return { expert_title: d.expert, employer: d.emp, relationship: d.rel, network: d.vendor, interviewer: d.by, length_min: d.mins };
    if (d.t === "note") return { author: d.by, note_type: d.ntype, stance: d.stance, conviction: d.conv, catalysts: d.cat };
    return { suggested_type: d.sug, confidence: d.conf, runner_up: d.alt, runner_up_confidence: d.altc, source: d.from };
  }
  const commonMeta = (d) => ({ doc_id: d.id, doc_type: d.t === "unc" ? null : d.t, date: d.date, name: d.title, summary: d.sum, primary_company: prim(d), primary_sector: secOf(d) });

  /* ------------------------------------------------------------------ shell (rendered once) */
  const comboHTML = (kind, label, ph) => `<div class="vv-ms" data-ms="${kind}">
      <span class="vv-mlab" id="vv-${kind}-l">${label}</span><span class="vv-chips" data-chips="${kind}"></span>
      <input type="text" role="combobox" aria-autocomplete="list" aria-expanded="false" aria-controls="vv-${kind}-pop" aria-labelledby="vv-${kind}-l" placeholder="${ph}" autocomplete="off" spellcheck="false">
      <ul class="vv-pop" id="vv-${kind}-pop" role="listbox" aria-labelledby="vv-${kind}-l" hidden></ul>
    </div>`;
  root.innerHTML = `<div class="pui-win vv-win">
    <div class="pui-bar vv-bar">${I.mark}<span class="pui-crumb"><span class="vv-cr">Data Agent / </span><b>Vault viewer</b></span><span class="pui-tag amber vv-sample">Illustrative sample data</span>
      <span class="pui-bar-r"><span class="vv-seg vv-view" role="group" aria-label="View as"><button type="button" data-view="ui" aria-pressed="true">Analyst UI</button><button type="button" data-view="mcp" aria-pressed="false">Agent (MCP)</button></span></span></div>
    <div class="vv-app">
      <div class="vv-rail"><p class="pui-k">Document types</p><div class="vv-types" data-types></div>
        <p class="vv-railnote">${I.lock}Counts respect your permissions</p></div>
      <div class="vv-main">
        <div class="vv-head" data-head></div>
        <div class="vv-filters">
          <div class="vv-fgrid">${comboHTML("co", "Company", "Name or ticker")}${comboHTML("sec", "Primary sector", "Any sector")}</div>
          <div class="vv-frow" data-frow></div>
        </div>
        <div class="vv-tw" data-table tabindex="-1"></div>
        <div class="vv-foot" data-foot></div>
        <form class="vv-ask" data-ask>
          <div class="vv-askrow"><span class="vv-askic">${I.spark}</span><input type="text" aria-label="Ask Pascal about these documents" placeholder="Ask about these documents"><button type="submit" class="pui-btn pri">Ask Pascal</button></div>
          <div class="vv-hint" data-hint></div>
        </form>
      </div>
    </div>
    <div class="vv-drawer-host" data-drawer></div>
    <div class="vv-toast" role="status" aria-live="polite" hidden></div>
  </div>`;
  root.classList.add("vv-live");

  /* ------------------------------------------------------------------ render */
  function renderRail() {
    $("[data-types]").innerHTML = Object.entries(TYPES).map(([k, t]) => {
      const n = D.filter((d) => (k === "all" || d.t === k) && inScope(d)).length;
      return `<button type="button" class="vv-type${k === "unc" ? " unc" : ""}" data-type="${k}" aria-pressed="${S.type === k}">
        <span class="vv-tn">${t.label}</span><span class="vv-tc">${n}</span>
        <span class="vv-tm">${esc(t.src)} · ${t.vault}</span></button>`;
    }).join("");
  }
  function renderChips() {
    $('[data-chips="co"]').innerHTML = S.cos.map((k) => `<span class="vv-chip" title="${esc(ENT[k].name)}">${k}<button type="button" data-rmco="${k}" aria-label="Remove ${k}">${I.close}</button></span>`).join("");
    $('[data-chips="sec"]').innerHTML = S.secs.map((x) => `<span class="vv-chip">${esc(x)}<button type="button" data-rmsec="${esc(x)}" aria-label="Remove ${esc(x)}">${I.close}</button></span>`).join("");
    $('[data-ms="co"] input').placeholder = S.cos.length ? "Add another" : "Name or ticker";
    $('[data-ms="sec"] input').placeholder = S.secs.length ? "Add another" : "Any sector";
  }
  function renderHead() {
    const T = TYPES[S.type], scope = [S.cos.join(", "), S.secs.join(", ")].filter(Boolean).join(" · ");
    const sub = S.type === "all" ? "Newest first · every document type" : S.type === "unc" ? "Files the classifier could not type with confidence. Newest first." : `Newest first · ${esc(T.src)} · synced ${T.sync}`;
    $("[data-head]").innerHTML = `<p class="vv-h">${T.label}${scope ? ` <span>· ${esc(scope)}</span>` : ""}</p><p class="vv-sub">${sub}</p>`;
  }
  function renderFilters() {
    const T = TYPES[S.type];
    const opts = [...new Set(D.filter((d) => ofType(d) && inScope(d)).map(facetVal).filter(Boolean))].sort();
    const seg = [["7", "7d"], ["30", "30d"], ["90", "90d"], ["all", "All"], ["custom", "Custom"]].map(([v, l]) => `<button type="button" data-r="${v}" aria-pressed="${S.range === v}">${l}</button>`).join("");
    const custom = S.range === "custom" ? `<span class="vv-dates"><input type="date" data-d="from" aria-label="From date" value="${S.from}"${S.to ? ` max="${S.to}"` : ""}><span>to</span><input type="date" data-d="to" aria-label="To date" value="${S.to}"${S.from ? ` min="${S.from}"` : ""}></span>` : "";
    $("[data-frow]").innerHTML = `<span class="vv-lab">${T.dateL}</span><span class="vv-seg" role="group" aria-label="Date range">${seg}</span>${custom}
      <label class="vv-sel"><span>${T.fl}</span><select data-facet aria-label="${T.fl}"><option value="">All</option>${opts.map((o) => `<option${o === S.f ? " selected" : ""}>${esc(o)}</option>`).join("")}</select>${I.down}</label>`;
  }
  function renderTable() {
    const r = rows(), T = TYPES[S.type], total = D.filter(ofType).length, tw = $("[data-table]");
    tw.classList.toggle("is-json", S.view === "mcp");
    if (S.view === "mcp") {
      const fk = { all: "type_filter", broker: "broker", expert: "relationship", note: "stance", unc: "suggested_type" }[S.type];
      const args = { doc_type: S.type === "all" ? null : S.type === "unc" ? "unclassified" : S.type, companies: S.cos, sectors: S.secs,
        ...(S.range === "custom" ? { date_from: S.from || null, date_to: S.to || null } : { since_days: S.range === "all" ? null : +S.range }), [fk]: S.f || null, order: "date_desc", limit: 3 };
      const docs = r.slice(0, 3).map((d) => S.type === "all" ? { ...commonMeta(d), source: orig(d) } : { ...commonMeta(d), metadata: typeMeta(d) });
      tw.innerHTML = `<div class="vv-jhead"><span class="vv-jdot"></span>MCP · <b>list_documents</b><span class="vv-jr">200 · 38 ms</span></div><pre class="vv-json">${json({ request: { tool: "list_documents", args }, response: { total: r.length, hidden_by_acl: T.hidden, documents: docs, next_cursor: r.length > 3 ? "c_3" : null } })}</pre>`;
    } else if (!r.length) {
      tw.innerHTML = `<div class="vv-empty"><b>No ${T.many} match these filters.</b><span>Widen the date range or remove a filter.</span></div>`;
    } else {
      const cols = S.type === "all" ? ALLCOLS : [COL_DATE, COL_DOC, COL_CO].concat(TCOLS[S.type]);
      const ts = S.type === "all" ? -1 : 3;
      tw.innerHTML = `<table class="vv-tbl t-${S.type}"><thead><tr>${cols.map((c, i) => `<th scope="col" class="${c[2]}${i === ts ? " ts" : ""}">${c[0]}</th>`).join("")}</tr></thead><tbody>${r.map((d) => `<tr tabindex="0" data-id="${d.id}" aria-label="Open ${esc(d.title)}"${S.open === d.id ? ' class="on"' : ""}>${cols.map((c, i) => `<td class="${c[2]}${i === ts ? " ts" : ""}">${c[1](d)}</td>`).join("")}</tr>`).join("")}</tbody></table>`;
    }
    $("[data-foot]").innerHTML = `<span><b>${r.length}</b> of ${total} sample ${T.many} · ${T.vault} in the vault</span>${T.hidden ? `<span class="vv-lock">${I.lock}${T.hidden} more hidden by your permissions (${T.why})</span>` : ""}`;
    const co = S.cos[0] || "NVDA";
    const sugg = {
      all: S.cos.length ? [`What changed on ${S.cos.join(", ")} this month?`, `Where do brokers and experts disagree on ${co}?`] : ["Summarise everything new this week", "Which names had the most new documents?"],
      broker: ["Which names had PT raises this month?", `Where do brokers disagree on ${co} gross margin?`],
      expert: ["Which experts discussed CoWoS allocation?", "What do ex-employees say about 2027 demand?"],
      note: [`How has our ${co} thesis changed since June?`, "Which notes flag supply as the key risk?"],
      unc: ["Which of these look like expert calls?"]
    }[S.type];
    $("[data-ask] input").placeholder = `Ask about these ${r.length} ${r.length === 1 ? T.one : T.many}`;
    $("[data-hint]").innerHTML = `<span>Scoped to this list</span>${sugg.map((s) => `<button type="button" class="vv-sugg">${esc(s)}</button>`).join("")}`;
  }
  function render() { renderRail(); renderChips(); renderHead(); renderFilters(); renderTable(); }

  /* ------------------------------------------------------------------ company / sector pickers */
  function combo(kind) {
    const box = $(`[data-ms="${kind}"]`), input = box.querySelector("input"), pop = box.querySelector(".vv-pop");
    let act = 0, items = [];
    const list = (q) => kind === "co"
      ? Object.keys(ENT).filter((k) => !S.cos.includes(k) && (!q || k.toLowerCase().startsWith(q) || ENT[k].name.toLowerCase().includes(q) || ENT[k].alias.includes(q)))
      : SECTORS.filter((x) => !S.secs.includes(x) && (!q || x.toLowerCase().includes(q)));
    function draw() {
      const q = input.value.trim().toLowerCase();
      items = list(q);
      act = Math.max(0, Math.min(act, items.length - 1));
      pop.innerHTML = items.length
        ? items.map((k, i) => `<li role="option" id="vv-${kind}-o${i}" data-v="${esc(k)}" aria-selected="${i === act}">${kind === "co" ? `<b>${k}</b><span>${esc(ENT[k].name)}</span><small>${esc(ENT[k].sec)}</small>` : `<span>${esc(k)}</span>`}</li>`).join("")
        : `<li class="vv-none">No match for “${esc(input.value.trim())}”</li>`;
      pop.hidden = false;
      input.setAttribute("aria-expanded", "true");
      if (items.length) input.setAttribute("aria-activedescendant", `vv-${kind}-o${act}`); else input.removeAttribute("aria-activedescendant");
    }
    function close() { pop.hidden = true; input.setAttribute("aria-expanded", "false"); input.removeAttribute("aria-activedescendant"); }
    function pick(v) {
      const arr = kind === "co" ? S.cos : S.secs;
      if (!arr.includes(v)) arr.push(v);
      S.f = ""; input.value = ""; act = 0;
      render(); reopen(); close();
    }
    input.addEventListener("focus", draw);
    input.addEventListener("input", () => { act = 0; draw(); });
    input.addEventListener("blur", () => setTimeout(close, 120));
    input.addEventListener("keydown", (e) => {
      const q = input.value.trim();
      if (e.key === "ArrowDown" || e.key === "ArrowUp") { e.preventDefault(); if (pop.hidden) draw(); act = (act + (e.key === "ArrowDown" ? 1 : -1) + items.length) % Math.max(items.length, 1); draw(); }
      else if (e.key === "Enter") { e.preventDefault(); if (items[act] && (q || !pop.hidden)) pick(items[act]); else if (q) toast(`No ${kind === "co" ? "company" : "sector"} matches “${q}”`); }
      else if (e.key === "Escape") { if (!pop.hidden) { e.stopPropagation(); close(); } }
      else if (e.key === "Backspace" && !q) { const arr = kind === "co" ? S.cos : S.secs; if (arr.length) { arr.pop(); S.f = ""; render(); reopen(); draw(); } }
    });
    pop.addEventListener("mousedown", (e) => { const li = e.target.closest("[data-v]"); if (li) { e.preventDefault(); pick(li.dataset.v); } });
    box.addEventListener("mousedown", (e) => { if (e.target === box || e.target.classList.contains("vv-mlab") || e.target.classList.contains("vv-chips")) { e.preventDefault(); input.focus(); } });
  }
  combo("co"); combo("sec");

  /* ------------------------------------------------------------------ document drawer */
  function hl(text, terms) {
    let t = esc(text);
    (terms || []).forEach((w) => { const re = new RegExp(esc(w).replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "g"); t = t.replace(re, (m) => `<mark>${m}</mark>`); });
    return t;
  }
  function typeFacets(d) {
    if (d.t === "broker") return [["Broker", esc(d.org)], ["Report type", esc(d.rtype)], ["Pages", d.pages]]
      .concat(Object.entries(d.rate).map(([k, r]) => [`${k} rating`, `${esc(r[0])} · $${r[1].toLocaleString("en-US")} <span class="vv-num">(${chg(r[2])})</span>`]));
    if (d.t === "expert") return [["Expert", esc(d.expert)], ["Employer", esc(d.emp)]]
      .concat(Object.entries(d.rel).map(([k, v]) => [`Relationship · ${k}`, esc(v)]), [["Network", esc(d.vendor)], ["Interviewer", d.by], ["Length", d.mins + " min"]]);
    if (d.t === "note") return [["Author", d.by], ["Note type", d.ntype], ["Stance", d.stance], ["Conviction", d.conv], ["Catalysts", esc(d.cat)]];
    return [["Suggested type", esc(d.sug)], ["Confidence", d.conf.toFixed(2)], ["Runner-up", `${esc(d.alt)} · ${d.altc.toFixed(2)}`], ["Source", esc(d.from)]];
  }
  const grid = (a) => `<div class="vv-facets">${a.map(([k, v]) => `<div><span>${esc(k)}</span>${v}</div>`).join("")}</div>`;
  let lastRow = null;
  function openDoc(id) {
    const d = byId[id], T = TYPES[d.t], p = prim(d), also = Object.keys(d.ents).filter((k) => d.ents[k] === "m");
    const fc = drawerFocus(d), sp = fc && d.spans[fc];
    S.open = id;
    $$("tr[data-id]").forEach((tr) => tr.classList.toggle("on", tr.dataset.id === id));
    const common = [[T.dateL, fmt(d.date) + ", 2026"], ["Primary company", esc(p.map((k) => `${ENT[k].name} (${k})`).join(", "))], ["Primary sector", esc(secOf(d))], ["Also mentions", also.join(", ") || "–"]];
    let body;
    if (S.view === "mcp") {
      body = `<div class="vv-jbox"><div class="vv-jhead"><span class="vv-jdot"></span>MCP · <b>get_document</b><span class="vv-jr">200 · 24 ms</span></div><pre class="vv-json">${json({ tool: "get_document", args: { doc_id: d.id, company: fc || null }, response: { ...commonMeta(d), metadata: typeMeta(d), span: sp ? { company: fc, locator: sp.loc, text: sp.text, tagged_by: sp.via.map((v) => ({ signal: v[0].toLowerCase().replace(/ /g, "_"), value: v[1], count: v[2] })) } : null } })}</pre></div>`;
    } else {
      const total = sp ? sp.via.reduce((a, v) => a + v[2], 0) : 0;
      body = `${grid(common)}
        <div class="vv-block"><p class="pui-k">${esc(T.pill)} fields</p>${grid(typeFacets(d))}</div>
        <div class="vv-span"><div class="vv-loc"><b>Summary</b></div><p>${esc(d.sum)}</p></div>
        ${sp ? `<div class="vv-span on"><div class="vv-loc"><span><b>${fc} section</b> · ${esc(sp.loc)}</span>${d.ents[fc] === "m" ? '<span class="vv-men">Mention only</span>' : ""}</div><p>${hl(sp.text, sp.hl)}</p><p class="vv-skip">Opens at this section. The full document is one click away.</p></div>
          <details class="vv-why" open><summary>Why this is tagged to ${esc(ENT[fc].name)}: <b>${total} mentions</b></summary><ul>${sp.via.map((v) => `<li><span>${esc(v[0])}</span><code>${esc(v[1])}</code><b>${v[2]}×</b></li>`).join("")}</ul></details>`
        : `<p class="vv-note">No company section stored for this file yet.</p>`}
        <div class="vv-also"><span class="pui-k">Filter by company</span>${Object.keys(d.ents).map((k) => `<button type="button" class="vv-cchip" data-co="${k}" aria-pressed="${S.cos.includes(k)}">${k}${d.ents[k] === "m" ? " · mention" : ""}</button>`).join("")}</div>
        ${d.t === "unc" ? `<div class="vv-also vv-assign"><span class="pui-k">Assign type</span>${["Broker report", "Expert call", "Internal research note"].map((x) => `<button type="button" class="vv-cchip" data-assign="${esc(x)}">${esc(x)}</button>`).join("")}</div>` : ""}`;
    }
    $("[data-drawer]").innerHTML = `<div class="vv-scrim" data-close></div><div class="vv-drawer" role="dialog" aria-labelledby="vv-dt">
      <div class="vv-dh"><div><span class="vv-pill t-${d.t}">${T.pill}</span><p class="vv-dtl${d.t === "unc" ? " vv-file" : ""}" id="vv-dt">${esc(d.title)}</p><p class="vv-sub">${esc(orig(d))} · ${fmt(d.date)}, 2026${d.pages ? ` · ${d.pages} pages` : d.mins ? ` · ${d.mins} min` : ""}</p></div><div class="vv-dact"><span class="vv-seg vv-dseg" role="group" aria-label="View as"><button type="button" data-view="ui" aria-pressed="${S.view === "ui"}">Analyst UI</button><button type="button" data-view="mcp" aria-pressed="${S.view === "mcp"}">MCP</button></span><button type="button" class="vv-x" data-close aria-label="Close document">${I.close}</button></div></div>
      <div class="vv-dbody">${body}</div></div>`;
    document.documentElement.classList.add("vv-lock");
    const x = $(".vv-x");
    if (x) x.focus({ preventScroll: true });
  }
  function closeDoc() {
    S.open = null;
    $("[data-drawer]").innerHTML = "";
    document.documentElement.classList.remove("vv-lock");
    $$("tr.on").forEach((tr) => tr.classList.remove("on"));
    if (lastRow) { const tr = $(`tr[data-id="${lastRow}"]`); if (tr) tr.focus({ preventScroll: true }); }
  }
  function reopen() { if (S.open) openDoc(S.open); }
  // desktop: the drawer sits inside the viewer, so bring the viewer's top edge below the sticky nav and subnav
  function reveal() {
    if (window.matchMedia("(max-width: 760px)").matches) return;
    const bars = [...document.querySelectorAll(".nav, .subnav")].reduce((m, el) => { const r = el.getBoundingClientRect(); return getComputedStyle(el).position === "sticky" || getComputedStyle(el).position === "fixed" ? Math.max(m, r.bottom) : m; }, 0);
    const top = root.getBoundingClientRect().top, gap = bars + 16;
    if (top < gap) window.scrollBy({ top: top - gap, behavior: "smooth" });
  }

  /* ------------------------------------------------------------------ events */
  let tt;
  function toast(m) {
    const t = $(".vv-toast");
    t.textContent = m; t.hidden = false;
    clearTimeout(tt); tt = setTimeout(() => { t.hidden = true; }, 3000);
  }
  root.addEventListener("click", (e) => {
    const g = (s) => e.target.closest(s);
    let el;
    if ((el = g("[data-view]"))) {
      S.view = el.dataset.view;
      $$("[data-view]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.view === S.view)));
      root.classList.toggle("is-mcp", S.view === "mcp");
      render(); reopen(); return;
    }
    if ((el = g("[data-type]"))) { S.type = el.dataset.type; S.f = ""; render(); if (S.open && !ofType(byId[S.open])) closeDoc(); return; }
    if ((el = g("[data-r]"))) {
      S.range = el.dataset.r;
      if (S.range === "custom" && !S.from && !S.to) { const f = new Date(TODAY); f.setDate(f.getDate() - 30); S.from = iso(f); S.to = iso(TODAY); }
      render(); return;
    }
    if ((el = g("[data-rmco]"))) { S.cos = S.cos.filter((x) => x !== el.dataset.rmco); S.f = ""; render(); reopen(); return; }
    if ((el = g("[data-rmsec]"))) { S.secs = S.secs.filter((x) => x !== el.dataset.rmsec); S.f = ""; render(); return; }
    if ((el = g("[data-co]"))) { const k = el.dataset.co; S.cos = S.cos.includes(k) ? S.cos.filter((x) => x !== k) : S.cos.concat(k); S.f = ""; render(); reopen(); return; }
    if ((el = g("[data-assign]"))) {
      $$("[data-assign]").forEach((b) => b.setAttribute("aria-pressed", String(b === el)));
      toast(`Type set to ${el.dataset.assign}. The classifier learns from this choice.`); return;
    }
    if (g("[data-close]")) { closeDoc(); return; }
    if ((el = g(".vv-sugg"))) { const i = $("[data-ask] input"); i.value = el.textContent; i.focus(); return; }
    if ((el = g("tr[data-id]"))) { lastRow = el.dataset.id; openDoc(el.dataset.id); reveal(); }
  });
  root.addEventListener("keydown", (e) => {
    const tr = e.target.closest && e.target.closest("tr[data-id]");
    if (tr && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); lastRow = tr.dataset.id; openDoc(tr.dataset.id); reveal(); }
    if (tr && (e.key === "ArrowDown" || e.key === "ArrowUp")) { e.preventDefault(); const n = e.key === "ArrowDown" ? tr.nextElementSibling : tr.previousElementSibling; if (n) n.focus(); }
  });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && S.open) closeDoc(); });
  root.addEventListener("change", (e) => {
    if (e.target.matches("[data-facet]")) { S.f = e.target.value; render(); }
    else if (e.target.matches("[data-d]")) { S[e.target.dataset.d] = e.target.value; render(); }
  });
  $("[data-ask]").addEventListener("submit", (e) => {
    e.preventDefault();
    const i = $("[data-ask] input"), q = i.value.trim();
    if (!q) { i.focus(); return; }
    const n = rows().length, T = TYPES[S.type];
    toast(`Sent to Ask Pascal, scoped to ${n} ${n === 1 ? T.one : T.many}${S.cos.length ? " on " + S.cos.join(", ") : ""}`);
    i.value = "";
  });

  render();
})();
