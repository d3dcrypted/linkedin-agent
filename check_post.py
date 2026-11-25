#!/usr/bin/env python3
"""Style gate for a LinkedIn draft. Enforces the rules of the linkedin-post skill.
Usage: python3 check_post.py posts/<file>.md
       python3 check_post.py posts/<file>.md --log   (after publishing)

Attribution: the banned patterns re-implement, as regular expressions, the
AI-writing tells catalogued in Wikipedia "Signs of AI writing", the same catalogue
the humanizer skill (MIT, github.com/blader/humanizer) implements. No code was
copied from it. See DECISIONS.md section 15. This file is MIT."""
import difflib, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(ROOT, "posts", ".closers.log")

DISCLAIMER = re.compile(r"(umano|uman[ao]).{0,80}(AI|intelligenza artificiale)", re.I | re.S)
BANNED = {
    "em dash": r"—",
    "en dash": r"–",
    "curly quotes": r"[“”‘’]",
    "not-X-but-Y": r"\bnon (?:è|e')\s+[^.,;]{1,60}?[,:]\s*(?:è|e')\b",
    "punchline ending": r"(?m)^(?:È|E'|Questa è|Questo è)[^.\n]{0,40}\.\s*$",
    "exclamation mark": r"!",
    "emoji": r"[\U0001F300-\U0001FAFF\u2600-\u27BF]",
    "shouting caps": r"\b[A-ZÀ-Ü]{5,}\b",
    "slop phrase": r"(?i)\b(?:nel mondo di oggi|al giorno d'oggi|in today's fast-paced|"
                   r"let'?s dive in|tuffiamoci dentro|game[- ]?changer|in the ever-evolving|"
                   r"panorama in continua evoluzione|unlock the potential|sblocca il potenziale|"
                   r"rivoluzionario|in conclusione|in sintesi,|key takeaways|"
                   r"punti chiave da portare a casa|non è solo .{1,40}, è)\b",
    "filler phrase": r"(?i)\b(?:è importante notare che|vale la pena sottolineare|"
                     r"come tutti sappiamo|it is worth noting|it'?s important to note)\b",
}


def closer_of(path):
    body = open(path, encoding="utf-8").read().split("---", 2)[-1]
    return body.strip().split("\n\n")[-1].strip()


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
    errs = [f"{name}: {m.findall(body)[:2]}" for name, pat in BANNED.items()
            for m in [re.compile(pat)] if m.search(body)]
    if not DISCLAIMER.search(body):
        errs.append("missing self-aware human/AI disclosure")
    cites = re.findall(r"\(([^()]{2,40}?,\s*(?:[a-z]{2,10}\.?\s*)?(?:19|20)\d{2})\)", body)
    if not cites:
        errs.append("no inline micro-source (Body, year)")
    if conflict := closer_conflict(path):
        errs.append(conflict)
    return errs, cites


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not args:
        sys.exit(__doc__)
    if "--log" in sys.argv:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(f"{os.path.basename(args[0])}\t{closer_of(args[0])}\n")
        print("closing line registered in posts/.closers.log")
        sys.exit(0)
    errs, cites = check(args[0])
    print(f"inline sources found: {len(cites)} -> {cites}")
    if errs:
        print("FAILED:\n  " + "\n  ".join(errs))
        sys.exit(1)
    print("OK: humanized, sources in the text, closing line not reused")
