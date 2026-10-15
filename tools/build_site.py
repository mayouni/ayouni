#!/usr/bin/env python3
"""build_site — assemble the AYOUNI house site from the books the house pins.

    python tools/build_site.py                 # writes site/ (ignored by git; GitHub Actions rebuilds it)
    python tools/build_site.py --out other     # elsewhere inside this repository

What it does, from site-src/books.json:
  * copies each published book's readers, manifest, agents' files, covers and registered downloads, byte for byte (no page is
    rewritten, so every draft banner survives); a PDF or ePub is copied only when the registry lists it under `downloads` with the
    decision that allows it: from the book's folder (`from`), or from a release asset (`url`) whose sha256 and size the registry pins, so
    a large PDF is never committed; any other file type the house does not publish stops the build;
  * writes the index of the books, the offer page and the licence page, in English and French, from site-src/layout.tmpl.html and
    site-src/pages/, reading titles, counts, editions and stamps from each book's own manifest, never composing them;
  * writes llms.txt and house.json (the exact URLs, the commit each book was built from, the sha256 of what was copied);
  * writes .nojekyll.
It changes nothing in a book. Then run:  python tools/check_public.py site
"""
import argparse, hashlib, html, json, posixpath, re, shutil, struct, subprocess, sys, urllib.request
from datetime import datetime
from pathlib import Path
from string import Template
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "site-src" / "books.json"
LAYOUT = ROOT / "site-src" / "layout.tmpl.html"
PAGES_DIR = ROOT / "site-src" / "pages"
PUBLISHABLE = {".html", ".json", ".txt", ".md", ".png", ".svg", ".css", ".js", ".woff2", ".jpg", ".webp"}
DOWNLOAD_SUFFIXES = {".pdf", ".epub"}
MONTHS = {
    "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    "fr": ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"],
}

# Where each page of the house lives, by language.
PAGES = {
    "index": {"en": "index.html", "fr": "fr/index.html"},
    "offer": {"en": "offer/index.html", "fr": "fr/offre/index.html"},
    "licence": {"en": "licence/index.html", "fr": "fr/licence/index.html"},
}

# The manifest's `edition` field, said in each language. The French is the book's own press edition's word for it.
EDITIONS = {
    "proof copy": {"en": "Proof copy", "fr": "Épreuve de travail"},
    "read by the author": {"en": "Read by the author", "fr": "Lu par l'auteur"},
}

STRINGS = {
    "en": {
        "page_title": "AYOUNI Press",
        "description": "The books of Mansour Ayouni, published by AYOUNI Press as readers for people and as data for AI agents.",
        "lead": "The books of Mansour Ayouni: readers for people, data for AI agents.",
        "lang_label": "Language",
        "nav_label": "The house",
        "nav": {"index": "Books", "offer": "Working with the author", "licence": "Licence"},
        "cover_alt": "Cover of {title}",
        "state_all": "{n} pages, all in {status}. Every page carries its draft banner.",
        "state_mixed": "{n} pages: {parts}.",
        "state_none": "Its reader is not on this address yet.",
        "status_word": {"draft": "draft", "read": "read"},
        "built": "Built {date}.",
        "read_en": "Read in English",
        "read_fr": "Lire en français",
        "langs": {"en": "English", "fr": "French"},
        "notes": {
            "book.json": "the whole book as data",
            "llms-book.txt": "a summary for AI agents",
            "llms-full-book.txt": "every page as text",
            "pdf": "the book as a PDF, to read or print",
            "epub": "the book as an ePub",
        },
        "invite": ("If one of these books is useful to your organisation, I work with organisations on its subjects: paper copies in quantity, "
                   "workshops and training, talks, consulting and the building of solutions. Write to {email}."),
        "work_h": "Working with the author",
        "work_more": "How these books are offered",
        "agents_h": "For AI agents",
        "agents_p": ("Each published book is also data, at the same address as its readers: a manifest, a summary, the full text, "
                     "and one file per page (agents/&lt;slug&gt;.md). llms.txt lists them; house.json gives the exact URLs and "
                     "the commit each book was built from."),
        "footer": "AYOUNI Press is the books imprint of AYOUNI.",
        "colophon": "Free to read and share under CC BY-NC-ND 4.0; code under the library's licence.",
        "pages": {
            "offer": {"title": "How these books are offered, and how to work with the author",
                      "lead": "Every AYOUNI book is free to read, in every form. There is no payment. What is sold is the work around the books.",
                      "description": "How AYOUNI Press offers its books: free to read in every form, no payment; organisations can work with the author on the books' subjects."},
            "licence": {"title": "Licence", "lead": "One licence shape for every AYOUNI book.",
                        "description": "The licence of the AYOUNI books: the text under CC BY-NC-ND 4.0, the code under the library's licence, illustrations as each book says."},
        },
    },
    "fr": {
        "page_title": "Éditions AYOUNI",
        "description": "Les livres de Mansour Ayouni, publiés par Éditions AYOUNI comme lecteurs pour les personnes et comme données pour les agents d'IA.",
        "lead": "Les livres de Mansour Ayouni : des lecteurs pour les personnes, des données pour les agents d'IA.",
        "lang_label": "Langue",
        "nav_label": "La maison",
        "nav": {"index": "Les livres", "offer": "Travailler avec l'auteur", "licence": "Licence"},
        "cover_alt": "Couverture de {title}",
        "state_all": "{n} pages, toutes en {status}. Chaque page porte son bandeau de brouillon.",
        "state_mixed": "{n} pages : {parts}.",
        "state_none": "Son lecteur n'est pas encore à cette adresse.",
        "status_word": {"draft": "brouillon", "read": "lue"},
        "built": "Construit le {date}.",
        "read_en": "Read in English",
        "read_fr": "Lire en français",
        "langs": {"en": "anglais", "fr": "français"},
        "notes": {
            "book.json": "le livre entier en données",
            "llms-book.txt": "un résumé pour les agents d'IA",
            "llms-full-book.txt": "chaque page en texte",
            "pdf": "le livre en PDF, à lire ou à imprimer",
            "epub": "le livre en ePub",
        },
        "invite": ("Si l'un de ces livres est utile à votre organisation, je travaille avec les organisations sur ses sujets : exemplaires papier en quantité, "
                   "ateliers et formations, conférences, conseil et réalisation de solutions. Écrivez à {email}."),
        "work_h": "Travailler avec l'auteur",
        "work_more": "Comment ces livres sont offerts",
        "agents_h": "Pour les agents d'IA",
        "agents_p": ("Chaque livre publié est aussi une donnée, à la même adresse que ses lecteurs : un manifeste, un résumé, le texte intégral "
                     "et un fichier par page (agents/&lt;slug&gt;.md). llms.txt les liste ; house.json donne les adresses exactes et "
                     "le commit d'où chaque livre a été construit."),
        "footer": "Éditions AYOUNI est la ligne de livres de la maison AYOUNI.",
        "colophon": "Libre à lire et à partager sous CC BY-NC-ND 4.0 ; le code sous la licence de la bibliothèque.",
        "pages": {
            "offer": {"title": "Comment ces livres sont offerts, et comment travailler avec l'auteur",
                      "lead": "Chaque livre AYOUNI est libre à lire, sous toutes ses formes. Il n'y a aucun paiement. Ce qui est vendu, c'est le travail autour des livres.",
                      "description": "Comment Éditions AYOUNI offre ses livres : libres à lire sous toutes leurs formes, sans paiement ; les organisations peuvent travailler avec l'auteur sur les sujets des livres."},
            "licence": {"title": "Licence", "lead": "Un seul modèle de licence pour chaque livre AYOUNI.",
                        "description": "La licence des livres AYOUNI : le texte sous CC BY-NC-ND 4.0, le code sous la licence de la bibliothèque, les illustrations comme le dit chaque livre."},
        },
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


def e(s):
    return html.escape(s, quote=True)


def href_to(src, dst):
    """The relative URL from the page at path `src` to the file at path `dst` (both inside the site)."""
    sdir = posixpath.dirname(src) or "."
    ddir = posixpath.dirname(dst) or "."
    rel = posixpath.relpath(ddir, sdir)
    rel = "" if rel == "." else rel + "/"
    name = posixpath.basename(dst)
    out = rel + ("" if name == "index.html" else name)
    return out or "./"


def copy_file(src, dst, report, allow_download=False):
    if src.suffix.lower() not in PUBLISHABLE and not allow_download:
        die(f"{src} is a type the house does not publish ({src.suffix}); no PDF or ePub goes online unless the registry lists it under `downloads`")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    report[dst] = sha256(dst)


def source_files(book):
    """The files of a book's folder that the house publishes one by one (its directories are added apart)."""
    rels = [*([book["entry"]] if book.get("entry") else []), *book["readers"].values(), *book.get("files", []),
            *book.get("extra_files", []), *book.get("covers", {}).values()]
    return list(dict.fromkeys(rels))


def published_path(book, rel):
    """Where a source file is served inside /books/<slug>/: its own path, unless the registry's `map` moves it."""
    return book.get("map", {}).get(rel, rel)


def publish_book(book, out, report):
    folder = ROOT / book["folder"]
    dest = out / "books" / book["slug"]
    manifest = None
    if book.get("manifest"):
        manifest_path = folder / book["manifest"]
        if not manifest_path.is_file():
            die(f"{manifest_path} is missing (is the submodule checked out?)")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    published = []
    for rel in source_files(book):
        src = folder / rel
        if not src.is_file():
            die(f"{src} is missing")
        copy_file(src, dest / published_path(book, rel), report)
        published.append(published_path(book, rel))
    for d in book.get("dirs", []):
        for src in sorted((folder / d).rglob("*")):
            if src.is_file():
                rel = src.relative_to(folder).as_posix()
                copy_file(src, dest / rel, report)
                published.append(rel)
    for d in book.get("downloads", []):
        suffix = Path(d["to"]).suffix.lower()
        if suffix not in DOWNLOAD_SUFFIXES or d.get("kind") != suffix.lstrip("."):
            die(f"{d['to']}: a download is a .pdf or .epub whose registry `kind` says so")
        if not d.get("authority"):
            die(f"{d['to']}: a download needs its `authority`, the decision of the author that allows it")
        src = folder / d["from"] if d.get("from") else fetch_download(d, folder)
        if not src.is_file():
            die(f"{src} is missing")
        if suffix == ".pdf" and src.read_bytes()[:5] != b"%PDF-":
            die(f"{src} is not a PDF")
        copy_file(src, dest / d["to"], report, allow_download=True)
        published.append(d["to"])
    return manifest, published


def fetch_download(d, folder):
    """A download that lives outside the repository (a release asset of the book's repository): the registry pins its sha256 and size,
    so what is served is exactly what the author's decision named, whoever hosts it. Found, in order, at `local` (a build on this machine,
    used when its hash matches), in the cache, or fetched from `url`."""
    want, size = d["sha256"], d["bytes"]
    local = folder / d["local"] if d.get("local") else None
    if local and local.is_file() and sha256(local) == want:
        return local
    cache = ROOT / ".cache" / "downloads" / f"{want}{Path(d['to']).suffix.lower()}"
    if cache.is_file() and sha256(cache) == want:
        return cache
    cache.parent.mkdir(parents=True, exist_ok=True)
    print(f"build_site: fetching {d['url']}")
    try:
        with urllib.request.urlopen(urllib.request.Request(d["url"], headers={"User-Agent": "ayouni-build-site"}), timeout=120) as r, open(cache, "wb") as f:
            shutil.copyfileobj(r, f)
    except OSError as ex:
        die(f"cannot fetch {d['url']}: {ex}")
    if cache.stat().st_size != size or sha256(cache) != want:
        found = f"{cache.stat().st_size} bytes, sha256 {sha256(cache)}"
        cache.unlink()
        die(f"{d['url']} is not the file the registry pins ({size} bytes, sha256 {want}); found {found}")
    return cache


def book_state(book):
    """The commit a published book is at, the commit the house pins, and whether the files we publish differ from the commit."""
    folder = ROOT / book["folder"]
    head = git("rev-parse", "HEAD", cwd=folder)
    pinned = None
    tree = git("ls-tree", "HEAD", book["folder"], cwd=ROOT)
    if tree:
        m = re.match(r"160000 commit ([0-9a-f]{40})\t", tree)
        pinned = m.group(1) if m else None
    paths = [*source_files(book), *book.get("dirs", []), *[d["from"] for d in book.get("downloads", []) if d.get("from")]]
    dirty = git("status", "--porcelain", "--", *paths, cwd=folder)
    return head, pinned, bool(dirty)


def png_width_height(path):
    """A PNG's size, read from its header, so the index never composes a cover's proportions."""
    with open(path, "rb") as f:
        head = f.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        die(f"{path} is not a PNG")
    return struct.unpack(">II", head[16:24])


def count_statuses(manifest):
    counts = {}
    for ch in manifest["chapters"]:
        counts[ch["status"]] = counts.get(ch["status"], 0) + 1
    return counts


def state_line(book, manifest, lang):
    S = STRINGS[lang]
    if not book["publish"]:
        return S["state_none"]
    if manifest is None:
        return book["state"][lang]
    counts = count_statuses(manifest)
    n = sum(counts.values())
    words = S["status_word"]
    if len(counts) == 1:
        (only,) = counts
        line = S["state_all"].format(n=n, status=words.get(only, only))
    else:
        parts = ", ".join(f"{c} {words.get(s, s)}" for s, c in sorted(counts.items()))
        line = S["state_mixed"].format(n=n, parts=parts)
    edition = manifest.get("edition")
    if edition:
        if edition not in EDITIONS:
            die(f"the manifest names an edition the house does not know: {edition!r}")
        line = f"{EDITIONS[edition][lang]}. {line}"
    return line


def invite_text(contact, lang):
    """The standing invitation, in the author's words, as plain text (the gate compares the pages with it)."""
    return STRINGS[lang]["invite"].format(email=contact["email"])


def invite_html(contact, lang):
    """The same sentence with the author's address as a mailto link."""
    before, after = STRINGS[lang]["invite"].split("{email}")
    return f'{e(before)}<a href="mailto:{e(contact["email"])}">{e(contact["email"])}</a>{e(after)}'


THUMBS_DIR = ROOT / "site-src" / "assets" / "thumbs"
THUMBS_JSON = ROOT / "site-src" / "assets" / "thumbs.json"
THUMBS_USED, THUMBS_STALE = set(), set()


def thumb_for(book, lang, cover_rel):
    """The home page's small cover for a book, while it was made from exactly the cover being published (tools/make_thumbs.py)."""
    if not THUMBS_JSON.is_file():
        return None
    name = f"{book['slug']}.{lang}.jpg"
    info = json.loads(THUMBS_JSON.read_text(encoding="utf-8")).get(name)
    if info and (THUMBS_DIR / name).is_file() and info["sha256"] == sha256(ROOT / book["folder"] / cover_rel):
        THUMBS_USED.add(name)
        return {"name": name, "width": info["width"], "height": info["height"]}
    THUMBS_STALE.add(name)
    return None


def render_book(book, manifest, lang):
    """One book on the home page: its cover first and large, as the way into the reader; then what it is; then the ways to read it.
    What every book shares (the invitation, the data files, the licence) is said once, below the books."""
    S = STRINGS[lang]
    base = "" if lang == "en" else "../"
    slug = book["slug"]
    title = book["title"][lang] or book["title"]["en"]
    sub = book["subtitle"].get(lang)
    sub_lang = ""
    if not sub:
        sub, sub_lang = book["subtitle"]["en"], ' lang="en"'
    order = [l for l in (["fr", "en"] if lang == "fr" else ["en", "fr"]) if l in book["readers"]]
    out = ['<article class="book">']
    covers = book.get("covers", {})
    if book["publish"] and covers:
        cover = covers.get(lang) or covers["en"]
        cover_lang = lang if lang in covers else "en"
        thumb = thumb_for(book, cover_lang, cover)
        if thumb:
            src, (w, h) = f'{base}assets/thumbs/{thumb["name"]}', (thumb["width"], thumb["height"])
        else:
            pw, ph = png_width_height(ROOT / book["folder"] / cover)
            src, (w, h) = f'{base}books/{slug}/{e(published_path(book, cover))}', (340, round(340 * ph / pw))
        out.append(f'  <a class="cover" href="{base}books/{slug}/{order[0]}/" hreflang="{order[0]}">'
                   f'<img src="{src}" width="{w}" height="{h}" decoding="async" '
                   f'alt="{e(S["cover_alt"].format(title=title))}"></a>')
    out.append('  <div class="text">')
    out.append(f'    <p class="label">{e(book["series"][lang])}</p>')
    out.append(f'    <h2>{e(title)}</h2>')
    out.append(f'    <p class="subtitle"{sub_lang}>{e(sub)}</p>')
    if book.get("tagline"):
        out.append(f'    <p class="tagline">{e(book["tagline"][lang])}</p>')
    out.append(f'    <p class="state">{e(state_line(book, manifest, lang))}</p>')
    if book["publish"]:
        out.append('    <ul class="links inline">')
        for l in order:
            out.append(f'      <li><a href="{base}books/{slug}/{l}/" hreflang="{l}" lang="{l}">{e(S["read_" + l])}</a></li>')
        downloads = book.get("downloads", [])
        for d in downloads:
            label = d["kind"].upper() if len(downloads) == 1 else f'{d["kind"].upper()} ({S["langs"][d["lang"]]})'
            out.append(f'      <li><a href="{base}books/{slug}/{e(d["to"])}" hreflang="{d["lang"]}">{e(label)}</a></li>')
        out.append('    </ul>')
        if manifest:
            out.append(f'    <p class="label">{e(S["built"].format(date=full_date(manifest["built"], lang)))}</p>')
    out.append('  </div>')
    out.append('</article>')
    return "\n".join(out)


def render_work(contact, lang):
    """The standing invitation, once, for every book (HOUSE-14)."""
    S = STRINGS[lang]
    page = PAGES["index"][lang]
    return "\n".join([
        '<section class="work">', '  <div class="text">', f'    <h2>{e(S["work_h"])}</h2>',
        f'    <p class="invite">{invite_html(contact, lang)}</p>',
        f'    <p><a href="{href_to(page, PAGES["offer"][lang])}">{e(S["work_more"])}</a></p>', '  </div>', '</section>'])


def render_agents(reg, lang):
    """The data of every published book, once: what it is in one paragraph, then the files of each book."""
    S = STRINGS[lang]
    base = "" if lang == "en" else "../"
    items = [f'      <li><a href="{base}llms.txt">llms.txt</a>, <a href="{base}house.json">house.json</a></li>']
    for b in reg["books"]:
        files = [f for f in b.get("files", []) if f in S["notes"]]
        if b["publish"] and files:
            title = b["title"][lang] or b["title"]["en"]
            links = ", ".join(f'<a href="{base}books/{b["slug"]}/{f}">{e(f)}</a>' for f in files)
            items.append(f'      <li>{e(title)}: {links}</li>')
    return "\n".join([
        '<section class="agents">', '  <div class="text">', f'    <h2>{e(S["agents_h"])}</h2>', f'    <p>{S["agents_p"]}</p>',
        '    <ul class="links">', *items, '    </ul>', '  </div>', '</section>'])


LOGO = ROOT / "site-src" / "assets" / "ayouni-logo.svg"
LOGO_PATH = "assets/ayouni-logo.svg"


def logo_tag(page, height):
    """The AYOUNI logo, as its SVG (traced from the author's logo), wherever the mark appears; the width follows the viewBox."""
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', LOGO.read_text(encoding="utf-8")).group(1).split()]
    return f'<img class="logo" src="{href_to(page, LOGO_PATH)}" alt="AYOUNI" width="{round(height * vb[2] / vb[3])}" height="{height}">'


def render_page(reg, lang, key, main, layout):
    """One page of the house in one language, inside the shared layout."""
    S = STRINGS[lang]
    house = reg["house"]
    page = PAGES[key][lang]
    other = "fr" if lang == "en" else "en"
    link = lambda k: href_to(page, PAGES[k][lang])
    nav = " ".join((f'<span aria-current="page">{e(S["nav"][k])}</span>' if k == key else f'<a href="{link(k)}">{e(S["nav"][k])}</a>')
                   for k in PAGES)
    here = f'<span aria-current="page">{"English" if lang == "en" else "Français"}</span>'
    there = f'<a href="{href_to(page, PAGES[key][other])}" hreflang="{other}" lang="{other}">{"Français" if lang == "en" else "English"}</a>'
    switch = f"{here} · {there}" if lang == "en" else f"{there} · {here}"
    meta = S if key == "index" else S["pages"][key]
    absolute = lambda l: urljoin(house["address"], PAGES[key][l].rsplit("index.html", 1)[0])
    return Template(layout).substitute(
        lang=lang,
        page_title=e(S["page_title"] if key == "index" else f'{S["pages"][key]["title"]} · {S["page_title"]}'),
        description=e(meta["description"]),
        href_en=absolute("en"),
        href_fr=absolute("fr"),
        href_llms=urljoin(house["address"], "llms.txt"),
        brand="" if key == "index" else (
            f'<p class="brand"><a href="{href_to(page, PAGES["index"][lang])}" aria-label="{e(house["line"][lang])}">{logo_tag(page, 36)}</a></p>'),
        h1=(e(house["line"][lang]).replace(house["mark"], logo_tag(page, 56)) if key == "index" else e(S["pages"][key]["title"])),
        lead=e(S["lead"] if key == "index" else S["pages"][key]["lead"]),
        nav_label=e(S["nav_label"]),
        site_nav=nav,
        lang_label=e(S["lang_label"]),
        lang_switch=switch,
        body_class="home" if key == "index" else "page",
        main=main,
        footer=e(S["footer"]),
        colophon=e(S["colophon"]),
    )


def render_llms(reg, manifests, states):
    house = reg["house"]
    addr = house["address"]
    lines = [f"# {house['line']['en']}", "",
             "> The books of Mansour Ayouni, published as readers for people and as data for AI agents. "
             f"In French: {house['line']['fr']}.", "",
             f"{house['mark']} is the house mark; {house['line']['en']} is its books imprint. "
             "Every book is free to read in every form; nothing is gated and there is no payment. Organisations can work with the author on the "
             "books' subjects: see the offer page.", ""]
    for b in reg["books"]:
        if not b["publish"]:
            continue
        m = manifests[b["slug"]]
        base = urljoin(addr, f"books/{b['slug']}/")
        pdfs = [f"- [{d['kind'].upper()}, {d['lang']}]({base}{d['to']})" for d in b.get("downloads", [])]
        if m is None:
            lines += [f"## {b['title']['en']}: {b['subtitle']['en']}", "", b["state"]["en"], "",
                      f"- [Reader, English]({base}en/)", *pdfs, ""]
            continue
        counts = count_statuses(m)
        n = sum(counts.values())
        lines += [f"## {m['title']}: {m['subtitle']}", "",
                  (f"Edition: {m['edition']}. " if m.get("edition") else "") +
                  f"{n} pages; by status: " + ", ".join(f"{c} {s}" for s, c in sorted(counts.items())) +
                  ". A draft page says so in its banner; the banner is part of the page.", "",
                  f"- [Reader, English]({base}en/)",
                  f"- [Lecteur, français]({base}fr/)",
                  *pdfs,
                  f"- [book.json]({base}book.json): the whole book as data; book.schema.json describes it",
                  f"- [llms-book.txt]({base}llms-book.txt): a summary for AI agents",
                  f"- [llms-full-book.txt]({base}llms-full-book.txt): every page as text",
                  f"- Per page: {base}agents/<slug>.md (the slugs are in book.json)", ""]
    lines += ["## House", "",
              f"- [How these books are offered, and how to work with the author]({urljoin(addr, PAGES['offer']['en'].rsplit('index.html', 1)[0])})",
              f"- [Licence]({urljoin(addr, PAGES['licence']['en'].rsplit('index.html', 1)[0])}): the text under CC BY-NC-ND 4.0",
              f"- [house.json]({urljoin(addr, 'house.json')}): the exact URLs and the commit each book was built from", ""]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Assemble the AYOUNI house site.")
    ap.add_argument("--out", default="site", help="output folder inside this repository (default: site)")
    args = ap.parse_args()
    out = (ROOT / args.out).resolve()
    if ROOT.resolve() not in out.parents:
        die(f"--out must be inside {ROOT}")
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    layout = LAYOUT.read_text(encoding="utf-8")

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
            if manifest and book[key]["en"] != manifest[field]:
                warnings.append(f"{book['slug']}: registry {key} differs from the manifest's; the manifest is right ({manifest[field]!r})")
                book[key]["en"] = manifest[field]
        head, pinned, dirty = book_state(book)
        states[book["slug"]] = {"commit": head, "pinned": pinned, "dirty": dirty, "published": published}
        if dirty:
            warnings.append(f"{book['slug']}: published files differ from the book's last commit; GitHub Actions will build from the pinned commit instead")
        if pinned and head and pinned != head:
            warnings.append(f"{book['slug']}: HEAD {head[:7]} is not the commit the house pins ({pinned[:7]})")

    ordered = sorted(reg["books"], key=lambda b: (not b["publish"], reg["books"].index(b)))
    for lang in ("en", "fr"):
        books_html = "\n".join(render_book(b, manifests.get(b["slug"]), lang) for b in ordered)
        index_main = ('<div class="books">\n' + books_html + '\n</div>\n' + render_work(reg["house"]["contact"], lang) + "\n"
                      + render_agents(reg, lang))
        target = out / PAGES["index"][lang]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_page(reg, lang, "index", index_main, layout), encoding="utf-8")
        for key in ("offer", "licence"):
            page = PAGES[key][lang]
            fragment = (PAGES_DIR / f"{key}.{lang}.html").read_text(encoding="utf-8")
            main_html = Template(fragment).safe_substitute(
                home=href_to(page, PAGES["index"][lang]), offer=href_to(page, PAGES["offer"][lang]),
                licence=href_to(page, PAGES["licence"][lang]), invite=invite_html(reg["house"]["contact"], lang))
            target = out / page
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(render_page(reg, lang, key, main_html, layout), encoding="utf-8")
    (out / "llms.txt").write_text(render_llms(reg, manifests, states), encoding="utf-8")
    (out / ".nojekyll").write_text("", encoding="utf-8")
    (out / LOGO_PATH).parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(LOGO, out / LOGO_PATH)
    for name in sorted(THUMBS_USED):
        (out / "assets" / "thumbs").mkdir(parents=True, exist_ok=True)
        shutil.copyfile(THUMBS_DIR / name, out / "assets" / "thumbs" / name)
    for name in sorted(THUMBS_STALE - THUMBS_USED):
        warnings.append(f"the thumbnail {name} is not made from the cover being published; the full cover is used (run tools/make_thumbs.py)")

    addr = reg["house"]["address"]
    books_out = []
    for book in reg["books"]:
        m = manifests[book["slug"]]
        entry = {"slug": book["slug"], "title": book["title"]["en"], "subtitle": book["subtitle"]["en"],
                 "author": book["author"], "series": book["series"]["en"], "published": book["publish"]}
        if book["publish"]:
            base = urljoin(addr, f"books/{book['slug']}/")
            entry.update({
                "commit": states[book["slug"]]["commit"], "pinned": states[book["slug"]]["pinned"],
                "readers": {l: base + published_path(book, p).rsplit("index.html", 1)[0] for l, p in book["readers"].items()},
                "sha256": {p.relative_to(out).as_posix(): h for p, h in sorted(report.items())
                           if p.relative_to(out).parts[:2] == ("books", book["slug"])},
            })
            if m:
                counts = count_statuses(m)
                entry.update({"pages": sum(counts.values()), "pages_by_status": counts, "edition": m.get("edition"), "built": m["built"],
                              "manifest": base + book["manifest"], "per_page": base + "agents/<slug>.md"})
            else:
                entry["state"] = book["state"]["en"]
            if book.get("files"):
                entry["files"] = {f: base + f for f in book["files"]}
            if book.get("covers"):
                entry["covers"] = {l: base + published_path(book, p) for l, p in book["covers"].items()}
            if book.get("downloads"):
                entry["downloads"] = [{"kind": d["kind"], "lang": d["lang"], "url": base + d["to"], "authority": d["authority"],
                                       "hosted_at": d.get("url") or "the repository",
                                       "bytes": (out / "books" / book["slug"] / d["to"]).stat().st_size,
                                       "sha256": report[out / "books" / book["slug"] / d["to"]]} for d in book["downloads"]]
        books_out.append(entry)
    house_json = {"schema": "ayouni-house-site/2", "built": stamp_now(), "address": addr,
                  "house_commit": git("rev-parse", "HEAD", cwd=ROOT),
                  "pages": {k: {l: urljoin(addr, p.rsplit("index.html", 1)[0]) for l, p in v.items()} for k, v in PAGES.items()},
                  "books": books_out}
    (out / "house.json").write_text(json.dumps(house_json, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    n_files = sum(1 for p in out.rglob("*") if p.is_file())
    print(f"build_site: {n_files} files in {out}")
    for w in warnings:
        print("  warning: " + w)


if __name__ == "__main__":
    main()
