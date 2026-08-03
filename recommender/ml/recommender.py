from pathlib import Path

import joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity



BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_DIR = BASE_DIR / "trained_models"

JOB_DATA_PATH = MODEL_DIR / "job_data.pkl"
JOB_EMBEDDINGS_PATH = MODEL_DIR / "job_embeddings.pkl"
NN_MODEL_PATH = MODEL_DIR / "nn_model.pkl"
MODEL_NAME = "all-MiniLM-L6-v2"

MODEL = None
job_data = None
job_embeddings = None
nn_model = None


def get_embedding_model():
    global MODEL
    if MODEL is None:
        from sentence_transformers import SentenceTransformer

        MODEL = SentenceTransformer(MODEL_NAME)
    return MODEL


def load_models():
    global job_data, job_embeddings, nn_model

    if job_data is None:
        if not JOB_DATA_PATH.exists():
            raise FileNotFoundError(f"Missing file: {JOB_DATA_PATH}")
        job_data = joblib.load(JOB_DATA_PATH)

    if job_embeddings is None:
        if not JOB_EMBEDDINGS_PATH.exists():
            raise FileNotFoundError(f"Missing file: {JOB_EMBEDDINGS_PATH}")
        job_embeddings = joblib.load(JOB_EMBEDDINGS_PATH)

    if nn_model is None and NN_MODEL_PATH.exists():
        nn_model = joblib.load(NN_MODEL_PATH)


def value(row, *names):
    """Return the first available, non-null value from a dataset row."""
    for name in names:
        result = row.get(name, "")
        if result is not None:
            return result
    return ""


def format_benefits(raw_value):
    """Convert set-like strings in the source CSV into readable text."""
    text = str(raw_value or "").strip()
    if text.startswith("{") and text.endswith("}"):
        text = text[1:-1]
    return ", ".join(
        item.strip().strip("'\"") for item in text.split(",") if item.strip()
    )


def format_skills(raw_value):
    """Add separators between title-cased skills while preserving examples."""
    text = str(raw_value or "").strip()
    output = []
    parentheses_depth = 0

    for index, character in enumerate(text):
        if character == "(":
            parentheses_depth += 1
        elif character == ")":
            parentheses_depth = max(0, parentheses_depth - 1)

        next_character = text[index + 1] if index + 1 < len(text) else ""
        if (
            character.isspace()
            and parentheses_depth == 0
            and next_character.isupper()
            and output
            and output[-1] not in {" ", ","}
        ):
            output.extend([",", " "])
        else:
            output.append(character)

    return "".join(output)


def recommend_jobs(resume_text, top_k=10):
    if not resume_text or not resume_text.strip():
        return []

    load_models()
    if job_data.empty:
        return []

    resume_embedding = get_embedding_model().encode(
        [resume_text], convert_to_numpy=True
    )

    if nn_model is not None:
        distances, indices = nn_model.kneighbors(
            resume_embedding, n_neighbors=min(top_k, len(job_data))
        )
        top_indices = indices[0]
        scores = 1 - distances[0]
    else:
        similarity = cosine_similarity(resume_embedding, job_embeddings)[0]
        top_indices = np.argsort(similarity)[::-1][:top_k]
        scores = similarity[top_indices]

    recommendations = []
    for idx, score in zip(top_indices, scores):
        row = job_data.iloc[idx]
        recommendations.append(
            {
                "title": value(row, "Job Title", "title"),
                "company": value(row, "Company", "Company Name", "company"),
                "location": value(row, "location", "Location"),
                "country": value(row, "Country"),
                "salary": value(row, "Salary Range", "Salary", "salary"),
                "role": value(row, "Role"),
                "work_type": value(row, "Work Type"),
                "portal": value(row, "Job Portal", "Job Portal name"),
                "contact_person": value(
                    row, "Contact Person", "Contact Personal of company"
                ),
                "contact": value(row, "Contact"),
                "description": value(row, "Job Description", "description"),
                "responsibility": value(row, "Responsibilities", "Responsibility"),
                "skills": format_skills(value(row, "skills", "Skills")),
                "benefits": format_benefits(value(row, "Benefits")),
                "match": round(max(0.0, float(score)) * 100, 2),
            }
        )
    return recommendations
