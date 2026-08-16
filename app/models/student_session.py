from sqlalchemy import Table, Column, Integer, ForeignKey

from app.database import Base


student_sessions = Table(
    "student_sessions",
    Base.metadata,

    Column(
        "student_id",
        Integer,
        ForeignKey("students.id"),
        primary_key=True
    ),

    Column(
        "session_id",
        Integer,
        ForeignKey("sessions.id"),
        primary_key=True
    )
)
