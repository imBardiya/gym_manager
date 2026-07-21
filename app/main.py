from fastapi import FastAPI
from app.core.templates import templates

from app.database import Base
from app.database import engine

from app.models import Student
from app.models import GymSession
from app.models import Attendance

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

from app.dependencies import get_db

from app.models import (
    Student,
    Attendance,
    GymSession
)

app = FastAPI(
    title="Gym Manager"
)

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
