import os
import joblib
import pandas as pd

from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler


# ===========================
# Project Paths
# ===========================

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)

DATASET_PATH = os.path.join(BASE_DIR, "data", "AI.csv")

MODEL_DIR = os.path.join(BASE_DIR, "trained_models")

os.makedirs(MODEL_DIR, exist_ok=True)


# ===========================
# Load Dataset
# ===========================

print("Loading dataset...")

df = pd.read_csv(DATASET_PATH)

df.fillna("", inplace=True)


# ===========================
# Columns Used
# ===========================

preferred_columns = [
    "Job Title",
    "Role",
    "Job Description",
    "Responsibilities",
    "Company",
    "Benefits",
    "Salary Range",
    "location",
    "Country",
    "Work Type",
    "Contact",
    "Contact Person",
    "Job Portal",
]

available_columns = [
    col
    for col in preferred_columns
    if col in df.columns
]


# ===========================
# Combine Text
# ===========================

print("Preparing text...")

df["combined_text"] = (
    df[available_columns]
    .astype(str)
    .agg(" ".join, axis=1)
)


# ===========================
# Load Sentence Transformer
# ===========================

print("Loading AI model...")

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ===========================
# Generate Embeddings
# ===========================

print("Generating embeddings...")

embeddings = model.encode(
    df["combined_text"].tolist(),
    show_progress_bar=True,
    convert_to_numpy=True
)


# ===========================
# Salary Processing
# ===========================

if "Salary Range" in df.columns:

    df["Salary_num"] = (
        df["Salary Range"]
        .astype(str)
        .replace("[$,]", "", regex=True)
        .str.extract(r"(\d+)")
        .astype(float)
    )

    scaler = MinMaxScaler()

    df["salary_score"] = scaler.fit_transform(
        df[["Salary_num"]].fillna(0)
    )

else:

    df["salary_score"] = 0


# ===========================
# Train Nearest Neighbors
# ===========================

print("Training recommendation model...")

nn_model = NearestNeighbors(
    n_neighbors=10,
    metric="cosine"
)

nn_model.fit(embeddings)


# ===========================
# Save Files
# ===========================

joblib.dump(
    nn_model,
    os.path.join(
        MODEL_DIR,
        "nn_model.pkl"
    )
)

joblib.dump(
    embeddings,
    os.path.join(
        MODEL_DIR,
        "job_embeddings.pkl"
    )
)

joblib.dump(
    df,
    os.path.join(
        MODEL_DIR,
        "job_data.pkl"
    )
)


print("\nTraining completed successfully.")

print("\nGenerated Files:")

print("✓ nn_model.pkl")

print("✓ job_embeddings.pkl")

print("✓ job_data.pkl")
