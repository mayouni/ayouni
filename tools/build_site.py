#!/usr/bin/env python3
"""build_site — assemble the AYOUNI house site from the books the house pins.

    python tools/build_site.py                 # writes site/ (ignored by git; GitHub Actions rebuilds it)
    python tools/build_site.py --out other     # elsewhere inside this repository

What it does, from site-src/books.json:
  * copies each published book's readers, manifest, agents' files and covers, byte for byte (no page is rewritten,
    so every draft banner survives); refuses a PDF, an ePub or any file type the house does not publish;
  * writes the index of the books in English (site/index.html) and French (site/fr/index.html) from site-src/index.tmpl.html,
    reading titles, counts and stamps from each book's own manifest, never composing them;
  * writes llms.txt and house.json (the exact URLs, the commit each book was built from, the sha256 of what was copied);
  * writes .nojekyll.
It changes nothing in a book. Then run:  python tools/check_public.py site
"""
import argparse, hashlib, html, json, re, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path
from string import Template
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "site-src" / "books.json"
TEMPLATE = ROOT / "site-src" / "index.tmpl.html"
PUBLISHABLE = {".html", ".json", ".txt", ".md", ".png", ".svg", ".css", ".js", ".woff2", ".jpg", ".webp"}
MONTHS = {
    "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    "fr": ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"],
}

STRINGS = {
    "en": {
        "page_title": "AYOUNI Press",
        "description": "The books of Mansour Ayouni, published by AYOUNI Press as readers for people and as data for AI agents.",
        "lead": "The books of Mansour Ayouni: readers for people, data for AI agents.",
        "lang_label": "Language",
        "cover_alt": "Cover of {title}",
        "state_all": "{n} pages, all in {status}. Every page carries its draft banner.",
        "state_mixed": "{n} pages: {parts}.",
        "state_none": "Its reader is not on this address yet.",
        "status_word": {"draft": "draft", "read": "read"},
        "built": "Built {date}.",
        "read_en": "Read in English",
        "read_fr": "Lire en français",
        "notes": {
            "book.json": "the whole book as data",
            "llms-book.txt": "a summary for AI agents",
            "llms-full-book.txt": "every page as text",
        },
        "agents_h": "For AI agents",
        "agents_p": ("Each published book is also data, at the same address as its readers: a manifest, a summary, the full text, "
                     "and one file per page (agents/&lt;slug&gt;.md). llms.txt lists them; house.json gives the exact URLs and "
                     "the commit each book was built from."),
        "footer": "AYOUNI Press is the books imprint of AYOUNI.",
    },
    "fr": {
        "page_title": "Éditions AYOUNI",
        "description": "Les livres de Mansour Ayouni, publiés par Éditions AYOUNI comme lecteurs pour les personnes et comme données pour les agents d'IA.",
        "lead": "Les livres de Mansour Ayouni : des lecteurs pour les personnes, des données pour les agents d'IA.",
        "lang_label": "Langue",
        "cover_alt": "Couverture de {title}",
        "state_all": "{n} pages, toutes en {status}. Chaque page porte son bandeau de brouillon.",
        "state_mixed": "{n} pages : {parts}.",
        "state_none": "Son lecteur n'est pas encore à cette adresse.",
        "status_word": {"draft": "brouillon", "read": "lue"},
        "built": "Construit le {date}.",
        "read_en": "Read in English",
        "read_fr": "Lire en français",
        "notes": {
            "book.json": "le livre entier en données",
            "llms-book.txt": "un résumé pour les agents d'IA",
            "llms-full-book.txt": "chaque page en texte",
        },
        "agents_h": "Pour les agents d'IA",
        "agents_p": ("Chaque livre publié est aussi une donnée, à la même adresse que ses lecteurs : un manifeste, un résumé, le texte intégral "
                     "et un fichier par page (agents/&lt;slug&gt;.md). llms.txt les liste ; house.json donne les adresses exactes et "
                     "le commit d'où chaque livre a été construit."),
        "footer": "Éditions AYOUNI est la ligne de livres de la maison AYOUNI.",
    },
}


def git(*args, cwd):
    try:
        r = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, encoding="utf-8")
    except OSError:
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def stamp_now():
    now = datetime.now().astimezone()
    off = now.strftime("%z")
    return now.strftime("%Y-%m-%d %H:%M") + " UTC" + off[:3] + ":" + off[3:]


def full_date(stamp, lang):
    m = re.match(r"(\d{4})-(\d{2})-(\d{2}) (\d{2}:\d{2}) (UTC[+-]\d{2}:\d{2})", stamp or "")
    if not m:
        return stamp or ""
    y, mo, d, hm, tz = m.groups()
    day = int(d)
    day_s = "1er" if (lang == "fr" and day == 1) else str(day)
    return f"{day_s} {MONTHS[lang][int(mo) - 1]} {y}, {hm} {tz}"


def die(msg):
    print("build_site: " + msg, file=sys.stderr)
    sys.exit(1)


def copy_file(src, dst, report):
    if src.suffix.lower() not in PUBLISHABLE:
        die(f"{src} is a type the house does not publish ({src.suffix}); no PDF, ePub or archive goes online")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    report[dst] = sha256(dst)


def publish_book(book, out, report):
    folder = ROOT / book["folder"]
    dest = out / "books" / book["slug"]
    manifest_path = folder / book["manifest"]
    if not manifest_path.is_file():
        die(f"{manifest_path} is missing (is the submodule checked out?)")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    published = []
    for rel in [book["entry"], *book["readers"].values(), *book["files"], *book["covers"].values()]:
        src = folder / rel
        if not src.is_file():
            die(f"{src} is missing")
        copy_file(src, dest / rel, report)
        published.append(rel)
    for d in book.get("dirs", []):
        for src in sorted((folder / d).rglob("*")):
            if src.is_file():
                rel = src.relative_to(folder).as_posix()
                copy_file(src, dest / rel, report)
                published.append(rel)
    return manifest, published


def book_state(book):
    """The commit a published book is at, the commit the house pins, and whether the files we publish differ from the commit."""
    folder = ROOT / book["folder"]
    head = git("rev-parse", "HEAD", cwd=folder)
    pinned = None
    tree = git("ls-tree", "HEAD", book["folder"], cwd=ROOT)
    if tree:
        m = re.match(r"160000 commit ([0-9a-f]{40})\t", tree)
        pinned = m.group(1) if m else None
    paths = [book["entry"], *book["readers"].values(), *book["files"], *book["covers"].values(), *book.get("dirs", [])]
    dirty = git("status", "--porcelain", "--", *paths, cwd=folder)
    return head, pinned, bool(dirty)


def count_statuses(manifest):
    counts = {}
    for ch in manifest["chapters"]:
        counts[ch["status"]] = counts.get(ch["status"], 0) + 1
    return counts


def state_line(book, manifest, lang):
    S = STRINGS[lang]
    if not book["publish"]:
        return S["state_none"]
    counts = count_statuses(manifest)
    n = sum(counts.values())
    words = S["status_word"]
    if len(counts) == 1:
        (only,) = counts
        return S["state_all"].format(n=n, status=words.get(only, only))
    parts = ", ".join(f"{c} {words.get(s, s)}" for s, c in sorted(counts.items()))
    return S["state_mixed"].format(n=n, parts=parts)


def e(s):
    return html.escape(s, quote=True)


def render_book(book, manifest, lang):
    S = STRINGS[lang]
    base = "" if lang == "en" else "../"
    slug = book["slug"]
    title = book["title"][lang] or book["title"]["en"]
    sub = book["subtitle"].get(lang)
    sub_lang = ""
    if not sub:
        sub, sub_lang = book["subtitle"]["en"], ' lang="en"'
    out = ['<article class="book">']
    if book["publish"]:
        w, h = book["cover_size"]["width"], book["cover_size"]["height"]
        out.append(f'  <img src="{base}books/{slug}/{e(book["covers"][lang])}" width="{w}" height="{h}" loading="lazy" '
                   f'alt="{e(S["cover_alt"].format(title=title))}">')
    out.append('  <div class="text">')
    out.append(f'    <p class="label">{e(book["series"][lang])}</p>')
    out.append(f'    <h2>{e(title)}</h2>')
    out.append(f'    <p class="subtitle"{sub_lang}>{e(sub)}</p>')
    if book.get("tagline"):
        out.append(f'    <p class="tagline">{e(book["tagline"][lang])}</p>')
    out.append(f'    <p class="state">{e(state_line(book, manifest, lang))}</p>')
    if book["publish"]:
        order = ["fr", "en"] if lang == "fr" else ["en", "fr"]
        out.append('    <ul class="links">')
        for l in order:
            lab = S["read_" + l]
            out.append(f'      <li><a href="{base}books/{slug}/{l}/" hreflang="{l}" lang="{l}">{e(lab)}</a></li>')
        for f in book["files"]:
            if f in S["notes"]:
                out.append(f'      <li><a href="{base}books/{slug}/{f}">{e(f)}</a><span class="note">: {e(S["notes"][f])}</span></li>')
        out.append('    </ul>')
        out.append(f'    <p class="label">{e(S["built"].format(date=full_date(manifest["built"], lang)))}</p>')
    out.append('  </div>')
    out.append('</article>')
    return "\n".join(out)


def render_index(reg, manifests, lang, template):
    S = STRINGS[lang]
    house = reg["house"]
    base = "" if lang == "en" else "../"
    ordered = sorted(reg["books"], key=lambda b: (not b["publish"], reg["books"].index(b)))
    books_html = "\n".join(render_book(b, manifests.get(b["slug"]), lang) for b in ordered)
    if lang == "en":
        switch = '<span aria-current="page">English</span> · <a href="fr/" hreflang="fr" lang="fr">Français</a>'
    else:
        switch = '<a href="../" hreflang="en" lang="en">English</a> · <span aria-current="page">Français</span>'
    links = [f'      <li><a href="{base}llms.txt">llms.txt</a></li>', f'      <li><a href="{base}house.json">house.json</a></li>']
    return Template(template).substitute(
        lang=lang,
        page_title=e(S["page_title"]),
        description=e(S["description"]),
        href_en=house["address"],
        href_fr=urljoin(house["address"], "fr/"),
        href_llms=urljoin(house["address"], "llms.txt"),
        mark=e(house["mark"]),
        line=e(house["line"][lang]),
        lead=e(S["lead"]),
        lang_label=e(S["lang_label"]),
        lang_switch=switch,
        books_html=books_html,
        agents_h=e(S["agents_h"]),
        agents_p=S["agents_p"],
        agents_links="\n".join(links),
        footer=e(S["footer"]),
    )


def render_llms(reg, manifests, states):
    house = reg["house"]
    addr = house["address"]
    lines = [f"# {house['line']['en']}", "",
             "> The books of Mansour Ayouni, published as readers for people and as data for AI agents. "
             f"In French: {house['line']['fr']}.", "",
             f"{house['mark']} is the house mark; {house['line']['en']} is its books imprint.", ""]
    for b in reg["books"]:
        if not b["publish"]:
            continue
        m = manifests[b["slug"]]
        counts = count_statuses(m)
        n = sum(counts.values())
        base = urljoin(addr, f"books/{b['slug']}/")
        lines += [f"## {m['title']}: {m['subtitle']}", "",
                  f"{n} pages; by status: " + ", ".join(f"{c} {s}" for s, c in sorted(counts.items())) +
                  ". A draft page says so in its banner; the banner is part of the page.", "",
                  f"- [Reader, English]({base}en/)",
                  f"- [Lecteur, français]({base}fr/)",
                  f"- [book.json]({base}book.json): the whole book as data; book.schema.json describes it",
                  f"- [llms-book.txt]({base}llms-book.txt): a summary for AI agents",
                  f"- [llms-full-book.txt]({base}llms-full-book.txt): every page as text",
                  f"- Per page: {base}agents/<slug>.md (the slugs are in book.json)", ""]
    lines += ["## House", "", f"- [house.json]({urljoin(addr, 'house.json')}): the exact URLs and the commit each book was built from", ""]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Assemble the AYOUNI house site.")
    ap.add_argument("--out", default="site", help="output folder inside this repository (default: site)")
    args = ap.parse_args()
    out = (ROOT / args.out).resolve()
    if ROOT.resolve() not in out.parents:
        die(f"--out must be inside {ROOT}")
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    template = TEMPLATE.read_text(encoding="utf-8")

    if out.exists():
        for child in out.iterdir():
            shutil.rmtree(child) if child.is_dir() else child.unlink()
    out.mkdir(parents=True, exist_ok=True)

    report, manifests, states, warnings = {}, {}, {}, []
    for book in reg["books"]:
        if not book["publish"]:
            manifests[book["slug"]] = None
            continue
        manifest, published = publish_book(book, out, report)
        manifests[book["slug"]] = manifest
        for field, key in (("title", "title"), ("subtitle", "subtitle"), ("tagline", "tagline"), ("series", "series")):
            if book[key]["en"] != manifest[field]:
                warnings.append(f"{book['slug']}: registry {key} differs from the manifest's; the manifest is right ({manifest[field]!r})")
                book[key]["en"] = manifest[field]
        head, pinned, dirty = book_state(book)
        states[book["slug"]] = {"commit": head, "pinned": pinned, "dirty": dirty, "published": published}
        if dirty:
            warnings.append(f"{book['slug']}: published files differ from the book's last commit; GitHub Actions will build from the pinned commit instead")
        if pinned and head and pinned != head:
            warnings.append(f"{book['slug']}: HEAD {head[:7]} is not the commit the house pins ({pinned[:7]})")

    (out / "index.html").write_text(render_index(reg, manifests, "en", template), encoding="utf-8")
    (out / "fr").mkdir(exist_ok=True)
    (out / "fr" / "index.html").write_text(render_index(reg, manifests, "fr", template), encoding="utf-8")
    (out / "llms.txt").write_text(render_llms(reg, manifests, states), encoding="utf-8")
    (out / ".nojekyll").write_text("", encoding="utf-8")

    addr = reg["house"]["address"]
    books_out = []
    for book in reg["books"]:
        m = manifests[book["slug"]]
        entry = {"slug": book["slug"], "title": book["title"]["en"], "subtitle": book["subtitle"]["en"],
                 "author": book["author"], "series": book["series"]["en"], "published": book["publish"]}
        if book["publish"]:
            base = urljoin(addr, f"books/{book['slug']}/")
            counts = count_statuses(m)
            entry.update({
                "pages": sum(counts.values()), "pages_by_status": counts, "built": m["built"],
                "commit": states[book["slug"]]["commit"], "pinned": states[book["slug"]]["pinned"],
                "readers": {l: base + p.rsplit("index.html", 1)[0] for l, p in book["readers"].items()},
                "manifest": base + book["manifest"],
                "files": {f: base + f for f in book["files"]},
                "per_page": base + "agents/<slug>.md",
                "covers": {l: base + p for l, p in book["covers"].items()},
                "sha256": {p.relative_to(out).as_posix(): h for p, h in sorted(report.items())
                           if p.relative_to(out).parts[:2] == ("books", book["slug"])},
            })
        books_out.append(entry)
    house_json = {"schema": "ayouni-house-site/1", "built": stamp_now(), "address": addr,
                  "house_commit": git("rev-parse", "HEAD", cwd=ROOT), "books": books_out}
    (out / "house.json").write_text(json.dumps(house_json, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    n_files = sum(1 for p in out.rglob("*") if p.is_file())
    print(f"build_site: {n_files} files in {out}")
    for w in warnings:
        print("  warning: " + w)


if __name__ == "__main__":
    main()
