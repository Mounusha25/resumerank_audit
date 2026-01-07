# Resume Ranking System - ML Evaluation & Auditing Framework

## 🎯 North Star

**Builds a resume–job description ranking model and systematically tests its fairness, stability, and explainability under controlled counterfactual changes.**

This is **not a hiring product**. It is a **model evaluation + auditing system** focused on behavior, not decisions.

---

## ⚠️ Non-Goals

This project explicitly does **NOT**:
- Predict hiring outcomes
- Automate candidate rejection
- Infer sensitive attributes (race, gender, age, etc.)
- Claim legal or regulatory compliance
- Make hiring recommendations or decisions

---

## 📋 Project Overview

This system evaluates how semantic similarity models rank resumes against job descriptions, with emphasis on:
- **Behavioral audit** of ranking consistency
- **Fairness testing** through controlled perturbations
- **Explainability** of ranking signals
- **Stability analysis** under counterfactual scenarios

**Key Principle**: Pretrained sentence transformers are used without fine-tuning unless explicitly stated; focus is on evaluation, not model training.

---

## 🏗️ Step-by-Step Implementation

### Step 1: Data Collection & Preparation

**Objective**: Create a controlled dataset for evaluation

**Data Components**:
- Resumes (text format: PDF → text extraction)
- Job descriptions
- **Heuristic or weak relevance signals** (if available) — proxy labels used only for evaluation, not ground truth

**Technical Requirements**:
- Parse resumes using PyPDF2 or pdfplumber
- Clean and normalize text (remove special characters, standardize formatting)
- Extract structured fields: skills, experience years, education
- Store in JSON/CSV format with unique IDs
- Create data splits: dev set (for tuning), test set (for final eval)

**Ethical Guardrails**:
- Remove or redact names, addresses, phone numbers
- Do not collect or infer protected attributes
- Document data sources and creation methodology

---

### Step 2: Baseline System

**Objective**: Establish simple, interpretable baselines

**Baseline Methods**:
1. **Keyword Overlap**: TF-IDF cosine similarity
2. **Skill Matching**: Jaccard similarity on extracted skills
3. **BM25**: Classic IR ranking

**Implementation**:
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
```

**Output**: Baseline rankings for each (resume, job_desc) pair

---

### Step 3: Main Semantic Model

**Objective**: Use pretrained embeddings for semantic matching

**Model Selection**:
- **Primary**: `sentence-transformers/all-MiniLM-L6-v2` (lightweight, fast)
- **Alternative**: `sentence-transformers/all-mpnet-base-v2` (more accurate)

**No Fine-Tuning Required**: Pretrained models are used as-is to maintain focus on evaluation infrastructure, not model optimization.

**Implementation**:
```python
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')
resume_emb = model.encode(resumes)
jd_emb = model.encode(job_descriptions)
scores = cosine_similarity(resume_emb, jd_emb)
```

**Output**: Embedding-based similarity scores for ranking

---

### Step 4: Ranking & Evaluation Metrics

**Objective**: Measure ranking quality systematically

**Metrics**:
- **NDCG@k** (Normalized Discounted Cumulative Gain): measures ranking quality
- **Precision@k**: relevance in top-k results
- **MRR** (Mean Reciprocal Rank): position of first relevant result
- **Spearman correlation**: ranking stability across models

**Evaluation Protocol**:
- Compare semantic model vs. baselines
- Test on held-out data
- Measure consistency across job categories

---

### Step 5: Counterfactual Fairness Testing

**Objective**: Test ranking stability under controlled perturbations

**Test Scenarios**:

1. **Gender Proxy Perturbation**:
   - Swap gendered pronouns (he/she → they, or vice versa)
   - Add/remove participation in gender-coded organizations
   - Measure: ΔRank per resume

2. **Name Perturbation**:
   - Redact all names → measure if ranking changes
   - Replace with ethnically neutral placeholders
   - Measure: ranking variance

3. **University Prestige Proxy**:
   - Swap university names (keeping degree constant)
   - Test: Does "Stanford" vs. "State University" change rank?
   - Measure: sensitivity to institution name

4. **Experience Gap Perturbation**:
   - Add/remove 6-month employment gaps
   - Measure: penalty for gaps

**Implementation**:
```python
def create_counterfactual(resume_text, perturbation_type):
    # Apply controlled text transformation
    return modified_resume

delta_rank = rank(original) - rank(counterfactual)
```

**Fairness Metrics**:
- Mean absolute rank change
- Proportion of resumes with |ΔRank| > threshold
- Correlation between perturbation and score change

---

### Step 6: Proxy Attribute Sensitivity Analysis

**Objective**: Measure how much rankings rely on potentially problematic signals

**Analysis**:
- Extract proxy features:
  - University tier (manually coded)
  - Years of experience
  - Industry keywords (finance, tech, etc.)
  - Writing style complexity (readability scores)

- **Regression Analysis**:
  ```python
  from sklearn.linear_model import LinearRegression
  # Predict: rank ~ proxy_features
  # Measure: R² and feature coefficients
  ```

- **Goal**: Identify if rankings are over-reliant on proxies vs. job-relevant skills

---

### Step 7: Explainability Analysis

**Objective**: Understand what drives ranking decisions

**Lightweight Explainability Methods**:

1. **Token/Phrase Contribution Analysis**:
   - Ablation study: remove keywords and measure rank change
   - Identify which resume sections contribute most to score

2. **Attention Visualization** (if using transformer models):
   - Extract attention weights between resume and JD tokens

3. **Stability Analysis**:
   - Measure rank variance under minor text changes
   - Test: Does fixing a typo drastically change rank?

**Optional** (if technically justified):
- SHAP values for embedding-based models
- Integrated gradients for neural ranking models

**Implementation Focus**:
```python
def explain_ranking(resume, job_desc, model):
    # Ablation-based explanation
    baseline_score = model.score(resume, job_desc)
    
    # Remove each section iteratively
    for section in ['skills', 'experience', 'education']:
        modified = remove_section(resume, section)
        delta = baseline_score - model.score(modified, job_desc)
        print(f"{section} contribution: {delta}")
```

---

### Step 8: Stability & Robustness Testing

**Objective**: Ensure rankings are not brittle

**Tests**:
1. **Typo Robustness**:
   - Introduce common typos → measure rank change
   - Expected: minimal change for minor errors

2. **Synonym Replacement**:
   - Replace "managed" → "led" → "oversaw"
   - Test if semantically equivalent changes preserve rank

3. **Formatting Robustness**:
   - Remove bullet points, change spacing
   - Measure: impact on ranking

**Success Criteria**: Rank change < 10% for semantically equivalent changes

---

### Step 9: Reporting & Documentation

**Objective**: Create transparent audit trail

**Deliverables**:

1. **Fairness Report** (JSON/HTML):
   ```json
   {
     "test": "gender_pronoun_swap",
     "mean_rank_change": 2.3,
     "max_rank_change": 15,
     "affected_percentage": 12.5
   }
   ```

2. **Explainability Dashboard**:
   - Top contributing keywords per resume
   - Section importance heatmap
   - Counterfactual comparison viewer

3. **Model Card**:
   - Document intended use
   - Known limitations
   - Fairness test results
   - Evaluation metrics

---

### Step 10: API & Interface (Optional)

**If building an interface**:

```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/rank")
def rank_resumes(job_description: str, resumes: List[str]):
    """
    Returns: Ranked list with scores + explanations
    Does NOT return: Hiring recommendations
    """
    scores = model.score(job_description, resumes)
    explanations = explain_rankings(job_description, resumes)
    return {
        "rankings": sorted(zip(resumes, scores)),
        "explanations": explanations,
        "disclaimer": "For evaluation purposes only. Not a hiring decision tool."
    }
```

**Key API Principles**:
- No "recommend hire/reject" endpoints
- All outputs labeled as "evaluation" not "decision"
- Include confidence intervals and explanation

---

## 🧪 Testing Strategy

**Unit Tests**:
- Data parsing correctness
- Embedding generation
- Ranking metric calculations

**Integration Tests**:
- End-to-end ranking pipeline
- Counterfactual generation accuracy

**Fairness Tests** (Critical):
- Validate perturbations don't change semantics
- Ensure proxy features are correctly extracted
- Test metric calculations

---

## 📊 Success Metrics

This project succeeds when:

1. ✅ Ranking system produces stable, reproducible results
2. ✅ Fairness tests identify specific sensitivity patterns
3. ✅ Explanations are interpretable and verifiable
4. ✅ Documentation clearly states limitations and non-goals
5. ✅ Code is modular, testable, and well-commented

**NOT** measured by:
- ❌ Accuracy at predicting hiring outcomes (not the goal)
- ❌ Commercial viability as a hiring tool
- ❌ Beating SOTA on some benchmark

---

## 🛠️ Technology Stack

**Core Libraries**:
- `sentence-transformers`: Embedding models
- `scikit-learn`: Baseline models, metrics
- `pandas`, `numpy`: Data manipulation
- `pytest`: Testing framework

**Optional**:
- `fastapi`: API layer
- `streamlit`: Visualization dashboard
- `shap`: Explainability (if justified)

**Data Processing**:
- `PyPDF2` or `pdfplumber`: Resume parsing
- `spacy` or `nltk`: Text processing

---

## 🎤 Interview Talking Points

**When asked about this project, emphasize**:

1. **"I built an evaluation system, not a hiring tool"**
   - Shows ethical awareness
   - Demonstrates understanding of ML limitations

2. **"I focused on measuring behavior, not optimizing accuracy"**
   - Shows maturity in ML engineering
   - Avoids overclaiming capability

3. **"Counterfactual testing revealed sensitivity to [specific finding]"**
   - Concrete, specific insight
   - Shows scientific rigor

4. **"I used pretrained models to focus on infrastructure, not model tuning"**
   - Time management
   - Systems thinking

5. **"This taught me how to audit ML systems for unintended behavior"**
   - Generalizable skill
   - Relevant to responsible AI teams

---

## 📝 Ethical Considerations

**Transparency**:
- All assumptions documented
- Limitations clearly stated
- No hidden inference of protected attributes

**Evaluation Focus**:
- System evaluates models, not people
- No deployment as hiring decision tool
- Results used only for research/audit

**Data Handling**:
- PII removed/redacted
- No sensitive attribute collection
- Clear data retention policies

---

## 🚀 Next Steps

1. **Phase 1**: Baseline + semantic model (Days 1-2)
2. **Phase 2**: Evaluation metrics (Day 3)
3. **Phase 3**: Counterfactual testing (Days 4-5)
4. **Phase 4**: Explainability + reporting (Days 6-7)
5. **Phase 5**: Documentation + refinement (Day 8)

---

## 📚 References & Resources

**Key Papers**:
- "Fairness and Abstraction in Sociotechnical Systems" (Selbst et al.)
- "Model Cards for Model Reporting" (Mitchell et al.)
- "Counterfactual Fairness" (Kusner et al.)

**Technical Resources**:
- Sentence-BERT paper (Reimers & Gurevych)
- NDCG metric explanation
- SHAP documentation (if used)

---

## ⚖️ Legal Disclaimer

This project is for **educational and research purposes only**.

- Not validated for employment decisions
- Not compliant with EEOC, GDPR, or other regulations
- No warranty for fairness or accuracy
- Must not be used in production hiring without legal review

---

**Version**: 1.0  
**Last Updated**: January 6, 2026  
**Author**: ML Evaluation Framework for Resume Ranking
