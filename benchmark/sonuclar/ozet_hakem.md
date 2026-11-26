# Hakem modeli: anlam kayması (20 cevap)

20 cevap tohumla (42) rastgele seçildi ve iki ayrı model, birbirinin puanını görmeden 0–2 arası puanladı. İkisi de temiz bağlamlı Claude Code alt ajanıydı: Sonnet 5.5 ve Opus 5.5. Puan ölçeği: 2 = anlam korunmuş, 1 = küçük kayma, 0 = ciddi hata.

| ölçüm | sonuç |
|---|---|
| tam uyum (0/1/2 aynı) | 16/20 (%80) |
| geçti/kaldı uyumu (2 mi değil mi) | 17/20 (%85) |
| Cohen kappa | 0.64 |
| kod (doğru) ile Sonnet (2) aynı karar | 12/20 |
| kod (doğru) ile Opus (2) aynı karar | 11/20 |

Puan dağılımı · Sonnet: 2→13, 1→6, 0→1 · Opus: 2→10, 1→8, 0→2


| # | soru | model | kod | Sonnet | Opus |
|---|---|---|---|---|---|
| 1 | A3-K010 | aya-expanse-8b | doğru | 1 | 1 |
| 2 | ozai-029 | llama3.1-8b | yanlış | 2 | 2 |
| 3 | ozai-002 | claude-opus-5.5 | doğru | 2 | 2 |
| 4 | A3-K064 | claude-opus-5.5 | doğru | 2 | 2 |
| 5 | A3-K002 | claude-opus-5.5 | doğru | 2 | 2 |
| 6 | ozai-008 | llama3.2-3b | yanlış | 2 | 2 |
| 7 | ozai-036 | gemma2-9b | yanlış | 2 | 2 |
| 8 | ozai-010 | llama3.1-8b | yanlış | 1 | 1 |
| 9 | A3-K086 | aya-expanse-8b | doğru | 2 | 1 |
| 10 | A3-K017 | mistral-7b | doğru | 2 | 1 |
| 11 | ozai-029 | qwen2.5-7b | doğru | 1 | 1 |
| 12 | A3-K010 | phi3.5-3.8b | yanlış | 0 | 0 |
| 13 | A3-K065 | qwen2.5-7b | doğru | 1 | 1 |
| 14 | ozai-016 | claude-opus-5.5 | doğru | 2 | 2 |
| 15 | ozai-012 | claude-opus-5.5 | doğru | 2 | 2 |
| 16 | ozai-042 | qwen2.5-7b | yanlış | 1 | 1 |
| 17 | ozai-048 | aya-expanse-8b | doğru | 2 | 2 |
| 18 | ozai-027 | llama3.2-3b | doğru | 2 | 2 |
| 19 | A3-K035 | gemma2-9b | yanlış | 2 | 1 |
| 20 | A3-K033 | phi3.5-3.8b | doğru | 1 | 0 |

İnsan puanı henüz eklenmedi. `sonuclar/hakem.csv` dosyasındaki `insan_puani` sütunu doldurulunca `python scripts/uyum.py` insan ile hakem arasındaki uyumu da hesaplar.
