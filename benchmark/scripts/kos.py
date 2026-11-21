"""Benchmark'ı modellerde koşar. Sadece standart kütüphane.

Modeller modeller.json'da tanımlı. Üç yol:
  openrouter : API ile (OPENROUTER_API_KEY ortam değişkeni). Maliyeti OpenRouter döndürür.
  ollama     : yerel model (http://localhost:11434). Maliyet 0.
  manuel     : sohbet arayüzü (ücretsiz katman). İstemleri dosyaya döker, sen yapıştırırsın.

Örnekler:
  python scripts/kos.py api --modeller hepsi
  python scripts/kos.py api --modeller qwen-yerel --orneklem 30          # 30 soruluk dengeli örneklem
  python scripts/kos.py api --modeller sonnet-5.5 --tekrar 3 --orneklem 20  # tekrar kararsızlığı
  python scripts/kos.py manuel --model "gemini-4-carbon-web" --orneklem 30
  python scripts/kos.py hakem --hakem-model sonnet-5.5 --n 20           # hakem model

Aynı (soru, model, deneme) zaten varsa atlanır: yarıda kalırsa tekrar çalıştır, kaldığı yerden devam eder.
"""
import argparse
import datetime as dt
import json
import os
import random
import sys
import time
import urllib.error
import urllib.request

from ortak import ISTEM_SURUMU, ROOT, SONUC, SONUC_COLS, istem, oku, sorulari_yukle, yaz

SICAKLIK = float(os.environ.get("SICAKLIK", "0"))  # tekrar deneyi için: SICAKLIK=0.7
MAKS_TOKEN = 400
TOHUM = 42


# ---------------------------------------------------------------- sağlayıcılar

def _post(url, veri, basliklar, zaman_asimi=180):
    req = urllib.request.Request(url, data=json.dumps(veri).encode(), headers=basliklar)
    with urllib.request.urlopen(req, timeout=zaman_asimi) as r:
        return json.loads(r.read())


def openrouter(model_id, metin):
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        sys.exit("OPENROUTER_API_KEY tanımlı değil:  export OPENROUTER_API_KEY=sk-or-...")
    j = _post("https://openrouter.ai/api/v1/chat/completions",
              {"model": model_id, "temperature": SICAKLIK, "max_tokens": MAKS_TOKEN,
               "messages": [{"role": "user", "content": metin}],
               "usage": {"include": True}},
              {"Authorization": f"Bearer {key}", "Content-Type": "application/json",
               "X-Title": "turkce-ozet-halusinasyon-bench"})
    u = j.get("usage") or {}
    return (j["choices"][0]["message"]["content"] or "",
            u.get("prompt_tokens"), u.get("completion_tokens"), u.get("cost"))


def ollama(model_id, metin):
    j = _post("http://localhost:11434/api/chat",
              {"model": model_id, "stream": False,
               "messages": [{"role": "user", "content": metin}],
               "options": {"temperature": SICAKLIK, "num_predict": MAKS_TOKEN, **({"seed": TOHUM} if SICAKLIK == 0 else {})}},
              {"Content-Type": "application/json"}, zaman_asimi=600)
    return (j["message"]["content"], j.get("prompt_eval_count"), j.get("eval_count"), 0.0)


SAGLAYICI = {"openrouter": openrouter, "ollama": ollama}


# ---------------------------------------------------------------- yardımcılar

def modelleri_yukle():
    return {m["ad"]: m for m in json.loads((ROOT / "modeller.json").read_text(encoding="utf-8"))}


def orneklem_sec(sorular, n):
    """Kategori × zorluk katmanlarından dengeli örneklem (aynı tohum → herkes aynı 30 soru)."""
    if not n or n >= len(sorular):
        return sorular
    rnd = random.Random(TOHUM)
    katman = {}
    for s in sorular:
        katman.setdefault((s["kategori"], s["zorluk"]), []).append(s)
    for v in katman.values():
        rnd.shuffle(v)
    secilen, anahtarlar = [], sorted(katman)
    while len(secilen) < n:
        for k in anahtarlar:
            if katman[k] and len(secilen) < n:
                secilen.append(katman[k].pop())
    return sorted(secilen, key=lambda s: s["id"])


def simdi():
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M")


# ---------------------------------------------------------------- komutlar

def cmd_api(a):
    tum = modelleri_yukle()
    secili = [m for m in tum.values() if m["saglayici"] in SAGLAYICI] if a.modeller == ["hepsi"] \
        else [tum[ad] for ad in a.modeller]
    sorular = orneklem_sec(sorulari_yukle(), a.orneklem)[: a.limit or None]
    yol = SONUC / a.cikti
    rows = oku(yol) if yol.exists() else []
    rows = [r for r in rows if not (r.get("not") or "").startswith("HATA")]  # hatalıları yeniden dene
    yapilmis = {(r["soru_id"], r["model"], str(r["deneme"])) for r in rows}

    for m in secili:
        f = SAGLAYICI[m["saglayici"]]
        for deneme in range(1, a.tekrar + 1):
            for i, s in enumerate(sorular, 1):
                if (s["id"], m["ad"], str(deneme)) in yapilmis:
                    continue
                t0 = time.time()
                try:
                    cevap, tin, tout, cost = f(m["model_id"], istem(s["soru"]))
                    not_ = ""
                except (urllib.error.URLError, KeyError, TimeoutError) as e:
                    cevap, tin, tout, cost, not_ = "", None, None, None, f"HATA: {e}"
                sure = time.time() - t0
                rows.append({
                    "soru_id": s["id"], "model": m["ad"], "cevap": cevap.strip(), "dogru_mu": "",
                    "sure_sn": f"{sure:.2f}",
                    "tahmini_maliyet": "" if cost is None else f"{cost:.6f}",
                    "not": not_ or f"{m.get('surum', m['model_id'])} · istem {ISTEM_SURUMU} · "
                                   f"T={SICAKLIK}",
                    "deneme": deneme, "tarih": simdi(), "erisim": m["saglayici"],
                    "girdi_token": tin or "", "cikti_token": tout or "",
                })
                print(f"[{m['ad']} d{deneme}] {i}/{len(sorular)} {s['id']} {sure:.1f}s"
                      + (f"  {not_}" if not_ else ""))
                yaz(yol, rows, SONUC_COLS)          # her cevaptan sonra kaydet
    print(f"✓ {yol.relative_to(ROOT)} · şimdi:  python scripts/puanla.py")


def cmd_manuel(a):
    """Sohbet arayüzü için: istemleri tek tek kopyalayıp yapıştıracağın bir dosya üretir."""
    sorular = orneklem_sec(sorulari_yukle(), a.orneklem)[: a.limit or None]
    slug = a.model.replace(" ", "-").lower()
    yol = SONUC / f"sonuclar_manuel_{slug}.csv"
    if yol.exists():
        sys.exit(f"{yol.name} zaten var; üzerine yazmıyorum.")
    rows = [{"soru_id": s["id"], "model": a.model, "cevap": "", "dogru_mu": "", "sure_sn": "",
             "tahmini_maliyet": "0", "not": f"sohbet arayüzü · yeni sohbet · hafıza kapalı · istem {ISTEM_SURUMU}",
             "deneme": 1, "tarih": dt.date.today().isoformat(), "erisim": "web", "girdi_token": "",
             "cikti_token": "", "istem": istem(s["soru"])} for s in sorular]
    yaz(yol, rows, SONUC_COLS + ["istem"])
    md = SONUC / f"istemler_{slug}.md"
    md.write_text("\n\n".join(f"## {r['soru_id']}\n\n```\n{r['istem']}\n```" for r in rows),
                  encoding="utf-8")
    print(f"✓ {md.name}: her istemi YENİ sohbette yapıştır.\n"
          f"  Cevabı {yol.name} içindeki 'cevap' sütununa, süreyi 'sure_sn'ye yaz.\n"
          f"  Sonra: python scripts/puanla.py")


HAKEM_ISTEM = """Bir özetin kaynağa sadakatini puanlıyorsun.

KAYNAK PARAGRAF:
{kaynak}

ÖZET:
{ozet}

Puan:
2 = Anlam korunmuş; kaynakta olmayan bilgi yok, bilgiler doğru kişiye/olaya bağlanmış.
1 = Küçük anlam kayması (ör. vurgu değişmiş, bir bilgi yanlış özneye kaymış ama rakamlar doğru).
0 = Ciddi hata: uydurma bilgi, yanlış sayı/tarih/isim veya ters anlam.

Yalnızca şu JSON'u döndür: {{"puan": 0|1|2, "gerekce": "<tek cümle>"}}"""


def cmd_hakem(a):
    """LLM-as-judge: n cevabı hakem modele puanlatır; sen 'insan_puani'nı doldurursun."""
    m = modelleri_yukle()[a.hakem_model]
    f = SAGLAYICI[m["saglayici"]]
    sorular = {s["id"]: s for s in sorulari_yukle()}
    havuz = []
    for p in sorted(SONUC.glob("sonuclar*.csv")):
        havuz += [r for r in oku(p) if (r.get("cevap") or "").strip() and str(r.get("deneme", "1")) == "1"]
    if not havuz:
        sys.exit("Önce cevap topla.")
    rnd = random.Random(TOHUM)
    secilen = rnd.sample(havuz, min(a.n, len(havuz)))
    out = []
    for r in secilen:
        s = sorular[r["soru_id"]]
        cevap, *_ = f(m["model_id"], HAKEM_ISTEM.format(kaynak=s["soru"], ozet=r["cevap"]))
        try:
            j = json.loads(cevap[cevap.index("{"): cevap.rindex("}") + 1])
        except ValueError:
            j = {"puan": "", "gerekce": f"ayrıştırılamadı: {cevap[:80]}"}
        out.append({"soru_id": r["soru_id"], "model": r["model"], "hakem": m["ad"],
                    "hakem_puani": j.get("puan"), "gerekce": j.get("gerekce"),
                    "insan_puani": "", "ozet": r["cevap"], "kaynak": s["soru"]})
        print(f"{r['soru_id']} {r['model']}: {j.get('puan')}")
    yaz(SONUC / "hakem.csv", out,
        ["soru_id", "model", "hakem", "hakem_puani", "insan_puani", "gerekce", "ozet", "kaynak"])
    print("✓ sonuclar/hakem.csv · 'insan_puani'nı kendin doldur (modelin puanına bakmadan), "
          "sonra: python scripts/uyum.py")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    alt = ap.add_subparsers(dest="komut", required=True)
    p = alt.add_parser("api")
    p.add_argument("--modeller", nargs="+", default=["hepsi"])
    p.add_argument("--orneklem", type=int, default=0, help="dengeli n soru (0 = hepsi)")
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--tekrar", type=int, default=1)
    p.add_argument("--cikti", default="sonuclar.csv")
    p.set_defaults(f=cmd_api)
    p = alt.add_parser("manuel")
    p.add_argument("--model", required=True)
    p.add_argument("--orneklem", type=int, default=0)
    p.add_argument("--limit", type=int, default=0)
    p.set_defaults(f=cmd_manuel)
    p = alt.add_parser("hakem")
    p.add_argument("--hakem-model", required=True)
    p.add_argument("--n", type=int, default=20)
    p.set_defaults(f=cmd_hakem)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
