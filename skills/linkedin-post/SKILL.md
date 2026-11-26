---
name: linkedin-post
description: Turn one raw thought into a cited LinkedIn post draft.
version: 0.2.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [linkedin, content, research, writing, automation]
    related_skills: [grounded-citations, humanizer, comedic-voice]
---

# LinkedIn Post Skill

Turns one raw thought from the author into an English LinkedIn post draft backed by
real, cited sources. Saves the draft to disk. **Does not publish** — publishing is
manual, the author copies and pastes.

A draft is three separate outputs, each a clean block to copy on its own:

1. **The post** — English, at most 3000 characters (LinkedIn's cap).
2. **The first comment** — the sources, pasted as the first comment under the post.
3. **The image prompt** — outside the post and outside its character count.

## When to Use

- The user asks "write me a LinkedIn post about <thought>" — e.g. "fammi/scrivimi un post LinkedIn su <pensiero>"
- The user hands over a thought and asks to "back it up with reliable research"
- Don't use for: posts without requested research, short comments, automatic
  publishing (not supported: the LinkedIn API requires an approved app and violates
  the ToS if automated through a browser).

## Prerequisites

- `web_search` and `web_extract` (native). No key, no package.
- The post is written in **English**, research included.

## Procedure

1. **Capture the seed.** Take the thought **verbatim**, in whatever language the
   author wrote it. If it's missing or empty, ask for that alone, don't invent a
   topic. Criterion: you have the author's exact text.
2. **Research.** 3-5 targeted `web_search` calls to find data that supports,
   quantifies or contradicts the thought. Then `web_extract` on the 2-4 best
   sources. Criterion: **≥3 facts, each with its own URL, and every URL actually
   extracted** — never cite from memory.
3. **Draft.** Write the post in **English**, with the `comedic-voice` skill active
   and the voice rules below. One comic structure per beat, 1-2 real laughs in the
   text, the rest is tone. Criterion: the post is in English and every number, date
   or name it uses is carried by a source collected in step 2 — the sources are not
   in the body, they go to the first comment in step 6.
4. **Humanize — ALWAYS, not optional.** Apply the `humanizer` skill to the draft
   text. The post isn't saved before it has been through that. If the draft is well
   written, the pass changes little; if it has the classic tells, it removes them.
   **Exception: deliberate comic devices** (rule of three, understatement, callback,
   reversal) stay. The humanizer hits the pattern you chose on your own, not the
   device you picked by hand.
   Criterion: meaning intact.
5. **Save.** `write_file` to `~/projects/linkedin-agent/posts/<YYYY-MM-DD>-<slug>.md`
   with frontmatter: `date`, `status: draft`, `seed` (verbatim), `sources` (list of
   URLs). Criterion: the file exists.
6. **First comment.** The post body carries **no URLs and no source block**. Under a
   `## First comment` heading, list the sources — name, date, URL, and the claim
   each one backs — so the block can be pasted as the first comment. End the post
   body with one short line that says the sources are in the first comment
   ("Sources in the first comment."). Criterion: the section exists, holds at least
   one URL, and the post points to it.
7. **Image prompt.** Every draft carries one, in the same file. Derive the object from
   the post: name its subject in one sentence, in the post's own words, and make that
   sentence visible as one or two objects on the house-style desk described in
   `IMAGE-PROMPTS.md` ("Deriving the object"). Never reuse an object another draft in
   `posts/` already uses: a generic writing prop (a tray of index cards, a notebook, a
   cup) fits every post, so it belongs to none. Then append the block exactly as
   `AGENTS.md` formats it: the prompt in English on one indented line, the alt text in
   English at most 120 characters, the aspect.
   **The prompt is outside the post**: it is not counted toward the character limit
   and it is never pasted into the post. Criterion: the block is in the file and
   `check_post.py` accepts it: it refuses a draft without one, one that is house
   style only, one whose prompt shares no word with the post, and one whose object
   repeats an object already used in `posts/`.
8. **Deliver and gate.** Run `python3 ~/projects/linkedin-agent/check_post.py <file>`:
   it must exit 0. Print the **three blocks separately**, each on its own so it can
   be copied in one go: the post text, the first comment with the sources, the image
   prompt. The author publishes by hand.
   **Once published**, log the closer used:
   `python3 ~/projects/linkedin-agent/check_post.py <file> --log`. That's what makes
   it impossible to repeat the same shape in the next post.
   Criterion: the check passes and the line exists in `posts/.closers.log`.

### Voice Rules (ghostwriter)

- First person, dry but **self-deprecating** tone: a technical person who knows their
  job and doesn't take themselves too seriously. Never formal, never motivational
  fluff, never "in a world where".
- **MAIN RULE — self-deprecating disclaimer, always.** The post states jokingly that
  the thought is a human's but the text was put together by an AI. It goes **inside**
  the text, not as a legal note at the bottom.
  Register (adapt one, don't copy them all):
  - "Thought by a human, assembled by an AI. The thinking is mine, the commas are negotiable."
  - "No AI was mistreated in the writing of this post."
  - "The thought is mine, the typing is someone else's. Take the work seriously, not the tone."
  **Never the same shape twice**: the closer is rewritten every time, and it's the part
  `check_post.py` compares against `posts/.closers.log` (difflib ≥ 0.7). An identical
  sentence in every post is the easiest signature to correlate: anyone reading two
  posts recognises it, and any detector finds it.
- **SOURCES IN THE FIRST COMMENT, ALWAYS.** The post body carries no URLs and no
  `Sources:` block. The sources travel in the first comment (step 6) and the post says
  so in one line at the end. This keeps the body clean and yields every character to
  the limit. A source that doesn't hold up a claim means the claim is dropped, never
  softened.
- First line = hook, max ~12 words, it has to stop the scroll. LinkedIn folds a post
  after roughly the first 210 characters, so the hook has to land before that.
- Length: LinkedIn's hard cap is **3000 characters**, and the gate fails anything
  longer. Stay well under it — landing inside the fold is a choice, the cap is a wall.
- At least one catch phrase that says something serious with a straight face, without
  taking itself too seriously.
- 3-6 short paragraphs (1-3 sentences), separated by a blank line.
- Close with a practical takeaway or a blunt question.
- No decorative emoji, no hashtag clusters.

## Quick Reference

    web_search(query="...", limit=3)          # search, in English
    web_extract(urls=[...])                   # clean text from the sources
    write_file(path="~/projects/linkedin-agent/posts/...", content="...")
    python3 ~/projects/linkedin-agent/check_post.py <file>   # must exit 0
    # image prompt: block format in AGENTS.md, house style in IMAGE-PROMPTS.md

## Pitfalls

- **Never invent statistics.** The value of the pipeline is that the numbers are real
  and cited. A post without sources is worse than no post.
- The search backend sometimes fails a single call: retry once with a reworded query
  before declaring the failure.
- PDFs and pages behind a login can extract badly: prefer HTML articles/reports.
- **The image prompt is not optional, the image is.** No image backend is configured
  here, and generating is the author's call in whatever tool they pick: never generate
  the picture unasked. The prompt, though, ships with every draft. It costs nothing,
  and it is outside the post: not part of the character count, not part of the body.
- **Three parts, not one.** Only the post text counts toward the 3000-character limit.
  The first comment has its own cap (1250) and the image prompt is never published.

## Verification

- `python3 ~/projects/linkedin-agent/check_post.py <file>` exits 0: em dash, en dash,
  curly quotes, exclamation mark, emoji, shouting caps, "it's not X, it's Y", AI slop
  and filler phrases, missing disclosure, missing first comment, missing source URL, a
  post over the limit, reused closer: all blocked.
- The post is in English, within 3000 characters, and points to the first comment.
- The first comment carries the source URLs (LinkedIn's comment cap: 1250 characters).
- No URL and no `Sources:` block inside the post body.
- The closer is not one of the shapes already used (`posts/.closers.log`).
- The `humanizer` skill was applied (step 4).
- The post contains the self-deprecating "human thought / AI assembly" disclaimer.
- The draft file exists at the expected path with `status: draft`.
- The three outputs are delivered as separate, individually copyable blocks.
- The draft ends with the `## Image prompt` block: one indented English line of at
  least 25 words, English alt text within 120 characters, an accepted aspect (4:5,
  1:1, 3:1, 1.91:1). `check_post.py` fails the draft if any of it is missing.
- The prompt follows the house style in `IMAGE-PROMPTS.md` and carries its own post: the
  object is derived from the post's subject, not a generic desk prop, and no other draft
  in `posts/` uses it. `check_post.py` fails a prompt with no word in common with the
  post, one that is house style only, and one whose object repeats another draft's.
- The prompt asks for no lettering, no logo and no recognizable person.
