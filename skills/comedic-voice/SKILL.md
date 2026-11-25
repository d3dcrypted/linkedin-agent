---
name: comedic-voice
description: Craft real irony, not cabaret. Stand-up structure for text.
version: 0.1.0
author: d3d (d3dcrypted), Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [writing, humor, irony, sarcasm, voice]
    related_skills: [humanizer, linkedin-post]
---

# Comedic Voice

Fa ridere **di mestiere**, non di improvvisazione. Stand-up scritto, non cabaret.
Un post che fa ridere una volta su dieci battute e' peggio di uno serio: il
lettore capisce che stai provando.

## When to Use

- Quando un testo deve risultare ironico, sarcastico o dissacrante, ma credibile.
- Quando serve alternare tono serio e tono comico nella stessa pagina.
- Don't use when: il contenuto e' una brutta notizia, un dato clinico, un
  messaggio di errore. Li' il tono e' piatto per scelta.

## La teoria (perche' funziona)

**Benign Violation Theory** (McGraw, Warren): l'umorismo scatta quando tre
condizioni valgono insieme: c'e' una violazione (qualcosa che stona con come il
mondo dovrebbe andare), la violazione e' percepita benigna, e le due percezioni
coesistono. Fallisce in due modi: troppo timida (nessuna violazione, nessuna
risata) o troppo spinta (violazione maligna, imbarazzo).

Tre leve per rendere benigna una violazione:
1. **Norme alternative**: la frase ha un secondo senso che regge (e' il
   meccanismo del doppio senso, ma anche della battuta tecnica).
2. **Distanza psicologica**: "la commedia e' tragedia piu' tempo". Un disastro
   di tre anni fa e' materiale, quello di ieri no.
3. **Adesione alla norma violata**: ride chi condivide la norma. Per questo il
   pubblico giusto e' quello che sa di cosa parli.

**Incongruity-resolution**: non e' l'incongruenza che fa ridere, e' la sua
*risoluzione*, il momento in cui il lettore capisce. Conseguenza pratica: il
setup deve essere abbastanza vago da permettere il ribaltamento, e la battuta
non si spiega mai.

**Ironia vs sarcasmo** (Partridge): l'ironia dice il contrario di cio' che
intende; il sarcasmo e' la sua versione intenzionale e critica, alternativa al
rimprovero diretto. Il sarcasmo pungente in un post pubblico si usa solo verso
se' stessi o verso la propria categoria, mai verso il lettore.

## Il mestiere (come si scrive)

Unita' minima: **premessa** (il tema), **setup** (crea l'attesa), **punchline**
(la ribalta), **tag** (estende la risata con una seconda battuta sullo stesso
setup).

Le 7 strutture. Usane **una** per beat, non tutte insieme:

| Struttura | Meccanismo |
|---|---|
| Misdirection | il setup punta a A, la punchline atterra su B |
| Regola del tre | due elementi coerenti, il terzo sfasa |
| Callback | riprendi una parola dell'apertura alla chiusura |
| Reversal | ribalti l'aspettativa su se' stessa (io sono il problema) |
| Analogia | accosti il tecnico a qualcosa di quotidiano |
| Esagerazione | porti il difetto a conseguenze assurdamente precise |
| Understatement | dici meno di quanto la situazione meriti |

Nel testo l'interruzione di riga **e'** il tempo. Una frase breve dopo una lunga
e' una punchline: non serve altro per marcare il beat.

Densita': **1-2 risate vere per testo**, non dieci. Il resto e' tono. In un post
la struttura giusta e' un *tight five* ridotto: apri con la battuta discreta,
chiudi con la migliore (mai aprirsi con la piu' forte).

## Anti-pattern (i tell del cabaret)

- Punto esclamativo, emoji, "LOL", maiuscole per ridere.
- Densita' cabaret: una battuta per frase. Fa rima con l'imbarazzo.
- Assurdita' senza premessa: e' il non-sequitur, non la battuta.
- Spiegare la battuta, o dichiarare che stai scherzando ("ovviamente", "si fa per dire").
- Battuta sui dati: il numero e' sacro, si puo' solo incorniciare. Mai farne la punchline.
- Pubblico sbagliato: la vittima e' sempre tu o la tua categoria, mai il lettore, mai chi e' piu' debole.
- Tono isterico: in testo vince il deadpan. Sotto-enuncia, non strillare.

## Tonalità

**Voce e tono non sono la stessa cosa.** La voce sono i tratti stabili che ti
rendono riconoscibile in ogni testo: lessico, contrazioni, lunghezza delle frasi,
ritmo. Il tono è l'atteggiamento verso il soggetto in quel momento. Analogia: la
voce è lo stile del musicista, il tono è l'umore del brano. Pratica: il tono
cambia da post a post, la voce no. Se cambia la voce, sembri un altro autore.

**Il tono si dichiara, non si allude.** In uno studio misurato su LLM (Sayem,
EJALS) le istruzioni stilistiche esplicite hanno avuto effetti più forti dei
segnali contestuali impliciti: prompt formali +137% di lunghezza delle frasi e
+185% di densità di termini tecnici; prompt emotivi fino a 7,19 marcatori emotivi
per 100 parole contro zero in condizione neutra. Tre manopole misurabili:
lunghezza frase, densità tecnica, marcatori emotivi.

**Tono per registro, non per aggettivi.** "Formale", "ironico", "diretto" sono
etichette vaghe e il modello ci infila quello che vuole. Il registro (Halliday)
ha tre assi specificabili:
- campo: di cosa si parla (tecnico-operativo, business, personale);
- tenore: il rapporto con chi legge (pari, esperto, venditore);
- modo: canale e forma (post breve, prosa scritta).
Caratterizzare il tono per registro batte le etichette sia in fedeltà al tono sia
in conservazione del significato.

**Mappa dei toni** (un tono per beat, non tutti insieme):

| Beat | Tono | Firme |
|---|---|---|
| Apertura | asciutto | frasi corte, zero aggettivi, zero segnali |
| Dati | piatto | frasi lunghe, densità tecnica alta, zero marcatori emotivi |
| Turn | ironico | frase breve dopo una lunga, understatement |
| Chiusura | asciutto | torna alla voce dell'apertura |

**Serio e ironico convivono solo se separati**: prima il fatto nudo, poi il
commento. Mai i due registri nella stessa frase, altrimenti il lettore non sa
cosa prendere sul serio. E il passaggio è il posto migliore per la battuta: la
serietà appena stabilita è il setup.

**Cambiare tono dentro il testo.** In un testo breve il tono non gira: un cambio
solo, ed è il turn. E il cambio deve avere una causa visibile, altrimenti il
lettore è disorientato, non divertito. Tre modi di farlo atterrare:
1. annunciarlo con una frase di transizione ("Qui la parte seria, perché serve");
2. prepararlo prima, mezzo-accennando il registro che arriva mentre sei ancora
   nell'altro (Catch-22 riprende gli stessi elementi, che diventano sempre più cupi);
3. mai farlo rientrare: il registro serio non si richiude con una battuta nella
   stessa frase.

Nota: se il post diventa audio, la tonalità si sposta sulla prosodia (controllo di
emozione e intensità a tre livelli: globale, frase, parola). Fuori scope finché il
prodotto è testo.

## Esempi di calibrazione

Buono (understatement + reversal, autore come bersaglio):
"Ho automatizzato il controllo qualita' del nostro codice. Il primo bug l'ha
trovato nell'automazione. Sto vincendo."

Cattivo (densita' cabaret, nessun bersaglio, spiega la battuta):
"Ho automatizzato TUTTO! Il codice e' un disastro! LOL! Ok, smetto di fare il
comico."

## AI Slop

**Definizione operativa** (Willison, deepfates): non tutto il testo AI è slop. Lo è
quando è generato senza testa **e** imposto a chi non l'ha chiesto. Wikipedia aggiunge il
contorno: riempitivo che privilegia velocità e quantità sulla sostanza, prodotto in
volume. Il discriminante non è "l'ho scritto con un LLM", è se il testo ha un motivo per
esistere.

**Il rischio concreto**: un post slop non viene contestato, viene archiviato. Non si
perde la discussione, si perde l'autore. Generato in serie non significa letto male,
significa non letto.

**Marcatori bloccati dal gate** (lista completa in Wikipedia:Signs of AI writing, di cui
la skill `humanizer` è la versione operativa):
- frasi di riempimento ("nel mondo di oggi", "è importante notare che", "in conclusione");
- chiusura a effetto, formule di cortesia finali;
- densità uniforme: paragrafi tutti lunghi uguali, nessuna asperità;
- lessico da brochure ("rivoluzionario", "sblocca il potenziale");
- struttura da elenco travestita da prosa.

**Rendere il post non correlabile.** I rilevatori vanno di stilometria (StyloAI, 31
feature) e la feature più comoda è la ricorrenza. Un testo identico a se stesso in ogni
post è il modo più rapido per farsi correlare: chi legge due post riconosce la firma, e
qualsiasi detector la trova. Quindi:
1. **Nessuna frase fissa, mai**, nemmeno il disclaimer. La semantica è fissata (pensiero
   umano, assemblaggio AI), la forma si riscrive ogni volta. `check_post.py` confronta la
   chiusura con quelle già usate (`posts/.closers.log`, similarità difflib ≥ 0.7) e blocca
   la ripetizione.
2. **Irregolarità**: varia la lunghezza dei paragrafi, non chiudere ogni sezione con una
   sintesi, lascia un dettaglio troppo specifico per essere generico. La specificità non
   si finge: è il residuo che un generatore non produce.
3. **Attrito**: un'opinione, un numero scomodo, un nome. Il testo piatto è la firma.

## Fonti

- McGraw & Warren, *Benign Violation Theory* (HuRL, Univ. of Colorado)
- *Incongruity-resolution*, ScIU, Indiana University, 2023
- Partridge, *Usage and Abusage*, citato in ACM CSUR, *Survey on Automatic Generation of Figurative Language*
- ACM CSUR, *Computational Humor Modeling: A Survey on the State of the Art*
- Haeusler, *Llama LOL* (few-shot come leva principale per il tono comico)
- Sayem, *Prompt Engineering and Stylistic Control in LLMs*, EJALS (tono esplicito vs implicito)
- Ouellette, *All Write Now* #17 (voce stabile, tono plasmabile)
- *Steering LLMs with Register Analysis for Arbitrary Style Transfer*, arXiv 2505.00679
- Halliday, registro: campo / tenore / modo
- *Nearest Neighbor LMs for Stylistic Controllable Generation*, arXiv 2210.15762
- Wikipedia, *AI slop* (Willison, deepfates; Merriam-Webster e ADS Word of the Year 2025)
- Wikipedia, *Signs of AI writing* (AISIGNS)
- *StyloAI*, arXiv 2405.10129 (31 feature stilometriche)
