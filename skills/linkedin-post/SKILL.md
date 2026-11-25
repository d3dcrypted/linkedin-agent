---
name: linkedin-post
description: Turn one raw thought into a cited LinkedIn post draft.
version: 0.1.0
author: d3d (d3dcrypted), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [linkedin, content, research, writing, automation]
    related_skills: [grounded-citations, humanizer, comedic-voice]
---

# LinkedIn Post Skill

Trasforma un pensiero grezzo dell'autore in una bozza di post LinkedIn sostenuta
da fonti reali e citate. Salva la bozza su disco. **Non pubblica** — la
pubblicazione è manuale, l'autore copia e incolla.

## When to Use

- L'utente chiede "fammi/scrivimi un post LinkedIn su <pensiero>"
- L'utente passa un pensiero e chiede di "enfatizzarlo con ricerche attendibili"
- Don't use for: post senza ricerca richiesta, commenti brevi, pubblicazione
automatica (non supportata: l'API LinkedIn richiede app approvata e viola le
ToS se automatizzata via browser).

## Prerequisites

- `web_search` e `web_extract` (nativi). Nessuna chiave, nessun pacchetto.
- L'autore scrive in italiano: il post è in italiano, le ricerche in inglese
  (copertura maggiore).

## Procedure

1. **Cattura il seed.** Il pensiero va preso **verbatim**. Se manca o è vuoto,
   chiedi solo quello, senza inventare un tema. Criterio: hai il testo esatto
   dell'autore.
2. **Ricerca.** 3-5 `web_search` mirate (in inglese) per trovare dati che
   sostengano, quantifichino o contraddicano il pensiero. Poi `web_extract` sulle
   2-4 fonti migliori. Criterio: **≥3 fatti, ognuno con il suo URL, e ogni URL
   effettivamente estratto** — mai citare da memoria.
3. **Bozza.** Scrivi il post con la skill `comedic-voice` attiva e con le regole
   di voce qui sotto. Una sola struttura comica per beat, 1-2 risate vere nel
   testo, il resto e' tono. Criterio: ogni numero, data o nome ha una micro-fonte
   **inline** `(Ente, anno)` dentro la frase che lo usa; se una fonte non regge
   un'affermazione, elimini l'affermazione.
4. **Umanizza — SEMPRE, non opzionale.** Applica la skill `humanizer` al testo
   della bozza. Il post non si salva prima di essere passato da lì. Se la bozza
   è scritta bene, il passaggio cambia poco; se ha i tell classici, li toglie.
   **Eccezione: le figure comiche deliberate** (regola del tre, understatement,
   callback, ribaltamento) restano. L'humanizer colpisce il pattern che si è
   scelto da solo, non il dispositivo scelto a mano.
   Criterio: significato intatto e tutte le micro-fonti inline ancora presenti.
5. **Salva.** `write_file` in `~/projects/linkedin-agent/posts/<AAAA-MM-GG>-<slug>.md`
   con frontmatter: `date`, `status: draft`, `seed`, `sources` (lista URL). Poi
   lancia `python3 ~/projects/linkedin-agent/check_post.py <file>`: deve uscire 0.
   Criterio: il file esiste, il check passa.
6. **Consegna.** Stampa il post e il path. L'autore pubblica a mano. **A
   pubblicazione avvenuta**, registra la chiusura usata:
   `python3 ~/projects/linkedin-agent/check_post.py <file> --log`. È questo che rende
   impossibile ripetere la stessa forma nel post successivo.
   Criterio: la riga esiste in `posts/.closers.log`.

### Regole di voce (ghostwriter)

- Prima persona, tono asciutto ma **autoironico**: una persona tecnica che sa
  fare il suo lavoro e non si prende troppo sul serio. Mai formale, mai fuffa
  motivazionale, mai "in un mondo in cui".
- **REGOLA PRINCIPALE — disclaimer autoironico, sempre.** Il post dichiara in
  modo scherzoso che il pensiero è di un umano, ma il testo è stato messo
  insieme da una AI. Va **dentro** il testo, non come nota legale in fondo.
  Registro (adattane uno, non copiarli tutti):
  - "Pensato da un umano, montato da una AI. Il pensiero è mio, le virgole sono negoziabili."
  - "Nessuna AI è stata maltrattata nella stesura di questo post."
  - "Pensiero mio, dattilografia altrui. Il grafico prendetelo sul serio, il tono no."
  **Mai la stessa forma due volte**: la chiusura si riscrive ogni volta, ed è la
  parte che `check_post.py` confronta con `posts/.closers.log` (difflib ≥ 0.7).
  Una frase identica in ogni post è la firma più facile da correlare: chi legge
  due post la riconosce, e qualsiasi rilevatore la trova.
- **RISORSE SEMPRE NEL TESTO.** Ogni dato ha la sua fonte **inline**, in forma
  minima tra parentesi: `(BSI, 2025)` o `(Paligo, ott. 2026)`. Mai blocco
  `Fonti:` a fondo, mai URL lunghi nel corpo — rubano spazio e scroll. La fonte
  sta dentro la frase che usa il dato.
- Prima riga = hook, max ~12 parole, deve fermare lo scroll.
- Almeno una catch phrase che dice una cosa seria con faccia seria, ma senza
  prendersi troppo sul serio.
- 3-6 paragrafi brevi (1-3 frasi), separati da riga vuota.
- Chiudi con una takeaway pratica o una domanda secca.
- Niente emoji decorative, niente grappoli di hashtag.

## Quick Reference

    web_search(query="...", limit=3)      # ricerca, in inglese
    web_extract(urls=[...])                # testo pulito delle fonti
    write_file(path="~/projects/linkedin-agent/posts/...", content="...")

## Pitfalls

- **Mai inventare statistiche.** Il valore della pipeline è che i numeri sono
  veri e citati. Un post senza fonti è peggio di nessun post.
- Il backend di ricerca a volte fallisce una singola chiamata: ritenta una volta
  con una query riformulata prima di dichiarare il fallimento.
- PDF e pagine dietro login possono estrarre male: preferisci articoli/report HTML.
- Non generare immagini di default: è l'ultima priorità, fallo solo se richiesto.

## Verification

- `python3 ~/projects/linkedin-agent/check_post.py <file>` esce 0: em dash, en
  dash, virgolette curve, punto esclamativo, emoji, maiuscole urlate, "non è X,
  è Y", frasi da slop ("nel mondo di oggi", "è importante notare che",
  "rivoluzionario", "in conclusione"), disclaimer mancante, fonti mancanti,
  chiusura riusata: tutti bloccati.
- La chiusura non è una delle forme già usate (`posts/.closers.log`).
- Applicata la skill `humanizer` (passo 4).
- Ogni numero nel post ha la sua micro-fonte inline `(Ente, anno)` — nessun
  blocco `Fonti:` a fondo.
- Il post contiene il disclaimer autoironico "pensiero umano / assemblaggio AI".
- Il file di bozza esiste nel path atteso con `status: draft`.
- L'output è in italiano, prima persona, senza hashtag a grappolo.
