"""Brand logos for product visuals: {{logo:name}} -> <img> (or inline SVG where no hosted file exists).
Local files live in static/assets/logos; the rest come from the lobehub and simpleicons CDNs."""
LOB = "https://cdn.jsdelivr.net/npm/@lobehub/icons-static-svg@latest/icons/"
SI = "https://cdn.simpleicons.org/"
SRC = {
    # local
    **{n: f"/assets/logos/{n}.png" for n in ["accord", "azure", "box", "crustdata", "dropbox", "excel", "gdrive", "notion",
                                             "onedrive", "onenote", "outlook", "powerpoint", "probe42", "quartr", "sharepoint", "x", "youtube"]},
    # models and clouds
    "openai": LOB + "openai.svg", "claude": LOB + "claude-color.svg", "gemini": LOB + "gemini-color.svg",
    "mistral": LOB + "mistral-color.svg", "deepseek": LOB + "deepseek-color.svg", "llama": LOB + "meta-color.svg",
    "copilot": LOB + "copilot-color.svg", "microsoft": LOB + "microsoft-color.svg", "mcp": LOB + "mcp.svg",
    "aws": LOB + "aws-color.svg", "bedrock": LOB + "bedrock-color.svg", "gcp": LOB + "googlecloud-color.svg",
    "cursor": LOB + "cursor.svg", "perplexity": LOB + "perplexity.svg",
    # apps and signals
    "reddit": SI + "reddit/FF4500", "applepodcasts": SI + "applepodcasts/9933CC", "spotify": SI + "spotify/1DB954",
    "hubspot": SI + "hubspot/FF7A59", "gmail": SI + "gmail/EA4335",
    "zoom": SI + "zoom/0B5CFF", "youtube-icon": SI + "youtube/FF0000", "snowflake": SI + "snowflake/29B5E8", "databricks": SI + "databricks/FF3621",
    "postgres": SI + "postgresql/4169E1", "okta": SI + "okta/007DC1", "gsheets": SI + "googlesheets/34A853",
    # companies used in examples
    "nvidia": SI + "nvidia/76B900", "meta": SI + "meta/0467DF", "shopee": SI + "shopee/EE4D2D",
}
# Microsoft Teams and Word have no hosted icon; simplified marks drawn here
INLINE = {
    "teams": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="18.5" cy="6.5" r="2.3" fill="#7B83EB"/><rect x="14" y="9.6" width="9" height="8.4" rx="2.4" fill="#7B83EB"/><circle cx="12.3" cy="5.4" r="3" fill="#5059C9"/><rect x="6.5" y="9" width="11.5" height="11" rx="3" fill="#5059C9"/><rect x="1" y="6.5" width="11" height="11" rx="1.6" fill="#4B53BC"/><path d="M3.6 9.3h5.8v1.4H7.2v5H5.8v-5H3.6z" fill="#fff"/></svg>',
    "word": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="7" y="2" width="15" height="20" rx="2" fill="#41A5EE"/><rect x="7" y="7" width="15" height="5" fill="#2B7CD3"/><rect x="7" y="12" width="15" height="5" fill="#185ABD"/><rect x="7" y="17" width="15" height="5" rx="0" fill="#103F91"/><rect x="2" y="6" width="11" height="12" rx="1.6" fill="#185ABD"/><path d="M3.9 9h1.4l.9 4 1-4h1.2l1 4 .9-4h1.3l-1.6 6H8.7L7.8 11.3 6.9 15H5.5z" fill="#fff"/></svg>',
    "pdf": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 2h10l5 5v15H5z" fill="#E5E7EB"/><path d="M15 2v5h5" fill="#CBD0D6"/><rect x="2" y="11" width="14" height="7" rx="1.4" fill="#D93025"/><text x="9" y="16.4" font-family="Arial" font-weight="700" font-size="5.2" text-anchor="middle" fill="#fff">PDF</text></svg>',
}

def logo(name, cls=""):
    c = f' class="{cls}"' if cls else ""
    if name in INLINE:
        return INLINE[name].replace("<svg ", f'<svg{c} width="18" height="18" ', 1)
    if name not in SRC:
        raise SystemExit(f"unknown logo: {name}")
    return f'<img{c} src="{SRC[name]}" alt="" width="18" height="18" loading="lazy">'
