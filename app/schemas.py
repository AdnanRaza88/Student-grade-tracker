from pydantic import BaseModel, field_validator
from typing import Optional

class GradeCreate(BaseModel):
    student_name: str
    father_name: Optional[str] = None
    subject: str
    marks_obtained: float
    total_marks: float
    semester: str
    date: str
    exam_type: str = "Combined"

    @field_validator('marks_obtained')
    def marks_not_exceed_total(cls, v, info):
        total = info.data.get('total_marks')
        if total and v > total:
            raise ValueError(f'Marks obtained {v} exceeds total {total}')
        return v

    @field_validator('total_marks')
    def total_positive(cls, v):
        if v <= 0:
            raise ValueError('Total marks must be positive')
        return v

class GradeResponse(BaseModel):
    id: int
    student_name: str
    father_name: Optional[str] = None
    subject: str
    marks_obtained: float
    total_marks: float
    semester: str
    date: str
    exam_type: str