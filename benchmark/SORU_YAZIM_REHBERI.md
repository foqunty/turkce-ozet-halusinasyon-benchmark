# 100 insan sorusunu yazarken

Bu kısım senin. AI sorularıyla ayrı raporlanıyor ve "hangisi daha zor çıktı?" sorusu tam da bu ayrıma dayanıyor. Elle yazılmamış bir soru `insan` etiketiyle girerse karşılaştırma anlamsızlaşır.

## Dosya

`data/sorular_insan.csv`, `data/ornek.csv` ile aynı başlık satırını kullanır. id'ler `oz-001`, `oz-002`, … şeklinde.

```
id,tur,alan,kategori,zorluk,dil,kaynak,soru,dogru_cevap,puanlama,tolerans,not
oz-001,metin,özet,haber,1,tr,insan,"<paragraf>","12 Mart 2025; 4.200; Ayşe Demir",kontrol_listesi,,
```

Bir paragraf yazdıkça şunu çalıştır:

```bash
python scripts/kontrol.py
```

Kritik bilgilerden biri paragrafta bire bir bulunamazsa bunu söyler.

## Kurallar

- 4–6 cümle, 200–1200 karakter.
- Tam 3 kritik bilgi: **bir sayı** (birimiyle), **bir tarih** ("12 Mart 2025"), **bir isim** (ad soyad).
- Kişi, kurum ve yerler **kurgusal** olsun (Kuzeyova, Sarıgöl…), gerçek haberi kopyalama.
- Dağılım: 3 kategori (haber · bilim · spor), her biri ≈33–34 soru. Soruların en az **%20'si zorluk 3** olacak (öneri: 30 z1 · 40 z2 · 30 z3).
- Soruları ve puanlama kuralını **modelleri denemeden önce** bitir.

## Zorluk nasıl artar

| zorluk | paragrafta ne var |
|---|---|
| 1 | Sadece 3 kritik bilgi ve sade cümleler. Başka rakam ya da isim yok. |
| 2 | Çeldiriciler var: ikinci bir rakam (eski değer, başka birim), ikinci bir tarih ya da ikinci bir kişi. |
| 3 | Tuzak var. Aşağıdaki tiplerden birini kullan. |

**Zorluk 3 tuzak tipleri**

1. **Düzeltme:** "İlk açıklanan 34 milyon değil, doğru rakam 43 milyon." Kritik bilgi düzeltilmiş olan.
2. **Aynı soyadı:** Ahmet Ilıcalı ile Zeynep Ilıcalı. Rakamı hangisi açıkladı?
3. **Dünya bilgisine ters:** Kurgusal bağlamda metinde açıkça yazıyor (91 °C'de kaynama, 13 aylık takvim). Model değeri "düzeltirse" bu bir halüsinasyondur.
4. **Saha skoru ile resmi sonuç:** 2-2 biten maç 3-0 hükmen tescil ediliyor.
5. **Yüzde ile yüzde puanı:** "%20'den %25'e çıktı" ifadesi 5 puanlık, ama %25'lik bir artış.
6. **Planlanan ile gerçekleşen:** 18 aylık görev planlanıyor, uydu 43 aydır çalışıyor.
7. **Olumsuzlama:** "Toplantıya Başkan Yıldız değil, yardımcısı Kaya katıldı."

## Kendine sor

- Özeti yazan bir insan 3 bilgiyi de rahatça koruyabilir mi? (Koruyamıyorsa soru adil değildir.)
- Kritik bilgi yalnızca **tek** biçimde mi doğru? ("4.200" ile "4200" ikisi de olur, normalleştirme bunu halleder. "Yaklaşık dört bin" ise olmaz.)
- Paragrafta kritik bilgi dışında sayı varsa, model onu da özete yazabilir. Bu uydurma sayılmaz, çünkü o sayı kaynakta var.
