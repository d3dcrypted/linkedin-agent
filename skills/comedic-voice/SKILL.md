---
name: comedic-voice
description: "Use when writing irony: stand-up structure for text."
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [writing, humor, irony, sarcasm, voice]
    related_skills: [humanizer, linkedin-post]
---

# Comedic Voice

Make people laugh **by craft**, not by improvisation. Written stand-up, not cabaret.
A post that gets a laugh once in every ten jokes is worse than a serious one: the
reader realizes you're trying.

## When to Use

- When a text must come across as ironic, sarcastic or irreverent, but credible.
- When you need to alternate a serious tone and a comic tone on the same page.
- Don't use when: the content is bad news, clinical data, an error message. There the
  tone is flat on purpose.

## Theory (why it works)

**Benign Violation Theory** (McGraw, Warren): humor triggers when three conditions hold
together: there is a violation (something that clashes with how the world should work),
the violation is perceived as benign, and the two perceptions coexist. It fails in two
ways: too timid (no violation, no laugh) or too pushed (malignant violation, embarrassment).

Three levers to make a violation benign:
1. **Alternative norms**: the sentence has a second meaning that holds up (this is the
   mechanism of the double meaning, but also of the technical joke).
2. **Psychological distance**: "comedy is tragedy plus time" (Italian rendering:
   `"la commedia e' tragedia piu' tempo"`). A disaster from three years ago is material;
   yesterday's is not.
3. **Adherence to the violated norm**: the people who share the norm are the ones who
   laugh. That is why the right audience is the one that knows what you're talking about.

**Incongruity-resolution**: it is not the incongruity that makes people laugh, it is its
*resolution*, the moment the reader gets it. Practical consequence: the setup must be vague
enough to allow the flip, and the joke is never explained.

**Irony vs sarcasm** (Partridge): irony says the opposite of what it means; sarcasm is its
intentional and critical version, an alternative to direct reproach. Biting sarcasm in a
public post is used only against yourself or your own category, never against the reader.

## The craft (how to write it)

Minimum unit: **premise** (the theme), **setup** (creates expectation), **punchline**
(the payoff), **tag** (extends the laugh with a second joke on the same setup).

The 7 structures. Use **one** per beat, not all of them together:

| Structure | Mechanism |
|---|---|
| Misdirection | the setup points to A, the punchline lands on B |
| Rule of three | two consistent elements, the third throws it off |
| Callback | repeat a word from the opening in the closing |
| Reversal | you flip the expectation onto yourself (I am the problem) |
| Analogy | pair the technical topic with something everyday |
| Exaggeration | push the flaw to absurdly precise consequences |
| Understatement | say less than the situation deserves |

In text, the line break **is** the timing. A short sentence after a long one is a
punchline: nothing else is needed to mark the beat.

Density: **1-2 real laughs per text**, not ten. The rest is tone. In a post, the right
structure is a reduced *tight five*: open with the discreet joke, close with the best one
(never open with the strongest).

## Anti-patterns (the tells of cabaret)

- Exclamation marks, emoji, "LOL", ALL CAPS for laughs.
- Cabaret density: one joke per sentence. It rhymes with embarrassment.
- Absurdity without a premise: that is the non-sequitur, not the joke.
- Explaining the joke, or declaring that you're kidding ("ovviamente" = "obviously",
  "si fa per dire" = "figuratively speaking"; Italian examples).
- Joke about data: the number is sacred, you can only frame it. Never make it the punchline.
- Wrong audience: the victim is always you or your category, never the reader, never
  whoever is weaker.
- Hysterical tone: in text, deadpan wins. Understate, don't shout.

## Tone

**Voice and tone are not the same thing.** Voice is the stable traits that make you
recognizable in every text: vocabulary, contractions, sentence length, rhythm. Tone is the
attitude toward the subject at that moment. Analogy: voice is a musician's style, tone is
the mood of the piece. In practice: tone changes from post to post, voice does not. If the
voice changes, you sound like a different author.

**Declare the tone, don't allude to it.** In a study measured on LLMs (Sayem, EJALS),
explicit stylistic instructions had stronger effects than implicit contextual signals:
formal prompts +137% sentence length and +185% technical-term density; emotional prompts up
to 7,19 emotional markers per 100 words versus zero in the neutral condition. Three
measurable knobs: sentence length, technical density, emotional markers.

**Tone by register, not by adjectives.** "Formal", "ironic", "direct" are vague labels and
the model stuffs in whatever it wants. Register (Halliday) has three specifiable axes:
- field: what is being talked about (technical-operational, business, personal);
- tenor: the relationship with the reader (peer, expert, salesperson);
- mode: channel and form (short post, written prose).
Characterizing tone by register beats labels both for tone fidelity and for preservation
of meaning.

**Tone map** (one tone per beat, not all together):

| Beat | Tone | Markers |
|---|---|---|
| Opening | dry | short sentences, zero adjectives, zero signals |
| Data | flat | long sentences, high technical density, zero emotional markers |
| Turn | ironic | short sentence after a long one, understatement |
| Closing | dry | returns to the voice of the opening |

**Serious and ironic coexist only if separated**: first the bare fact, then the comment.
Never both registers in the same sentence, otherwise the reader doesn't know what to take
seriously. And the transition is the best place for the joke: the seriousness just
established is the setup.

**Changing tone within the text.** In a short text the tone doesn't rotate: one change
only, and it is the turn. The change must have a visible cause, otherwise the reader is
disoriented, not amused. Three ways to make it land:
1. announce it with a transition sentence (Italian example: "Qui la parte seria, perché
   serve" = "Here's the serious part, because it's needed");
2. prepare it, half-hinting at the register that is coming while you are still in the
   other one (Catch-22 revisits the same elements, which become darker and darker);
3. never let it fall back: the serious register is not closed again with a joke in the
   same sentence.

Note: if the post becomes audio, tone moves to prosody (control of emotion and intensity
at three levels: global, sentence, word). Out of scope while the product is text.

## Calibration examples

**Good** (understatement + reversal, author as target):
Example (write yours in English): "Ho automatizzato il controllo qualita' del nostro codice. Il primo bug l'ha trovato nell'automazione. Sto vincendo."

**Bad** (cabaret density, no target, explains the joke):
Example (write yours in English): "Ho automatizzato TUTTO! Il codice e' un disastro! LOL! Ok, smetto di fare il comico."

## AI Slop

**Operational definition** (Willison, deepfates): not all AI text is slop. It is slop when it
is generated without thought **and** imposed on someone who did not ask for it. Wikipedia
adds the surrounding context: filler that favors speed and quantity over substance,
produced in volume. The discriminant is not "I wrote it with an LLM", it is whether
the text has a reason to exist.

**The concrete risk**: a slop post is not contested, it is archived. You don't lose the
discussion, you lose the author. Generated in series does not mean read badly; it means
not read.

**Markers blocked by the gate** (full list in Wikipedia:Signs of AI writing, of which the
`humanizer` skill is the operational version):
- filler phrases ("in today's world", "it is important to note that",
  "in conclusion");
- punchy closers, final courtesy formulas;
- uniform density: all paragraphs the same length, no roughness;
- brochure vocabulary ("revolutionary", "unlocks the potential");
- list structure disguised as prose.

**Make the post non-correlatable.** Detectors use stylometry (StyloAI, 31 features), and
the most convenient feature is recurrence. A text identical to itself in every post is the
fastest way to get correlated: anyone reading two posts recognizes the signature, and any
detector finds it. So:
1. **No fixed sentences, ever**, not even the disclaimer. The semantics are fixed (human
   thought, AI assembly); the form is rewritten every time. `check_post.py` compares the
   closer with those already used (`posts/.closers.log`, difflib similarity ≥ 0.7) and
   blocks the repetition.
2. **Irregularity**: vary paragraph length, don't close every section with a summary, leave
   one detail too specific to be generic. Specificity cannot be faked: it is the residue a
   generator does not produce.
3. **Friction**: an opinion, an uncomfortable number, a name. Flat text is the signature.

## Sources

- McGraw & Warren, *Benign Violation Theory* (HuRL, Univ. of Colorado)
- *Incongruity-resolution*, ScIU, Indiana University, 2023
- Partridge, *Usage and Abusage*, cited in ACM CSUR, *Survey on Automatic Generation of Figurative Language*
- ACM CSUR, *Computational Humor Modeling: A Survey on the State of the Art*
- Haeusler, *Llama LOL* (few-shot as the main lever for comic tone)
- Sayem, *Prompt Engineering and Stylistic Control in LLMs*, EJALS (explicit vs implicit tone)
- Ouellette, *All Write Now* #17 (stable voice, malleable tone)
- *Steering LLMs with Register Analysis for Arbitrary Style Transfer*, arXiv 2505.00679
- Halliday, register: field / tenor / mode
- *Nearest Neighbor LMs for Stylistic Controllable Generation*, arXiv 2210.15762
- Wikipedia, *AI slop* (Willison, deepfates; Merriam-Webster and ADS Word of the Year 2025)
- Wikipedia, *Signs of AI writing* (AISIGNS)
- *StyloAI*, arXiv 2405.10129 (31 stylometric features)
