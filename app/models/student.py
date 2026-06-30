from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from app.database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

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

    session_id = Column(
        Integer,
        ForeignKey("sessions.id")
    )

    session = relationship(
        "GymSession",
        back_populates="students"
    )