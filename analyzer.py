from google import genai
from dotenv import load_dotenv
import os
from prompt import resume_analysis_prompt

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def analyze_resume(resume_text, job_role):
    prompt = resume_analysis_prompt(resume_text, job_role)

    response = client.models.generate_content(
        model="models/gemini-flash-latest", 
        contents=prompt
    )

    return response.text
