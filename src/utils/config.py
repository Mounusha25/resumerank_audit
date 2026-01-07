"""Configuration management utilities."""

import yaml
from pathlib import Path
from typing import Dict, Any


def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file.

    Args:
        config_path: Path to configuration file

    Returns:
        Configuration dictionary
    """
    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(path, "r") as f:
        config = yaml.safe_load(f)

    # Convert ngram_range from list to tuple for sklearn compatibility
    if "models" in config and "baseline" in config["models"]:
        if "tfidf" in config["models"]["baseline"]:
            ngram = config["models"]["baseline"]["tfidf"].get("ngram_range")
            if isinstance(ngram, list):
                config["models"]["baseline"]["tfidf"]["ngram_range"] = tuple(ngram)

    return config


def get_data_paths(config: Dict[str, Any]) -> Dict[str, str]:
    """Extract data paths from configuration.

    Args:
        config: Configuration dictionary

    Returns:
        Dictionary of data paths
    """
    return {
        "raw_resumes": config["data"]["raw_resumes"],
        "raw_job_descriptions": config["data"]["raw_job_descriptions"],
        "processed_resumes": config["data"]["processed_resumes"],
        "processed_job_descriptions": config["data"]["processed_job_descriptions"],
    }
