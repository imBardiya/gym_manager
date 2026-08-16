from fastapi import FastAPI
from app.core.templates import templates

from app.database import Base
from app.database import engine

from app.models import Student
from app.models import GymSession
from app.models import Attendance
from app.models import student_sessions

from app.routers.students import router as students_router
from app.routers.sessions import router as sessions_router
from app.routers.attendance import router as attendance_router
from app.routers.backup import router as backup_router
from app.routers.restore import router as restore_router

from sqlalchemy import func

from datetime import date

from fastapi import Request
from fastapi import Depends

from sqlalchemy.orm import Session

from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.dependencies import get_db

from app.models import (
    Student,
    Attendance,
    GymSession
)

app = FastAPI(
    title="Gym Manager"
)

app.mount("/static", StaticFiles(directory=Path("app/static")), name="static")

Base.metadata.create_all(bind=engine)

app.include_router(students_router)
app.include_router(sessions_router)
app.include_router(attendance_router)
app.include_router(backup_router)
app.include_router(restore_router)


@app.get("/")
def dashboard(request: Request,db: Session = Depends(get_db)):

    total_students = (
        db.query(Student)
        .count()
    )

    total_sessions = (
        db.query(GymSession)
        .count()
    )

    students_need_renew = (
        db.query(Student)
        .filter(
            (
                Student.total_sessions -
                Student.used_sessions
            ) <= 0
        )
        .count()
    )

    present_today = (
        db.query(Attendance)
        .filter(
            Attendance.date == date.today(),
            Attendance.status == "present"
        )
        .count()
    )

    absent_today = (
        db.query(Attendance)
        .filter(
            Attendance.date == date.today(),
            Attendance.status == "absent"
        )
        .count()
    )

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "total_students": total_students,
            "total_sessions": total_sessions,
            "students_need_renew": students_need_renew,
            "present_today": present_today,
            "absent_today": absent_today
        }
    )



from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.dependencies import get_db
from app.models import Student
from app.models.student_session import student_sessions

@app.get("/migrate-sessions")
def migrate_sessions(db: Session = Depends(get_db)):
    students = db.query(Student).filter(Student.session_id.isnot(None)).all()
    
    migrated_count = 0

    for student in students:
        # چک می‌کنیم قبلاً مهاجرت شده یا نه
        exists = db.execute(
            select(student_sessions).where(
                student_sessions.c.student_id == student.id,
                student_sessions.c.session_id == student.session_id
            )
        ).first()

        if not exists:
            db.execute(
                student_sessions.insert().values(
                    student_id=student.id,
                    session_id=student.session_id
                )
            )
            migrated_count += 1

    db.commit()

    return {
        "message": "مهاجرت با موفقیت انجام شد",
        "migrated_students": migrated_count,
        "total_checked": len(students)
    }
