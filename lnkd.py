#!/usr/bin/env python3
"""lnkd — seed -> research -> LinkedIn post draft. Standard library only.

Usage:
    python3 lnkd.py "my raw thought" [--n 4] [--model X] [--out posts]

Publishes nothing. Prints the post and saves it under posts/. You copy it to LinkedIn.
"""
import argparse, datetime, html.parser, json, os, re, sys, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}

# ── prompts (tune them here) ─────────────────────────────────────────────────
P_QUERIES = """Given this thought from an IT/infrastructure/cybersecurity professional:
---
{seed}
---
Generate {n} short and specific web search queries to find recent data and
reliable sources that support, quantify or contradict that thought.
Rules: in English (wider coverage), no explanations, ONE query per line."""

P_WRITER = """You are a LinkedIn ghostwriter. Write in ENGLISH, first person, dry and
concrete tone, like a technical person with hands on the tools. No fluff,
no "in a world where", no decorative emoji, no hashtag clusters.

Structure:
- First line = hook (max 12 words, it has to stop the scroll).
- 3-6 SHORT paragraphs (1-3 sentences), separated by a blank line.
- Close with a practical takeaway or a blunt question.
- Then a short self-deprecating line: the thought is a human's, the text was
  assembled by an AI.
- Then, on its own last line: "Sources in the first comment."

HARD RULES:
- Use ONLY facts contained in the SOURCES below. If a source is useless, do not cite it.
- Do NOT invent numbers, dates, names or statistics that are not in the sources.
- Do NOT put URLs or a sources block in the body: the sources go in the first
  comment, added separately.
- No em dash, no en dash, no curly quotes, no exclamation mark. Stay under 3000 characters.
- If the sources are not enough to support a claim, drop the claim."""

P_IMAGE = """You write the image prompt for the LinkedIn post below. Full guide: IMAGE-PROMPTS.md.

HOUSE STYLE, keep it as it is: editorial still-life photograph on a desk; palette slate
grey, off-white and one amber accent; soft diffused light from the left, no hard shadows;
50mm lens, shallow depth of field, subject off-centre with generous empty space; no people,
no faces, no hands, no logos, no brand marks, no lettering; mood calm and slightly dry.

Turn the post's idea into ONE or TWO physical objects on that desk. Not a metaphor, not a
diagram, not a person.

Reply with exactly three lines, nothing else, no labels:
1. the prompt: ONE line, 30-80 words, English, starting with "A photo of", naming the 4:5 ratio
2. the alt text: English, at most 120 characters, describing only what is visible
3. the negative prompt: five to eight short English terms"""


def load_env():
    for p in (os.path.join(ROOT, ".env"), os.path.expanduser("~/.hermes/.env")):
        if not os.path.exists(p):
            continue
        for line in open(p, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def llm(messages, model, temperature=0.7, max_tokens=1600):
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        sys.exit("OPENROUTER_API_KEY missing (looked in ./.env and ~/.hermes/.env)")
    body = json.dumps({"model": model, "messages": messages,
                       "temperature": temperature, "max_tokens": max_tokens}).encode()
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=body,
                                 headers={**UA, "Authorization": f"Bearer {key}",
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)["choices"][0]["message"]["content"].strip()


class _Text(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.out, self.skip = [], 0
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "nav", "header", "footer"):
            self.skip += 1
    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "nav", "header", "footer") and self.skip:
            self.skip -= 1
        if tag in ("p", "br", "li", "h1", "h2", "h3"):
            self.out.append("\n")
    def handle_data(self, d):
        if not self.skip:
            self.out.append(d)


def to_text(raw):
    p = _Text()
    p.feed(raw)
    return re.sub(r"[ \t]+", " ", re.sub(r"\n{2,}", "\n", "".join(p.out))).strip()


TAVILY = "https://api.tavily.com"
# Tavily free tier does both search and full-text extract under ONE key, so a
# single TAVILY_API_KEY unblocks the whole research stage. Get one at
# https://tavily.com (1000 calls/month free). Nothing here is required: without
# the key the code falls back to keyless DuckDuckGo + a plain HTTP fetch.


def tavily_key():
    return os.environ.get("TAVILY_API_KEY")


def _tavily(path, payload):
    """One POST to the Tavily API. ponytail: no retry/backoff, add it if a 429 shows up."""
    req = urllib.request.Request(TAVILY + path, data=json.dumps(payload).encode(),
                                 headers={**UA, "Authorization": f"Bearer {tavily_key()}",
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def tavily_search(query, n=4):
    """Keyed search: URLs only, the full text is extracted in one batch after."""
    data = _tavily("/search", {"query": query, "max_results": max(1, min(n, 20)),
                               "search_depth": "basic"})
    return [{"url": r["url"]} for r in data.get("results", []) if r.get("url")]


def tavily_extract(urls):
    """Batch full-text extract. Returns {url: text}. One HTTP call for all URLs."""
    if not urls:
        return {}
    data = _tavily("/extract", {"urls": list(urls)})
    return {r["url"]: (r.get("raw_content") or "") for r in data.get("results", [])}


def search(query, n=4):
    """Keyed provider when TAVILY_API_KEY is set, keyless DuckDuckGo otherwise.
    ponytail: the keyless branch is intentional — it is what a reader without a
    key still gets, and what keeps the tool from depending on a paid account."""
    return tavily_search(query, n) if tavily_key() else ddg(query, n)


def ddg(query, n=4):
    """Keyless search via the DuckDuckGo html endpoint. ponytail: fragile if DDG
    changes its markup or blocks; upgrade path = keyed provider (TAVILY_API_KEY)."""
    url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
    raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20).read().decode("utf-8", "ignore")
    out = []
    for m in re.finditer(r'<a[^>]*class="result__a"[^>]*href="([^"]+)"', raw):
        link = html.unescape(m.group(1))
        if "uddg=" in link:
            link = urllib.parse.unquote(urllib.parse.parse_qs(urllib.parse.urlparse(link).query)["uddg"][0])
        if link.startswith("http") and link not in [o["url"] for o in out]:
            out.append({"url": link})
        if len(out) >= n:
            break
    return out


def fetch(url, limit=3500):
    try:
        raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20).read().decode("utf-8", "ignore")
        return to_text(raw)[:limit]
    except Exception as e:
        print(f"  ! fetch skipped {url} ({type(e).__name__})", file=sys.stderr)
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("seed", help="your raw thought")
    ap.add_argument("--n", type=int, default=4, help="number of sources (default 4)")
    ap.add_argument("--model", default=os.environ.get("OPENROUTER_MODEL", "openai/gpt-oss-120b"))
    ap.add_argument("--out", default=os.path.join(ROOT, "posts"))
    a = ap.parse_args()
    load_env()

    print("1/4 generating the queries...", file=sys.stderr)
    qs = [l.strip(" -•\t") for l in llm([{"role": "user", "content": P_QUERIES.format(seed=a.seed, n=a.n)}],
                                        a.model, 0.3, 300).splitlines() if l.strip()][:a.n]
    if not qs:
        sys.exit("no query generated")

    print("2/4 collecting the sources...", file=sys.stderr)
    cands, seen = [], set()
    for q in qs:
        for r in search(q, 3):
            if r["url"] in seen:
                continue
            seen.add(r["url"])
            cands.append(r | {"query": q})
    # One batched extract call when a key is set; a per-URL HTTP fetch otherwise.
    extracted = tavily_extract([r["url"] for r in cands]) if tavily_key() else {}
    srcs = []
    for r in cands:
        txt = extracted.get(r["url"]) or fetch(r["url"])
        if txt and len(txt) > 400:
            srcs.append(r | {"text": txt[:3500]})
        if len(srcs) >= a.n:
            break
    if not srcs:
        sys.exit("no source collected — search/fetch down. Set TAVILY_API_KEY to unblock "
                 "(see README, section Status).")

    blocks = "\n\n".join(f"### SOURCE {i+1}: {s['url']}\n{s['text']}" for i, s in enumerate(srcs))
    print(f"3/4 writing the post ({len(srcs)} sources)...", file=sys.stderr)
    post = llm([{"role": "system", "content": P_WRITER},
                {"role": "user", "content": f"AUTHOR'S THOUGHT:\n{a.seed}\n\nSOURCES:\n{blocks}"}],
                a.model, 0.7, 1600)

    print("4/4 writing the image prompt...", file=sys.stderr)
    # ponytail: no validation here, check_post.py is the gate.
    lines = [l.strip() for l in llm([{"role": "user", "content": P_IMAGE + "\n\nPOST:\n" + post}],
                                    a.model, 0.4, 400).splitlines() if l.strip()] + ["", "", ""]
    prompt, alt, neg = (re.sub(r"^\d[.)]\s*", "", l) for l in lines[:3])
    comment = "## First comment\n\nSources:\n" + "\n".join(f"- {s['url']}" for s in srcs)
    block = (f"\n{comment}\n\n## Image prompt\n\n    {prompt}\n\n"
             f"**Alt text** (English, max 120 characters): {alt}\n\n"
             f"**Aspect** 4:5 (1080x1350) · **Negative** (only where the model has the field): {neg}\n")

    os.makedirs(a.out, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", a.seed.lower())[:40].strip("-")
    path = os.path.join(a.out, f"{datetime.date.today()}-{slug}.md")
    fm_sources = "".join(f"  - {s['url']}\n" for s in srcs)
    open(path, "w", encoding="utf-8").write(
        f"---\ndate: {datetime.date.today()}\nstatus: draft\nmodel: {a.model}\n"
        f"seed: {json.dumps(a.seed, ensure_ascii=False)}\nsources:\n{fm_sources}---\n\n{post}\n{block}")
    print("\n" + "═" * 60 + f"\n{post}\n{block}" + "═" * 60)
    print(f"\ndraft saved: {path}", file=sys.stderr)


if __name__ == "__main__":
    main()
