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

P_WRITER = """You are a LinkedIn ghostwriter. Write in Italian, first person, dry and
concrete tone, like a technical person with hands on the tools. No fluff,
no "in a world where", no decorative emoji, no hashtag clusters.

Structure:
- First line = hook (max 12 words, it has to stop the scroll).
- 3-6 SHORT paragraphs (1-3 sentences), separated by a blank line.
- Close with a practical takeaway or a blunt question.
- At the bottom, a "Fonti:" section (Italian for "Sources") with only the URLs actually used.

HARD RULES:
- Use ONLY facts contained in the SOURCES below. If a source is useless, do not cite it.
- Do NOT invent numbers, dates, names or statistics that are not in the sources.
- If the sources are not enough to support a claim, drop the claim."""


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


def ddg(query, n=4):
    """Keyless search via the DuckDuckGo html endpoint. ponytail: fragile if DDG
    changes its markup or blocks; upgrade path = keyed provider (Brave/Serper)."""
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

    print("1/3 generating the queries...", file=sys.stderr)
    qs = [l.strip(" -•\t") for l in llm([{"role": "user", "content": P_QUERIES.format(seed=a.seed, n=a.n)}],
                                        a.model, 0.3, 300).splitlines() if l.strip()][:a.n]
    if not qs:
        sys.exit("no query generated")

    print("2/3 collecting the sources...", file=sys.stderr)
    srcs, seen = [], set()
    for q in qs:
        for r in ddg(q, 3):
            if r["url"] in seen:
                continue
            seen.add(r["url"])
            txt = fetch(r["url"])
            if txt and len(txt) > 400:
                srcs.append(r | {"text": txt, "query": q})
            if len(srcs) >= a.n:
                break
        if len(srcs) >= a.n:
            break
    if not srcs:
        sys.exit("no source collected — network or search down")

    blocks = "\n\n".join(f"### SOURCE {i+1}: {s['url']}\n{s['text']}" for i, s in enumerate(srcs))
    print(f"3/3 writing the post ({len(srcs)} sources)...", file=sys.stderr)
    post = llm([{"role": "system", "content": P_WRITER},
                {"role": "user", "content": f"AUTHOR'S THOUGHT:\n{a.seed}\n\nSOURCES:\n{blocks}"}],
                a.model, 0.7, 1600)

    os.makedirs(a.out, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", a.seed.lower())[:40].strip("-")
    path = os.path.join(a.out, f"{datetime.date.today()}-{slug}.md")
    open(path, "w", encoding="utf-8").write(
        f"---\ndate: {datetime.date.today()}\nstatus: draft\n"
        f"model: {a.model}\nsources: {len(srcs)}\n---\n\n{post}\n")
    print("\n" + "═" * 60 + f"\n{post}\n" + "═" * 60)
    print(f"\ndraft saved: {path}", file=sys.stderr)


if __name__ == "__main__":
    main()
