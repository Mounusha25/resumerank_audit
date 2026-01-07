"""Visualization utilities for reports."""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Dict, Any, List
from pathlib import Path


def create_fairness_visualizations(
    results: Dict[str, Any],
    output_dir: str = "reports/output/"
) -> None:
    """Create visualizations for fairness test results.

    Args:
        results: Fairness test results
        output_dir: Directory to save plots
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Set style
    sns.set_style("whitegrid")

    if "details" not in results:
        return

    # Extract data
    tests = []
    mean_changes = []
    affected_pcts = []

    for test_name, details in results["details"].items():
        tests.append(test_name.replace("_", " ").title())
        mean_changes.append(details["mean_rank_change"])
        affected_pcts.append(details["affected_percentage"])

    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Plot 1: Mean rank changes
    colors = ['#28a745' if mc <= 3.0 else '#dc3545' for mc in mean_changes]
    ax1.barh(tests, mean_changes, color=colors)
    ax1.axvline(x=3.0, color='red', linestyle='--', label='Threshold')
    ax1.set_xlabel('Mean Rank Change')
    ax1.set_title('Mean Rank Change by Test')
    ax1.legend()

    # Plot 2: Affected percentages
    colors = ['#28a745' if ap <= 15.0 else '#dc3545' for ap in affected_pcts]
    ax2.barh(tests, affected_pcts, color=colors)
    ax2.axvline(x=15.0, color='red', linestyle='--', label='Threshold')
    ax2.set_xlabel('Affected Percentage (%)')
    ax2.set_title('Affected Percentage by Test')
    ax2.legend()

    plt.tight_layout()
    plt.savefig(output_path / 'fairness_overview.png', dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Visualization saved to {output_path / 'fairness_overview.png'}")


def create_rank_change_distribution(
    all_results: Dict[str, Dict[str, Any]],
    output_dir: str = "reports/output/"
) -> None:
    """
    Create distribution plots showing rank change spread across models.
    
    This is production-relevant: two models can have the same mean ΔRank
    but very different risk profiles (rare-but-large vs frequent-but-small).
    
    Args:
        all_results: Dict of {model_name: fairness_results}
        output_dir: Directory to save plots
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Prepare data for plotting
    plot_data = []
    
    for model_name, results in all_results.items():
        if "details" not in results:
            continue
            
        for test_name, details in results["details"].items():
            if "rank_changes" in details:
                for rank_change in details["rank_changes"]:
                    plot_data.append({
                        "Model": model_name,
                        "Test": test_name.replace("_", " ").title(),
                        "Rank Change": abs(rank_change)
                    })
    
    if not plot_data:
        print("No rank change data available for distribution plot")
        return
    
    import pandas as pd
    df = pd.DataFrame(plot_data)
    
    # Create figure
    fig, axes = plt.subplots(1, len(all_results), figsize=(6 * len(all_results), 6))
    if len(all_results) == 1:
        axes = [axes]
    
    for idx, (model_name, ax) in enumerate(zip(all_results.keys(), axes)):
        model_data = df[df["Model"] == model_name]
        
        if len(model_data) > 0:
            sns.boxplot(
                data=model_data,
                x="Test",
                y="Rank Change",
                hue="Test",
                ax=ax,
                palette="Set2",
                legend=False
            )
            ax.set_title(f"{model_name}\nRank Change Distribution", fontweight='bold')
            ax.set_xlabel("Test Type")
            ax.set_ylabel("Absolute Rank Change")
            ax.tick_params(axis='x', rotation=45)
            ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path / 'rank_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Distribution plot saved to {output_path / 'rank_distribution.png'}")


def create_model_comparison_heatmap(
    all_results: Dict[str, Dict[str, Any]],
    metric: str = "mean_rank_change",
    output_dir: str = "reports/output/"
) -> None:
    """
    Create heatmap comparing all models across all fairness tests.
    
    Instantly communicates tradeoffs. Very recruiter-friendly.
    
    Args:
        all_results: Dict of {model_name: fairness_results}
        metric: "mean_rank_change" or "affected_percentage"
        output_dir: Directory to save plots
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Extract test names (assuming all models have same tests)
    test_names = []
    for results in all_results.values():
        if "summary" in results:
            test_names = [t.replace("_", " ").title() for t in results["summary"].keys()]
            break
    
    if not test_names:
        print("No test data available for heatmap")
        return
    
    # Build matrix
    matrix = []
    model_names = []
    
    for model_name, results in all_results.items():
        model_names.append(model_name)
        row = []
        
        if "summary" in results:
            for test_name in results["summary"].keys():
                value = results["summary"][test_name].get(metric, 0.0)
                row.append(value)
        
        matrix.append(row)
    
    import pandas as pd
    df = pd.DataFrame(matrix, index=model_names, columns=test_names)
    
    # Create heatmap
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Choose colormap based on metric
    if metric == "mean_rank_change":
        cmap = "YlOrRd"
        fmt = ".2f"
        title = "Mean Rank Change by Model & Test"
    else:
        cmap = "YlOrRd"
        fmt = ".1f"
        title = "Affected Percentage (%) by Model & Test"
    
    sns.heatmap(
        df,
        annot=True,
        fmt=fmt,
        cmap=cmap,
        cbar_kws={'label': metric.replace('_', ' ').title()},
        ax=ax,
        linewidths=0.5,
        linecolor='white'
    )
    
    ax.set_title(title, fontweight='bold', fontsize=14)
    ax.set_xlabel("Fairness Test", fontweight='bold')
    ax.set_ylabel("Model", fontweight='bold')
    
    plt.tight_layout()
    
    # Save with appropriate filename
    if metric == "mean_rank_change":
        filename = "model_comparison_rank_change.png"
    else:
        filename = "model_comparison_affected_pct.png"
    
    plt.savefig(output_path / filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Heatmap saved to {output_path / filename}")


def create_all_advanced_visualizations(
    all_results: Dict[str, Dict[str, Any]],
    output_dir: str = "reports/output/"
) -> None:
    """
    Generate all advanced visualizations for comprehensive analysis.
    
    Args:
        all_results: Dict of {model_name: fairness_results}
        output_dir: Directory to save plots
    """
    print("\nCreating advanced visualizations...")
    
    # 1. Distribution plots (shows risk profiles)
    create_rank_change_distribution(all_results, output_dir)
    
    # 2. Model comparison heatmap (shows tradeoffs)
    create_model_comparison_heatmap(all_results, "mean_rank_change", output_dir)
    create_model_comparison_heatmap(all_results, "affected_percentage", output_dir)
    
    print("✅ Advanced visualizations complete")
