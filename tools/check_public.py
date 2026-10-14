#!/usr/bin/env python3
"""check_public — the gates before anything of the house goes online.

    python tools/check_public.py site [--site site] [--online]     # the built site (run tools/build_site.py first)
    python tools/check_public.py tree [repo ...]                    # the tracked files of each repository (default: the house)
    python tools/check_public.py history repo [repo ...] [--deny-file F]   # every blob of every commit, before a first push

site:    no PDF or ePub; every reader is the book's file byte for byte; every draft page keeps its banner; the house's own copy
         agrees with the book's reader; the index pages follow one type scale; no emoji or forbidden word in the house's own text;
         every internal link resolves (the readers' links to the Softanza website are checked as /stzsite/..., which is where
         they land at /books/<slug>/<lang>/). --online asks the live addresses (HEAD) and reports what does not answer.
tree:    no PDF, ePub, Word or archive file tracked; nothing of books/ring-book/ but its README, CLAUDE.md and style/; no file over 50 MB.
history: a first push publishes every commit, so this reads every blob ever committed: secrets (a hit fails), this machine's paths,
         the commit authors' emails, large files, forbidden file types, and the words of --deny-file (one per line).

Exit 1 when a gate fails. Warnings are for the author to read; --strict makes them fail too.
"""
import argparse, html, json, posixpath, re, subprocess, sys, threading
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
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

    bad = [p.relative_to(site).as_posix() for p in site.rglob("*") if p.suffix.lower() in FORBIDDEN_SUFFIXES]
    (rep.fail(f"files the house does not publish: {bad[:5]}") if bad else rep.ok("no PDF, ePub, Word or archive file"))
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
        for rel, digest in entry["sha256"].items():
            published = site / rel
            source = folder / rel.split("/", 2)[2]
            if not published.is_file():
                rep.fail(f"{rel} is in house.json and not in the site")
            elif source.is_file() and published.read_bytes() != source.read_bytes():
                drift.append(rel)
        (rep.warn(f"{len(drift)} file(s) differ from the checkout (rebuild): {drift[:3]}") if drift
         else rep.ok(f"{len(entry['sha256'])} published files are the book's own, byte for byte"))

        mf = json.loads((dest / book["manifest"]).read_text(encoding="utf-8"))
        drafts = sum(1 for c in mf["chapters"] if c["status"] == "draft")
        for lang, rel in book["readers"].items():
            text = (dest / rel).read_text(encoding="utf-8", errors="replace")
            banners = text.count('class="status-banner st-draft"')
            (rep.ok(f"{lang} reader: {banners} draft banners for {drafts} draft pages") if banners == drafts
             else rep.fail(f"{lang} reader: {banners} draft banners for {drafts} draft pages in the manifest"))
            norm = lambda s: re.sub(r"[\W_]+", " ", s.casefold()).strip()
            desc = norm(html.unescape((re.search(r'<meta name="description" content="([^"]*)"', text) or [None, ""])[1]))
            for key in ("subtitle", "tagline", "series"):
                want = norm(book[key][lang])
                (rep.ok(f"{lang} reader agrees with the house's {key}") if want in desc
                 else rep.fail(f"{lang} reader's description does not contain the house's {key}: {book[key][lang]!r}"))
            hosts = Counter(urlparse(u).netloc + "/" + (urlparse(u).path.split("/")[1] if urlparse(u).path.count("/") > 1 else "")
                            for u in re.findall(r"(?:src|href)=[\"'](https?://[^\"']+)", text))
            foreign = {h: n for h, n in hosts.items() if not h.startswith("github.com/mayouni")}
            (rep.warn(f"{lang} reader calls other hosts: {foreign}") if foreign else rep.ok(f"{lang} reader links only github.com/mayouni ({sum(hosts.values())} links)"))
            check_links(rep, site, reg, address_path, f"books/{slug}/{rel}", book.get("known_gaps", []), stz_targets, f"{lang} reader")

    print("\nthe house's own pages")
    for rel in ("index.html", "fr/index.html"):
        text = (site / rel).read_text(encoding="utf-8")
        check_type_scale(rep, rel, text)
        prose = re.sub(r"<style>.*?</style>", "", text, flags=re.S)
        hits = [m for m in EMOJI.findall(prose)]
        words = [label for pat, label in HOUSE_WORDS.items() if re.search(pat, re.sub(r"<[^>]+>", " ", prose), re.I)]
        (rep.fail(f"{rel}: emoji in a reader-visible page") if hits else rep.ok(f"{rel}: no emoji"))
        (rep.fail(f"{rel}: forbidden words: {words}") if words else rep.ok(f"{rel}: no forbidden word"))
        ext = re.findall(r"""(?:src|href)=["'](https?://[^"']+)""", prose)
        own = [u for u in ext if not u.startswith(reg["house"]["address"])]
        (rep.fail(f"{rel}: calls other hosts: {own[:3]}") if own else rep.ok(f"{rel}: no third-party request"))
        check_links(rep, site, reg, address_path, rel, [], stz_targets, rel)
    llms = (site / "llms.txt").read_text(encoding="utf-8")
    (rep.fail("llms.txt: emoji") if EMOJI.search(llms) else rep.ok("llms.txt: no emoji"))

    if args.online:
        import urllib.request
        urls = sorted({"https://mayouni.github.io" + u for u in stz_targets} |
                      {reg["house"]["address"], reg["house"]["address"] + "fr/", reg["house"]["address"] + "llms.txt", reg["house"]["address"] + "house.json"})
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
        bad = [p for mode, p in blobs if mode != "160000" and Path(p).suffix.lower() in FORBIDDEN_SUFFIXES]
        (rep.fail(f"tracked files of a type the house does not publish: {bad[:5]}") if bad else rep.ok("no PDF, ePub, Word or archive file tracked"))
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
        forb = sorted({paths[s] for s in sizes if Path(paths[s]).suffix.lower() in FORBIDDEN_SUFFIXES})
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
