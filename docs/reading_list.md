# Reading List — AM2 Newsletter Automation

Ordered by priority. Start with the foundational pieces before moving to the advanced material. Everything free unless marked 📖.

---

## 1. Transformers — understand the architecture first

**The Illustrated Transformer** — Jay Alammar
The best visual explanation of how transformers work. Read this before any paper.
https://jalammar.github.io/illustrated-transformer/

**Attention Is All You Need** — Vaswani et al. (2017)
The original transformer paper. Dense but worth reading once you've done the illustrated version.
https://arxiv.org/abs/1706.03762

**The Illustrated BERT** — Jay Alammar
How BERT uses the transformer for language understanding. Directly relevant to fine-tuning.
https://jalammar.github.io/illustrated-bert/

**BERT: Pre-training of Deep Bidirectional Transformers** — Devlin et al. (2018)
The BERT paper. Skim the architecture section; read the fine-tuning section carefully.
https://arxiv.org/abs/1810.04805

---

## 2. Sentence Transformers — for embeddings and deduplication

**Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks** — Reimers & Gurevych (2019)
Introduces the sentence transformer approach used in the deduplication task.
https://arxiv.org/abs/1908.10084

**Sentence Transformers documentation**
Practical guide to using the `sentence-transformers` library — models, semantic search, clustering.
https://www.sbert.net/

---

## 3. HuggingFace — the practical toolkit

**HuggingFace NLP Course** (free, interactive)
Chapters 1–4 are essential: pipeline, tokenisers, fine-tuning with Trainer API. This is the hands-on complement to reading the papers.
https://huggingface.co/learn/nlp-course/

**Fine-tuning a pretrained model** — HuggingFace docs
The specific guide for the text classification fine-tuning you'll do in Phase 1.
https://huggingface.co/docs/transformers/training

---

## 4. LLMs and prompt engineering

**Prompt Engineering Guide** — DAIR.AI
Comprehensive, practical. Covers zero-shot, few-shot, chain-of-thought. Read the zero-shot and few-shot sections before building Models 4 and 5.
https://www.promptingguide.ai/

**Anthropic API documentation**
The Claude API docs — messages API, system prompts, structured output. You'll need this to build the LLM classifier.
https://docs.anthropic.com/

**An Introduction to Large Language Models** — Sebastian Raschka (blog)
Clear, technical overview of how LLMs work, how they're trained, and how fine-tuning differs from prompting. Good context before you build the LLM classifiers.
https://magazine.sebastianraschka.com/p/understanding-large-language-models

---

## 5. MLOps and experiment tracking

**MLflow Quickstart**
You'll use this to track all experiments. Read the quickstart and the model tracking guide before Phase 1.
https://mlflow.org/docs/latest/quickstart.html

**Weights & Biases Quickstart** (alternative to MLflow)
W&B has better visualisations; MLflow is simpler to self-host. Pick one before you start experiments.
https://docs.wandb.ai/quickstart

---

## 6. Text classification in practice

**scikit-learn: Working with Text Data**
The definitive guide to TF-IDF + classification pipeline in sklearn. Read before building Model 1.
https://scikit-learn.org/stable/tutorial/text_analytics/working_with_text_data.html

**Natural Language Processing with Transformers** — Tunstall, von Werra, Wolf 📖
The HuggingFace team's book. Chapters 2 (text classification) and 4 (multilingual) are most relevant. Available free online.
https://www.oreilly.com/library/view/natural-language-processing/9781098136789/

---

## 7. Broader AI engineering context

**Designing Machine Learning Systems** — Chip Huyen 📖
The best book on building ML systems in production: data, training, deployment, monitoring. Read chapters on labelling and serving before Phase 4.

**Full Stack Deep Learning — LLM Bootcamp** (free video lectures)
Covers the full stack: prompting, fine-tuning, deployment, evaluation. Very applied.
https://fullstackdeeplearning.com/llm-bootcamp/

---

## Reading order if time is short

1. Illustrated Transformer
2. Illustrated BERT
3. HuggingFace NLP Course chapters 1–4
4. Prompt Engineering Guide (zero-shot + few-shot sections)
5. Sentence Transformers docs
6. MLflow Quickstart
