import streamlit as st
import json
import re
from resume_parser import extract_text_from_pdf
from analyzer import analyze_resume
from pdf_generator import generate_pdf
from job_links import get_job_links



def extract_json(text: str) -> dict:
    
    start = text.find("{")
    end = text.rfind("}") + 1

    if start == -1 or end == -1:
        raise ValueError("No JSON object found in LLM output")

    return json.loads(text[start:end])


def safe_list(data, key):
    
    return data.get(key, []) if isinstance(data.get(key), list) else []




st.set_page_config(page_title="AI Resume Analyzer", layout="centered")
st.title("📄 ResumeOPS")

st.markdown(
    "Upload your resume and get an **ATS-friendly, role-specific analysis** "
    "with actionable improvements."
)

job_role = st.text_input("🎯 Target Job Role (e.g. ML Engineer)")
uploaded_file = st.file_uploader("📎 Upload Resume (PDF only)", type=["pdf"])



if uploaded_file and job_role:
    with st.spinner("Analyzing your resume...."):

        resume_text = extract_text_from_pdf(uploaded_file)
        raw_result = analyze_resume(resume_text, job_role)

        
        try:
            result = extract_json(raw_result)
            if result.get("service_status") == "busy":
                st.warning("Service is busy right now. Please retry again in a few minutes.")
                st.stop()
        except Exception as e:
            st.error(" Failed to parse AI response")
            st.exception(e)
            st.subheader("Raw AI Output (Debug)")
            st.text(raw_result)
            st.stop()

        
        strengths = safe_list(result, "strengths")
        weaknesses = safe_list(result, "weaknesses")
        missing_skills = safe_list(result, "missing_skills")
        improved_bullets = safe_list(result, "improved_bullets")
        suggestions = safe_list(result, "suggestions")
        skill_roadmap = safe_list(result, "skill_roadmap")
        project_feedback = safe_list(result, "project_feedback")
        recommended_projects = safe_list(result, "recommended_projects")

        ats_score = result.get("ats_score", 0)

        

        st.divider()

        
        st.markdown("## ATS Compatibility Score")
        st.progress(min(ats_score, 100) / 100)
        st.metric("Score", f"{ats_score} / 100")

        st.divider()

        
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Strengths")
            for s in strengths:
                st.markdown(f"- {s}")

        with col2:
            st.markdown("### Weaknesses")
            for w in weaknesses:
                st.markdown(f"- {w}")

        st.divider()

      
        st.markdown("## Missing / Suggested Skills")
        for skill in missing_skills:
            st.markdown(f"- {skill}")

        st.divider()

        st.markdown("## Improved Resume Bullet Points")
        for i, bullet in enumerate(improved_bullets, 1):
            st.markdown(f"**{i}.** {bullet}")

        st.divider()

        
        st.markdown("## Overall Suggestions")
        for s in suggestions:
            st.markdown(f"- {s}")

        st.divider()

        
        st.markdown("## Skill Improvement Roadmap")
        for step in skill_roadmap:
            st.markdown(f"- {step}")

        st.divider()

       
        st.markdown("## Project Feedback")
        for p in project_feedback:
            st.markdown(f"- {p}")

        st.divider()

       
        st.markdown("## Recommended Projects to Add")
        for p in recommended_projects:
            st.markdown(f"- {p}")

        st.divider()

       
        if st.button("📄 Generate & Download PDF Report"):
            pdf_path = generate_pdf(result)
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="⬇ Download Resume Analysis PDF",
                    data=f,
                    file_name="Resume_Analysis_Report.pdf",
                    mime="application/pdf"
                )

        st.divider()

        
        st.markdown("## 🔗 Active Job Openings")
        job_links = get_job_links(job_role)

        for job in job_links:
            st.markdown(
                f"🔹 **{job['platform']}** → [View Jobs]({job['url']})",
                unsafe_allow_html=True
            )
        st.divider()

        st.markdown("### 💡 Motivation for Your Job Search")

        quotes = [
            "Success is not final, failure is not fatal — it is the courage to continue that counts.",
            "Every rejection brings you one step closer to the right opportunity.",
            "Your resume gets you interviews. Your persistence gets you offers.",
            "Don’t tailor yourself to rejection — tailor your resume to success.",
            "The right job will value the skills you’re building today."
        ]
        import random
        st.info(random.choice(quotes))

