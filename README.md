# NEXA Fellowship · Week 4

**Türkçe özet + halüsinasyon benchmark'ı.** Modeller Türkçe bir paragrafı özetlerken sayıyı, tarihi ve ismi koruyor mu, yoksa uyduruyor mu?

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

Ayrıntılar, yöntem, grafikler ve yorum: **[benchmark/README.md](benchmark/README.md)**

- `benchmark/`: puanlayıcı, model koşucu, sonuçlar, grafikler
- `notlar/`: görev notları (makale A3, alignment-handbook, yerel model, nexa-bench)
- `PLAN.md`: haftalık plan ve teslim listesi

Soru seti ve cevap anahtarı gizli tutuluyor (model eğitimine sızmasın diye), GitHub'da yok.
