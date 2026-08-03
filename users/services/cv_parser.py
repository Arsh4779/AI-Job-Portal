import re

import numpy as np


KNOWN_SKILLS = (
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "SQL",
    "HTML", "CSS", "React", "Angular", "Vue", "Django", "Flask", "FastAPI",
    "Node.js", "Bootstrap", "Git", "Docker", "Kubernetes", "AWS", "Azure",
    "Google Cloud", "Machine Learning", "Data Analysis", "Pandas", "NumPy",
    "TensorFlow", "PyTorch", "Power BI", "Tableau", "Excel", "Figma", "UI/UX",
    "REST API", "Agile", "Scrum", "Communication", "Leadership",
)

SECTION_QUERIES = {
    "skills": "technical skills, programming languages, software tools, and technologies",
    "education": "education, university degree, academic qualification, and coursework",
    "experience": "professional work experience, employment history, job role, and responsibilities",
}


def _normalise_lines(text):
    return [re.sub(r"\s+", " ", line).strip(" -\t") for line in text.splitlines()]


def _section_lines(lines, headings):
    collected = []
    capture = False
    heading_pattern = re.compile(r"^(?:" + "|".join(headings) + r")\s*:?$", re.I)
    stop_pattern = re.compile(
        r"^(skills?|technical skills?|education|experience|work experience|"
        r"employment|projects?|certifications?|achievements?|languages?)\s*:?$", re.I
    )
    for line in lines:
        if heading_pattern.match(line):
            capture = True
            continue
        if capture and stop_pattern.match(line):
            break
        if capture and line:
            collected.append(line)
    return collected


def _semantic_section_lines(lines, limit=5):
    """Use Sentence Transformers to find CV lines related to each section."""
    candidates = [line for line in lines if 12 <= len(line) <= 300]
    if not candidates:
        return {section: [] for section in SECTION_QUERIES}

    # Reuse the recommendation model so CV parsing and matching share one model cache.
    from recommender.ml.recommender import get_embedding_model

    model = get_embedding_model()
    queries = list(SECTION_QUERIES.values())
    embeddings = model.encode(
        queries + candidates,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    query_embeddings = embeddings[:len(queries)]
    line_embeddings = embeddings[len(queries):]
    similarity = np.matmul(query_embeddings, line_embeddings.T)

    result = {}
    for index, section in enumerate(SECTION_QUERIES):
        ranked_indexes = np.argsort(similarity[index])[::-1]
        # A modest floor prevents unrelated contact/header lines entering a section.
        result[section] = [
            candidates[item]
            for item in ranked_indexes[:limit]
            if similarity[index][item] >= 0.28
        ]
    return result


def _skills_from_lines(lines):
    skills = []
    for line in lines:
        content = line.split(":", 1)[-1]
        for item in re.split(r"[,;|/]+", content):
            item = item.strip(" .-")
            if 2 <= len(item) <= 40 and item.lower() not in {"skills", "technical skills"}:
                skills.append(item)
    return skills


def _unique(items, limit):
    result = []
    seen = set()
    for item in items:
        key = item.casefold()
        if item and key not in seen:
            seen.add(key)
            result.append(item)
        if len(result) == limit:
            break
    return result


def extract_cv_details(text):
    """Extract dashboard details using semantic Sentence Transformer matching."""
    lines = _normalise_lines(text)
    searchable = "\n".join(lines)
    phone_match = re.search(r"(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)(?!\w)", searchable)

    # Semantic matching works even if authors use unusual section names.
    semantic_lines = _semantic_section_lines(lines)
    recognised_skills = [
        skill for skill in KNOWN_SKILLS
        if re.search(r"(?<!\w)" + re.escape(skill) + r"(?!\w)", searchable, re.I)
    ]
    skills = _unique(recognised_skills + _skills_from_lines(semantic_lines["skills"]), 15)

    education_lines = _section_lines(lines, ("education", "academic background"))
    education_lines = education_lines or semantic_lines["education"]
    experience_lines = _section_lines(
        lines, ("experience", "work experience", "employment history", "professional experience")
    )
    experience_lines = experience_lines or semantic_lines["experience"]

    return {
        "phone": phone_match.group(0).strip()[:15] if phone_match else "",
        "skills": ", ".join(skills),
        "education": " | ".join(_unique(education_lines, 2))[:200],
        "experience": "\n".join(_unique(experience_lines, 5))[:2000],
    }
