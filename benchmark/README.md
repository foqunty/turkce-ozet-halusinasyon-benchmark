# Türkçe Özet + Halüsinasyon Benchmark'ı

**Türkçe** · [English](README.en.md)

> LLM'ler Türkçe bir paragrafı özetlerken **kritik bilgileri (sayı, tarih, isim) koruyor mu, yoksa uyduruyor mu?**

Sorular gizli (Hugging Face gated dataset), skorlar ve kod açık.
**HF dataset:** `https://huggingface.co/datasets/<hf-kullanici>/turkce-ozet-halusinasyon` *(erişim istekli)*

---

## Amaç

Özetleme, modellerin en çok kullanıldığı işlerden biri. Ama özetin akıcı olması doğru olduğu anlamına gelmiyor. Bir sayının değişmesi ("43 milyon" → "34 milyon") ya da kaynakta olmayan bir ismin eklenmesi, okuyan kişinin fark edemeyeceği bir hata. Bu benchmark tam olarak bunu ölçüyor: **Türkçe** metinde, **kodla** kontrol edilebilir kritik bilgiler.

## Görev

Her soru kısa bir Türkçe paragraf. İçinde 3 kritik bilgi var: bir sayı, bir tarih ve bir isim. Model paragrafı 2-3 cümleyle özetliyor.

| ölçüm | nasıl |
|---|---|
| **olgu** | 3 kritik bilgiden kaçı özette doğru geçiyor (tarih biçimi, binlik ayraç, "yüzde 45" = "%45", Türkçe ekler normalleştirilir) |
| **uydurma sayı/tarih** | özette olup kaynakta olmayan her rakam |
| **uydurma isim** | cümle ortasında büyük harfle geçen ve kaynakta olmayan özel isim |
| **doğru** | 3/3 bilgi var **ve** hiç uydurma yok |
| **anlam kayması** | 20 cevap hakem modele puanlatılır, aynı cevapları ben de puanlarım → uyum oranı |

Puanlama ekrandan değil, ham çıktıdan ve kodla yapılır: [`scripts/puanla.py`](scripts/puanla.py).

## Modele ne gönderildi?

Her modele kelimesi kelimesine **aynı istem** gitti (istem `v1`). `{paragraf}` yerine her seferinde o sorunun metni yazıldı:

```text
Aşağıdaki paragrafı Türkçe olarak 2-3 cümleyle özetle. Yalnızca paragrafta geçen bilgileri kullan; sayıları, tarihleri ve isimleri değiştirme, yeni bilgi ekleme. Sadece özeti yaz.

Paragraf:
{paragraf}
```

Sistem istemi yok, örnek (few-shot) yok. Gerçek sorular gizli olduğu için aşağıdaki örnek, setin dışında yazılmış bir biçim örneğidir ([`data/ornek.csv`](data/ornek.csv)).

**Örnek metin (zorluk 1, haber):**

> Kurgusal Akçay Belediyesi, ilçenin ilk kreşini **4 Mart 2025**'te açtı. Kreşte **60** çocuk için yer bulunuyor. Belediye Başkanı **Gönül Ertaş**, ikinci kreşin gelecek yıl açılacağını söyledi. Kreşin yapımı yaklaşık on ay sürdü.

**Cevap anahtarı:** `4 Mart 2025; 60; Gönül Ertaş`

| model özeti | sonuç | neden |
|---|---|---|
| Akçay Belediyesi ilk kreşini 4 Mart 2025'te açtı. 60 çocukluk kreşin ikincisinin gelecek yıl açılacağını Başkan Gönül Ertaş duyurdu. | doğru | 3 bilgi de var, uydurma yok |
| Akçay Belediyesi 04.03.2025'te ilk kreşini açtı; 60 çocuk kapasiteli. Başkan Ertaş ikinci kreşi müjdeledi. | doğru | tarih biçimi farklı ama aynı; soyadı tek başına yeterli |
| Akçay'da ilk kreş açıldı, 60 çocuk kapasiteli. Başkan Gönül Ertaş ikinci kreşin gelecek yıl açılacağını söyledi. | yanlış | tarih yok |
| Akçay Belediyesi ilk kreşini 4 Mart 2025'te açtı. 80 çocukluk kreşi Başkan Gönül Ertaş ve Müdür Ali Kaya tanıttı. | yanlış | 60 yerine 80 yazmış; "Ali Kaya" metinde yok |

**Zor (zorluk 3) örnek:** maç sahada 1-1 biter ama federasyon 3-0 hükmen tescil eder. Anahtar `3-0; 9 Nisan 2025; Orçun Talay`. Özette yalnızca "1-1" yazan model, saha skorunu verdiği için yanlış sayılır.

## Metinden ne istedik? (soru yazım kuralları)

Her paragraf şu şartları sağlıyor; [`scripts/kontrol.py`](scripts/kontrol.py) bunları otomatik denetliyor:

| kural | neden |
|---|---|
| Türkçe, 200–1200 karakter, 3–6 cümle | 2-3 cümlelik özet için yeterli bilgi, ama bilgiyi seçmeyi gerektirecek kadar uzun |
| Tam **3 kritik bilgi**: bir sayı, bir tarih, bir isim | üçü de kodla kesin kontrol edilebilir |
| Her bilgi paragrafta **bire bir** geçiyor | cevap anahtarı yorum gerektirmez |
| Paragrafta kritik olmayan ek bilgiler de var (süre, yer, ikinci bir rakam) | modelin neyin önemli olduğunu seçmesi gerekir; ek rakamlar uydurma tespitini de zorlaştırır |
| Kişi, yer ve kurumlar **kurgusal** | model cevabı ezberinden veremez, sadece metne bakabilir (kontaminasyon önlemi) |
| Zorluk 3'te bir **tuzak**: düzeltilen rakam, aynı soyadlı iki kişi, dünya bilgisine ters düşen değer, birden çok tarih, yüzde/yüzde puanı | "metne sadakat" ile "genel bilgi" çatıştığında model hangisini seçiyor? |
| 3 kategori (haber, bilim, spor), 3 zorluk; en az %20'si zorluk 3 | sonuçlar tek bir türe bağlı kalmasın |

## Özetten ne istedik? (puanlama)

| şart | ayrıntı |
|---|---|
| 3 bilginin üçü de özette | "4 Mart 2025" = "04.03.2025" = "4 Mart'ta (2025)"; "1.250" = "1250"; "yüzde 45" = "%45"; Türkçe ekler ("Ertaş'ın") ve büyük/küçük harf yok sayılır; kişi için soyadı yeterli |
| Uydurma rakam/tarih yok | özetteki her sayı ve tarih kaynakta olmalı |
| Uydurma isim yok | cümle ortasında büyük harfle geçen her kelimenin kaynakta karşılığı olmalı (ay adları hariç) |
| **Doğru** = | 3/3 bilgi **ve** sıfır uydurma |

Özetin uzunluğu ya da üslubu puanlanmıyor. Ölçülen tek şey kritik bilgilerin **doğru aktarılması**.

## Kategori ve zorluk dağılımı

| | zorluk 1 | zorluk 2 | zorluk 3 | toplam |
|---|---|---|---|---|
| haber | | | | |
| bilim | | | | |
| spor | | | | |
| **insan** | | | | **≥100** |
| **AI** (ayrı etiket) | 15 | 20 | 15 | **50** |

**Zorluk 3** soruların tuzağı var: metin içinde düzeltilen rakam ("ilk açıklanan 34 değil, 43"), aynı soyadlı iki kişi, dünya bilgisine ters düşen ama metinde açıkça yazan değer (yüksek rakımda suyun 91 °C'de kaynaması), birden çok tarih, yüzde ile yüzde puanının karışması.

Bütün kişi, yer ve kurumlar **kurgusaldır**. Böylece model ezberinden cevap üretemez, sadece metne bakabilir. Bu aynı zamanda kontaminasyona karşı bir önlem.

## Koşul (her model için aynı)

- İstem `v1` ([`scripts/ortak.py`](scripts/ortak.py)), en fazla 400 token
- Açık modeller Ollama ile bu bilgisayarda: sistem istemi yok, her soru ayrı ve tek mesaj, sıcaklık 0
- Claude modelleri Claude Code alt ajanlarıyla: 50 istem tek dosyada verildi, model her birini ayrı cevapladı ama hepsi aynı oturumda yazıldı; sıcaklık ayarlanamadı
- Web arayüzü kullanılacak modellerde (ChatGPT) her soru için yeni sohbet ve hafıza kapalı
- Model sürümü, tarih ve erişim yolu `sonuclar.csv`'nin `not`, `tarih`, `erisim` sütunlarında

## Sonuçlar

*İlk koşu · 21 Kasım 2026 · 50 AI sorusu · istem v1. Claude modelleri Claude Code alt ajanlarıyla, açık modeller Ollama ile (Apple M4, 16 GB, sıcaklık 0) koşuldu. Açık modeller: Qwen 2.5 7B, Llama 3.1 8B, Llama 3.2 3B, Gemma 2 9B, Mistral 7B, Phi-3.5, Aya Expanse 8B. ChatGPT henüz eklenmedi.*
| model | doğruluk | olgu (3 üzerinden) | uydurma sayı | uydurma isim | sn/soru | $ toplam | n |
|---|---|---|---|---|---|---|---|
| aya-expanse-8b | **66%** | 2.62 | 0% | 0% | 7.0 | 0.0000 | 50 |
| claude-haiku-5.5 | **94%** | 2.94 | 0% | 0% | – | 0.0000 | 50 |
| claude-opus-5.5 | **100%** | 3.00 | 0% | 0% | – | 0.0000 | 50 |
| claude-sonnet-5.5 | **100%** | 3.00 | 0% | 0% | – | 0.0000 | 50 |
| gemma2-9b | **18%** | 1.88 | 0% | 0% | 6.3 | 0.0000 | 50 |
| llama3.1-8b | **0%** | 0.78 | 46% | 22% | 3.9 | 0.0000 | 50 |
| llama3.2-3b | **42%** | 2.26 | 0% | 0% | 3.0 | 0.0000 | 50 |
| mistral-7b | **74%** | 2.72 | 4% | 2% | 10.8 | 0.0000 | 50 |
| phi3.5-3.8b | **24%** | 2.32 | 48% | 46% | 10.7 | 0.0000 | 50 |
| qwen2.5-7b | **22%** | 1.98 | 0% | 2% | 4.3 | 0.0000 | 50 |

### Kategoriye göre doğruluk

| model | bilim | haber | spor |
|---|---|---|---|
| aya-expanse-8b | 62% | 65% | 71% |
| claude-haiku-5.5 | 100% | 88% | 94% |
| claude-opus-5.5 | 100% | 100% | 100% |
| claude-sonnet-5.5 | 100% | 100% | 100% |
| gemma2-9b | 19% | 0% | 35% |
| llama3.1-8b | 0% | 0% | 0% |
| llama3.2-3b | 31% | 41% | 53% |
| mistral-7b | 69% | 71% | 82% |
| phi3.5-3.8b | 31% | 6% | 35% |
| qwen2.5-7b | 31% | 18% | 18% |

### Zorluğa göre doğruluk

| model | 1 | 2 | 3 |
|---|---|---|---|
| aya-expanse-8b | 40% | 65% | 93% |
| claude-haiku-5.5 | 93% | 90% | 100% |
| claude-opus-5.5 | 100% | 100% | 100% |
| claude-sonnet-5.5 | 100% | 100% | 100% |
| gemma2-9b | 13% | 5% | 40% |
| llama3.1-8b | 0% | 0% | 0% |
| llama3.2-3b | 40% | 60% | 20% |
| mistral-7b | 67% | 70% | 87% |
| phi3.5-3.8b | 20% | 25% | 27% |
| qwen2.5-7b | 7% | 15% | 47% |

### İnsan vs AI soruları

| model | ai |
|---|---|
| aya-expanse-8b | 66% |
| claude-haiku-5.5 | 94% |
| claude-opus-5.5 | 100% |
| claude-sonnet-5.5 | 100% |
| gemma2-9b | 18% |
| llama3.1-8b | 0% |
| llama3.2-3b | 42% |
| mistral-7b | 74% |
| phi3.5-3.8b | 24% |
| qwen2.5-7b | 22% |

### Deney: gerçek Vikipedi metinleri + ezber tuzağı

25 KPSS konulu Türkçe Vikipedi metni (CC BY-SA 4.0) ve her birinin tek bilgisi değiştirilmiş hâli (`data/deney_vikipedi.csv`, `scripts/vikipedi_seti.py`). Ezber analizi: `python3 scripts/ezber.py`. Sonuç: 10 modelin hiçbiri değiştirilmiş metinde ezberdeki gerçek değeri yazmadı (ezber = 0); hatalar atlama ve uydurma.

| model | doğruluk | olgu (3 üzerinden) | uydurma sayı | uydurma isim | sn/soru | $ toplam | n |
|---|---|---|---|---|---|---|---|
| aya-expanse-8b | **40%** | 2.18 | 0% | 4% | 7.5 | 0.0000 | 50 |
| claude-haiku-5.5 | **74%** | 2.68 | 0% | 0% | – | 0.0000 | 50 |
| claude-opus-5.5 | **100%** | 3.00 | 0% | 0% | – | 0.0000 | 50 |
| claude-sonnet-5.5 | **92%** | 2.90 | 0% | 0% | – | 0.0000 | 50 |
| gemma2-9b | **20%** | 1.64 | 0% | 6% | 7.2 | 0.0000 | 50 |
| llama3.1-8b | **4%** | 0.62 | 28% | 14% | 4.1 | 0.0000 | 50 |
| llama3.2-3b | **36%** | 2.06 | 0% | 4% | 3.5 | 0.0000 | 50 |
| mistral-7b | **46%** | 2.42 | 0% | 8% | 14.6 | 0.0000 | 50 |
| phi3.5-3.8b | **10%** | 2.00 | 48% | 20% | 9.6 | 0.0000 | 50 |
| qwen2.5-7b | **22%** | 1.66 | 4% | 2% | 4.3 | 0.0000 | 50 |

### Ek: tekrar kararsızlığı

Aya Expanse 8B ve Llama 3.2 3B, aynı 20 soruyu (dengeli örneklem, tohum 42) **sıcaklık 0.7** ile 3'er kez çözdü (`SICAKLIK=0.7 python3 scripts/kos.py api --tekrar 3 --orneklem 20`).

| model | deneme 1 / 2 / 3 doğru | sonucu değişen soru | kararsızlık |
|---|---|---|---|
| aya-expanse-8b | 13 / 13 / 13 (20 üzerinden) | 7 | %35 |
| llama3.2-3b | 9 / 11 / 11 | 13 | %65 |

Aya'nın toplam skoru üç denemede de aynı (13/20), ama **hangi** soruları doğru yaptığı 7 soruda değişiyor. Tek bir koşunun skoru sabit görünse bile soru düzeyinde sonuç şansa bağlı. Bu yüzden ana sonuçlar sıcaklık 0 ile alındı ve tek koşu, tek ölçüm olarak okunmamalı.

![Karşılaştırma tablosu](grafikler/5_karsilastirma.png)
![model × kategori](grafikler/1_model_kategori.png)
![doğruluk vs maliyet](grafikler/2_maliyet_dogruluk.png)
![insan vs AI](grafikler/3_insan_ai.png)
![halüsinasyon](grafikler/4_halusinasyon.png)

## Yorum

Claude modelleri açık farkla önde: Sonnet ve Opus 50/50, Haiku 47/50 yaptı. Açık modellerde en iyiler Mistral 7B (37/50) ve Türkçe dahil 23 dil için eğitilmiş Aya Expanse 8B (33/50). Hatalar iki türe ayrılıyor. Qwen, Gemma, Aya ve Llama 3.2 bilgiyi atlıyor ama neredeyse hiç uydurmuyor. Llama 3.1 8B ve Phi-3.5 ise metinde olmayan isim, rakam ve tarih yazıyor; Llama 3.1 hiçbir soruyu doğru yapamadı ve özetlerinin %54'ünde uydurma var. Model boyutu tek başına belirleyici değil: Llama 3.2 3B (21/50), kendinden büyük Llama 3.1 8B'yi (0/50) açık ara geçti. Kısa özet yazan modeller önce isimleri, sonra tarihleri atıyor. Claude ise metnin %92–94'ünü koruyor, yani test Claude için doymuş durumda; istem v2 ("en fazla 20 kelime") ile yeniden ayırt edici hale getirilmeli. Şaşırtıcı bulgu: açık modeller "zor" (z3) sorularda daha başarılı. Zor sorularda kritik bilgi paragrafın ana konusu; kolay sorularda isim kenarda kalıyor ve kısaltırken ilk o atılıyor. Gerçek Vikipedi metinleriyle kurulan ezber tuzağında (bilgiyi değiştirilmiş metin) 10 modelin hiçbiri ezberdeki doğru değeri yazmadı. Yani metin önündeyken modeller metne uyuyor; asıl risk ezber değil, uydurma. İnsan soruları henüz eklenmediği için insan ve AI karşılaştırması bekliyor.

## Nasıl koşulur

```bash
# 1) soruları data/ altına koy (gizli; repoda yok, HF'ten erişim iste)
python scripts/kontrol.py                 # set kurallara uyuyor mu?

# 2) modelleri koş
export OPENROUTER_API_KEY=sk-or-...
python scripts/kos.py api --modeller hepsi
python scripts/kos.py manuel --model gemini-4-carbon-web   # web arayüzü için istem dosyası

# 3) puanla + grafik
python scripts/puanla.py                  # → sonuclar/puanli.csv, sonuclar/ozet.md
pip install -r requirements.txt
python scripts/grafik.py                  # → grafikler/*.png

# ekler
python scripts/kos.py api --modeller sonnet-5.5 --tekrar 3 --orneklem 20   # tekrar / kararsızlık
python scripts/kos.py hakem --hakem-model sonnet-5.5 --n 20 && python scripts/uyum.py
```

Betiklerin hepsi standart kütüphaneyle çalışır, yalnızca `grafik.py` matplotlib ister.

## Sınırlamalar

- İsim kontrolü sezgisel: büyük harfle başlayan kelimeye bakar, yanlış pozitif verebilir. `puanli.csv`'de her uydurma işareti görünür ve elle kontrol edilebilir.
- Model hem yanlış hem doğru rakamı yazarsa ("34 değil 43 milyon") kod geçer verir. Bu tür anlam hatalarını hakem modelle ayrıca ölçüyorum.
- 3 kritik bilgi dışındaki ayrıntıların kaybı ölçülmüyor. Bu bir sadakat testi, özet kalitesi testi değil.

## Dosyalar

```
data/ornek.csv          biçim örneği (gerçek sorular gizli, .gitignore'da)
scripts/ortak.py        istem, CSV biçimi, Türkçe normalleştirme
scripts/kos.py          modelleri koşar (openrouter / ollama / manuel / hakem)
scripts/puanla.py       kodla puanlama + özet tablolar
scripts/grafik.py       grafikler
scripts/tablo.py        bütün ölçümler tek karşılaştırma tablosunda
scripts/kontrol.py      soru seti kurallarını denetler
scripts/uyum.py         hakem model ile insan puanının uyumu
modeller.json           model listesi
sonuclar/               ham cevaplar ve puanlar
```
