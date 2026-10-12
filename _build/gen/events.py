#!/usr/bin/env python3
"""Event pages: writes _build/pages/events*.html from the EVENTS data below.

    python3 _build/gen/events.py && python3 _build/build.py --only events,events-hong-kong-2026,events-new-york-2026

Layout follows LinqAlpha's summit pages: city photo hero with a date / time / location strip, About,
Agenda, Speakers, a request-an-invitation form and the rest of the series. Copy is the user's event brief.
Set "start"/"end" (ISO with offset) once a date is confirmed; that also switches on Event schema.
To add a hero photo, drop it in _build/static/assets/photos/ and set "photo".
"""
import json
from pathlib import Path

PAGES = Path(__file__).resolve().parents[1] / "pages"

SERIES = "Front Office to Back Office"
TOPIC = "Where AI Is Actually Working in Asset Management"
INVITE = ("An invite-only roundtable breakfast for about 20–25 senior guests from hedge funds and asset managers: "
          "CTOs, COOs, CIOs, and heads of data, research and operations.")
NOTE = ("Please note: this is an invite-only roundtable breakfast for about 20–25 senior guests from hedge funds "
        "and asset managers. Admission is by invitation.")

EVENTS = [
    {
        "slug": "hong-kong-2026", "city": "Hong Kong", "country": "HK", "cc": "+852",
        "date": "27 October 2026 (Tue)", "date_short": "27 Oct 2026", "date_sub": "",
        "time": "8:00–10:30 AM", "time_sub": "Hong Kong time",
        "venue": "Hong Kong", "venue_sub": "Venue to be confirmed",
        "start": "2026-10-27T08:00:00+08:00", "end": "2026-10-27T10:30:00+08:00",
        "photo": None,  # e.g. "/assets/photos/event-hong-kong.jpg"
        "title": "Front Office to Back Office: AI Roundtable, Hong Kong",
        "description": "Invite-only roundtable breakfast in Hong Kong on 27 October 2026 for hedge fund and asset manager leaders on where AI is working, front to back office.",
        "about": [
            INVITE,
            "After breakfast and a short welcome, we open with what has changed in the past 12 months: AI moving from "
            "analyst tools into core fund workflows, and what that asks of data and controls.",
            "This leads into a moderated discussion with <b>Rowel Balot</b> (CTO, Bare Cove Technology) and "
            "<b>Vibhav Viswanathan</b> (CEO &amp; Co-Founder, Pascal AI Labs), in three segments of about 15–20 minutes "
            "each. Guests then share their experience and questions, followed by optional networking.",
        ],
        "opening": "What has changed in the past 12 months: AI moving from analyst tools into core fund workflows, "
                   "and what that asks of data and controls.",
        "opening_t": "After breakfast",
        "welcome": "Breakfast and a short welcome",
        "speakers": [("Rowel Balot", "CTO", "Bare Cove Technology", "Speaker"),
                     ("Vibhav Viswanathan", "CEO &amp; Co-Founder", "Pascal AI Labs", "Speaker")],
        "moderator": None,
        "segments": [
            ("Where AI is earning its place", "Which workflows have moved beyond pilots, and which haven't."),
            ("Build, buy, or rely on your servicer", "What funds build in-house, buy, or expect from administrators and service providers."),
            ("Trust and control", "Security, auditability and governance before AI touches client-facing or NAV work."),
        ],
        "floor": "Guests share their experience and questions.",
        "close_t": "Until 10:30 AM", "close": "Optional networking.",
    },
    {
        "slug": "new-york-2026", "city": "New York", "country": "US", "cc": "+1",
        "date": "First week of November 2026", "date_short": "Early Nov 2026", "date_sub": "Exact date to be confirmed",
        "time": "8:00–10:30 AM", "time_sub": "Eastern time",
        "venue": "New York", "venue_sub": "Venue to be confirmed",
        "start": None, "end": None,
        "photo": ("/assets/photos/hero-manhattan.jpg", "/assets/photos/hero-manhattan-sm.jpg"),
        "title": "Front Office to Back Office: AI Roundtable, New York",
        "description": "Invite-only roundtable breakfast in New York, first week of November 2026, for hedge fund and asset manager leaders on where AI is working in funds.",
        "about": [
            INVITE,
            "We'll start the session with a short welcome, breakfast, why this group is in the room, and the opening "
            "perspective. A brief view on what has changed in the past 12 months: AI moving from analyst tools into the "
            "fund's core workflows across research, risk, compliance and operations, and what that asks of data and controls.",
            "Then, we'll move to a moderated discussion with <b>Sean Lee</b> (D1 Capital Partners) and <b>Jay Rooney</b> "
            "(MUFG Investor Services), with us as the moderators, in three segments of roughly 15–20 minutes each.",
            "After this, the guests share their own experience and questions for the speakers to respond. At the end, "
            "we'll close with optional networking for about 20–30 minutes.",
        ],
        "opening": "A brief view on what has changed in the past 12 months: AI moving from analyst tools into the fund's "
                   "core workflows across research, risk, compliance and operations, and what that asks of data and controls.",
        "opening_t": "Opening perspective",
        "welcome": "Short welcome, breakfast and why this group is in the room",
        "speakers": [("Sean Lee", "", "D1 Capital Partners", "Speaker"),
                     ("Jay Rooney", "", "MUFG Investor Services", "Speaker")],
        "moderator": ("Pascal AI Labs", "", "Host", "Moderator"),
        "segments": [
            ("Where AI is earning its place", "Which workflows have moved beyond pilots, at the manager and at the servicer, and which have not."),
            ("Build, buy, or rely on your servicer", "How funds decide what to build in-house, what to buy, and what to expect from administrators and service providers; how the manager–administrator relationship changes when both sides run AI."),
            ("Trust and control", "Data security, auditability and governance: what investors, boards and regulators will ask, and what has to be in place before AI touches anything client-facing or NAV-related."),
        ],
        "floor": "The guests share their own experience and questions for the speakers to respond.",
        "close_t": "About 20–30 min", "close": "Close, with optional networking.",
    },
]

COUNTRIES = [("+852", "Hong Kong"), ("+1", "United States"), ("+44", "United Kingdom"), ("+65", "Singapore"),
             ("+91", "India"), ("+971", "United Arab Emirates"), ("+61", "Australia"), ("+81", "Japan"),
             ("+86", "China"), ("+49", "Germany"), ("+33", "France"), ("+41", "Switzerland")]


def meta_block(m):
    return "<!--meta\n" + json.dumps(m, indent=1, ensure_ascii=False) + "\n-->\n"


def hero_media(ev, cls="ev-hero-img", lazy=False):
    if not ev["photo"]:
        return '<div class="ev-hero-plain" aria-hidden="true"></div>'
    big, small = ev["photo"]
    load = ' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high"'
    return (f'<img class="{cls}" src="{big}" srcset="{small} 1000w, {big} 2000w" sizes="100vw" alt="" '
            f'width="2000" height="1333"{load}>')


def tile(ev):
    if ev["photo"]:
        big, small = ev["photo"]
        img = f'<img src="{small}" alt="" width="1000" height="667" loading="lazy" decoding="async">'
    else:
        img = ""
    return f"""<a class="ev-tile" href="/events/{ev['slug']}">
      {img}
      <span class="ev-tile-k">Invite-only roundtable breakfast</span>
      <span class="ev-tile-city">{ev['city']}</span>
      <span class="ev-tile-t">{SERIES}: {TOPIC}</span>
      <span class="ev-tile-row"><span>{ev['date_short']} · {ev['time']}</span><b>View event</b></span>
    </a>"""


def card(name, title, firm, role):
    t = f'<p class="ev-card-p">{title}</p>' if title else ""
    return f"""<div class="ev-card"><p class="ev-card-role">{role}</p><p class="ev-card-n">{name}</p>{t}<p class="ev-card-f">{firm}</p></div>"""


def page(ev):
    others = [o for o in EVENTS if o is not ev]
    who = "".join(f"<span><b>{n}</b> · {(t + ', ') if t else ''}{f}</span>" for n, t, f, _ in ev["speakers"])
    if ev["moderator"]:
        who += f"<span>Moderated by <b>{ev['moderator'][0]}</b></span>"
    segs = "".join(f"<li><b>{h}.</b><span>{d}</span></li>" for h, d in ev["segments"])
    cards = "".join(card(*s) for s in ev["speakers"])
    if ev["moderator"]:
        n, t, f, r = ev["moderator"]
        cards += card(n, t, "Pascal AI Labs hosts and moderates the discussion.", r)
    opts = "".join(f'<option value="{c}" data-country="{n}"{" selected" if c == ev["cc"] else ""}>{n} ({c})</option>'
                   for c, n in COUNTRIES)
    date_sub = f"<small>{ev['date_sub']}</small>" if ev["date_sub"] else ""
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
        "word_limit": 900, "faq_min": 0, "lead_min": 6, "priority": 0.6,
        "event": {"name": f"{SERIES}: {TOPIC} ({ev['city']})", "start": ev["start"], "end": ev["end"],
                  "place": ev["venue"], "city": ev["city"], "country": ev["country"],
                  "speakers": [(n, f"{t}, {f}" if t else f) for n, t, f, _ in ev["speakers"]]},
    }
    return meta_block(meta) + f"""<section class="ev-hero dark" aria-labelledby="page-title">
  {hero_media(ev)}
  <div class="ev-hero-in">
    <p class="ev-kicker">Invite-only roundtable breakfast · Hosted by Pascal AI Labs</p>
    <h1 class="ev-h1" id="page-title"><span class="ev-series">{SERIES}</span> <span class="ev-city">{ev['city']}</span></h1>
    <p class="lead">{TOPIC}</p>
    <div class="actions"><a class="btn btn-white" href="#request">Request an invitation</a></div>
  </div>
  <div class="ev-facts">
    <dl class="ev-facts-in">
      <div class="ev-fact"><dt>Date</dt><dd>{ev['date']}{date_sub}</dd></div>
      <div class="ev-fact"><dt>Time</dt><dd>{ev['time']}<small>{ev['time_sub']}</small></dd></div>
      <div class="ev-fact"><dt>Location</dt><dd>{ev['venue']}<small>{ev['venue_sub']}</small></dd></div>
    </dl>
  </div>
  <p class="ev-note">{NOTE}</p>
</section>

<section class="ev-sec" aria-labelledby="about-title">
  <div class="ev-in ev-about">
    <h2 class="ev-h2" id="about-title">About the roundtable</h2>
    <div class="ev-about-copy">
      {about}
      <dl class="ev-meta">
        <div><dt>Format</dt><dd>Roundtable breakfast, about 20–25 guests</dd></div>
        <div><dt>For</dt><dd>CTOs, COOs, CIOs, heads of data, research and operations</dd></div>
        <div><dt>Hosted by</dt><dd>Pascal AI Labs, with AI for <a href="/solutions/hedge-funds">hedge funds</a>, <a href="/solutions/asset-wealth-management">asset managers</a> and <a href="/solutions/asset-servicing">fund servicers</a></dd></div>
      </dl>
    </div>
  </div>
</section>

<section class="ev-sec ev-agenda ev-mint" aria-labelledby="agenda-title">
  <div class="ev-in">
    <h2 class="ev-h2" id="agenda-title">Agenda</h2>
    <ol class="ev-ag">
      <li><p class="ev-ag-t">8:00 AM</p><div><h3 class="ev-ag-h">{ev['welcome']}</h3></div></li>
      <li><p class="ev-ag-t">{ev['opening_t']}</p><div><h3 class="ev-ag-h">What has changed in the past 12 months</h3><p class="ev-ag-d">{ev['opening']}</p></div></li>
      <li><p class="ev-ag-t">Three segments, about 15–20 min each</p><div><span class="ev-ag-tag">Moderated discussion</span><h3 class="ev-ag-h">{SERIES}: {TOPIC}</h3><p class="ev-ag-who">{who}</p><ol class="ev-segs">{segs}</ol></div></li>
      <li><p class="ev-ag-t">Open floor</p><div><h3 class="ev-ag-h">Guest experience and questions</h3><p class="ev-ag-d">{ev['floor']}</p></div></li>
      <li><p class="ev-ag-t">{ev['close_t']}</p><div><h3 class="ev-ag-h">{ev['close']}</h3></div></li>
    </ol>
  </div>
</section>

<section class="ev-sec ev-speakers ev-cream" aria-labelledby="speakers-title">
  <div class="ev-in">
    <h2 class="ev-h2" id="speakers-title">Speakers</h2>
    <div class="ev-spk">{cards}</div>
  </div>
</section>

<section class="ev-sec ev-req" id="request" aria-labelledby="request-title">
  <div class="ev-in ev-req-grid">
    <div class="ev-req-copy">
      <h2 class="ev-h2" id="request-title">Request an invitation</h2>
      <p>Seats are limited to about 20–25 senior guests. Tell us a little about you and the Pascal team will confirm your place by email.</p>
      <dl class="ev-req-sum">
        <div><dt>Event</dt><dd>{SERIES}: {TOPIC}</dd></div>
        <div><dt>Date</dt><dd>{ev['date']}</dd></div>
        <div><dt>Time</dt><dd>{ev['time']} ({ev['time_sub']})</dd></div>
        <div><dt>Location</dt><dd>{ev['venue']} · {ev['venue_sub'].lower()}</dd></div>
      </dl>
    </div>
    <div class="ev-form-card">
      <form class="ev-form" data-event-form data-event="{ev['slug']}" data-event-name="{SERIES}: {TOPIC}" data-city="{ev['city']}" data-date="{ev['date']}" novalidate>
        <label>Full name *<input name="name" autocomplete="name" required></label>
        <label>Work email *<input name="email" type="email" autocomplete="email" required></label>
        <div class="ev-form-2">
          <label>Firm *<input name="organization" autocomplete="organization" required></label>
          <label>Job title *<input name="jobTitle" autocomplete="organization-title" required></label>
        </div>
        <label>Phone <span class="ev-opt">(optional)</span><span class="ev-phone"><select name="countryCode" aria-label="Country code">{opts}</select><input name="phone" type="tel" autocomplete="tel-national" inputmode="tel"></span></label>
        <label>What would you like the speakers to cover? <span class="ev-opt">(optional)</span><textarea name="topics" rows="3"></textarea></label>
        <p class="ev-err" role="alert" hidden></p>
        <button class="btn btn-dark" type="submit">Request an invitation</button>
        <p class="ev-fine">By submitting, you agree to be contacted by Pascal AI Labs about this event.</p>
      </form>
      <div class="ev-done" hidden>
        <span class="ev-done-ok">{{{{icon:check}}}}</span>
        <h3>Thank you.</h3>
        <p>We've received your request for {ev['city']}. The Pascal team will confirm your place at <b data-done-email></b>.</p>
      </div>
    </div>
  </div>
</section>

<section class="ev-sec ev-more ev-mint" aria-labelledby="more-title">
  <div class="ev-in">
    <h2 class="ev-h2" id="more-title">Also in the series</h2>
    <div class="ev-more-grid">
      {"".join(tile(o) for o in others)}
      <div class="ev-more-links">
        <p>Pascal AI Labs builds AI agents for institutional finance, from research in the front office to operations and reporting in the back office.</p>
        <a href="/events">All events<span>Upcoming roundtables hosted by Pascal AI Labs</span></a>
        <a href="/platform">The Pascal platform<span>Context graph, agents and governance in one workspace</span></a>
        <a href="/security">Security<span>How Pascal keeps your data inside your perimeter</span></a>
      </div>
    </div>
  </div>
</section>
<script src="/assets/pages/events.js" defer></script>
"""


def hub():
    meta = {
        "path": "/events",
        "title": "Events: AI Roundtables for Asset Managers | Pascal AI",
        "description": "Upcoming invite-only roundtables hosted by Pascal AI Labs for hedge fund and asset manager leaders, in Hong Kong and New York.",
        "crumbs": [["Events", "/events"]],
        "og_kicker": "Pascal AI",
        "og_title": "Events and roundtables",
        "llms": "Upcoming Pascal AI Labs events: invite-only roundtable breakfasts in Hong Kong and New York on where AI is working in asset management.",
        "css": ["events.css"],
        "word_limit": 500, "faq_min": 0, "priority": 0.6,
    }
    tiles = "".join(tile(e) for e in EVENTS)
    return meta_block(meta) + f"""<section class="ev-top" aria-labelledby="page-title">
  <div class="ev-in">
    <h1 class="ev-h1" id="page-title">Events</h1>
    <p class="lead">Invite-only roundtables where senior leaders from hedge funds and asset managers compare notes on where AI is working across the front, middle and back office.</p>
  </div>
</section>

<section class="ev-sec ev-mint" aria-labelledby="upcoming-title">
  <div class="ev-in">
    <h2 class="ev-h2" id="upcoming-title" style="margin-bottom:36px">Upcoming</h2>
    <div class="ev-list">{tiles}</div>
  </div>
</section>

<section class="ev-sec" aria-labelledby="series-title">
  <div class="ev-in ev-about">
    <h2 class="ev-h2" id="series-title">{SERIES}</h2>
    <div class="ev-about-copy">
      <p>{TOPIC}. Each breakfast brings together about 20–25 CTOs, COOs, CIOs and heads of data, research and operations for a moderated discussion in three segments: where AI is earning its place, build, buy, or rely on your servicer, and trust and control.</p>
      <dl class="ev-meta">
        <div><dt>Format</dt><dd>Roundtable breakfast, 8:00–10:30 AM</dd></div>
        <div><dt>Admission</dt><dd>By invitation</dd></div>
        <div><dt>Hosted by</dt><dd>Pascal AI Labs, with AI for <a href="/solutions/hedge-funds">hedge funds</a>, <a href="/solutions/asset-wealth-management">asset managers</a> and <a href="/solutions/asset-servicing">fund servicers</a></dd></div>
      </dl>
    </div>
  </div>
</section>
"""


if __name__ == "__main__":
    for ev in EVENTS:
        (PAGES / f"events-{ev['slug']}.html").write_text(page(ev), encoding="utf-8")
    (PAGES / "events.html").write_text(hub(), encoding="utf-8")
    print("wrote", ", ".join(f"events-{e['slug']}.html" for e in EVENTS), "+ events.html")
