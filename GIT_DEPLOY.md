# Git Setup & Deployment Commands

## First-Time Setup

```bash
# Initialize git (if not already done)
git init

# Add remote
git remote add origin https://github.com/Mounusha25/resumerank_audit.git

# Check current branch
git branch -M main

# Stage all files
git add .

# Commit with freeze message
git commit -m "v2.0: Production-ready hybrid ML fairness auditor

- Hybrid ranker (70% semantic + 15% education + 10% continuity + 5% reserved)
- 4 counterfactual fairness tests (gender, name, university, gap)
- 3-way ablation study (Hybrid vs Semantic vs TF-IDF)
- Advanced visualizations (boxplots, heatmaps)
- Streamlit audit demo (9.8/10 quality)
- Complete documentation & deployment assets

Key result: University swap Δ=1.76 (hybrid) vs Δ=0.00 (semantic)
Makes implicit biases explicit and measurable."

# Push to GitHub
git push -u origin main
```

---

## Deploy to Streamlit Cloud

After pushing to GitHub:

1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Sign in with GitHub
3. Click **"New app"**
4. Configure:
   - **Repository**: `Mounusha25/resumerank_audit`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **Python version**: `3.13`
   - **Requirements file**: `requirements-deploy.txt`
5. Click **"Deploy"**

**First deploy time**: 5-10 minutes (SBERT model download ~400MB)

---

## After Deployment

### Update README with Live URL

Once Streamlit gives you the URL (e.g., `https://resumerank-audit.streamlit.app`):

```bash
# Edit README.md - replace:
# **[🚀 Live Demo](#)** *(Deploy to get URL)*

# With:
# **[🚀 Live Demo](https://your-app-url.streamlit.app)**

git add README.md
git commit -m "Add live demo URL"
git push
```

---

## Quick Commands Reference

```bash
# Check git status
git status

# View commit history
git log --oneline

# Create .gitignore for sensitive data
echo "data/*.csv" >> .gitignore
echo "outputs/*.html" >> .gitignore

# Force push (CAREFUL - overwrites remote)
git push -f origin main

# Clone to another machine
git clone https://github.com/Mounusha25/resumerank_audit.git
cd resumerank_audit
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-deploy.txt
streamlit run app.py
```

---

## Troubleshooting

**Issue**: "fatal: remote origin already exists"  
**Fix**: `git remote remove origin` then re-add

**Issue**: Large files (>100MB) rejected  
**Fix**: Use Git LFS or exclude from repo:
```bash
# Add to .gitignore
echo "data/resume_data.csv" >> .gitignore
echo "data/job_title_des.csv" >> .gitignore
git rm --cached data/*.csv
git commit -m "Remove large CSV files"
```

**Issue**: Streamlit Cloud out of memory  
**Fix**: Upgrade to Cloud Pro or reduce model size in [semantic_model.py](src/models/semantic_model.py)

---

## Repository URL

**GitHub**: https://github.com/Mounusha25/resumerank_audit  
**Streamlit Cloud**: *(Add after deployment)*

---

**Ready to ship!** 🚀
