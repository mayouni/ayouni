# What the copyeditor changed — the reviewed Word text against the published proofs (chapters 1 and 5)

Made 2026-10-11 by an agent aligning `manuscript/text/ch01.md` and `ch05.md` (the author's last Word text) with `proof-ch01.txt` and `proof-ch05.txt` (the typeset pages), sentence by sentence with difflib, and reading Apress's 48 author queries (AU) in the proofs. It shows the author's habits as a professional editor saw them; which of the editor's choices were right is the author's to say.

**Caveat first.** The Word files are an earlier state than what went to Apress: the proofs contain whole sections the Word text lacks (ch01 "What You Will Learn", footnotes 1–52; ch05 "Nine Things", for/for in, infinite loops, output listings). So "no counterpart" sentences are mostly author-side additions, not editor cuts. Only same-content pairs and the AU queries are attributable to the copyeditor.

**Proportion untouched.** Word-identical after ignoring punctuation, quote style, cross-references and footnote marks: ch01 88/334 = 26%, ch05 113/365 = 31%. Another 25–33% changed only by a serial comma, "see Figure 1-x", or a period. Roughly one sentence in four was substantively rewritten.

## 1. Sentences split or shortened
- "Frankly Mahmoud Fayed is an amazing guy: answers in a fraction, is reliable, clear-thinking, very well organized, and socially kind-and-funny" → "an amazing guy. He responds quickly, is reliable, and is kind of funny" (a meaning slip: kind-and-funny → kind of funny)
- "this is a LIST containing the answers and what you need is to get the answer by simply specifying its index" → "this function is a list containing the answers. To get the answer, you just need to specify its index"
- "Very little visual helpers are embedded into our IDEs: a syntax spell checker, …" → "A few visual helpers are embedded into our IDEs. They usually have a syntax spelling checker, …"
- "(remember what we've made in the last section in helloring.ring)" → "(remember helloring.ring?)"
- "My recipe to you … is to cut with the established mental paradigm of representing computer code, cultivated by our software industry since its old days, and avoid" → "My advice to you … is to stay away from"

## 2. Words cut
"very" 10→2 in ch05; ellipses "…" 12→2 in ch01 (nearly every trailing "…" became a period). Hedging pile-ups and "obvious" went too.
- "the very known WHILE loop" → "the well-known while loop"
- "The following is a very minimal Drakon diagram." → "Figure 5-2 shows a minimal Drakon diagram."
- "the very important subject of scoping" → "the important subject of scoping"
- "call the obvious addDays() function" → "call the addDays() function"
- "this would take, maybe, and probably, and hopefully, and some times, and many times… 2 to 3 hours to come!" → "this will take probably two to three hours!"
- "Let's listify it to save the world…" → "Let's listify it to save the world."
- "Its implementation is dead simple. Its use is a real fun." → "Its implementation is simple, and it's fun."

## 3. Contractions: kept
"I'm", "let's", "can't", "you're done", "learn 'em by heart!", "Congrats!" all survive. Two expansions only: "It's not gratuitous poetry though" → "This is not gratuitous poetry"; "It's identical to what we had" → "The results are identical to what we had".

## 4. "we" → "you"/"I", and future tense for roadmaps
- "In this chapter, we learn the language constructs we have in Ring" → "In this chapter, you will learn the language constructs in Ring"
- "That's why we adopted a pure visual approach" → "That's why I have adopted a purely visual approach"
- "In this section, we try to unveil relevant samples" → "In this section, I will show relevant samples"
- "In this chapter, we learned a lot!" → "In this chapter, you learned a lot!"
- "In the first section, I guide you in installing Ring and getting it running." → "First, I will guide you to install Ring and get it up and running."
Inside worked examples, "we"/"our" was left alone.

## 5. Personification and gender
Ring as "she" (4 in ch01) → "it"; user "her" → neutral; AU20: "could we use craftsperson to be gender neutral throughout?"
- "Let's ask her about the current date, no mystery, you say? Date():" → "Now let's ask Ring about the current date. It's easy too: we type ? date()."
- "I want her to understand that I'm thanking her and respond accordingly!" → "I want Ring to understand that I'm thanking it and respond accordingly."
- "Listening to Ring when she complains" → "Listening to Ring When It Complains"
- "She can end it gently without disruption" → "The programmer can end it gently without disruption"
- "delivering a new data to the user as a solution to her problem" → "delivering data to the user as a solution to a problem"

## 6. Informal phrases, French calques, flourishes replaced
- "What the hell is this?! A programming language accepting" → "What is this? It's a programming language accepting"
- "Run it again! Mooooving so smoothly…" → "Run it again. We're moving along so smoothly!"
- "Ready? Please give me your hand…" → "Ready?"
- "without having pills of sweat in the forehead" → "without any sweat from the programmer"
- "You are only a little step from putting the magical Ring your finger!" → "You are only a few steps from having Ring up and running."
- "To coronate our tour of Ring documentation system we end up with a very useful piece" → "To end our tour of Ring documentation system, let's look at"
- "I take you in a promenade in the rich set" → "I will introduce you to the rich set"
- "rather than being your black beast in writing programs in Ring" → cut
- "you've snapped halfway of your path to programming craftsmanship" → "you're on your way to programming craftsmanship"
Homophone/spelling slips fixed in prose: hole→whole, fellow→follow, staff→stuff (but "implementation staff" and "Required Ring Staff" survived), haltered→hindered, mussels→muscles, dye→die, wandering→wondering, Mosco→Moscow, CNTRL→Ctrl.

## 7. Metaphors and jokes: queried, mostly kept
AU10: "these metaphors are very confusing to someone trying to learn a language. what does apples have to do with this discussion?" — yet "From Dates to Apples" is still the printed heading. AU8 "delete this? it seems distracting" (Karni/Hausa aside) — kept, with a footnote. AU3: "I'm deleting some of this extra text that distracts… it's not going translate well for different audiences. ok?" (installation-folder hospitality riff, trimmed). Kept intact: Ring garden and flowers, "Ring and gaming are in love!", "stranger in Moscow", "hot dish of shakshuka", "expressiveness paranoia", "at your own cost, dear friend!", "nocturnal programming owl", the Egyptian-friends train joke, "yalla", "Barka da zuwa", "Taya murna".

## 8. Headings renamed
Title Case throughout; "Ring algorithms" → "Crafting Ring Algorithms"; "Question of the beginnings: any "Hello, World!" tutorial?" → "Any "Hello, World!" Tutorial?"; "Introductive article" → "Introductory Article"; "Asking questions to Ring" → "Asking Ring Questions"; "Say hello to the window" → "Say Hello in the Window"; "The 1st commandment" → "The First Commandment"; "Before you leave: a homework!" → "Before You Leave: Homework!"; "Summary" heading added. Left inconsistent: "Three Ways to Access Ring Documentation" over a body saying "There are four ways". AU6 proposed renaming "Your First Ring Program"; author kept "Hello Ring!".

## 9. Notes, tips, lists restructured
Run-on enumerations became bullets or numbered steps, each a full sentence with a period; list-final ";" and "; and" removed; every colon lead-in ("like this:", "Result:") became "as shown in Figure 1-x" / "See Listing 5-x".
- "print the content of the whole list: ? ti;" → "You can print the content of the whole list with ? ti."
- "Set 222 in a constant" → "1. Set 222 in a constant."
- "Arrows are replaced with plain lines; and" → "Arrows are replaced with plain lines."
- Note box: "hash maps, sometimes called dictionaries or indexed lists." → "hash maps. (They are sometimes also called dictionaries or indexed lists.)"
AU13: "please change it to its own code line and introduce it with a sentence."

## 10. Code and comments: not edited
Typos in code survived: "// Witch leads logically to "32"", "// In stead of :", "// Bye a puppy", output "I won't bye a Terrier !", "int the console". AU24 asked whether See/Put should be lowercase; they stayed capitalized.

## 11. Sentences added for clarity
"I will answer these questions in the following sections." / "Here are some other resources for Ring." / "Let's fix it." / "Try it." / "It's as simple as that." / "The following are my three commandments to you."

## 12. Mechanics
Serial comma everywhere; numerals under ten spelled out ("3 windows" → "three windows", "7 minutes" → "seven minutes"); "304$M" → "$304 million"; "30%" → "30 percent"; "Youtube" → "YouTube"; "Mac OS" → "macOS"; "File > New" → "File ➤ New"; "hit" → "click/press"; "say ? time()" → "type ? time()".

## 13. What the editor refused outright
Emojis, three times: AU7 "are we really printing little emojis like this?", AU22, AU19. The arithmetic: AU4 "it's really confusing to use 10 million if the number is really 22 million", AU5 "please update these numbers to match the new math". AU2 doubted "skewer" (kept). Four queries on "Ringuifying" (AU5/10/12/14) — the author kept it.

## The five habits the editor corrected most
1. Lead-ins ending in a colon or "…" pointing at an unnamed figure, replaced by a full sentence with an explicit cross-reference.
2. Narrator "we" and present-tense roadmaps, replaced by "you will"/"I will".
3. Personified or gendered pronouns (Ring as "she", user as "her", "craftsman").
4. Intensifiers and hedges: very, really, obvious, dead simple, stacked "maybe, and probably…".
5. Run-on sentences with colons/semicolons and inline lists, split into short sentences or bullets, plus homophone slips (hole, fellow, staff, witch).

## What the editor left alone
Jokes, metaphors and cultural words (asked about, rarely removed); contractions; exclamation marks (count went up, not down); first-person asides and footnote digressions; all code and code comments, typos included; "Ringuify" and "craftsman" despite repeated queries.
