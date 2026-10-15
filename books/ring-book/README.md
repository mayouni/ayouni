# Beginning Ring Programming (Apress, 2020) — the archive

Mansour Ayouni's first book, *Beginning Ring Programming: From Novice to Professional*, Apress, 2020 (ISBN 978-1-4842-5832-3),
foreword by Mahmoud Fayed. Nine chapters in three parts, an annex, about 600 pages. Written May 2019 to March 2020 in Sousse; published May 2020.

This folder holds the **last versions** of the author's files, copied on 2026-10-11 from `D:\MyDocs\Ring Book`, and a study of the
author's writing style made from them (`style/`). It is the raw material of the AYOUNI writing framework (`../../writing-framework/`),
which is why it sits beside the AYOUNI books although Apress, not AYOUNI, published it.

## Which file is the last version

The source folder holds three generations. The lineage, by date:

| Generation | Where (in the source folder) | Dates | What it is |
|---|---|---|---|
| Drafts | root: `ring-book-chap-0N*.docx` and the `-bis`, `-flower`, `-hope`, `-jasmin`, `-palm` variants of chapter 3 | June 2019 – January 2020 | the writing; **not copied** (superseded) |
| Masters | `Gold/0N_*.docx`, `Gold/The-Ring-Book.docx` | 27 January – 4 March 2020 | the chapters assembled; the whole book in one file (copied) |
| **Reviewed** | `Gold/Reviewed/ring-book-chap-0N.docx` (+ `-9Things.docx`, `.pptx`, `.pdf`) | **6 February – 5 March 2020** | **the last Word text of each chapter**, as sent to Apress after technical review; with the "Nine things you will learn" list and the figure deck of each chapter |
| Proofs | `Footprint/0N .../485799_1_En_N_Chapter_Author.pdf` | 7 May 2020 | the typeset pages after Apress's copyedit: **the published text** |
| Corrections | `ring-book-corrections.docx` | 27 May 2020 | the author's corrections to the proofs |

So: the author's own last words are `manuscript/reviewed/`; the words readers hold are `proofs/`. The two differ by the copyedit
(`style/copyedit-diff.md` records what the editor changed).

## Layout

| Folder | Contents |
|---|---|
| `manuscript/reviewed/` | the nine chapters, last Word versions (chapter 2 is the `-bis` file, renamed), their PDF exports of 8 March 2020, and the nine `-9Things` lists |
| `manuscript/whole-book/` | `The-Ring-Book.docx` (4 March 2020, the whole book in one file), `00_Content.docx`, `parts.docx` |
| `manuscript/text/` | the same texts extracted to plain Markdown-ish files (`ch01.md` …; code indented four spaces; `proof-ch01/05/09.txt` are the published text of three chapters; `_stats.json` word and sentence counts). **Chapter 9's code was pasted as images in Word, so its text is in `proof-ch09.txt`.** |
| `front-matter/` | foreword (Mahmoud Fayed), introduction, front matter, annex ("A dialogue with Mahmoud Fayed"), cover text, back-cover drafts, author résumé |
| `proofs/` | Apress's typeset proofs, front matter and nine chapters (`_Author.pdf` the pages, `_DeltaPDF.pdf` the changes) |
| `materials/` | the 2019 book story and proposal (`ring-book-story.docx`: a 30-chapter plan; `ring-book-description.docx` and the editor's feedback), the V2 table of contents (19 chapters), the proof corrections, `ring_book.xlsx` (North Africa population data of chapter 4), `ring-functions.txt`, `fiction.rtf` (notes on metaphor in fiction), `map.docx` (the Ringorialand map), `Reviewing Book Proofs.pdf` (Apress's instructions), and `literary-piece-arabic-2020.docx` (a 263-word literary text of the author's in Arabic, May 2020, kept as evidence of his literary voice) |
| `code/` | `chapters/chap1..8` the book's code, `from-nestor/` a reviewer's number-to-words program in parts, `ring-book-code-update.zip` |
| `figures/` | the figure deck of each chapter (PowerPoint; chapter 9's is 42 MB) and `ring-book-final-snapshots.pptm` |
| `cover/` | the cover (Apress PDF, PNG, 3D mock-up), the author's photo, the cover draft deck |
| `press/` | Amazon sales screenshots (2020) and the Medium article's images |
| `style/` | the study of the writing: `readings/` one close reading per chapter by a fresh reader, `copyedit-diff.md`, `metrics.md`, and `STYLE-ANALYSIS.md` (the synthesis) |

Not copied: the 2019 drafts and their variants, the duplicate `Gold/0N_*.docx` masters (same text as the reviewed files minus the review), stock image packs,
DHL receipts, the Apress reviewer's PDF of a paper on visual programming, a root-cause-analysis tool installer. They remain in `D:\MyDocs\Ring Book`.

## Numbers (from `manuscript/text/_stats.json`, prose only, code excluded)

Chapters 1 to 9: about 73,000 words of prose and 3,600 lines of code in Word (chapter 9's code excluded), 4,100 sentences, median sentence 16 words,
one sentence in thirty longer than 40 words; 192 questions to the reader, 140 exclamation marks, 455 parenthetical sentences; "you" 1,760 times, "we" 1,060, "I" 520.
The published book is longer (chapter 9 alone is 26,000 words typeset) because figures, tables and code are counted there.
