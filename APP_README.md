# Resume Ranking Demo App

**Purpose:** Interactive demo to explore ranking behavior and fairness auditing.

⚠️ **NOT for making hiring decisions** — This is an evaluation and research tool only.

## Features

### Tab 1: Resume Ranking Demo
- Select a job description (from dataset or custom)
- Rank resumes by relevance
- View scores and top matches
- **Label:** "Relevance ranking (demo) — NOT a hiring decision"

### Tab 2: Bias & Stability Audit (Key Differentiator)
- Test individual resumes with counterfactual variants
- Compare side-by-side: original vs perturbed
- Visualize rank/score changes
- Tests available:
  - Gender proxy (he/she pronouns)
  - Name redaction
  - University prestige swap
  - Employment gap insertion

## Quick Start

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Ensure data is processed
python scripts/csv_quick_start.py

# 3. Run Streamlit app
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## What This Shows in Interviews

> "I built a lightweight demo so interviewers could interact with the ranking and fairness audit instead of just reading metrics."

This demonstrates:
- **Engineering completeness:** Can ship, not just analyze
- **User empathy:** Made the system tangible and interactive
- **Confidence:** Shows you understand the system behavior deeply

## Important Boundaries

### ✅ What the app does:
- Demonstrates ranking behavior
- Tests fairness under controlled perturbations
- Provides transparency into model decisions

### ❌ What the app does NOT do:
- Make hiring recommendations
- Optimize resumes
- Automate recruiting decisions
- Provide "pass/fail" scores

## Architecture

- **Frontend:** Streamlit (simple, effective for ML demos)
- **Models:** TF-IDF baseline + SBERT semantic model
- **Fairness:** Counterfactual perturbation testing
- **Scope:** Audit and evaluation only

## Usage in Your Portfolio

Include this statement:

> "Additionally, I built an interactive Streamlit app allowing users to explore ranking behavior and run fairness audits on individual resumes. This makes the research tangible without making hiring recommendations."

This positions you as an ML engineer who:
- Understands productionization
- Values transparency
- Ships complete solutions
- Knows when to stop (maturity signal)
