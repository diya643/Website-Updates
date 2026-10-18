#!/usr/bin/env python3
"""Event pages: writes _build/pages/events*.html from the EVENTS data below.

    python3 _build/gen/events.py && python3 _build/build.py --only events,events-hong-kong-2026,events-new-york-2026

Layout follows LinqAlpha's summit pages: city photo hero with a date / time / location strip, About,
Agenda (with speakers), Hosted by, a request-an-invitation form and the rest of the series. Copy is the user's event brief.
Set "start"/"end" (ISO with offset) once a date is confirmed; that also switches on Event schema.
Hero photos and headshots live in _build/static/assets/photos/.
"""
import json
from pathlib import Path

PAGES = Path(__file__).resolve().parents[1] / "pages"

SERIES = "From Front to Back Office"
TOPIC = "Where AI Is Actually Working in Asset Management"
INVITE = ("An invite-only roundtable breakfast for about 20–25 senior guests from hedge funds and asset managers: "
          "CTOs, COOs, CIOs, and heads of data, research and operations.")
ROUNDTABLE_SUMMARY = ("Invite-only roundtables where senior leaders from hedge funds and asset managers compare notes on "
                      "where AI is working across the front, middle and back office.")
NOTE = ("Please note: seats are limited to about 20–25 senior guests from hedge funds and asset managers. "
        "Admission is by invitation.")

EVENTS = [
    {
        "slug": "hong-kong-2026", "city": "Hong Kong", "country": "HK", "cc": "+852", "live": True,
        "format": "Invite-only roundtable dinner", "format_kv": "Roundtable dinner, about 20–25 guests",
        "date": "27 October 2026 (Tue)", "date_short": "27 Oct 2026", "date_sub": "",
        "time": "7:00–9:30 PM", "time_sub": "Hong Kong time",
        "venue": "JW Marriott Hotel Hong Kong", "venue_sub": "Admiralty",
        "start": "2026-10-27T19:00:00+08:00", "end": "2026-10-27T21:30:00+08:00",
        "photo": ("/assets/photos/event-hong-kong.jpg", "/assets/photos/event-hong-kong-sm.jpg"),  # CC0, see photos/CREDITS.txt
        "title": "From Front to Back Office: AI Roundtable, Hong Kong",
        "description": "Invite-only roundtable dinner in Hong Kong on 27 October 2026 for hedge fund and asset manager leaders on where AI is working, front to back office.",
        "about": [
            "Pascal AI Labs and Bare Cove Technology are bringing together 20–25 senior leaders from hedge funds and asset managers for an "
            "invite-only dinner and discussion on AI in institutional finance.",
            "Over the past year, AI has moved from experimentation towards day-to-day use across investment firms. As firms "
            "look to bring AI into core fund workflows, the questions around implementation, data infrastructure, governance "
            "and controls are becoming harder to solve in isolation.",
            "This session is an opportunity for leaders working through these challenges to compare notes and learn from how "
            "their peers are approaching them.",
            "The evening will begin with dinner and a brief welcome before moving into a moderated discussion on the "
            "realities of deploying AI across investment workflows. <b>Rowel Balot</b> (CTO, Bare Cove Technology) and "
            "<b>Vibhav Viswanathan</b> (CEO &amp; Co-Founder, Pascal AI Labs) will lead the conversation across three "
            "segments of 15–20 minutes each. Together, they will explore the infrastructure and controls needed to make AI "
            "work reliably at scale.",
            "We’ll then open the floor for guests to share their experiences, raise questions and exchange perspectives, "
            "followed by optional networking.",
        ],
        # (name, title, firm, headshot path or None). Headshots show only once every speaker has one.
        "speakers": [("Rowel Balot", "CTO", "Bare Cove Technology", "/assets/photos/speaker-rowel-balot.jpg", "https://www.linkedin.com/in/rowelbalot/"),
                     ("Vibhav Viswanathan", "CEO &amp; Co-Founder", "Pascal AI Labs", "/assets/photos/speaker-vibhav-viswanathan.jpg", "https://www.linkedin.com/in/vibhav-viswanathan-13550015")],
        "moderator": None,
        # (left label, title, description, is the moderated discussion)
        "agenda": [
            ("7:00 PM", "Drinks and arrivals", "", False),
            ("7:30 PM", "Welcome and opening", "", False),
            ("Moderated discussion", "Deploying AI across investment workflows",
             "Three segments of 15–20 minutes each on the infrastructure and controls needed to make AI work reliably at scale.", True),
            ("8:30 PM", "Open forum and networking over dinner",
             "Guests share their experiences, raise questions and exchange perspectives.", False),
        ],
        "segments": [
            ("Past the pilot: Where AI is delivering value", "Which workflows made it to production in Hong Kong, and what model access and scale really cost."),
            ("Build, Buy or Outsource: Who Keeps Your Edge?", "What to build, buy or hand to service providers, and how to stop vendors learning from your research."),
            ("Trust and Control: Ready When the Regulator Asks", "What the SFC and HKMA expect, and how to run AI across Hong Kong and mainland teams without breaching data rules."),
        ],
    },
    {
        # Not live yet (user, 14 Oct 2026): set "live" to True to publish.
        "slug": "new-york-2026", "city": "New York", "country": "US", "cc": "+1", "live": False,
        "format": "Invite-only roundtable breakfast", "format_kv": "Roundtable breakfast, about 20–25 guests",
        "date": "First week of November 2026", "date_short": "Early Nov 2026", "date_sub": "Exact date to be confirmed",
        "time": "8:00–10:30 AM", "time_sub": "Eastern time",
        "venue": "New York", "venue_sub": "Venue to be confirmed",
        "start": None, "end": None,
        "photo": ("/assets/photos/hero-manhattan.jpg", "/assets/photos/hero-manhattan-sm.jpg"),
        "title": "From Front to Back Office: AI Roundtable, New York",
        "description": "Invite-only roundtable breakfast in New York, first week of November 2026, for hedge fund and asset manager leaders on where AI is working in funds.",
        "about": [
            "Pascal AI Labs is hosting an invite-only breakfast in New York for 20–25 senior leaders from hedge funds and "
            "asset managers, including CTOs, COOs, CIOs and heads of data, research and operations.",
            "In the past 12 months, AI has moved beyond analyst tools and into the core workflows of the fund, across research, "
            "risk, compliance and operations. That shift places new demands on data and controls, for managers and for the "
            "administrators and service providers that support them.",
            "This roundtable brings both sides of that relationship into one room, so leaders can compare notes on what is "
            "working, what is still unresolved, and how their peers are approaching it.",
            "After breakfast and a short welcome, the morning opens with a brief perspective on the past year before moving into "
            "a moderated discussion with <b>Sean Lee</b> (D1 Capital Partners) and <b>Jay Rooney</b> (MUFG Investor Services), "
            "led by Pascal AI Labs. The conversation runs across three segments of 15–20 minutes each, from where AI is "
            "delivering value to the security and governance required before it is applied to client-facing or NAV-related work.",
            "Guests will then share their own experience and questions with the speakers, followed by optional networking of "
            "about 20–30 minutes.",
        ],
        "speakers": [("Sean Lee", "", "D1 Capital Partners", None),
                     ("Jay Rooney", "", "MUFG Investor Services", None)],
        "moderator": "Moderated by Pascal AI Labs",
        "agenda": [
            ("8:00 AM", "Breakfast and welcome", "", False),
            ("Opening remarks", "AI across the fund: the past twelve months",
             "How AI has moved from analyst tools into research, risk, compliance and operations, and what that requires of "
             "data and controls.", False),
            ("Moderated discussion", "Deploying AI across the manager and the servicer",
             "Three segments of 15–20 minutes each on how managers and their service providers are putting AI to work.", True),
            ("Open forum", "Guest perspectives and questions",
             "Guests share their experiences and questions, with responses from the speakers.", False),
            ("Until 10:30 AM", "Networking (optional)", "", False),
        ],
        "segments": [
            ("Where AI is delivering value", "Which workflows have moved from pilot into production, at the manager and at the servicer, and which have not."),
            ("Build, buy or rely on your servicer", "How firms decide what to develop in-house, what to buy and what to expect from administrators and service providers, and how the manager–administrator relationship changes when both sides run AI."),
            ("Trust and control", "What investors, boards and regulators will ask about data security, auditability and governance, and what must be in place before AI is applied to client-facing or NAV-related work."),
        ],
    },
]

LIVE = [e for e in EVENTS if e["live"]]

COUNTRIES = [("+852", "Hong Kong"), ("+1", "United States"), ("+44", "United Kingdom"), ("+65", "Singapore"),
             ("+91", "India"), ("+971", "United Arab Emirates"), ("+61", "Australia"), ("+81", "Japan"),
             ("+86", "China"), ("+49", "Germany"), ("+33", "France"), ("+41", "Switzerland")]


def meta_block(m):
    return "<!--meta\n" + json.dumps(m, indent=1, ensure_ascii=False) + "\n-->\n"


def hero_img(ev):
    big, small = ev["photo"]
    return (f'<img class="ev-hero-img" src="{big}" srcset="{small} 1000w, {big} 2000w" sizes="100vw" alt="" '
            f'width="2000" height="1333" fetchpriority="high">')


def people(ev, show_photos=True):
    photos = show_photos and all(sp[3] for sp in ev["speakers"])  # 2:3 portraits, 600x900
    out = []
    for name, title, firm, photo, *rest in ev["speakers"]:
        li = f'<a class="ev-li" href="{rest[0]}" rel="noopener" target="_blank">LinkedIn profile</a>' if rest and show_photos else ""
        img = f'<img src="{photo}" alt="{name}" width="600" height="900" loading="lazy" decoding="async">' if photos else ""
        t = f"<span>{title}</span>" if title else ""
        out.append(f'<div class="ev-person">{img}<b>{name}</b>{t}<em>{firm}</em>{li}</div>')
    return "".join(out)


def facts(ev):
    sub = f"<small>{ev['date_sub']}</small>" if ev["date_sub"] else ""
    return f"""<dl class="ev-facts-in">
      <div class="ev-fact"><dt>Date</dt><dd>{ev['date']}{sub}</dd></div>
      <div class="ev-fact"><dt>Time</dt><dd>{ev['time']}<small>{ev['time_sub']}</small></dd></div>
      <div class="ev-fact"><dt>Location</dt><dd>{ev['venue']}<small>{ev['venue_sub']}</small></dd></div>
    </dl>"""


def row(ev):
    return f"""<li class="ev-row"><span class="ev-row-city">{ev['city']}</span><span class="ev-row-t">{SERIES}: {TOPIC}</span><span class="ev-row-d">{ev['date_short']}<br>{ev['time']}, {ev['time_sub']}</span><a href="/events/{ev['slug']}">View event</a></li>"""


HOST = f"""<div class="ev-host">
      <div class="ev-host-logo"><img src="/assets/pascal-logo.png" alt="Pascal AI Labs" width="360" height="106" loading="lazy"></div>
      <div class="ev-host-copy">
        <h3>Pascal AI Labs</h3>
        <p>Pascal builds context-driven AI agents for institutional finance, working across the front, middle and back office for <a href="/solutions/hedge-funds">hedge funds</a>, <a href="/solutions/asset-wealth-management">asset managers</a> and <a href="/solutions/asset-servicing">fund servicers</a>.</p>
      </div>
    </div>"""


HOSTS = """<div class="ev-hosts">
      <div class="ev-hostc"><div class="ev-host-logo"><img src="/assets/pascal-logo.png" alt="Pascal AI Labs" width="360" height="106" loading="lazy"></div>
        <div class="ev-host-copy"><h3>Pascal AI Labs</h3><p>Context-driven AI agents for institutional finance, across the front, middle and back office for <a href="/solutions/hedge-funds">hedge funds</a>, <a href="/solutions/asset-wealth-management">asset managers</a> and <a href="/solutions/asset-servicing">fund servicers</a>.</p></div></div>
      <div class="ev-hostc"><div class="ev-host-logo"><img src="/assets/logos/bare-cove-technology.svg" alt="Bare Cove Technology" width="1953" height="415" loading="lazy"></div>
        <div class="ev-host-copy"><h3>Bare Cove Technology</h3><p>An Asia-based technology company providing IT and cybersecurity solutions to the financial industry. <a href="https://barecovetech.com/" rel="noopener" target="_blank">barecovetech.com</a></p></div></div>
    </div>"""


def agenda(ev):
    segs = "".join(f"<li><div><b>{h}</b><span>{d}</span></div></li>" for h, d in ev["segments"])
    mod = f'<p class="ev-ag-d">{ev["moderator"]}.</p>' if ev["moderator"] else ""
    rows = []
    for label, title, desc, disc in ev["agenda"]:
        d = f'<p class="ev-ag-d">{desc}</p>' if desc else ""
        extra = f'<div class="ev-people">{people(ev, False)}</div>{mod}<ol class="ev-segs">{segs}</ol>' if disc else ""
        rows.append(f'<li><p class="ev-ag-t">{label}</p><div><h3 class="ev-ag-h">{title}</h3>{d}{extra}</div></li>')
    return "\n      ".join(rows)


def more(others):
    if not others:
        return ""
    return f"""<section class="ev-sec ev-mint" aria-labelledby="more-title">
  <div class="ev-in">
    <h2 class="ev-h2" id="more-title">More events</h2>
    <ul class="ev-rows">{"".join(row(o) for o in others)}</ul>
    <p class="ev-all"><a href="/events">See all events</a></p>
  </div>
</section>
"""


def page(ev):
    others = [o for o in LIVE if o is not ev]
    opts = "".join(f'<option value="{c}" data-country="{n}"{" selected" if c == ev["cc"] else ""}>{n} ({c})</option>'
                   for c, n in COUNTRIES)
    about = "".join(f"<p>{p}</p>" for p in ev["about"])
    meta = {
        "path": f"/events/{ev['slug']}",
        "title": ev["title"],
        "description": ev["description"],
        "crumbs": [["Events", "/events"], [ev["city"], f"/events/{ev['slug']}"]],
        "og_kicker": f"Pascal AI · {ev['city']}",
        "og_title": f"{SERIES}: {TOPIC}",
        "llms": f"{SERIES}: {TOPIC}. Invite-only roundtable breakfast in {ev['city']}, {ev['date']}, {ev['time']}, hosted by Pascal AI Labs, with a form to request an invitation.",
        "css": ["events.css"],
        "word_limit": 900, "faq_min": 0, "lead_min": 5, "priority": 0.6,
        "event": {"name": f"{SERIES}: {TOPIC} ({ev['city']})", "start": ev["start"], "end": ev["end"],
                  "place": ev["venue"], "city": ev["city"], "country": ev["country"],
                  "speakers": [(n, f"{t}, {f}" if t else f) for n, t, f, *_ in ev["speakers"]]},
    }
    return meta_block(meta) + f"""<section class="ev-hero dark" aria-labelledby="page-title">
  {hero_img(ev)}
  <div class="ev-hero-in">
    <p class="ev-kicker"><b>{ev['city']}</b>{ev['format']}</p>
    <p class="lead ev-series">{SERIES}</p>
    <h1 class="ev-h1" id="page-title">{TOPIC}<span class="sr-only"> ({ev['city']})</span></h1>
    <div class="actions"><a class="btn btn-white" href="#request">Request an invitation</a></div>
  </div>
  <div class="ev-facts">
    {facts(ev)}
  </div>
  <p class="ev-note">{NOTE}</p>
</section>

<section class="ev-sec" aria-labelledby="about-title">
  <div class="ev-in">
    <div class="ev-about2">
      <h2 class="ev-h2" id="about-title">About the roundtable</h2>
      <div class="ev-copy">{about}</div>
    </div>
    <dl class="ev-kv">
      <div><dt>Format</dt><dd>{ev['format_kv']}</dd></div>
      <div><dt>For</dt><dd>CTOs, COOs, CIOs, heads of data, research and operations</dd></div>
      <div><dt>Admission</dt><dd>By invitation</dd></div>
    </dl>
  </div>
</section>

<section class="ev-sec ev-sec-line" aria-labelledby="speakers-title">
  <div class="ev-in ev-about2">
    <h2 class="ev-h2" id="speakers-title">Speakers</h2>
    <div class="ev-spk">{people(ev)}</div>
  </div>
</section>

<section class="ev-sec ev-cream" aria-labelledby="agenda-title">
  <div class="ev-in">
    <h2 class="ev-h2" id="agenda-title">Agenda</h2>
    <ol class="ev-ag">
      {agenda(ev)}
    </ol>
  </div>
</section>

<section class="ev-sec ev-req" id="request" aria-labelledby="request-title">
  <div class="ev-in">
    <div class="ev-req-grid">
    <div>
      <h2 class="ev-h2" id="request-title">Request an invitation</h2>
      <p class="ev-req-sub">Seats are limited to about 20–25 senior guests. Share a few details and the Pascal team will confirm your place by email.</p>
    </div>
    <div class="ev-form-wrap">
      <form class="ev-form" data-event-form data-event="{ev['slug']}" data-event-name="{SERIES}: {TOPIC}" data-city="{ev['city']}" data-date="{ev['date']}" novalidate>
        <div class="ev-form-2">
          <label>Full name<input name="name" autocomplete="name" required></label>
          <label>Work email<input name="email" type="email" autocomplete="email" required></label>
        </div>
        <div class="ev-form-2">
          <label>Company name<input name="organization" autocomplete="organization" required></label>
          <label>Job title<input name="jobTitle" autocomplete="organization-title" required></label>
        </div>
        <label><span>Phone</span><span class="ev-phone"><select name="countryCode" aria-label="Country code">{opts}</select><input name="phone" type="tel" autocomplete="tel-national" inputmode="tel" required></span></label>
        <label><span>What would you like the speakers to cover? <span class="ev-opt">(optional)</span></span><textarea name="topics" rows="3"></textarea></label>
        <p class="ev-err" role="alert" hidden></p>
        <div class="ev-form-foot">
          <p class="ev-fine">By submitting, you agree to be contacted by us about this event.</p>
          <button class="btn btn-white" type="submit">Request an invitation</button>
        </div>
      </form>
      <div class="ev-done" hidden>
        <h3>Thank you.</h3>
        <p>We've received your request for {ev['city']}. The Pascal team will confirm your place at <b data-done-email></b>.</p>
      </div>
    </div>
    </div>
  </div>
</section>

<section class="ev-sec" aria-labelledby="host-title">
  <div class="ev-in">
    <h2 class="ev-h2" id="host-title">Hosted by</h2>
    {HOSTS}
  </div>
</section>

{more(others)}<script src="/assets/pages/events.js" defer></script>
"""


def hub():
    meta = {
        "path": "/events",
        "title": "Events | Pascal AI",
        "description": "Upcoming events with Pascal AI Labs: roundtables we host for hedge fund and asset manager leaders, and the industry forums where we speak.",
        "crumbs": [["Events", "/events"]],
        "og_kicker": "Pascal AI",
        "og_title": "Events",
        "llms": "Upcoming Pascal AI Labs events: hosted roundtables for hedge fund and asset manager leaders, and industry forums Pascal attends or speaks at.",
        "css": ["events.css"],
        "word_limit": 500, "faq_min": 0, "priority": 0.6,
    }
    items = []
    for n, ev in enumerate(LIVE):
        big, small = ev["photo"]
        flip = " flip" if n % 2 else ""
        items.append(f"""<section class="row split{flip}" aria-labelledby="ev-{ev['slug']}">
    <div class="split-copy">
      <p class="eyebrow">{ev['format']} · {ev['city']}</p>
      <h2 class="ev-hub-h" id="ev-{ev['slug']}">{SERIES}: {TOPIC}</h2>
      <p>{ROUNDTABLE_SUMMARY}</p>
      <dl class="ev-feat-dl">
        <div><dt>Date</dt><dd>{ev['date']}</dd></div>
        <div><dt>Time</dt><dd>{ev['time']}, {ev['time_sub']}</dd></div>
        <div><dt>Location</dt><dd>{ev['venue']}, {ev['venue_sub']}</dd></div>
      </dl>
      <a class="btn btn-dark ev-hub-btn" href="/events/{ev['slug']}">View event</a>
    </div>
    <div class="split-media"><a class="panel ev-hub-photo" href="/events/{ev['slug']}" aria-label="{ev['city']} event"><img src="{small}" srcset="{small} 1000w, {big} 2000w" sizes="(max-width: 1000px) 100vw, 640px" alt="{ev['city']} skyline" width="1000" height="667" loading="lazy" decoding="async"></a></div>
  </section>""")
    return meta_block(meta) + f"""<section class="hero-teal hero-ent" aria-labelledby="page-title">
  <div class="hero-teal-in">
    {{{{crumbs}}}}
    <div class="ht-grid">
      <div><h1 class="h1" id="page-title">Events</h1></div>
      <div class="ht-side">
        <p class="lead">Find us at industry conferences, join our private roundtables, and hear our team share perspectives on AI and institutional finance.</p>
      </div>
    </div>
  </div>
</section>
<div class="frame">
  {"".join(items)}
  <section class="row row-pad bg-cream" aria-labelledby="host-title">
    <h2 class="h2" id="host-title" style="margin-bottom:40px">About Pascal AI Labs</h2>
    {HOST}
  </section>
</div>
"""


if __name__ == "__main__":
    for ev in EVENTS:
        fp = PAGES / f"events-{ev['slug']}.html"
        if ev["live"]:
            fp.write_text(page(ev), encoding="utf-8")
        elif fp.exists():
            fp.unlink()  # unpublished: drop the page source so the build removes it
    (PAGES / "events.html").write_text(hub(), encoding="utf-8")
    print("wrote", ", ".join(f"events-{e['slug']}.html" for e in LIVE), "+ events.html")
