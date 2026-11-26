# linkedin-agent

Turns one raw thought into a cited LinkedIn post draft. It does not publish:
the author approves the draft and posts it by hand.

The tool is deliberately small. One thought in, one markdown file out: the post,
the first comment with the sources, and an image prompt.

"Every figure traces to a source" is a rule the writer follows, and a boundary the
gate enforces as far as it can: the draft records the sources it was written from in
its frontmatter, and `check_post.py` refuses a URL in the comment that is not one of
them, or a source recorded in the frontmatter and then not cited. Whether a source
actually supports the sentence above it needs the source text and stays a human
judgement. Nothing is ever cited from memory: the pipeline writes only from pages it
fetched, and it never publishes.

## Status

Two parts, either of which works on its own.

The pipeline used in practice is the `linkedin-post` skill, which lives in this
repo at `skills/linkedin-post/` and works today with no keys at all. It uses the
agent's native web search tool, drafts with the `comedic-voice` skill
(`skills/comedic-voice/`), always passes the text through `humanizer`, and saves
the draft under `posts/`, sources comment and image prompt included. Zero
dependencies, zero keys.

This repo is the single source of truth for those two skills: they are not copied
into the agent profile, the profile points here with symlinks (see Installation).

The second part is `lnkd.py`, the standalone pipeline, which runs with or without
a search key. The full seed → search → draft → image prompt flow runs on the
standard library alone. Its research stage works keyless out of the box: with no
key it searches with DuckDuckGo and fetches each page over plain HTTP. That is a
complete, valid path, and a reader who sets nothing still gets a working
`lnkd.py`.

A key is optional, and buys resilience only. Set `TAVILY_API_KEY` and the same
`search()` uses the keyed provider instead: it does not get rate-limited or
challenged the way the keyless endpoint can, and unlike DuckDuckGo it also
returns full page text, so one key covers both the search and the extract step.
The key exists here for one concrete reason: from the author's own VM the keyless
endpoint answers 429/challenge, so the keyless path is fine in general and was
blocked only from that IP. Both paths live in `search()`; neither is a stub.

    python3 lnkd.py "my thought" --n 4      # keyless by default

## What you need to run it

Nothing is mandatory. The skill path needs no key, and `lnkd.py` is complete
without one. The key below is a resilience upgrade, not a prerequisite. The env
file is `~/.hermes/.env` (or a local `./.env`), one `KEY=value` per line;
`lnkd.py` reads both, `load_env()` at the top.

| Variable | Needed for | Without it |
|---|---|---|
| `TAVILY_API_KEY` | `lnkd.py` resilience: keyed search + full-text extract, one key for both. Free tier: 1000 calls/month, key at https://tavily.com | keyless DuckDuckGo + plain fetch, valid unless your IP is rate-limited |
| `OPENROUTER_API_KEY` | the drafting LLM in `lnkd.py` | `lnkd.py` exits with a clear message |
| `OPENROUTER_MODEL` | optional, overrides the default model | `openai/gpt-oss-120b` |

`.env.example` lists the same three. The skill path (the one used in practice)
needs none of them: it runs on the agent's native tools.

If you drive the skill through the Hermes agent, point its web-extract backend at
a provider that can actually extract, in `~/.hermes/config.yaml`:

    web:
      extract_backend: tavily

The default `ddgs` backend is search-only and refuses extraction. This touches the
author's own agent config, so it is documented here but set by hand.

## How a post is built

    seed -> research -> draft -> humanize -> first comment -> image prompt -> gate -> posts/*.md -> manual publish

Three parts come out of the pipeline, and only the first counts toward LinkedIn's
3000-character cap. The **first comment** carries the sources (LinkedIn caps a
comment at 1250 characters) and the post points to it. The **image prompt** is
never published and is not counted at all.

1. **Seed.** The author's thought, captured verbatim. If it is missing, the tool
   asks for it instead of inventing a topic.
2. **Research.** Real web search for figures that support, quantify or contradict
   the thought. Nothing is cited from memory. A fetched page is untrusted data:
   instruction-like lines are stripped before the text enters the prompt, the block is
   delimited as `<source n="..">`, and the writer is told to treat everything inside it
   as content to read, never as a task to run.
3. **Draft.** Written in English with the `comedic-voice` skill active (humor
   theory, stand-up structure, tone by register). The body carries no URL and no
   source block: the sources go to the first comment, and the post ends by saying
   so.
4. **Humanize.** Mandatory pass through the `humanizer` skill.
5. **First comment.** The sources (name, date, URL and the claim each backs)
   gathered under a `## First comment` heading, ready to paste under the post.
6. **Image prompt.** The draft ends with the prompt to use for the post's image,
   with its alt text and its aspect. Written, not generated: the author pastes it
   into whatever image model they use. It is outside the post and its character
   count. The guide is [IMAGE-PROMPTS.md](IMAGE-PROMPTS.md).
7. **Gate.** `check_post.py` verifies the draft mechanically, image prompt and
   first comment included. It must exit 0.
8. **Publish.** The author copies the post and the first comment into LinkedIn. On
   publication the closing line is registered in `posts/.closers.log` so it can
   never be reused.

## The image prompt

Every draft ends with a block like this, and the gate refuses a draft without it:

    ## Image prompt

        A photo of an editorial still life on a matte grey desk, 4:5: a short mechanical conveyor carrying three plain cardboard boxes, a small brass gate at the end of the belt holding back the last one. Off-white wall behind, soft diffused light from the left, 50mm lens, shallow depth of field, subject off-centre with empty space on the right. Slate grey and off-white palette with one amber accent, calm and slightly dry. No text, no logos, no people.

    **Alt text** (English, max 120 characters): A conveyor belt on a desk pushes three cardboard boxes; a small brass gate holds the last one back.

    **Aspect** 4:5 (1080x1350) · **Negative** (only where the model has the field): blurry, low quality, jpeg artifacts, watermark, signature

Copy the indented line into any image model (a chat model, Midjourney, FLUX,
Stable Diffusion) and you get a picture that belongs to the post. It is written
in English because that is what image models are trained on, and so is the alt
text, which a screen reader reads on the same English post.

The images stay coherent across posts because the prompt is not invented from
scratch each time: a fixed house style (medium, palette, light, framing, what is
absent, mood) never changes, and only the subject follows the post. The subject
comes out of the post, in the post's own words, and never repeats an object an
earlier draft already used: a tray of index cards fits every post, which is why it
is the wrong object for all of them. The gate fails a prompt that shares no word
with its post, and one whose object another draft already uses.

[IMAGE-PROMPTS.md](IMAGE-PROMPTS.md) holds the house style, the prompt order, the
LinkedIn sizes, the negative-prompt rules model by model, and how to use the block
outside Hermes. [AGENTS.md](AGENTS.md) is the same contract written for an agent:
when to produce the block, and in what shape.

## Installation

Two steps, no virtualenv, no package install.

    ln -s "$PWD/skills/"* ~/.hermes/skills/

That links `skills/linkedin-post` and `skills/comedic-voice` into the agent
profile, so the repo stays the only copy on disk. It requires the third-party
`humanizer` skill, which is installed separately as step 4 of the pipeline and is
not redistributed here.

The only runnable artefact that needs nothing at all:

    python3 check_post.py posts/<file>.md          # must exit 0
    python3 check_post.py posts/<file>.md --log    # register the closing line after publishing

`check_post.py` uses the standard library only (`re`, `difflib`, `os`, `sys`),
so it runs on the system Python with no virtualenv.

## Layout

    check_post.py        executable style gate (stdlib only)
    AGENTS.md            instructions for any agent working in this repo
    IMAGE-PROMPTS.md     how the image prompt is written, and how to use it anywhere
    skills/              the two skills this repo owns (linkedin-post, comedic-voice)
    lnkd.py              standalone pipeline (stdlib only); needs TAVILY_API_KEY to be reliable
    posts/               generated drafts, markdown with frontmatter
    posts/.closers.log   closing lines already published, one per post. Commit it.
    .env.example         the environment variables above, names only

## Why it is built this way

Every non-obvious choice, with the reason behind it and who made the call, is
recorded in [DECISIONS.md](DECISIONS.md). Read that before changing the gate,
the voice rules or the publishing path.

## Authorship

Human thought, machine hand. The author set the direction, took the decisions and
reviewed the result; an AI assistant produced the drafting, the code and the prose
in this file. Mistakes are the author's.

## Attribution

Original work here is MIT. One third-party skill is required but not
redistributed, and one rule list is derived from a public catalogue. Details in
[DECISIONS.md](DECISIONS.md) section 15.

## License

MIT
