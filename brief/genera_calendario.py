#!/usr/bin/env python3
"""Genera il calendario dei posti in macchina per l'a.s. 2026/27.
Uso: python3 genera_calendario.py [--sabato]   (--sabato = scuola anche il sabato)
Ordine posti: Avanti, Dietro sinistra, Centro, Dietro destra."""
import csv, json, sys
from datetime import date, timedelta

SABATO = "--sabato" in sys.argv
INIZIO, FINE = date(2026, 9, 10), date(2027, 6, 8)

# Sospensioni da decreto IC "De Filippo" (prot. 5911 del 02/07/2026) + festivita' nazionali
SOSPESI = {
 date(2026,10,30): "Recupero anticipo inizio anno",
 date(2026,11,2):  "Commemorazione dei defunti",
 date(2026,12,7):  "Ponte Immacolata",
 date(2026,12,8):  "Immacolata Concezione",
 date(2026,12,23): "Festività natalizie", date(2026,12,24): "Festività natalizie",
 date(2026,12,25): "Natale", date(2026,12,26): "Santo Stefano",
 date(2026,12,28): "Festività natalizie", date(2026,12,29): "Festività natalizie",
 date(2026,12,30): "Festività natalizie", date(2026,12,31): "Festività natalizie",
 date(2027,1,1): "Capodanno", date(2027,1,2): "Festività natalizie",
 date(2027,1,4): "Festività natalizie", date(2027,1,5): "Festività natalizie",
 date(2027,1,6): "Epifania",
 date(2027,2,8): "Carnevale", date(2027,2,9): "Carnevale",
 date(2027,2,10): "Recupero anticipo inizio anno",
 date(2027,3,25): "Festività pasquali", date(2027,3,26): "Festività pasquali",
 date(2027,3,27): "Festività pasquali", date(2027,3,29): "Lunedì dell'Angelo",
 date(2027,3,30): "Festività pasquali",
 date(2027,4,25): "Festa della Liberazione",
 date(2027,4,30): "Recupero anticipo inizio anno",
 date(2027,5,1): "Festa del Lavoro", date(2027,6,2): "Festa della Repubblica",
}

# Ciclo: ogni riga = [Avanti, Dietro sx, Centro, Dietro dx]. Sequenza continua da 16-17-18 sett.
CICLO = ["OMLA", "LAOM", "MLAO", "AOML"]
# I nomi dei bambini NON stanno nel repository (sono in Firebase, /config/sigle): qui solo le sigle.
NOMI = {"O": "O", "L": "L", "A": "A", "M": "M"}
GG = ["lun","mar","mer","gio","ven","sab","dom"]
POSTI = ["avanti","dietro_sx","centro","dietro_dx"]

# Tutti i giorni di scuola dal primo giorno (10/9)
giorni_scuola = []
d = INIZIO
while d <= FINE:
    wd = d.weekday()
    if d not in SOSPESI and wd != 6 and (wd != 5 or SABATO):
        giorni_scuola.append(d)
    d += timedelta(days=1)

# Il 16/9 = OMLA, 17 = LAOM, 18 = MLAO (dati reali). Il ciclo e' di 4 giorni, quindi si estende all'indietro
# fino al primo giorno di scuola (10/9): i 4 giorni 10, 11, 14, 15/9 (RICOSTRUITI) sono un ciclo completo
# e ognuno arriva al 16/9 avendo provato ogni posto una volta. Il ciclo parte dal 10/9 con indice 0.
PRIMO_REALE = date(2026, 9, 16)
righe = []
for i, g in enumerate(giorni_scuola):
    disp = CICLO[i % 4]
    r = {"data": g.isoformat(), "giorno": GG[g.weekday()], "n_scuola": i+1, "disposizione": disp}
    if g < PRIMO_REALE: r["ricostruito"] = True
    r.update({p: NOMI[c] for p, c in zip(POSTI, disp)})
    righe.append(r)

suff = "_6gg" if SABATO else ""
with open(f"calendario_posti{suff}.csv","w",newline="",encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(righe[0].keys())); w.writeheader(); w.writerows(righe)
json.dump({"ordine_posti": ["Avanti","Dietro sinistra","Centro","Dietro destra"],
           "sigle": NOMI, "sabato_a_scuola": SABATO,
           "sospensioni": {k.isoformat(): v for k, v in sorted(SOSPESI.items())},
           "giorni": righe}, open(f"calendario_posti{suff}.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)

# Verifiche
print("Giorni di lezione totali (da 10/9):", len(giorni_scuola))
from collections import Counter
c = {k: Counter() for k in "OLAM"}
for r in righe:
    for p, ch in zip(POSTI, r["disposizione"]): c[ch][p] += 1
for k in "OLAM": print(NOMI[k], dict(c[k]))
print("Primi:", [(r["data"], r["disposizione"]) for r in righe[:6]])
print("Ultimo:", righe[-1]["data"], righe[-1]["disposizione"])
