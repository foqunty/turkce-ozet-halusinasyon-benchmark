"""Vikipedi deneyi: orijinal (viki) ve değiştirilmiş (vikd) metinlerde modelleri karşılaştırır.

ezber = değiştirilmiş metnin özetinde, metindeki yeni değer yerine gerçek (eski) değerin yazılması.
Kullanım (benchmark klasöründen):
  SORU_DESENI=deney_vikipedi.csv CIKTI_EK=_viki python3 scripts/puanla.py sonuclar/sonuclar_viki_*.csv
  python3 scripts/ezber.py      → sonuclar/ezber.json + ekrana tablo
"""
import collections, json, re

from ortak import DATA, SONUC, normal, oku
from puanla import olgu_var_mi

sorular = {s["id"]: s for s in oku(DATA / "deney_vikipedi.csv")}
puanli = oku(SONUC / "puanli_viki.csv")

ist = collections.defaultdict(lambda: dict(orj=0, orj_n=0, deg=0, deg_n=0, ezber=0, yeni_yazdi=0, ornekler=[]))
for r in puanli:
    s = sorular[r["soru_id"]]
    m = ist[r["model"]]
    if r["soru_id"].startswith("viki"):
        m["orj_n"] += 1; m["orj"] += int(r["dogru_mu"])
        continue
    m["deg_n"] += 1; m["deg"] += int(r["dogru_mu"])
    eski, yeni = re.search(r"DEĞİŞTİRİLMİŞ: (.*?) → (.*?) ·", s["not"]).groups()
    n, t, sy = normal(r["cevap"])
    e = olgu_var_mi(eski, n, t, sy)
    y = olgu_var_mi(yeni, n, t, sy)
    m["yeni_yazdi"] += y
    if e and not y:
        m["ezber"] += 1
        m["ornekler"].append(dict(id=r["soru_id"], eski=eski, yeni=yeni, cevap=r["cevap"]))

print(f"{'model':22} {'orijinal':>9} {'değişmiş':>9} {'ezber':>6} {'yeni değeri yazdı':>18}")
for k, m in sorted(ist.items(), key=lambda kv: (-kv[1]["ezber"], kv[0])):
    print(f"{k:22} {m['orj']:>4}/{m['orj_n']:<4} {m['deg']:>4}/{m['deg_n']:<4} {m['ezber']:>6} {m['yeni_yazdi']:>12}/{m['deg_n']}")
    for o in m["ornekler"]:
        print(f"    {o['id']}: metin {o['yeni']} dedi, model {o['eski']} yazdı")
(SONUC / "ezber.json").write_text(json.dumps(ist, ensure_ascii=False, indent=1), encoding="utf-8")
