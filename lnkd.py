#!/usr/bin/env python3
"""lnkd — seed -> ricerca -> bozza post LinkedIn. Solo stdlib.

Uso:
    python3 lnkd.py "il mio pensiero grezzo" [--n 4] [--model X] [--out posts]

Non pubblica nulla. Stampa il post e lo salva in posts/. Lo copi su LinkedIn.
"""
import argparse, datetime, html.parser, json, os, re, sys, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}

# ── prompt (tunali qui) ──────────────────────────────────────────────────────
P_QUERIES = """Dato questo pensiero di un professionista IT/infrastruttura/cybersecurity:
---
{seed}
---
Genera {n} query di ricerca web, brevi e specifiche, per trovare dati recenti e
fonti attendibili che sostengano, quantifichino o contraddicano questo pensiero.
Regole: in inglese (più copertura), niente spiegazioni, UNA query per riga."""

P_WRITER = """Sei un ghostwriter LinkedIn. Scrivi in italiano, prima persona, tono
asciutto e concreto da persona tecnica che ha le mani in pasta. Niente fuffa,
niente "in un mondo in cui", niente emoji decorative, niente hashtag a grappolo.

Struttura:
- Prima riga = hook (max 12 parole, deve far fermare lo scroll).
- 3-6 paragrafi BREVI (1-3 frasi), separati da riga vuota.
- Chiudi con una takeaway pratica o una domanda secca.
- In fondo, sezione "Fonti:" con solo gli URL effettivamente usati.

REGOLE DURE:
- Usa SOLO fatti presenti nelle FONTI qui sotto. Se una fonte non è utile, non citarla.
- NON inventare numeri, date, nomi o statistiche che non siano nelle fonti.
- Se le fonti non bastano a sostenere un'affermazione, ometti l'affermazione."""


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
        sys.exit("OPENROUTER_API_KEY assente (cercato in ./.env e ~/.hermes/.env)")
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
    """Ricerca keyless via endpoint html di DuckDuckGo. ponytail: fragile se DDG
    cambia markup o blocca; upgrade path = provider con chiave (Brave/Serper)."""
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
        print(f"  ! fetch saltato {url} ({type(e).__name__})", file=sys.stderr)
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("seed", help="il tuo pensiero grezzo")
    ap.add_argument("--n", type=int, default=4, help="numero di fonti (default 4)")
    ap.add_argument("--model", default=os.environ.get("OPENROUTER_MODEL", "openai/gpt-oss-120b"))
    ap.add_argument("--out", default=os.path.join(ROOT, "posts"))
    a = ap.parse_args()
    load_env()

    print("1/3 ricerco le query...", file=sys.stderr)
    qs = [l.strip(" -•\t") for l in llm([{"role": "user", "content": P_QUERIES.format(seed=a.seed, n=a.n)}],
                                        a.model, 0.3, 300).splitlines() if l.strip()][:a.n]
    if not qs:
        sys.exit("nessuna query generata")

    print("2/3 raccolgo le fonti...", file=sys.stderr)
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
        sys.exit("nessuna fonte raccolta — rete o ricerca giù")

    blocchi = "\n\n".join(f"### FONTE {i+1}: {s['url']}\n{s['text']}" for i, s in enumerate(srcs))
    print(f"3/3 scrivo il post ({len(srcs)} fonti)...", file=sys.stderr)
    post = llm([{"role": "system", "content": P_WRITER},
                {"role": "user", "content": f"PENSIERO DELL'AUTORE:\n{a.seed}\n\nFONTI:\n{blocchi}"}],
                a.model, 0.7, 1600)

    os.makedirs(a.out, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", a.seed.lower())[:40].strip("-")
    path = os.path.join(a.out, f"{datetime.date.today()}-{slug}.md")
    open(path, "w", encoding="utf-8").write(
        f"---\ndate: {datetime.date.today()}\nstatus: draft\n"
        f"model: {a.model}\nsources: {len(srcs)}\n---\n\n{post}\n")
    print("\n" + "═" * 60 + f"\n{post}\n" + "═" * 60)
    print(f"\nbozza salvata: {path}", file=sys.stderr)


if __name__ == "__main__":
    main()
