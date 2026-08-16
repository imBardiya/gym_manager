from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class GymSession(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)

    start_time = Column(String)

    end_time = Column(String)

    session_type = Column(String)

    # رابطه قدیمی - فعلاً نگه می‌داریم
    students = relationship(
        "Student",
        back_populates="session"
    )

    # رابطه چندسانسی جدید
    students_multiple = relationship(
        "Student",
        secondary="student_sessions",
        back_populates="sessions"
    )
