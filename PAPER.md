# Paper editions: how an AYOUNI book becomes paper

Status: **proposal from the house desk, 2026-10-15.** The author chooses the print-on-demand service and the trim sizes; nothing is ordered,
no service is signed up to, no price is set. This file says what the records already hold, what the desk proposes, and what each book must
hand over, so that every book session prepares its press files to one specification.

## The rule (the author's, HOUSE-11)

Every AYOUNI book is free to read in every form. What is sold is what cannot be copied: the paper edition and the author's time.

- **The paper edition** is industry-grade, printed on demand, and priced at **cost plus a fair margin**.
- **The supporter's edition** is numbered and signed, and carries the supporter's name in the colophon of the next printing. A name is printed
  only with the supporter's consent.

## What the records hold today

| | *Refinement-Oriented Programming* | *Softanza* |
|---|---|---|
| Service planned | IngramSpark, print on demand (its publishing plan) | none named |
| Trim | 6 x 9 in, perfect-bound paperback (its publishing plan); the PDF is built at exactly 6 x 9 in | 6.5 x 8.5 in, the cover's own proportion, full bleed (the book's PRINT-01) |
| Pages | 106 (PDF of 2026-07-18) | 606 English, 623 French (proof copy PDFs, per the book session) |
| ISBN | pending | none recorded |
| Cover art | `web/cover.png`, 1097 x 1434 px | `assets/cover/cover.png`, 1097 x 1434 px |

## The desk's proposal (for the author to choose)

1. **Service: IngramSpark**, because the author's own publishing plan already names it: worldwide wholesale distribution, no inventory,
   one master file per edition. Another service is possible; the specification below does not depend on the choice.
2. **Trim: as each book already is** (Refinement 6 x 9 in; Softanza 6.5 x 8.5 in), unless the author wants one house trim.
3. **Price rule:** price = the service's printing cost per copy at the book's page count, plus the retailer discount the channel requires,
   plus a margin the author sets. The house publishes the rule, never an amount the author has not given.
4. **Supporter's edition:** printed in small numbered runs and signed by the author; the number is on the page that carries the colophon.

## What a book hands over (to verify with the chosen service before any order)

- **Interior PDF** at the trim size, fonts embedded, no crop marks: the book's existing press PDF is the starting point.
- **Cover PDF**: front, spine and back in one file, with bleed. The spine width depends on the page count and the paper; the service's
  calculator gives it. The back cover carries the ISBN and its barcode.
- **Cover artwork at print resolution.** The usual requirement is 300 dpi at trim plus bleed. Both current covers are 1097 x 1434 px, which is
  about 160 to 185 dpi at their trims: **a higher-resolution source is needed before paper.** This is a finding, not a decision.
- **One ISBN per edition** (paper, and any other form that has its own), assigned by the author through the national agency.
- **A proof copy** ordered and read by the author before the book is listed.

## Order of work

1. The author picks the service and the trims. 2. The book session prepares the files to this file's specification (`release.py` lists
them). 3. A proof copy is ordered. 4. The author reads it and approves. 5. The book is listed; its card on the house site says so.

## Not decided

The service, the trims, the prices, the ISBNs, the supporter's edition's size and price, and when. The consulting address is on the offer
page as "to come".
