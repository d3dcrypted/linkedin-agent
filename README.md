# linkedin-agent

Turns one raw thought into a cited LinkedIn post draft. It does not publish:
the author approves the draft and posts it by hand.

The tool is deliberately small. One thought in, one markdown file out, with
every figure in the text traceable to a source.

## Status

Two parts, either of which works on its own.

**Working today with zero keys: a Hermes skill.** The pipeline used in practice is
the `linkedin-post` skill, which lives in this repo at `skills/linkedin-post/`. It
uses the agent's native web search tool, drafts with the `comedic-voice` skill
(`skills/comedic-voice/`), always passes the text through `humanizer`, and saves
the draft under `posts/`, image prompt included. Zero dependencies, zero keys.

This repo is the single source of truth for those two skills: they are not copied
into the agent profile, the profile points here with symlinks (see Installation).

**Working with one search key: `lnkd.py`, the standalone pipeline.** The full
seed → search → draft → image prompt flow runs on the standard library alone.
Its research stage needs a search provider: set `TAVILY_API_KEY` and it uses
Tavily for both search and full-text extract (one key covers both). With no key
it falls back to keyless DuckDuckGo plus a plain HTTP fetch — which is what this
repo's author hit as blocked from his own VM, hence the key below.

    python3 lnkd.py "my thought" --n 4

## What you need to run it

Nothing is mandatory: the skill path needs no key. What makes `lnkd.py` reliable
is one key. In both cases the file is `~/.hermes/.env` (or a local `./.env`),
one `KEY=value` per line — `lnkd.py` reads both, `load_env()` at the top.

| Variable | Needed for | Without it |
|---|---|---|
| `TAVILY_API_KEY` | `lnkd.py` search + extract. Free tier: 1000 calls/month, key at https://tavily.com | keyless DuckDuckGo fallback, often blocked/429 |
| `OPENROUTER_API_KEY` | the drafting LLM in `lnkd.py` | `lnkd.py` exits with a clear message |
| `OPENROUTER_MODEL` | optional, overrides the default model | `openai/gpt-oss-120b` |

`.env.example` lists the same three. The skill path (the one used in practice)
needs none of them: it runs on the agent's native tools.

If you drive the skill through the Hermes agent, point its web-extract backend at
a provider that can actually extract — in `~/.hermes/config.yaml`:

    web:
      extract_backend: tavily

The default `ddgs` backend is search-only and refuses extraction. This touches the
author's own agent config, so it is documented here but set by hand.

## How a post is built

    seed  ->  research  ->  draft  ->  humanize  ->  image prompt  ->  gate  ->  posts/*.md  ->  manual publish

1. **Seed.** The author's thought, captured verbatim. If it is missing, the tool
   asks for it instead of inventing a topic.
2. **Research.** Real web search for figures that support, quantify or contradict
   the thought. Nothing is cited from memory.
3. **Draft.** Written in Italian with the `comedic-voice` skill active (humor
   theory, stand-up structure, tone by register). Italian is a choice, not a
   leftover: it carries the concepts better and gives the author one more cue to
   express himself.
4. **Humanize.** Mandatory pass through the `humanizer` skill. Not optional.
5. **Image prompt.** The draft ends with the prompt to use for the post's image,
   with its alt text and its aspect. Written, not generated: the author pastes it
   into whatever image model he uses. The guide is
   [IMAGE-PROMPTS.md](IMAGE-PROMPTS.md).
6. **Gate.** `check_post.py` verifies the draft mechanically, image prompt
   included. It must exit 0.
7. **Publish.** The author copies the draft into LinkedIn. On publication the
   closing line is registered in `posts/.closers.log` so it can never be reused.

## The image prompt

Every draft ends with a block like this, and the gate refuses a draft without it:

    ## Image prompt

        A photo of an editorial still life on a matte grey desk, 4:5: a short mechanical conveyor carrying three plain cardboard boxes, a small brass gate at the end of the belt holding back the last one. Off-white wall behind, soft diffused light from the left, 50mm lens, shallow depth of field, subject off-centre with empty space on the right. Slate grey and off-white palette with one amber accent, calm and slightly dry. No text, no logos, no people.

    **Alt text** (Italian, max 120 characters): Un nastro trasportatore su una scrivania con tre scatole di cartone: un cancelletto di ottone ferma l'ultima.

    **Aspect** 4:5 (1080x1350) · **Negative** (only where the model has the field): blurry, low quality, jpeg artifacts, watermark, signature

Copy the indented line into any image model — a chat model, Midjourney, FLUX,
Stable Diffusion — and you get a picture that belongs to the post. It is written
in English because that is what image models are trained on. The alt text is
Italian because the post is Italian and a screen reader will read it in Italian.

The images stay coherent across posts because the prompt is not invented from
scratch each time: a fixed house style (medium, palette, light, framing, what is
absent, mood) never changes, and only the subject follows the post.

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

## Attribution

Original work here is MIT. One third-party skill is required but not
redistributed, and one rule list is derived from a public catalogue. Details in
[DECISIONS.md](DECISIONS.md) section 15.

## License

MIT
