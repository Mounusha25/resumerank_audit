# Resume Ranking System: Hybrid ML Fairness Audit

> **Production Insight**: *Pure embedding models under-represent structured hiring signals. This project demonstrates a production-realistic hybrid architecture that makes implicit biases **explicit and measurable**.*

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.41+-red.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**[🚀 Live Demo](https://resumerankaudit.streamlit.app/)** | **[📊 Sample Report](outputs/hybrid_ranker_fairness_report.html)**

---

## Why This Project Matters

**The Problem**: Most resume ranking demos use pure semantic embeddings (SBERT, BERT). In production hiring systems, structured signals like university prestige and employment continuity **silently influence rankings**. Pure embedding models make these biases **invisible** to auditors.

**The Solution**: A hybrid architecture that:
- ✅ **Makes signals explicit** (70% semantic + 15% education + 10% continuity + 5% reserved)
- ✅ **Enables counterfactual testing** (swap universities, redact names, insert gaps)
- ✅ **Surfaces real risks** (education tier changes rank by **Δ=1.76 positions**)

**The Impact**: Built for ML engineers shipping responsible hiring tools — where fairness audits are non-negotiable.

---

## Architecture: Production-Realistic Hybrid Ranker

### Component Breakdown

```python
WEIGHTS = {
    'semantic_relevance': 0.70,  # Job-resume similarity (SBERT all-MiniLM-L6-v2)
    'education_prestige': 0.15,  # Explicit university tier mapping
    'employment_continuity': 0.10, # Gap detection via pattern matching
    'other_signals': 0.05          # Reserved for future signals
}

UNIVERSITY_TIERS = {
    'Elite': 1.0,      # MIT, Stanford, CMU, Berkeley, etc.
    'Strong': 0.85,    # UT Austin, Georgia Tech, Purdue, etc.
    'Standard': 0.6,   # State universities, regional colleges
    'Unknown': 0.4     # Unrecognized or missing institutions
}
```

**Key Design Choice**: Unlike pure embedding models where university effect is **accidental** (leaks through semantic similarity), this hybrid makes education prestige an **auditable, controllable parameter**.

### Why Hybrid > Pure Embeddings?

| Test | Hybrid Ranker | Semantic-Only | TF-IDF Baseline |
|------|---------------|---------------|-----------------|
| **University Swap** | Δ=**1.76** (4% affected) | Δ=0.00 (0%) | Δ=0.00 (0%) |
| **Pronoun Swap** | Δ=0.62 (2% affected) | Δ=0.58 (2%) | Δ=0.00 (0%) |
| **Name Redaction** | Δ=0.84 (3% affected) | Δ=0.79 (3%) | Δ=0.00 (0%) |
| **Gap Insertion** | Δ=**2.14** (5% affected) | Δ=0.00 (0%) | Δ=0.00 (0%) |

**Interpretation**:
- **Hybrid detects structural bias** (university swap: Δ=1.76 vs 0.00)
- **Semantic misses structured signals** (gap insertion: Δ=0.00 vs 2.14)
- **TF-IDF lacks semantic understanding** (pronoun swap: Δ=0.00 vs 0.62)

> **Interview Insight**: "I chose hybrid architecture because production hiring systems combine semantic understanding with explicit structured signals. Pure embeddings under-represent education and continuity biases that real stakeholders care about measuring."

---

## Fairness Testing Framework

### Counterfactual Interventions

| Intervention | Purpose | Implementation |
|--------------|---------|----------------|
| **Gender Pronoun Swap** | Test gender bias | Replace he/she/him/her across resumes |
| **Name Redaction** | Test name-based bias | Remove candidate names entirely |
| **University Swap** | Test education prestige | Replace tier 3 → tier 1 universities |
| **Employment Gap** | Test continuity penalty | Insert 18-month career gap |

### Metrics Dashboard

Each test generates:
- **Rank Change Distribution** (boxplots showing risk profiles)
- **Affected Candidates %** (scope of impact)
- **Model Comparison Heatmap** (3 models × 4 tests)
- **Per-Resume Explanations** (transparency for auditors)

---

## Demo: Streamlit Audit Interface

**Philosophy**: Built as **internal ML tooling**, not a hiring product. Clean, analytical, with non-negotiable disclaimers.

### Features

**Tab 1: Ranking Demo** *(Context)*
- Pre-filled job description (Senior ML Engineer)
- Top 10 candidates with relevance scores
- Note: "Semantic similarity alone ≠ job fit"

**Tab 2: Fairness Audit** *(Primary Feature)*
- 4 counterfactual tests with baseline comparison
- Rank change metrics + affected candidates %
- Interpretation guidance for each test
- Disclaimer: Research tool only, not production system

**Design**: Neutral theme (#f8f9fa background, #4a5568 accents), no gamification, calm typography.

---

## Dataset & Evaluation

- **400 Resumes** (software engineering roles, varied experience)
- **100 Job Descriptions** (ML Engineer, Data Scientist, SWE)
- **Evaluation**: 3-way ablation study (Hybrid, Semantic-Only, TF-IDF)
- **Outputs**: HTML reports, JSON results, 4 visualizations

### Running Full Evaluation

```bash
# Activate environment
source venv/bin/activate

# Run complete pipeline (3 models × 4 tests = 12 experiments)
python scripts/run_evaluation.py

# Outputs generated in outputs/:
# - hybrid_ranker_fairness_report.html
# - semantic_model_fairness_report.html
# - tfidf_ranker_fairness_report.html
# - ablation_study_complete.json
# - fairness_overview.png
# - rank_change_distribution.png
# - model_comparison_heatmap_rank.png
# - model_comparison_heatmap_affected.png
```

---

## Setup & Installation

### Prerequisites
- Python 3.13+
- 2GB RAM (for SBERT model download)

### Quick Start

```bash
# Clone repository
git clone https://github.com/Mounusha25/resumerank_audit.git
cd resumerank_audit

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-deploy.txt

# Run Streamlit app
streamlit run app.py
```

App opens at `http://localhost:8501`

### Project Structure

```
resume_ranking_system/
├── app.py                          # Streamlit fairness audit demo
├── src/
│   ├── models/
│   │   ├── hybrid_ranker.py       # Production-realistic hybrid scorer
│   │   ├── semantic_model.py      # SBERT embedding baseline
│   │   └── tfidf_ranker.py        # Keyword-matching baseline
│   ├── evaluation/
│   │   ├── fairness_tests.py      # Counterfactual test suite
│   │   └── perturbations.py       # Data augmentation functions
│   └── reporting/
│       └── visualizations.py      # Boxplots, heatmaps, overview
├── scripts/
│   └── run_evaluation.py          # Full ablation pipeline
├── outputs/                        # Generated reports & plots
├── data/
│   ├── resume_data.csv            # Candidate profiles
│   └── job_title_des.csv          # Job descriptions
└── docs/                           # Architecture & design references
```

---

## Key Innovations

### 1. **Explicit Structured Signals**
```python
# NOT this (implicit, unauditable):
score = cosine_similarity(resume_embedding, jd_embedding)

# THIS (explicit, controllable):
score = (
    0.70 * semantic_similarity +
    0.15 * education_tier_lookup(university) +
    0.10 * continuity_score(gap_detection) +
    0.05 * reserved_signals
)
```

### 2. **Tier-Based Education Scoring**
```python
def _calculate_education_score(self, resume_text):
    for tier, institutions in UNIVERSITY_TIERS.items():
        if any(uni.lower() in resume_text.lower() for uni in institutions):
            return tier_weights[tier]  # 1.0, 0.85, 0.6, 0.4
    return 0.4  # Unknown default
```

### 3. **Pattern-Based Gap Detection**
```python
def _calculate_continuity_score(self, resume_text):
    gap_patterns = [
        r'\bgap\b', r'\bbreak\b', r'\bunemployed\b',
        r'\d{4}\s*-\s*\d{4}.*gap', r'career break'
    ]
    if any(re.search(p, resume_text, re.I) for p in gap_patterns):
        return 0.5  # Penalty for detected gaps
    return 1.0  # Full score for continuity
```

---

## Interview Positioning

**Q: Why build this instead of just using SBERT?**

> "Production hiring systems combine semantic understanding with structured signals like education and employment history. I wanted to measure fairness **at the architecture level** — can we audit a system where prestige effects are explicit vs accidental? The hybrid design makes counterfactual testing meaningful: swapping MIT↔Unknown actually changes rankings (Δ=1.76), whereas pure embeddings can't measure this (Δ=0.00)."

**Q: What's the hardest part of fairness auditing?**

> "**Defining the counterfactual**. For university swap, I had to choose: do we replace text mentions only, or simulate candidate pool shifts? I chose text replacement to isolate the scoring mechanism. For gender, pronoun swap is imperfect (misses implicit signals in writing style), but it's transparent and reproducible. The key is documenting limitations upfront."

**Q: How would you productionize this?**

> "Three changes:
> 1. **Configurable weights**: Move 70/15/10/5 to YAML so stakeholders can run sensitivity analysis
> 2. **Audit logs**: Track every ranking with component scores (semantic vs education vs continuity)
> 3. **Threshold alerts**: Flag candidates where education/continuity signals dominate semantic fit (e.g., education > 40% of total score)
>
> The goal isn't to eliminate structured signals — it's to make them **visible, tunable, and accountable**."

---

## Limitations & Future Work

### Known Limitations
1. **Coarse Education Tiers**: 4-tier mapping is subjective; production needs finer granularity
2. **Gap Detection**: Pattern matching misses nuanced career narratives (sabbaticals, consulting)
3. **No Fine-Tuning**: SBERT is pretrained-only; domain adaptation could improve semantic fit
4. **Static Weights**: 70/15/10/5 split is fixed; stakeholders may want dynamic weighting

### Extensions
- [ ] A/B test different weight configurations (70/15/10/5 vs 60/20/15/5)
- [ ] Add skill extraction signal (years of Python, TensorFlow, etc.)
- [ ] Integrate explainability (LIME/SHAP for semantic component)
- [ ] Expand to multimodal inputs (resumes + LinkedIn + GitHub)

---

## Technical Stack

| Component | Technology | Justification |
|-----------|------------|---------------|
| **Embeddings** | SBERT (all-MiniLM-L6-v2) | Lightweight, 384-dim, strong zero-shot performance |
| **Baseline** | TF-IDF + Cosine | Classic IR baseline for comparison |
| **Scoring** | Weighted Hybrid | Explicit signals > implicit embeddings |
| **Testing** | Counterfactual Interventions | Gold standard for fairness auditing |
| **Visualization** | Seaborn + Matplotlib | Boxplots (risk profiles), heatmaps (model comparison) |
| **Demo** | Streamlit | Fast iteration, built-in caching, clean UI |

---

## Citation

If you use this project in your research or work, please cite:

```bibtex
@software{resume_ranking_hybrid,
  author = {Mounusha},
  title = {Resume Ranking System: Hybrid ML Fairness Audit},
  year = {2025},
  url = {https://github.com/Mounusha25/resumerank_audit}
}
```

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

## Acknowledgments

- **SBERT**: Reimers & Gurevych, "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks" (2019)
- **Fairness Testing**: Inspired by counterfactual frameworks in "Fairness and Abstraction in Sociotechnical Systems" (Selbst et al., 2019)
- **Hybrid Architecture**: Motivated by production ML at hiring platforms (Lever, Greenhouse, etc.)

---

**Built for ML engineers who ship responsible AI systems.** Questions? Open an issue or reach out.
