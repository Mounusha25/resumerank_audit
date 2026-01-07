"""Model evaluator for comparing ranking models."""

from typing import List, Dict, Any, Optional
import numpy as np
from .metrics import RankingMetrics


class ModelEvaluator:
    """Evaluate and compare ranking models."""

    def __init__(self, k_values: List[int] = [5, 10]):
        """Initialize evaluator.

        Args:
            k_values: List of k values for @k metrics
        """
        self.metrics_calculator = RankingMetrics(k_values=k_values)
        self.results = {}

    def evaluate_model(
        self,
        model_name: str,
        model: Any,
        test_data: List[Dict[str, Any]],
        weak_labels: Optional[Dict[str, Dict[str, float]]] = None,
    ) -> Dict[str, float]:
        """Evaluate a ranking model.

        Args:
            model_name: Name of the model
            model: Ranking model instance
            test_data: Test dataset
            weak_labels: Optional weak relevance labels

        Returns:
            Dictionary of metrics
        """
        if weak_labels is None:
            # Cannot compute metrics without labels
            print(f"Warning: No labels provided for {model_name}. "
                  "Evaluation metrics require heuristic or weak labels.")
            return {}

        all_metrics = []

        # Evaluate on each job description
        for job_data in test_data:
            job_id = job_data["id"]
            job_text = job_data["text"]

            # Get rankings
            rankings = model.rank(job_text, top_k=None)

            # Get true labels if available
            if job_id in weak_labels:
                y_true = []
                y_pred = []

                for resume_id, pred_score in rankings:
                    if resume_id in weak_labels[job_id]:
                        y_true.append(weak_labels[job_id][resume_id])
                        y_pred.append(pred_score)

                # Compute metrics
                if y_true:
                    metrics = self.metrics_calculator.compute_all(y_true, y_pred)
                    all_metrics.append(metrics)

        # Average metrics across all jobs
        if not all_metrics:
            return {}

        avg_metrics = {}
        for metric_name in all_metrics[0].keys():
            values = [m[metric_name] for m in all_metrics]
            avg_metrics[metric_name] = np.mean(values)

        # Store results
        self.results[model_name] = avg_metrics

        return avg_metrics

    def compare_models(
        self,
        models: Dict[str, Any],
        test_data: List[Dict[str, Any]],
        weak_labels: Optional[Dict[str, Dict[str, float]]] = None,
    ) -> Dict[str, Dict[str, float]]:
        """Evaluate and compare multiple models.

        Args:
            models: Dictionary of model_name -> model instance
            test_data: Test dataset
            weak_labels: Optional weak relevance labels

        Returns:
            Dictionary of model_name -> metrics
        """
        results = {}

        for model_name, model in models.items():
            print(f"Evaluating {model_name}...")
            metrics = self.evaluate_model(
                model_name,
                model,
                test_data,
                weak_labels,
            )
            results[model_name] = metrics

        return results

    def get_best_model(self, metric: str = "ndcg@10") -> Optional[str]:
        """Get best performing model by metric.

        Args:
            metric: Metric to use for comparison

        Returns:
            Name of best model
        """
        if not self.results:
            return None

        best_model = None
        best_score = -float("inf")

        for model_name, metrics in self.results.items():
            if metric in metrics and metrics[metric] > best_score:
                best_score = metrics[metric]
                best_model = model_name

        return best_model

    def print_comparison(self) -> None:
        """Print comparison table of all models."""
        if not self.results:
            print("No evaluation results available.")
            return

        # Get all metric names
        all_metrics = set()
        for metrics in self.results.values():
            all_metrics.update(metrics.keys())

        all_metrics = sorted(all_metrics)

        # Print header
        print("\n" + "=" * 80)
        print("Model Evaluation Results")
        print("=" * 80)

        # Print table
        print(f"{'Model':<30}", end="")
        for metric in all_metrics:
            print(f"{metric:>12}", end="")
        print()
        print("-" * 80)

        for model_name, metrics in self.results.items():
            print(f"{model_name:<30}", end="")
            for metric in all_metrics:
                score = metrics.get(metric, 0.0)
                print(f"{score:>12.4f}", end="")
            print()

        print("=" * 80)
