---
name: linkedin-post
description: Turn one raw thought into a cited LinkedIn post draft.
version: 0.1.0
author: d3d (d3dcrypted), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [linkedin, content, research, writing, automation]
    related_skills: [grounded-citations, humanizer, comedic-voice]
---

# LinkedIn Post Skill

Turns one raw thought from the author into a LinkedIn post draft backed by real,
cited sources. Saves the draft to disk. **Does not publish** — publishing is
manual, the author copies and pastes.

## When to Use

- The user asks "write me a LinkedIn post about <thought>" — example (Italian,
  the working language): "fammi/scrivimi un post LinkedIn su <pensiero>"
- The user hands over a thought and asks to "back it up with reliable research" —
  example (Italian, the working language): "enfatizzarlo con ricerche attendibili"
- Don't use for: posts without requested research, short comments, automatic
  publishing (not supported: the LinkedIn API requires an approved app and
  violates the ToS if automated through a browser).

## Prerequisites

- `web_search` and `web_extract` (native). No key, no package.
- The author writes in Italian **by choice, not by habit**: it carries the
  concepts better and gives him one more cue to express himself. So the post is
  in Italian, the research in English (broader coverage).

## Procedure

1. **Capture the seed.** Take the thought **verbatim**. If it's missing or empty,
   ask for that alone, don't invent a topic. Criterion: you have the author's
   exact text.
2. **Research.** 3-5 targeted `web_search` calls (in English) to find data that
   supports, quantifies or contradicts the thought. Then `web_extract` on the
   2-4 best sources. Criterion: **≥3 facts, each with its own URL, and every URL
   actually extracted** — never cite from memory.
3. **Draft.** Write the post with the `comedic-voice` skill active and the voice
   rules below. One comic structure per beat, 1-2 real laughs in the text, the
   rest is tone. Criterion: every number, date or name has an **inline**
   micro-source `(Body, year)` inside the sentence that uses it; if a source
   doesn't hold up a claim, you drop the claim.
4. **Humanize — ALWAYS, not optional.** Apply the `humanizer` skill to the draft
   text. The post isn't saved before it has been through that. If the draft is
   well written, the pass changes little; if it has the classic tells, it removes
   them. **Exception: deliberate comic devices** (rule of three, understatement,
   callback, reversal) stay. The humanizer hits the pattern you chose on your
   own, not the device you picked by hand.
   Criterion: meaning intact and all inline micro-sources still there.
5. **Save.** `write_file` to `~/projects/linkedin-agent/posts/<YYYY-MM-DD>-<slug>.md`
   with frontmatter: `date`, `status: draft`, `seed`, `sources` (list of URLs).
   Criterion: the file exists.
6. **Image prompt.** Every draft carries one, in the same file. Turn the post's
   idea into one or two objects on the house-style desk described in
   `IMAGE-PROMPTS.md`, then append the block exactly as `AGENTS.md` formats it:
   the prompt in English on one indented line, the alt text in Italian at most
   120 characters, the aspect. Criterion: the block is in the file and
   `check_post.py` accepts it — it refuses a draft without one.
7. **Deliver and gate.** Run `python3 ~/projects/linkedin-agent/check_post.py <file>`:
   it must exit 0. It checks the image prompt block too, so a draft that skipped
   step 6 fails here. Print the post, the image prompt and the path. The author
   publishes by hand.
   **Once published**, log the closer used:
   `python3 ~/projects/linkedin-agent/check_post.py <file> --log`. That's what makes
   it impossible to repeat the same shape in the next post.
   Criterion: the check passes and the line exists in `posts/.closers.log`.

### Voice Rules (ghostwriter)

- First person, dry but **self-deprecating** tone: a technical person who knows
  their job and doesn't take themselves too seriously. Never formal, never
  motivational fluff, never "in a world where".
- **MAIN RULE — self-deprecating disclaimer, always.** The post states jokingly
  that the thought is a human's, but the text was put together by an AI. It goes
  **inside** the text, not as a legal note at the bottom.
  Register (adapt one, don't copy them all):
  - Example (Italian, the working language): "Pensato da un umano, montato da una AI. Il pensiero è mio, le virgole sono negoziabili."
  - Example (Italian, the working language): "Nessuna AI è stata maltrattata nella stesura di questo post."
  - Example (Italian, the working language): "Pensiero mio, dattilografia altrui. Il grafico prendetelo sul serio, il tono no."
  **Never the same shape twice**: the closer is rewritten every time, and it's the
  part `check_post.py` compares against `posts/.closers.log` (difflib ≥ 0.7).
  An identical sentence in every post is the easiest signature to correlate:
  anyone reading two posts recognises it, and any detector finds it.
- **SOURCES ALWAYS IN THE TEXT.** Every data point has its source **inline**, in
  minimal parenthetical form: `(BSI, 2025)` or `(Paligo, ott. 2026)`. Never a
  `Sources:` block at the bottom, never long URLs in the body — they steal space
  and scroll. The source sits inside the sentence that uses the data.
- First line = hook, max ~12 words, it has to stop the scroll.
- At least one catch phrase that says something serious with a straight face, but
  without taking itself too seriously.
- 3-6 short paragraphs (1-3 sentences), separated by a blank line.
- Close with a practical takeaway or a blunt question.
- No decorative emoji, no hashtag clusters.

## Quick Reference

    web_search(query="...", limit=3)      # search, in English
    web_extract(urls=[...])                # clean text from the sources
    write_file(path="~/projects/linkedin-agent/posts/...", content="...")
    # image prompt: block format in AGENTS.md, house style in IMAGE-PROMPTS.md

## Pitfalls

- **Never invent statistics.** The value of the pipeline is that the numbers are
  real and cited. A post without sources is worse than no post.
- The search backend sometimes fails a single call: retry once with a reworded
  query before declaring the failure.
- PDFs and pages behind a login can extract badly: prefer HTML articles/reports.
- **The image prompt is not optional, the image is.** No image backend is
  configured here, and generating is the author's call in whatever tool he picks:
  never generate the picture unasked. The prompt, though, ships with every draft.
  It costs nothing and it is the only part of the image stage that can be checked
  mechanically.

## Verification

- `python3 ~/projects/linkedin-agent/check_post.py <file>` exits 0: em dash, en
  dash, curly quotes, exclamation mark, emoji, shouting caps, "non è X, è Y"
  (Italian, the working language: "not X, it's Y"),
  slop phrases (Italian strings it matches: "nel mondo di oggi", "è importante
  notare che", "rivoluzionario", "in conclusione"), missing disclaimer, missing
  sources, reused closer: all blocked.
- The closer is not one of the shapes already used (`posts/.closers.log`).
- The `humanizer` skill was applied (step 4).
- Every number in the post has its inline micro-source `(Body, year)` — no
  `Sources:` block at the bottom.
- The post contains the self-deprecating "human thought / AI assembly" disclaimer.
- The draft file exists at the expected path with `status: draft`.
- The output is in Italian, first person, with no hashtag cluster.
- The draft ends with the `## Image prompt` block: one indented English line of at
  least 25 words, Italian alt text within 120 characters, an accepted aspect (4:5,
  1:1, 3:1, 1.91:1). `check_post.py` fails the draft if any of it is missing.
- The prompt follows the house style in `IMAGE-PROMPTS.md`, and it asks for no
  lettering, no logo and no recognizable person.
