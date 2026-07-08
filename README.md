# AI Resume Analyzer & Job Match Platform

An NLP-powered web app that parses resumes, extracts skills, and scores how well a resume matches a job description using semantic similarity (SBERT) — with a real-time skill-gap report.

**Live demo:** _add your Streamlit Cloud link here after deploying (see below)_

## Features

- **Resume/JD parsing** — accepts PDF, DOCX, or plain text
- **Skill extraction** — spaCy `PhraseMatcher` against a categorized skills taxonomy (languages, ML/AI, cloud, databases, etc.)
- **Semantic match scoring** — Sentence-BERT (`all-MiniLM-L6-v2`) embeddings + cosine similarity produce a 0–100% fit score, so the match isn't just keyword overlap
- **Skill-gap analysis** — matched, missing, and extra skills computed instantly and shown in the UI
- **Persistence** — every analysis is saved to SQLite, with a History tab to review past candidates/scores
- **Web interface** — built with Streamlit for a clean, real-time UX

## Tech Stack

Python · spaCy · Sentence-Transformers (SBERT) · scikit-learn · SQLite · Streamlit · pdfplumber · python-docx

## Project Structure

```
ai-resume-analyzer/
├── app.py                     # Streamlit web app (entry point)
├── src/
│   ├── parser.py               # PDF/DOCX/TXT text extraction
│   ├── skill_extractor.py      # spaCy-based skill extraction
│   ├── matcher.py               # SBERT similarity scoring + skill-gap diff
│   └── database.py             # SQLite persistence
├── data/
│   └── skills_taxonomy.json    # categorized skill dictionary
├── sample_data/                # sample resume + JD for quick testing
├── requirements.txt
└── README.md
```

## Run Locally

```bash
git clone https://github.com/vishnuk-15/ai-resume-analyzer.git
cd ai-resume-analyzer

python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
python -m spacy download en_core_web_sm

streamlit run app.py
```

The app opens at `http://localhost:8501`. Use the files in `sample_data/` to try it immediately without needing your own resume.

## Deploy a Free Live Demo (Streamlit Community Cloud)

1. Push this project to a public GitHub repo (steps below).
2. Go to **[share.streamlit.io](https://share.streamlit.io)** and sign in with GitHub.
3. Click **New app**, select your repo, branch `main`, and set the main file path to `app.py`.
4. Click **Deploy**. First build takes a few minutes (installs spaCy model + SBERT).
5. You'll get a public URL like `https://ai-resume-analyzer-<yourname>.streamlit.app` — this is your demo link for the resume.

> Note: `en_core_web_sm` needs to be downloaded at build time. Streamlit Cloud runs `pip install -r requirements.txt` automatically; add a `packages.txt`/postinstall step or simply add this line to the top of `app.py` as a one-time safeguard, or include it directly in requirements.txt as shown below.

**Recommended for Streamlit Cloud:** add this exact line to `requirements.txt` so the spaCy model installs automatically during build (no manual download step needed):
```
https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
```

## How It Works (for interviews)

1. **Parsing:** `pdfplumber`/`python-docx` extract raw text from uploaded files, which is normalized (whitespace collapsed, empty lines stripped).
2. **Skill extraction:** spaCy tokenizes the text; a `PhraseMatcher` loaded with ~80 skill phrases (across 8 categories) finds exact/lemma matches, categorizing each hit.
3. **Semantic matching:** Both texts are embedded with `all-MiniLM-L6-v2` (a distilled SBERT model, 384-dim vectors). Cosine similarity between the two embeddings gives a fit score — this captures meaning, not just keyword overlap, so "built REST APIs" and "developed backend services" score as similar even without exact word matches.
4. **Skill-gap analysis:** Simple set operations (matched = intersection, missing = JD − resume, extra = resume − JD) turn the two skill sets into an actionable report.
5. **Persistence:** Every run writes a row to a local SQLite table (`analyses`) so multiple candidates/uploads can be compared later — this is what "supports multiple uploads" refers to on the resume.

## Resume Bullet Points (for reference)

- Built an NLP pipeline using spaCy and SBERT to extract skills and experience from resumes, reducing manual profiling effort by 70%.
- Scored how well a resume matches a job description using cosine similarity, improving screening accuracy across multiple roles.
- Stored resume data in a SQL database to support multiple uploads and deliver real-time skill-gap analysis via a web interface.
