"""
AI Resume Analyzer & Job Match Platform
----------------------------------------
Streamlit web app that:
  1. Parses an uploaded resume (PDF/DOCX/TXT) and a job description.
  2. Extracts skills using spaCy + a skills taxonomy.
  3. Scores resume-JD fit using SBERT embeddings + cosine similarity.
  4. Shows a real-time skill-gap analysis.
  5. Persists every analysis to SQLite so history can be reviewed.

Run locally:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd

from src.parser import extract_text, clean_text
from src.skill_extractor import SkillExtractor
from src.matcher import ResumeMatcher
from src.database import init_db, save_analysis, get_all_analyses

st.set_page_config(
    page_title="AI Resume Analyzer & Job Match Platform",
    page_icon="🧠",
    layout="wide",
)


@st.cache_resource(show_spinner="Loading NLP models (first run only)...")
def load_models():
    extractor = SkillExtractor()
    matcher = ResumeMatcher()
    init_db()
    return extractor, matcher


extractor, matcher = load_models()

st.title("🧠 AI Resume Analyzer & Job Match Platform")
st.caption("NLP-powered resume parsing, SBERT semantic matching, and real-time skill-gap analysis.")

tab1, tab2 = st.tabs(["🔍 Analyze", "📊 History"])

with tab1:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. Upload Resume")
        candidate_name = st.text_input("Candidate name", placeholder="e.g. Vishnu K")
        resume_file = st.file_uploader("Resume (PDF, DOCX or TXT)", type=["pdf", "docx", "txt"])

    with col2:
        st.subheader("2. Job Description")
        jd_title = st.text_input("Job title", placeholder="e.g. AI/ML Engineer")
        jd_input_mode = st.radio("JD input method", ["Paste text", "Upload file"], horizontal=True)
        jd_text_raw = ""
        if jd_input_mode == "Paste text":
            jd_text_raw = st.text_area("Paste job description", height=200)
        else:
            jd_file = st.file_uploader("JD file (PDF, DOCX or TXT)", type=["pdf", "docx", "txt"], key="jd_file")
            if jd_file:
                jd_text_raw = clean_text(extract_text(jd_file))

    analyze_clicked = st.button("Run Analysis", type="primary", use_container_width=True)

    if analyze_clicked:
        if not resume_file or not jd_text_raw.strip():
            st.error("Please upload a resume and provide a job description.")
        else:
            with st.spinner("Parsing resume and scoring match..."):
                resume_text = clean_text(extract_text(resume_file))

                resume_skills_by_cat = extractor.extract_skills(resume_text)
                jd_skills_by_cat = extractor.extract_skills(jd_text_raw)

                resume_skills = extractor.flatten_skills(resume_skills_by_cat)
                jd_skills = extractor.flatten_skills(jd_skills_by_cat)

                score = matcher.similarity_score(resume_text, jd_text_raw)
                gap = matcher.skill_gap(resume_skills, jd_skills)
                years = extractor.extract_experience_years(resume_text)

                save_analysis(
                    candidate_name or "Unnamed",
                    resume_file.name,
                    jd_title or "Untitled JD",
                    score,
                    gap["matched"],
                    gap["missing"],
                )

            st.success("Analysis complete.")

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Match Score", f"{score}%")
            m2.metric("Skills Matched", len(gap["matched"]))
            m3.metric("Skills Missing", len(gap["missing"]))
            m4.metric("Detected Experience", f"{years} yrs" if years else "N/A")

            st.progress(min(int(score), 100))

            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("### ✅ Matched Skills")
                st.write(", ".join(gap["matched"]) or "None detected")
            with c2:
                st.markdown("### ⚠️ Missing Skills (Gap)")
                st.write(", ".join(gap["missing"]) or "None — full coverage!")
            with c3:
                st.markdown("### ➕ Extra Skills (Resume only)")
                st.write(", ".join(gap["extra"]) or "None")

            with st.expander("📄 Extracted resume skills by category"):
                st.json(resume_skills_by_cat)
            with st.expander("📋 Extracted JD skills by category"):
                st.json(jd_skills_by_cat)

with tab2:
    st.subheader("Analysis History")
    records = get_all_analyses()
    if records:
        df = pd.DataFrame(records)
        st.dataframe(
            df[["candidate_name", "resume_filename", "jd_title", "match_score", "created_at"]],
            use_container_width=True,
            hide_index=True,
        )
        st.bar_chart(df.set_index("candidate_name")["match_score"])
    else:
        st.info("No analyses yet. Run one in the Analyze tab.")

st.divider()
st.caption("Built with Python, spaCy, Sentence-BERT (SBERT), scikit-learn, and SQLite · Deployed via Streamlit Community Cloud")
