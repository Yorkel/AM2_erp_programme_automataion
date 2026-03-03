# AM2: ERP Newsletter — Project Overview & Plan

> Part of the Data Science & AI Apprenticeship (AM2 project). The ERP Weekly Newsletter has been manually curated since July 2023. This project semi-automates the curation process using a pipeline of NLP models, freeing the curator to focus on editorial judgement rather than administrative sorting.

---

## 1. The Problem

Two members of the ERP team (programme director + research assistant) spend approximately 7 hours per week:

- Scanning ~55 sources (email newsletters and websites) for relevant articles
- Deciding which newsletter section each article belongs in
- Identifying when multiple sources cover the same story
- Writing short editorial descriptions for each included article
- Compiling and distributing the final newsletter

**Key risks of the current process:**
- Single point of failure — if a curator is unavailable, the newsletter doesn't happen
- Editorial logic is entirely tacit — lives in curators' heads, not documented
- Not scalable — more sources or higher frequency breaks the manual process
- Defined end date — the system must survive the current team

**What this project does NOT do:** Replace the curators. It handles the administrative sorting (gathering, classifying, deduplicating) so the curators focus on what requires human judgement — deciding whether an article is genuinely worth including and writing the editorial voice.

---

## 2. The Newsletter Structure

**Fixed sections (as of early 2026):**

| Section | Label used in models | Content |
|---|---|---|
| Teacher recruitment, retention & development | `teacher_workforce` | Workforce policy, recruitment, retention, CPD |
| EdTech | `edtech` | Technology in education, AI in schools, digital tools |
| Political environment and key organisations | `political_environment` | Government policy, parliamentary activity, sector organisations |
| Four Nations | `four_nations` | Scotland, Wales, Northern Ireland education news |
| Research – Practice – Policy | `research_practice_policy` | Research with clear policy/practice implications |
| What matters in education? | `what_matters` | Inequality, poverty, mental health, broader social context |

*Update from Programme* and *Update from PI [Name]* are internal sections — always manually written, outside the scope of ML classification.

---

## 3. Available Data

### Training data
**`data/processed/newsletter_items_nov.csv`** — 1,668 rows extracted from 87 newsletters (issues 1–87, Oct 2023 – May 2025). Each row is one article, with `theme` (curator-assigned section), `title`, `description` (curator-written summary), and `link`.

After label normalisation (collapsing ~68 raw theme variants into 6 clean labels and removing internal/noise rows): approximately **1,200–1,400 usable labelled examples** across 6 sections.

### Raw newsletters not yet processed
Issues 88–102 are in `data/raw/newsletters_html/` — approximately 180 more labelled examples available once extracted. Extending coverage to ~February 2026.

### External sources
**`x_ERP_newsletter_automation/docs/external_sources.md`** — ~55 sources the curators currently monitor (mix of email newsletters and websites).

See [docs/datasets.md](datasets.md) for full dataset descriptions.

---

## 4. The Two Core ML Tasks

### Task A — Section Classifier (supervised classification)
**Input:** Article title (+ optionally a short text snippet from the source)
**Output:** One of 6 section labels + confidence score
**Type:** Multi-class text classification

This is a supervised learning problem — the curators have already assigned labels to ~1,400 articles. The challenge is short-text classification (titles are short, descriptions are curator-written so can't be used at inference time).

### Task B — Semantic Deduplication (similarity)
**Input:** All candidate articles for the current week
**Output:** Groups of articles covering the same story; one recommended per group
**Type:** Pairwise semantic similarity → clustering

When multiple sources cover the same event, the curators currently read all versions and choose one. The system should surface the duplicate group and rank versions by source authority or description quality.

---

## 5. Model Comparison Plan

The plan is to train and compare multiple approaches for Task A. This is both good practice and demonstrates the full range of NLP techniques relevant to an AI engineer role.

### Step 0 — Label normalisation & data prep
- Collapse 68 raw theme variants into 6 clean labels
- Remove internal programme rows and parsing noise
- Decide: train on `title` only, or `title + description`?
  - **Preference: title only** — at inference time, the curator has a title but has not yet written a description. Using descriptions in training would create a training/inference mismatch.
- Stratified train/validation/test split (e.g. 70/15/15) preserving temporal order where possible
- Establish evaluation metrics: macro F1, per-class precision/recall, confusion matrix

### Model 1 — TF-IDF + Logistic Regression (baseline)
- Fast, interpretable, surprisingly strong on short text
- Establishes the performance floor — all other models must beat this
- Examine which words most strongly predict each section (coefficients)
- **Skills:** classical ML, feature engineering, sklearn pipelines

### Model 2 — Fine-tuned Transformer (DistilBERT / RoBERTa)
- Fine-tune a pre-trained transformer on the 6-section classification task
- Use HuggingFace `transformers` + `Trainer` API
- Experiment with: `distilbert-base-uncased`, `roberta-base`, `bert-base-uncased`
- Techniques to handle small dataset: early stopping, learning rate warmup, weight decay
- **This is the core technical stretch** — demonstrates understanding of attention, tokenisation, fine-tuning, and transfer learning
- **Skills:** HuggingFace, PyTorch, transformer architecture, fine-tuning on small data

### Model 3 — Sentence Transformer + Classifier Head
- Encode each title using a pre-trained sentence transformer (e.g. `all-MiniLM-L6-v2`, `all-mpnet-base-v2`)
- Freeze the encoder; train a lightweight classifier head (MLP or LogReg) on top of the embeddings
- Compare to Model 2: are frozen sentence transformer embeddings good enough, or does full fine-tuning help?
- **Skills:** sentence-transformers, embedding representations, transfer learning without fine-tuning

### Model 4 — Zero-shot LLM (Claude API)
- Use Claude (via Anthropic API) with a carefully engineered prompt: give it the 6 section definitions and ask it to classify each article title
- No training data needed — pure prompt engineering
- Evaluate on the same test set as Models 1–3
- **Skills:** LLM APIs, prompt engineering, zero-shot classification, cost/latency trade-offs

### Model 5 — Few-shot LLM (Claude API)
- Extend Model 4 by including curated examples (3–5 per section) in the prompt
- Experiment with example selection: random vs most similar to the query (RAG-style retrieval)
- Compare zero-shot vs few-shot performance and cost
- **Skills:** few-shot prompting, in-context learning, retrieval-augmented example selection

### Comparison framework
- All models evaluated on the same held-out test set
- Track: macro F1, per-class F1, inference latency, cost (for LLM models)
- Use MLflow or Weights & Biases for experiment tracking — logs hyperparameters, metrics, artefacts
- **Skills:** MLOps, experiment tracking, reproducibility

### Expected outcome
| Model | Expected F1 | Key learning |
|---|---|---|
| TF-IDF + LogReg | 0.70–0.80 | Baseline, interpretability |
| Sentence transformer + head | 0.80–0.88 | Embeddings, transfer learning |
| Fine-tuned DistilBERT | 0.85–0.92 | Full transformer fine-tuning |
| Zero-shot Claude | 0.65–0.80 | LLMs without training data |
| Few-shot Claude | 0.75–0.88 | In-context learning |

*Estimates — actual results will depend on label quality and title length distribution.*

---

## 6. Task B — Semantic Deduplication

- Encode all candidate articles for the week using the sentence transformer selected in Task A
- Compute pairwise cosine similarity
- Group articles with similarity above a threshold (start at 0.85, tune manually)
- For each group, rank versions by: (1) source authority, (2) description richness
- Present groups to the curator for confirmation — they choose one or dismiss the grouping
- **Skills:** vector similarity, clustering, threshold tuning, embedding spaces

---

## 7. Stretch Goal — Newsletter Draft Generation

Once classification and deduplication are done, use an LLM to generate a structured draft:

- Grouped by section (from classifier output)
- One article per section minimum, deduplicated (from Task B)
- Short description per article — generated from article title + scraped body text
- Curator edits the draft, adds their voice, writes the internal sections manually

**Tech:** Claude API with structured prompts, RAG for retrieving article body text where needed.

**Why this matters for an AI engineer portfolio:** This combines classification + embeddings + retrieval + LLM generation into an end-to-end pipeline. It demonstrates you can build production-ready AI systems, not just train individual models.

**Skills:** RAG, structured LLM output, prompt chaining, end-to-end pipeline design

---

## 8. Tech Stack

| Component | Technology |
|---|---|
| Data processing | pandas, BeautifulSoup |
| Baseline classifier | scikit-learn (TF-IDF, LogReg, SVM) |
| Transformer fine-tuning | HuggingFace `transformers`, PyTorch |
| Sentence embeddings | `sentence-transformers` library |
| LLM classification & generation | Anthropic Claude API |
| Experiment tracking | MLflow or Weights & Biases |
| Database | Supabase (shared with AM1 where relevant) |
| Notebook environment | Jupyter |

---

## 9. Implementation Phases

### Phase 0 — Data preparation (do first)
- [ ] Run extraction script on issues 88–102 to extend the labelled dataset
- [ ] Normalise labels: map 68 raw themes → 6 clean labels, remove noise rows
- [ ] Decide on input features: title only vs title + snippet
- [ ] Create train/val/test split
- [ ] Baseline stats: class distribution, average title length, label stability over time

### Phase 1 — Baseline & transformer models
- [ ] Model 1: TF-IDF + LogReg — establish baseline
- [ ] Model 2: Sentence transformer + head
- [ ] Model 3: Fine-tuned DistilBERT
- [ ] Set up MLflow/W&B — log all experiments from the start
- [ ] Compare on held-out test set; document findings

### Phase 2 — LLM models
- [ ] Model 4: Zero-shot Claude API classifier
- [ ] Model 5: Few-shot Claude API classifier
- [ ] Compare cost, latency, accuracy against fine-tuned models
- [ ] Select best overall model for production use

### Phase 3 — Semantic deduplication
- [ ] Implement cosine similarity grouping using chosen embedding model
- [ ] Tune threshold on a small manually-reviewed sample
- [ ] Evaluate precision (are groups real duplicates?) and recall (any missed?)

### Phase 4 — End-to-end pipeline
- [ ] Build pipeline: ingest articles → classify → deduplicate → surface to curator
- [ ] Define the curator interface (Supabase table + simple UI, or structured output file)
- [ ] Curator feedback loop: corrections logged as future training signal

### Phase 5 — Stretch: draft generation
- [ ] Prompt design for section-grouped newsletter draft
- [ ] Evaluate draft quality with curators
- [ ] Integrate article body retrieval (scraping) to improve description quality

---

## 10. Questions to Resolve With Curators

See [docs/process_curators_follow.md](process_curators_follow.md) for the full list. Key ones for model design:

- Does section assignment happen before or after writing the description? (Affects whether we train on title only or title + description)
- How many articles do they review vs include per week? (Defines the scale of the gathering tool)
- What makes one source version preferable over another when deduplicating?
- What would "good enough" output look like — does every suggestion need to be correct, or is a correct-most-of-the-time system with easy human override acceptable?
