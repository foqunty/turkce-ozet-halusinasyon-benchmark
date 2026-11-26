"""Telefondan/elle doldurulan Markdown şablonunu soru CSV'sine çevirir.

Şablon her soru için bir blok içerir:

    ### oz-001 · haber · zorluk 1
    Paragraf: <4-6 cümle>
    Sayı: <paragraftaki sayı>
    Tarih: <paragraftaki tarih>
    İsim: <paragraftaki ad soyad>
    Not: <isteğe bağlı, ör. hangi tuzak>

Boş bırakılan bloklar atlanır. Metne dokunulmaz; yalnızca biçim kontrol edilir.

Kullanım (benchmark klasöründen):
  python3 scripts/sablondan_csv.py ../notlar/insan_sorulari.md data/sorular_insan.csv
  python3 scripts/sablondan_csv.py ../notlar/nexa_bench_sorulari.md /yol/nexa-bench/sorular/foqunty.csv
  python3 scripts/sablondan_csv.py sablon.md cikti.csv ai     # üçüncü argüman: kaynak (insan | ai, varsayılan insan)
"""
import csv
import re
import sys

from ortak import SORU_COLS, normal
from puanla import olgu_var_mi

BASLIK = re.compile(r"^###\s+(\S+)\s+·\s+(\S+)\s+·\s+zorluk\s+([123])", re.M)
ALAN = re.compile(r"^(Paragraf|Sayı|Tarih|İsim|Not):[ \t]*(.*)$", re.M)


def bloklar(metin):
    bas = list(BASLIK.finditer(metin))
    for i, m in enumerate(bas):
        son = bas[i + 1].start() if i + 1 < len(bas) else len(metin)
        alanlar = {k: v.strip() for k, v in ALAN.findall(metin[m.end():son])}
        yield m.group(1), m.group(2), m.group(3), alanlar


def main(girdi, cikti, kaynak="insan"):
    if kaynak not in ("insan", "ai"):
        sys.exit("kaynak 'insan' ya da 'ai' olmalı")
    satirlar, sorunlar = [], []
    for sid, kat, zor, a in bloklar(open(girdi, encoding="utf-8").read()):
        p = a.get("Paragraf", "")
        olgular = [a.get(k, "") for k in ("Sayı", "Tarih", "İsim")]
        if not p and not any(olgular):
            continue  # henüz yazılmamış
        eksik = [k for k, v in zip(("Sayı", "Tarih", "İsim"), olgular) if not v]
        if not p or eksik:
            sorunlar.append(f"{sid}: eksik alan {eksik or ['Paragraf']}")
            continue
        n, t, sy = normal(p)
        for o in olgular:
            if not olgu_var_mi(o, n, t, sy):
                sorunlar.append(f"{sid}: '{o}' paragrafta bire bir geçmiyor")
        if not 200 <= len(p) <= 1200:
            sorunlar.append(f"{sid}: paragraf {len(p)} karakter (200–1200 olmalı)")
        satirlar.append(dict(id=sid, tur="metin", alan="özet", kategori=kat, zorluk=zor, dil="tr",
                             kaynak=kaynak, soru=p, dogru_cevap="; ".join(olgular),
                             puanlama="kontrol_listesi", tolerans="", **{"not": a.get("Not", "")}))
    with open(cikti, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SORU_COLS)
        w.writeheader()
        w.writerows(satirlar)
    print(f"{len(satirlar)} soru yazıldı → {cikti}")
    for s in sorunlar:
        print("  !", s)
    return 1 if sorunlar else 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
