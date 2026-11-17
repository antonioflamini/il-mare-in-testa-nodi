# Il Mare in Testa · Nodi

Il nodario di bordo della collana **Il Mare in Testa** di Antonio Flamini: i nodi che servono davvero in barca, in 3D realistico, passo passo, con la storia, il trucco del nostromo, la trappola d'esame e i quiz.

**App:** https://antonioflamini.github.io/il-mare-in-testa-nodi/ (funziona anche offline e si può installare sul telefono).

## Come funziona

- `tools/` — il **simulatore fisico della cima** (Python + NumPy). Ogni nodo è disegnato a mano come percorso (`knots_src.py`, `knots_more.py`) con la sequenza sopra/sotto degli incroci; il simulatore rilassa la cima senza compenetrazioni (la cima ha un diametro e non attraversa sé stessa né gli oggetti), poi la mette in tensione tirando i capi e salva i fotogrammi del serraggio.
  - `python bake.py` rigenera `app/data/geom.json` (tutti i nodi) — `python bake.py savoia gassa-damante` solo quelli indicati.
  - `python shot.py <nodo> <g> out.png` rende un fotogramma (serve per il libro e per i controlli); `python sheet.py out.png 1.35 nodo1 nodo2 …` fa un foglio di confronto.
- `app/` — l'app (HTML + three.js, nessuna compilazione): cima intrecciata con texture e rilievo procedurali, coperta in teak, oggetti di bordo (bitta, galloccia, anello, tientibene), passi sincronizzati con l'animazione, vista a specchio per i mancini, quiz e progressi.
- `.github/workflows/pages.yml` — pubblica `app/` su GitHub Pages a ogni modifica.

## Aggiungere un nodo

1. Disegna il percorso in `tools/knots_more.py` con `@knot` (vedi gli esempi: incroci con `flat(...)`, giri attorno agli oggetti con coordinate 3D).
2. `python bake.py <id>` e controlla con `python sheet.py`.
3. Aggiungi i testi in `app/data/knots.js` (passi con il punto dell'animazione `at`).

© 2026 Antonio Flamini. Testi, modelli 3D, codice e illustrazioni: tutti i diritti riservati.
