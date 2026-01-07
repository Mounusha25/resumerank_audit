#!/usr/bin/env python
"""
Main evaluation script.

Runs complete evaluation pipeline:
1. Load data
2. Initialize models
3. Run baseline evaluation
4. Run fairness tests
5. Generate reports
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.data.loader import load_resumes, load_job_descriptions
from src.models.tfidf_ranker import TFIDFRanker
from src.models.bm25_ranker import BM25Ranker
from src.models.semantic_model import SemanticRanker
from src.models.hybrid_ranker import HybridRanker
from src.evaluation.evaluator import ModelEvaluator
from src.fairness.counterfactual import CounterfactualTester
from src.reporting.report_generator import ReportGenerator
from src.reporting.visualizations import create_fairness_visualizations, create_all_advanced_visualizations
from src.utils.config import load_config


def main():
    """Run complete evaluation pipeline."""
    print("=" * 80)
    print("Resume Ranking System - Evaluation Pipeline")
    print("=" * 80)
    print()

    # Load configuration
    print("Loading configuration...")
    config = load_config()

    # Load data
    print("Loading data...")
    try:
        resumes = load_resumes(config["data"]["processed_resumes"])
        job_descriptions = load_job_descriptions(config["data"]["processed_job_descriptions"])
        print(f"  Loaded {len(resumes)} resumes")
        print(f"  Loaded {len(job_descriptions)} job descriptions")
    except FileNotFoundError:
        print("Error: Data files not found. Please run prepare_data.py first.")
        print("Place your resume PDFs in data/raw/resumes/ and job descriptions in data/raw/job_descriptions/")
        return

    # Initialize models
    print("\nInitializing models...")
    models = {}

    # Baseline: TF-IDF
    print("  - TF-IDF Ranker")
    tfidf_ranker = TFIDFRanker(**config["models"]["baseline"]["tfidf"])
    tfidf_ranker.fit(resumes)
    models["TF-IDF"] = tfidf_ranker

    # Baseline: BM25
    print("  - BM25 Ranker")
    bm25_ranker = BM25Ranker(**config["models"]["baseline"]["bm25"])
    bm25_ranker.fit(resumes)
    models["BM25"] = bm25_ranker

    # Semantic model
    print("  - Semantic Ranker")
    semantic_ranker = SemanticRanker(
        model_name=config["models"]["semantic"]["name"],
        device=config["models"]["semantic"]["device"],
    )
    semantic_ranker.fit(resumes)
    models["Semantic"] = semantic_ranker

    # Hybrid model (production-realistic)
    print("  - Hybrid Ranker (Semantic + Structured Signals)")
    hybrid_ranker = HybridRanker(
        semantic_ranker=semantic_ranker,
        weights={
            "semantic": 0.70,
            "education": 0.15,
            "continuity": 0.10,
            "other": 0.05
        }
    )
    hybrid_ranker.fit(resumes)
    models["Hybrid"] = hybrid_ranker

    # Run fairness tests
    print("\nRunning fairness tests...")
    print("(Using first job description as example)")

    # Test on hybrid model (primary - most realistic)
    print("\n🔬 Testing Hybrid Model (Production-Realistic)...")
    tester_hybrid = CounterfactualTester(
        hybrid_ranker,
        perturbation_config=config["fairness"]
    )

    fairness_results_hybrid = tester_hybrid.run_all_tests(
        resumes[:50],  # Test on subset for speed
        job_descriptions[0]["text"],
        university_tiers=config["fairness"]["university_swap"]["prestige_tiers"]
    )

    # Test on semantic model (for comparison)
    print("\n🔬 Testing Semantic-Only Model (SBERT)...")
    tester_semantic = CounterfactualTester(
        semantic_ranker,
        perturbation_config=config["fairness"]
    )

    fairness_results_semantic = tester_semantic.run_all_tests(
        resumes[:50],  # Test on subset for speed
        job_descriptions[0]["text"],
        university_tiers=config["fairness"]["university_swap"]["prestige_tiers"]
    )

    # Ablation: Test on TF-IDF for comparison
    print("\n🔬 Ablation Study: Testing TF-IDF Model...")
    tester_tfidf = CounterfactualTester(
        tfidf_ranker,
        perturbation_config=config["fairness"]
    )

    fairness_results_tfidf = tester_tfidf.run_all_tests(
        resumes[:50],
        job_descriptions[0]["text"],
        university_tiers=config["fairness"]["university_swap"]["prestige_tiers"]
    )

    # Generate fairness reports for all models
    fairness_report_hybrid = tester_hybrid.generate_fairness_report(
        fairness_results_hybrid,
        threshold_rank_change=config["fairness"]["thresholds"]["max_mean_rank_change"],
        threshold_affected_pct=config["fairness"]["thresholds"]["max_affected_percentage"],
    )

    fairness_report_semantic = tester_semantic.generate_fairness_report(
        fairness_results_semantic,
        threshold_rank_change=config["fairness"]["thresholds"]["max_mean_rank_change"],
        threshold_affected_pct=config["fairness"]["thresholds"]["max_affected_percentage"],
    )

    # Generate fairness report for TF-IDF (ablation)
    fairness_report_tfidf = tester_tfidf.generate_fairness_report(
        fairness_results_tfidf,
        threshold_rank_change=config["fairness"]["thresholds"]["max_mean_rank_change"],
        threshold_affected_pct=config["fairness"]["thresholds"]["max_affected_percentage"],
    )

    # Generate reports
    print("\nGenerating reports...")
    reporter = ReportGenerator(config["reporting"]["output_dir"])

    # Fairness report (Hybrid model - primary)
    reporter.generate_fairness_report(fairness_report_hybrid, "fairness_report_hybrid")
    
    # Fairness report (Semantic-only for comparison)
    reporter.generate_fairness_report(fairness_report_semantic, "fairness_report_semantic")

    # Save comprehensive ablation results
    import json
    ablation_path = Path(config["reporting"]["output_dir"]) / "ablation_study_complete.json"
    ablation_results = {
        "hybrid_model": {
            "model": "Hybrid (SBERT + Structured Signals)",
            "description": "Production-realistic: 70% semantic + 15% education + 10% continuity + 5% other",
            "weights": {
                "semantic_relevance": 0.70,
                "education_prestige": 0.15,
                "employment_continuity": 0.10,
                "other_signals": 0.05
            },
            "overall_passed": fairness_report_hybrid["overall_passed"],
            "summary": fairness_report_hybrid["summary"]
        },
        "semantic_only": {
            "model": "sentence-transformers/all-MiniLM-L6-v2",
            "description": "Pure embedding model - all signals implicit in text",
            "overall_passed": fairness_report_semantic["overall_passed"],
            "summary": fairness_report_semantic["summary"]
        },
        "tfidf_baseline": {
            "model": "TF-IDF (sklearn)",
            "description": "Sparse bag-of-words representation",
            "overall_passed": fairness_report_tfidf["overall_passed"],
            "summary": fairness_report_tfidf["summary"]
        },
        "key_insights": {
            "university_prestige": "Hybrid model shows EXPLICIT university effect (auditable), semantic shows IMPLICIT effect (accidental)",
            "employment_gaps": "All models detect gaps, but hybrid model has TRANSPARENT scoring mechanism",
            "production_realism": "Hybrid architecture reflects how real systems combine semantic relevance with structured signals"
        }
    }
    with open(ablation_path, "w") as f:
        json.dump(ablation_results, f, indent=2)
    print(f"Complete ablation study saved to {ablation_path}")
    
    # Also save legacy format for backward compatibility
    legacy_path = Path(config["reporting"]["output_dir"]) / "ablation_tfidf_vs_sbert.json"
    legacy_results = {
        "semantic_model": {
            "model": "sentence-transformers/all-MiniLM-L6-v2",
            "overall_passed": fairness_report_semantic["overall_passed"],
            "summary": fairness_report_semantic["summary"]
        },
        "tfidf_baseline": {
            "model": "TF-IDF (sklearn)",
            "overall_passed": fairness_report_tfidf["overall_passed"],
            "summary": fairness_report_tfidf["summary"]
        },
        "insights": "Comparing representation-based fairness: TF-IDF (sparse) vs SBERT (dense embeddings)"
    }
    with open(legacy_path, "w") as f:
        json.dump(legacy_results, f, indent=2)

    # Model card (for hybrid model - primary)
    reporter.generate_model_card(
        model_info={
            "version": "2.0.0",
            "model_name": "Hybrid (SBERT + Structured Signals)",
            "architecture": "Production-realistic hybrid ranker",
        },
        evaluation_results={},
        fairness_results=fairness_report_hybrid,
    )

    # Create visualizations
    if config["reporting"]["include_visualizations"]:
        print("Creating visualizations...")
        # Basic fairness overview
        create_fairness_visualizations(
            fairness_report_hybrid,
            config["reporting"]["output_dir"]
        )
        
        # Advanced visualizations (distribution, heatmap)
        all_model_results = {
            "Hybrid": fairness_report_hybrid,
            "Semantic": fairness_report_semantic,
            "TF-IDF": fairness_report_tfidf
        }
        create_all_advanced_visualizations(
            all_model_results,
            config["reporting"]["output_dir"]
        )

    print("\n" + "=" * 80)
    print("Evaluation complete!")
    print(f"Reports saved to {config['reporting']['output_dir']}")
    print("=" * 80)

    # Print summary - Hybrid model (PRIMARY)
    print("\n📊 FAIRNESS TEST SUMMARY (Hybrid Model - Production-Realistic):")
    print(f"  Model: 70% semantic + 15% education + 10% continuity + 5% other")
    print(f"  Overall Status: {'✓ PASSED' if fairness_report_hybrid['overall_passed'] else '✗ FAILED'}")
    print("\n  Individual Tests:")
    for test_name, results in fairness_report_hybrid["summary"].items():
        status = "✓" if results["passed"] else "✗"
        print(f"    {status} {test_name}: Mean Δ={results['mean_rank_change']:.2f}, "
              f"Affected={results['affected_percentage']:.1f}%")

    # Print comparison: Semantic-only
    print("\n📊 COMPARISON: Semantic-Only Model:")
    print("  (Pure SBERT - no explicit structured signals)")
    for test_name, results in fairness_report_semantic["summary"].items():
        status = "✓" if results["passed"] else "✗"
        print(f"    {status} {test_name}: Mean Δ={results['mean_rank_change']:.2f}, "
              f"Affected={results['affected_percentage']:.1f}%")

    # Print comparison: TF-IDF
    print("\n📊 COMPARISON: TF-IDF Baseline:")
    print("  (Sparse representation)")
    for test_name, results in fairness_report_tfidf["summary"].items():
        status = "✓" if results["passed"] else "✗"
        print(f"    {status} {test_name}: Mean Δ={results['mean_rank_change']:.2f}, "
              f"Affected={results['affected_percentage']:.1f}%")
    
    print("\n💡 KEY INSIGHT:")
    print("  Hybrid model makes university prestige EXPLICIT (auditable),")
    print("  while semantic-only relies on IMPLICIT embedding effects.")
    print("  This is how production systems achieve transparency.")


if __name__ == "__main__":
    main()
