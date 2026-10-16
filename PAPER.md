# Paper editions: how an AYOUNI book becomes paper

Status: **proposal from the house desk, revised 2026-10-15 (HOUSE-12).** The author chooses the printer and the trim sizes; nothing is ordered,
no service is signed up to. This file says what the records already hold, what the desk proposes, and what each book must hand over, so that
every book session prepares its press files to one specification.

## The rule (the author's, HOUSE-11 and HOUSE-12)

Every AYOUNI book is free to read in every form, and there is no payment in the books or on the site. Paper is part of the work the author does
with organisations:

- **Paper copies are supplied to organisations in quantity, on request.** The amount is discussed case by case with each customer, and payment
  follows ordinary banking. There is no price list and no price rule in the house.
- **The licence keeps the paper edition the author's**: the text is CC BY-NC-ND 4.0, so no one else may sell it.
- **A distributor for single copies is for later**, when a structure exists to run one. The model does not need it.

## What the records hold today

| | *Refinement-Oriented Programming* | *Softanza* |
|---|---|---|
| Service planned | IngramSpark, print on demand (its publishing plan, written before HOUSE-12) | none named |
| Trim | 6 x 9 in, perfect-bound paperback (its publishing plan); the PDF is built at exactly 6 x 9 in | 6.5 x 8.5 in, the cover's own proportion, full bleed (the book's PRINT-01) |
| Pages | 107 (PDF rebuilt 2026-10-15, one page more than the 106 of 2026-07-18: the last page before the back cover) | 618 English, 637 French (proof copy PDFs, per the book session) |
| ISBN | pending | none recorded |
| Cover art | `web/cover.png`, 2194 x 2868 px, white background | `assets/cover/cover.png`, 2194 x 2868 px, white background |

## The desk's proposal (for the author to choose)

1. **Printer.** One able to print a run of a few dozen to a few hundred copies for an organisation, on request. IngramSpark, which the
   Refinement book's own plan names, is a candidate because it prints on demand without inventory; a local printer is another. The
   specification below does not depend on the choice.
2. **Trim: as each book already is** (Refinement 6 x 9 in; Softanza 6.5 x 8.5 in), unless the author wants one house trim.
3. **No price in the house.** An order is quoted to the customer by the author, from the printer's cost for that run and the work of the
   engagement it belongs to.

## What a book hands over (to verify with the chosen printer before any order)

- **Interior PDF** at the trim size, fonts embedded, no crop marks: the book's existing press PDF is the starting point.
- **Cover PDF**: front, spine and back in one file, with bleed. The spine width depends on the page count and the paper; the printer's
  calculator gives it. The back cover carries the ISBN and its barcode.
- **Cover artwork at print resolution.** The usual requirement is 300 dpi at trim plus bleed. Both covers are now 2194 x 2868 px: about 340 dpi at
  the 6.5 x 8.5 in trim and 365 dpi at 6 x 9 in, so the front is sharp enough; the bleed (usually 0.125 in on each side) has to be added to the cover
  file, and the spine and back come with the cover PDF. To confirm with the chosen printer.
- **One ISBN per edition**, assigned by the author through the national agency.
- **A proof copy** ordered and read by the author before any customer receives the book.

## Order of work

1. The author picks the printer and the trims. 2. The book session prepares the files to this file's specification (`release.py` lists them).
3. A proof copy is ordered. 4. The author reads it and approves. 5. Copies are supplied to organisations that ask for them.

## Not decided

The printer, the trims, the ISBNs, and when. The consulting and workshop side of the model has no file here: it is the author's work with each
customer.
