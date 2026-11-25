#!/usr/bin/env python3
"""Style gate for a LinkedIn draft. Enforces the rules of the linkedin-post skill.
Usage: python3 check_post.py posts/<file>.md
       python3 check_post.py posts/<file>.md --log   (after publishing)

A draft is three parts: the post text (English, at most POST_MAX characters), the
first comment carrying the sources, and the image prompt. Only the post text counts
toward LinkedIn's limit; the first comment has its own, smaller limit; the image
prompt is never published and is not counted.

Attribution: the banned patterns re-implement, as regular expressions, the
AI-writing tells catalogued in Wikipedia "Signs of AI writing", the same catalogue
the humanizer skill (MIT, github.com/blader/humanizer) implements. No code was
copied from it. See DECISIONS.md section 15. This file is MIT."""
import difflib, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(ROOT, "posts", ".closers.log")

# LinkedIn limits, verified November 2026: post 3000 characters, comment 1250.
# The feed folds a post after roughly 210 characters, so the hook has to land early.
POST_MAX = 3000
COMMENT_MAX = 1250

DISCLAIMER = re.compile(r"\b(human|person)\b.{0,80}\b(AI|artificial intelligence|machine)\b", re.I | re.S)
BANNED = {
    "em dash": r"—",
    "en dash": r"–",
    "curly quotes": r"[“”‘’]",
    "not-X-but-Y": r"\b(?:it'?s|this is|that'?s)\s+not\s+[^.,;]{1,60}?[,:]\s*(?:it'?s|this is)\b",
    "punchline ending": r"(?m)^(?:It'?s|This is|That'?s)[^.\n]{0,40}\.\s*$",
    "exclamation mark": r"!",
    "emoji": r"[\U0001F300-\U0001FAFF\u2600-\u27BF]",
    "shouting caps": r"\b[A-Z]{5,}\b",
    "slop phrase": r"(?i)\b(?:in today'?s fast-paced|let'?s dive in|game[- ]?changer|"
                   r"in the ever-evolving|unlock the potential|revolutionary|"
                   r"in conclusion|key takeaways|it'?s not just .{1,40}, it'?s)\b",
    "filler phrase": r"(?i)\b(?:it is worth noting|it'?s important to note|"
                     r"as we all know|needless to say)\b",
}

# A draft ships a sources comment and an image prompt. See DECISIONS.md 20 and IMAGE-PROMPTS.md.
COMMENT_SECTION = re.compile(r"(?m)^##\s+First comment\s*$")
IMAGE_SECTION = re.compile(r"(?m)^##\s+Image prompt\s*$")
IMAGE_PROMPT = re.compile(r"(?m)^ {4}(\S.*)$")
ALT_TEXT = re.compile(r"(?m)^\*\*Alt text\*\*[^:]*:\s*(.+?)\s*$")
ASPECT = re.compile(r"Aspect\D{0,3}(4:5|1:1|3:1|1\.91:1)")
MIN_PROMPT_WORDS = 25
ALT_TEXT_MAX = 120  # LinkedIn's own limit: it cannot be edited after posting.
URL = re.compile(r"https?://\S+")


def split_sections(body):
    """(post, comment, image), each stripped; a missing section yields ''."""
    c, i = COMMENT_SECTION.search(body), IMAGE_SECTION.search(body)
    end_post = min(x.start() for x in (c, i) if x) if (c or i) else len(body)
    post = body[:end_post]
    comment = body[c.end():i.start()] if c and i else (body[c.end():] if c else "")
    image = body[i.end():] if i else ""
    return post.strip(), comment.strip(), image.lstrip("\n")  # keep the prompt's indent


def image_prompt_errors(image):
    if not image.strip():
        return ["missing '## Image prompt' section"]
    errs = []
    prompt = IMAGE_PROMPT.search(image)
    if not prompt or len(prompt.group(1).split()) < MIN_PROMPT_WORDS:
        errs.append(f"image prompt missing or under {MIN_PROMPT_WORDS} words (one line, indented 4 spaces)")
    alt = ALT_TEXT.search(image)
    if not alt:
        errs.append("image prompt without alt text")
    elif len(alt.group(1)) > ALT_TEXT_MAX:
        errs.append(f"alt text over {ALT_TEXT_MAX} characters ({len(alt.group(1))})")
    if not ASPECT.search(image):
        errs.append("image prompt without an accepted aspect (4:5, 1:1, 3:1, 1.91:1)")
    return errs


def closer_of(path):
    body = open(path, encoding="utf-8").read().split("---", 2)[-1]
    return split_sections(body)[0].split("\n\n")[-1].strip()


def closer_conflict(path, ratio=0.7):
    """A closing line too similar to one already used is a signature correlatable across posts."""
    # ponytail: 0.7 ratio on difflib; raise it if it starts producing false positives.
    if not os.path.exists(LOG):
        return None
    me, mine = os.path.basename(path), closer_of(path)
    for line in open(LOG, encoding="utf-8"):
        fn, _, past = line.rstrip("\n").partition("\t")
        if not past or fn == me:
            continue
        r = difflib.SequenceMatcher(None, mine, past).ratio()
        if r >= ratio:
            return f"closing line reused ({r:.0%} similar to {fn}): {past[:50]}"
    return None


def check(path):
    raw = open(path, encoding="utf-8").read()
    body = raw.split("---", 2)[2] if raw.startswith("---") else raw
    post, comment, image = split_sections(body)
    errs = [f"{name}: {m.findall(post)[:2]}" for name, pat in BANNED.items()
            for m in [re.compile(pat)] if m.search(post)]
    if not DISCLAIMER.search(post):
        errs.append("missing self-aware human/AI disclosure")
    if len(post) > POST_MAX:
        errs.append(f"post over {POST_MAX} characters ({len(post)})")
    if not comment:
        errs.append("missing '## First comment' section carrying the sources")
    else:
        if len(comment) > COMMENT_MAX:
            errs.append(f"first comment over {COMMENT_MAX} characters ({len(comment)})")
        if not URL.search(comment):
            errs.append("first comment without a source URL")
    if not re.search(r"(?i)first comment", post):
        errs.append("post does not point to the sources in the first comment")
    if conflict := closer_conflict(path):
        errs.append(conflict)
    errs += image_prompt_errors(image)
    return errs, post, comment, len(URL.findall(comment))


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not args:
        sys.exit(__doc__)
    if "--log" in sys.argv:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(f"{os.path.basename(args[0])}\t{closer_of(args[0])}\n")
        print("closing line registered in posts/.closers.log")
        sys.exit(0)
    errs, post, comment, nsrc = check(args[0])
    print(f"post: {len(post)}/{POST_MAX} chars · first comment: {len(comment)}/{COMMENT_MAX} chars · sources in comment: {nsrc}")
    if errs:
        print("FAILED:\n  " + "\n  ".join(errs))
        sys.exit(1)
    print("OK: English post within the limit, sources in the first comment, closing line not reused")
