import sqlite3

from fastapi import APIRouter
from sqlalchemy.orm import Session

from app.dependencies import SessionLocal
from app.models.student import Student
from app.models.session import GymSession
from app.models.attendance import Attendance

router = APIRouter(
    prefix="/restore",
    tags=["Restore"]
)


@router.get("/")
def restore_backup():

    db: Session = SessionLocal()

    sqlite_conn = sqlite3.connect("gym_backup.db")
    sqlite_conn.row_factory = sqlite3.Row

    cur = sqlite_conn.cursor()

    # جلوگیری از دوبار ایمپورت
    if db.query(Student).first():
        return {
            "message": "Database already contains data"
        }

    # Sessions

    sessions = cur.execute(
        "SELECT * FROM sessions"
    ).fetchall()

    for row in sessions:

        db.add(
            GymSession(
                id=row["id"],
                title=row["title"],
                start_time=row["start_time"],
                end_time=row["end_time"],
                session_type=row["session_type"]
            )
        )

    db.commit()

    # Students

    students = cur.execute(
        "SELECT * FROM students"
    ).fetchall()

    for row in students:

        db.add(
            Student(
                id=row["id"],
                full_name=row["full_name"],
                phone=row["phone"],
                register_date=row["register_date"],
                total_sessions=row["total_sessions"],
                used_sessions=row["used_sessions"],
                absence_count=row["absence_count"],
                deduct_absence=row["deduct_absence"],
                notes=row["notes"],
                session_id=row["session_id"]
            )
        )

    db.commit()

    # Attendance

    attendance = cur.execute(
        "SELECT * FROM attendance"
    ).fetchall()

    for row in attendance:

        db.add(
            Attendance(
                id=row["id"],
                student_id=row["student_id"],
                date=row["date"],
                status=row["status"]
            )
        )

    db.commit()

    sqlite_conn.close()

    return {
        "message": "Restore completed",
        "sessions": len(sessions),
        "students": len(students),
        "attendance": len(attendance)
    }