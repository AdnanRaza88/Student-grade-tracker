from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models import Grade
from app.schemas import GradeCreate, GradeResponse
from app.ai_chain import get_study_tips, load_questions

router = APIRouter(prefix="/grades", tags=["grades"])

@router.post("/", response_model=GradeResponse)
def create_grade(grade: GradeCreate, session: Session = Depends(get_session)):
    db_grade = Grade(**grade.model_dump())
    session.add(db_grade)
    session.commit()
    session.refresh(db_grade)
    return db_grade

@router.get("/", response_model=list[GradeResponse])
def list_grades(session: Session = Depends(get_session)):
    return session.exec(select(Grade)).all()

@router.get("/{grade_id}", response_model=GradeResponse)
def get_grade(grade_id: int, session: Session = Depends(get_session)):
    grade = session.get(Grade, grade_id)
    if not grade:
        raise HTTPException(status_code=404, detail="Grade record not found")
    return grade

@router.put("/{grade_id}", response_model=GradeResponse)
def update_grade(grade_id: int, grade_update: GradeCreate, session: Session = Depends(get_session)):
    grade = session.get(Grade, grade_id)
    if not grade:
        raise HTTPException(status_code=404, detail="Grade record not found")
    for key, value in grade_update.model_dump().items():
        setattr(grade, key, value)
    session.commit()
    session.refresh(grade)
    return grade

@router.delete("/{grade_id}")
def delete_grade(grade_id: int, session: Session = Depends(get_session)):
    grade = session.get(Grade, grade_id)
    if not grade:
        raise HTTPException(status_code=404, detail="Grade record not found")
    session.delete(grade)
    session.commit()
    return {"ok": True}

@router.post("/{grade_id}/study-tips")
def study_tips(grade_id: int, question_id: int, session: Session = Depends(get_session)):
    grade = session.get(Grade, grade_id)
    if not grade:
        raise HTTPException(status_code=404, detail="Grade record not found")
    questions = load_questions()
    q = next((q for q in questions if q["id"] == question_id), None)
    if not q:
        raise HTTPException(status_code=400, detail="Invalid question id")
    tips = get_study_tips(grade.subject, grade.marks_obtained, grade.total_marks, q["template"])
    return {"grade_id": grade_id, "study_tips": tips}