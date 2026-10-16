#!/usr/bin/env python3
"""check_public — the gates before anything of the house goes online.

    python tools/check_public.py site [--site site] [--online]     # the built site (run tools/build_site.py first)
    python tools/check_public.py tree [repo ...]                    # the tracked files of each repository (default: the house)
    python tools/check_public.py history repo [repo ...] [--deny-file F]   # every blob of every commit, before a first push

site:    no PDF or ePub except those the registry lists under `downloads` (each allowed by a decision of the author, byte for byte the
         book's own, and the reader's print icon opens it); every reader is the book's file byte for byte; every page keeps its stage banner (Draft, In review or Published); the house's own copy
         agrees with the book's reader; the index pages follow one type scale; no emoji or forbidden word in the house's own text;
         every internal link resolves (the readers' links to the Softanza website are checked as /stzsite/..., which is where
         they land at /books/<slug>/<lang>/). --online asks the live addresses (HEAD) and reports what does not answer.
tree:    no PDF, ePub, Word or archive file tracked; nothing of books/ring-book/ but its README, CLAUDE.md and style/; no file over 50 MB.
history: a first push publishes every commit, so this reads every blob ever committed: secrets (a hit fails), this machine's paths,
         the commit authors' emails, large files, forbidden file types, and the words of --deny-file (one per line).

Exit 1 when a gate fails. Warnings are for the author to read; --strict makes them fail too.
"""
import argparse, hashlib, html, json, posixpath, re, subprocess, sys, threading
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_site import EDITIONS, PAGES, STRINGS, invite_text  # the words the index uses; where each page lives; the author's invitation

FORBIDDEN_SUFFIXES = {".pdf", ".epub", ".mobi", ".docx", ".doc", ".pptx", ".xlsx", ".zip", ".7z", ".exe", ".dll"}
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF\U0000FE0F\U0000200D]")
HOUSE_WORDS = {
    r"\bsubstrate\b": "substrate",
    r"(?<!decision-)\bmakers?\b": "maker (say crafter; decision-maker is the one exception)",
    r"\b(revolutionary|game[- ]changing|paradigm shift)\b": "hype word",
    r"\b(leverage|utilize|best practices?|stakeholders)\b": "jargon word",
    r"\bweak\b|\bfalls? short\b|\bnothing runs\b": "undersells the work (AWF-08)",
}
SECRETS = {
    "github token": r"\bgh[pousr]_[A-Za-z0-9]{36}\b",
    "github fine-grained token": r"\bgithub_pat_[A-Za-z0-9_]{50,}\b",
    "aws access key": r"\bAKIA[0-9A-Z]{16}\b",
    "private key": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    "api key (sk-)": r"\bsk-[A-Za-z0-9_-]{32,}\b",
    "slack token": r"\bxox[abprs]-[A-Za-z0-9-]{20,}\b",
    "assigned secret": r"(?i)\b(api[_-]?key|secret|token|passwd|password)\b\s*[:=]\s*[\"'][^\"'\s]{12,}[\"']",
}
LOCAL_PATH = re.compile(r"\b[A-Za-z]:[\\/](?:Users|MyDocs|GitHub)[\\/][^\s\"'<>`)]{0,40}|/home/[a-z][\w-]*/[^\s\"'<>`)]{0,30}")
STZSITE_PREFIX = "/stzsite/"


def registered_downloads():
    """Repository paths of the PDFs and ePubs the registry lists, each allowed by a decision of the author."""
    reg = json.loads((ROOT / "site-src" / "books.json").read_text(encoding="utf-8"))
    return {f"{b['folder']}/{d['from']}" for b in reg["books"] if b["publish"] for d in b.get("downloads", []) if d.get("from")}


def allowed_downloads(repo):
    """The PDFs and ePubs a repository may track: the house's own registered downloads; and, in a book's repository (found by its folder's name,
    books/refinement-book -> refinement-book), the files the registry lists for that book, by their path inside it."""
    if repo == ROOT.resolve():
        return registered_downloads()
    reg = json.loads((ROOT / "site-src" / "books.json").read_text(encoding="utf-8"))
    return {d["from"] for b in reg["books"] if b["publish"] and Path(b["folder"]).name == repo.name for d in b.get("downloads", []) if d.get("from")}


class Report:
    def __init__(self, strict):
        self.strict, self.fails, self.warns = strict, 0, 0

    def ok(self, msg):
        print("  ok    " + msg)

    def fail(self, msg):
        self.fails += 1
        print("  FAIL  " + msg)

    def warn(self, msg):
        self.warns += 1
        print("  warn  " + msg)

    def code(self):
        print(f"\n{self.fails} failed, {self.warns} warnings")
        return 1 if self.fails or (self.strict and self.warns) else 0


def git(*args, cwd, binary=False):
    r = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout if binary else r.stdout.decode("utf-8", errors="replace")


# ---------------------------------------------------------------- site

def css_blocks(css):
    return re.findall(r"\{([^{}]*)\}", css)


def check_type_scale(rep, name, text):
    css = "\n".join(re.findall(r"<style>(.*?)</style>", text, re.S))
    order = ["house", "book", "subtitle", "body", "label"]
    sets = 0
    for block in css_blocks(css):
        toks = dict(re.findall(r"--t-([a-z]+):\s*([\d.]+)px", block))
        if not toks:
            continue
        sets += 1
        vals = [float(toks[k]) for k in order if k in toks]
        if len(vals) == len(order) and all(vals[i] > vals[i + 1] for i in range(len(vals) - 1)):
            if float(toks["label"]) >= 12:
                continue
        rep.fail(f"{name}: the type scale breaks its order or goes under 12px: {toks}")
        return
    raw = [d for d in re.findall(r"font(?:-size)?:\s*([^;}]*)", css) if re.search(r"(?<![\w.-])\d+(?:\.\d+)?(?:px|em|rem|pt)\b", d)]
    if raw:
        rep.fail(f"{name}: a component takes a size of its own (use the --t-* scale): {raw[:3]}")
    elif sets:
        rep.ok(f"{name}: one type scale ({sets} set(s)), house > book > subtitle > body > label, labels at 12px or more")
    else:
        rep.fail(f"{name}: no --t-* type scale found")


def resolve(site, page_rel, ref, address_path):
    """Resolve a reference found in a page, in URL space (the site lives under address_path on the host)."""
    ref = ref.split("#")[0].split("?")[0]
    if not ref:
        return None
    base_dir = posixpath.dirname(address_path + page_rel)
    return posixpath.normpath(posixpath.join(base_dir, ref)) + ("/" if ref.endswith("/") else "")


def page_refs(text):
    refs = re.findall(r"""(?:src|href)=["']([^"']*)["']""", text) + re.findall(r"""url\(\s*["']?([^)"']+)""", text)
    return [r for r in refs if r and not r.startswith(("data:", "#", "http:", "https:", "mailto:", "url(", "javascript:"))]


def check_links(rep, site, reg, address_path, page_rel, known, stz_targets, label):
    text = (site / page_rel).read_text(encoding="utf-8", errors="replace")
    broken, gaps, stz_missing, outside = [], [], [], 0
    sibling = ROOT.parent / "stzsite"
    seen = set()
    for ref in page_refs(text):
        url = resolve(site, page_rel, ref, address_path)
        if url is None or url in seen:
            continue
        seen.add(url)
        if url.startswith(address_path):
            rel = url[len(address_path):]
            target = site / rel
            if rel.endswith("/") or target.is_dir():
                target = target / "index.html"
            if target.is_file():
                continue
            gap = next((k for k in known if rel.split("/", 2)[-1].startswith(k["ref"]) or rel.endswith(k["ref"])), None)
            (gaps if gap else broken).append(rel)
        elif url.startswith(STZSITE_PREFIX):
            stz_targets.add(url)
            if sibling.is_dir() and not (sibling / url[len(STZSITE_PREFIX):]).is_file():
                stz_missing.append(url)
        else:
            outside += 1
    if broken:
        rep.fail(f"{label}: {len(broken)} internal link(s) do not resolve: {broken[:4]}")
    else:
        rep.ok(f"{label}: internal links resolve ({len(seen)} distinct)")
    if gaps:
        rep.warn(f"{label}: {len(gaps)} known gap(s) in the book's own output (site-src/books.json): {sorted(set(gaps))[:4]}")
    if stz_missing:
        rep.fail(f"{label}: links to the Softanza website that its checkout does not have: {stz_missing[:4]}")
    if outside:
        rep.warn(f"{label}: {outside} link(s) land outside the site and the Softanza website")


# HOUSE-18: a page has one of three stages, its banner says which, and only the author moves a page beyond Draft.
STAGES = ("draft", "review", "published")
STAGE_WORDS = {"en": {"draft": "Draft", "review": "In review", "published": "Published"},
               "fr": {"draft": "Brouillon", "review": "En relecture", "published": "Publié"}}


def check_site(args):
    rep = Report(args.strict)
    site = (ROOT / args.site).resolve()
    reg = json.loads((ROOT / "site-src" / "books.json").read_text(encoding="utf-8"))
    address_path = urlparse(reg["house"]["address"]).path
    if not (site / "house.json").is_file():
        print(f"check_public: {site} has no house.json; run python tools/build_site.py first", file=sys.stderr)
        return 2
    manifest_of = json.loads((site / "house.json").read_text(encoding="utf-8"))
    print(f"site {site}")

    allowed = {f"books/{b['slug']}/{d['to']}" for b in reg["books"] if b["publish"] for d in b.get("downloads", [])}
    bad = [p.relative_to(site).as_posix() for p in site.rglob("*")
           if p.suffix.lower() in FORBIDDEN_SUFFIXES and p.relative_to(site).as_posix() not in allowed]
    (rep.fail(f"files the house does not publish: {bad[:5]}") if bad
     else rep.ok(f"no PDF, ePub, Word or archive file beyond the {len(allowed)} download(s) the registry lists"))
    for need in ("index.html", "fr/index.html", "llms.txt", "house.json", ".nojekyll"):
        if not (site / need).is_file():
            rep.fail(f"missing {need}")

    stz_targets = set()
    for book in reg["books"]:
        if not book["publish"]:
            continue
        slug, folder = book["slug"], ROOT / book["folder"]
        entry = next(b for b in manifest_of["books"] if b["slug"] == slug)
        print(f"\n{slug}")
        dest = site / "books" / slug
        drift = []
        source_of = {v: k for k, v in book.get("map", {}).items()}  # published path inside the book's folder -> its source path
        for rel, digest in entry["sha256"].items():
            published = site / rel
            inside = rel.split("/", 2)[2]
            source = folder / source_of.get(inside, inside)
            if not published.is_file():
                rep.fail(f"{rel} is in house.json and not in the site")
            elif source.is_file() and published.read_bytes() != source.read_bytes():
                drift.append(rel)
        (rep.warn(f"{len(drift)} file(s) differ from the checkout (rebuild): {drift[:3]}") if drift
         else rep.ok(f"{len(entry['sha256'])} published files are the book's own, byte for byte"))

        mf = json.loads((dest / book["manifest"]).read_text(encoding="utf-8")) if book.get("manifest") else None
        stages = Counter(c["status"] for c in mf["chapters"]) if mf else Counter()
        if mf:
            summary = ", ".join(f"{n} {s}" for s, n in stages.items())
            retired = sorted(s for s in stages if s not in STAGES + ("missing",))
            if retired:
                rep.warn(f"{slug}: the manifest uses retired stage values {retired}; the stages are draft, review and published (HOUSE-18)")
            moved = book.get("moved_by_author", {})
            unrecorded = [f"{c['id']} ({c['status']})" for c in mf["chapters"]
                          if c["status"] not in ("draft", "missing") and moved.get(c["id"], {}).get("stage") != c["status"]]
            if unrecorded:
                rep.fail(f"{slug}: {len(unrecorded)} page(s) beyond Draft that the house has no record of the author moving (moved_by_author): {unrecorded[:4]}")
            else:
                beyond = sum(n for s, n in stages.items() if s not in ("draft", "missing"))
                rep.ok(f"{slug}: page stages ({summary})" + (f"; the {beyond} beyond Draft are recorded as moved by the author" if beyond else ""))
            every = bool(mf["chapters"]) and all(c["status"] == "published" for c in mf["chapters"])
            if mf.get("edition") == "published" and not every:
                rep.fail(f"{slug}: the edition says published and not every page is ({summary})")
            elif mf.get("edition") == "proof copy" and every:
                rep.warn(f"{slug}: every page is published and the edition still says proof copy")
        if mf and mf.get("edition"):
            names = EDITIONS.get(mf["edition"])
            index = {"en": (site / "index.html").read_text(encoding="utf-8"), "fr": (site / "fr" / "index.html").read_text(encoding="utf-8")}
            if not names:
                rep.fail(f"the manifest names an edition the house does not know: {mf['edition']!r}")
            else:
                (rep.ok(f"the index pages name the edition: {names}") if all(names[l] in index[l] for l in index)
                 else rep.fail(f"the manifest says {mf['edition']!r} and an index page does not"))
        for d in book.get("downloads", []):
            served, source = dest / d["to"], (folder / d["from"] if d.get("from") else None)
            where = f"books/{slug}/{d['to']}"
            if not served.is_file():
                rep.fail(f"{where}: registered download is not in the site")
                continue
            data = served.read_bytes()
            if d["kind"] == "pdf" and data[:5] != b"%PDF-":
                rep.fail(f"{where}: not a PDF")
            elif d.get("sha256") and (hashlib.sha256(data).hexdigest() != d["sha256"] or len(data) != d["bytes"]):
                rep.fail(f"{where}: is not the file the registry pins ({d['bytes']} bytes, sha256 {d['sha256'][:12]}...)")
            elif source is not None and source.is_file() and data != source.read_bytes():
                rep.warn(f"{where}: differs from the checkout (rebuild)")
            else:
                how = "pinned by sha256 in the registry" if d.get("sha256") else "the book's own file"
                rep.ok(f"{where}: the book's {d['kind'].upper()}, {len(data) >> 10} KB, {how}, allowed by {d['authority']}")
            names = [lang for lang, src in book["readers"].items()
                     if f"../{d['to']}" in (dest / book.get("map", {}).get(src, src)).read_text(encoding="utf-8", errors="replace")]
            (rep.ok(f"the reader's print button opens it ({d['lang']}: ../{d['to']})") if names
             else rep.warn(f"no reader of {slug} opens {where}: the print icon should open the published PDF"))
        for fonts in sorted({p.parent for p in dest.rglob("*.woff2")}):
            (rep.ok(f"{fonts.relative_to(site).as_posix()}: every font family ships with its OFL licence") if list(fonts.glob("OFL*.txt"))
             else rep.fail(f"{fonts.relative_to(site).as_posix()}: font files without an OFL licence text beside them"))
        for lang, source_rel in book["readers"].items():
            rel = book.get("map", {}).get(source_rel, source_rel)
            text = (dest / rel).read_text(encoding="utf-8", errors="replace")
            norm = lambda s: re.sub(r"[\W_]+", " ", s.casefold()).strip()
            desc = norm(html.unescape((re.search(r'<meta name="description" content="([^"]*)"', text) or [None, ""])[1]))
            if re.search(r"(?i)pay what it was worth|payez ce que le livre|payez ce qu'il", text):
                rep.warn(f"{lang} reader of {slug} still carries the retired ask (HOUSE-12); the book session replaces it with the invitation")
            if mf:
                seen = {s: text.count(f'class="status-banner st-{s}"') for s in STAGES}
                off = {s: (seen[s], stages[s]) for s in STAGES if seen[s] != stages[s]}
                (rep.ok(f"{lang} reader: stage banners agree with the manifest ({', '.join(f'{seen[s]} {s}' for s in STAGES if seen[s])})") if not off
                 else rep.fail(f"{lang} reader: banners and manifest disagree, as (banners, pages) per stage: {off}"))
                labels = [(m.group(1), html.unescape(m.group(2)).strip())
                          for m in re.finditer(r'class="status-banner st-(draft|review|published)"[^>]*>([^<]*)<', text)]
                wrong = sorted({(s, w) for s, w in labels if not w.startswith(STAGE_WORDS[lang][s])})
                (rep.fail(f"{lang} reader: a banner does not say its stage in the house's words: {wrong[:3]}") if wrong
                 else rep.ok(f"{lang} reader: every banner says its stage in the house's words ({', '.join(STAGE_WORDS[lang].values())})"))
                keys = ("subtitle", "tagline", "series")
            else:
                keys = ("subtitle",)  # a book without a manifest: the house's own copy is checked against what the reader says of itself
            for key in keys:
                want = norm(book[key][lang] or book[key]["en"])
                (rep.ok(f"{lang} reader agrees with the house's {key}") if want in desc
                 else rep.fail(f"{lang} reader's description does not contain the house's {key}: {book[key][lang]!r}"))
            hosts = Counter(urlparse(u).netloc + "/" + (urlparse(u).path.split("/")[1] if urlparse(u).path.count("/") > 1 else "")
                            for u in re.findall(r"(?:src|href)=[\"'](https?://[^\"']+)", text))
            foreign = {h: n for h, n in hosts.items() if not h.startswith(("github.com/mayouni", "mayouni.github.io/ayouni"))}
            (rep.warn(f"{lang} reader calls other hosts: {foreign}") if foreign
             else rep.ok(f"{lang} reader links only github.com/mayouni and the house ({sum(hosts.values())} links)"))
            check_links(rep, site, reg, address_path, f"books/{slug}/{rel}", book.get("known_gaps", []), stz_targets, f"{lang} reader")

    print("\nthe house's own pages")
    own_prefixes = (reg["house"]["address"], "https://github.com/mayouni/", "https://creativecommons.org/")
    for rel in [p for langs in PAGES.values() for p in langs.values()]:
        text = (site / rel).read_text(encoding="utf-8")
        check_type_scale(rep, rel, text)
        prose = re.sub(r"<style>.*?</style>", "", text, flags=re.S)
        hits = [m for m in EMOJI.findall(prose)]
        words = [label for pat, label in HOUSE_WORDS.items() if re.search(pat, re.sub(r"<[^>]+>", " ", prose), re.I)]
        (rep.fail(f"{rel}: emoji in a reader-visible page") if hits else rep.ok(f"{rel}: no emoji"))
        (rep.fail(f"{rel}: forbidden words: {words}") if words else rep.ok(f"{rel}: no forbidden word"))
        is_home = rel in (PAGES["index"]["en"], PAGES["index"]["fr"])
        logo_ok = 'class="logo"' in prose and (site / "assets" / "ayouni-logo.svg").is_file() and \
            (site / "assets" / "ayouni-logo.svg").read_text(encoding="utf-8").lstrip().startswith("<svg")
        (rep.ok(f"{rel}: the AYOUNI logo is its SVG") if logo_ok else rep.fail(f"{rel}: the AYOUNI logo (assets/ayouni-logo.svg) is not on the page"))
        if not is_home:
            home = re.search(r'<p class="brand"><a href="([^"]*)"', prose)
            target = resolve(site, rel, home.group(1), address_path) if home else None
            (rep.ok(f"{rel}: the logo links back to the home page") if target and target.rstrip("/") in
             {address_path.rstrip("/") + "/" + PAGES["index"][l].rsplit("index.html", 1)[0].rstrip("/") for l in ("en", "fr")}
                 | {address_path.rstrip("/")} else rep.fail(f"{rel}: the logo must link back to the home page (found {target})"))
        # a request is a resource the page loads; a link is a place the reader may go
        loads = re.findall(r"""<(?:img|script|iframe|source|video|audio)[^>]*\ssrc=["'](https?://[^"']+)""", prose) + \
            re.findall(r"""<link[^>]*\shref=["'](https?://[^"']+)""", prose)
        loads = [u for u in loads if not u.startswith(reg["house"]["address"])]
        (rep.fail(f"{rel}: loads from other hosts: {loads[:3]}") if loads else rep.ok(f"{rel}: no third-party request"))
        links = [u for u in re.findall(r"""<a[^>]*\shref=["'](https?://[^"']+)""", prose) if not u.startswith(own_prefixes)]
        (rep.fail(f"{rel}: links to hosts the house has not named: {links[:3]}") if links else rep.ok(f"{rel}: external links only to the house, github.com/mayouni and creativecommons.org"))
        check_links(rep, site, reg, address_path, rel, [], stz_targets, rel)
    for key, label in (("offer", "the offer page"), ("licence", "the licence page")):
        for lang in ("en", "fr"):
            text = (site / PAGES[key][lang]).read_text(encoding="utf-8")
            if key == "licence":
                (rep.ok(f"{lang} {label} states CC BY-NC-ND 4.0") if "CC BY-NC-ND 4.0" in text else rep.fail(f"{lang} {label} does not state CC BY-NC-ND 4.0"))
            else:
                gate = re.findall(r"(?i)<(form|input|script|dialog|iframe)\b", text)
                (rep.ok(f"{lang} {label}: no form, script, dialog or frame: nothing can gate or nag") if not gate
                 else rep.fail(f"{lang} {label}: {sorted(set(gate))} on a page that must never gate or nag"))
    contact = reg["house"]["contact"]
    plain = lambda s: re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()  # inline tags only: a link inside a sentence
    for lang in ("en", "fr"):
        want = invite_text(contact, lang)
        index = (site / PAGES["index"][lang]).read_text(encoding="utf-8")
        cards = index.count('<article class="book">')
        published = sum(1 for b in reg["books"] if b["publish"])
        (rep.ok(f"{lang} index: {cards} book cards for {published} published books") if cards == published
         else rep.fail(f"{lang} index: {cards} book cards for {published} published books"))
        heavy = []
        for src in re.findall(r'<a class="cover"[^>]*><img src="([^"]+)"', index):
            f = (site / PAGES["index"][lang]).parent / src
            if f.is_file() and f.stat().st_size > 500 << 10:
                heavy.append(f"{src} ({f.stat().st_size >> 10} KB)")
        (rep.warn(f"{lang} index: card covers over 500 KB, run tools/make_thumbs.py after a cover changes: {heavy}") if heavy
         else rep.ok(f"{lang} index: every card cover is light (under 500 KB)"))
        covers = index.count('<a class="cover" ')
        with_cover = sum(1 for b in reg["books"] if b["publish"] and b.get("covers"))
        (rep.ok(f"{lang} index: every book with a cover shows it, linked to its reader ({covers})") if covers == with_cover
         else rep.fail(f"{lang} index: {covers} covers shown for {with_cover} books that have one"))
        invites = [plain(m) for m in re.findall(r'<p class="invite">(.*?)</p>', index, re.S)]
        (rep.ok(f"{lang} index: the standing invitation once, word for word (HOUSE-14)") if invites == [want]
         else rep.fail(f"{lang} index: the invitation must appear exactly once, word for word; found {len(invites)}"))
        offer = (site / PAGES["offer"][lang]).read_text(encoding="utf-8")
        (rep.ok(f"{lang} offer page: the standing invitation, word for word") if want in [plain(m) for m in re.findall(r'<p class="invite">(.*?)</p>', offer, re.S)]
         else rep.fail(f"{lang} offer page does not carry the standing invitation word for word"))
        mail = f'href="mailto:{contact["email"]}"'
        (rep.ok(f"{lang} pages: the author's address is a mailto link") if mail in index and mail in offer
         else rep.fail(f"{lang} index or offer page lacks the mailto link to {contact['email']}"))
        for key in PAGES:
            page = (site / PAGES[key][lang]).read_text(encoding="utf-8")
            footer = plain(re.search(r'<p class="colophon">(.*?)</p>', page, re.S).group(1))
            (rep.ok(f"{lang} {key}: the colophon line, word for word") if footer == STRINGS[lang]["colophon"]
             else rep.fail(f"{lang} {key}: the colophon line differs from the house's"))
    pay = re.compile(r"(?i)pay what it was worth|payez ce que|payez ce qu'il|class=\"(?:ask|button)\"")
    retired = [rel for langs in PAGES.values() for rel in langs.values() if pay.search((site / rel).read_text(encoding="utf-8"))]
    retired += ["llms.txt"] if pay.search((site / "llms.txt").read_text(encoding="utf-8")) else []
    (rep.fail(f"the retired ask (HOUSE-12: there is no payment anywhere) is still on: {retired}") if retired
     else rep.ok("no ask, no button, no 'pay what it was worth' on the house's pages"))
    llms = (site / "llms.txt").read_text(encoding="utf-8")
    (rep.fail("llms.txt: emoji") if EMOJI.search(llms) else rep.ok("llms.txt: no emoji"))

    if args.online:
        import urllib.request
        addr = reg["house"]["address"]
        urls = sorted({"https://mayouni.github.io" + u for u in stz_targets}
                      | {addr + p.rsplit("index.html", 1)[0] for langs in PAGES.values() for p in langs.values()}
                      | {addr + "llms.txt", addr + "house.json"}
                      | {f"{addr}books/{b['slug']}/{d['to']}" for b in reg["books"] if b["publish"] for d in b.get("downloads", [])})
        print(f"\nonline: {len(urls)} addresses")
        for u in urls:
            try:
                req = urllib.request.Request(u, method="HEAD")
                code = urllib.request.urlopen(req, timeout=15).status
            except Exception as ex:
                code = getattr(ex, "code", str(ex))
            (rep.ok(f"{code} {u}") if code == 200 else rep.warn(f"{code} {u}"))
    elif stz_targets:
        print(f"\n  {len(stz_targets)} distinct Softanza-website addresses checked against the local checkout (add --online to ask the live site)")
    return rep.code()


# ---------------------------------------------------------------- tree

def check_tree(args):
    rep = Report(args.strict)
    for repo in [Path(r).resolve() for r in (args.repos or [str(ROOT)])]:
        print(f"tree {repo}")
        out = git("-c", "core.quotepath=false", "ls-files", "-s", cwd=repo)
        if out is None:
            rep.fail(f"{repo} is not a git repository")
            continue
        files = [l.split("\t", 1) for l in out.splitlines()]
        blobs = [(meta.split()[0], p) for meta, p in files]
        allowed = allowed_downloads(repo)
        bad = [p for mode, p in blobs if mode != "160000" and Path(p).suffix.lower() in FORBIDDEN_SUFFIXES and p not in allowed]
        (rep.fail(f"tracked files of a type the house does not publish: {bad[:5]}") if bad
         else rep.ok(f"no PDF, ePub, Word or archive file tracked beyond the {len(allowed)} the registry lists"))
        submods = {p: meta.split()[1] for meta, p in files if meta.split()[0] == "160000"}
        inside = {p: next(m for m in submods if p.startswith(m + "/")) for p in allowed if any(p.startswith(m + "/") for m in submods)}
        missing = [p for p in allowed if p not in inside and p not in {q for _, q in blobs}]
        (rep.fail(f"registered downloads that are not tracked (GitHub Actions would not find them): {missing}") if missing else None)
        # a registered download that lives in a submodule is checked in the commit the house pins
        lacking = [p for p, m in inside.items() if git("cat-file", "-e", f"{submods[m]}:{p[len(m) + 1:]}", cwd=repo / m) is None]
        (rep.fail(f"registered downloads that the pinned submodule commit does not hold: {lacking}") if lacking
         else (rep.ok(f"{len(inside)} registered download(s) held by the pinned submodule commit") if inside else None))
        ring = [p for mode, p in blobs if p.startswith("books/ring-book/") and p not in ("books/ring-book/README.md", "books/ring-book/CLAUDE.md")
                and not p.startswith("books/ring-book/style/")]
        (rep.fail(f"Ring archive files tracked (Apress's property): {ring[:5]}") if ring else rep.ok("nothing of the Ring archive but its README, CLAUDE.md and style/"))
        big = [(p, (repo / p).stat().st_size) for mode, p in blobs if mode != "160000" and (repo / p).is_file() and (repo / p).stat().st_size > 10 << 20]
        for p, size in big:
            (rep.fail if size > 50 << 20 else rep.warn)(f"{p}: {size >> 20} MB")
        if not big:
            rep.ok("no file over 10 MB")
        print(f"  {len(blobs)} entries tracked ({sum(1 for m, _ in blobs if m == '160000')} submodules)")
    return rep.code()


# ---------------------------------------------------------------- history

def blob_stream(repo, shas):
    """Yield (sha, bytes) for each sha through one `git cat-file --batch` process, without holding the history in memory."""
    p = subprocess.Popen(["git", "cat-file", "--batch"], cwd=str(repo), stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def feed():
        for s in shas:
            p.stdin.write((s + "\n").encode())
        p.stdin.close()
    threading.Thread(target=feed, daemon=True).start()
    while True:
        header = p.stdout.readline()
        if not header:
            break
        sha, kind, size = header.decode().split()
        data = p.stdout.read(int(size))
        p.stdout.read(1)
        yield sha, kind, data
    p.wait()


def check_history(args):
    rep = Report(args.strict)
    deny = [w.strip() for w in Path(args.deny_file).read_text(encoding="utf-8").splitlines() if w.strip()] if args.deny_file else []
    for repo in [Path(r).resolve() for r in args.repos]:
        print(f"history {repo}")
        n_commits = git("rev-list", "--all", "--count", cwd=repo)
        if n_commits is None:
            rep.fail(f"{repo} is not a git repository")
            continue
        people = Counter(git("log", "--all", "--format=%an <%ae>%n%cn <%ce>", cwd=repo).split("\n"))
        people.pop("", None)
        rep.warn(f"{n_commits.strip()} commits will publish these name and email pairs: {dict(people)}")

        listing = git("rev-list", "--objects", "--all", cwd=repo).splitlines()
        paths = {}
        for line in listing:
            sha, _, path = line.partition(" ")
            if path:
                paths.setdefault(sha, path)
        sizes = {}
        pr = subprocess.run(["git", "cat-file", "--batch-check"], cwd=str(repo), input=("\n".join(paths) + "\n").encode(), capture_output=True)
        for l in pr.stdout.decode().splitlines():
            parts = l.split()
            if len(parts) == 3 and parts[1] == "blob":
                sizes[parts[0]] = int(parts[2])
        rep.ok(f"{len(sizes)} distinct blobs, {sum(sizes.values()) >> 20} MB before compression")

        for sha, size in sizes.items():
            if size > 25 << 20:
                rep.fail(f"{paths[sha]}: {size >> 20} MB blob in history (GitHub refuses over 100 MB; over 25 MB is unwise)")
            elif size > 10 << 20:
                rep.warn(f"{paths[sha]}: {size >> 20} MB blob in history")
        allowed = allowed_downloads(repo)
        forb = sorted({paths[s] for s in sizes if Path(paths[s]).suffix.lower() in FORBIDDEN_SUFFIXES and paths[s] not in allowed})
        (rep.warn(f"files of a type the house does not publish exist in history (they would be public): {forb[:6]}") if forb
         else rep.ok("no PDF, ePub, Word or archive file ever committed"))

        want = [s for s, size in sizes.items() if size <= 3 << 20 and Path(paths[s]).suffix.lower() not in {".png", ".jpg", ".woff2", ".ico", ".gif", ".webp"}]
        hits = {k: Counter() for k in SECRETS}
        local, denied = Counter(), Counter()
        for sha, kind, data in blob_stream(repo, want):
            if b"\x00" in data[:2048]:
                continue
            text = data.decode("utf-8", errors="ignore")
            for k, pat in SECRETS.items():
                for m in re.finditer(pat, text):
                    hits[k][paths[sha] + "  (" + m.group(0)[:6] + "..., " + str(len(m.group(0))) + " chars)"] += 1
            for m in LOCAL_PATH.finditer(text):
                local[m.group(0)[:60]] += 1
            for w in deny:
                if re.search(r"\b" + re.escape(w) + r"\b", text, re.I):
                    denied[w] += 1
        for k, c in hits.items():
            (rep.fail(f"{k}: {len(c)} place(s), first: {list(c)[:3]}") if c else None)
        if not any(hits.values()):
            rep.ok(f"no secret pattern in {len(want)} text blobs")
        (rep.warn(f"{len(local)} distinct local paths of this machine appear in history, e.g. {[p for p, _ in local.most_common(4)]}") if local
         else rep.ok("no local path of this machine"))
        if deny:
            (rep.warn(f"denied words found (blobs containing each): {dict(denied)}") if denied else rep.ok("none of the denied words"))
    return rep.code()


def main():
    ap = argparse.ArgumentParser(description="Gates before anything of the house goes online.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("site"); s.add_argument("--site", default="site"); s.add_argument("--online", action="store_true")
    t = sub.add_parser("tree"); t.add_argument("repos", nargs="*")
    h = sub.add_parser("history"); h.add_argument("repos", nargs="+"); h.add_argument("--deny-file")
    for p in (s, t, h):
        p.add_argument("--strict", action="store_true")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit({"site": check_site, "tree": check_tree, "history": check_history}[args.cmd](args))


if __name__ == "__main__":
    main()
