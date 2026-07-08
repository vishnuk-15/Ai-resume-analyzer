"""
matcher.py
----------
Embeds resume and job-description text using a Sentence-BERT model and
scores their semantic similarity via cosine similarity. Also produces a
skill-gap report by diffing extracted skill sets.
"""

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class ResumeMatcher:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # Small, fast SBERT model — good accuracy/latency tradeoff for a
        # real-time web interface.
        self.model = SentenceTransformer(model_name)

    def similarity_score(self, resume_text: str, jd_text: str) -> float:
        """
        Returns a 0-100 match score between resume and job description.
        """
        embeddings = self.model.encode([resume_text, jd_text])
        score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        # cosine similarity is -1..1, clamp and rescale to 0..100
        score = max(0.0, min(1.0, score))
        return round(score * 100, 2)

    def skill_gap(self, resume_skills: set, jd_skills: set) -> dict:
        """
        Compares two skill sets and returns matched / missing / extra skills.
        """
        matched = resume_skills & jd_skills
        missing = jd_skills - resume_skills
        extra = resume_skills - jd_skills

        return {
            "matched": sorted(matched),
            "missing": sorted(missing),
            "extra": sorted(extra),
            "match_rate": round(len(matched) / len(jd_skills) * 100, 2) if jd_skills else 0.0,
        }
