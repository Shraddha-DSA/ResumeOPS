from google import genai

import os
from prompt import resume_analysis_prompt

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def analyze_resume(resume_text, job_role):
    prompt = resume_analysis_prompt(resume_text, job_role)

    try:
        response = client.models.generate_content(
        model="models/gemini-flash-latest", 
        contents=prompt
    )

        return response.text

    except Exception:
        
        return """{
          "service_status": "busy",
          "strengths": [],
          "weaknesses": [],
          "missing_skills": [],
          "improved_bullets": [],
          "suggestions": [],
          "skill_roadmap": [],
          "project_feedback": [],
          "recommended_projects": []
        }"""
