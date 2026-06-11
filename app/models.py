from sqlmodel import SQLModel, Field
from typing import Optional

class Grade(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    student_name: str
    father_name: Optional[str] = None
    subject: str
    marks_obtained: float
    total_marks: float
    exam_type: str = "Combined"
    semester: str
    date: str