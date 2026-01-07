# Resume Ranking System - ML Evaluation & Auditing Framework

**Version**: 1.0.0  
**Purpose**: Educational and research evaluation of resume ranking models

---

## ⚠️ Important Disclaimer

This is **NOT** a hiring decision tool. This system is designed for:
- Evaluating semantic similarity models
- Testing fairness under controlled conditions
- Auditing ML system behavior
- Research and educational purposes only

**Do not use this system for actual hiring decisions without proper legal review and compliance validation.**

---

## 🎯 What This System Does

- Ranks resumes against job descriptions using semantic similarity
- Tests ranking stability under counterfactual perturbations
- Measures sensitivity to proxy attributes
- Provides explainability for ranking decisions
- Generates comprehensive fairness audit reports
- **NEW:** Interactive Streamlit app for live demos and auditing
- **NEW:** Ablation study comparing TF-IDF vs SBERT fairness behavior

---

## ✨ Key Features

### 1. Comprehensive Evaluation (400 resumes, 100 JDs)
- Multiple ranking models: TF-IDF, BM25, Semantic (SBERT)
- Ranking metrics: NDCG@k, Precision@k, MRR, Spearman correlation
- No fine-tuning (pretrained embeddings only)

### 2. Fairness Auditing
- **Gender proxy testing:** Pronoun insertion (he/she)
- **Name redaction:** Stability to name removal
- **University prestige:** Elite vs standard institution swaps
- **Employment gaps:** Sensitivity to career breaks
- All tests use synthetic counterfactuals (no real bias labels)

### 3. Ablation Study
- Compares TF-IDF (sparse) vs SBERT (dense embeddings)
- Shows how representation choice affects fairness behavior
- Results: TF-IDF more stable to gaps (Δ=0.08), SBERT to pronouns (Δ=0.00)

### 4. Interactive Demo App
- **Tab 1:** Resume ranking demo (NOT hiring decisions)
- **Tab 2:** Bias & stability audit with counterfactuals
- Makes research tangible and interactive
- See [APP_README.md](APP_README.md) for details

---

## 📁 Project Structure

```
resume_ranking_system/
├── src/
│   ├── data/              # Data processing and preparation
│   ├── models/            # Baseline and semantic models
│   ├── evaluation/        # Metrics and evaluation logic
│   ├── fairness/          # Counterfactual testing
│   ├── explainability/    # Ranking explanations
│   ├── reporting/         # Report generation
│   └── api/               # Optional API layer
├── tests/                 # Test suite
├── data/                  # Data directory (gitignored)
├── config/                # Configuration files
├── notebooks/             # Jupyter notebooks for exploration
├── reports/               # Generated reports
└── scripts/               # Utility scripts
```

---

## 🚀 Quick Start

### Option A: Using CSV Data (Recommended)

```bash
# 1. Setup environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Place your CSV files in project root:
#    - resume_data.csv
#    - job_title_des.csv

# 3. Process data (400 resumes, 100 JDs)
python scripts/csv_quick_start.py

# 4. Run evaluation with ablation study
python scripts/run_evaluation.py

# 5. Launch interactive app
streamlit run app.py
```

### Option B: Using PDF Files

```bash
# 1. Setup environment (same as above)

# 2. Place files in data/raw/
#    - data/raw/resumes/ (PDF files)
#    - data/raw/job_descriptions/ (PDF files)

# 3. Process PDFs
python scripts/prepare_data.py

# 4. Run evaluation
python scripts/run_evaluation.py
```

### 1. Installation

```bash
# Clone the repository
cd resume_ranking_system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

### 2. Prepare Data

```bash
# Place resume PDFs in data/raw/resumes/
# Place job descriptions in data/raw/job_descriptions/

# Run data preparation
python scripts/prepare_data.py
```

### 3. Run Evaluation

```bash
# Run complete evaluation pipeline
python scripts/run_evaluation.py

# Or run specific components
python scripts/run_baseline.py
python scripts/run_fairness_tests.py
python scripts/run_explainability.py
```

### 4. View Reports

```bash
# Open HTML report
open reports/output/fairness_report.html

# Or launch dashboard
streamlit run src/reporting/dashboard.py
```

---

## 📊 Usage Examples

### Basic Ranking

```python
from src.models.semantic_model import SemanticRanker
from src.data.loader import load_resumes, load_job_descriptions

# Load data
resumes = load_resumes("data/processed/resumes.json")
job_desc = load_job_descriptions("data/processed/job_descriptions.json")[0]

# Initialize ranker
ranker = SemanticRanker(model_name="all-MiniLM-L6-v2")

# Rank resumes
rankings = ranker.rank(job_desc, resumes)

for rank, (resume_id, score) in enumerate(rankings, 1):
    print(f"{rank}. Resume {resume_id}: {score:.3f}")
```

### Fairness Testing

```python
from src.fairness.counterfactual import CounterfactualTester

# Initialize tester
tester = CounterfactualTester(ranker)

# Run gender proxy test
results = tester.test_gender_proxy(resumes, job_desc)

print(f"Mean rank change: {results['mean_rank_change']:.2f}")
print(f"Max rank change: {results['max_rank_change']}")
print(f"Affected: {results['affected_percentage']:.1f}%")
```

### Explainability

```python
from src.explainability.ablation import AblationExplainer

# Initialize explainer
explainer = AblationExplainer(ranker)

# Explain ranking for a specific resume
explanation = explainer.explain(resume, job_desc)

for section, contribution in explanation.items():
    print(f"{section}: {contribution:.3f}")
```

---

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test module
pytest tests/test_fairness.py -v
```

---

## 📖 Documentation

- [PROJECT_PROMPT.md](PROJECT_PROMPT.md) - Detailed project specification
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System architecture
- [API_REFERENCE.md](docs/API_REFERENCE.md) - API documentation
- [FAIRNESS_GUIDE.md](docs/FAIRNESS_GUIDE.md) - Fairness testing guide

---

## 🛠️ Configuration

Edit `config/config.yaml` to customize:

```yaml
models:
  semantic:
    name: "all-MiniLM-L6-v2"
    device: "cpu"
  
evaluation:
  metrics:
    - ndcg@5
    - ndcg@10
    - precision@5
    - mrr

fairness:
  perturbations:
    - gender_proxy
    - name_redaction
    - university_swap
    - gap_insertion
  
  thresholds:
    max_rank_change: 5
    max_affected_percentage: 15.0
```

---

## 📈 Evaluation Metrics

- **NDCG@k**: Normalized Discounted Cumulative Gain
- **Precision@k**: Relevance in top-k results
- **MRR**: Mean Reciprocal Rank
- **Spearman ρ**: Ranking correlation

---

## ⚖️ Ethical Guidelines

1. **No Sensitive Attributes**: Never collect or infer race, gender, age, etc.
2. **Transparency**: All assumptions and limitations documented
3. **Evaluation Only**: Results used for audit, not hiring decisions
4. **PII Protection**: Personal information redacted from all data
5. **Clear Communication**: All outputs labeled as evaluation, not recommendations

---

## 🤝 Contributing

This is an educational project. Contributions should focus on:
- Improving evaluation methodology
- Adding fairness tests
- Enhancing explainability
- Better documentation

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

**Legal Note**: This software comes with no warranty and is not validated for employment decisions. Use at your own risk.

---

## 🎤 Citation

If you use this framework in research, please cite:

```bibtex
@software{resume_ranking_eval_2026,
  title={Resume Ranking System: ML Evaluation \& Auditing Framework},
  author={Your Name},
  year={2026},
  version={1.0.0},
  url={https://github.com/yourusername/resume_ranking_system}
}
```

---

## 📞 Contact

For questions about this educational project:
- Open an issue on GitHub
- Email: your.email@example.com

**Remember**: This is an evaluation framework, not a hiring product.
