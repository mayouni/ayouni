#!/usr/bin/env python3
"""make_thumbs — small cover images for the home page's book cards, so the front door stays light (a cover is about 3 MB at print size).

    python tools/make_thumbs.py            # writes site-src/assets/thumbs/<slug>.<lang>.jpg and site-src/assets/thumbs.json

Each thumbnail is made from the cover exactly as the house publishes it: the file of the commit the house pins (a submodule) or of the house's
HEAD (plain files), never from a working tree another session may be editing. thumbs.json records the sha256 of that source, so
tools/build_site.py uses a thumbnail only while its source is still the published cover, and falls back to the full cover otherwise (and says so).
The full cover stays published beside the reader. Needs Pillow; GitHub Actions does not: the thumbnails are committed.
"""
import hashlib, io, json, re, subprocess
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "site-src" / "assets" / "thumbs"
WIDTH = 880  # twice the 440 CSS px a card shows, for a sharp cover on a high-density screen


def blob(book, rel):
    """The bytes of a cover as the house publishes it: from the pinned commit of a submodule, or from the house's HEAD."""
    folder = book["folder"]
    tree = subprocess.run(["git", "ls-tree", "HEAD", folder], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    m = re.match(r"160000 commit ([0-9a-f]{40})\t", tree)
    if m:
        r = subprocess.run(["git", "show", f"{m.group(1)}:{rel}"], cwd=ROOT / folder, capture_output=True)
    else:
        r = subprocess.run(["git", "show", f"HEAD:{folder}/{rel}"], cwd=ROOT, capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"cannot read {folder}/{rel} from git: {r.stderr.decode()[:200]}")
    return r.stdout


def main():
    reg = json.loads((ROOT / "site-src" / "books.json").read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for book in reg["books"]:
        if not book["publish"]:
            continue
        for lang, rel in book.get("covers", {}).items():
            data = blob(book, rel)
            im = Image.open(io.BytesIO(data)).convert("RGB")
            h = round(WIDTH * im.height / im.width)
            im = im.resize((WIDTH, h), Image.LANCZOS)
            name = f"{book['slug']}.{lang}.jpg"
            im.save(OUT / name, "JPEG", quality=86, optimize=True, progressive=True)
            manifest[name] = {"source": f"{book['folder']}/{rel}", "sha256": hashlib.sha256(data).hexdigest(), "width": WIDTH, "height": h}
            print(f"{name}: {WIDTH}x{h}, {(OUT / name).stat().st_size >> 10} KB, from {book['folder']}/{rel} ({len(data) >> 10} KB)")
    (ROOT / "site-src" / "assets" / "thumbs.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
