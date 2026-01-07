# 🚀 Quick Start: Resume Ranking System

## One-Minute Setup

```bash
# 1. Clone & enter directory
git clone https://github.com/Mounusha25/resumerank_audit.git
cd resumerank_audit

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies (20 packages, ~400MB)
pip install -r requirements-deploy.txt

# 4. Run app
streamlit run app.py
```

**App opens at** `http://localhost:8501`

---

## What You'll See

### Tab 1: Ranking Demo
- Pre-filled job description (Senior ML Engineer)
- Top 10 candidates with relevance scores
- Clean table showing semantic similarity

### Tab 2: Fairness Audit ⭐
- **4 Counterfactual Tests**:
  1. Gender Pronoun Swap (he/she)
  2. Name Redaction
  3. University Swap (tier 3 → tier 1)
  4. Employment Gap Insertion (18 months)
- **Metrics**: Rank change (Δ), affected candidates (%)
- **Interpretation**: Guidance for each test

---

## Key Files

| File | Purpose |
|------|---------|
| [app.py](app.py) | Streamlit demo (2 tabs) |
| [src/models/hybrid_ranker.py](src/models/hybrid_ranker.py) | 70/15/10/5 hybrid scorer |
| [scripts/run_evaluation.py](scripts/run_evaluation.py) | Full ablation pipeline |
| [README.md](README.md) | Complete documentation |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Streamlit Cloud guide |

---

## Run Full Evaluation (Optional)

```bash
# Generates 3 HTML reports + 4 visualizations
python scripts/run_evaluation.py

# Outputs in outputs/:
# - hybrid_ranker_fairness_report.html
# - semantic_model_fairness_report.html
# - tfidf_ranker_fairness_report.html
# - fairness_overview.png
# - rank_change_distribution.png
# - model_comparison_heatmap_rank.png
# - model_comparison_heatmap_affected.png
```

**Time**: ~3-5 minutes (400 resumes × 3 models × 4 tests)

---

## Troubleshooting

**Q: Model download slow?**  
A: First run downloads SBERT (all-MiniLM-L6-v2, ~400MB). Cached after.

**Q: Import errors?**  
A: Ensure virtual environment active: `source venv/bin/activate`

**Q: Port 8501 busy?**  
A: Use custom port: `streamlit run app.py --server.port 8502`

---

## Next Steps

1. ✅ **Test locally** — Try all tabs, run evaluation
2. 📤 **Deploy to cloud** — See [DEPLOYMENT.md](DEPLOYMENT.md)
3. 📖 **Read README** — Understand hybrid architecture
4. 🎤 **Prepare demo** — 2-minute walkthrough for interviews

---

**Built for ML engineers shipping responsible AI.** Questions? Open an issue.
