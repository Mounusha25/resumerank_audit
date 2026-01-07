#!/bin/bash
# Pre-deployment verification checklist

echo "=== Resume Ranking System - Deployment Verification ==="
echo ""

# Check Python version
echo "✓ Python version:"
python3 --version
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "✓ Virtual environment exists"
else
    echo "✗ Virtual environment not found - run: python3 -m venv venv"
    exit 1
fi

# Check critical files
echo ""
echo "✓ Critical files:"
files=(
    "app.py"
    "requirements-deploy.txt"
    ".streamlit/config.toml"
    ".gitignore"
    "README.md"
    "DEPLOYMENT.md"
    "src/models/hybrid_ranker.py"
    "src/models/semantic_model.py"
    "src/evaluation/fairness_tests.py"
)

for file in "${files[@]}"; do
    if [ -f "$file" ] || [ -d "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file MISSING"
    fi
done

# Check data files
echo ""
echo "✓ Data files:"
if [ -f "data/resume_data.csv" ]; then
    size=$(du -h data/resume_data.csv | cut -f1)
    echo "  ✓ resume_data.csv ($size)"
else
    echo "  ✗ resume_data.csv MISSING"
fi

if [ -f "data/job_title_des.csv" ]; then
    size=$(du -h data/job_title_des.csv | cut -f1)
    echo "  ✓ job_title_des.csv ($size)"
else
    echo "  ✗ job_title_des.csv MISSING"
fi

# Test imports (in virtual environment)
echo ""
echo "✓ Testing core imports:"
source venv/bin/activate

python3 -c "
import sys
try:
    import streamlit
    print('  ✓ streamlit')
except ImportError:
    print('  ✗ streamlit - run: pip install -r requirements-deploy.txt')
    sys.exit(1)

try:
    from sentence_transformers import SentenceTransformer
    print('  ✓ sentence_transformers')
except ImportError:
    print('  ✗ sentence_transformers')
    sys.exit(1)

try:
    import sklearn
    print('  ✓ scikit-learn')
except ImportError:
    print('  ✗ scikit-learn')
    sys.exit(1)

try:
    import pandas
    print('  ✓ pandas')
except ImportError:
    print('  ✗ pandas')
    sys.exit(1)

try:
    import matplotlib
    print('  ✓ matplotlib')
except ImportError:
    print('  ✗ matplotlib')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "=== ALL CHECKS PASSED ==="
    echo ""
    echo "Ready to deploy! Next steps:"
    echo "1. Run: streamlit run app.py (test locally)"
    echo "2. Push to GitHub: git push origin main"
    echo "3. Deploy on share.streamlit.io"
    echo "4. Update README.md with live demo URL"
else
    echo ""
    echo "=== CHECKS FAILED ==="
    echo "Fix the issues above before deploying"
    exit 1
fi
