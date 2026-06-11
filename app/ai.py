import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_study_tips(subject: str, marks_obtained: float, total_marks: float, exam_type: str) -> str:
    percentage = (marks_obtained / total_marks) * 100
    prompt = f"""
Student scored {marks_obtained} out of {total_marks} ({percentage:.1f}%) in {subject} ({exam_type}).
Give exactly 3 specific, actionable study tips to improve.
Return only the tips as plain text, numbered 1 to 3.
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=300,
    )
    return response.choices[0].message.content