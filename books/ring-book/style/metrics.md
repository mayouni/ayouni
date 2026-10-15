# Metrics of the Ring book's prose (chapters 1 to 9, the author's last Word text)

Computed 2026-10-11 over `manuscript/text/ch01.md` … `ch09.md`, prose only: code lines, tables, headings and figure captions excluded. Chapter 9's prose is complete in Word; its code was pasted as images and is not counted anywhere here. Counts are mechanical (a regex over the text); treat them as orders of magnitude.

## Size and rhythm

| | value |
|---|---|
| prose words | 72,915 |
| sentences | 4,112 |
| mean sentence | 17.7 words |
| sentence length quartiles | 10 · 16 · 23 words; longest 86 |
| sentences over 40 words | 3.3 % |
| paragraphs | 2,158; median 26 words |
| one-sentence paragraphs | 968 (45 %) |
| sentences with a parenthesis | 455 (11 %) |

The rhythm is a long sentence then a short one: a quarter of the sentences are ten words or fewer, and almost half the paragraphs are a single sentence (a verdict, a hand-over, a question).

## Per chapter (prose words · sentences · mean length · questions · exclamations · you · I · we)

| ch | words | sentences | mean | ? | ! | you | I | we |
|---|---|---|---|---|---|---|---|---|
| 1 | 6,129 | 243 | 25.2 | 41 | 24 | 155 | 87 | 110 |
| 2 | 5,745 | 209 | 27.5 | 15 | 5 | 105 | 41 | 78 |
| 3 | 3,786 | 155 | 24.4 | 12 | 5 | 46 | 24 | 98 |
| 4 | 2,363 | 115 | 20.5 | 12 | 4 | 70 | 11 | 33 |
| 5 | 6,559 | 269 | 24.4 | 11 | 20 | 165 | 55 | 102 |
| 6 | 3,826 | 204 | 18.8 | 13 | 16 | 92 | 24 | 56 |
| 7 | 10,655 | 470 | 22.7 | 26 | 22 | 240 | 24 | 219 |
| 8 | 14,984 | 609 | 24.6 | 35 | 24 | 364 | 99 | 198 |
| 9 | 19,733 | 867 | 22.8 | 40 | 26 | 524 | 155 | 166 |

(The per-chapter sentence splitter counts fewer sentences than the whole-corpus one; the ratios hold.) "You" outnumbers "we" two to one, and "we" outnumbers "I" two to one, except in chapters 1, 8 and 9 where the author tells his own story. The annex (7,373 words) inverts it: I 175, we 109, you 103.

## Address and punctuation (per 1,000 prose words)

| | per 1,000 words |
|---|---|
| colons | 15.2 |
| parentheses opened | 8.4 |
| double quotes | 6.7 |
| question marks | 3.3 |
| exclamation marks | 2.4 (140 in all; the published book has more, not fewer) |
| ellipses | 1.2 |
| semicolons | 0.6 |
| dashes | 0.5 |

The colon is the signature mark: it introduces code, output, a list, a definition, a punchline. Em dashes are almost absent (the Refine book's style guide made them "the workhorse"; that is the agent's rhythm, not the author's). Semicolons appear only at the ends of list items.

## Openers (first two words of a sentence, most frequent)

In the (82) · This is (55) · In fact (41) · If you (35) · In this (30) · The first (27) · To do (21) · There is (21) · It is (20) · There are (20) · In Ring (18) · In particular (18) · At the (18) · As a (18) · The next (18) · As you (16) · When you (16) · And then (15) · For the (15) · In practice (15).
First words: The 360 · In 351 · This 126 · To 119 · And 113 · A 98 · You 92 · But 88 · If 79 · As 66 · When 62 · There 56 · Let's 55 · We 52 · For 50 · Now 48 · It 47 · Then 44 · At 37 · I 36.
Sentences beginning with "And" or "But": 201 (5 %).

## Imperatives that open a sentence

Let's 55 · Execute 25 · Run 25 · Save 13 · Add 10 · Try 9 · Take 8 · Go 6 · Put 5 · Remember 5 · Look 5 · Read 4 · Open 3 · Note 3 · Imagine 3 · Think 3 · Change 3 · Create 3 · Hit 2. "Execute" and "Run" are the book's two verbs.

## Word counts worth knowing

| word | count | | word | count |
|---|---|---|---|---|
| then | 319 | | very | 58 |
| so | 191 | | well | 52 |
| world | 157 | | think | 49 |
| now | 111 | | therefore | 44 |
| let's | 104 | | in fact | 43 |
| visual / visually | 125 | | clean | 41 |
| see | 98 | | mind / brain | 47 |
| just | 120 | | simply | 31 |
| game | 328 (ch 8–9) | | story | 28 |
| expressive / -ness | 32 | | of course | 23 |
| imagine | 14 | | magic / magical | 20 |
| beautiful | 16 | | journey / trip | 19 |
| she / her (for Ring or the programmer) | 52 | | garden / flower | 9 |

"World" is the author's noun for a program's domain long before the Softanza book made it a term. "Visual" and its family outnumber "beautiful" eight to one: the doctrine is visuality, not beauty.

## Questions and exclamations: where they sit

192 questions. Most are of three kinds: the question put to the machine ("What time is it now?"), the question put to the reader as a beat ("Agreed?", "Tired? I understand."), and the self-answered question ("Practice? Yes, nothing is better than practice."). 140 exclamations; the readers' finding across chapters is that they sit after a run or a reveal, almost never on an abstract sentence.
