#!/bin/bash
# Quick setup script for CSV workflow

echo "==================================================================="
echo "Resume Ranking System - Quick Setup for CSV Data"
echo "==================================================================="
echo

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install pandas pyyaml scikit-learn sentence-transformers rank-bm25 matplotlib seaborn

echo
echo "✅ Dependencies installed!"
echo
echo "Next steps:"
echo "1. Run: python3 scripts/prepare_csv_data.py"
echo "2. Then: python3 scripts/run_evaluation.py"
echo
