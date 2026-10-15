# The open book: what every book session applies

The author ruled on 2026-10-15 how AYOUNI Press offers its books (house decision HOUSE-11 in `DECISIONS.md`, which keeps the argument). This file
is what the house gives each book session so that every book says the same thing in the same words. A book session never writes a different
ask, never names a payment service, an amount or a consulting address the author has not given, and never gates anything.

## The ruling, in five lines

1. Every book is **free to read in every form** the house publishes: web reader, PDF, ePub, and the book as data for AI agents. Nothing is gated.
2. The reader **pays after, if it was useful and if they can**: one sentence, once per form, after the reading, never a condition or a nag.
3. What is **sold** is the paper edition (cost plus a fair margin; a supporter's edition) and the author's time (AYOUNI Consulting).
4. The text is **CC BY-NC-ND 4.0**; code follows the licence of the library it runs against; illustrations and covers follow the book's `LICENSE.md`.
5. The **print icon of a reader opens the book's PDF**, published beside the reader; never a page the browser generates.

## The values

| What | EN | FR |
|---|---|---|
| The offer page | <https://mayouni.github.io/ayouni/offer/> | <https://mayouni.github.io/ayouni/fr/offre/> |
| The licence page | <https://mayouni.github.io/ayouni/licence/> | <https://mayouni.github.io/ayouni/fr/licence/> |
| **The ask** (one sentence, word for word) | If this book was useful to you, and you can, pay what it was worth. | Si ce livre vous a été utile, et si vous le pouvez, payez ce qu'il a valu pour vous. |
| The ask's button | How to pay what it was worth | Comment payer ce qu'il a valu |
| **The colophon line** | Free to read and share under CC BY-NC-ND 4.0; code under the library's licence; pay what it was worth, if it was. | Libre à lire et à partager sous CC BY-NC-ND 4.0 ; le code sous la licence de la bibliothèque ; payez ce que le livre a valu, s'il a valu quelque chose. |

- **The ask's link** is the offer page: the author has named no payment service yet, so the button leads to the page that says the way to pay is
  to come. When he names one, the house changes the link and tells each book session; the sentence does not change.
- **Where the ask goes in a book**: at the end of the reader (after the last chapter, not in the hero) and on the PDF's last page (the colophon), in
  each language of the edition. The colophon line goes in the same places.
- **The PDF**: served at `/books/<slug>/book.pdf`, or one per language (`book.en.pdf`, `book.fr.pdf`) as the registry `site-src/books.json` names
  them under `downloads`, each with the author's decision that allows it. From a reader at `/books/<slug>/<lang>/` the relative link is
  `../book.pdf`. The Refinement book's is live: <https://mayouni.github.io/ayouni/books/refinement/book.pdf>.
- **`LICENSE.md`**: `templates/LICENSE.md` in this repository is the shape; the Refinement book's own file is the reference. The Softanza book
  has none yet.
- **The paper edition**: `PAPER.md` says how a book becomes paper and what it must hand over.
- **No ePub online** unless the author asks; the PDF and the data are the forms today.

## What a book session does (in its book, then tells the house desk the commit)

- The **print icon** opens the PDF at the path the house serves, per language.
- The **ask** and the **colophon line**, word for word, in the reader and on the PDF's last page.
- **`LICENSE.md`** at the root, from the template; the book states its illustrations' licence.
- The **PDFs** built from the pinned commit, handed to the house desk with their size and sha256; `release.py`'s manifest lists them. A PDF of
  several megabytes is not committed on every rebuild: the desk proposes how it is served when the first one is handed over.
- The **press files** follow `PAPER.md` once the author has chosen the service and the trims.
- Record it in the book's `DECISIONS.md` (the ruling quoted, the date), commit by explicit paths, never push without the desk's word and the
  author's go.

## What the house has done (2026-10-15)

The offer page and the licence page, in both languages, linked from every page and from every book card with the ask and its button; the
colophon line in every page's footer; the PDFs in the registry and the gate (`tools/check_public.py` allows only the PDFs the registry lists,
checks each is the book's own file byte for byte, and that the reader's print icon opens it); `PAPER.md`; `templates/LICENSE.md`; this file.
The Refinement PDF is live.
