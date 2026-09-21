#!/usr/bin/env python3
"""Incorpora in index.html i dati (cosi' la pagina funziona anche aperta direttamente da file).

  brief/calendario_posti.json  ->  <script id="dati-calendario">
  forzati.json                 ->  <script id="dati-forzati">   (copia di riserva: online la pagina legge forzati.json aggiornato)
  massime.json                 ->  <script id="dati-massime">   (massime del giorno per l'autista)

Uso:  python3 aggiorna_dati.py
Da rilanciare dopo aver rigenerato il calendario o modificato forzati.json.
Inoltre incorpora la data di modifica di forzati.json (mostrata come "agg." nella barra in alto).
"""
import json, re, sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SORGENTI = {
    "dati-calendario": ROOT / "brief" / "calendario_posti.json",
    "dati-forzati": ROOT / "forzati.json",
    "dati-massime": ROOT / "massime.json",
}

def compatto(path):
    dati = json.loads(path.read_text(encoding="utf-8"))          # fallisce subito se il JSON e' rotto
    # "</" dentro un <script> chiuderebbe il tag: lo si evita con l'escape JSON equivalente
    return json.dumps(dati, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

html_path = ROOT / "index.html"
html = html_path.read_text(encoding="utf-8")
for sid, path in SORGENTI.items():
    pattern = re.compile(r'(<script type="application/json" id="%s">)(.*?)(</script>)' % sid, re.S)
    if not pattern.search(html):
        sys.exit("Blocco <script id=\"%s\"> non trovato in index.html" % sid)
    html = pattern.sub(lambda m: m.group(1) + compatto(path) + m.group(3), html, count=1)
    print("incorporato", path.relative_to(ROOT))
# data di ultima modifica di forzati.json (mostrata come "agg." nella barra in alto; online la pagina usa Last-Modified)
modificato = datetime.fromtimestamp(SORGENTI["dati-forzati"].stat().st_mtime).date().isoformat()
html, n = re.subn(r'(<meta name="forzati-modificato" content=")[^"]*(">)', lambda m: m.group(1) + modificato + m.group(2), html)
if n != 1:
    sys.exit('<meta name="forzati-modificato"> non trovato in index.html')
print("forzati.json modificato il", modificato)
html_path.write_text(html, encoding="utf-8")
print("index.html aggiornato (%d KB)" % (len(html.encode("utf-8")) // 1024))
