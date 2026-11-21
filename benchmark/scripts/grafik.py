"""sonuclar/puanli.csv'den grafikler üretir → grafikler/*.png

  1_model_kategori.png   model × kategori doğruluk (gruplu çubuk)
  2_maliyet_dogruluk.png doğruluk ve doğru cevap başına maliyet tek grafikte
  3_insan_ai.png         insan vs AI sorularında doğruluk
  4_halusinasyon.png     uydurma sayı / isim oranı

Kurulum: pip install matplotlib
"""
import collections

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from ortak import ROOT, SONUC, oku  # noqa: E402

OUT = ROOT / "grafikler"
OUT.mkdir(exist_ok=True)
RENK = ["#2a78d6", "#1baf7a", "#e8a33d", "#c4486b", "#7a5bd6"]

rows = [r for r in oku(SONUC / "puanli.csv") if str(r["deneme"]) == "1"]
modeller = sorted({r["model"] for r in rows},
                  key=lambda m: -sum(int(r["dogru_mu"]) for r in rows if r["model"] == m)
                  / max(1, sum(r["model"] == m for r in rows)))


def oran(f, **kosul):
    xs = [f(r) for r in rows if all(r[k] == v for k, v in kosul.items())]
    return 100 * sum(xs) / len(xs) if xs else 0


def dogru(r):
    return int(r["dogru_mu"])


def stil(ax, baslik, ylabel):
    ax.set_title(baslik, loc="left", fontsize=12, fontweight="bold")
    ax.set_ylabel(ylabel)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.25)


def gruplu(dosya, baslik, anahtar):
    gruplar = sorted({r[anahtar] for r in rows})
    fig, ax = plt.subplots(figsize=(max(8, len(modeller) * 0.9), 4.5))
    w = 0.8 / len(gruplar)
    for i, g in enumerate(gruplar):
        xs = [j + i * w - 0.4 + w / 2 for j in range(len(modeller))]
        ax.bar(xs, [oran(dogru, model=m, **{anahtar: g}) for m in modeller], w,
               label=g, color=RENK[i % len(RENK)])
    ax.set_xticks(range(len(modeller)), modeller, rotation=30, ha="right")
    ax.set_ylim(0, 100)
    stil(ax, baslik, "doğruluk (%)")
    ax.legend(frameon=False, ncol=len(gruplar))
    fig.tight_layout()
    fig.savefig(OUT / dosya, dpi=160)
    plt.close(fig)


gruplu("1_model_kategori.png", "Model × kategori: doğru özet oranı", "kategori")
gruplu("3_insan_ai.png", "İnsan vs AI yazımı sorular", "kaynak")

# 2) maliyet
fig, ax = plt.subplots(figsize=(8, 5))
for m in modeller:
    rs = [r for r in rows if r["model"] == m]
    acc = oran(dogru, model=m)
    toplam = sum(float(r["tahmini_maliyet"] or 0) for r in rs)
    n_dogru = sum(dogru(r) for r in rs)
    kd = toplam / n_dogru if n_dogru else 0
    ax.scatter(kd * 1000, acc, s=70, color="#2a78d6" if toplam else "#1baf7a", zorder=3)
    ax.annotate(m, (kd * 1000, acc), xytext=(6, 4), textcoords="offset points", fontsize=9)
ax.set_xlabel("doğru cevap başına maliyet ($ / 1000 doğru)  ·  yeşil = ücretsiz / yerel")
ax.set_ylim(0, 100)
stil(ax, "Doğruluk vs maliyet", "doğruluk (%)")
ax.grid(alpha=0.25)
fig.tight_layout()
fig.savefig(OUT / "2_maliyet_dogruluk.png", dpi=160)
plt.close(fig)

# 4) halüsinasyon
fig, ax = plt.subplots(figsize=(max(8, len(modeller) * 0.9), 4.5))
xs = range(len(modeller))
ax.bar([x - 0.2 for x in xs], [oran(lambda r: bool(r["halu_sayi"]), model=m) for m in modeller],
       0.4, label="uydurma sayı/tarih", color="#c4486b")
ax.bar([x + 0.2 for x in xs], [oran(lambda r: bool(r["halu_ad"]), model=m) for m in modeller],
       0.4, label="uydurma isim", color="#e8a33d")
ax.set_xticks(list(xs), modeller, rotation=30, ha="right")
stil(ax, "Kaynakta olmayan bilgi ekleyen özet oranı", "özetlerin %'si")
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(OUT / "4_halusinasyon.png", dpi=160)
plt.close(fig)

print("✓ grafikler/ altına 4 PNG yazıldı:", ", ".join(p.name for p in sorted(OUT.glob("*.png"))))
