# Getting Started with Resume Ranking System

## Quick Start Guide

### 1. Installation

```bash
# Clone or navigate to project directory
cd resume_ranking_system

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model (optional, for advanced NER)
python -m spacy download en_core_web_sm
```

### 2. Prepare Your Data

**Resumes:**
- Place resume PDFs in `data/raw/resumes/`
- Supported format: PDF
- Recommended: 10-100 resumes for meaningful evaluation

**Job Descriptions:**
- Place job description files in `data/raw/job_descriptions/`
- Supported formats: `.txt` or `.pdf`
- Can start with just 1-2 job descriptions

**Process the data:**
```bash
python scripts/prepare_data.py
```

This will:
- Parse PDFs
- Extract text
- Redact PII
- Save to `data/processed/`

### 3. Run Basic Example

```bash
python scripts/example_usage.py
```

This demonstrates:
- Ranking resumes
- Fairness testing
- Explainability

### 4. Run Full Evaluation

```bash
python scripts/run_evaluation.py
```

This will:
- Initialize all models (TF-IDF, BM25, Semantic)
- Run fairness tests
- Generate reports in `reports/output/`

### 5. View Results

Open the generated reports:
- `reports/output/fairness_report.html` - Interactive fairness report
- `reports/output/model_card.md` - Model documentation
- `reports/output/fairness_overview.png` - Visualization

## Configuration

Edit `config/config.yaml` to customize:

```yaml
models:
  semantic:
    name: "sentence-transformers/all-MiniLM-L6-v2"  # Change model
    device: "cpu"  # or "cuda" for GPU

fairness:
  thresholds:
    max_mean_rank_change: 3.0  # Adjust thresholds
    max_affected_percentage: 15.0
```

## Common Use Cases

### Testing a Single Resume

```python
from src.models.semantic_model import SemanticRanker

ranker = SemanticRanker()

resume = {"id": "test", "text": "Your resume text here"}
job_desc = "Your job description here"

score = ranker.score(resume, job_desc)
print(f"Similarity score: {score:.4f}")
```

### Running Custom Fairness Test

```python
from src.fairness.counterfactual import CounterfactualTester

tester = CounterfactualTester(ranker)

results = tester.test_gender_proxy(resumes, job_description)
print(f"Mean rank change: {results['mean_rank_change']}")
```

### Explaining Rankings

```python
from src.explainability.ablation import AblationExplainer

explainer = AblationExplainer(ranker)

explanation = explainer.explain(resume, job_description)
for section, contribution in explanation.items():
    print(f"{section}: {contribution:.4f}")
```

## Troubleshooting

**Error: "Data files not found"**
- Make sure you've run `prepare_data.py` first
- Check that PDFs are in `data/raw/resumes/`

**Error: "CUDA not available"**
- Set `device: "cpu"` in `config/config.yaml`
- Or install PyTorch with CUDA support

**Slow processing**
- Reduce number of resumes in test set
- Use smaller model: `all-MiniLM-L6-v2` instead of `all-mpnet-base-v2`
- Enable GPU if available

## Next Steps

1. **Customize perturbations**: Edit `config/config.yaml` fairness section
2. **Add more tests**: Create custom perturbations in `src/fairness/perturbations.py`
3. **Tune thresholds**: Adjust fairness thresholds based on your requirements
4. **Integrate with existing systems**: Use the API components (see API docs)

## Important Reminders

⚠️ **This is an evaluation tool, NOT a hiring system**
- Do not use for actual hiring decisions
- Results are for research and audit purposes only
- Consult legal counsel before any production use

## Getting Help

- Check the [README.md](README.md) for full documentation
- Review [PROJECT_PROMPT.md](PROJECT_PROMPT.md) for detailed specifications
- Open an issue on GitHub for bugs or questions
