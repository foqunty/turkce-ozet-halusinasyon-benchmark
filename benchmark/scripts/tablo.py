"""Bütün ölçümleri tek bir karşılaştırma tablosunda gösterir → grafikler/5_karsilastirma(_en).png

Satırlar ölçüm, sütunlar model. Her satırda en iyi değer vurgulanır: lider sütunda mavi, diğerlerinde gri.
Kullanım (benchmark klasöründen): python3 scripts/tablo.py
"""
import collections

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

from ortak import ROOT, SONUC, oku  # noqa: E402

AD = {"claude-opus-5.5": "Claude\nOpus 5.5", "claude-sonnet-5.5": "Claude\nSonnet 5.5", "claude-haiku-5.5": "Claude\nHaiku 5.5",
      "mistral-7b": "Mistral\n7B", "aya-expanse-8b": "Aya\nExpanse 8B", "llama3.2-3b": "Llama 3.2\n3B",
      "phi3.5-3.8b": "Phi-3.5\n3.8B", "qwen2.5-7b": "Qwen 2.5\n7B", "gemma2-9b": "Gemma 2\n9B", "llama3.1-8b": "Llama 3.1\n8B"}

ana = [r for r in oku(SONUC / "puanli.csv") if str(r["deneme"]) == "1"]
viki = oku(SONUC / "puanli_viki.csv")
tekrar = oku(SONUC / "puanli_tekrar.csv")


def ort(rows, f, **k):
    xs = [f(r) for r in rows if all(r[a] == b for a, b in k.items())]
    return sum(xs) / len(xs) if xs else None


def dogru(r):
    return int(r["dogru_mu"])


modeller = sorted(AD, key=lambda m: -(ort(ana, dogru, model=m) or 0))

# kararsızlık: 3 denemede sonucu değişen soru oranı
kararsiz = {}
by = collections.defaultdict(set)
for r in tekrar:
    by[(r["model"], r["soru_id"])].add(r["dogru_mu"])
for m in {m for m, _ in by}:
    qs = [v for (mm, _), v in by.items() if mm == m]
    kararsiz[m] = 100 * sum(len(v) > 1 for v in qs) / len(qs)


def sure(m):
    xs = [float(r["sure_sn"]) for r in ana if r["model"] == m and r["sure_sn"]]
    return sum(xs) / len(xs) if xs else None


def satir(f):
    return [f(m) for m in modeller]


pct = lambda v: f"{v:.0f}%"  # noqa: E731
# (grup_tr, grup_en, ölçüm_tr, ölçüm_en, alt_tr, alt_en, değerler, biçim, büyük_iyi)
SATIRLAR = [
    ("Genel", "Overall", "Doğruluk", "Accuracy", "50 kurgusal paragraf", "50 fictional paragraphs",
     satir(lambda m: 100 * ort(ana, dogru, model=m)), pct, True),
    ("", "", "Korunan bilgi", "Facts kept", "3 üzerinden", "out of 3",
     satir(lambda m: ort(ana, lambda r: int(r["olgu_bulunan"]), model=m)), lambda v: f"{v:.2f}", True),
    ("Kategori", "Category", "Haber", "News", "", "", satir(lambda m: 100 * ort(ana, dogru, model=m, kategori="haber")), pct, True),
    ("", "", "Bilim", "Science", "", "", satir(lambda m: 100 * ort(ana, dogru, model=m, kategori="bilim")), pct, True),
    ("", "", "Spor", "Sports", "", "", satir(lambda m: 100 * ort(ana, dogru, model=m, kategori="spor")), pct, True),
    ("Zorluk", "Difficulty", "Zorluk 1", "Level 1", "sade metin", "plain text", satir(lambda m: 100 * ort(ana, dogru, model=m, zorluk="1")), pct, True),
    ("", "", "Zorluk 2", "Level 2", "çeldirici", "distractors", satir(lambda m: 100 * ort(ana, dogru, model=m, zorluk="2")), pct, True),
    ("", "", "Zorluk 3", "Level 3", "tuzak", "trap", satir(lambda m: 100 * ort(ana, dogru, model=m, zorluk="3")), pct, True),
    ("Halüsinasyon", "Hallucination", "Uydurma sayı/tarih", "Invented number/date", "düşük daha iyi", "lower is better",
     satir(lambda m: 100 * ort(ana, lambda r: int(bool(r["halu_sayi"])), model=m)), pct, False),
    ("", "", "Uydurma isim", "Invented name", "düşük daha iyi", "lower is better",
     satir(lambda m: 100 * ort(ana, lambda r: int(bool(r["halu_ad"])), model=m)), pct, False),
    ("Gerçek metin", "Real text", "Vikipedi, orijinal", "Wikipedia, original", "25 metin", "25 texts",
     satir(lambda m: 100 * ort([r for r in viki if r["soru_id"].startswith("viki")], dogru, model=m)), pct, True),
    ("", "", "Vikipedi, değiştirilmiş", "Wikipedia, altered", "ezber tuzağı", "memorization trap",
     satir(lambda m: 100 * ort([r for r in viki if r["soru_id"].startswith("vikd")], dogru, model=m)), pct, True),
    ("Kararlılık", "Stability", "Kararsızlık", "Instability", "sıcaklık 0.7, 3 deneme", "temperature 0.7, 3 runs",
     satir(lambda m: kararsiz.get(m)), pct, False),
    ("Hız", "Speed", "Soru başına süre", "Time per question", "Apple M4, saniye", "Apple M4, seconds",
     satir(sure), lambda v: f"{v:.1f} sn", False),
]

MAVI, MAVI_KENAR, GRI, CIZGI, YAZI, SOLUK = "#a8d1fb", "#4a90e2", "#e4e6e8", "#c9ccd0", "#1f1f1f", "#5f6368"


def ciz(dil, yol):
    en = dil == "en"
    W = [1.35, 2.0, 1.75] + [1.0] * len(modeller)
    X = [sum(W[:i]) for i in range(len(W) + 1)]
    H0, H = 0.75, 0.5
    toplam_h = H0 + H * len(SATIRLAR) + 0.45
    fig, ax = plt.subplots(figsize=(X[-1], toplam_h))
    ax.set_xlim(0, X[-1]); ax.set_ylim(toplam_h, 0); ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.text(X[1] + 0.1, H0 / 2, "Benchmark", va="center", fontsize=11, color=YAZI)
    for j, m in enumerate(modeller):
        ax.text((X[3 + j] + X[4 + j]) / 2, H0 / 2, AD[m], ha="center", va="center", fontsize=10, color=YAZI, linespacing=1.15)
    ax.plot([0, X[-1]], [H0, H0], color=CIZGI, lw=1.2)
    lider = 0
    for i, (g_tr, g_en, o_tr, o_en, a_tr, a_en, vals, fmt, buyuk) in enumerate(SATIRLAR):
        y = H0 + i * H
        var = [v for v in vals if v is not None]
        en_iyi = (max if buyuk else min)(var) if var else None
        hepsi_ayni = len(set(round(v, 6) for v in var)) <= 1
        for j, v in enumerate(vals):
            if v is not None and not hepsi_ayni and abs(v - en_iyi) < 1e-9:
                ax.add_patch(Rectangle((X[3 + j], y), W[3 + j], H, color=MAVI if j == lider else GRI, zorder=0))
            ax.text((X[3 + j] + X[4 + j]) / 2, y + H / 2, "—" if v is None else fmt(v), ha="center", va="center",
                    fontsize=11, color=YAZI, fontweight="bold" if (v is not None and not hepsi_ayni and abs(v - en_iyi) < 1e-9) else "normal")
        grup = g_en if en else g_tr
        if grup:
            ax.text(0.1, y + 0.12, grup, va="top", fontsize=9.5, color=SOLUK)
            if i:
                ax.plot([0, X[-1]], [y, y], color=CIZGI, lw=1)
        else:
            ax.plot([X[1], X[-1]], [y, y], color=CIZGI, lw=1)
        ax.text(X[1] + 0.1, y + H / 2, o_en if en else o_tr, va="center", fontsize=11, color=YAZI)
        alt = a_en if en else a_tr
        if alt:
            ax.text(X[3] - 0.1, y + H / 2, alt, va="center", ha="right", fontsize=8.5, color=SOLUK)
    y_son = H0 + H * len(SATIRLAR)
    ax.plot([0, X[-1]], [y_son, y_son], color=CIZGI, lw=1.2)
    ax.add_patch(Rectangle((X[3], 0.02), W[3], y_son - 0.02, fill=False, ec=MAVI_KENAR, lw=2, zorder=3))
    not_ = ("Method: github.com/foqunty/turkce-ozet-halusinasyon-benchmark · prompt v1 · temperature 0 · open models via Ollama on Apple M4 16 GB"
            if en else
            "Yöntem: github.com/foqunty/turkce-ozet-halusinasyon-benchmark · istem v1 · sıcaklık 0 · açık modeller Ollama ile Apple M4 16 GB")
    ax.text(0.1, y_son + 0.25, not_, va="center", fontsize=8.5, color=SOLUK)
    fig.savefig(yol, dpi=160, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    print("→", yol)


ciz("tr", ROOT / "grafikler" / "5_karsilastirma.png")
ciz("en", ROOT / "grafikler" / "5_karsilastirma_en.png")
