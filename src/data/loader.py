"""Data loading utilities."""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd


def load_resumes(file_path: str) -> List[Dict[str, Any]]:
    """Load resumes from JSON file.

    Args:
        file_path: Path to resumes JSON file

    Returns:
        List of resume dictionaries
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Resume file not found: {file_path}")

    with open(path, "r", encoding="utf-8") as f:
        resumes = json.load(f)

    return resumes


def load_job_descriptions(file_path: str) -> List[Dict[str, Any]]:
    """Load job descriptions from JSON file.

    Args:
        file_path: Path to job descriptions JSON file

    Returns:
        List of job description dictionaries
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Job description file not found: {file_path}")

    with open(path, "r", encoding="utf-8") as f:
        job_descriptions = json.load(f)

    return job_descriptions


def save_resumes(resumes: List[Dict[str, Any]], file_path: str) -> None:
    """Save resumes to JSON file.

    Args:
        resumes: List of resume dictionaries
        file_path: Output file path
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(resumes, f, indent=2, ensure_ascii=False)


def save_job_descriptions(job_descriptions: List[Dict[str, Any]], file_path: str) -> None:
    """Save job descriptions to JSON file.

    Args:
        job_descriptions: List of job description dictionaries
        file_path: Output file path
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(job_descriptions, f, indent=2, ensure_ascii=False)


def create_data_splits(
    resumes: List[Dict[str, Any]],
    dev_ratio: float = 0.3,
    seed: int = 42
) -> Dict[str, List[Dict[str, Any]]]:
    """Split resumes into dev and test sets.

    Args:
        resumes: List of resume dictionaries
        dev_ratio: Proportion for dev set
        seed: Random seed for reproducibility

    Returns:
        Dictionary with 'dev' and 'test' keys
    """
    import random
    random.seed(seed)

    shuffled = resumes.copy()
    random.shuffle(shuffled)

    split_idx = int(len(shuffled) * dev_ratio)

    return {
        "dev": shuffled[:split_idx],
        "test": shuffled[split_idx:],
    }


def load_weak_labels(file_path: str) -> Dict[str, Dict[str, float]]:
    """Load weak relevance labels if available.

    Args:
        file_path: Path to labels file (JSON or CSV)

    Returns:
        Dictionary: {resume_id: {job_id: relevance_score}}
    """
    path = Path(file_path)

    if not path.exists():
        return {}

    if path.suffix == ".json":
        with open(path, "r") as f:
            return json.load(f)
    elif path.suffix == ".csv":
        df = pd.read_csv(path)
        labels = {}
        for _, row in df.iterrows():
            resume_id = row["resume_id"]
            job_id = row["job_id"]
            score = row["relevance"]

            if resume_id not in labels:
                labels[resume_id] = {}
            labels[resume_id][job_id] = score

        return labels
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}")
