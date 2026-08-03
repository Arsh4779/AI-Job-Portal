from functools import lru_cache
from pathlib import Path

import pandas as pd


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "AI.csv"


@lru_cache(maxsize=1)
def get_jobs_dataframe():
    """Load AI.csv once; it is the source of truth for available jobs."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Missing job dataset: {DATA_PATH}")
    return pd.read_csv(DATA_PATH, dtype=str, low_memory=False).fillna("")


def to_job_record(index, row):
    return {
        "id": index, "title": row.get("Job Title", ""),
        "company": row.get("Company", ""), "location": row.get("location", ""),
        "country": row.get("Country", ""), "salary": row.get("Salary Range", ""),
        "experience": row.get("Experience", ""), "job_type": row.get("Work Type", ""),
        "description": row.get("Job Description", ""), "required_skills": row.get("skills", ""),
        "role": row.get("Role", ""), "portal": row.get("Job Portal", ""),
    }
