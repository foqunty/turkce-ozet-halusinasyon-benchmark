# Turkish Summary + Hallucination Benchmark

[Türkçe](README.md) · **English**

> When an LLM summarizes a Turkish paragraph, **does it keep the critical facts (number, date, name), or does it make them up?**

The questions are hidden (Hugging Face gated dataset); the scores and the code are public.
**HF dataset:** `https://huggingface.co/datasets/<hf-user>/turkce-ozet-halusinasyon` *(access on request)*

---

## Goal

Summarization is one of the most common things people use models for. But a fluent summary is not always a correct one. A changed number ("43 million" → "34 million") or a name that is not in the source is an error the reader cannot notice. This benchmark measures exactly that: critical facts in **Turkish** text that can be checked **by code**.

## Task

Each question is a short Turkish paragraph with 3 critical facts: a number, a date and a name. The model summarizes the paragraph in 2-3 sentences.

| metric | how |
|---|---|
| **facts** | how many of the 3 critical facts appear correctly in the summary (date formats, thousands separators, "yüzde 45" = "%45" and Turkish suffixes are normalized) |
| **invented number/date** | any number in the summary that is not in the source |
| **invented name** | any capitalized proper noun mid-sentence that is not in the source |
| **correct** | 3/3 facts **and** nothing invented |
| **meaning drift** | 20 answers are graded by a judge model and by me → agreement rate |

Scoring is done by code from the raw output, not from the screen: [`scripts/puanla.py`](scripts/puanla.py).

## What was sent to the model?

Every model got **the exact same prompt** (prompt `v1`). `{paragraf}` was replaced with the text of each question:

```text
Aşağıdaki paragrafı Türkçe olarak 2-3 cümleyle özetle. Yalnızca paragrafta geçen bilgileri kullan; sayıları, tarihleri ve isimleri değiştirme, yeni bilgi ekleme. Sadece özeti yaz.

Paragraf:
{paragraf}
```

In English: *"Summarize the paragraph below in Turkish in 2-3 sentences. Use only information from the paragraph; do not change numbers, dates or names, and do not add new information. Write only the summary."*

There is no system prompt and no few-shot examples. The real questions are hidden, so the example below is a format example written outside the set ([`data/ornek.csv`](data/ornek.csv)).

**Example text (difficulty 1, news):**

> Kurgusal Akçay Belediyesi, ilçenin ilk kreşini **4 Mart 2025**'te açtı. Kreşte **60** çocuk için yer bulunuyor. Belediye Başkanı **Gönül Ertaş**, ikinci kreşin gelecek yıl açılacağını söyledi. Kreşin yapımı yaklaşık on ay sürdü.

*(The fictional Akçay municipality opened the district's first nursery on 4 March 2025. It has room for 60 children. Mayor Gönül Ertaş said a second nursery will open next year. Construction took about ten months.)*

**Answer key:** `4 Mart 2025; 60; Gönül Ertaş`

| model summary | result | why |
|---|---|---|
| Akçay Belediyesi ilk kreşini 4 Mart 2025'te açtı. 60 çocukluk kreşin ikincisinin gelecek yıl açılacağını Başkan Gönül Ertaş duyurdu. | correct | all 3 facts present, nothing invented |
| Akçay Belediyesi 04.03.2025'te ilk kreşini açtı; 60 çocuk kapasiteli. Başkan Ertaş ikinci kreşi müjdeledi. | correct | different date format, same date; the surname alone is enough |
| Akçay'da ilk kreş açıldı, 60 çocuk kapasiteli. Başkan Gönül Ertaş ikinci kreşin gelecek yıl açılacağını söyledi. | wrong | date missing |
| Akçay Belediyesi ilk kreşini 4 Mart 2025'te açtı. 80 çocukluk kreşi Başkan Gönül Ertaş ve Müdür Ali Kaya tanıttı. | wrong | wrote 80 instead of 60; "Ali Kaya" is not in the text |

**Hard example (difficulty 3):** a match ends 1-1 on the pitch, but the federation awards it 3-0. The key is `3-0; 9 Nisan 2025; Orçun Talay`. A model that only writes "1-1" gave the pitch score, so it is wrong.

## What did we require from the text? (question writing rules)

Every paragraph meets these rules; [`scripts/kontrol.py`](scripts/kontrol.py) checks them automatically:

| rule | why |
|---|---|
| Turkish, 200–1200 characters, 3–6 sentences | enough for a 2-3 sentence summary, but long enough that the model has to choose what matters |
| Exactly **3 critical facts**: a number, a date, a name | all three can be checked exactly by code |
| Each fact appears in the paragraph **word for word** | the answer key needs no interpretation |
| The paragraph also has non-critical details (duration, place, a second number) | the model has to pick what is important; extra numbers also make invented ones harder to spot |
| People, places and organizations are **fictional** | the model cannot answer from memory, only from the text (contamination guard) |
| Difficulty 3 has a **trap**: a corrected number, two people with the same surname, a value that contradicts world knowledge, several dates, percent vs. percentage point | when "faithful to the text" and "general knowledge" clash, which one does the model choose? |
| 3 categories (news, science, sports), 3 difficulty levels; at least 20% difficulty 3 | results should not depend on one type of text |

## What did we require from the summary? (scoring)

| requirement | details |
|---|---|
| All 3 facts in the summary | "4 Mart 2025" = "04.03.2025" = "4 Mart'ta (2025)"; "1.250" = "1250"; "yüzde 45" = "%45"; Turkish suffixes ("Ertaş'ın") and letter case are ignored; the surname is enough for a person |
| No invented numbers or dates | every number and date in the summary must be in the source |
| No invented names | every capitalized word in the middle of a sentence must appear in the source (month names excluded) |
| **Correct** = | 3/3 facts **and** zero invented items |

Length and style of the summary are not scored. The only thing measured is whether the critical facts are **carried over correctly**.

## Category and difficulty distribution

| | difficulty 1 | difficulty 2 | difficulty 3 | total |
|---|---|---|---|---|
| news | | | | |
| science | | | | |
| sports | | | | |
| **human** | | | | **≥100** |
| **AI** (separate label) | 15 | 20 | 15 | **50** |

**Difficulty 3** questions have a trap: a number corrected inside the text ("not 34 as first announced, but 43"), two people with the same surname, a value that contradicts world knowledge but is stated clearly in the text (water boiling at 91 °C at high altitude), several dates, or percent mixed up with percentage points.

All people, places and organizations are **fictional**. The model cannot answer from memory, only from the text. This is also a guard against contamination.

## Conditions (the same for every model)

- Prompt `v1` ([`scripts/ortak.py`](scripts/ortak.py)), at most 400 tokens
- Open models ran on this computer with Ollama: no system prompt, each question as a separate single message, temperature 0
- Claude models ran through Claude Code subagents: the 50 prompts were given in one file and the model answered each one separately, but all in the same session; temperature could not be set
- For models used through a web UI (ChatGPT): a new chat for each question, memory off
- Model version, date and access route are in the `not`, `tarih` and `erisim` columns of `sonuclar.csv`

## Results

*First run · 21 November 2026 · 50 AI questions · prompt v1. Claude models ran through Claude Code subagents, open models with Ollama (Apple M4, 16 GB, temperature 0). Open models: Qwen 2.5 7B, Llama 3.1 8B, Llama 3.2 3B, Gemma 2 9B, Mistral 7B, Phi-3.5, Aya Expanse 8B. ChatGPT has not been added yet.*

| model | accuracy | facts (out of 3) | invented numbers | invented names | s/question | $ total | n |
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

### Accuracy by category

| model | science | news | sports |
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

### Accuracy by difficulty

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

### Human vs. AI questions

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

### Experiment: real Wikipedia texts + memorization trap

25 Turkish Wikipedia texts on KPSS (Turkish civil service exam) topics (CC BY-SA 4.0), plus a version of each with one fact changed (`data/deney_vikipedi.csv`, `scripts/vikipedi_seti.py`). Memorization analysis: `python3 scripts/ezber.py`. Result: none of the 10 models wrote the real, memorized value on the changed texts (memorization = 0); the errors were omissions and inventions.

| model | accuracy | facts (out of 3) | invented numbers | invented names | s/question | $ total | n |
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

### Extra: repeat instability

Aya Expanse 8B and Llama 3.2 3B answered the same 20 questions (balanced sample, seed 42) 3 times each at **temperature 0.7** (`SICAKLIK=0.7 python3 scripts/kos.py api --tekrar 3 --orneklem 20`).

| model | run 1 / 2 / 3 correct | questions whose result changed | instability |
|---|---|---|---|
| aya-expanse-8b | 13 / 13 / 13 (out of 20) | 7 | 35% |
| llama3.2-3b | 9 / 11 / 11 | 13 | 65% |

Aya's total score is the same in all three runs (13/20), but **which** questions it gets right changes on 7 questions. Even when a single run's score looks stable, the result per question depends on chance. That is why the main results use temperature 0, and a single run should not be read as a final measurement.

![model × category](grafikler/1_model_kategori.png)
![accuracy vs cost](grafikler/2_maliyet_dogruluk.png)
![human vs AI](grafikler/3_insan_ai.png)
![hallucination](grafikler/4_halusinasyon.png)

## Interpretation

The Claude models lead by a wide margin: Sonnet and Opus scored 50/50, Haiku 47/50. Among open models the best are Mistral 7B (37/50) and Aya Expanse 8B (33/50), which was trained for 23 languages including Turkish. The errors fall into two types. Qwen, Gemma, Aya and Llama 3.2 drop facts but almost never invent anything. Llama 3.1 8B and Phi-3.5, on the other hand, write names, numbers and dates that are not in the text; Llama 3.1 got no question right and 54% of its summaries contain something invented. Model size alone does not decide: Llama 3.2 3B (21/50) clearly beat the larger Llama 3.1 8B (0/50). Models that write short summaries drop names first, then dates. Claude keeps 92–94% of the facts, so the test is saturated for Claude; prompt v2 ("at most 20 words") should make it discriminative again. A surprising finding: open models do better on "hard" (difficulty 3) questions. In hard questions the critical fact is the main topic of the paragraph; in easy ones the name sits on the side and is the first thing cut when shortening. In the memorization trap built from real Wikipedia texts (with one fact changed), none of the 10 models wrote the memorized true value. So when the text is in front of them, models follow the text; the real risk is not memorization but invention. The human questions have not been added yet, so the human vs. AI comparison is still pending.

## How to run

```bash
# 1) put the questions under data/ (hidden; not in the repo, request access on HF)
python scripts/kontrol.py                 # does the set follow the rules?

# 2) run the models
export OPENROUTER_API_KEY=sk-or-...
python scripts/kos.py api --modeller hepsi
python scripts/kos.py manuel --model gemini-4-carbon-web   # prompt file for a web UI

# 3) score + charts
python scripts/puanla.py                  # → sonuclar/puanli.csv, sonuclar/ozet.md
pip install -r requirements.txt
python scripts/grafik.py                  # → grafikler/*.png

# extras
python scripts/kos.py api --modeller sonnet-5.5 --tekrar 3 --orneklem 20   # repeat / instability
python scripts/kos.py hakem --hakem-model sonnet-5.5 --n 20 && python scripts/uyum.py
```

All scripts use only the standard library; only `grafik.py` needs matplotlib.

## Limitations

- The name check is heuristic: it looks at capitalized words and can give false positives. Every invention flag is visible in `puanli.csv` and can be checked by hand.
- If a model writes both the wrong and the right number ("not 34 but 43 million"), the code passes it. I measure this kind of meaning error separately with a judge model.
- Loss of details other than the 3 critical facts is not measured. This is a faithfulness test, not a summary quality test.

## Files

```
data/ornek.csv          format example (real questions are hidden, in .gitignore)
scripts/ortak.py        prompt, CSV format, Turkish normalization
scripts/kos.py          runs the models (openrouter / ollama / manual / judge)
scripts/puanla.py       scoring by code + summary tables
scripts/grafik.py       charts
scripts/kontrol.py      checks the question set rules
scripts/uyum.py         agreement between judge model and human scores
modeller.json           model list
sonuclar/               raw answers and scores
```
