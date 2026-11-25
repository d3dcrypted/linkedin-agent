# AGENTS.md

Instructions for any coding agent working in this repository — Hermes, Claude
Code, Cursor, Codex, a human with a shell. The repo is a LinkedIn post pipeline:
a raw thought goes in, a sourced and humanized draft comes out, plus an image
prompt for the post.

## What is where

    lnkd.py                  standalone CLI: seed -> research -> draft (stdlib only)
    check_post.py            the style gate; exits non-zero if a draft breaks the rules
    skills/linkedin-post/    the skill: the procedure, the voice rules, the template
    skills/comedic-voice/    humor theory used while drafting
    posts/                   the drafts (Italian) and posts/.closers.log
    IMAGE-PROMPTS.md         how to write and use the image prompt
    DECISIONS.md             why the repo is the way it is; read before changing a rule

## The two contracts

**1. A draft must pass the gate.**

    python3 check_post.py posts/<file>.md

It exits 0 or lists what is wrong. It blocks em dashes, en dashes, curly quotes,
exclamation marks, emoji, shouting caps, Italian slop and filler phrases, a
missing self-aware human/AI disclosure, a missing inline micro-source, a closing
line too similar to one already used, and a missing image prompt block (below).

**2. Every draft carries an image prompt.** Not optional, not "if the user asks".
The draft is not finished until the block is in the file, in this exact shape:

    ## Image prompt

        <one paragraph, 30-80 words, English>

    **Alt text** (Italian, max 120 characters): <one line>

    **Aspect** 4:5 (1080x1350) · **Negative** (only where the model has the field): blurry, watermark, text

The prompt is one single indented line so it is one copyable block. The gate
checks the heading, that the line has at least 25 words, that the alt text is
present and at most 120 characters, and that the aspect is one of the ratios
LinkedIn accepts.

## How to write the image prompt

Read `IMAGE-PROMPTS.md` — it is the full guide, with the fixed house style that
keeps the images coherent across posts, the prompt order, the LinkedIn sizes, and
the negative-prompt rules per model family. The short version:

1. Take the post's idea and turn it into **one or two physical objects on a desk**.
   Not a metaphor, not a diagram, not a person.
2. Keep the fixed block (medium, palette, light, framing, "absent" row, mood) as
   it is in the guide. Only the subject changes from post to post.
3. Write it in **English**: image models are trained on English captions. The alt
   text is in **Italian**, because the post is Italian and a screen reader will
   read it in Italian.
4. Ask for **4:5** explicitly — models compose for the ratio they are told.
5. Never put lettering in the image, never a real logo, never a recognizable face.
   Add the alt text and the AI disclosure to the post, not to the picture.

When you are the agent answering the invocation command, the image prompt block
is part of your answer: print it with the post and the file path, so the author
can copy it straight into whatever image model he uses.

## Rules that are not about style

- **The tree is English, the drafts are Italian.** README, code, comments,
  docstrings, skills, this file: English. `posts/`, `posts/.closers.log` and the
  patterns in `check_post.py`: Italian, because that is the language they police.
  Italian is the author's choice for the output, not a leftover.
- **Never commit a secret.** No token, key or password in the tree, not in a
  comment, not in an example. Before any push, scan the tracked files
  (`git grep` for `ghp_`, `github_pat_`, `sk-`, `AKIA`, `BEGIN ... PRIVATE KEY`)
  and check that nothing like `.env`, `.pem`, `.key` or `id_rsa` is tracked.
- **Never invent a fact.** Every number, date or name in a post has an inline
  micro-source `(Body, year)` inside the sentence that uses it. A source that does
  not hold up the claim means the claim is dropped.
- **Publishing is manual.** Nothing in this repo posts to LinkedIn; the API needs
  an approved app and browser automation breaks the ToS.
