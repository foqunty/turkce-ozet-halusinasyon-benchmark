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
| `id` | `oz-001` (insan), `ozai-001` (AI) |
| `kategori` | haber · bilim · spor |
| `zorluk` | 1–3 |
| `kaynak` | `insan` (elle yazıldı) / `ai` (model üretti, elle kontrol edildi) |
| `soru` | özetlenecek paragraf |
| `dogru_cevap` | `;` ile ayrılmış 3 kritik bilgi |
| `puanlama` | `kontrol_listesi` |

12 sütunlu CSV biçimi kullanılır.

## Dağılım

| | z1 | z2 | z3 | toplam |
|---|---|---|---|---|
| insan | | | | |
| ai | 15 | 20 | 15 | 50 |

## Puanlama

Bir özet ancak **3 bilginin üçü de doğru geçiyorsa ve kaynakta olmayan hiçbir sayı, tarih ya da isim içermiyorsa** doğru sayılır. Kod: `<github-repo-linki>/scripts/puanla.py`

## Skor tablosu

*(model × kategori tablosunu buraya ekle)*

## Lisans ve sınırlamalar

CC BY-NC 4.0. Küçük bir set (≈150 soru), tek bir istem ve sıcaklık 0 ile koşuldu. İsim kontrolü sezgiseldir. Ayrıntılar GitHub README'sinde.

## Atıf

Sedat Çoban, 2025.
