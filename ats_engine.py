import re
import json
from functools import lru_cache
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from google import genai
import os


# =====================================================
# Gemini client (ONLY for role → skill ontology)
# =====================================================

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


# =====================================================
# Utilities
# =====================================================

def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


# =====================================================
# Skill synonyms (VERY IMPORTANT)
# =====================================================

SYNONYMS = {
    "machine learning": ["ml"],
    "deep learning": ["dl"],
    "natural language processing": ["nlp"],
    "computer vision": ["cv"],
    "artificial intelligence": ["ai"],
    "data structures": ["dsa"],
    "object oriented programming": ["oop"],
    "continuous integration": ["ci"],
    "continuous deployment": ["cd"]
}


# =====================================================
# Role → Skill Generator (LLM, cached)
# =====================================================

@lru_cache(maxsize=64)
def generate_role_skills(job_role: str):
    """
    Generate a realistic core skill set for a role.
    Called ONCE per role due to caching.
    """

    prompt = f"""
    You are an ATS engine.

    Generate a JSON list of the TOP 12 core technical skills
    required for the job role: "{job_role}"

    Rules:
    - skills only
    - industry standard terminology
    - lowercase
    - no explanations
    - no duplicates

    Output format:
    ["skill1","skill2",...]
    """

    response = client.models.generate_content(
        model="models/gemini-flash-latest",
        contents=prompt
    )

    text = response.text.strip()
    start = text.find("[")
    end = text.rfind("]") + 1

    return json.loads(text[start:end])


# =====================================================
# Skill matching (forgiving like real ATS)
# =====================================================

def skill_match(skill: str, resume_text: str) -> bool:
    # direct match
    if skill in resume_text:
        return True

    # token-level partial match
    for token in skill.split():
        if token in resume_text:
            return True

    # synonym match
    for alias in SYNONYMS.get(skill, []):
        if alias in resume_text:
            return True

    return False


# =====================================================
# Keyword score (core + partial)
# =====================================================

def keyword_score(resume_text: str, skills: list):
    matched, missing = [], []

    for skill in skills:
        if skill_match(skill, resume_text):
            matched.append(skill)
        else:
            missing.append(skill)

    score = (len(matched) / len(skills)) * 100
    return round(score, 2), matched, missing


# =====================================================
# Semantic similarity (resume vs skill corpus)
# =====================================================

def semantic_score(resume_text: str, skills: list):
    corpus = [" ".join(skills), resume_text]

    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform(corpus)

    sim = cosine_similarity(vectors[0], vectors[1])[0][0]
    return round(sim * 100, 2)


# =====================================================
# Resume structure score
# =====================================================

def structure_score(resume_text: str):
    sections = ["experience", "education", "skills", "projects"]
    found = sum(1 for sec in sections if sec in resume_text)

    # forgiving structure scoring
    return round((found / len(sections)) * 100, 2)


# =====================================================
# FINAL ATS SCORE (REALISTIC)
# =====================================================

def calculate_ats_score_role_only(resume_text: str, job_role: str):
    resume_text = clean_text(resume_text)

    skills = generate_role_skills(job_role)

    k_score, matched, missing = keyword_score(resume_text, skills)
    s_score = semantic_score(resume_text, skills)
    st_score = structure_score(resume_text)

    # REALISTIC WEIGHTS (no JD case)
    final_score = (
        0.35 * k_score +
        0.45 * s_score +
        0.20 * st_score
    )

    # Clamp like real ATS systems
    final_score = max(40, min(final_score, 88))

    return {
        "ats_score": round(final_score, 2),
        "keyword_match": k_score,
        "semantic_match": s_score,
        "structure_score": st_score,
        "matched_skills": matched,
        "missing_skills": missing
    }
