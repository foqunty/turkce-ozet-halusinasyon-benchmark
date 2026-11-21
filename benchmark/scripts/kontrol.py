"""Kendi soru setini Week 4 kurallarına göre denetler.

  - nexa-bench ile aynı 12 sütun
  - en az 100 insan, 40–80 AI sorusu
  - en az 3 kategori, 3 zorluk; sorularin en az %20'si zorluk 3
  - her dogru_cevap tam 3 kritik bilgi (';' ile), ve her bilgi paragrafta gerçekten geçiyor

Kullanım: python scripts/kontrol.py
"""
import collections
import sys

from ortak import DATA, SORU_COLS, normal, oku
from puanla import olgu_var_mi

hatalar, uyarilar, rows = [], [], []
for p in sorted(DATA.glob("sorular*.csv")):
    r = oku(p)
    if r and list(r[0].keys()) != SORU_COLS:
        hatalar.append(f"{p.name}: başlık satırı {','.join(SORU_COLS)} olmalı")
        continue
    rows += [(p.name, i + 2, x) for i, x in enumerate(r)]

ids = collections.Counter(x["id"] for _, _, x in rows)
for ad, n, x in rows:
    yer = f"{ad}:{n} ({x['id']})"
    if ids[x["id"]] > 1:
        hatalar.append(f"{yer}: id tekrar ediyor")
    olgular = [o.strip() for o in x["dogru_cevap"].split(";") if o.strip()]
    if len(olgular) != 3:
        hatalar.append(f"{yer}: {len(olgular)} kritik bilgi var, 3 olmalı")
    pn, pt, ps = normal(x["soru"])
    for o in olgular:
        if not olgu_var_mi(o, pn, pt, ps):
            hatalar.append(f"{yer}: '{o}' paragrafta bulunamadı (yazım/biçim farkı?)")
    if x["puanlama"] != "kontrol_listesi":
        uyarilar.append(f"{yer}: puanlama 'kontrol_listesi' olmalı")
    if not (200 <= len(x["soru"]) <= 1200):
        uyarilar.append(f"{yer}: paragraf {len(x['soru'])} karakter (önerilen 200–1200)")

say = collections.Counter(x["kaynak"] for _, _, x in rows)
zor = collections.Counter(x["zorluk"] for _, _, x in rows)
kat = collections.Counter(x["kategori"] for _, _, x in rows)
n = len(rows)
print(f"toplam {n} · insan {say['insan']} · ai {say['ai']}")
print("kategori:", dict(kat), " zorluk:", dict(sorted(zor.items())))
if say["insan"] < 100:
    uyarilar.append(f"insan sorusu {say['insan']}/100")
if not 40 <= say["ai"] <= 80:
    uyarilar.append(f"AI sorusu {say['ai']} (40–80 olmalı)")
if len(kat) < 3:
    uyarilar.append("en az 3 kategori olmalı")
if n and zor["3"] / n < 0.20:
    uyarilar.append(f"zorluk 3 oranı %{100 * zor['3'] / n:.0f} (en az %20)")
for u in uyarilar:
    print("  ! " + u)
for h in hatalar:
    print("  ✕ " + h)
if hatalar:
    sys.exit(1)
print("✓ Biçim hatası yok." + (" (uyarılar teslimden önce kapanmalı)" if uyarilar else ""))
