"""Public scorer tests: only the example questions in data/ornek.csv (no hidden set).

The cases are the examples shown in the README. Run: python scripts/test_ornek.py
"""
import sys

from ortak import DATA, oku
from puanla import puanla_satir

S = {r["id"]: r for r in oku(DATA / "ornek.csv")}

# (question id, model summary, expected correct (1/0), why)
CASES = [
    ("ornek-001", "Akçay Belediyesi ilk kreşini 4 Mart 2025'te açtı. 60 çocukluk kreşin ikincisinin gelecek yıl "
                  "açılacağını Başkan Gönül Ertaş duyurdu.", 1, "all 3 facts, nothing invented"),
    ("ornek-001", "Akçay Belediyesi 04.03.2025'te ilk kreşini açtı; 60 çocuk kapasiteli. Başkan Ertaş ikinci kreşi "
                  "müjdeledi.", 1, "other date format, surname only"),
    ("ornek-001", "Akçay'da ilk kreş açıldı, 60 çocuk kapasiteli. Başkan Gönül Ertaş ikinci kreşin gelecek yıl "
                  "açılacağını söyledi.", 0, "date missing"),
    ("ornek-001", "Akçay Belediyesi ilk kreşini 4 Mart 2025'te açtı. 80 çocukluk kreşi Başkan Gönül Ertaş ve Müdür "
                  "Ali Kaya tanıttı.", 0, "80 instead of 60, invented name"),
    ("ornek-001", "", 0, "empty answer"),
    ("ornek-002", "Akçayspor'un 1-1 biten maçı, federasyonun 9 Nisan 2025 kararıyla 3-0 tescil edildi; kurul başkanı "
                  "Orçun Talay karar kesin dedi.", 1, "registered score kept"),
    ("ornek-002", "Akçayspor'un maçı 1-1 bitti. Kurul başkanı Orçun Talay 9 Nisan 2025'te kararın kesin olduğunu "
                  "söyledi.", 0, "trap: pitch score only"),
]


def main():
    hata = 0
    for sid, ozet, beklenen, neden in CASES:
        r = puanla_satir(S[sid], ozet)
        ok = int(r["dogru_mu"]) == beklenen
        hata += not ok
        print(f"{'✓' if ok else '✗'} {sid} · expected {beklenen}, got {r['dogru_mu']} · {neden}"
              + ("" if ok else f" · missing={r['eksik_olgular']} num={r['halu_sayi']} name={r['halu_ad']}"))
    print(f"\n{len(CASES) - hata}/{len(CASES)} passed")
    sys.exit(1 if hata else 0)


if __name__ == "__main__":
    main()
