# Türkçe Özet + Halüsinasyon Benchmark'ı

LLM'ler Türkçe bir paragrafı özetlerken **sayıyı, tarihi ve ismi koruyor mu, yoksa uyduruyor mu?**

Her soru, içinde 3 kritik bilgi (sayı, tarih, isim) olan bir Türkçe paragraf. Özet ancak üç bilgiyi de koruyor ve kaynakta olmayan hiçbir rakam ya da isim içermiyorsa doğru sayılıyor.

| model | doğru (50) |
|---|---|
| Claude Opus 5.5 | 50 |
| Claude Sonnet 5.5 | 50 |
| Claude Haiku 5.5 | 47 |
| Mistral 7B | 37 |
| Aya Expanse 8B | 33 |
| Llama 3.2 3B | 21 |
| Phi-3.5 3.8B | 12 |
| Qwen 2.5 7B | 11 |
| Gemma 2 9B | 9 |
| Llama 3.1 8B | 0 |

Yöntem, grafikler, ezber tuzağı deneyi ve yorum: **[benchmark/README.md](benchmark/README.md)**

Soru seti ve cevap anahtarı gizli tutuluyor (model eğitimine sızmasın diye), bu repoda yok.
