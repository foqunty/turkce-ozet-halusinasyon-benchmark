"""sonuclar/puanli.csv'den grafikler üretir → grafikler/*.png

  1_model_kategori.png   model × kategori doğruluk, insan soruları (gruplu çubuk)
  1b_model_kategori_ai.png  aynısı, AI soruları
  2_maliyet_dogruluk.png doğruluk ve doğru cevap başına süre (bütün koşular ücretsiz olduğu için maliyet yerine süre)
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
AD = {"claude-opus-5.5": "Claude Opus 5.5", "claude-sonnet-5.5": "Claude Sonnet 5.5", "claude-haiku-5.5": "Claude Haiku 5.5",
      "mistral-7b": "Mistral 7B", "aya-expanse-8b": "Aya Expanse 8B", "llama3.2-3b": "Llama 3.2 3B",
      "phi3.5-3.8b": "Phi-3.5 3.8B", "qwen2.5-7b": "Qwen 2.5 7B", "gemma2-9b": "Gemma 2 9B", "llama3.1-8b": "Llama 3.1 8B",
      "gemini-4-neon": "Gemini 4 Neon"}
GRUP_AD = {"insan": "İnsan yazımı (100)", "ai": "AI yazımı (50)"}

rows = [r for r in oku(SONUC / "puanli.csv") if str(r["deneme"]) == "1"]
modeller = sorted({r["model"] for r in rows},
                  key=lambda m: (-sum(int(r["dogru_mu"]) for r in rows if r["model"] == m)
                                 / max(1, sum(r["model"] == m for r in rows)), m))


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


def gruplu(dosya, baslik, anahtar, **filtre):
    gruplar = sorted({r[anahtar] for r in rows if all(r[k] == v for k, v in filtre.items())})
    fig, ax = plt.subplots(figsize=(max(8, len(modeller) * 0.9), 5.2))
    w = 0.8 / len(gruplar)
    for i, g in enumerate(gruplar):
        xs = [j + i * w - 0.4 + w / 2 for j in range(len(modeller))]
        ax.bar(xs, [oran(dogru, model=m, **{anahtar: g}, **filtre) for m in modeller], w,
               label=GRUP_AD.get(g, g), color=RENK[i % len(RENK)])
    ax.set_xticks(range(len(modeller)), [AD.get(m, m) for m in modeller], rotation=30, ha="right")
    ax.set_ylim(0, 100)
    stil(ax, baslik, "doğruluk (%)")
    ax.legend(frameon=False, ncol=min(len(gruplar), 5), loc="upper center", bbox_to_anchor=(0.5, -0.32), fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / dosya, dpi=160)
    plt.close(fig)


gruplu("1_model_kategori.png", "Model × kategori (insan yazımı 100 soru): doğru özet oranı", "kategori", kaynak="insan")
gruplu("1b_model_kategori_ai.png", "Model × kategori (AI yazımı 50 soru): doğru özet oranı", "kategori", kaynak="ai")
gruplu("3_insan_ai.png", "İnsan vs AI yazımı sorular", "kaynak")

# 2) doğruluk vs süre: koşuların hepsi ücretsiz (yerel model ya da abonelik arayüzü), Task 4'ün izin verdiği gibi süre kullanılır
fig, ax = plt.subplots(figsize=(9, 5.2))
olcusuz = []
for m in modeller:
    rs = [r for r in rows if r["model"] == m and r["sure_sn"]]
    if not rs:
        olcusuz.append(AD.get(m, m))
        continue
    acc = oran(dogru, model=m)
    n_dogru = sum(dogru(r) for r in rs)
    sn = sum(float(r["sure_sn"]) for r in rs) / max(1, n_dogru)
    ax.scatter(sn, acc, s=70, color="#2a78d6" if m.startswith("gemini") else "#1baf7a", zorder=3)
    ax.annotate(AD.get(m, m), (sn, acc), xytext=(6, 4), textcoords="offset points", fontsize=9)
ax.set_xscale("log")
ax.set_xlabel("doğru cevap başına süre (saniye, log ölçek)  ·  yeşil = yerel (Apple M4), mavi = web arayüzü")
ax.set_ylim(0, 105)
stil(ax, "Doğruluk vs doğru cevap başına süre (maliyet: hepsi 0 TL)", "doğruluk (%)")
ax.grid(alpha=0.25)
if olcusuz:
    ax.text(0.99, 0.02, "süre ölçülmedi: " + ", ".join(olcusuz), transform=ax.transAxes, ha="right", va="bottom",
            fontsize=8, color="#5f6368")
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
ax.set_xticks(list(xs), [AD.get(m, m) for m in modeller], rotation=30, ha="right")
stil(ax, "Kaynakta olmayan bilgi ekleyen özet oranı", "özetlerin %'si")
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(OUT / "4_halusinasyon.png", dpi=160)
plt.close(fig)

print("✓ grafikler/:", ", ".join(p.name for p in sorted(OUT.glob("*.png"))))
