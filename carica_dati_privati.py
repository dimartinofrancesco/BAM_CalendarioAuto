#!/usr/bin/env python3
"""Carica in Firebase i dati personali che NON devono stare nel repository pubblico (i nomi dei bambini).

  dati_privati.json  ->  Realtime Database, nodo /config      (dati_privati.json e' ignorato da git: sta solo sul tuo computer)

Uso:
  FB_PASSWORD='la-password' python3 carica_dati_privati.py     (oppure senza variabile: la chiede)

Serve l'utente Firebase di famiglia (stessa password dell'app) e le regole di firebase-rules.json gia' pubblicate.
Indirizzo del database, chiave API ed email dell'utente sono letti da index.html.
"""
import getpass, json, os, re, sys, urllib.error, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
html = (ROOT / "index.html").read_text(encoding="utf-8")

def costante(nome):
    m = re.search(r"const %s = '([^']*)'" % nome, html)
    if not m or not m.group(1):
        sys.exit("%s non impostato in index.html" % nome)
    return m.group(1)

DB = costante("DB_URL").rstrip("/")
CHIAVE = costante("FB_API_KEY")
EMAIL = costante("AUTH_EMAIL")

privati = ROOT / "dati_privati.json"
if not privati.exists():
    sys.exit("Manca dati_privati.json (vedi dati_privati.esempio.json)")
dati = json.loads(privati.read_text(encoding="utf-8"))
if not isinstance(dati.get("sigle"), dict) or not dati["sigle"]:
    sys.exit('dati_privati.json deve contenere {"sigle": {"O": "Nome", ...}}')

def chiama(url, corpo, metodo="POST"):
    req = urllib.request.Request(url, data=json.dumps(corpo).encode(), method=metodo, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        sys.exit("Errore %s da %s: %s" % (e.code, url.split("?")[0], e.read().decode(errors="replace")[:300]))

password = os.environ.get("FB_PASSWORD") or getpass.getpass("Password dell'app: ")
login = chiama("https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=" + urllib.parse.quote(CHIAVE),
               {"email": EMAIL, "password": password, "returnSecureToken": True})
chiama(DB + "/config.json?auth=" + urllib.parse.quote(login["idToken"]), {"sigle": dati["sigle"]}, "PUT")
print("Caricato /config/sigle su Firebase (%d nomi)." % len(dati["sigle"]))
