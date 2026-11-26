---
language:
- tr
license: cc-by-nc-4.0
task_categories:
- summarization
- text-generation
tags:
- benchmark
- hallucination
- turkish
- faithfulness
pretty_name: Türkçe Özet + Halüsinasyon
size_categories:
- n<1K
extra_gated_prompt: "Bu set, modellerin eğitim verisine sızmaması için gizli tutuluyor. Lütfen soruları ve cevap anahtarını herkese açık bir yerde yeniden yayımlamayacağını onayla."
extra_gated_fields:
  Ad Soyad: text
  Kurum / amaç: text
  Soruları herkese açık yayımlamayacağım: checkbox
---

# Türkçe Özet + Halüsinasyon

LLM'lerin Türkçe paragrafları özetlerken **kritik bilgileri (sayı, tarih, isim) koruyup korumadığını** ve **kaynakta olmayan bilgi uydurup uydurmadığını** ölçen küçük bir benchmark.

> **Erişim:** Sorular ve cevap anahtarı yalnızca onaylanan kişilere açıktır (manual approval). Bu kart, dağılım ve skorlar herkese açıktır.

## Amaç

Akıcı bir özet her zaman doğru bir özet değildir. Bu set, Türkçe metinde kodla doğrulanabilen üç kritik bilgi üzerinden **özet sadakatini** ölçer. Tüm kişi, kurum ve yerler kurgusaldır, yani model cevabı ezberinden değil metinden çıkarmak zorundadır.

## Yapı

| sütun | açıklama |
|---|---|
| `id` | `A3-K001` (insan), `ozai-001` (AI) |
| `kategori` | insan seti: doğa ve çevre · kültür ve sanat · kent ve ulaşım · eğitim ve gözlem · spor ve gündelik yaşam; AI seti: haber · bilim · spor |
| `zorluk` | 1–3 |
| `kaynak` | `insan` (elle yazıldı) / `ai` (model üretti, elle kontrol edildi) |
| `soru` | özetlenecek paragraf |
| `dogru_cevap` | `;` ile ayrılmış 3 kritik bilgi |
| `puanlama` | `kontrol_listesi` |

12 sütunlu CSV biçimi kullanılır.

## Dağılım

| | z1 | z2 | z3 | toplam |
|---|---|---|---|---|
| insan | 20 | 50 | 30 | 100 |
| ai | 15 | 20 | 15 | 50 |
| toplam | 35 | 70 | 45 | 150 |

İnsan setinde her kategoride 20 soru var; AI setinde haber 17, spor 17, bilim 16. Zorluk 3 oranı: insan %30, AI %30.

## Puanlama

Bir özet ancak **3 bilginin üçü de doğru geçiyorsa ve kaynakta olmayan hiçbir sayı, tarih ya da isim içermiyorsa** doğru sayılır. Kod: [github.com/foqunty/turkce-ozet-halusinasyon-benchmark](https://github.com/foqunty/turkce-ozet-halusinasyon-benchmark) (`benchmark/scripts/puanla.py`)

## Skor tablosu

| model | insan (100) | AI (50) | genel (150) |
|---|---|---|---|
| Claude Opus 5.5 | 100% | 100% | 100% |
| Claude Sonnet 5.5 | 100% | 100% | 100% |
| Claude Haiku 5.5 | 100% | 94% | 98% |
| Aya Expanse 8B | 83% | 66% | 77% |
| Mistral 7B | 69% | 74% | 71% |
| Qwen 2.5 7B | 68% | 22% | 53% |
| Llama 3.2 3B | 67% | 42% | 59% |
| Phi-3.5 3.8B | 46% | 24% | 39% |
| Gemma 2 9B | 42% | 18% | 34% |
| Llama 3.1 8B | 9% | 0% | 6% |

İstem v1, sıcaklık 0. Açık modeller Ollama ile Apple M4 16 GB üzerinde koşuldu. Ayrıntılı model × kategori tabloları ve grafikler GitHub reposunda.


## Lisans ve sınırlamalar

CC BY-NC 4.0. Küçük bir set (≈150 soru), tek bir istem ve sıcaklık 0 ile koşuldu. İsim kontrolü sezgiseldir. Ayrıntılar GitHub README'sinde.

## Atıf

Sedat Çoban, 2026.
