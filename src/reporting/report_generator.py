"""Generate comprehensive evaluation reports."""

import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


class ReportGenerator:
    """Generate evaluation and fairness reports."""

    def __init__(self, output_dir: str = "reports/output/"):
        """Initialize report generator.

        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_fairness_report(
        self,
        results: Dict[str, Any],
        filename: str = "fairness_report",
    ) -> None:
        """Generate fairness test report.

        Args:
            results: Fairness test results
            filename: Output filename (without extension)
        """
        # Save JSON
        json_path = self.output_dir / f"{filename}.json"
        with open(json_path, "w") as f:
            json.dump(results, f, indent=2)

        # Generate HTML
        html_path = self.output_dir / f"{filename}.html"
        html_content = self._generate_fairness_html(results)

        with open(html_path, "w") as f:
            f.write(html_content)

        print(f"Fairness report saved to {html_path}")

    def _generate_fairness_html(self, results: Dict[str, Any]) -> str:
        """Generate HTML fairness report.

        Args:
            results: Fairness test results

        Returns:
            HTML content
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Fairness Evaluation Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1, h2 {{
            color: #333;
        }}
        .disclaimer {{
            background-color: #fff3cd;
            border: 1px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .summary {{
            background-color: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .test-result {{
            background-color: white;
            padding: 20px;
            margin: 15px 0;
            border-radius: 5px;
            border-left: 4px solid #ccc;
        }}
        .passed {{
            border-left-color: #28a745;
        }}
        .failed {{
            border-left-color: #dc3545;
        }}
        .metric {{
            display: inline-block;
            padding: 10px 15px;
            margin: 5px;
            background-color: #f8f9fa;
            border-radius: 3px;
        }}
        .metric-label {{
            font-weight: bold;
            color: #666;
        }}
        .metric-value {{
            color: #333;
            font-size: 1.2em;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f8f9fa;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <h1>Resume Ranking System - Fairness Evaluation Report</h1>

    <div class="disclaimer">
        <strong>⚠️ IMPORTANT DISCLAIMER:</strong>
        This report evaluates model behavior under controlled perturbations.
        It does NOT make hiring recommendations and should NOT be used for employment decisions.
        This is an evaluation and auditing tool only.
    </div>

    <div class="summary">
        <h2>Report Summary</h2>
        <p><strong>Generated:</strong> {timestamp}</p>
        <p><strong>Overall Status:</strong> 
            <span style="color: {'#28a745' if results.get('overall_passed', False) else '#dc3545'}; font-weight: bold;">
                {'PASSED' if results.get('overall_passed', False) else 'FAILED'}
            </span>
        </p>
    </div>
"""

        # Add test results
        if "summary" in results:
            for test_name, test_info in results["summary"].items():
                passed = test_info["passed"]
                status_class = "passed" if passed else "failed"

                html += f"""
    <div class="test-result {status_class}">
        <h3>{test_name.replace('_', ' ').title()}</h3>
        <p><strong>Status:</strong> <span style="color: {'#28a745' if passed else '#dc3545'};">
            {'✓ PASSED' if passed else '✗ FAILED'}
        </span></p>

        <div class="metric">
            <span class="metric-label">Mean Rank Change:</span>
            <span class="metric-value">{test_info['mean_rank_change']:.2f}</span>
        </div>

        <div class="metric">
            <span class="metric-label">Affected Percentage:</span>
            <span class="metric-value">{test_info['affected_percentage']:.1f}%</span>
        </div>
"""

                if test_info.get("issues"):
                    html += "<h4>Issues Identified:</h4><ul>"
                    for issue in test_info["issues"]:
                        html += f"<li>{issue}</li>"
                    html += "</ul>"

                html += "</div>"

        # Add detailed results table
        if "details" in results:
            html += """
    <div class="summary">
        <h2>Detailed Test Results</h2>
        <table>
            <tr>
                <th>Test</th>
                <th>Mean Rank Change</th>
                <th>Max Rank Change</th>
                <th>Affected %</th>
                <th>Std Dev</th>
            </tr>
"""

            for test_name, details in results["details"].items():
                html += f"""
            <tr>
                <td>{test_name.replace('_', ' ').title()}</td>
                <td>{details['mean_rank_change']:.2f}</td>
                <td>{details['max_rank_change']}</td>
                <td>{details['affected_percentage']:.1f}%</td>
                <td>{details.get('std_rank_change', 0):.2f}</td>
            </tr>
"""

            html += """
        </table>
    </div>
"""

        html += """
    <div class="summary">
        <h2>Interpretation Guidelines</h2>
        <ul>
            <li><strong>Mean Rank Change:</strong> Average change in rank position after perturbation. Lower is better.</li>
            <li><strong>Affected Percentage:</strong> Percentage of resumes with rank change > 5 positions. Lower is better.</li>
            <li><strong>Pass Criteria:</strong> Mean rank change ≤ 3.0 AND affected percentage ≤ 15.0%</li>
        </ul>

        <h3>What This Means</h3>
        <p>
            Tests that PASS indicate the model is relatively stable under that type of perturbation.
            Tests that FAIL suggest the model may be sensitive to proxy attributes that could correlate
            with protected characteristics.
        </p>
    </div>

    <div class="disclaimer">
        <h3>Legal & Ethical Notes</h3>
        <ul>
            <li>This report is for evaluation purposes only</li>
            <li>Passing all tests does NOT guarantee legal compliance</li>
            <li>No sensitive attributes were inferred or predicted</li>
            <li>Consult legal counsel before using any ranking system for hiring</li>
        </ul>
    </div>
</body>
</html>
"""

        return html

    def generate_model_card(
        self,
        model_info: Dict[str, Any],
        evaluation_results: Dict[str, Any],
        fairness_results: Dict[str, Any],
        filename: str = "model_card.md",
    ) -> None:
        """Generate model card documentation.

        Args:
            model_info: Model configuration and metadata
            evaluation_results: Evaluation metrics
            fairness_results: Fairness test results
            filename: Output filename
        """
        card_path = self.output_dir / filename

        content = f"""# Model Card: Resume Ranking System

**Version:** {model_info.get('version', '1.0.0')}
**Date:** {datetime.now().strftime('%Y-%m-%d')}
**Model Type:** Semantic Similarity Ranking

---

## Model Details

**Purpose:** Evaluation and auditing of resume ranking models for research and educational purposes.

**Model Architecture:** {model_info.get('model_name', 'sentence-transformers/all-MiniLM-L6-v2')}

**Training:** NO FINE-TUNING. Uses pretrained embeddings only.

---

## Intended Use

### ✅ Appropriate Use Cases
- Evaluating semantic similarity models
- Testing fairness under controlled conditions
- Research on ranking system behavior
- Educational demonstrations

### ❌ Inappropriate Use Cases
- Making actual hiring decisions
- Automating candidate selection
- Any production hiring system
- Generating hiring recommendations

---

## Performance Metrics

"""

        # Add evaluation metrics
        if evaluation_results:
            content += "### Evaluation Results\n\n"
            for model_name, metrics in evaluation_results.items():
                content += f"**{model_name}:**\n"
                for metric_name, value in metrics.items():
                    content += f"- {metric_name}: {value:.4f}\n"
                content += "\n"

        # Add fairness results
        if fairness_results:
            content += "### Fairness Test Results\n\n"
            if "summary" in fairness_results:
                for test_name, results in fairness_results["summary"].items():
                    status = "✓ PASSED" if results["passed"] else "✗ FAILED"
                    content += f"**{test_name}:** {status}\n"
                    content += f"- Mean Rank Change: {results['mean_rank_change']:.2f}\n"
                    content += f"- Affected Percentage: {results['affected_percentage']:.1f}%\n\n"

        content += """
---

## Limitations

1. **No Ground Truth:** Evaluation uses weak/heuristic labels, not actual hiring outcomes
2. **Proxy Attributes:** Testing is limited to known proxy attributes
3. **Coverage:** Cannot test all possible fairness dimensions
4. **Context:** Performance may vary across job types and industries
5. **No Fine-Tuning:** Using pretrained embeddings may not be optimal for all domains

---

## Ethical Considerations

### Privacy
- PII is redacted from all resumes
- No collection of sensitive attributes
- No inference of protected characteristics

### Fairness
- Tested for stability under controlled perturbations
- No guarantees of legal compliance
- Results are descriptive, not prescriptive

### Transparency
- All assumptions documented
- Open methodology
- Clear scope limitations

---

## Recommendations

1. **Do NOT use for hiring:** This is an evaluation tool only
2. **Interpret carefully:** Fairness tests show behavior, not compliance
3. **Seek legal review:** Before any production use
4. **Continue monitoring:** Fairness is an ongoing process
5. **Update regularly:** As models and data evolve

---

## Contact

For questions about this evaluation framework:
- GitHub: [Your Repository]
- Email: [Your Email]

---

## License

MIT License - See LICENSE file

---

**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}
"""

        with open(card_path, "w") as f:
            f.write(content)

        print(f"Model card saved to {card_path}")
