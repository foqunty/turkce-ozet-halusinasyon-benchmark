"""Ortak yardımcılar: CSV biçimi, istem şablonu, Türkçe metin normalleştirme.

Sadece standart kütüphane. Diğer betikler buradan içe aktarır.
"""
import csv
import os
import pathlib
import re
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SONUC = ROOT / "sonuclar"

# nexa-bench (sorular/_ornek.csv) ile birebir aynı sütunlar:
# aynı dosya hem bu repoda hem ortak repoda doğrulanabilir.
SORU_COLS = ["id", "tur", "alan", "kategori", "zorluk", "dil", "kaynak",
             "soru", "dogru_cevap", "puanlama", "tolerans", "not"]

# Week 4 PDF'teki sonuclar.csv sütunları + sonda ek bilgi sütunları.
SONUC_COLS = ["soru_id", "model", "cevap", "dogru_mu", "sure_sn", "tahmini_maliyet", "not",
              "deneme", "tarih", "erisim", "girdi_token", "cikti_token"]

ISTEM_SURUMU = "v1"
ISTEM = (
    "Aşağıdaki paragrafı Türkçe olarak 2-3 cümleyle özetle. "
    "Yalnızca paragrafta geçen bilgileri kullan; sayıları, tarihleri ve isimleri "
    "değiştirme, yeni bilgi ekleme. Sadece özeti yaz.\n\n"
    "Paragraf:\n{paragraf}"
)


def istem(paragraf: str) -> str:
    return ISTEM.format(paragraf=paragraf.strip())


# ---------------------------------------------------------------- CSV

def oku(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def yaz(path, rows, cols):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def sorulari_yukle(desen=None):
    """data/ altındaki soru dosyalarını birleştirir (ornek.csv hariç).
    Ayrı deney seti için: SORU_DESENI=deney_vikipedi.csv"""
    desen = desen or os.environ.get("SORU_DESENI", "sorular*.csv")
    rows = []
    for p in sorted(DATA.glob(desen)):
        if p.name.startswith("ornek"):
            continue
        rows += oku(p)
    return rows


# ---------------------------------------------------------------- normalleştirme

AYLAR = ["ocak", "subat", "mart", "nisan", "mayis", "haziran", "temmuz",
         "agustos", "eylul", "ekim", "kasim", "aralik"]
SAYI_KELIME = {"iki": 2, "uc": 3, "dort": 4, "bes": 5, "alti": 6, "yedi": 7,
               "sekiz": 8, "dokuz": 9, "on": 10, "yirmi": 20, "otuz": 30,
               "kirk": 40, "elli": 50, "yuz": 100}
OLCEK = {"bin": 1_000, "milyon": 1_000_000, "milyar": 1_000_000_000}
_FOLD = str.maketrans("çğıöşüâîû", "cgiosuaiu")


def kucult(s: str) -> str:
    """Türkçe küçük harf (I→ı, İ→i) + aksan katlama (ç→c ...; Višegrad → visegrad)."""
    t = s.replace("I", "ı").replace("İ", "i").lower().translate(_FOLD)
    return "".join(c for c in unicodedata.normalize("NFKD", t) if not unicodedata.combining(c))


def _sayi(tok: str) -> float:
    """'1.250' → 1250, '1,5' → 1.5, '2.500.000' → 2500000, '3.5' → 3.5"""
    if "." in tok and "," in tok:              # 1.250,75
        tok = tok.replace(".", "").replace(",", ".")
    elif "," in tok:                           # 1,5
        tok = tok.replace(",", ".")
    elif "." in tok:
        parts = tok.split(".")
        if all(len(p) == 3 for p in parts[1:]):  # binlik ayraç
            tok = tok.replace(".", "")
    return float(tok)


def _fmt(x: float) -> str:
    return str(int(x)) if abs(x - round(x)) < 1e-9 else f"{x:.6g}"


def normal(s: str, kelime_sayilar=True):
    """Metni karşılaştırılabilir hale getirir.

    Dönüş: (metin, tarihler kümesi, sayılar kümesi)
      tarihler: 'gg.aa.yyyy', 'aa.yyyy' biçiminde
      sayılar: '1250', '%45', '1.5' gibi kanonik dizgiler
    """
    t = kucult(s)
    t = re.sub(r"[*_#`]", " ", t)
    t = re.sub(r"(?<=\w)['’]\w+", "", t)              # Ankara'da → ankara
    t = re.sub(r"(?<![%\d])(\d+(?:[.,]\d+)*)\s?%(?!\s*\d)", r"%\1", t)  # 45% → %45
    t = re.sub(r"\byuzde\s+(\d)", r"%\1", t)

    tarihler = set()
    ay = "|".join(AYLAR)

    def _t1(m):
        g, a, y = int(m.group(1)), AYLAR.index(m.group(2)) + 1, m.group(3)
        d = f"{g:02d}.{a:02d}.{y}"
        tarihler.add(d)
        return f" TARIH{d} "

    def _t2(m):
        g, a, y = int(m.group(1)), int(m.group(2)), m.group(3)
        if not (1 <= g <= 31 and 1 <= a <= 12):
            return m.group(0)
        d = f"{g:02d}.{a:02d}.{y}"
        tarihler.add(d)
        return f" TARIH{d} "

    def _t3(m):
        d = f"{AYLAR.index(m.group(1)) + 1:02d}.{m.group(2)}"
        tarihler.add(d)
        return f" TARIH{d} "

    t = re.sub(rf"\b(\d{{1,2}})\s+({ay})\w*\s+(\d{{4}})\b", _t1, t)
    t = re.sub(r"\b(\d{1,2})[./](\d{1,2})[./](\d{4})\b", _t2, t)
    t = re.sub(rf"\b({ay})\w*\s+(\d{{4}})\b", _t3, t)

    def _t4(m):  # "2025 mayıs ayında" (önce yıl)
        d = f"{AYLAR.index(m.group(2)) + 1:02d}.{m.group(1)}"
        tarihler.add(d)
        return f" TARIH{d} "

    t = re.sub(rf"\b(\d{{4}})\s+({ay})\w*", _t4, t)

    if kelime_sayilar:
        for k, v in SAYI_KELIME.items():
            t = re.sub(rf"\b{k}\b", str(v), t)

    sayilar = set()

    def _n(m):
        yuzde, tok, olcek = m.group(1), m.group(2), m.group(3)
        x = _sayi(tok)
        if olcek:
            x *= OLCEK[olcek]
        k = ("%" if yuzde else "") + _fmt(x)
        sayilar.add(k)
        return f" {k} "

    t = re.sub(r"(?<![\w.])(%?)(\d+(?:[.,]\d+)*)(?:\s*(bin|milyon|milyar)\b)?", _n, t)
    # tarihin parçalarını (yıl, gün) da sayı say: "2024'te" gibi tek başına yıl geçebilir
    for d in tarihler:
        for p in d.split("."):
            sayilar.add(str(int(p)))
    t = re.sub(r"\s+", " ", t).strip()
    return t, tarihler, sayilar


def kelimeler(t: str):
    return re.findall(r"[a-z0-9%]+", t)
