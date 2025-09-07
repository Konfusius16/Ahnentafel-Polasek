#!/usr/bin/env python3
"""
make_index.py – erstellt eine hübsche index.html mit Download-Optionen.

- Im Hauptverzeichnis: gruppiert PDF/SVG/PNG-Dateien nach Name.
  -> Radio-Buttons zur Auswahl des Formats (pdf/svg/png).
  -> „Ansehen“ und „Download“-Links passen sich an die Auswahl an.

- Im Unterordner "Unterlagen": zeigt Dateien + optionale Beschreibung
  aus gleichnamigen .txt-Dateien.
"""

from pathlib import Path
from datetime import datetime
import html

ROOT = Path(".")
OUT = ROOT / "index.html"
DOC_DIR = ROOT / "Unterlagen"
ALLOWED = {".pdf", ".svg", ".png"}

def human_size(n: int) -> str:
    """Dateigröße menschenfreundlich formatieren."""
    units = ["B","KB","MB","GB","TB"]
    i = 0
    f = float(n)
    while f >= 1024 and i < len(units)-1:
        f /= 1024.0
        i += 1
    return f"{f:.1f} {units[i]}" if i else f"{int(f)} {units[i]}"

def scan_main():
    files = [p for p in ROOT.iterdir() if p.is_file() and p.suffix.lower() in ALLOWED]
    groups = {}
    for p in files:
        groups.setdefault(p.stem, {}).update({p.suffix.lower(): p})
    return dict(sorted(groups.items(), key=lambda kv: kv[0].lower()))

def scan_unterlagen():
    items = []
    if not DOC_DIR.exists():
        return items
    for p in sorted(DOC_DIR.iterdir(), key=lambda x: x.name.lower()):
        if p.is_file() and p.suffix.lower() in ALLOWED:
            txt = p.with_suffix(".txt")
            text = ""
            if txt.exists():
                try:
                    text = txt.read_text(encoding="utf-8").strip()
                except Exception:
                    text = txt.read_text(errors="ignore").strip()
            items.append((p, text))
    return items

css = """
:root{
  --bg:#0b1118; --card:#0f1720; --fg:#e6eef7; --muted:#8aa0b7;
  --accent:#5bbcff; --accent2:#9ee493; --br:16px;
}
*{box-sizing:border-box}
body{margin:0; font:15px/1.6 ui-sans-serif,system-ui,Segoe UI,Roboto,Helvetica,Arial; color:var(--fg); background:linear-gradient(180deg,#0a1016,#0c121a 40%,#0b1118)}
.container{max-width:1080px; margin:36px auto; padding:0 16px}
h1{margin:0 0 10px; font-weight:800; letter-spacing:.2px}
.lead{color:var(--muted); margin:0 0 24px}
.card{background:linear-gradient(180deg,#101925,#0f1720); border:1px solid rgba(255,255,255,.06); border-radius:var(--br); box-shadow:0 10px 30px rgba(0,0,0,.35);}
.section{padding:18px 18px 6px; margin-bottom:18px}
.group{display:flex; align-items:center; justify-content:space-between; gap:14px; padding:12px 14px; margin:10px 0; border-radius:12px; background:rgba(255,255,255,.02); border:1px solid rgba(255,255,255,.05)}
.group .name{font-weight:700}
.meta{color:var(--muted); font-size:13px}
.formats{display:flex; gap:10px; align-items:center}
.format{display:flex; align-items:center; gap:6px; padding:6px 10px; border-radius:999px; background:rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.12)}
.format input{accent-color:var(--accent)}
.actions a{display:inline-flex; align-items:center; gap:8px; padding:8px 12px; border-radius:10px; text-decoration:none; border:1px solid rgba(255,255,255,.14); color:var(--fg)}
.actions a.primary{background:linear-gradient(180deg,#198bff,#0d6efd); border-color:transparent}
.actions{display:flex; gap:10px; flex-wrap:wrap}
h2{margin:6px 0 10px}
.details{padding:10px 14px; background:rgba(255,255,255,.03); border:1px solid rgba(255,255,255,.07); border-radius:12px; margin:8px 0 16px}
details>summary{cursor:pointer; font-weight:600}
footer{color:var(--muted); text-align:center; padding:20px 0 40px}
.badge{display:inline-block; padding:2px 8px; border-radius:999px; background:rgba(255,255,255,.1); border:1px solid rgba(255,255,255,.2); font-size:12px; margin-left:8px}
hr.sep{border:0; height:1px; background:linear-gradient(90deg,transparent,rgba(255,255,255,.2),transparent); margin:18px 0}
a:hover{color:#bfe2ff}
.tooltip{border-bottom:1px dotted var(--muted)}
"""

js = """
function applyChoice(stem, format){
  const aView = document.getElementById('view-'+stem);
  const aDl   = document.getElementById('dl-'+stem);
  const base  = document.getElementById('base-'+stem).dataset.base;
  const href  = base + '.' + format;
  aView.href = href; aDl.href = href;
  aView.dataset.ext = format; aDl.dataset.ext = format;
}
function initDefaults(){
  for (const wrap of document.querySelectorAll('[data-stem]')){
    const stem = wrap.dataset.stem;
    const first = wrap.querySelector('input[type=radio]');
    if (first){ first.checked = true; applyChoice(stem, first.value); }
  }
}
document.addEventListener('DOMContentLoaded', initDefaults);
"""

def radio(stem, ext, size):
    value = ext[1:]
    return (
        f'<label class="format">'
        f'<input type="radio" name="fmt-{stem}" '
        f'onchange="applyChoice(\'{stem}\', \'{value}\')" '
        f'value="{value}" /> {value.upper()} '
        f'<span class="meta">{size}</span>'
        f'</label>'
    )


def format_group_html(stem, fmt_map):
    radios = []
    for ext in (".pdf",".svg",".png"):
        if ext in fmt_map:
            size = human_size(fmt_map[ext].stat().st_size)
            radios.append(radio(stem, ext, size))
    if not radios:
        return ""
    base = html.escape(stem)
    first_ext = next(iter(fmt_map)).lstrip(".")
    return (
        f'<div class="group card" data-stem="{base}">'
        f'  <div class="name" id="base-{base}" data-base="{base}">{base}</div>'
        f'  <div class="formats">{"".join(radios)}</div>'
        f'  <div class="actions">'
        f'    <a id="view-{base}" class="primary" href="{base}.{first_ext}" target="_blank" rel="noopener">Ansehen</a>'
        f'    <a id="dl-{base}" href="{base}.{first_ext}" download>Download</a>'
        f'  </div>'
        f'</div>'
    )

def unterlagen_item_html(p: Path, text: str) -> str:
    name = html.escape(p.name)
    href = html.escape(str(p.relative_to(ROOT)))
    size = human_size(p.stat().st_size)
    tooltip = html.escape(text[:300]) if text else "Kein Beschreibungstext vorhanden."
    block = (
        f'<div class="group card">'
        f'  <div class="name"><a href="{href}" download title="{tooltip}" class="tooltip">{name}</a>'
        f'    <span class="badge">{size}</span>'
        f'  </div>'
        f'  <div class="actions"><a class="primary" href="{href}" target="_blank" rel="noopener">Ansehen</a>'
        f'  <a href="{href}" download>Download</a></div>'
        f'</div>'
    )
    if text:
        block += f'<div class="details"><details><summary>Beschreibung einblenden</summary><div style="white-space:pre-wrap;margin-top:8px;color:var(--muted)">{html.escape(text)}</div></details></div>'
    return block

def main():
    groups = scan_main()
    unterlagen = scan_unterlagen()
    parts = []
    parts.append(f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Downloads</title>
<style>{css}</style>
<script>{js}</script>
</head>
<body>
<div class="container">
  <h1>Downloads</h1>
  <p class="lead">Wähle oben das gewünschte Format (PDF/SVG/PNG). Unten findest du Unterlagen mit Beschreibungstext.</p>

  <div class="section card">
    <h2 style="padding:8px 12px 0;">Dateien im Hauptverzeichnis</h2>
""")

    if groups:
        for stem, fmap in groups.items():
            parts.append(format_group_html(stem, fmap))
    else:
        parts.append('<div class="group" style="justify-content:center;color:var(--muted)">Keine PDF/SVG/PNG-Dateien gefunden.</div>')

    parts.append("""
  </div>
  <hr class="sep"/>
  <div class="section card">
    <h2 style="padding:8px 12px 0;">Unterlagen</h2>
""")

    if unterlagen:
        for p, text in unterlagen:
            parts.append(unterlagen_item_html(p, text))
    else:
        parts.append('<div class="group" style="justify-content:center;color:var(--muted)">Verzeichnis „Unterlagen“ ist leer oder fehlt.</div>')

    parts.append(f"""
  </div>
  <footer>Stand: {datetime.now().strftime('%Y-%m-%d %H:%M')}</footer>
</div>
</body>
</html>
""")

    OUT.write_text("".join(parts), encoding="utf-8")
    print(f"Index-Seite erstellt: {OUT}")

if __name__ == "__main__":
    main()

