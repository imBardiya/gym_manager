from datetime import date
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from fastapi import HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.models import Student
from app.models import Attendance
from app.models import GymSession
from datetime import date
import jdatetime

from fastapi import Query

from fastapi import Request
from fastapi.responses import RedirectResponse

from app.main import templates
from typing import Optional

router = APIRouter(
    prefix="/students",
    tags=["Students"]
)


@router.get("/add")
def add_student_form(
    request: Request
):
    return templates.TemplateResponse(
        request=request,
        name="add_student.html"
    )


@router.post("/add")
def add_student(
    full_name: str = Form(...),
    phone: str = Form(None),
    total_sessions: int = Form(...),
    db: Session = Depends(get_db)
):

    student = Student(
        full_name=full_name,
        phone=phone if phone else None,
        register_date=date.today(),
        total_sessions=total_sessions
    )

    db.add(student)

    db.commit()

    db.refresh(student)

    return RedirectResponse(
        url="/students",
        status_code=303
    )

@router.get("/")
def list_students(
    request: Request,
    search: str = Query(None),
    db: Session = Depends(get_db)
):

    students_query = db.query(Student)

    if search:

        students_query = (
            students_query.filter(
                Student.full_name.contains(search)
            )
        )

    students = students_query.order_by(Student.full_name.asc()).all()

    return templates.TemplateResponse(
        request=request,
        name="students.html",
        context={
            "students": students,
            "search": search
        }
    )

@router.get("/{student_id}")
def student_detail(
    request: Request,
    student_id: int,
    db: Session = Depends(get_db)
):

    student = (
        db.query(Student)
        .filter(Student.id == student_id)
        .first()
    )

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    attendance_records = (
        db.query(Attendance)
        .filter(
            Attendance.student_id == student_id
        )
        .order_by(
            Attendance.date.desc()
        )
        .all()
    )

    attendance_date = []

    for record in attendance_records:
        jalili_date = jdatetime.date.fromgregorian(date=record.date)

        attendance_date.append({
            "id": record.id,
            "status": record.status,
            "jalali_date": jalili_date.strftime("%Y/%m/%d")
        })

    return templates.TemplateResponse(
        request=request,
        name="student_detail.html",
        context={
            "student": student,
            "attendance_records": attendance_date
        }
    )

@router.post("/{student_id}/delete")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db)
):

    student = (
        db.query(Student)
        .filter(Student.id == student_id)
        .first()
    )

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    attendance_records = (
        db.query(Attendance)
        .filter(
            Attendance.student_id == student_id
        )
        .all()
    )

    for record in attendance_records:
        db.delete(record)

    db.delete(student)

    db.commit()

    return RedirectResponse(
        url="/students",
        status_code=303
    )

@router.get("/{student_id}/edit")
def edit_student_form(
    request: Request,
    student_id: int,
    db: Session = Depends(get_db)
):

    student = (
        db.query(Student)
        .filter(Student.id == student_id)
        .first()
    )

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )
    
    sessions = (
       db.query(GymSession)
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="edit_student.html",
        context={
            "student": student,
            "sessions": sessions
        }
    )

@router.post("/{student_id}/present")
def mark_present(
    student_id: int,
    attendance_date: str = Form(None),
    db: Session = Depends(get_db)
):

    student = (
        db.query(Student)
        .filter(Student.id == student_id)
        .first()
    )

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    if attendance_date:
        today = date.fromisoformat(attendance_date)
    else:
        today = date.today()

    existing = (
        db.query(Attendance)
        .filter(
            Attendance.student_id == student_id,
            Attendance.date == today
        )
        .first()
    )

    if existing:
        return RedirectResponse(
            url=f"/students/{student_id}",
            status_code=303
        )

    attendance = Attendance(
        student_id=student_id,
        date=today,
        status="present"
    )

    db.add(attendance)

    student.used_sessions += 1

    db.commit()

    return RedirectResponse(
        url=f"/students/{student_id}",
        status_code=303
    )

@router.post("/{student_id}/absent")
def mark_absent(
    student_id: int,
    attendance_date: str = Form(None),
    db: Session = Depends(get_db)
):
    student = (
        db.query(Student)
        .filter(Student.id == student_id)
        .first()
    )

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    if attendance_date:
        today = date.fromisoformat(attendance_date)
    else:
        today = date.today()

    existing = (
        db.query(Attendance)
        .filter(
            Attendance.student_id == student_id,
            Attendance.date == today
        )
        .first()
    )

    if existing:
        return RedirectResponse(
            url=f"/students/{student_id}",
            status_code=303
        )

    attendance = Attendance(
        student_id=student_id,
        date=today,
        status="absent"
    )

    db.add(attendance)

    student.absence_count += 1

    if student.deduct_absence:
        student.used_sessions += 1

    db.commit()

    return RedirectResponse(
        url=f"/students/{student_id}",
        status_code=303
    )

@router.post("/{student_id}/update")
def update_student(
    student_id: int,

    session_id: Optional[str] = Form(None),
    
    full_name: str = Form(...),

    phone: str = Form(None),

    total_sessions: int = Form(...),

    #used_sessions: int = Form(...),

    #absence_count: int = Form(...),

    deduct_absence: bool = Form(False),

    notes: str = Form(None),

    missed_present_sessions: int = Form(0),

    missed_absent_sessions: int = Form(0),

    db: Session = Depends(get_db)
):

    student = (
        db.query(Student)
        .filter(Student.id == student_id)
        .first()
    )

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    student.full_name = full_name

    student.phone = phone if phone else None

    student.total_sessions = total_sessions

    #student.used_sessions = used_sessions

    #student.absence_count = absence_count

    student.deduct_absence = deduct_absence

    student.notes = notes

    if session_id == "":
        session_id = None
    else:
        session_id = int(session_id)

    student.session_id = session_id

    # جلسات حاضر جاافتاده

    if missed_present_sessions > 0:

        student.used_sessions += (
            missed_present_sessions
        )

    # غیبت های جاافتاده

    if missed_absent_sessions > 0:

        student.absence_count += (
            missed_absent_sessions
        )

        if student.deduct_absence:

            student.used_sessions += (
                missed_absent_sessions
            )

    db.commit()

    return RedirectResponse(
    url=f"/students/{student_id}",
    status_code=303
)

@router.post("/{student_id}/renew")
def renew_student(
    student_id: int,
    sessions: int = Form(...),
    db: Session = Depends(get_db)
):

    student = (
        db.query(Student)
        .filter(Student.id == student_id)
        .first()
    )

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    student.total_sessions = sessions

    student.used_sessions = 0

    db.commit()

    return RedirectResponse(
        url=f"/students/{student_id}",
        status_code=303
    )
    
@router.post("/attendance/{attendance_id}/delete")
def delete_attendance(
    attendance_id: int,
    db: Session = Depends(get_db)
):

    attendance = (
        db.query(Attendance)
        .filter(Attendance.id == attendance_id)
        .first()
    )

    if not attendance:
        raise HTTPException(
            status_code=404,
            detail="Attendance not found"
        )

    student = (
        db.query(Student)
        .filter(Student.id == attendance.student_id)
        .first()
    )

    if attendance.status == "present":

        if student.used_sessions > 0:
            student.used_sessions -= 1

    else:

        if student.absence_count > 0:
            student.absence_count -= 1

        if student.deduct_absence:

            if student.used_sessions > 0:
                student.used_sessions -= 1

    student_id = student.id

    db.delete(attendance)

    db.commit()

    return RedirectResponse(
        url=f"/students/{student_id}",
        status_code=303
    )
