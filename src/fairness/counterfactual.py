"""Counterfactual tester for fairness evaluation.

Tests how ranking changes under controlled perturbations.
"""

from typing import List, Dict, Any, Tuple
import numpy as np
from .perturbations import PerturbationGenerator


class CounterfactualTester:
    """Test ranking fairness using counterfactual perturbations."""

    def __init__(self, ranker: Any, perturbation_config: Dict = None):
        """Initialize counterfactual tester.

        Args:
            ranker: Ranking model with rank() method
            perturbation_config: Configuration for perturbations
        """
        self.ranker = ranker
        self.perturbation_generator = PerturbationGenerator(perturbation_config or {})

    def test_single_perturbation(
        self,
        resumes: List[Dict[str, Any]],
        job_description: str,
        perturbation_type: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Test impact of a single perturbation type.

        Args:
            resumes: List of resumes
            job_description: Job description text
            perturbation_type: Type of perturbation to test
            **kwargs: Additional perturbation arguments

        Returns:
            Dictionary with test results
        """
        # Get original rankings
        original_rankings = self.ranker.rank(job_description, resumes)
        original_rank_dict = {rid: rank for rank, (rid, _) in enumerate(original_rankings)}

        # Apply perturbations and re-rank
        rank_changes = []
        perturbed_resumes = []

        for resume in resumes:
            # Create perturbed version
            perturbed_text = self.perturbation_generator.apply_perturbation(
                resume["text"],
                perturbation_type,
                **kwargs
            )

            perturbed_resume = {
                **resume,
                "text": perturbed_text,
            }
            perturbed_resumes.append(perturbed_resume)

        # Get new rankings
        new_rankings = self.ranker.rank(job_description, perturbed_resumes)
        new_rank_dict = {rid: rank for rank, (rid, _) in enumerate(new_rankings)}

        # Calculate rank changes
        for resume_id in original_rank_dict.keys():
            original_rank = original_rank_dict[resume_id]
            new_rank = new_rank_dict[resume_id]
            rank_change = abs(new_rank - original_rank)
            rank_changes.append(rank_change)

        # Calculate metrics
        mean_rank_change = np.mean(rank_changes)
        max_rank_change = np.max(rank_changes)
        median_rank_change = np.median(rank_changes)

        # Count significantly affected resumes (change > 5 positions)
        significantly_affected = sum(1 for change in rank_changes if change > 5)
        affected_percentage = (significantly_affected / len(resumes)) * 100

        return {
            "perturbation_type": perturbation_type,
            "mean_rank_change": float(mean_rank_change),
            "median_rank_change": float(median_rank_change),
            "max_rank_change": int(max_rank_change),
            "std_rank_change": float(np.std(rank_changes)),
            "affected_percentage": float(affected_percentage),
            "num_resumes": len(resumes),
            "rank_changes": rank_changes,
        }

    def test_gender_proxy(
        self,
        resumes: List[Dict[str, Any]],
        job_description: str,
    ) -> Dict[str, Any]:
        """Test gender proxy perturbation (pronoun swap).

        Args:
            resumes: List of resumes
            job_description: Job description text

        Returns:
            Test results
        """
        return self.test_single_perturbation(
            resumes,
            job_description,
            "gender_pronoun",
            direction="to_neutral",
        )

    def test_name_redaction(
        self,
        resumes: List[Dict[str, Any]],
        job_description: str,
    ) -> Dict[str, Any]:
        """Test name redaction perturbation.

        Args:
            resumes: List of resumes
            job_description: Job description text

        Returns:
            Test results
        """
        return self.test_single_perturbation(
            resumes,
            job_description,
            "name_redaction",
        )

    def test_university_swap(
        self,
        resumes: List[Dict[str, Any]],
        job_description: str,
        university_tiers: Dict[str, List[str]],
    ) -> Dict[str, Any]:
        """Test university prestige bias.

        Args:
            resumes: List of resumes
            job_description: Job description text
            university_tiers: Dictionary of tier -> universities

        Returns:
            Test results
        """
        return self.test_single_perturbation(
            resumes,
            job_description,
            "university_swap",
            university_tiers=university_tiers,
        )

    def test_gap_insertion(
        self,
        resumes: List[Dict[str, Any]],
        job_description: str,
        gap_months: int = 6,
    ) -> Dict[str, Any]:
        """Test employment gap bias.

        Args:
            resumes: List of resumes
            job_description: Job description text
            gap_months: Length of gap in months

        Returns:
            Test results
        """
        return self.test_single_perturbation(
            resumes,
            job_description,
            "gap_insertion",
            gap_months=gap_months,
        )

    def run_all_tests(
        self,
        resumes: List[Dict[str, Any]],
        job_description: str,
        university_tiers: Dict[str, List[str]] = None,
    ) -> Dict[str, Dict[str, Any]]:
        """Run all fairness tests.

        Args:
            resumes: List of resumes
            job_description: Job description text
            university_tiers: Optional university tier configuration

        Returns:
            Dictionary of test_name -> results
        """
        results = {}

        print("Running fairness tests...")

        # Gender proxy test
        print("  - Testing gender proxy...")
        results["gender_proxy"] = self.test_gender_proxy(resumes, job_description)

        # Name redaction test
        print("  - Testing name redaction...")
        results["name_redaction"] = self.test_name_redaction(resumes, job_description)

        # University swap test
        if university_tiers:
            print("  - Testing university prestige...")
            results["university_swap"] = self.test_university_swap(
                resumes,
                job_description,
                university_tiers,
            )

        # Gap insertion test
        print("  - Testing employment gap...")
        results["gap_insertion"] = self.test_gap_insertion(resumes, job_description)

        print("Fairness tests complete.")

        return results

    def generate_fairness_report(
        self,
        results: Dict[str, Dict[str, Any]],
        threshold_rank_change: float = 3.0,
        threshold_affected_pct: float = 15.0,
    ) -> Dict[str, Any]:
        """Generate fairness report with pass/fail indicators.

        Args:
            results: Test results from run_all_tests
            threshold_rank_change: Maximum acceptable mean rank change
            threshold_affected_pct: Maximum acceptable affected percentage

        Returns:
            Fairness report with pass/fail indicators
        """
        report = {
            "summary": {},
            "details": results,
            "thresholds": {
                "max_mean_rank_change": threshold_rank_change,
                "max_affected_percentage": threshold_affected_pct,
            },
        }

        # Evaluate each test
        for test_name, test_results in results.items():
            mean_change = test_results["mean_rank_change"]
            affected_pct = test_results["affected_percentage"]

            passed = (
                mean_change <= threshold_rank_change and
                affected_pct <= threshold_affected_pct
            )

            report["summary"][test_name] = {
                "passed": passed,
                "mean_rank_change": mean_change,
                "affected_percentage": affected_pct,
                "issues": [],
            }

            # Identify issues
            if mean_change > threshold_rank_change:
                report["summary"][test_name]["issues"].append(
                    f"Mean rank change ({mean_change:.2f}) exceeds threshold ({threshold_rank_change})"
                )

            if affected_pct > threshold_affected_pct:
                report["summary"][test_name]["issues"].append(
                    f"Affected percentage ({affected_pct:.1f}%) exceeds threshold ({threshold_affected_pct}%)"
                )

        # Overall pass/fail
        report["overall_passed"] = all(
            test["passed"] for test in report["summary"].values()
        )

        return report
