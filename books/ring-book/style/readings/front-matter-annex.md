# Close reading — the front matter, the annex, the nine-things lists and the 2019 proposal

Read 2026-10-11 by a fresh reader (an agent given the extracted texts and `STYLE-BRIEF.md`, nothing else).

## (a) What the author says he is doing

**The promise, in one sentence he reuses verbatim across five documents** (description §The book, resume, gold-back1/2, introduction, story §The Ring language): "Ring is used in this book more as a computational thinking medium then a programming language." The companion claim, also copied: "Its simple pseudo-code-like footprint helps focusing on the underlining logic and ideas instead of the code itself." Note the recurring typo "then" for "than" survives every draft until the Apress proof ("medium than").

**The pedagogy he claims:** "gentle yet rigorous ... with clarity as a first concern, rich visualizations and a lot of practical code examples" (introduction §The book). Visuality is doctrine, not decoration: "Visuality is then used as an obligatory passage to write beautiful code" (story §Coding-for-failure); "Reader is never left to theoretic narration or general advices" and "Lessons learned from practice and real-world situations are first-class citizens of the book" (story §The book). The chapter-5 title confirms it: "Before We Start: Long Live Visuality!" (proof ToC).

**What it is not:** "not intended to be a clinical user manual of Ring, though, but rather a passionate alchemy of technical knowledge, real world programming experience and critical personal reflections" (introduction, resume, description; "forged by the author during the last three decades" in story §Disclaimer). The book is "an intellectual conversation ... between a seasoned programmer questioning todays code complexity, from one hand, and an emergent programming language providing elegant and unprecedented answers" (introduction). The copyeditor recast the partners as "between you, the reader, and me" (proof xxiii) — the author had made the language, not the reader, his interlocutor.

**The reader he imagines:** feminine by default — "whatever language programming camp she comes from" (description, resume), "Focus is put on the programmer herself" (story §Purpose). Not a beginner but a convert: "for those who are passionate about the craftsmanship culture in writing code" (introduction); "a special chapter dedicated to anyone who gets an emotional connection to Ring through this book and decides to become a master of ring" (gold-back1). The 2019 story.md addressed ten audiences, from "Old-days programmers who deserve a respectful comeback" to "Technology decision makers inside governments" (§Audience). The stakes he sets: "To be a computer programmer is more than gathering a set of technical skills ... It's a personal legend, a destiny!" (story §Problem).

**Self-reference:** in every submitted front-matter text he writes about himself in the third person — "author's motherland", "the author delivers the juice of his 30 years' experience" (introduction). The proof converts all of it to "I" ("I'll deliver 30 years of experience"). He is first-person in the annex and in prose addressed to Mahmoud, but hides behind "the author" in official paratext.

**The biographical anchor, repeated in four documents:** "wrote his first BASIC computer statement, in the mid-80s, using only pen and paper, when he was 10 years old ... in the rural village of Regueb" (bio); gold-back1 adds the fantasy world was "made for his 8 years old daughter to explain to her what he is talking about in this book". Dedication: "To the soul of my father, Mohsen, who gave me his ring as a message."

## (b) The annex's voice

The annex is Mansour as questioner, and the register shifts three ways:

1. **To Mahmoud: deferential, batteried questions, superlative thanks.** Questions arrive in volleys of three or four after a framing observation: "By closely studying the programming style adopted in writing Ring ... Now, can you tell me why..." (§Composition Over Inheritance); "A bunch of questions this time:" (§About the Ring Compiler and VM); "My question is double:" (§The secret behind your reactiveness). Responses escalate: "Very nice answer, yet really instructive!", "This is phenomenal!", and the closing blessing "May your life be all happiness and success" (§The secret...). Mahmoud's prose by contrast is short, bracketed "(Int)", bulleted, with ":D"; the contrast makes Mansour's abstraction audible: "shape the perimeter of Mahmoud's technical personality" (intro), "belongs to the deep spirit of the language" (§When the default value of NULL is changed).

2. **To Bert: courteous combat with a measurement.** "What you say is interesting. Just I want to emphasize that..." then a 60-word cache sentence, then: "I took 5 minutes this morning to try optimize the code ... 658.78s ... a gain of 72% in raw performance (185.67s)" (§Speed of Ring list VS C-code array). He concedes publicly: "In my book 'Beginning Ring', unfortunately, I didn't find a window to talk about this, may be in a future book about 'Advanced Ring' :)".

3. **To Ring itself, as a person** — the same move the chapter titles make ("Asking Ring Questions", "Listening to Ring When It Complains", proof ToC): "Let's talk to Ring and say:" (§A strange behavior in len()), "what we have is... nothing!" (§NULL).

Personal material is placed inside code, not around it: `["mansour","teeba","haneen"]`; "the arabic names of my two daughters, Teeba and Haneen"; the Shawqi verse on the teacher as test string; "مصر هي أم الدنيا" (a courtesy to the Egyptian Mahmoud) as example data (§Advice on the use of operator overloading, §Numeric Overflow Error). That is the chapters' Tunisia/family habit, miniaturised.

## (c) What the 9-things lists reveal

- **Value is framed as disposition, not fact.** Verbs: Understanding (×6), Mastering (×4), Discovering, Embracing, Practicing, Experimenting, Fabricating, Mitigating. Chapter 7 promises "Embracing the spirit of functional programming" and "Developing a self-consciousness of when to go functional"; chapter 9 "Understanding the meta-code social and emotional dimensions of programming".
- **Counted sets everywhere:** "three forms of logic flows", "three algorithmic levels", "three golden rules" (ch 5); "four object composition techniques" (ch 7); "the 12 technical skills" (ch 8); the ToC adds "Three Values of MVC", "Seven Steps", "Three Commandments", "Twelve Practical Skills", "Meet the Gang of Four". Nine itself is such a number.
- **Ring is the grammatical agent:** "How Ring sees variables", "How Ring undertakes the implicit conversion", "How Ring switches object scopes" (ch 2, 6).
- **The ninth item is the lofty one:** ch 2 "the dynamic advantage", ch 5 "golden rules of programming craftsmanship", ch 9 ends on a question, "How to design a personalized mastery capacity building program ...?"
- **Scope inflation:** chapter 1 claims "How to contribute the official Ring codebase" and "Writing multilingual text"; chapter 4 "Changing the core keywords and operators of the language".
- **Tic:** mixed grammar inside one list (How-to / gerund / question), e.g. ch 9 item 2 is a question, items 3–8 gerunds.

## (d) description.md → description-feedback1.md

Only three regions changed; the Rationale (Tunisia, "nobleness"), the Ring paragraph, the four-part plan and the bio are untouched.

1. **Audience opener** cut from "Anyone who care about simplicity and innovation in programming, about critical thinking and capacity building in coding and software craftsmanship" to "Anyone who is passionate about computer programming".
2. **Audience bullets four → two.** Deleted: "Passionate programmers who want to hack new things and walk around crazy software ideas" and "Researchers in computational linguistics, natural language processing and machine learning". Kept: educators/students (now prefixed "Beginners,") and 2D gaming.
3. **Author line:** "effective yet beautiful software" → "effective software". Also "20 years" → "30 years", "+21 million" → "21+ million".

So the publisher wanted the word *beginners* in, and the hacker/researcher/craftsmanship framing out. The Tunisia opening survived this round but drew AU4–AU6 at copyedit: "these seem like some big statements that aren't backed up ... I suggest deleting this part of the intro". The TIOBE "top 50 ... February 2018" became "top 100" with AU7. Scope shrank across drafts: story (2019) promised "30 chapters divided into 5 parts"; description, four parts with TextParser and "Advanced Ring"; the book shipped three parts, nine chapters, annex.

## Brief §3, 5, 7, 8 for the annex

**§3 Voice.** "I" for witness and tester ("I read once", "I noticed", "I'm not very comfortable"); "we" for the Ring community ("a unique feature we are all proud of", §Speed); "you" only in the intro ("I insisted to share them with you"). Exclamations: 9 in his own turns. Smileys ":)" ×2. Imperatives almost absent; he suggests ("I suggest then to be patient"). Humour is affectionate hyperbole: "no other languages can have such a 'big heart' :)" (§A language copying Ring).

**§5 Craft.** Long clause-stacked sentences closed by a colon and self-gloss: "...is something that makes a huge difference: I mean that one programmer can..." (§Speed). Openers: "Now,", "So,", "Hence", "Then,", "Finally, it is important to know that". Trailing ellipses end four turns. Signature connective **"yet"** used as "and": "Very nice answer, yet really instructive!", "gentle yet rigorous", "impressive yet comprehensive", "effective yet beautiful", "Yet you discover". Favourite words across the corpus: beautiful/beautifully, spirit, craftsmanship, learnability, expressiveness, visual/visuality, unprecedented, dogma-free, alchemy, journey, "window" (as opportunity), fabricate, juice. French calques an editor cuts: "then" for than, "in the same time", "from one hand ... from the other hand", "may be", "imbricated loops", "witch", "hole", "cash misses", "programming luggage", "quiet like this".

**§7 Exemplary.**
1. "This is phenomenal! I didn't' expect that it is possible to overload the functions made in C directly in Ring. I better see now why flexibility is not a risk but belongs to the deep spirit of the language" (§NULL) — discovery in public, then a principle extracted.
2. "if we want to subdivide the text between two persons, طيبة and حنين (the arabic names of my two daughters, Teeba and Haneen)" (§Operator overloading) — family as test data, no comment.
3. "In my book 'Beginning Ring', unfortunately, I didn't find a window to talk about this, may be in a future book about 'Advanced Ring' :)" (§Speed) — honesty marker plus his "window" image.
**Weakest:** "Understanding how cashes work (at their three levels L1, L2, and L3), and what best practices the programmer need to adopt in designing his lists and writing his iterations over them, is something that makes a huge difference" (§Speed) — 40-word subject, misspelling, vague predicate, before he reaches the point.

**§8 Easy to fake badly:** the exclamation-and-smiley enthusiasm and the "beautiful/spirit/magical" lexicon (becomes gush); the counted-set headings (becomes listicle); the calques (an AI either caricatures or scrubs them — the proof shows they are noise the copyeditor removed, not voice). **Hard-to-fake core:** the questioner's stance — he reports the test he actually ran with its numbers, concedes what the book lacks, puts his daughters and village inside the code, addresses the language as a person, and lifts every technical point to a civilizational claim (Al-Jam to code quality; "a personal legend, a destiny!").
