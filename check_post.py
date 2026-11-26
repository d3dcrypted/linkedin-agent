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
copied from it. See DECISIONS.md section 15. This file is MIT.

The two rules about AI are not in tension, they are different in kind: the banned
patterns remove the FORM that makes text read as generated, the disclosure states
the FACT that a machine assembled it. A post can be free of every tell and still
owe the reader the second sentence, and a post that declares the AI and keeps the
tells is what the gate exists to stop. Removing the declaration to look less
generated would be the one use of this file that is dishonest. See DECISIONS.md 23."""
import difflib, glob, os, re, sys

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
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)
# The line pointing at the sources comment is boilerplate: it must not count as the closing line.
POINTER = re.compile(r"(?i)sources?\b[^.\n]*first comment\.?")

# The prompt's fixed block is the same in every draft, so a prompt carrying only that
# block says nothing about its own post. Telling the style apart from the subject means
# the gate has to know the style vocabulary: this is the one deliberate copy of the
# table in IMAGE-PROMPTS.md, keep it aligned when the house style changes.
HOUSE_WORDS = frozenset("""photo editorial still life desk matte grey white wall behind
soft diffused light left lens shallow depth field subject centre empty space right slate
palette amber accent calm slightly dry text logos people ratio""".split())
MIN_SUBJECT_WORDS = 4  # the per-post part has to carry more than the style
# ponytail: plain token overlap, no stemming. Raise it if a false positive shows up.
SUBJECT_OVERLAP = 0.6


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


def content_words(text):
    return {w for w in re.findall(r"[a-z]{4,}", text.lower())}


def image_subject(image):
    """The words of a prompt that carry its post, rather than the house style."""
    m = IMAGE_PROMPT.search(image)
    return content_words(m.group(1)) - HOUSE_WORDS if m else set()


def image_coherence_errors(image, post, path):
    """The prompt has to come out of the post, not out of the house style alone.

    Three mechanical failures: a prompt that is the fixed block and nothing else, one
    whose object has nothing to do with the text, and one that reuses the object of an
    earlier draft in posts/ (the same picture in two posts is the signature the reused
    closing line is). See IMAGE-PROMPTS.md, "Deriving the object".
    """
    m = IMAGE_PROMPT.search(image)
    if not m:
        return []  # missing or unparsable block: image_prompt_errors reports that
    subject = content_words(m.group(1)) - HOUSE_WORDS
    if len(subject) < MIN_SUBJECT_WORDS:
        return [f"image prompt is house style only ({len(subject)} words carry the post, "
                f"need {MIN_SUBJECT_WORDS})"]
    if not subject & content_words(post):
        return ["image prompt shares no word with the post: make the post's own subject "
                "visible, not a generic desk object"]
    errs = []
    for other in sorted(glob.glob(os.path.join(ROOT, "posts", "*.md"))):
        if os.path.abspath(other) == os.path.abspath(path):
            continue
        theirs = image_subject(open(other, encoding="utf-8").read().split("---", 2)[-1])
        shared = subject & theirs
        if theirs and len(shared) / len(subject) > SUBJECT_OVERLAP:
            errs.append(f"image object reused ({len(shared)}/{len(subject)} words also in "
                        f"{os.path.basename(other)}): give this post its own object")
            break
    return errs


def closer_of(path):
    """The closing line: the last paragraph of the post, minus the pointer to the sources comment."""
    body = open(path, encoding="utf-8").read().split("---", 2)[-1]
    paras = [p.strip() for p in split_sections(body)[0].split("\n\n") if p.strip()]
    while paras and POINTER.fullmatch(paras[-1]):
        paras.pop()
    text = paras[-1] if paras else ""
    tail = POINTER.search(text)
    return text[:tail.start()].strip() if tail else text


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


def declared_sources(raw):
    """The URLs the draft frontmatter says it was written from, in order."""
    m = FRONTMATTER.match(raw.lstrip("\ufeff"))
    if not m:
        return []
    parts = re.split(r"(?m)^sources:\s*$", m.group(1), maxsplit=1)
    if len(parts) == 1:
        return []
    return [line.strip().lstrip("-").strip() for line in parts[1].splitlines()
            if line.strip().startswith("-")]


def _bare(url):
    """Url minus the punctuation that belongs to the sentence, not to the address.

    A closing bracket is stripped only when it is unbalanced: Wikipedia-style URLs
    end in one, and stripping it would make the two lists disagree for good.
    """
    url = url.rstrip(".,;]")
    return url[:-1] if url.endswith(")") and url.count("(") < url.count(")") else url


def citation_errors(raw, comment):
    """'Every fact has a source' as a boundary instead of a wish.

    The gate cannot read a claim and decide whether a source supports it: that
    judgement needs the source text and stays with the writer. What it can check is
    that the citations and the frontmatter agree, so no URL can appear in the first
    comment that no search returned, and no source can be recorded in the metadata
    and then dropped from the comment that is supposed to carry it.
    """
    declared, cited = declared_sources(raw), [u for u in URL.findall(comment)]
    if not declared:
        return ["frontmatter without a 'sources' list: the draft does not record what it was "
                "written from, so the citations cannot be checked against anything"]
    errs = [f"cited source not declared in the frontmatter: {url}" for url in cited
            if _bare(url) not in [_bare(d) for d in declared]]
    errs += [f"declared source not cited in the first comment: {url}" for url in declared
             if _bare(url) not in [_bare(c) for c in cited]]
    return errs


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
        errs += citation_errors(raw, comment)
    if not re.search(r"(?i)first comment", post):
        errs.append("post does not point to the sources in the first comment")
    if conflict := closer_conflict(path):
        errs.append(conflict)
    errs += image_prompt_errors(image) + image_coherence_errors(image, post, path)
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
    print("OK: English post within the limit, sources in the first comment, closing line not "
          "reused, image prompt derived from this post")
