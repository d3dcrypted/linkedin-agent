# AGENTS.md

Instructions for any coding agent working in this repository — Hermes, Claude
Code, Cursor, Codex, a human with a shell. The repo is a LinkedIn post pipeline:
a raw thought goes in, a sourced and humanized draft comes out. Three parts come
out: the post (English, at most 3000 characters), the first comment carrying the
sources, and an image prompt for the post.

## What is where

    lnkd.py                  standalone CLI: seed -> research -> draft (stdlib only)
    check_post.py            the style gate; exits non-zero if a draft breaks the rules
    skills/linkedin-post/    the skill: the procedure, the voice rules, the template
    skills/comedic-voice/    humor theory used while drafting
    posts/                   the drafts (English) and posts/.closers.log
    IMAGE-PROMPTS.md         how to write and use the image prompt
    DECISIONS.md             why the repo is the way it is; read before changing a rule

## The two contracts

**1. A draft must pass the gate.**

    python3 check_post.py posts/<file>.md

It exits 0 or lists what is wrong. It blocks em dashes, en dashes, curly quotes,
exclamation marks, emoji, shouting caps, AI slop and filler phrases, a missing
self-aware human/AI disclosure, a missing first comment carrying the sources, a
post over LinkedIn's 3000-character limit, a closing line too similar to one
already used, and a missing image prompt block (below).

**2. Every draft carries an image prompt.** Not optional, not "if the user asks".
The draft is not finished until the block is in the file, in this exact shape:

    ## Image prompt

        <one paragraph, 30-80 words, English>

    **Alt text** (English, max 120 characters): <one line>

    **Aspect** 4:5 (1080x1350) · **Negative** (only where the model has the field): blurry, watermark, text

The prompt is one single indented line so it is one copyable block. The gate
checks the heading, that the line has at least 25 words, that the alt text is
present and at most 120 characters, and that the aspect is one of the ratios
LinkedIn accepts.

The post also ships a `## First comment` section: the sources (name, date, URL and
the claim each backs), meant to be pasted as the first comment under the post. The
body carries no URL and no source block, and ends with one line saying the sources
are in the first comment. The gate requires the section and that pointer line.

## How to write the image prompt

Read `IMAGE-PROMPTS.md` — it is the full guide, with the fixed house style that
keeps the images coherent across posts, the prompt order, the LinkedIn sizes, and
the negative-prompt rules per model family. The short version:

1. Take the post's idea and turn it into **one or two physical objects on a desk**.
   Not a metaphor, not a diagram, not a person.
2. Keep the fixed block (medium, palette, light, framing, "absent" row, mood) as
   it is in the guide. Only the subject changes from post to post.
3. Write it in **English**: image models are trained on English captions. The alt
   text is in **English** too, so a screen reader reads the post and its image in
   the same language.
4. Ask for **4:5** explicitly — models compose for the ratio they are told.
5. Never put lettering in the image, never a real logo, never a recognizable face.
   Add the alt text and the AI disclosure to the post, not to the picture.

When you are the agent answering the invocation command, the image prompt block
is part of your answer: print it with the post and the file path, and print the
three parts **separately** — post, first comment, image prompt — so each is one
copyable block. The image prompt is outside the post: it is not counted toward the
character limit and it is never pasted into LinkedIn.

## Rules that are not about style

- **The whole tree is English, drafts included.** README, code, comments,
  docstrings, skills, this file, `posts/`, `posts/.closers.log`, and the
  banned-pattern regular expressions in `check_post.py`: all English, because that
  is the language the posts are written and policed in.
- **Never commit a secret.** No token, key or password in the tree, not in a
  comment, not in an example. Before any push, scan the tracked files
  (`git grep` for `ghp_`, `github_pat_`, `sk-`, `AKIA`, `BEGIN ... PRIVATE KEY`)
  and check that nothing like `.env`, `.pem`, `.key` or `id_rsa` is tracked.
- **Never invent a fact.** Every number, date or name in a post is backed by a
  source collected in the research stage and listed in the first comment. A source
  that does not hold up the claim means the claim is dropped.
- **Publishing is manual.** Nothing in this repo posts to LinkedIn; the API needs
  an approved app and browser automation breaks the ToS.
