from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select
from typing import List, Dict, Any
import pandas as pd
import io
from app.database import get_session
from app.models import Grade
from app.schemas import GradeCreate, GradeResponse
from app.ai import get_study_tips

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
def study_tips(grade_id: int, session: Session = Depends(get_session)):
    grade = session.get(Grade, grade_id)
    if not grade:
        raise HTTPException(status_code=404, detail="Grade record not found")
    tips = get_study_tips(grade.subject, grade.marks_obtained, grade.total_marks, grade.exam_type)
    return {"grade_id": grade_id, "study_tips": tips}

@router.get("/stats/summary")
def get_stats(session: Session = Depends(get_session)):
    all_grades = session.exec(select(Grade)).all()
    if not all_grades:
        return {"total_students": 0, "avg_percentage": 0, "total_records": 0, "highest_scorer": None}
    unique_students = set(g.student_name for g in all_grades)
    total_records = len(all_grades)
    percentages = [(g.marks_obtained / g.total_marks) * 100 for g in all_grades]
    avg_percentage = sum(percentages) / len(percentages)
    highest_percentage = max(percentages) if percentages else 0
    highest_student = None
    for g in all_grades:
        p = (g.marks_obtained / g.total_marks) * 100
        if p == highest_percentage:
            highest_student = g.student_name
            break
    return {
        "total_students": len(unique_students),
        "avg_percentage": round(avg_percentage, 2),
        "total_records": total_records,
        "highest_scorer": highest_student
    }

@router.post("/upload/preview")
async def preview_upload(file: UploadFile = File(...)):
    contents = await file.read()
    if file.filename.endswith('.csv'):
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
    else:
        df = pd.read_excel(io.BytesIO(contents))
    preview = df.head(5).to_dict(orient='records')
    columns = df.columns.tolist()
    return {"columns": columns, "preview": preview}

@router.post("/upload/validate")
async def validate_upload(file: UploadFile = File(...), mapping: Dict[str, str] = None):
    if mapping is None:
        raise HTTPException(status_code=400, detail="Mapping required")
    contents = await file.read()
    if file.filename.endswith('.csv'):
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
    else:
        df = pd.read_excel(io.BytesIO(contents))
    required_fields = ["student_name", "subject", "marks_obtained", "total_marks", "semester", "date"]
    for field in required_fields:
        if field not in mapping or mapping[field] not in df.columns:
            raise HTTPException(status_code=400, detail=f"Column for {field} not mapped or missing")
    errors = []
    valid_rows = []
    for idx, row in df.iterrows():
        try:
            grade_data = {
                "student_name": str(row[mapping["student_name"]]),
                "subject": str(row[mapping["subject"]]),
                "marks_obtained": float(row[mapping["marks_obtained"]]),
                "total_marks": float(row[mapping["total_marks"]]),
                "semester": str(row[mapping["semester"]]),
                "date": str(row[mapping["date"]]),
                "exam_type": mapping.get("exam_type", "Combined"),
                "father_name": mapping.get("father_name") and str(row[mapping["father_name"]]) or None
            }
            GradeCreate(**grade_data)
            valid_rows.append(grade_data)
        except Exception as e:
            errors.append(f"Row {idx+2}: {str(e)}")
    return {"valid_rows": len(valid_rows), "errors": errors, "data": valid_rows[:100]}

@router.post("/upload/insert")
async def insert_upload(data: List[Dict[str, Any]], session: Session = Depends(get_session)):
    inserted = 0
    for item in data:
        grade = Grade(**item)
        session.add(grade)
        inserted += 1
    session.commit()
    return {"inserted": inserted}

@router.get("/export/csv")
def export_csv(session: Session = Depends(get_session)):
    grades = session.exec(select(Grade)).all()
    data = [g.model_dump() for g in grades]
    df = pd.DataFrame(data)
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    from fastapi.responses import StreamingResponse
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=grades.csv"})

@router.get("/export/excel")
def export_excel(session: Session = Depends(get_session)):
    grades = session.exec(select(Grade)).all()
    data = [g.model_dump() for g in grades]
    df = pd.DataFrame(data)
    output = io.BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    from fastapi.responses import StreamingResponse
    return StreamingResponse(iter([output.getvalue()]), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=grades.xlsx"})