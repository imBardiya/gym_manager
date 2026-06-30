from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi.responses import RedirectResponse

from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models import Attendance
from app.models import Student

router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"]
)


@router.post("/{attendance_id}/toggle")
def toggle_attendance(
    attendance_id: int,
    db: Session = Depends(get_db)
):

    attendance = (
        db.query(Attendance)
        .filter(
            Attendance.id == attendance_id
        )
        .first()
    )

    if not attendance:
        raise HTTPException(
            status_code=404,
            detail="Attendance not found"
        )

    student = (
        db.query(Student)
        .filter(
            Student.id == attendance.student_id
        )
        .first()
    )

    if attendance.status == "present":

        attendance.status = "absent"

        student.used_sessions -= 1

        student.absence_count += 1

        if student.deduct_absence:
            student.used_sessions += 1

    else:

        attendance.status = "present"

        student.absence_count -= 1

        if student.deduct_absence:
            student.used_sessions -= 1

        student.used_sessions += 1

    db.commit()

    return RedirectResponse(
        url=f"/students/{student.id}",
        status_code=303
    )