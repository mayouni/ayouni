# AYOUNI Press

The books of Mansour Ayouni, as readers for people and as data for AI agents. In French: Éditions AYOUNI.

AYOUNI is the house mark; AYOUNI Press is its books imprint. The site is built from this repository and served at
<https://mayouni.github.io/ayouni/>.

| Folder | What it holds |
|---|---|
| `books/softanza-book/` | *Softanza: The Governed Software Platform of the AI Age* (submodule: its own repository and history). Every page is a draft and says so |
| `books/refinement-book/` | *Refinement-Oriented Programming* |
| `books/ring-book/` | the archive of the author's first book (Apress, 2020); its manuscript files are never public |
| `writing-framework/` | the AYOUNI Writing Framework: the one voice of the books (submodule: its own repository and history) |
| `site-src/`, `tools/`, `.github/` | how the site is assembled and checked |

Clone with the books: `git clone --recurse-submodules https://github.com/mayouni/ayouni.git`.

To build the site on your machine: `python tools/build_site.py`, then `python tools/check_public.py site`. The result is in `site/`.
A reader lives at `/books/<slug>/en/` or `/books/<slug>/fr/`; the same folder carries the book as data: `book.json`, `llms-book.txt`,
`llms-full-book.txt`, and one Markdown file per page under `agents/`.

Every book is free to read in every form; the reader pays after, if it was useful; paper and the author's time are what is sold. How the books
are offered is on the site's offer page and in [OPEN-BOOK.md](OPEN-BOOK.md); the paper edition is in [PAPER.md](PAPER.md); the licence shape is
[templates/LICENSE.md](templates/LICENSE.md).

The decisions of the house, with the author's words, are in [DECISIONS.md](DECISIONS.md).
