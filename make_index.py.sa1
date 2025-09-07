#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import fnmatch
import html
import mimetypes
import os
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_EXCLUDES = [
    "index.html",
    ".git/*",
    ".git",
    ".gitattributes",
    ".gitignore",
]

TEXT_EXT = {".txt", ".yaml", ".yml", ".csv", ".json", ".md", ".log"}
IMG_EXT  = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
PDF_EXT  = {".pdf"}

def css_text():
    return "\n".join([
        ":root { --fg:#111; --muted:#666; --bg:#fafafa; --card:#fff; --br:14px; }",
        "body { margin:0; font:16px/1.5 system-ui,Segoe UI,Roboto,Helvetica,Arial,sans-serif; color:var(--fg); background:var(--bg); }",
        ".wrap { max-width:980px; margin:32px auto; padding:0 16px; }",
        "h1 { margin:0 0 8px; }",
        "p.note { color:var(--muted); margin:0 0 24px; }",
        "ul.files { list-style:none; padding:0; margin:0 0 28px; }",
        "ul.files li { background:var(--card); border-radius:var(--br); padding:14px 16px; margin:10px 0; display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:10px; box-shadow:0 1px 4px rgba(0,0,0,.06); }",
        ".meta { color:var(--muted); font-size:13px; }",
        ".name { font-weight:600; }",
        ".actions a { margin-left:12px; text-decoration:none; }",
        ".actions a:first-child { margin-left:0; }",
        ".preview { background:var(--card); border-radius:var(--br); padding:16px; box-shadow:0 1px 4px rgba(0,0,0,.06); }",
        "img.preview-img { max-width:100%; height:auto; display:block; border-radius:12px; }",
        "details { background:var(--card); border-radius:var(--br); padding:10px 12px; margin-top:12px; box-shadow:0 1px 4px rgba(0,0,0,.06); }",
        "details > summary { cursor:pointer; font-weight:600; }",
        "iframe.txt { width:100%; height:60vh; border:0; border-radius:10px; margin-top:10px; background:#fff; }",
        "object.pdf { width:100%; height:75vh; border:0; border-radius:10px; }",
        "footer { color:var(--muted); font-size:13px; margin-top:28px; text-align:center; }",
        "@media (prefers-color-scheme: dark) {",
        "  :root { --fg:#eee; --muted:#aaa; --bg:#0d0f12; --card:#14171c; }",
        "  a { color:#8ab4ff; }",
        "}",
    ])

def human_size(num: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    for i, unit in enumerate(units):
        if num < 1024.0 or unit == units[-1]:
            if unit == "B":
                return f"{num:.0f} {unit}"
            return f"{num:.1f} {unit}"
        num /= 1024.0

def match_any(path: str, patterns):
    p = path.replace(os.sep, "/")
    return any(fnmatch.fnmatch(p, pat) for pat in patterns)

def categorize(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in IMG_EXT:
        return "image"
    if ext in PDF_EXT:
        return "pdf"
    if ext in TEXT_EXT:
        return "text"
    mt, _ = mimetypes.guess_type(str(path))
    if mt:
        if mt.startswith("image/"): return "image"
        if mt == "application/pdf": return "pdf"
        if mt.startswith("text/"): return "text"
    return "other"

def build_list_item(rel_path: str, size: int, mtime: float, target_blank: bool, prefix: str) -> str:
    name = html.escape(rel_path)
    href = html.escape(prefix + rel_path)
    view_target = ' target="_blank" rel="noopener"' if target_blank else ""
    size_s = human_size(size)
    mtime_s = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
    return (
        "<li>"
        "<div>"
        f'<div class="name">{name}</div>'
        f'<div class="meta">{size_s} · geändert: {mtime_s}</div>'
        "</div>"
        '<div class="actions">'
        f'<a href="{href}"{view_target}>ansehen</a>'
        f'<a href="{href}" download>download</a>'
        "</div>"
        "</li>"
    )

def build_preview_block(rel_path: str, kind: str, prefix: str) -> str:
    esc = html.escape(rel_path)
    href = html.escape(prefix + rel_path)
    if kind == "image":
        return (
            '<div class="preview">'
            f"<h2>Bild-Vorschau: {esc}</h2>"
            f'<img class="preview-img" src="{href}" alt="{esc}" />'
            "</div>"
        )
    if kind == "pdf":
        return (
            '<div class="preview">'
            f"<h2>PDF-Vorschau: {esc}</h2>"
            f'<object class="pdf" data="{href}" type="application/pdf">'
            f'<p><a href="{href}">PDF öffnen</a></p>'
            "</object>"
            "</div>"
        )
    if kind == "text":
        return (
            "<details>"
            f"<summary>Text-Vorschau: {esc}</summary>"
            f'<iframe class="txt" src="{href}"></iframe>'
            "</details>"
        )
    return ""

def main():
    ap = argparse.ArgumentParser(description="Erzeuge index.html mit Download-/Ansehen-Links für alle Dateien im Ordner.")
    ap.add_argument("--out", default="index.html", help="Zieldatei (default: index.html)")
    ap.add_argument("--root", default="./", help="Wurzelordner (default: ./)")
    ap.add_argument("--title", default="Downloads", help="Seitentitel")
    ap.add_argument("--recursive", action="store_true", help="Unterordner rekursiv einbeziehen")
    ap.add_argument("--exclude", action="append", default=None, help="Zusätzliche Ausschlussmuster (glob). Mehrfach nutzbar.")
    ap.add_argument("--no-previews", action="store_true", help="Keine Inline-Vorschauen erzeugen")
    ap.add_argument("--target-blank", action="store_true", help="Links in neuem Tab öffnen")
    ap.add_argument("--prefix", default="./", help="Link-Prefix vor jedem Dateipfad (default: ./)")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"Fehler: root '{root}' nicht gefunden", file=sys.stderr)
        sys.exit(1)

    excludes = list(DEFAULT_EXCLUDES)
    try:
        excludes.append(Path(__file__).name)
    except NameError:
        pass
    if args.exclude:
        excludes.extend(args.exclude)

    files = []
    if args.recursive:
        for p in root.rglob("*"):
            if p.is_file():
                rel = str(p.relative_to(root)).replace(os.sep, "/")
                if not match_any(rel, excludes):
                    files.append(p)
    else:
        for p in root.iterdir():
            if p.is_file():
                rel = p.name
                if not match_any(rel, excludes):
                    files.append(p)

    files.sort(key=lambda x: str(x).lower())

    items_html = []
    previews_html = []
    for p in files:
        rel = str(p.relative_to(root)).replace(os.sep, "/")
        try:
            st = p.stat()
            size = st.st_size
            mtime = st.st_mtime
        except OSError:
            size, mtime = 0, 0.0

        items_html.append(build_list_item(rel, size, mtime, args.target_blank, args.prefix))

        if not args.no_previews:
            kind = categorize(p)
            if kind in {"image", "pdf", "text"}:
                previews_html.append(build_preview_block(rel, kind, args.prefix))

    # HTML bauen (ohne Triple-Quotes)
    head = (
        "<!doctype html>\n"
        "<html lang=\"de\">\n"
        "<head>\n"
        "  <meta charset=\"utf-8\" />\n"
        "  <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\" />\n"
        f"  <title>{html.escape(args.title)}</title>\n"
        "  <style>\n"
        f"{css_text()}\n"
        "  </style>\n"
        "</head>\n"
    )
    body_open = "<body>\n  <div class=\"wrap\">\n"
    header = (
        f"    <h1>{html.escape(args.title)}</h1>\n"
        "    <p class=\"note\">Ansehen im Browser oder direkt herunterladen. Diese Seite wurde automatisch erzeugt.</p>\n"
        "    <ul class=\"files\">\n"
        f"{''.join(items_html)}\n"
        "    </ul>\n"
    )
    previews_block = "".join(previews_html)
    footer = (
        f"    <footer>Generiert am {datetime.now().strftime('%Y-%m-%d %H:%M')} · {len(files)} Dateien</footer>\n"
        "  </div>\n</body>\n</html>\n"
    )

    html_out = head + body_open + header + previews_block + footer
    out_path = (root / args.out)
    out_path.write_text(html_out, encoding="utf-8")
    print(f"✔ index erzeugt: {out_path}")

if __name__ == "__main__":
    main()
    
