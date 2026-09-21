# Chi si siede dove? – posti in macchina a.s. 2026/27

Pagina unica (`index.html`, HTML+CSS+JS inline, nessuna dipendenza) che mostra ai bambini dove sedersi in macchina.

## File
| File | A cosa serve |
|---|---|
| `index.html` | l'app; contiene incorporati calendario, `forzati.json` e `massime.json` |
| `forzati.json` | i giorni con assenti/forzati: usato solo **senza** database (vedi sotto) |
| `firebase-rules.json` | regole di sicurezza da incollare in Firebase Realtime Database |
| `carica_dati_privati.py` | carica in Firebase i nomi dei bambini (da `dati_privati.json`, che non è nel repository) |
| `dati_privati.esempio.json` | formato di `dati_privati.json` |
| `massime.json` | le massime del giorno per l'autista (una per data, a rotazione; aggiungine quante vuoi) |
| `aggiorna_dati.py` | ri-incorpora in `index.html` calendario, forzati e massime |
| `brief/` | materiale di partenza (calendario JSON/CSV, `genera_calendario.py`) |

## Pubblicare su GitHub Pages
1. Crea un repository su GitHub e collegalo: `git remote add origin <url>` poi `git push -u origin main`.
2. Repository → *Settings* → *Pages* → *Deploy from a branch* → `main` / `(root)`.
3. L'app sarà su `https://<utente>.github.io/<repo>/`.

## Giorni forzati / assenti
Nella vista Giorno, sulla stessa riga, ci sono due pulsanti:
- **Ricalcola con assenti**: scegli chi manca (anche più di uno, ma almeno un bambino deve restare). I posti lasciati liberi sono fissi:
  1 assente → libero il centro · 2 assenti → liberi centro e avanti (si usano i due dietro ai lati) · 3 assenti → si usa solo l'avanti.
- **Forza disposizione**: scegli tu chi sta in ogni posto (scegliendo un bambino già seduto altrove i due si scambiano).

In entrambi i casi il ricalcolo dei giorni successivi si applica subito e viene **salvato online** su Firebase (vedi sotto):
da quel momento tutti i dispositivi lo vedono, senza messaggi né modifiche a mano. Per annullare una forzatura basta riaprire il giorno
e premere **Ripristina** (o "Ripristina" nell'elenco *Giorni con assenti* in Statistiche): vale per tutti i dispositivi.
Se al momento del salvataggio sei offline, il giorno resta "solo su questo telefono" e da Statistiche puoi premere **Salva online** per riprovare.

## Salvataggio online (Firebase Realtime Database, gratis)
Nel database stanno: `/forzati/<data>` = `{assenti|disposizione, updatedAt}` (gli assenti come sigle O/L/A/M), `/ultimaModifica` (la data "agg." in alto)
e `/config/sigle` = i **nomi dei bambini** (vedi *Dati personali* qui sotto).
Ogni salvataggio scrive solo il suo giorno, quindi due telefoni non si sovrascrivono. L'app tiene una copia dell'ultimo scaricato per funzionare anche offline
e rilegge i dati ogni volta che torna in primo piano.

**Configurazione (una volta sola, ~10 minuti, piano Spark gratuito):**
1. Su <https://console.firebase.google.com> → *Aggiungi progetto* (senza Analytics).
2. *Build → Realtime Database → Crea database*, regione a scelta (es. `europe-west1`), modalità *bloccata*.
3. Scheda *Regole* → per iniziare senza password puoi incollare le regole della versione precedente (`.read`/`.write` a `true` con gli stessi controlli);
   per la versione con password segui *Accesso con password* qui sotto e incolla `firebase-rules.json`.
4. Copia l'URL del database (in cima alla scheda *Dati*, tipo `https://NOME-default-rtdb.europe-west1.firebasedatabase.app`)
   in `DB_URL` all'inizio dello script di `index.html`, alza `VERSIONE_APP`, poi commit e push.

Con `DB_URL` vuoto l'app funziona come prima: messaggio WhatsApp e `forzati.json` a mano (la sezione qui sotto).

### Accesso con password (Firebase Authentication)
L'app è pubblica su GitHub Pages, ma i dati dei forzati sono leggibili e scrivibili **solo con la password**. C'è un unico utente Firebase (email fissa `AUTH_EMAIL`,
password scelta da te) e le regole del database accettano solo lui. La password non è nel repository: sta in Firebase (cifrata) ed è richiesta all'apertura:
- con `?pwd=LaTuaPassword` nell'indirizzo (poi viene tolta dalla barra), oppure
- con la schermata "Accesso riservato" se non è nell'indirizzo; se è sbagliata compare "Non autorizzato: password errata".
Dopo un accesso riuscito il telefono se ne ricorda (un token, non la password) e non la chiede più. Se cambi la password in Firebase tutti i dispositivi la richiedono di nuovo.

**Attivazione (dopo la configurazione base sopra):**
1. Console Firebase → *Authentication → Inizia → Metodo di accesso → Email/password* → abilita.
2. *Authentication → Utenti → Aggiungi utente*: email `famiglia@calendarioauto.app` (o un'altra, purché uguale a `AUTH_EMAIL` in `index.html` e nelle regole) e la password scelta.
   Facoltativo: *Impostazioni → Azioni utente* → disattiva "Abilita creazione (registrazione)".
3. *Impostazioni progetto → Generali → Chiave API web*: copiala in `FB_API_KEY` in `index.html`.
   (Non è un segreto; volendo limitala al tuo dominio `*.github.io` in Google Cloud → *Credenziali* → *Restrizioni referrer HTTP*.)
4. Aggiorna le *Regole* del database con il nuovo `firebase-rules.json` e pubblica. **Fallo dopo** aver messo online l'app con `FB_API_KEY`,
   altrimenti la versione senza password non riesce più a leggere.
5. Apri l'app con `https://<utente>.github.io/<repo>/?pwd=LaTuaPassword` una volta per telefono (o digitala nel modulo).

Con `FB_API_KEY` vuoto l'app funziona senza password (le regole devono allora essere quelle pubbliche della versione precedente).

**Cosa protegge e cosa no:** la password protegge i dati online (nomi, forzati, assenti, ultima modifica) e impedisce a chiunque di scriverli. Il calendario di base
(giorni di scuola e rotazione dei posti, con i bambini indicati solo dalle sigle O/L/A/M) è invece dentro `index.html`, quindi resta visibile a chi legge il sorgente
del sito o del repository: la schermata di accesso nasconde l'app ma non quel file. Per nascondere anche quello serve un hosting con accesso protetto (es. Cloudflare Access).

### Dati personali (nomi dei bambini)
I nomi **non sono nel repository**: nel codice e nei file del calendario i bambini sono solo le sigle O, L, A, M e l'app li mostra con il nome dopo il login,
leggendolo da `/config/sigle`. Sul telefono ne resta una copia (come per i forzati) per funzionare offline. Per impostarli o cambiarli:
1. copia `dati_privati.esempio.json` in `dati_privati.json` (è ignorato da git) e scrivi i nomi;
2. pubblica le regole di `firebase-rules.json` (includono `/config`);
3. `FB_PASSWORD='la-password' python3 carica_dati_privati.py` (senza la variabile la password viene chiesta).
Finché i nomi non sono in Firebase, l'app mostra le sigle al posto dei nomi.
Con il piano gratuito Spark non ci sono costi: in caso di abusi il database viene solo bloccato per superamento quota.

**Modifica a mano:** dalla scheda *Dati* della console puoi aggiungere/togliere voci `forzati/AAAA-MM-GG` (con `assenti` = lista di sigle oppure `disposizione`, più `updatedAt` numerico).

### Senza database (come prima)
Il ricalcolo si applica subito su quel telefono e si apre WhatsApp con il messaggio pronto (scegli tu a chi inviarlo). Per renderlo definitivo su tutti i dispositivi:
1. copia la riga `{"data":"…","assenti":["M"]}` (oppure `{"data":"…","disposizione":"MAOL"}`) dal messaggio dentro l'elenco `forzati` di `forzati.json`
   (modificabile anche dal sito GitHub) e salva/commit;
2. da quel momento tutti i dispositivi leggono `forzati.json` e vedono i giorni successivi ricalcolati.
   Facoltativo: `python3 aggiorna_dati.py` per aggiornare anche la copia incorporata (usata aprendo il file direttamente).

Come si ricalcola: ogni giorno i bambini presenti occupano i posti in uso (regola sopra) e vengono messi su quelli in cui si sono seduti *meno volte*;
a parità non si ripete il posto del giorno prima, e a ulteriore parità si segue il calendario originale.
Senza forzature il risultato coincide esattamente con `brief/calendario_posti.json`.

## Storico dal 10 settembre
La scuola è iniziata il 10/9: i giorni 10, 11, 14 e 15/9 sono stati ricostruiti estendendo all'indietro lo stesso ciclo da 4 disposizioni
(un ciclo completo: ognuno ha provato ogni posto una volta prima del 16/9). Sono marcati `"ricostruito": true` in `calendario_posti.json`
e nell'app compare "Storico ricostruito". Se conosci le disposizioni reali di quei giorni, inseriscile in `forzati.json` con `disposizione`.
Il calendario si rigenera con `cd brief && python3 genera_calendario.py`, poi `python3 aggiorna_dati.py`.

## Barra in alto: data e versione
Sotto il titolo compare `A.s. 2026/27 · agg. GG/MM/AA · vX.Y.Z`.
- **agg.** è la data dell'ultima modifica dei forzati. Con il database è `/ultimaModifica`; senza, la pagina la legge dall'intestazione `Last-Modified`
  di `forzati.json` (su GitHub Pages) oppure usa la data che `aggiorna_dati.py` ha incorporato (aprendo `index.html` da disco).
- **versione**: costante `VERSIONE_APP` all'inizio dello script in `index.html`; va alzata a mano quando si modifica l'app
  (utile per capire se il telefono sta mostrando la versione aggiornata).

## Prove
Il parametro `?oggi=AAAA-MM-GG` simula un'altra data (es. `index.html?oggi=2026-11-02`); `&tab=mese` o `&tab=stat` aprono le altre sezioni.
