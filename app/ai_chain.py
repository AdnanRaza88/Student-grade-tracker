import os
import json
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.7,
    max_tokens=300
)

def load_questions():
    with open("questions.json", "r") as f:
        return json.load(f)

def get_study_tips(subject: str, marks_obtained: float, total_marks: float, question_template: str) -> str:
    percentage = (marks_obtained / total_marks) * 100
    prompt = PromptTemplate(
        input_variables=["subject", "marks", "total", "percentage"],
        template=question_template
    )
    formatted_prompt = prompt.format(
        subject=subject,
        marks=marks_obtained,
        total=total_marks,
        percentage=round(percentage, 1)
    )
    response = llm.invoke(formatted_prompt)
    return response.content