# AYOUNI — the house

AYOUNI is the house mark. **AYOUNI Press** (French: **Éditions AYOUNI**) is its books line; "imprint" is the common noun the colophons use.
The lines to come (AYOUNI Consulting and others) get their own repositories, never folders here.

Two kinds of session work in this folder:

- **The house session** (the AYOUNI Press desk) owns this root: this file, `DECISIONS.md`, `README.md`, the site (`site-src/`, `tools/`,
  `.github/`), publication, and the common ground the books share. It does not write the books.
- **A book session** owns one book's folder. That book's own `CLAUDE.md` is authoritative for it. Do not mix the books' files; never edit a
  book's text from the house session (send its session a message).

| # | Book | Folder | State |
|---|---|---|---|
| 0 | *Beginning Ring Programming* (Apress, 2020) | `books/ring-book/` | **archive**: the last files and a study of the writing (`style/`); the source of the writing framework. Its own repository; the manuscript files are Apress's property and never go public (HOUSE-06) |
| 1 | *Refinement-Oriented Programming* | `books/refinement-book/` | shipped (web reader + PDF); tracked here as plain files, PDFs excluded; its reader is not on the house address yet |
| 2 | *Softanza — The Governed Software Platform of the AI Age* | `books/softanza-book/` | **active**; its own repository, a submodule of the house; all pages `status: draft` |

Unless the author says otherwise, a book session works in its book's folder; the house session works here at the root.

**The writing framework.** `writing-framework/` is the AYOUNI Writing Framework: how the author writes (from the Ring book study), what agents do and
do not do in an AYOUNI book, the briefs, the checklists and the tools. Every book session reads its `CLAUDE.md` before drafting or revising prose.
It is its own repository, a submodule of the house like the Softanza book. The platform's own repository is not part of the house.

## Publication (the house session's work)

- Address: `https://mayouni.github.io/ayouni/`, repository `mayouni/ayouni`, public. A book is at `/books/<slug>/en/` and `/books/<slug>/fr/`,
  with its covers, `book.json`, `llms-*.txt` and `agents/` under `/books/<slug>/`. Today's slugs: `softanza`.
- A book is a git **submodule**: it keeps its own repository and history; the house pins one commit. A book goes online, or changes online,
  only when a commit of the house moves its pointer.
- `python tools/build_site.py` assembles `site/` (ignored by git) from the pinned books; `python tools/check_public.py site` is the gate
  (no PDF or ePub, every reader the book's own file byte for byte, every draft banner kept, links resolve). GitHub Actions runs both.
  Before a first push: `python tools/check_public.py tree` and `... history <repo>` for each repository.
- **Publishing is the author's, and never done without his explicit "go" in the session**: creating a public repository, pushing to one,
  switching Pages on. Prepare, then ask. The first three acts were done on 2026-10-14 (DECISIONS HOUSE-03): `mayouni/ayouni`,
  `mayouni/softanza-book` and `mayouni/writing-framework` are public and Pages is on, so from now **every push to them publishes at once**:
  ask first, and ask the book session to tell the desk before it pushes.
- No PDF or ePub online unless the author says so. Keep every page's draft banner.

## Rules that bind this session

Commit by explicit paths, never `git add -A` (a hook refuses it). Never set a book page to `status: read`. Never edit a book's text. Never
background a heavy command. A decision is a dated row in `DECISIONS.md` with the author's words quoted.
The author's standing rules: never undersell the work (stage and direction, never "weak" or "falls short"); the language is Haro, and Ring is named
only in the Softanza book's Appendix H; "crafter" is the person, never "maker" (outside "decision-maker"), and the platform is defined by what it does;
"AI model" and "AI agent" where the bare word is ambiguous; text size follows semantic level in anything rendered; no emoji in anything a reader sees.
