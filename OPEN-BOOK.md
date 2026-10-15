# The open book: what every book session applies

The author ruled on 2026-10-15 how AYOUNI Press offers its books, and revised it the same day (house decisions HOUSE-11 and HOUSE-12 in
`DECISIONS.md`, which keep his words and the reasons). This file is what the house gives each book session so that every book says the same
thing in the same words. A book session never writes a different invitation, never names an amount, a payment service or an address the author
has not given, and never gates anything.

## The ruling, in six lines

1. Every book is **free to read in every form** the house publishes: web reader, PDF, ePub, and the book as data for AI agents. Nothing is
   gated: no address, no login, no payment, anywhere.
2. **There is no payment** in the books or on the site: no ask, no button, no "pay what it was worth", no bank details, no payment service.
3. What is **sold is the work around the books, to organisations**: paper copies in quantity, workshops and training, talks and conference
   invitations, consulting and the building of solutions on the books' subjects. Amounts are discussed case by case; payment follows ordinary banking.
4. **One standing invitation** in the author's voice stands where the ask stood: at the end of each reader after its last chapter, on the last
   page of each PDF, once on the house's home page (HOUSE-14: not repeated on each book card) and on the offer page.
5. The text is **CC BY-NC-ND 4.0** (which also keeps the paper edition the author's); code follows the licence of the library it runs against;
   illustrations and covers follow the book's `LICENSE.md`.
6. The **print icon of a reader opens the book's PDF**, published beside the reader; never a page the browser generates.

## The values

| What | EN | FR |
|---|---|---|
| The offer page | <https://mayouni.github.io/ayouni/offer/> | <https://mayouni.github.io/ayouni/fr/offre/> |
| The licence page | <https://mayouni.github.io/ayouni/licence/> | <https://mayouni.github.io/ayouni/fr/licence/> |
| **The invitation** (word for word) | If this book is useful to your organisation, I work with organisations on its subjects: paper copies in quantity, workshops and training, talks, consulting and the building of solutions. Write to kalidianow@gmail.com. | Si ce livre est utile à votre organisation, je travaille avec les organisations sur ses sujets : exemplaires papier en quantité, ateliers et formations, conférences, conseil et réalisation de solutions. Écrivez à kalidianow@gmail.com. |
| **The colophon line** | Free to read and share under CC BY-NC-ND 4.0; code under the library's licence. | Libre à lire et à partager sous CC BY-NC-ND 4.0 ; le code sous la licence de la bibliothèque. |

- **The address** is the author's current one, until he makes a dedicated one; where a link is possible it is a `mailto:` link. When he changes it,
  the house changes `site-src/books.json` (`house.contact`) and tells each book session; the sentence does not change.
- **Two forms of the same sentence** (HOUSE-15). Inside a book, at the end of the reader and on the PDF's last page, it speaks of that book: "If this
  book is useful to your organisation, ..." (French: "Si ce livre est utile à votre organisation, ..."). On the house's own pages (the home page and the
  offer page), which speak of all the books, it reads "If one of these books is useful to your organisation, I work with organisations on its subjects:
  paper copies in quantity, workshops and training, talks, consulting and the building of solutions. Write to kalidianow@gmail.com." (French: "Si l'un de
  ces livres est utile à votre organisation, je travaille avec les organisations sur ses sujets : exemplaires papier en quantité, ateliers et formations,
  conférences, conseil et réalisation de solutions. Écrivez à kalidianow@gmail.com."). The rest of each sentence is the same, word for word.
- **The logo and the way home** (HOUSE-15). The AYOUNI logo is the SVG at `site-src/assets/ayouni-logo.svg` (served at
  <https://mayouni.github.io/ayouni/assets/ayouni-logo.svg>, traced from the author's logo file; the gradient is part of the file). Wherever a reader
  or a PDF shows the AYOUNI mark, it shows that logo, inlined in a reader so the reader stays one self-contained file. In every reader the logo is also a
  link back to the AYOUNI Press home page, <https://mayouni.github.io/ayouni/>, at the top of the page; a reader must never be a dead end.
- **Readable at 100% zoom** (HOUSE-15). A reader's body text is at least 20px on a desktop screen at 100% zoom and set in a face that stays legible at that
  size (a Garamond reads small: size it up); no label under 14px; the contrast of body text is at least that of the house pages (#17140f on #fbf8f3).
  The author's test: place the page next to a book page from a publisher's site at 100% zoom; ours must be as easy to read.
- **Where it goes in a book**: the invitation and the colophon line at the end of the reader (after the last chapter, not in the hero) and on the
  PDF's last page, in each language of the edition. No amounts, no service names, no form unless the author asks for one.
- **The PDF**: served at `/books/<slug>/book.pdf`, or one per language (`book.en.pdf`, `book.fr.pdf`) as the registry `site-src/books.json` names
  them under `downloads`, each with the author's decision that allows it. A large PDF is not committed: the registry pins a release asset by sha256.
  From a reader at `/books/<slug>/<lang>/` the relative link is `../book.pdf`.
- **`LICENSE.md`**: `templates/LICENSE.md` is the shape; the Refinement book's own file is the reference.
- **The paper edition**: `PAPER.md`. **No ePub online** unless the author asks.

## What a book session does (in its book, then tells the house desk the commit)

- The **print icon** opens the PDF at the path the desk serves, per language.
- The **invitation** and the **colophon line**, word for word, in the reader and on the PDF's last page.
- **`LICENSE.md`** at the root, from the template; the book states its illustrations' licence.
- The **PDFs** built from the pinned commit, handed to the desk with size and sha256.
- Record it in the book's `DECISIONS.md` (the ruling quoted, the date), commit by explicit paths, never push without the desk's word and the
  author's go.

## What the house has done

The offer page ("How these books are offered, and how to work with the author") and the licence page, in both languages; the standing invitation
once on the home page, which shows the book covers large and says what the books share once (HOUSE-14), and on the offer page; the colophon line in every footer; the PDFs in the registry and the gate (`tools/check_public.py`
allows only the PDFs the registry lists, checks each is the book's own file or the pinned release asset, that the reader's print icon opens it,
and that the invitation and the colophon line are on the pages word for word, with no ask left); `PAPER.md`; `templates/LICENSE.md`; this file.
