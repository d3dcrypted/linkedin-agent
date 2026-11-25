# linkedin-agent

Turns one raw thought into a cited LinkedIn post draft. It does not publish:
the author approves the draft and posts it by hand.

The tool is deliberately small. One thought in, one markdown file out, with
every figure in the text traceable to a source.

## Status

Two parts, one of which works today.

**Working: a Hermes skill.** The pipeline used in practice is the `linkedin-post`
skill, which lives in this repo at `skills/linkedin-post/`. It uses the agent's
native web search tool, drafts with the `comedic-voice` skill
(`skills/comedic-voice/`), always passes the text through `humanizer`, and saves
the draft under `posts/`. Zero dependencies, zero keys.

This repo is the single source of truth for those two skills: they are not copied
into the agent profile, the profile points here with symlinks (see Installation).

**Not working: `lnkd.py`.** The standalone pipeline is complete (search, draft,
write to disk) but its search stage is blocked. From this VM, every keyless
search engine reachable (DDG html/lite, Bing, Mojeek, SearXNG, Brave, Ecosia)
answers with a challenge or HTTP 429, and letting the LLM guess URLs produced
hallucinated identifiers. To unblock it the repo needs a search key: set
`TAVILY_API_KEY` (or Brave/Serper) and wire it up in `ddg()`.

    python3 lnkd.py "my thought" --n 4      # requires an unblocked search backend

## How a post is built

    seed  ->  research  ->  draft  ->  humanize  ->  gate  ->  posts/*.md  ->  manual publish

1. **Seed.** The author's thought, captured verbatim. If it is missing, the tool
   asks for it instead of inventing a topic.
2. **Research.** Real web search for figures that support, quantify or contradict
   the thought. Nothing is cited from memory.
3. **Draft.** Written in Italian with the `comedic-voice` skill active (humor
   theory, stand-up structure, tone by register).
4. **Humanize.** Mandatory pass through the `humanizer` skill. Not optional.
5. **Gate.** `check_post.py` verifies the draft mechanically. It must exit 0.
6. **Publish.** The author copies the draft into LinkedIn. On publication the
   closing line is registered in `posts/.closers.log` so it can never be reused.

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
    skills/              the two skills this repo owns (linkedin-post, comedic-voice)
    lnkd.py              standalone pipeline, search stage blocked (see Status)
    posts/               generated drafts, markdown with frontmatter
    posts/.closers.log   closing lines already published, one per post. Commit it.

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
