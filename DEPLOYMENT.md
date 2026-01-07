# Deployment Guide

## Quick Deploy to Streamlit Cloud

### 1. Prepare Repository

```bash
# Ensure all changes are committed
git add .
git commit -m "Freeze for deployment"
git push origin main
```

### 2. Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select your repository: `Mounusha25/resumerank_audit`
4. Set:
   - **Main file path**: `app.py`
   - **Python version**: 3.13
   - **Requirements file**: `requirements-deploy.txt`
5. Click "Deploy"

### 3. Configuration

The app uses `.streamlit/config.toml` for theme settings:
- Primary color: #4a5568
- Background: #f8f9fa
- Clean, professional audit interface

### 4. Expected Behavior

**First deploy**: 5-10 minutes (SBERT model download ~400MB)  
**Subsequent deploys**: 2-3 minutes (cached)

**Memory usage**: ~1.2GB (Streamlit Cloud free tier: 1GB limit)  
⚠️ If you hit memory limits, upgrade to Cloud Pro or reduce model size.

---

## Alternative: Local Demo

```bash
# Run locally
source venv/bin/activate
streamlit run app.py

# Accessible at http://localhost:8501
# Share with ngrok (optional):
# pip install pyngrok
# streamlit run app.py & ngrok http 8501
```

---

## Deployment Checklist

- [x] Frozen requirements (`requirements-deploy.txt`)
- [x] Streamlit config (`.streamlit/config.toml`)
- [x] Clean `.gitignore` (exclude venv, large data files)
- [x] README with demo link placeholder
- [ ] Update README with live demo URL after deployment
- [ ] Test all tabs (Ranking Demo, Fairness Audit)
- [ ] Verify disclaimers render correctly

---

## Troubleshooting

**Issue**: Model download timeout  
**Fix**: Increase timeout in `.streamlit/config.toml`:
```toml
[server]
maxUploadSize = 500
```

**Issue**: Memory error on Streamlit Cloud  
**Fix**: Switch to smaller SBERT model:
```python
# In src/models/semantic_model.py
MODEL_NAME = 'all-MiniLM-L6-v2'  # Current (384 dim)
# vs
MODEL_NAME = 'paraphrase-MiniLM-L3-v2'  # Smaller (384 dim, faster)
```

**Issue**: CSV files not loading  
**Fix**: Ensure `data/resume_data.csv` and `data/job_title_des.csv` exist in repo.  
If too large (>100MB), use Git LFS or host externally.

---

## Post-Deployment

1. Test live app (all tabs, sample queries)
2. Update README.md with live URL
3. Take screenshots for portfolio
4. Monitor Streamlit Cloud logs for errors
