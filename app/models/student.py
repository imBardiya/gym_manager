from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String, nullable=False)

    phone = Column(String, nullable=True)

    register_date = Column(Date)

    total_sessions = Column(Integer, default=0)

    used_sessions = Column(Integer, default=0)

    absence_count = Column(Integer, default=0)

    deduct_absence = Column(Boolean, default=False)

    notes = Column(String, nullable=True)

    # سانس قدیمی - فعلاً نگهش می‌داریم
    session_id = Column(
        Integer,
        ForeignKey("sessions.id")
    )

    # سانس قدیمی
    session = relationship(
        "GymSession",
        back_populates="students"
    )

    # سانس‌های جدید - چندتایی
    sessions = relationship(
        "GymSession",
        secondary="student_sessions",
        back_populates="students_multiple"
    )
