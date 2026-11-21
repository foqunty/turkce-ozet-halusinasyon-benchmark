"""Task 4 · 03: hakem modelin puanı ile senin puanın ne kadar uyuşuyor?

Önce: python scripts/kos.py hakem --hakem-model sonnet-5.5 --n 20
Sonra sonuclar/hakem.csv'de 'insan_puani' sütununu (0/1/2) kendin doldur ve bunu çalıştır.
"""
from ortak import SONUC, oku

rows = [r for r in oku(SONUC / "hakem.csv") if str(r["insan_puani"]).strip() and str(r["hakem_puani"]).strip()]
if not rows:
    raise SystemExit("hakem.csv'de doldurulmuş insan_puani yok.")
tam = sum(r["insan_puani"].strip() == str(r["hakem_puani"]).strip() for r in rows)
gecti = sum((int(r["insan_puani"]) == 2) == (int(r["hakem_puani"]) == 2) for r in rows)
print(f"n = {len(rows)}")
print(f"Tam uyum (0/1/2 aynı)        : {100 * tam / len(rows):.0f}%")
print(f"Geçti/kaldı uyumu (2 mi değil mi): {100 * gecti / len(rows):.0f}%")
for r in rows:
    if r["insan_puani"].strip() != str(r["hakem_puani"]).strip():
        print(f"  ayrıştı · {r['soru_id']} {r['model']}: sen {r['insan_puani']} / hakem {r['hakem_puani']} — {r['gerekce']}")
