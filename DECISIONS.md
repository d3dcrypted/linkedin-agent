# Design decisions

Why this repo is built the way it is. Every non-obvious choice is recorded here
with the reason behind it.

`Decided by` is `Human` when the author (d3d) made the call, `Agent` when the
assistant proposed it and the author accepted it. Several entries quote the
author's own request, because the wording is more precise than a paraphrase.

---

## 1. Publish by hand, not through the LinkedIn API

- **Decided by:** Human.
- **Choice:** the tool produces a draft, the author approves it, then copies and
  pastes it into LinkedIn.
- **Why:** posting through `w_member_social` requires an approved LinkedIn app
  and puts account risk on the line; automating the publish action through a
  browser violates the platform's terms of service. Manual publishing has zero
  API surface, zero approval friction, and the author is going to read the post
  before it goes out anyway.
- **Rejected:** OAuth app plus API posting; browser automation of the publish
  button.

## 2. The working version is an agent skill, not a standalone script

- **Decided by:** Joint, after measurement.
- **Why:** the native `web_search` tool works from this VM; every keyless engine
  reachable from this IP returns a challenge or 429, and asking the LLM to
  propose URLs produced hallucinated arXiv identifiers. Shipping a standalone
  tool whose search stage does not work would have been a demo, not a product.
- **Consequence:** `lnkd.py` carries the blocked-search history in its comments.
  Running it standalone needs a search key (`TAVILY_API_KEY`) wired into the
  `search()` dispatcher; without it the keyless DuckDuckGo fallback applies.
  See §18.
- **Cost of this choice:** the repo cannot reproduce the pipeline end to end on
  its own, because the runtime is a skill living in the author's agent profile.
  Stated plainly in the README rather than hidden.

## 3. Markdown files and git. No database, no queue, no scheduler.

- **Decided by:** Human, explicitly asking for the laziest option that works.
- **Why:** one post is one file. The pipeline stage lives in the frontmatter
  (`status: draft`), and git is the history. A queue or a database would be
  infrastructure with no reader and no second consumer.
- **Rejected:** SQLite/Postgres state, a job queue, cron. Version 1 has no
  recurring work, so a scheduler would only be a way to burn tokens unattended.

## 4. `humanizer` runs on every post, and it is not optional

- **Decided by:** Human, verbatim: *"cerca script skill plugin o quello che di
  humanizer e applicalo sempre"*.
- **Choice:** the draft does not get saved before passing through the `humanizer`
  skill. Vendored copy of `blader/humanizer` v4.0.0, MIT, pinned in git rather
  than installed from a package index so the exact version travels with the repo.
- **Why:** the text is machine-assembled by definition, so the classic generated
  tells are the default outcome, not a risk. The pass is cheap and it is the
  difference between a post and a template.
- **Carve-out:** deliberate comedic devices (rule of three, understatement,
  callback, reversal) stay. The humanizer removes patterns the text chose for
  itself, not devices chosen on purpose. This is the author's requirement to be
  actually ironic rather than generically formal.

## 5. Sources are inline micro-citations, never a block at the end

- **Decided by:** Human, verbatim: *"le risorse debbano essere sempre presenti
  nel testo, troviamo un modo per inserire le risorse senza togliere troppo
  testo"*.
- **Choice:** `(BSI, 2025)` or `(Paligo, ott. 2026)` inside the sentence that uses
  the figure. No `Sources:` block, no long URLs in the body.
- **Why:** an inline attribution proves the specific claim and costs about four
  words. A source list at the bottom costs a scroll, and it can be dropped from a
  repost without the text losing anything visible.
- **Rule that follows:** if a source cannot support a claim, the claim is
  removed. It is never softened into something the source does support.

## 6. The AI disclosure is a fixed rule with a variable form

- **Decided by:** Human, verbatim: *"specificare sempre in modo autoironico che
  il post è stato pensato da un umano ma messo insieme da una AI come regola
  principale"*.
- **Choice:** the draft states, in a dry and self-aware way, that the thought is
  human and the assembly is machine. It sits inside the text, not as a legal
  footer.
- **Why it is in the text:** a disclosure at the bottom reads as compliance. The
  same statement as the closing line reads as the author talking about his own
  tool, which is what it actually is.
- **Anti-correlation rule:** the same sentence in every post is the easiest
  stylometric anchor there is. Anyone reading two posts recognises the template,
  and any detector finds it in one pass. So the semantics is fixed (human
  thought, AI assembly) and the wording is rewritten every time.
  `check_post.py` compares the closing line against `posts/.closers.log` with a
  `difflib` ratio threshold of 0.7 and fails the draft if it repeats.

## 7. `check_post.py` is an executable gate, standard library only

- **Decided by:** Agent, accepted after it caught real defects.
- **Why:** a style rule that lives only in prose gets ignored the first time
  there is a hurry. The gate has to run anywhere, on any machine, with no
  virtualenv, so it uses `re`, `difflib`, `os` and `sys` and nothing else.
- **Banned families:** em dash, en dash, curly quotes, `not X but Y`,
  punchline-ending, exclamation mark, emoji, all-caps shouting, AI slop filler
  phrases, missing AI disclosure, missing inline sources, reused closing line.
- **Known ceiling:** the checks are regex based, so they catch templates, not
  intent. The gate protects the floor. A human still reads the draft. The
  similarity threshold of 0.7 is a heuristic and can produce false positives on
  short closers; raise it if that starts to bite.

## 8. Voice and humor come from published research, not from vibes

- **Decided by:** Human, verbatim: *"dobbiamo far sì che siano realmente ironiche
  sarcastiche e serie quando serve, non un'improvvisazione cabaré ma più uno
  stand-up comico eseguito dall'AI"*.
- **Why:** "make it funny" produces cabaret improvisation: a gag per sentence and
  no premise. The `comedic-voice` skill instead encodes Benign Violation Theory
  (McGraw & Warren: humor needs a violation, a benign framing, and the two held
  at once), incongruity-resolution, the setup/punchline/tag structure of
  stand-up, and measured prompt-control effects.
- **Measured input worth keeping:** explicit stylistic instructions beat implicit
  contextual cues (formal prompts produced 137% longer sentences and 185% higher
  technical-term density; emotional prompts produced up to 7.19 emotion markers
  per 100 words against zero in the neutral condition). That is why the tone is
  declared outright instead of implied.
- **Tone by register, not by adjectives:** "formal", "ironic", "direct" are vague
  labels that a model fills in as it likes. The same effect is specified through
  register axes (Halliday: field, tenor, mode), which is more faithful to the
  intended tone and preserves meaning better.
- **Non-negotiable rule:** the number is sacred, the tone is not. Figures stay
  flat and exact, and the humor lives in the framing, never in a punchline about
  a figure.

## 9. The AI slop check

- **Definition used:** not all machine-written text is slop. It is slop when it
  was generated mindlessly *and* pushed on someone who did not ask for it. The
  discriminating question is not "was an LLM involved", it is whether the text has
  a reason to exist.
- **Why it matters here:** a post that reads as mass produced is not argued with,
  it is filed away. The cost is not the discussion, it is the author's
  credibility.
- **What the gate blocks:** filler openers, brochure vocabulary ("revolutionary",
  "unlock the potential"), final summaries, courtesy closers, uniformly dense
  paragraphs.
- **Anti-correlation:** detectors work on stylometry and the most convenient
  feature is recurrence. Irregularity, specificity and friction (an opinion, an
  inconvenient number, a name) are what a generator does not produce on its own.

## 10. Images are the last priority

- **Decided by:** Human, verbatim: *"l'immagine associata, è l'ultima priorità"*.
- **Why:** no image-generation backend is configured, and a post with correct
  claims and no picture is worth more than the reverse. Adding an image stage
  before the text stage is solid would be building the easy half first.

## 11. Research in English, post in Italian

- **Decided by:** Agent, accepted.
- **Why:** coverage. Sources with usable figures on these topics are mostly
  English. The output is read by an Italian IT audience, so the post is Italian
  and the queries are not.

## 12. Known limitation, not a decision: `web_extract`

- `web.extract_backend` is set to `ddgs` in `~/.hermes/config.yaml`, and `ddgs` is
  a search-only backend, so `web_extract` fails with "cannot extract URL content".
  The native `web_search` returns enough page text to work from, so the pipeline
  works around it.
- **Fix when PDFs need extracting:** set `web.extract_backend` to `exa`,
  `tavily`, `firecrawl`, `keenable` or `parallel`.

## 13. This repo is the single source of truth for the skills it owns

- **Decided by:** Agent, under the author's constraint: *"deve essere una
  soluzione trasparente senza duplicati"*.
- **Choice:** the two skills written for this project (`linkedin-post`,
  `comedic-voice`) live in `skills/` in this repo. The agent profile points at
  them with symlinks:

      ln -s "$PWD/skills/"* ~/.hermes/skills/

- **Why:** a vendored copy in the repo plus the live copy in the profile is the
  same content twice, and the two drift. The symlink keeps one copy on disk and
  makes the repo the origin.
- **Verified, not assumed:** the Hermes skill loader follows symlinked skill
  directories. The two skills moved out of the profile and still report as
  `local` / `enabled`.
- **Rejected: repo-local `.hermes/skills` plus `hermes skills trust`.** It is the
  native mechanism, but those skills only load while the working directory is
  inside the project, and these are used from wherever the author happens to be.
- **Rejected: vendoring copies.** Duplication plus drift, which is what the
  constraint forbids.
- **Ceiling:** the symlink targets are absolute, so moving the repo breaks them.
  Fix: delete the dangling links and run the command above again.

## 14. `humanizer` is declared as a dependency, not vendored

- **Decided by:** Agent, same constraint.
- **Choice:** the repo contains no copy of `humanizer`. The README names its
  origin, version and license, and the pipeline requires it installed.
- **Why:** it is third party, MIT, and registered in the agent's skill registry
  (reported as `builtin`), which tracks its version and updates. Copying it here
  would duplicate it, detach it from upstream, and stop `hermes skills update`
  from maintaining it.

## 15. Attribution

- `linkedin-post`, `comedic-voice`, `check_post.py`, `lnkd.py`: original work,
  MIT, no third-party code.
- `humanizer`: third party, MIT, by `blader` (github.com/blader/humanizer),
  required by step 4 of the pipeline. Not redistributed in this repo. Not
  modified.
- **The banned-pattern list in `check_post.py` is a re-implementation in regular
  expressions** of the AI-writing tells catalogued in Wikipedia *Signs of AI
  writing*, the same catalogue `humanizer` implements. No code was copied; the
  rules were rewritten. Recorded because the list is derived from that source.
- The humor and tone rules in `comedic-voice` summarise published research, cited
  in that skill's own Sources section. Summaries, not reproductions.

## 16. One language for the tree: English, except what is Italian by design

- **Decided by:** Human, verbatim: *"aggiorna quello che è rimasto appeso e
  traducilo in inglese"*.
- **Choice:** every artifact in the committed tree is English: README, this file,
  code comments, docstrings, printed output, `--help`, and the instructions of
  both skills. Italian survives in exactly three places: the drafts under
  `posts/`, the closing-line log `posts/.closers.log`, and the banned-pattern
  regular expressions in `check_post.py`.
- **Why:** Italian is the *output* language of the product, not the language of
  the code. A reader who does not read Italian can still audit and reuse the gate
  and the skills. The parts left in Italian are data, not prose: the drafted text,
  the closing lines already published, and the patterns that must match Italian
  sentences to be useful at all.
- **Why the Italian survives at all:** it is not a leftover waiting to be
  translated, it is the chosen working language of the output. The author's
  reason, verbatim: *"l'italiano è stato scelto perché rende di più i concetti e
  per mia necessità mi da uno spunto in più di espressione"*. It carries the
  concepts better, and it hands him one more cue to express himself. Translating
  the drafts into English to look tidy would cost exactly the thing the project
  exists for.
- **Kept as quotes:** the verbatim author quotes in this file stay in Italian,
  marked as quotes. They are the record of what was asked; translating them would
  forge it.
- **Rejected: translating the example draft.** `posts/2026-11-25-*.md` is a real
  draft written for an Italian audience. Its value as an example is that it is
  genuine, and a translated fake would be worth less.

## 17. The draft ships an image prompt, not an image

- **Decided by:** Human, verbatim: *"l'agente quando mi risponde al comando con cui
  lo invoco mi deve andare dare un prompt da usare per generare immagini inerenti
  al post"*, plus *"lascia anche un .md per gli agenti in cui gli spieghi come
  usarlo e spiegalo anche nella facciata della repo"*.
- **Choice:** every draft ends with an `## Image prompt` block — the prompt (one
  indented line, English), the alt text (Italian, max 120 characters) and the
  aspect. `check_post.py` refuses a draft without it. The prompt is written, the
  image is not generated.
- **Reconciliation with §10:** §10 said images are the last priority and no image
  backend is configured here. Both still hold. What changed is that the cheap half
  of the image stage is now mechanical: the prompt travels into whatever tool the
  author picks, so the choice of model, licence and look stays his.
- **Why English for the prompt, Italian for the alt text:** image models are
  trained on English captions. The alt text is read aloud to an Italian audience,
  on an Italian post, so it is Italian.
- **Why a fixed house style:** coherence across posts comes from the constant part
  (medium, palette, light, framing, what is absent, mood), not from a long prompt.
  Only the subject changes per post. The table lives in `IMAGE-PROMPTS.md`; change
  it there to re-brand the whole set.
- **Why 4:5:** it is the tallest ratio LinkedIn accepts (3:1 to 4:5, 1080 px
  recommended width, 5 MB per photo), so it fills the most of the mobile feed, and
  a wider image is centred and cropped by LinkedIn anyway.
- **Rejected: a separate skill for the image prompt.** A second procedure to keep
  in sync with the voice rules, for one extra step in the same pipeline.
- **Rejected: `image_prompt:` in the frontmatter.** Frontmatter is machine data and
  this block is meant to be read and copied by hand. Keeping it out of the post
  text also means it cannot be pasted into LinkedIn by accident.
- **Gate details:** heading, at least 25 words in the indented line, alt text
  within 120 characters, accepted aspect. `closer_of()` cuts the body at that
  heading, so the image prompt can never be read as the closing line.
- **Not verified:** no image was generated from these prompts on this machine —
  there is no backend. The prompt structure is sourced in `IMAGE-PROMPTS.md`, and
  the LinkedIn limits come from LinkedIn's help pages read through third-party
  guides, because `web_extract` is down (§12).

## 18. One search key (Tavily) for both search and extract, keyless fallback kept

- **Decided by:** Joint. The author asked for "the best solution" and a guide to
  set it up; the choice of a single provider is the agent's proposal, accepted.
- **Choice:** `lnkd.py` gets a `search()` dispatcher. With `TAVILY_API_KEY` set it
  uses Tavily for search and, in one batched call, for full-text extract. With no
  key it keeps the keyless DuckDuckGo path. The Hermes skill path is unchanged and
  stays keyless; its `web_extract` is documented to run against
  `web.extract_backend: tavily` in the agent's `config.yaml`.
- **Why one provider:** Tavily does search *and* extract under a single key, so one
  signup unblocks the whole research stage. A search-only provider would leave the
  extract half blocked (§12). 1000 calls/month free is more than this pipeline uses.
- **Why the keyless fallback stays (not deleted):** the repo must keep working for
  a reader who has no key. Deleting the fallback would trade one soft failure
  (blocked keyless search) for a hard one (it cannot even try). It is also the
  author's rule for this project: never remove the working path to add the new one.
- **Rejected: vendorizing a search library.** The standard library does the HTTP;
  adding a dependency for two POSTs is cost without benefit.
- **Rejected: Brave/Serper.** Search-only in the shape this uses, so they unblock
  half the stage. Listed as alternatives in the old note; superseded by the
  single-key option.
- **Not verified:** the keyed path was not exercised end to end here — no key was
  configured during the change. Offline checks only: `py_compile` and the
  `search()` branch. Live verification needs the author's key in `.env`.

