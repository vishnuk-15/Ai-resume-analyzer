"""
skill_extractor.py
-------------------
Uses spaCy for tokenization/lemmatization plus a phrase-matcher built on a
skills taxonomy to pull structured skills and experience signals out of
free-text resumes and job descriptions.
"""

import json
import re
from pathlib import Path

import spacy
from spacy.matcher import PhraseMatcher

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "skills_taxonomy.json"


class SkillExtractor:
    def __init__(self, taxonomy_path: Path = DATA_PATH):
        self.nlp = spacy.load("en_core_web_sm")
        with open(taxonomy_path, "r") as f:
            self.taxonomy = json.load(f)

        # Flatten taxonomy into a single skill -> category lookup
        self.skill_to_category = {}
        for category, skills in self.taxonomy.items():
            for skill in skills:
                self.skill_to_category[skill.lower()] = category

        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        patterns = [self.nlp.make_doc(skill) for skill in self.skill_to_category.keys()]
        self.matcher.add("SKILLS", patterns)

    def extract_skills(self, text: str) -> dict:
        """
        Returns a dict: {category: sorted list of matched skills}
        """
        doc = self.nlp(text)
        matches = self.matcher(doc)

        found = set()
        for match_id, start, end in matches:
            span_text = doc[start:end].text.lower()
            found.add(span_text)

        categorized = {}
        for skill in found:
            category = self.skill_to_category.get(skill, "other")
            categorized.setdefault(category, set()).add(skill)

        return {cat: sorted(list(skills)) for cat, skills in categorized.items()}

    def extract_experience_years(self, text: str) -> float:
        """
        Rough heuristic: finds patterns like '3 years', '2+ years of experience'
        and returns the max value found. Returns 0 if none found.
        """
        pattern = r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years|yrs)"
        matches = re.findall(pattern, text.lower())
        years = [float(m) for m in matches]
        return max(years) if years else 0.0

    def flatten_skills(self, categorized: dict) -> set:
        all_skills = set()
        for skills in categorized.values():
            all_skills.update(skills)
        return all_skills
