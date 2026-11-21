"""Model özetlerini koddan puanlar (ekrandan değil, ham çıktıdan).

Her soru = bir paragraf + 3 kritik bilgi (dogru_cevap: "sayı; tarih; isim").
Bir özet için:
  olgu_bulunan  : 3 kritik bilgiden kaçı özette doğru geçiyor
  halu_sayi     : kaynakta OLMAYAN sayı/tarih (uydurma rakam)
  halu_ad       : kaynakta OLMAYAN özel isim (cümle ortasında büyük harfle başlayan)
  dogru_mu      : 3/3 bilgi var VE hiç uydurma sayı/tarih/isim yok → 1, yoksa 0

Kullanım:
  python scripts/puanla.py                       # sonuclar/sonuclar*.csv hepsi
  python scripts/puanla.py sonuclar/sonuclar.csv
Çıktı:
  sonuclar/puanli.csv   satır satır ayrıntı
  sonuclar/ozet.md      model × kategori / zorluk / kaynak tabloları (README'ye kopyala)
"""
import collections
import re
import statistics
import sys

import os

from ortak import AYLAR, SONUC, kelimeler, kucult, normal, oku, sorulari_yukle, yaz

PUANLI_COLS = ["soru_id", "model", "deneme", "kategori", "zorluk", "kaynak",
               "olgu_bulunan", "olgu_toplam", "eksik_olgular", "halu_sayi", "halu_ad",
               "dogru_mu", "sure_sn", "tahmini_maliyet", "cevap"]


def temizle(cevap: str) -> str:
    c = cevap.strip()
    c = re.sub(r"^\s*(özet|ozet|summary)\s*:\s*", "", c, flags=re.I)
    return c


def olgu_var_mi(olgu: str, ozet_norm, ozet_tarih, ozet_sayi) -> bool:
    on, ot, os_ = normal(olgu)
    if ot:                                   # tarih: aynı gün/ay/yıl
        return ot <= ozet_tarih
    if os_:                                  # sayı: tüm sayılar (yüzde işaretiyle) geçmeli
        return os_ <= ozet_sayi
    # isim / ifade: her kelime, özetteki bir kelimenin başı olmalı (Türkçe ekler için)
    ozet_k = kelimeler(ozet_norm)
    toks = [k for k in kelimeler(on) if len(k) >= 2]
    if not toks:
        return False

    def bul(tok):
        return any(w == tok or (len(tok) >= 3 and w.startswith(tok)) for w in ozet_k)

    if all(bul(t) for t in toks):
        return True
    # "Ahmet Yılmaz" yerine yalnız "Yılmaz" yazıldıysa da kabul (soyadı ≥4 harf)
    return len(toks) >= 2 and len(toks[-1]) >= 4 and bul(toks[-1])


def uydurma_sayilar(ozet: str, kaynak: str):
    _, kt, ks = normal(kaynak, kelime_sayilar=False)
    _, ot, os_ = normal(ozet, kelime_sayilar=False)
    kaynak_deger = {s.lstrip("%") for s in ks}
    yeni = sorted(d for d in ot if d not in kt)
    yeni += sorted(s for s in os_ if s.lstrip("%") not in kaynak_deger)
    return yeni


def uydurma_adlar(ozet: str, kaynak: str):
    # tarih dönüşümü yapmadan kaynaktaki kelimeler (ay adları kaybolmasın) + ay adları
    kaynak_k = kelimeler(re.sub(r"(?<=\w)['’]\w+", "", kucult(kaynak))) + AYLAR
    supheli = []
    for cumle in re.split(r"(?<=[.!?:])\s+|\n+", ozet):
        toks = re.findall(r"[\wçğıöşüÇĞİÖŞÜ’']+", cumle)
        for i, tok in enumerate(toks):
            if i == 0 or not tok[:1].isupper() or tok.isupper() and len(tok) <= 3:
                continue
            kok = kucult(re.split(r"['’]", tok)[0])
            on = kok[:5] if len(kok) > 5 else kok
            if not any(w.startswith(on) for w in kaynak_k):
                supheli.append(tok)
    return supheli


def puanla_satir(soru, cevap):
    ozet = temizle(cevap)
    if not ozet:
        return dict(olgu_bulunan=0, olgu_toplam=0, eksik_olgular="(boş cevap)",
                    halu_sayi="", halu_ad="", dogru_mu=0)
    on, ot, os_ = normal(ozet)
    olgular = [o.strip() for o in soru["dogru_cevap"].split(";") if o.strip()]
    eksik = [o for o in olgular if not olgu_var_mi(o, on, ot, os_)]
    hs = uydurma_sayilar(ozet, soru["soru"])
    ha = uydurma_adlar(ozet, soru["soru"])
    return dict(
        olgu_bulunan=len(olgular) - len(eksik),
        olgu_toplam=len(olgular),
        eksik_olgular=" | ".join(eksik),
        halu_sayi=" | ".join(hs),
        halu_ad=" | ".join(ha),
        dogru_mu=int(not eksik and not hs and not ha),
    )


def yuzde(xs):
    return f"{100 * sum(xs) / len(xs):.0f}%" if xs else "–"


def tablo(baslik, satirlar, anahtar, modeller):
    gruplar = sorted({r[anahtar] for r in satirlar})
    out = [f"### {baslik}", "", "| model | " + " | ".join(gruplar) + " |",
           "|---|" + "---|" * len(gruplar)]
    for m in modeller:
        hucre = []
        for g in gruplar:
            xs = [int(r["dogru_mu"]) for r in satirlar if r["model"] == m and r[anahtar] == g]
            hucre.append(yuzde(xs))
        out.append(f"| {m} | " + " | ".join(hucre) + " |")
    return "\n".join(out) + "\n"


def main():
    import glob
    dosyalar = sys.argv[1:] or sorted(
        p for p in glob.glob(str(SONUC / "sonuclar*.csv")))
    if not dosyalar:
        sys.exit("sonuclar/ altında sonuclar*.csv yok. Önce scripts/kos.py çalıştır.")
    sorular = {s["id"]: s for s in sorulari_yukle()}
    satirlar, eksik_soru = [], set()
    for d in dosyalar:
        ham = oku(d)
        for r in ham:
            s = sorular.get(r["soru_id"])
            if s is None:
                eksik_soru.add(r["soru_id"])
                continue
            if not (r.get("cevap") or "").strip():
                continue                      # manuel dosyada henüz doldurulmamış
            p = puanla_satir(s, r["cevap"])
            r["dogru_mu"] = p["dogru_mu"]     # ham dosyaya da yaz
            satirlar.append({**r, **p, "kategori": s["kategori"], "zorluk": s["zorluk"],
                             "kaynak": s["kaynak"], "deneme": r.get("deneme") or "1"})
        alanlar = list(ham[0].keys()) if ham else []
        yaz(d, ham, alanlar)
    if eksik_soru:
        print(f"! {len(eksik_soru)} soru_id data/ içinde bulunamadı: {sorted(eksik_soru)[:5]}…")
    if not satirlar:
        sys.exit("Puanlanacak cevap yok.")
    yaz(SONUC / f"puanli{os.environ.get('CIKTI_EK', '')}.csv", satirlar, PUANLI_COLS)

    modeller = sorted({r["model"] for r in satirlar})
    ilk = [r for r in satirlar if str(r["deneme"]) == "1"]   # tablolar ilk denemeden

    md = ["## Sonuçlar", "",
          "| model | doğruluk | olgu (3 üzerinden) | uydurma sayı | uydurma isim | sn/soru | $ toplam | n |",
          "|---|---|---|---|---|---|---|---|"]
    for m in modeller:
        rs = [r for r in ilk if r["model"] == m]
        if not rs:
            continue
        acc = yuzde([int(r["dogru_mu"]) for r in rs])
        olgu = statistics.mean(int(r["olgu_bulunan"]) for r in rs)
        hs = yuzde([bool(r["halu_sayi"]) for r in rs])
        ha = yuzde([bool(r["halu_ad"]) for r in rs])
        sure = [float(r["sure_sn"]) for r in rs if r.get("sure_sn")]
        mal = sum(float(r["tahmini_maliyet"] or 0) for r in rs)
        md.append(f"| {m} | **{acc}** | {olgu:.2f} | {hs} | {ha} | "
                  f"{statistics.mean(sure):.1f} | {mal:.4f} | {len(rs)} |" if sure else
                  f"| {m} | **{acc}** | {olgu:.2f} | {hs} | {ha} | – | {mal:.4f} | {len(rs)} |")
    md.append("")
    md.append(tablo("Kategoriye göre doğruluk", ilk, "kategori", modeller))
    md.append(tablo("Zorluğa göre doğruluk", ilk, "zorluk", modeller))
    md.append(tablo("İnsan vs AI soruları", ilk, "kaynak", modeller))

    # Tekrar: aynı soru aynı modele birden çok kez sorulduysa
    tekrar = collections.defaultdict(set)
    for r in satirlar:
        tekrar[(r["model"], r["soru_id"])].add(int(r["dogru_mu"]))
    coklu = collections.defaultdict(lambda: [0, 0])
    sayac = collections.Counter((r["model"], r["soru_id"]) for r in satirlar)
    for (m, sid), v in tekrar.items():
        if sayac[(m, sid)] > 1:
            coklu[m][0] += 1
            coklu[m][1] += int(len(v) > 1)
    if coklu:
        md += ["### Tekrar: kararsızlık oranı", "",
               "| model | tekrarlanan soru | sonucu değişen | kararsızlık |", "|---|---|---|---|"]
        for m, (n, k) in sorted(coklu.items()):
            md.append(f"| {m} | {n} | {k} | {100 * k / n:.0f}% |")
        md.append("")

    (SONUC / f"ozet{os.environ.get('CIKTI_EK', '')}.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))
    print(f"\n✓ {len(satirlar)} cevap puanlandı → sonuclar/puanli{os.environ.get('CIKTI_EK', '')}.csv")


if __name__ == "__main__":
    main()
